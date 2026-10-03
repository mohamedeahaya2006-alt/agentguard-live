"""AgentGuard Python SDK.

Drop-in security and governance client for autonomous AI agent frameworks
(LangChain, AutoGen, CrewAI, OpenAI Assistants, LlamaIndex, custom agents).
"""

import functools
import requests
from typing import Dict, Any, Optional, Callable


class SecurityException(Exception):
    """Raised when an agent action is blocked by AgentGuard."""
    def __init__(self, message: str, risk_score: float, evidence: list):
        super().__init__(message)
        self.risk_score = risk_score
        self.evidence = evidence


class AgentGuard:
    """AgentGuard Client SDK."""

    def __init__(
        self,
        agent_id: str,
        gateway_url: str = "http://127.0.0.1:8000",
        session_id: str = "default_session"
    ):
        self.agent_id = agent_id
        self.gateway_url = gateway_url.rstrip("/")
        self.session_id = session_id
        self.intercept_endpoint = f"{self.gateway_url}/api/v1/intercept"

    def check(
        self,
        declared_goal: str,
        tool_name: str,
        target_resource: str,
        action_type: str = "read",
        parameters: Optional[Dict[str, Any]] = None,
        destination: str = "internal",
        context_snippet: str = ""
    ) -> Dict[str, Any]:
        """
        Synchronously checks an action before execution.
        Returns the interception evaluation dictionary.
        Raises SecurityException if the action is BLOCKED.
        """
        payload = {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "declared_goal": declared_goal,
            "action": {
                "tool_name": tool_name,
                "target_resource": target_resource,
                "action_type": action_type,
                "parameters": parameters or {},
                "destination": destination
            },
            "context": {
                "prompt_history_snippet": context_snippet
            }
        }

        try:
            resp = requests.post(self.intercept_endpoint, json=payload, timeout=5.0)
            resp.raise_for_status()
            data = resp.json()

            if data.get("decision") == "BLOCK":
                explanation = data.get("explanation", {})
                raise SecurityException(
                    message=f"AgentGuard Intercept BLOCKED action on '{target_resource}': {explanation.get('summary')}",
                    risk_score=data.get("risk_score", 100.0),
                    evidence=explanation.get("evidence", [])
                )

            return data

        except requests.exceptions.RequestException as e:
            # Safe fallback if control plane unreachable
            print(f"[AgentGuard Warning] Unable to reach control plane: {e}")
            return {"decision": "ALLOW", "risk_score": 0.0, "warning": "gateway_unreachable"}

    def intercept(
        self,
        target_resource: str,
        action_type: str = "execute",
        declared_goal: Optional[str] = None
    ):
        """
        Decorator for wrapping agent tool methods.
        Example:
            @guard.intercept(target_resource="finance_db", action_type="read")
            def query_db(sql: str):
                ...
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                goal = declared_goal or f"Execute {func.__name__}"
                params = {"args": [str(a) for a in args], "kwargs": {k: str(v) for k, v in kwargs.items()}}
                self.check(
                    declared_goal=goal,
                    tool_name=func.__name__,
                    target_resource=target_resource,
                    action_type=action_type,
                    parameters=params
                )
                return func(*args, **kwargs)
            return wrapper
        return decorator
