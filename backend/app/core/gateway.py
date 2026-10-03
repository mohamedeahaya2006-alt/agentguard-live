"""Gateway Orchestrator executing the complete AgentGuard Interception Pipeline."""

import time
import uuid
from typing import Optional
from sqlalchemy.orm import Session

from app.models.agent import AgentModel
from app.models.policy import PolicyModel
from app.models.event import EventModel
from app.models.approval import ApprovalModel
from app.schemas.intercept import InterceptRequest, InterceptResponse
from app.core.identity_engine import evaluate_identity_and_permissions
from app.core.policy_engine import evaluate_policies
from app.core.sensitivity_engine import evaluate_data_sensitivity
from app.core.intent_engine import evaluate_intent
from app.core.anomaly_engine import evaluate_behavioral_anomaly_and_destination
from app.core.prompt_injection import scan_for_prompt_injection
from app.core.risk_scorer import calculate_risk_score
from app.core.decision_engine import determine_decision
from app.core.explainability import generate_explanation
from app.core.incident_memory import record_or_update_incident


def process_agent_action(
    request: InterceptRequest,
    db: Session,
    ws_broadcast_func=None
) -> InterceptResponse:
    """
    Executes the full real-time interception pipeline for an incoming agent action.
    """
    start_time = time.perf_counter()
    event_id = str(uuid.uuid4())
    all_evidence = []

    # 1. Fetch Agent Identity
    agent = db.query(AgentModel).filter(AgentModel.id == request.agent_id).first()
    if not agent:
        # Create ad-hoc profile for unknown agents with high base risk
        agent = AgentModel(
            id=request.agent_id,
            name=f"Unknown Agent ({request.agent_id})",
            department="External/Unassigned",
            purpose="Unregistered autonomous agent",
            allowed_resources=[],
            restricted_resources=["*"],
            external_access="blocked",
            base_risk_level="HIGH",
            is_active=True
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        all_evidence.append(f"Security Alert: Unregistered agent ID '{request.agent_id}' intercepted")

    all_evidence.append(f"Agent identity verified: {agent.name} [{agent.department}]")

    # 2. Identity & Permissions Check
    permission_score, perm_evidence = evaluate_identity_and_permissions(
        agent=agent,
        target_resource=request.action.target_resource,
        destination=request.action.destination or "internal",
        action_type=request.action.action_type
    )
    all_evidence.extend(perm_evidence)

    # 3. Deterministic Policy Evaluation
    active_policies = db.query(PolicyModel).filter(PolicyModel.is_active == True).all()
    policy_score, requires_human_approval, triggered_policies, pol_evidence = evaluate_policies(
        agent_id=agent.id,
        target_resource=request.action.target_resource,
        action_type=request.action.action_type,
        active_policies=active_policies
    )
    all_evidence.extend(pol_evidence)

    # 4. Data Sensitivity Check
    sensitivity_score, detected_categories, sens_evidence = evaluate_data_sensitivity(
        target_resource=request.action.target_resource,
        parameters=request.action.parameters
    )
    all_evidence.extend(sens_evidence)

    # 5. Prompt Injection Scan
    is_injection, injection_score, inj_evidence = scan_for_prompt_injection(
        declared_goal=request.declared_goal,
        parameters_text=str(request.action.parameters),
        context_snippet=request.context.prompt_history_snippet if request.context else ""
    )
    if is_injection:
        all_evidence.extend(inj_evidence)
        policy_score = max(policy_score, 100.0)

    # 6. Intent & Goal Alignment
    goal_mismatch_score, intent_evidence = evaluate_intent(
        declared_goal=request.declared_goal,
        target_resource=request.action.target_resource,
        action_type=request.action.action_type,
        parameters=request.action.parameters,
        context_snippet=request.context.prompt_history_snippet if request.context else ""
    )
    all_evidence.extend(intent_evidence)

    # 7. Behavioral Anomaly & Destination Risk
    anomaly_score, destination_score, anom_evidence = evaluate_behavioral_anomaly_and_destination(
        agent_id=agent.id,
        tool_name=request.action.tool_name,
        action_type=request.action.action_type,
        destination=request.action.destination or "internal",
        parameters=request.action.parameters
    )
    all_evidence.extend(anom_evidence)

    # 8. Calculate Composite Risk Score (6 dimensions)
    composite_risk, breakdown = calculate_risk_score(
        permission_risk=permission_score,
        data_sensitivity=sensitivity_score,
        goal_mismatch=goal_mismatch_score,
        behavioral_anomaly=anomaly_score,
        destination_risk=destination_score,
        policy_violation=policy_score
    )

    # 9. Determine Threat Category
    threat_category = "NORMAL"
    if is_injection:
        threat_category = "PROMPT_INJECTION"
    elif "COMPENSATION_AND_FINANCIAL" in detected_categories or "CUSTOMER_PII" in detected_categories:
        if permission_score >= 80.0:
            threat_category = "UNAUTHORIZED_PII_ACCESS"
        else:
            threat_category = "SENSITIVE_DATA_ACCESS"
    elif permission_score >= 80.0:
        threat_category = "UNAUTHORIZED_RESOURCE_ACCESS"
    elif requires_human_approval:
        threat_category = "PRODUCTION_DEPLOYMENT_GATE"

    # 10. Determine Decision
    is_hard_block = (policy_score >= 100.0) or (permission_score >= 100.0 and sensitivity_score >= 80.0)
    decision = determine_decision(
        risk_score=composite_risk,
        requires_human_approval=requires_human_approval,
        is_hard_policy_block=is_hard_block,
        is_prompt_injection=is_injection
    )

    # 11. Generate Explainable Narrative
    explanation = generate_explanation(
        decision=decision,
        agent_id=agent.id,
        agent_name=agent.name,
        declared_goal=request.declared_goal,
        target_resource=request.action.target_resource,
        action_type=request.action.action_type,
        all_evidence=all_evidence,
        threat_category=threat_category
    )

    latency_ms = (time.perf_counter() - start_time) * 1000.0

    # 12. Handle Human Approval Object if paused
    approval_id = None
    approval_status = "NONE"
    if decision == "WARN":
        approval_id = f"APP-{str(uuid.uuid4())[:8].upper()}"
        approval_status = "PENDING"
        approval = ApprovalModel(
            id=approval_id,
            event_id=event_id,
            agent_id=agent.id,
            action_description=f"{request.action.action_type.upper()} on {request.action.target_resource}",
            target_resource=request.action.target_resource,
            risk_score=composite_risk,
            status="PENDING"
        )
        db.add(approval)

    # 13. Persist Intercepted Event
    event = EventModel(
        id=event_id,
        agent_id=agent.id,
        session_id=request.session_id,
        declared_goal=request.declared_goal,
        tool_name=request.action.tool_name,
        target_resource=request.action.target_resource,
        action_type=request.action.action_type,
        payload_preview=str(request.action.parameters)[:500],
        destination=request.action.destination or "internal",
        risk_score=composite_risk,
        decision=decision,
        risk_breakdown=breakdown.model_dump(),
        explanation=explanation.model_dump(),
        approval_status=approval_status,
        latency_ms=latency_ms
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # 14. Record in Incident Memory if high risk or blocked
    if decision == "BLOCK":
        record_or_update_incident(
            db=db,
            event=event,
            threat_category=threat_category,
            summary=explanation.summary,
            base_severity="CRITICAL" if composite_risk > 85.0 else "HIGH"
        )

    # Build response
    response = InterceptResponse(
        event_id=event_id,
        decision=decision,
        risk_score=composite_risk,
        risk_breakdown=breakdown,
        explanation=explanation,
        approval_id=approval_id,
        latency_ms=round(latency_ms, 2)
    )

    # 15. Broadcast to WebSocket clients if provided
    if ws_broadcast_func:
        ws_broadcast_func({
            "type": "ACTION_INTERCEPTED",
            "data": {
                "event": event.to_dict(),
                "approval_id": approval_id
            }
        })

    return response
