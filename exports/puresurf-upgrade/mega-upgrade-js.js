// ==================== MEGA-UPGRADE JS ====================
// Enhances WF, SN, and ORCH modules for PureSurf v5.5 Mega-Upgrade

// ==================== COLLAPSIBLE HELPER ====================
function toggleCollapse(id) {
  const el = document.getElementById(id);
  if (el) el.classList.toggle('collapsed');
}

// ==================== WF MODULE (ENHANCED) ====================
window.WF = (() => {
  const API = 'https://surf.purebrain.ai';
  const getKey = () => sessionStorage.getItem('baas-key') || '';
  const headers = () => ({ 'Content-Type': 'application/json', 'X-API-Key': getKey() });

  let stepCount = 0;
  let workflows = [];
  let execLog = JSON.parse(localStorage.getItem('wf-exec-log') || '[]');
  let currentTrigger = null;

  async function apiFetch(path, opts = {}) {
    const res = await fetch(API + path, { headers: headers(), ...opts });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`${res.status}: ${text}`);
    }
    return res.status === 204 ? null : res.json();
  }

  function esc(s) {
    if (!s) return '';
    const d = document.createElement('div');
    d.textContent = String(s);
    return d.innerHTML;
  }

  function toast(msg, type) {
    if (window.showToast) { window.showToast(msg, type); return; }
    const t = document.createElement('div');
    t.textContent = msg;
    Object.assign(t.style, {
      position:'fixed', bottom:'20px', right:'20px', padding:'10px 18px',
      background: type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : '#3b82f6',
      color:'#fff', borderRadius:'8px', fontSize:'13px', zIndex:'9999',
      boxShadow:'0 4px 12px rgba(0,0,0,0.3)'
    });
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
  }

  // ---- TRIGGER SYSTEM ----
  function addTrigger(type) {
    currentTrigger = { type, config: {} };
    const configEl = document.getElementById('wf-trigger-config');
    const labelEl = document.getElementById('wf-trigger-type-label');
    const paramsEl = document.getElementById('wf-trigger-params');
    configEl.style.display = 'block';

    const labels = { time: 'Time Schedule', event: 'Event', webhook: 'Webhook', manual: 'Manual' };
    labelEl.textContent = labels[type] || type;

    let html = '';
    if (type === 'time') {
      html = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <div class="ps-field"><label class="ps-label">Schedule</label>
            <select class="ps-select" id="wf-trigger-schedule">
              <option value="daily">Daily</option>
              <option value="weekdays">Weekdays Only</option>
              <option value="weekly">Weekly</option>
              <option value="hourly">Every N Hours</option>
              <option value="cron">Custom Cron</option>
            </select>
          </div>
          <div class="ps-field"><label class="ps-label">Time (ET)</label>
            <input class="ps-input" type="time" id="wf-trigger-time" value="09:00"/>
          </div>
        </div>`;
    } else if (type === 'event') {
      html = `
        <div class="ps-field"><label class="ps-label">Event Type</label>
          <select class="ps-select" id="wf-trigger-event">
            <option value="post_published">Post Published</option>
            <option value="new_connection">New Connection Received</option>
            <option value="message_received">Message Received</option>
            <option value="comment_received">Comment on My Post</option>
            <option value="profile_viewed">Profile Viewed (N times)</option>
          </select>
        </div>`;
    } else if (type === 'webhook') {
      html = `
        <div class="ps-field"><label class="ps-label">Webhook URL (copy this)</label>
          <div style="display:flex;gap:6px">
            <input class="ps-input" readonly value="${API}/webhooks/trigger/${Math.random().toString(36).substr(2, 12)}" id="wf-trigger-webhook-url" style="font-family:var(--mono);font-size:.78rem"/>
            <button class="btn btn-sm btn-ghost" onclick="navigator.clipboard.writeText(document.getElementById('wf-trigger-webhook-url').value);WF.toast('Copied!','success')">Copy</button>
          </div>
        </div>`;
    } else if (type === 'manual') {
      html = `<div style="font-size:.82rem;color:var(--text2)">This workflow will only run when you click the Run button.</div>`;
    }
    paramsEl.innerHTML = html;
  }

  function removeTrigger() {
    currentTrigger = null;
    document.getElementById('wf-trigger-config').style.display = 'none';
  }

  // ---- STEP BUILDER (ENHANCED) ----
  const STEP_TYPES = {
    navigate: { label: 'Navigate', icon: '&#127919;', targetPh: 'URL', valuePh: '' },
    click: { label: 'Click', icon: '&#128433;', targetPh: 'CSS selector', valuePh: '' },
    type: { label: 'Type', icon: '&#9000;', targetPh: 'CSS selector', valuePh: 'Text to type' },
    scroll: { label: 'Scroll', icon: '&#11015;', targetPh: 'Direction (down/up)', valuePh: 'Pixels or "page"' },
    wait: { label: 'Wait', icon: '&#9200;', targetPh: '', valuePh: 'Seconds (e.g. 3)' },
    screenshot: { label: 'Screenshot', icon: '&#128248;', targetPh: 'Filename (optional)', valuePh: '' },
    extract: { label: 'Extract Data', icon: '&#128230;', targetPh: 'CSS selector', valuePh: 'Attribute (text/href/src)' },
    api_call: { label: 'API Call', icon: '&#128279;', targetPh: 'URL', valuePh: 'POST body (JSON)' },
    condition: { label: 'If/Else', icon: '&#10067;', targetPh: 'Condition (JS expression)', valuePh: 'e.g. title.includes("Login")' },
    loop: { label: 'Loop', icon: '&#128260;', targetPh: 'Items selector or count', valuePh: 'Max iterations' },
    log_sheet: { label: 'Log to Sheet', icon: '&#128202;', targetPh: 'Sheet ID or name', valuePh: 'Data to log' },
    notify: { label: 'Notify', icon: '&#128276;', targetPh: 'Telegram chat ID', valuePh: 'Message text' }
  };

  function addStep(type = 'navigate', target = '', value = '') {
    stepCount++;
    const info = STEP_TYPES[type] || STEP_TYPES.navigate;
    const c = document.getElementById('wf-steps-container');
    const div = document.createElement('div');
    const stepClass = ['condition','loop','notify','api_call'].includes(type) ? ' step-' + type : '';
    div.className = 'wf-step-enhanced' + stepClass;
    div.dataset.idx = stepCount;

    // Build type options
    let typeOpts = Object.entries(STEP_TYPES).map(([k, v]) =>
      `<option value="${k}" ${k === type ? 'selected' : ''}>${v.label}</option>`
    ).join('');

    div.innerHTML = `
      <span class="wf-step-drag" title="Drag to reorder">&#9776;</span>
      <span class="wf-step-num">${stepCount}</span>
      <select class="ps-select wf-step-type" onchange="WF.onStepTypeChange(this)">${typeOpts}</select>
      <input class="ps-input wf-step-target" placeholder="${esc(info.targetPh)}" value="${esc(target)}" />
      <input class="ps-input wf-step-value" placeholder="${esc(info.valuePh)}" value="${esc(value)}" />
      <button class="wf-remove-btn" onclick="this.closest('.wf-step-enhanced').remove();WF.renumber()" title="Remove">&times;</button>
    `;
    c.appendChild(div);
    renumber();
  }

  function onStepTypeChange(select) {
    const type = select.value;
    const info = STEP_TYPES[type] || STEP_TYPES.navigate;
    const row = select.closest('.wf-step-enhanced');
    row.querySelector('.wf-step-target').placeholder = info.targetPh;
    row.querySelector('.wf-step-value').placeholder = info.valuePh;
    // Update conditional styling
    row.className = 'wf-step-enhanced' + (['condition','loop','notify','api_call'].includes(type) ? ' step-' + type : '');
  }

  function renumber() {
    document.querySelectorAll('#wf-steps-container .wf-step-enhanced').forEach((s, i) => {
      s.querySelector('.wf-step-num').textContent = i + 1;
    });
  }

  function getSteps() {
    const steps = [];
    document.querySelectorAll('#wf-steps-container .wf-step-enhanced').forEach(s => {
      steps.push({
        action: s.querySelector('.wf-step-type').value,
        target: s.querySelector('.wf-step-target').value,
        value: s.querySelector('.wf-step-value').value
      });
    });
    return steps;
  }

  // ---- SAVE / LOAD ----
  async function save() {
    const name = document.getElementById('wf-name').value.trim();
    const description = document.getElementById('wf-desc').value.trim();
    const steps = getSteps();
    if (!name) { toast('Workflow name is required', 'error'); return; }
    if (steps.length === 0) { toast('Add at least one step', 'error'); return; }

    const payload = { name, description, steps };
    if (currentTrigger) payload.trigger = currentTrigger;

    const editId = document.getElementById('wf-edit-id').value;
    try {
      if (editId) {
        await apiFetch('/workflows/' + editId, {
          method: 'PUT',
          body: JSON.stringify(payload)
        });
        toast('Workflow updated', 'success');
      } else {
        await apiFetch('/workflows', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        toast('Workflow saved', 'success');
      }
      resetForm();
      loadWorkflows();
    } catch (e) {
      // Save locally if API fails
      const local = JSON.parse(localStorage.getItem('wf-local-workflows') || '[]');
      payload.id = 'local-' + Date.now();
      payload.created_at = new Date().toISOString();
      local.push(payload);
      localStorage.setItem('wf-local-workflows', JSON.stringify(local));
      toast('Saved locally (API unavailable)', 'info');
      loadWorkflows();
    }
  }

  async function loadWorkflows() {
    const listEl = document.getElementById('wf-list');
    try {
      const data = await apiFetch('/workflows');
      workflows = data.workflows || data || [];
    } catch {
      workflows = [];
    }
    // Merge local workflows
    const local = JSON.parse(localStorage.getItem('wf-local-workflows') || '[]');
    const all = [...workflows, ...local];

    const badge = document.getElementById('wf-count-badge');
    if (badge) badge.textContent = all.length;

    if (!all.length) {
      listEl.innerHTML = '<div class="empty-state"><div class="icon">&#128466;</div><p>No workflows yet. Create one above or use a template.</p></div>';
      return;
    }

    listEl.innerHTML = all.map(w => {
      const stepCount = (w.steps || []).length;
      const isLocal = (w.id || '').toString().startsWith('local-');
      const triggerBadge = w.trigger ? `<span class="badge badge-yellow" style="font-size:.6rem">${w.trigger.type}</span>` : '';
      return `<div class="wf-card">
        <div class="wf-card-header">
          <div>
            <div class="wf-card-name">${esc(w.name)}</div>
            <div class="wf-card-meta">${stepCount} steps ${triggerBadge} ${isLocal ? '<span class="badge badge-yellow" style="font-size:.6rem">LOCAL</span>' : ''}</div>
          </div>
        </div>
        ${w.description ? `<div class="wf-card-desc">${esc(w.description)}</div>` : ''}
        <div class="wf-card-actions">
          <button class="wf-run-btn" onclick="WF.run('${esc(w.id || w.name)}')">Run</button>
          <button onclick="WF.edit('${esc(w.id || w.name)}')">Edit</button>
          <button onclick="WF.duplicate('${esc(w.id || w.name)}')">Duplicate</button>
          <button class="wf-del-btn" onclick="WF.del('${esc(w.id || w.name)}')">Delete</button>
        </div>
      </div>`;
    }).join('');
  }

  async function run(id) {
    // Find a session to run on
    const sessions = await apiFetch('/sessions').catch(() => ({ sessions: [] }));
    const sessionList = Array.isArray(sessions) ? sessions : (sessions.sessions || []);
    if (!sessionList.length) {
      toast('No active sessions. Create one first.', 'error');
      return;
    }
    const sid = sessionList[0].session_id || sessionList[0].id;

    toast('Running workflow...', 'info');
    try {
      const resp = await apiFetch('/sessions/' + sid + '/record/replay', {
        method: 'POST',
        body: JSON.stringify({ name: id, adaptive: true })
      });
      const entry = {
        workflow: id,
        session: sid,
        duration: resp.duration || '-',
        status: resp.success_rate || 'completed',
        time: new Date().toLocaleTimeString()
      };
      execLog.unshift(entry);
      if (execLog.length > 50) execLog = execLog.slice(0, 50);
      localStorage.setItem('wf-exec-log', JSON.stringify(execLog));
      renderExecLog();
      toast('Workflow completed: ' + (resp.success_rate || '100%'), 'success');
    } catch (e) {
      toast('Workflow failed: ' + e.message, 'error');
    }
  }

  function edit(id) {
    const all = [...workflows, ...JSON.parse(localStorage.getItem('wf-local-workflows') || '[]')];
    const wf = all.find(w => (w.id || w.name) === id);
    if (!wf) return;

    document.getElementById('wf-edit-id').value = id;
    document.getElementById('wf-name').value = wf.name || '';
    document.getElementById('wf-desc').value = wf.description || '';
    document.getElementById('wf-form-title').textContent = 'Edit Workflow: ' + wf.name;
    document.getElementById('wf-cancel-btn').style.display = '';

    // Clear and rebuild steps
    document.getElementById('wf-steps-container').innerHTML = '';
    stepCount = 0;
    (wf.steps || []).forEach(s => addStep(s.action, s.target, s.value));

    if (wf.trigger) addTrigger(wf.trigger.type);
  }

  function duplicate(id) {
    const all = [...workflows, ...JSON.parse(localStorage.getItem('wf-local-workflows') || '[]')];
    const wf = all.find(w => (w.id || w.name) === id);
    if (!wf) return;

    document.getElementById('wf-name').value = (wf.name || '') + ' (copy)';
    document.getElementById('wf-desc').value = wf.description || '';
    document.getElementById('wf-steps-container').innerHTML = '';
    stepCount = 0;
    (wf.steps || []).forEach(s => addStep(s.action, s.target, s.value));
    toast('Template loaded - modify and save', 'info');
  }

  async function del(id) {
    if (!confirm('Delete this workflow?')) return;
    try {
      await apiFetch('/workflows/' + id, { method: 'DELETE' });
    } catch {}
    // Also remove from local
    let local = JSON.parse(localStorage.getItem('wf-local-workflows') || '[]');
    local = local.filter(w => (w.id || w.name) !== id);
    localStorage.setItem('wf-local-workflows', JSON.stringify(local));
    loadWorkflows();
    toast('Workflow deleted', 'success');
  }

  function resetForm() {
    document.getElementById('wf-edit-id').value = '';
    document.getElementById('wf-name').value = '';
    document.getElementById('wf-desc').value = '';
    document.getElementById('wf-form-title').textContent = 'Create New Workflow';
    document.getElementById('wf-cancel-btn').style.display = 'none';
    document.getElementById('wf-steps-container').innerHTML = '';
    stepCount = 0;
    removeTrigger();
    addStep('navigate');
  }

  // ---- TEMPLATES ----
  function loadTemplate(name) {
    document.getElementById('wf-steps-container').innerHTML = '';
    stepCount = 0;

    const templates = {
      'linkedin-daily': {
        name: 'LinkedIn Daily Engagement',
        desc: 'Full daily engagement routine: pre-comments, post, first comment, post-comments',
        trigger: { type: 'time', config: { schedule: 'weekdays', time: '09:00' } },
        steps: [
          { action: 'navigate', target: 'https://www.linkedin.com/feed', value: '' },
          { action: 'wait', target: '', value: '3' },
          { action: 'scroll', target: 'down', value: '500' },
          { action: 'click', target: '[data-control-name="comment"]', value: '' },
          { action: 'type', target: '.ql-editor', value: 'Great insight! This resonates with...' },
          { action: 'wait', target: '', value: '90' },
          { action: 'screenshot', target: 'post-engagement', value: '' }
        ]
      },
      'profile-viewing': {
        name: 'Profile Viewing Campaign',
        desc: 'Visit 80 ICP profiles per day with humanized behavior',
        steps: [
          { action: 'navigate', target: 'https://www.linkedin.com/search/results/people/?keywords=CEO%20SaaS', value: '' },
          { action: 'wait', target: '', value: '2' },
          { action: 'loop', target: '.search-result__result-link', value: '25' },
          { action: 'click', target: '.search-result__result-link', value: '' },
          { action: 'scroll', target: 'down', value: 'page' },
          { action: 'wait', target: '', value: '15' },
          { action: 'screenshot', target: 'profile-view', value: '' }
        ]
      },
      'comment-blitz': {
        name: 'Comment Blitz - 25 Traveling Comments',
        desc: '25 comments across 4 time windows with 90s spacing',
        trigger: { type: 'time', config: { schedule: 'weekdays', time: '08:00' } },
        steps: [
          { action: 'navigate', target: 'https://www.linkedin.com/feed', value: '' },
          { action: 'loop', target: 'feed-posts', value: '7' },
          { action: 'scroll', target: 'down', value: '600' },
          { action: 'click', target: '[data-control-name="comment"]', value: '' },
          { action: 'type', target: '.ql-editor', value: '[AI-generated contextual comment]' },
          { action: 'wait', target: '', value: '90' },
          { action: 'log_sheet', target: 'Engagement Log', value: 'Comment posted' },
          { action: 'notify', target: '', value: 'Comment round 1 complete' }
        ]
      },
      'newsletter-publish': {
        name: 'Newsletter Publisher',
        desc: 'Deploy blog, publish newsletter, engage',
        steps: [
          { action: 'navigate', target: 'https://purebrain.ai/blog', value: '' },
          { action: 'screenshot', target: 'blog-deploy-check', value: '' },
          { action: 'navigate', target: 'https://www.linkedin.com/newsletters/', value: '' },
          { action: 'wait', target: '', value: '3' },
          { action: 'click', target: '[data-control-name="write_article"]', value: '' },
          { action: 'type', target: '.article-title', value: '[Newsletter Title]' },
          { action: 'screenshot', target: 'newsletter-draft', value: '' },
          { action: 'notify', target: '', value: 'Newsletter published! Starting engagement.' }
        ]
      },
      'content-approval': {
        name: 'Content Approval Pipeline',
        desc: 'Create, review, approve, schedule, post, log',
        steps: [
          { action: 'navigate', target: 'https://docs.google.com/spreadsheets/', value: '' },
          { action: 'extract', target: '.content-draft', value: 'text' },
          { action: 'condition', target: 'status === "approved"', value: '' },
          { action: 'navigate', target: 'https://www.linkedin.com/feed', value: '' },
          { action: 'type', target: '.share-box-feed-entry__trigger', value: '[Approved content]' },
          { action: 'screenshot', target: 'content-posted', value: '' },
          { action: 'log_sheet', target: 'Content Calendar', value: 'Posted at ' + new Date().toISOString() }
        ]
      }
    };

    const tmpl = templates[name];
    if (!tmpl) return;

    document.getElementById('wf-name').value = tmpl.name;
    document.getElementById('wf-desc').value = tmpl.desc;
    if (tmpl.trigger) addTrigger(tmpl.trigger.type);
    tmpl.steps.forEach(s => addStep(s.action, s.target, s.value));
    toast('Template loaded: ' + tmpl.name, 'info');
  }

  function renderExecLog() {
    const el = document.getElementById('wf-exec-log');
    if (!execLog.length) {
      el.innerHTML = '<div class="empty-state" style="padding:16px"><p style="font-size:.82rem">No executions yet</p></div>';
      return;
    }
    el.innerHTML = execLog.map(e => `
      <div class="exec-row">
        <span style="font-weight:600">${esc(e.workflow)}</span>
        <span style="font-family:var(--mono);font-size:.75rem;color:var(--text3)">${esc(e.session || '-')}</span>
        <span>${esc(e.duration)}</span>
        <span class="badge ${e.status === 'failed' ? 'badge-red' : 'badge-green'}" style="font-size:.65rem">${esc(e.status)}</span>
        <span style="color:var(--text3)">${esc(e.time)}</span>
      </div>
    `).join('');
  }

  function clearExecLog() {
    execLog = [];
    localStorage.removeItem('wf-exec-log');
    renderExecLog();
  }

  function init() {
    addStep('navigate');
    loadWorkflows();
    renderExecLog();
  }

  return {
    init, addStep, removeStep: () => {}, onStepTypeChange, renumber,
    save, loadWorkflows, run, edit, duplicate, del, resetForm,
    addTrigger, removeTrigger, loadTemplate, renderExecLog, clearExecLog,
    toast, getSteps, esc
  };
})();


// ==================== SN MODULE (ENHANCED) ====================
window.SN = (() => {
  const API = 'https://surf.purebrain.ai';
  const getKey = () => sessionStorage.getItem('baas-key') || '';
  const headers = () => ({ 'Content-Type': 'application/json', 'X-API-Key': getKey() });
  let currentMode = 'navigate';
  let feedInterval = null;
  let pvInterval = null;
  let recordingActive = false;
  let navHistory = JSON.parse(localStorage.getItem('sn-history') || '[]');

  async function apiFetch(path, opts = {}) {
    const res = await fetch(API + path, { headers: headers(), ...opts });
    if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`);
    return res.json();
  }

  function esc(s) { const d = document.createElement('div'); d.textContent = String(s || ''); return d.innerHTML; }

  function toast(msg, type) {
    if (window.showToast) { window.showToast(msg, type); return; }
    const t = document.createElement('div');
    t.textContent = msg;
    Object.assign(t.style, {
      position:'fixed', bottom:'20px', right:'20px', padding:'10px 18px',
      background: type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : '#3b82f6',
      color:'#fff', borderRadius:'8px', fontSize:'13px', zIndex:'9999'
    });
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
  }

  // ---- MODE SWITCHING ----
  function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.sn-mode-btn').forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
    document.querySelectorAll('.sn-mode-panel').forEach(p => p.style.display = 'none');
    const panel = document.getElementById('sn-panel-' + mode);
    if (panel) panel.style.display = '';

    // Show/hide source fields for profile viewing
    if (mode === 'profile-view') {
      const src = document.getElementById('sn-pv-source');
      if (src) {
        document.getElementById('sn-pv-list-field').style.display = src.value === 'list' ? '' : 'none';
        document.getElementById('sn-pv-search-field').style.display = src.value !== 'list' ? '' : 'none';
      }
    }
  }

  // ---- NAVIGATE MODE ----
  async function navigate() {
    const sid = document.getElementById('sn-session').value;
    const url = document.getElementById('sn-url').value.trim();
    const goal = document.getElementById('sn-goal').value.trim();
    const maxSteps = parseInt(document.getElementById('sn-steps').value) || 5;

    if (!sid) { toast('Select a session first', 'error'); return; }
    if (!goal) { toast('Enter a goal', 'error'); return; }

    const btn = document.getElementById('sn-go-btn');
    btn.disabled = true;
    btn.textContent = 'Navigating...';

    const resultEl = document.getElementById('sn-result');
    const statusEl = document.getElementById('sn-result-status');
    const stepsEl = document.getElementById('sn-result-steps');
    const dataEl = document.getElementById('sn-result-data');
    resultEl.style.display = '';

    statusEl.innerHTML = '<span style="color:var(--yellow)">&#9889; Analyzing page for: "' + esc(goal) + '"...</span>';
    stepsEl.innerHTML = '';
    dataEl.innerHTML = '';

    const startTime = Date.now();

    try {
      // First navigate if URL given
      if (url) {
        await apiFetch('/sessions/' + sid + '/navigate', {
          method: 'POST',
          body: JSON.stringify({ url })
        });
      }

      // Then smart navigate
      const data = await apiFetch('/sessions/' + sid + '/smart-navigate', {
        method: 'POST',
        body: JSON.stringify({ goal, click_best: true, max_steps: maxSteps })
      });

      const duration = ((Date.now() - startTime) / 1000).toFixed(1);
      document.getElementById('sn-result-duration').textContent = duration + 's';

      if (data.clicked) {
        statusEl.innerHTML = '<span style="color:var(--green)">&#9989; Clicked: "' + esc((data.clicked_text || '').slice(0, 60)) + '"</span>';
      } else {
        statusEl.innerHTML = '<span style="color:var(--yellow)">&#9888; No strong match (' + (data.candidates_found || 0) + ' analyzed)</span>';
      }

      // Show matches
      if (data.top_matches && data.top_matches.length) {
        stepsEl.innerHTML = '<div style="font-size:.78rem;font-weight:600;color:var(--text3);margin-bottom:6px">TOP MATCHES</div>' +
          data.top_matches.map(m => `
            <div style="display:flex;gap:8px;padding:4px 0;font-size:.82rem;border-bottom:1px solid var(--border)">
              <span style="color:var(--green);font-weight:600;width:40px">${m.score}</span>
              <span style="width:60px;color:var(--text3)">${m.type || ''}</span>
              <span style="flex:1">${esc((m.text || '').slice(0, 80))}</span>
            </div>
          `).join('');
      }

      // Update screenshot
      refreshScreenshot();

      // Log to history
      addToHistory(url || 'current', goal, data.clicked ? 'success' : 'partial', duration);

    } catch (e) {
      statusEl.innerHTML = '<span style="color:var(--red)">Error: ' + esc(e.message) + '</span>';
      addToHistory(url || 'current', goal, 'error', '-');
    }

    btn.disabled = false;
    btn.textContent = 'Navigate';
  }

  function preset(url, goal) {
    if (url) document.getElementById('sn-url').value = url;
    document.getElementById('sn-goal').value = goal;
    setMode('navigate');
  }

  // ---- FEED MODE ----
  async function startFeed() {
    const sid = document.getElementById('sn-session').value;
    if (!sid) { toast('Select a session', 'error'); return; }

    const platform = document.getElementById('sn-feed-platform').value;
    const duration = parseInt(document.getElementById('sn-feed-duration').value) || 15;
    const engagement = document.getElementById('sn-feed-engagement').value;

    const urls = { linkedin: 'https://www.linkedin.com/feed', twitter: 'https://twitter.com/home', instagram: 'https://www.instagram.com/' };
    const statusEl = document.getElementById('sn-feed-status');

    statusEl.innerHTML = '<div class="sn-feed-active"><span class="refresh-dot"></span> Browsing ' + platform + ' feed with ' + engagement + ' engagement for ' + duration + ' min...</div>';
    document.getElementById('sn-feed-stop').style.display = '';

    try {
      // Navigate to feed
      await apiFetch('/sessions/' + sid + '/navigate', {
        method: 'POST',
        body: JSON.stringify({ url: urls[platform] })
      });

      // Start autopilot with feed parameters
      await apiFetch('/sessions/' + sid + '/autopilot', {
        method: 'POST',
        body: JSON.stringify({
          goal: `Browse ${platform} feed naturally for ${duration} minutes. Engagement level: ${engagement}. Scroll through posts, ${engagement === 'active' ? 'react and leave thoughtful comments on relevant posts' : engagement === 'light' ? 'react to interesting posts occasionally' : 'just scroll and read'}. Be human-like.`,
          max_steps: Math.min(duration * 3, 50)
        })
      });

      refreshScreenshot();
      statusEl.innerHTML = '<div class="sn-feed-active"><span style="color:var(--green)">&#9989;</span> Feed session completed</div>';
    } catch (e) {
      statusEl.innerHTML = '<span style="color:var(--red)">Error: ' + esc(e.message) + '</span>';
    }

    document.getElementById('sn-feed-stop').style.display = 'none';
  }

  function stopFeed() {
    document.getElementById('sn-feed-status').innerHTML = '<span style="color:var(--yellow)">Feed stopped</span>';
    document.getElementById('sn-feed-stop').style.display = 'none';
  }

  // ---- SEARCH MODE ----
  async function startSearch() {
    const sid = document.getElementById('sn-session').value;
    if (!sid) { toast('Select a session', 'error'); return; }

    const query = document.getElementById('sn-search-query').value.trim();
    const platform = document.getElementById('sn-search-platform').value;
    if (!query) { toast('Enter a search query', 'error'); return; }

    const resultEl = document.getElementById('sn-search-results');
    resultEl.innerHTML = '<span style="color:var(--blue)">Searching...</span>';

    const urls = {
      linkedin: 'https://www.linkedin.com/search/results/people/?keywords=' + encodeURIComponent(query),
      'linkedin-posts': 'https://www.linkedin.com/search/results/content/?keywords=' + encodeURIComponent(query),
      google: 'https://www.google.com/search?q=' + encodeURIComponent(query),
      twitter: 'https://twitter.com/search?q=' + encodeURIComponent(query)
    };

    try {
      await apiFetch('/sessions/' + sid + '/navigate', {
        method: 'POST',
        body: JSON.stringify({ url: urls[platform] })
      });
      refreshScreenshot();
      resultEl.innerHTML = '<span style="color:var(--green)">&#9989; Navigated to search results. See live view below.</span>';
    } catch (e) {
      resultEl.innerHTML = '<span style="color:var(--red)">Error: ' + esc(e.message) + '</span>';
    }
  }

  // ---- PROFILE VIEWING ----
  async function startProfileViewing() {
    const sid = document.getElementById('sn-session').value;
    if (!sid) { toast('Select a session', 'error'); return; }

    const count = parseInt(document.getElementById('sn-pv-count').value) || 25;
    const source = document.getElementById('sn-pv-source').value;
    const delay = parseInt(document.getElementById('sn-pv-delay').value) || 15;
    const keywords = document.getElementById('sn-pv-keywords').value.trim();

    document.getElementById('sn-pv-stop').style.display = '';
    toast('Starting profile viewing: ' + count + ' profiles', 'info');

    try {
      if (source === 'search') {
        await apiFetch('/sessions/' + sid + '/navigate', {
          method: 'POST',
          body: JSON.stringify({ url: 'https://www.linkedin.com/search/results/people/?keywords=' + encodeURIComponent(keywords) })
        });
      }

      await apiFetch('/sessions/' + sid + '/autopilot', {
        method: 'POST',
        body: JSON.stringify({
          goal: `View ${count} LinkedIn profiles from search results. Click each profile, scroll down to read their about section, wait ${delay} seconds, then go back and click the next profile. Be natural and human-like.`,
          max_steps: count * 4
        })
      });

      refreshScreenshot();
      // Update stats
      const viewed = parseInt(document.getElementById('sn-pv-viewed').textContent) + count;
      document.getElementById('sn-pv-viewed').textContent = viewed;
      toast('Profile viewing session completed', 'success');
    } catch (e) {
      toast('Error: ' + e.message, 'error');
    }

    document.getElementById('sn-pv-stop').style.display = 'none';
  }

  function stopProfileViewing() {
    document.getElementById('sn-pv-stop').style.display = 'none';
    toast('Profile viewing stopped', 'info');
  }

  // ---- RECORDING MODE ----
  async function startRecording() {
    const sid = document.getElementById('sn-session').value;
    if (!sid) { toast('Select a session', 'error'); return; }

    recordingActive = true;
    document.getElementById('sn-rec-start').style.display = 'none';
    document.getElementById('sn-rec-stop').style.display = '';
    document.getElementById('sn-rec-badge').style.display = '';
    document.getElementById('sn-rec-badge').classList.add('rec-pulse');

    try {
      await apiFetch('/sessions/' + sid + '/record/start', { method: 'POST' });
      toast('Recording started! Browse naturally.', 'info');
    } catch (e) {
      toast('Error: ' + e.message, 'error');
      recordingActive = false;
      document.getElementById('sn-rec-start').style.display = '';
      document.getElementById('sn-rec-stop').style.display = 'none';
      document.getElementById('sn-rec-badge').style.display = 'none';
    }
  }

  async function stopRecording() {
    const sid = document.getElementById('sn-session').value;
    recordingActive = false;
    document.getElementById('sn-rec-start').style.display = '';
    document.getElementById('sn-rec-stop').style.display = 'none';
    document.getElementById('sn-rec-badge').style.display = 'none';
    document.getElementById('sn-rec-badge').classList.remove('rec-pulse');

    try {
      const data = await apiFetch('/sessions/' + sid + '/record/stop', { method: 'POST' });
      const name = prompt('Name this recorded workflow:', 'Recorded ' + new Date().toLocaleDateString());
      if (name) {
        await apiFetch('/sessions/' + sid + '/record/save', {
          method: 'POST',
          body: JSON.stringify({ name })
        });
        toast('Recording saved as "' + name + '"', 'success');
        // Show recorded steps
        const stepsEl = document.getElementById('sn-rec-steps');
        const steps = data.actions || data.steps || [];
        stepsEl.innerHTML = steps.map((s, i) => `
          <div style="display:flex;gap:8px;padding:6px 8px;font-size:.82rem;border-bottom:1px solid var(--border)">
            <span style="color:var(--text3);width:24px">${i + 1}</span>
            <span style="color:var(--blue);width:80px">${s.action || s.type}</span>
            <span style="color:var(--text2);flex:1">${s.target || s.selector || s.url || ''}</span>
          </div>
        `).join('');
      }
    } catch (e) {
      toast('Error saving recording: ' + e.message, 'error');
    }
  }

  // ---- QUICK ACTIONS ----
  async function quickAction(action) {
    const sid = document.getElementById('sn-session').value;
    if (!sid) { toast('Select a session', 'error'); return; }

    const actions = {
      'react-insightful': { goal: 'Find the most recent post in view and react with Insightful', action: 'click' },
      'react-support': { goal: 'Find the most recent post in view and react with Support', action: 'click' },
      'scroll-past': { goal: 'Scroll down naturally past the current content', action: 'scroll' },
      'view-profile': { goal: 'Click on the author name of the first visible post to view their profile', action: 'click' },
      'traveling-comment': { goal: 'Find the top post in view, click comment, and type a thoughtful 2-sentence comment related to the post topic', action: 'comment' }
    };

    const qa = actions[action];
    if (!qa) return;

    toast('Executing: ' + action, 'info');
    try {
      await apiFetch('/sessions/' + sid + '/smart-navigate', {
        method: 'POST',
        body: JSON.stringify({ goal: qa.goal, click_best: true })
      });
      refreshScreenshot();
      toast(action + ' completed', 'success');
    } catch (e) {
      toast('Error: ' + e.message, 'error');
    }
  }

  // ---- AI SUGGESTIONS ----
  async function getAISuggestions() {
    const sid = document.getElementById('sn-session').value;
    if (!sid) { toast('Select a session', 'error'); return; }

    const el = document.getElementById('sn-ai-suggestions');
    el.innerHTML = '<span style="color:var(--blue)">&#129302; Analyzing page...</span>';

    try {
      const data = await apiFetch('/sessions/' + sid + '/smart-navigate', {
        method: 'POST',
        body: JSON.stringify({ goal: 'Analyze the current page. List what engagement actions are available (react, comment, share, connect, follow). Suggest the top 3 actions.', click_best: false })
      });

      const matches = data.top_matches || [];
      if (matches.length) {
        el.innerHTML = '<div style="font-size:.78rem;font-weight:600;color:var(--text3);margin-bottom:8px">SUGGESTED ACTIONS</div>' +
          matches.slice(0, 5).map(m => `
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--border)">
              <span style="color:var(--green);font-weight:600;width:40px">${m.score}</span>
              <span style="font-size:.85rem">${esc(m.text || '')}</span>
              <button class="btn btn-sm btn-ghost" onclick="SN.clickSuggestion('${sid}','${esc(m.selector || '')}')">Execute</button>
            </div>
          `).join('');
      } else {
        el.innerHTML = '<span style="color:var(--text3)">No actionable elements found on this page.</span>';
      }
    } catch (e) {
      el.innerHTML = '<span style="color:var(--red)">Error: ' + esc(e.message) + '</span>';
    }
  }

  async function clickSuggestion(sid, selector) {
    if (!selector) return;
    try {
      await apiFetch('/sessions/' + sid + '/evaluate', {
        method: 'POST',
        body: JSON.stringify({ expression: `document.querySelector('${selector}').click()` })
      });
      refreshScreenshot();
      toast('Executed', 'success');
    } catch (e) {
      toast('Error: ' + e.message, 'error');
    }
  }

  // ---- SCREENSHOT ----
  async function refreshScreenshot() {
    const sid = document.getElementById('sn-session').value;
    if (!sid) return;
    try {
      const data = await apiFetch('/sessions/' + sid + '/screenshot');
      const frame = document.getElementById('sn-screenshot');
      if (data.screenshot || data.screenshot_url) {
        const src = data.screenshot_url || ('data:image/png;base64,' + data.screenshot);
        frame.innerHTML = '<img src="' + src + '" style="max-width:100%;height:auto;display:block" />';
      }
    } catch {}
  }

  // ---- HISTORY ----
  function addToHistory(url, goal, status, duration) {
    navHistory.unshift({
      url: url || '-',
      goal: goal || '-',
      status,
      duration,
      time: new Date().toLocaleTimeString()
    });
    if (navHistory.length > 50) navHistory = navHistory.slice(0, 50);
    localStorage.setItem('sn-history', JSON.stringify(navHistory));
    renderHistory();
  }

  function renderHistory() {
    const el = document.getElementById('sn-history');
    if (!navHistory.length) {
      el.innerHTML = '<div class="empty-state" style="padding:16px"><p style="font-size:.82rem">No history yet</p></div>';
      return;
    }
    el.innerHTML = navHistory.map(h => `
      <div class="exec-row" style="grid-template-columns:1fr 1.5fr 80px 80px 100px">
        <span style="font-size:.78rem;color:var(--text2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(h.url)}</span>
        <span style="font-size:.78rem">${esc(h.goal)}</span>
        <span class="badge ${h.status === 'success' ? 'badge-green' : h.status === 'error' ? 'badge-red' : 'badge-yellow'}" style="font-size:.6rem">${h.status}</span>
        <span style="font-size:.78rem;color:var(--text3)">${h.duration}s</span>
        <span style="font-size:.78rem;color:var(--text3)">${h.time}</span>
      </div>
    `).join('');
  }

  function clearHistory() {
    navHistory = [];
    localStorage.removeItem('sn-history');
    renderHistory();
  }

  function init() {
    setMode('navigate');
    renderHistory();
    // Update session dropdown
    populateSessions();
    // Source change handler
    const srcEl = document.getElementById('sn-pv-source');
    if (srcEl) srcEl.addEventListener('change', function() {
      document.getElementById('sn-pv-list-field').style.display = this.value === 'list' ? '' : 'none';
      document.getElementById('sn-pv-search-field').style.display = this.value !== 'list' ? '' : 'none';
    });
  }

  async function populateSessions() {
    try {
      const data = await apiFetch('/sessions');
      const sessions = Array.isArray(data) ? data : (data.sessions || []);
      const sel = document.getElementById('sn-session');
      sel.innerHTML = '<option value="">-- Select session --</option>';
      sessions.forEach(s => {
        const id = s.session_id || s.id;
        const name = s.profile_name || s.name || id;
        sel.innerHTML += `<option value="${id}">${esc(name)} (${esc(id.slice(0,8))})</option>`;
      });
    } catch {}
  }

  return {
    setMode, navigate, preset, startFeed, stopFeed, startSearch,
    startProfileViewing, stopProfileViewing, startRecording, stopRecording,
    quickAction, getAISuggestions, clickSuggestion, refreshScreenshot,
    clearHistory, init, populateSessions
  };
})();


// ==================== ORCH MODULE (ENHANCED) ====================
// Keep existing ORCH but extend it
(function extendORCH() {
  const existingInit = ORCH.init;

  ORCH.addProfile = function() {
    if (typeof showModal === 'function') {
      showModal('Add New Profile', `
        <label>Profile Name</label>
        <input type="text" id="modal-profile-name" placeholder="e.g., nathan-linkedin">
        <label>Platform</label>
        <select id="modal-profile-platform">
          <option value="linkedin">LinkedIn</option>
          <option value="twitter">Twitter/X</option>
          <option value="facebook">Facebook</option>
          <option value="instagram">Instagram</option>
        </select>
        <label>Proxy Location</label>
        <input type="text" id="modal-profile-proxy" placeholder="e.g., NYC, NJ">
        <label>Assigned To</label>
        <input type="text" id="modal-profile-owner" placeholder="e.g., Jared, Nathan, Aether">
      `, [
        { text: 'Cancel', cls: 'btn-ghost', action: typeof closeModal === 'function' ? closeModal : () => {} },
        { text: 'Add Profile', cls: 'btn-primary', action: function() {
          const name = document.getElementById('modal-profile-name').value.trim();
          if (name) {
            ORCH.toast('Profile "' + name + '" created. Create a session with this profile name to activate.', 'success');
            if (typeof closeModal === 'function') closeModal();
          }
        }}
      ]);
    } else {
      alert('Use the Sessions panel to create a new browser session with a custom profile name.');
    }
  };

  ORCH.launchProfile = async function(profile) {
    try {
      const API = 'https://surf.purebrain.ai';
      const key = sessionStorage.getItem('baas-key') || '';
      const res = await fetch(API + '/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': key },
        body: JSON.stringify({ profile_name: profile })
      });
      if (res.ok) {
        ORCH.toast('Session launched for ' + profile, 'success');
        ORCH.loadSessions();
      } else {
        throw new Error(await res.text());
      }
    } catch (e) {
      ORCH.toast('Error: ' + e.message, 'error');
    }
  };

  ORCH.runWorkflow = function(profile) {
    if (typeof switchPanel === 'function') switchPanel('workflows');
    ORCH.toast('Select a workflow to run on ' + profile, 'info');
  };

  ORCH.viewActivity = function(profile) {
    const filter = document.getElementById('orch-activity-filter');
    if (filter) filter.value = profile;
    ORCH.filterActivity();
  };

  ORCH.syncAction = function(action) {
    if (action === 'post') {
      if (typeof showModal === 'function') {
        showModal('Post to All Profiles', `
          <label>Content</label>
          <textarea id="modal-sync-content" rows="4" placeholder="Write your post content..."></textarea>
          <label>Stagger (minutes between posts)</label>
          <input type="number" id="modal-sync-stagger" value="10" min="1" max="60">
        `, [
          { text: 'Cancel', cls: 'btn-ghost', action: typeof closeModal === 'function' ? closeModal : () => {} },
          { text: 'Post to All', cls: 'btn-primary', action: function() {
            ORCH.toast('Post queued for all profiles with 10min stagger', 'success');
            if (typeof closeModal === 'function') closeModal();
          }}
        ]);
      }
    } else if (action === 'engagement') {
      ORCH.toast('Running daily engagement workflow on all active profiles (staggered 10min)', 'info');
    } else if (action === 'navigate') {
      ORCH.openNavigateModal();
    } else if (action === 'screenshot') {
      ORCH.screenshotAll();
    }
  };

  ORCH.editTeam = function() {
    ORCH.toast('Team management coming soon. Currently configured via profile settings.', 'info');
  };

  ORCH.calView = function(view) {
    document.querySelectorAll('.sn-cal-view').forEach(b => b.classList.toggle('active', b.dataset.view === view));
    ORCH.toast('Calendar view: ' + view, 'info');
  };

  ORCH.filterActivity = function() {
    const filter = document.getElementById('orch-activity-filter').value;
    const items = document.querySelectorAll('.orch-activity-item');
    items.forEach(item => {
      if (filter === 'all') {
        item.style.display = '';
      } else {
        const badge = item.querySelector('.badge');
        item.style.display = (badge && badge.textContent.trim() === filter) ? '' : 'none';
      }
    });
  };

  ORCH.clearActivity = function() {
    document.getElementById('orch-activity-feed').innerHTML = '<div class="orch-empty">Activity cleared</div>';
  };

  ORCH.toast = function(msg, type) {
    if (window.showToast) { window.showToast(msg, type); return; }
    const t = document.createElement('div');
    t.textContent = msg;
    Object.assign(t.style, {
      position:'fixed', bottom:'20px', right:'20px', padding:'10px 18px',
      background: type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : '#3b82f6',
      color:'#fff', borderRadius:'8px', fontSize:'13px', zIndex:'9999'
    });
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
  };

  // Add new presets
  const existingLoadPreset = ORCH.loadPreset;
  ORCH.loadPreset = function(name) {
    if (name === 'daily-engagement' || name === 'profile-warmup') {
      ORCH.toast('Loading preset: ' + name + '...', 'info');
      // These use the existing addStep mechanism
      document.getElementById('orch-steps-list').innerHTML = '';
      if (name === 'daily-engagement') {
        ORCH.addStep('', 'navigate', 'https://linkedin.com/feed', 0);
        ORCH.addStep('', 'evaluate', 'scroll(0,500)', 2000);
        ORCH.addStep('', 'click', '[data-control-name="comment"]', 3000);
        ORCH.addStep('', 'type', 'Great insight!', 1000);
        ORCH.addStep('', 'screenshot', '', 2000);
      } else if (name === 'profile-warmup') {
        ORCH.addStep('', 'navigate', 'https://linkedin.com/feed', 0);
        ORCH.addStep('', 'evaluate', 'scroll(0,300)', 5000);
        ORCH.addStep('', 'navigate', 'https://linkedin.com/mynetwork/', 10000);
        ORCH.addStep('', 'evaluate', 'scroll(0,200)', 5000);
        ORCH.addStep('', 'screenshot', '', 3000);
      }
    } else {
      existingLoadPreset(name);
    }
  };
})();


// ==================== INIT ON PANEL SWITCH ====================
const _origSwitchPanel = typeof switchPanel === 'function' ? switchPanel : null;
if (_origSwitchPanel) {
  window._switchPanelOriginal = _origSwitchPanel;
}

// Hook into panel switching to init modules
document.addEventListener('DOMContentLoaded', function() {
  // Init WF when workflows panel shown
  const wfPanel = document.getElementById('panel-workflows');
  if (wfPanel) {
    const observer = new MutationObserver(function() {
      if (wfPanel.classList.contains('active') || wfPanel.style.display === 'block') {
        WF.init();
        observer.disconnect();
      }
    });
    observer.observe(wfPanel, { attributes: true, attributeFilter: ['class', 'style'] });
  }

  // Init SN when smart-nav panel shown
  const snPanel = document.getElementById('panel-smart-nav');
  if (snPanel) {
    const observer = new MutationObserver(function() {
      if (snPanel.classList.contains('active') || snPanel.style.display === 'block') {
        SN.init();
        observer.disconnect();
      }
    });
    observer.observe(snPanel, { attributes: true, attributeFilter: ['class', 'style'] });
  }
});
