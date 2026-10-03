/**
 * AgentGuard Live — Real-Time Control Plane Frontend Controller
 */

// State
let events = [];
let agents = [];
let incidents = [];
let selectedEvent = null;
let currentFilter = 'ALL';
let activePendingApproval = null;
let soundEnabled = true;
let socket = null;

// Dynamic Base URLs (works for http://localhost:8000 AND direct file:/// opening)
const isHttp = window.location.protocol === 'http:' || window.location.protocol === 'https:';
const API_BASE = isHttp ? window.location.origin : 'http://127.0.0.1:8000';
const WS_BASE = window.location.protocol === 'https:'
  ? `wss://${window.location.host}`
  : isHttp
    ? `ws://${window.location.host}`
    : 'ws://127.0.0.1:8000';

// Safe Lucide Icon Renderer (never throws even if CDN is offline)
function safeCreateIcons() {
  if (typeof lucide !== 'undefined' && lucide && lucide.createIcons) {
    try {
      lucide.createIcons();
    } catch (e) {
      console.warn('Lucide icons warning:', e);
    }
  }
}

// Audio Synthesizer (Lazy initialization to satisfy browser autoplay security)
let audioCtx = null;
function getAudioContext() {
  if (!audioCtx && (window.AudioContext || window.webkitAudioContext)) {
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    } catch (e) {
      audioCtx = null;
    }
  }
  return audioCtx;
}

function playTone(freq, type, duration) {
  if (!soundEnabled) return;
  const ctx = getAudioContext();
  if (!ctx) return;
  try {
    if (ctx.state === 'suspended') {
      ctx.resume();
    }
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + duration);
  } catch (e) {
    // Autoplay restrictions or headless browser
  }
}

function playDecisionSound(decision) {
  if (decision === 'ALLOW') {
    playTone(587.33, 'sine', 0.15); // D5 pleasant blip
  } else if (decision === 'WARN') {
    playTone(440, 'triangle', 0.3); // A4 amber chime
    setTimeout(() => playTone(554.37, 'triangle', 0.4), 150); // C#5
  } else if (decision === 'BLOCK') {
    playTone(220, 'sawtooth', 0.35); // Warning buzzer
    setTimeout(() => playTone(180, 'sawtooth', 0.4), 120);
  }
}

// ================= DOM ELEMENTS =================
const elements = {
  indicator: document.getElementById('system-indicator'),
  statusText: document.getElementById('system-status-text'),
  telemetryTps: document.getElementById('telemetry-tps'),
  telemetryTotal: document.getElementById('telemetry-total'),
  telemetryWarn: document.getElementById('telemetry-warn'),
  telemetryBlocked: document.getElementById('telemetry-blocked'),
  agentsList: document.getElementById('agents-list'),
  agentBadge: document.getElementById('agent-count-badge'),
  incidentList: document.getElementById('incident-list'),
  incidentBadge: document.getElementById('incident-count-badge'),
  streamFeed: document.getElementById('stream-feed'),
  streamCount: document.getElementById('stream-count'),
  inspector: document.getElementById('inspector-content'),
  selectedBadge: document.getElementById('selected-event-badge'),
  soundToggle: document.getElementById('btn-sound-toggle'),
  soundIcon: document.getElementById('icon-sound'),
  // Modal
  modal: document.getElementById('approval-modal'),
  modalAgent: document.getElementById('modal-agent'),
  modalTool: document.getElementById('modal-tool'),
  modalTarget: document.getElementById('modal-target'),
  modalRisk: document.getElementById('modal-risk'),
  modalReason: document.getElementById('modal-reason'),
  modalApprove: document.getElementById('modal-btn-approve'),
  modalReject: document.getElementById('modal-btn-reject'),
  // Scenario Buttons
  btnScenario1: document.getElementById('btn-scenario-1'),
  btnScenario2: document.getElementById('btn-scenario-2'),
  btnScenario3: document.getElementById('btn-scenario-3'),
  btnReset: document.getElementById('btn-reset'),
};

// ================= WEBSOCKET CONNECTION =================
function connectWebSocket() {
  const wsUrl = `${WS_BASE}/ws/live`;

  try {
    socket = new WebSocket(wsUrl);
  } catch (err) {
    markServerOffline();
    setTimeout(connectWebSocket, 3000);
    return;
  }

  socket.onopen = () => {
    elements.indicator.className = 'w-2.5 h-2.5 rounded-full bg-emerald-400 pulse-green';
    elements.statusText.textContent = 'SYSTEM ONLINE';
    elements.statusText.className = 'text-xs font-semibold tracking-wider text-emerald-400 mono';
    // Refresh data immediately on connect
    fetchAgents();
    fetchTelemetry();
    fetchIncidents();
    fetchEventsHistory();
  };

  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      handleWebSocketMessage(msg);
    } catch (e) {
      console.error('Error parsing WS message:', e);
    }
  };

  socket.onclose = () => {
    markServerOffline();
    setTimeout(connectWebSocket, 2500);
  };

  socket.onerror = () => {
    markServerOffline();
  };
}

function markServerOffline() {
  elements.indicator.className = 'w-2.5 h-2.5 rounded-full bg-red-500 pulse-red';
  elements.statusText.textContent = 'SERVER OFFLINE (Run: python run.py)';
  elements.statusText.className = 'text-xs font-semibold tracking-wider text-red-400 mono';
  
  if (events.length === 0) {
    elements.streamFeed.innerHTML = `
      <div class="p-4 rounded-lg bg-red-950/30 border border-red-800/50 text-center my-8">
        <div class="text-red-400 font-bold text-sm mb-1">⚠️ Control Plane Offline</div>
        <div class="text-slate-300 text-xs mb-3">The AgentGuard backend is currently not running.</div>
        <div class="text-[11px] mono bg-black/60 p-2.5 rounded text-amber-300 select-all">
          cd C:\\Users\\LENOVO\\.gemini\\antigravity\\scratch\\agentguard-live<br>
          python run.py
        </div>
        <div class="text-[10px] text-slate-500 mt-2">The dashboard will automatically connect once started.</div>
      </div>
    `;
    safeCreateIcons();
  }
}

function handleWebSocketMessage(msg) {
  if (msg.type === 'ACTION_INTERCEPTED') {
    const event = msg.data.event;
    events.unshift(event);
    playDecisionSound(event.decision);

    // Update Telemetry
    updateTelemetry();
    renderStream();

    // If WARN/Approval required, trigger modal
    if (event.decision === 'WARN' && msg.data.approval_id) {
      openApprovalModal(msg.data.approval_id, event);
    }

    // Auto-select latest event in inspector
    selectEvent(event.id);
    fetchIncidents();
  } else if (msg.type === 'APPROVAL_RESOLVED') {
    const data = msg.data;
    closeApprovalModal();
    // Update local event
    const ev = events.find(e => e.id === data.event_id);
    if (ev) {
      ev.approval_status = data.decision;
    }
    renderStream();
    if (selectedEvent && selectedEvent.id === data.event_id) {
      renderInspector(selectedEvent);
    }
  } else if (msg.type === 'SIMULATION_RESET') {
    events = [];
    incidents = [];
    selectedEvent = null;
    closeApprovalModal();
    renderStream();
    renderIncidents();
    renderInspector(null);
    updateTelemetry();
  }
}

// ================= API FETCHERS =================
async function fetchAgents() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/agents`);
    if (res.ok) {
      agents = await res.json();
      renderAgents();
    }
  } catch (e) {
    console.warn('Backend currently unreachable for agents:', e.message);
  }
}

async function fetchTelemetry() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/telemetry`);
    if (res.ok) {
      const data = await res.json();
      elements.telemetryTotal.textContent = data.total_actions;
      elements.telemetryWarn.textContent = data.warn_count;
      elements.telemetryBlocked.textContent = data.block_count;
      elements.telemetryTps.innerHTML = `${data.actions_per_minute} <span class="text-[10px] text-slate-500">act/m</span>`;
    }
  } catch (e) {
    console.warn('Backend currently unreachable for telemetry:', e.message);
  }
}

async function fetchIncidents() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/incidents?limit=15`);
    if (res.ok) {
      incidents = await res.json();
      renderIncidents();
    }
  } catch (e) {
    console.warn('Backend currently unreachable for incidents:', e.message);
  }
}

async function fetchEventsHistory() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/events?limit=30`);
    if (res.ok) {
      events = await res.json();
      renderStream();
      if (events.length > 0) {
        selectEvent(events[0].id);
      }
    }
  } catch (e) {
    console.warn('Backend currently unreachable for events:', e.message);
  }
}

// ================= RENDERERS =================
function renderAgents() {
  if (agents.length === 0) {
    elements.agentsList.innerHTML = `<div class="text-slate-500 text-center py-6">Connecting to agent registry...</div>`;
    return;
  }
  elements.agentBadge.textContent = `${agents.length} ACTIVE`;
  elements.agentsList.innerHTML = agents.map(agent => {
    const isWarn = agent.base_risk_level === 'HIGH';
    return `
      <div class="p-3 bg-slate-900/80 border border-cyberBorder rounded-lg hover:border-slate-700 transition">
        <div class="flex items-center justify-between mb-1.5">
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full ${isWarn ? 'bg-amber-400' : 'bg-emerald-400'}"></span>
            <span class="font-mono font-bold text-xs text-slate-200">${agent.id}</span>
          </div>
          <span class="text-[10px] px-1.5 py-0.5 rounded mono uppercase ${
            agent.base_risk_level === 'LOW' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
            agent.base_risk_level === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
            'bg-red-500/10 text-red-400 border border-red-500/20'
          }">${agent.base_risk_level} RISK</span>
        </div>
        <div class="text-xs font-semibold text-slate-300 truncate">${agent.name}</div>
        <div class="text-[10px] text-slate-400 line-clamp-2 mt-0.5">${agent.purpose}</div>

        <div class="mt-2 pt-2 border-t border-slate-800 flex flex-wrap gap-1">
          ${(agent.allowed_resources || []).slice(0, 2).map(r => 
            `<span class="text-[9px] px-1.5 py-0.2 rounded bg-emerald-950/40 text-emerald-300 border border-emerald-800/30 mono">✓ ${r}</span>`
          ).join('')}
          ${(agent.restricted_resources || []).slice(0, 2).map(r => 
            `<span class="text-[9px] px-1.5 py-0.2 rounded bg-red-950/40 text-red-300 border border-red-800/30 mono">✗ ${r}</span>`
          ).join('')}
        </div>
      </div>
    `;
  }).join('');
}

function renderIncidents() {
  elements.incidentBadge.textContent = `${incidents.length} DETECTED`;
  if (incidents.length === 0) {
    elements.incidentList.innerHTML = `<div class="text-slate-500 text-center py-6">No security incidents detected. System healthy.</div>`;
    return;
  }

  elements.incidentList.innerHTML = incidents.map(inc => {
    const isCritical = inc.severity === 'CRITICAL';
    const isRepeat = inc.repetition_count > 1;
    return `
      <div class="p-2.5 bg-red-950/20 border border-red-900/40 rounded-lg">
        <div class="flex items-center justify-between">
          <span class="mono font-bold text-[11px] text-red-400">${inc.id}</span>
          <div class="flex items-center space-x-1">
            ${isRepeat ? `<span class="px-1.5 py-0.5 rounded text-[9px] bg-red-600 text-white font-bold mono animate-pulse">REPEAT ${inc.repetition_count}x</span>` : ''}
            <span class="px-1.5 py-0.5 rounded text-[9px] ${isCritical ? 'bg-red-500/20 text-red-300 border border-red-500/40' : 'bg-amber-500/20 text-amber-300'} font-bold mono">
              ${inc.severity}
            </span>
          </div>
        </div>
        <div class="font-semibold text-slate-200 mt-1">${inc.title}</div>
        <div class="text-[10px] text-slate-400 mt-0.5">${inc.summary}</div>
      </div>
    `;
  }).join('');
}

function renderStream() {
  const filtered = events.filter(e => {
    if (currentFilter === 'ALL') return true;
    return e.decision === currentFilter;
  });

  elements.streamCount.textContent = `${events.length} ACTIONS INTERCEPTED`;

  if (filtered.length === 0) {
    elements.streamFeed.innerHTML = `
      <div class="text-slate-500 text-center py-16">
        <div class="text-xl mb-2">📡</div>
        Listening for autonomous agent actions...
      </div>
    `;
    safeCreateIcons();
    return;
  }

  elements.streamFeed.innerHTML = filtered.map(ev => {
    const isSelected = selectedEvent && selectedEvent.id === ev.id;
    const timeStr = ev.timestamp ? ev.timestamp.split('T')[1]?.split('.')[0] : '--:--:--';
    
    let badgeHtml = '';
    let rowClass = '';
    if (ev.decision === 'ALLOW') {
      badgeHtml = `<span class="badge-allow px-2 py-0.5 rounded font-bold">✓ ALLOWED</span>`;
      rowClass = 'row-allow';
    } else if (ev.decision === 'WARN') {
      const isApproved = ev.approval_status === 'APPROVED';
      const isRejected = ev.approval_status === 'REJECTED';
      if (isApproved) {
        badgeHtml = `<span class="badge-allow px-2 py-0.5 rounded font-bold">✓ APPROVED</span>`;
      } else if (isRejected) {
        badgeHtml = `<span class="badge-block px-2 py-0.5 rounded font-bold">✗ REJECTED</span>`;
      } else {
        badgeHtml = `<span class="badge-warn px-2 py-0.5 rounded font-bold animate-pulse">⏸ PAUSED</span>`;
      }
      rowClass = 'row-warn';
    } else {
      badgeHtml = `<span class="badge-block px-2 py-0.5 rounded font-bold">🚫 BLOCKED</span>`;
      rowClass = 'row-block';
    }

    return `
      <div class="stream-row ${rowClass} ${isSelected ? 'active' : ''} p-2.5 rounded bg-slate-900/60 border border-slate-800/80 cursor-pointer flex items-center justify-between" onclick="selectEvent('${ev.id}')">
        <div class="flex items-center space-x-3 overflow-hidden">
          <span class="text-slate-500 text-[11px]">${timeStr}</span>
          <span class="text-cyan-400 font-bold">${ev.agent_id}</span>
          <span class="text-slate-300 font-medium truncate">${ev.action_type} <span class="text-slate-500">→</span> ${ev.target_resource}</span>
        </div>
        <div class="flex items-center space-x-2 shrink-0">
          <span class="text-[11px] text-slate-400">${ev.risk_score}/100</span>
          ${badgeHtml}
        </div>
      </div>
    `;
  }).join('');
  safeCreateIcons();
}

function selectEvent(eventId) {
  const ev = events.find(e => e.id === eventId);
  if (!ev) return;
  selectedEvent = ev;
  elements.selectedBadge.textContent = `${ev.agent_id} (${ev.id.substring(0, 8)})`;
  renderStream();
  renderInspector(ev);
}

function renderInspector(ev) {
  if (!ev) {
    elements.inspector.innerHTML = `
      <div class="text-slate-500 text-center py-20">
        <div class="text-2xl mb-2">🎯</div>
        Select an action from the live feed to inspect risk reasoning.
      </div>
    `;
    safeCreateIcons();
    return;
  }

  const rb = ev.risk_breakdown || {};
  const exp = ev.explanation || {};
  const isBlock = ev.decision === 'BLOCK';
  const isWarn = ev.decision === 'WARN';
  const scoreColor = isBlock ? 'text-red-400' : isWarn ? 'text-amber-400' : 'text-emerald-400';
  const scoreBorder = isBlock ? 'border-red-500/50' : isWarn ? 'border-amber-500/50' : 'border-emerald-500/50';

  elements.inspector.innerHTML = `
    <!-- Top Composite Gauge Card -->
    <div class="bg-slate-900/90 border ${scoreBorder} p-4 rounded-xl flex items-center justify-between">
      <div>
        <span class="text-[10px] uppercase font-bold tracking-wider text-slate-400 mono">Composite Risk Score</span>
        <div class="text-3xl font-black ${scoreColor} font-mono mt-0.5">
          ${ev.risk_score} <span class="text-sm font-normal text-slate-500">/ 100</span>
        </div>
        <div class="text-xs font-semibold text-slate-300 mt-1">
          Decision: <span class="uppercase ${scoreColor}">${ev.decision}</span>
          ${ev.approval_status && ev.approval_status !== 'NONE' ? `<span class="ml-2 text-cyan-300 mono">(${ev.approval_status})</span>` : ''}
        </div>
      </div>
      <div class="text-right">
        <span class="text-[10px] text-slate-500 mono">LATENCY</span>
        <div class="text-cyan-400 font-mono text-sm font-bold">${ev.latency_ms || 12.4} ms</div>
        <span class="text-[10px] text-slate-500 mono">THREAT LEVEL</span>
        <div class="text-xs font-bold ${scoreColor} mono">${exp.threat_category || 'NORMAL'}</div>
      </div>
    </div>

    <!-- 6-Factor Weighted Risk Breakdown -->
    <div class="p-3 bg-slate-900/60 border border-cyberBorder rounded-lg space-y-2.5">
      <div class="text-xs font-bold uppercase tracking-wider text-slate-300 mono flex items-center justify-between">
        <span>6-Factor Risk Breakdown</span>
        <span class="text-[10px] text-slate-500">WEIGHTED</span>
      </div>

      <!-- Factor 1: Permission Risk (25%) -->
      <div>
        <div class="flex justify-between text-xs mono mb-1">
          <span class="text-slate-400">Permission Risk (25%)</span>
          <span class="text-slate-200 font-semibold">${rb.permission_risk || 0}%</span>
        </div>
        <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div class="h-1.5 bg-red-500 rounded-full" style="width: ${rb.permission_risk || 0}%"></div>
        </div>
      </div>

      <!-- Factor 2: Data Sensitivity (20%) -->
      <div>
        <div class="flex justify-between text-xs mono mb-1">
          <span class="text-slate-400">Data Sensitivity (20%)</span>
          <span class="text-slate-200 font-semibold">${rb.data_sensitivity || 0}%</span>
        </div>
        <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div class="h-1.5 bg-amber-500 rounded-full" style="width: ${rb.data_sensitivity || 0}%"></div>
        </div>
      </div>

      <!-- Factor 3: Goal Mismatch (20%) -->
      <div>
        <div class="flex justify-between text-xs mono mb-1">
          <span class="text-slate-400">Goal Mismatch (20%)</span>
          <span class="text-slate-200 font-semibold">${rb.goal_mismatch || 0}%</span>
        </div>
        <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div class="h-1.5 bg-purple-500 rounded-full" style="width: ${rb.goal_mismatch || 0}%"></div>
        </div>
      </div>

      <!-- Factor 4: Behavioral Anomaly (15%) -->
      <div>
        <div class="flex justify-between text-xs mono mb-1">
          <span class="text-slate-400">Behavioral Anomaly (15%)</span>
          <span class="text-slate-200 font-semibold">${rb.behavioral_anomaly || 0}%</span>
        </div>
        <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div class="h-1.5 bg-cyan-500 rounded-full" style="width: ${rb.behavioral_anomaly || 0}%"></div>
        </div>
      </div>

      <!-- Factor 5: Destination Risk (10%) -->
      <div>
        <div class="flex justify-between text-xs mono mb-1">
          <span class="text-slate-400">Destination Risk (10%)</span>
          <span class="text-slate-200 font-semibold">${rb.destination_risk || 0}%</span>
        </div>
        <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div class="h-1.5 bg-emerald-500 rounded-full" style="width: ${rb.destination_risk || 0}%"></div>
        </div>
      </div>

      <!-- Factor 6: Policy Violation (10%) -->
      <div>
        <div class="flex justify-between text-xs mono mb-1">
          <span class="text-slate-400">Policy Violation (10%)</span>
          <span class="text-slate-200 font-semibold">${rb.policy_violation || 0}%</span>
        </div>
        <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div class="h-1.5 bg-pink-500 rounded-full" style="width: ${rb.policy_violation || 0}%"></div>
        </div>
      </div>
    </div>

    <!-- Explainability Narrative -->
    <div class="p-3 bg-slate-900/60 border border-cyberBorder rounded-lg space-y-2">
      <div class="text-xs font-bold uppercase tracking-wider text-cyan-400 mono flex items-center space-x-1.5">
        <span>🧠 AI Explainability Report</span>
      </div>
      <p class="text-xs text-slate-300 leading-relaxed">${exp.summary || 'Action analyzed by AgentGuard engines.'}</p>
      
      <div class="pt-2 border-t border-slate-800">
        <span class="text-[10px] uppercase font-bold text-slate-400 mono">Key Evidence Points:</span>
        <ul class="mt-1 space-y-1 text-xs">
          ${(exp.evidence || []).map(item => `
            <li class="flex items-start space-x-2 text-slate-300">
              <span class="text-cyan-400 font-bold mt-0.5">•</span>
              <span>${item}</span>
            </li>
          `).join('')}
        </ul>
      </div>

      <div class="mt-3 p-2 rounded bg-black/40 border border-slate-800 text-[11px] mono">
        <span class="text-slate-500">RECOMMENDED ACTION:</span>
        <div class="font-bold ${scoreColor} mt-0.5">${exp.recommended_action || 'ALLOW'}</div>
      </div>
    </div>
  `;
  safeCreateIcons();
}

function updateTelemetry() {
  const total = events.length;
  const warned = events.filter(e => e.decision === 'WARN').length;
  const blocked = events.filter(e => e.decision === 'BLOCK').length;
  elements.telemetryTotal.textContent = total;
  elements.telemetryWarn.textContent = warned;
  elements.telemetryBlocked.textContent = blocked;
}

// ================= HUMAN-IN-THE-LOOP MODAL =================
function openApprovalModal(approvalId, event) {
  activePendingApproval = approvalId;
  elements.modalAgent.textContent = `${event.agent_id}`;
  elements.modalTool.textContent = `${event.tool_name} (${event.action_type})`;
  elements.modalTarget.textContent = `${event.target_resource}`;
  elements.modalRisk.textContent = `${event.risk_score} / 100`;
  elements.modalReason.textContent = event.explanation?.summary || 'Action paused for human verification.';
  elements.modal.classList.remove('hidden');
}

function closeApprovalModal() {
  activePendingApproval = null;
  elements.modal.classList.add('hidden');
}

async function resolveApproval(decision) {
  if (!activePendingApproval) return;
  try {
    const res = await fetch(`${API_BASE}/api/v1/approvals/${activePendingApproval}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        decision: decision,
        reviewed_by: 'Operator Live Demo',
        justification: `Action ${decision.toLowerCase()} via dashboard review.`
      })
    });
    const result = await res.json();
    closeApprovalModal();
  } catch (e) {
    console.error('Failed to resolve approval:', e);
  }
}

// ================= EVENT LISTENERS =================
function initEventListeners() {
  // Scenario Triggers
  elements.btnScenario1.addEventListener('click', () => triggerScenario('/api/v1/simulate/scenario-1'));
  elements.btnScenario2.addEventListener('click', () => triggerScenario('/api/v1/simulate/scenario-2'));
  elements.btnScenario3.addEventListener('click', () => triggerScenario('/api/v1/simulate/scenario-3'));
  elements.btnReset.addEventListener('click', () => triggerScenario('/api/v1/simulate/reset'));

  // Approval Modal Actions
  elements.modalApprove.addEventListener('click', () => resolveApproval('APPROVED'));
  elements.modalReject.addEventListener('click', () => resolveApproval('REJECTED'));

  // Filter Buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.filter-btn').forEach(b => {
        b.className = 'filter-btn px-2 py-0.5 rounded bg-slate-900 text-slate-400 hover:text-slate-200';
      });
      e.target.className = 'filter-btn active px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-400 border border-cyan-800/40';
      currentFilter = e.target.getAttribute('data-filter');
      renderStream();
    });
  });

  // Sound FX Toggle
  elements.soundToggle.addEventListener('click', () => {
    soundEnabled = !soundEnabled;
    elements.soundIcon.textContent = soundEnabled ? '🔊' : '🔇';
    elements.soundToggle.className = soundEnabled 
      ? 'p-2 bg-slate-900 border border-slate-800 rounded-lg text-cyan-400 transition'
      : 'p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-600 transition';
  });
}

async function triggerScenario(endpoint) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, { method: 'POST' });
    if (!res.ok) {
      console.error(`Scenario failed with HTTP status ${res.status}`);
    }
  } catch (e) {
    console.error('Scenario execution failed. Is backend running?', e);
    markServerOffline();
  }
}

// ================= INITIALIZATION =================
window.addEventListener('DOMContentLoaded', () => {
  safeCreateIcons();
  initEventListeners();
  connectWebSocket();
});
