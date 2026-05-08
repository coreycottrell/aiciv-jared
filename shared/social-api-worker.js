--484a2c40926622eeb17c319cc3e0553723fc154eecfe96d83d019287cc16
Content-Disposition: form-data; name="worker.js"

/**
 * social-api Worker — multi-tenant social posting platform backend
 *
 * D1 binding: env.DB = purebrain-social
 *
 * Endpoints:
 *   GET  /health
 *   POST /api/login                       — email/password → session token
 *   GET  /api/sso/exchange?token=...      — portal SSO handoff
 *   GET  /api/me                          — current user (requires auth)
 *   GET  /api/content                     — list user's content (filters: status, platform, limit)
 *   POST /api/content                     — create draft
 *   PATCH /api/content/:id                — update (edit/approve/reschedule)
 *   GET  /api/content/team                — team aggregate (scheduled+posted only, read-only)
 *   GET  /api/content/ready               — ContentRouter polling (leader/system role only)
 *
 * Auth: bearer token in Authorization header OR social_session cookie
 * Sessions: 12h lifetime, stored in `sessions` table
 *
 * SSO from portal: HMAC-signed {user_id, exp, redirect} → creates local session
 */

const SESSION_DURATION_MS = 12 * 60 * 60 * 1000; // 12h
const PBKDF2_ITER = 100000;

const FRONTEND_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>social · PureBrain</title>
<link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Oswald:wght@500;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#080a12;
  --surface:rgba(255,255,255,0.03);
  --surface-hover:rgba(255,255,255,0.05);
  --border:rgba(255,255,255,0.07);
  --border-focus:rgba(42,147,193,0.45);
  --text:rgba(255,255,255,0.88);
  --text-muted:rgba(255,255,255,0.48);
  --text-dim:rgba(255,255,255,0.28);
  --blue:#2a93c1;
  --orange:#f1420b;
  --green:#22c55e;
  --red:#ef4444;
  --glow-blue:rgba(42,147,193,0.2);
  --glow-orange:rgba(241,66,11,0.18);
}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}
body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;min-height:100vh;min-height:100dvh;overflow-x:hidden;touch-action:manipulation}
body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 70% 50% at 50% -10%,var(--glow-blue),transparent 70%),radial-gradient(ellipse 50% 40% at 80% 100%,var(--glow-orange),transparent 70%);pointer-events:none;z-index:0;animation:drift 18s ease-in-out infinite alternate}
@keyframes drift{0%{opacity:.75}50%{opacity:1}100%{opacity:.75}}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}

.app{position:relative;z-index:1;min-height:100vh;min-height:100dvh;display:flex;flex-direction:column}

/* ---------- AUTH GATE ---------- */
.auth-gate{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;min-height:100dvh;padding:24px;animation:fadeUp .5s ease}
.auth-shell{width:100%;max-width:380px;background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:36px 32px;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}
.auth-logo{font-family:'Oswald',sans-serif;font-size:14px;font-weight:500;letter-spacing:.35em;text-transform:uppercase;text-align:center;color:var(--text-muted);margin-bottom:8px}
.auth-logo .blue{color:var(--blue)}.auth-logo .orange{color:var(--orange)}
.auth-title{font-size:26px;font-weight:800;color:#fff;text-align:center;letter-spacing:-.02em;margin-bottom:8px}
.auth-sub{font-size:13px;color:var(--text-muted);text-align:center;margin-bottom:28px}
.field{margin-bottom:16px}
.field label{display:block;font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--text-muted);margin-bottom:6px}
.field input{width:100%;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:10px;padding:14px 16px;color:#fff;font-family:inherit;font-size:15px;transition:border-color .2s,background .2s}
.field input:focus{outline:none;border-color:var(--border-focus);background:rgba(255,255,255,0.06)}
.btn{display:block;width:100%;background:linear-gradient(135deg,var(--blue),var(--orange));color:#fff;border:none;border-radius:10px;padding:15px;font-family:inherit;font-size:14px;font-weight:700;letter-spacing:.04em;cursor:pointer;transition:transform .15s,box-shadow .2s}
.btn:hover{transform:translateY(-1px);box-shadow:0 8px 24px var(--glow-blue)}
.btn:active{transform:translateY(0)}
.btn:disabled{opacity:.5;cursor:wait}
.auth-error{color:var(--red);font-size:13px;text-align:center;margin-top:12px;min-height:18px}

/* ---------- MAIN APP ---------- */
.topbar{position:sticky;top:0;z-index:10;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);background:rgba(8,10,18,.8);border-bottom:1px solid var(--border);padding:14px 20px;padding-top:max(14px,env(safe-area-inset-top));display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{font-family:'Oswald',sans-serif;font-size:13px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:var(--text)}
.brand .blue{color:var(--blue)}.brand .orange{color:var(--orange)}
.user-chip{display:flex;align-items:center;gap:10px;padding:6px 10px 6px 6px;background:var(--surface);border:1px solid var(--border);border-radius:100px;cursor:pointer;font-size:13px;color:var(--text);transition:border-color .2s}
.user-chip:hover{border-color:var(--border-focus)}
.user-chip .avatar{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--orange));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;color:#fff}

.tabs{display:flex;gap:4px;padding:12px 20px;overflow-x:auto;-webkit-overflow-scrolling:touch;border-bottom:1px solid var(--border)}
.tab{flex-shrink:0;padding:10px 16px;font-size:13px;font-weight:600;color:var(--text-muted);cursor:pointer;border-radius:8px;transition:all .2s;background:transparent;border:1px solid transparent}
.tab:hover{color:var(--text);background:var(--surface-hover)}
.tab.active{color:#fff;background:var(--surface);border-color:var(--border-focus);box-shadow:0 0 0 1px var(--border-focus)}

.panel{display:none;padding:24px 20px 40px;max-width:1100px;margin:0 auto;width:100%}
.panel.active{display:block;animation:fadeUp .35s ease}

/* ---------- CALENDAR (MY CONTENT) ---------- */
.calendar-head{display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px}
.calendar-title{font-size:22px;font-weight:800;letter-spacing:-.01em;color:#fff}
.calendar-sub{font-size:12px;color:var(--text-muted)}
.filter-row{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.chip{padding:7px 14px;font-size:12px;font-weight:600;color:var(--text-muted);background:var(--surface);border:1px solid var(--border);border-radius:100px;cursor:pointer;transition:all .2s}
.chip:hover{color:var(--text);border-color:var(--border-focus)}
.chip.active{color:#fff;background:linear-gradient(135deg,rgba(42,147,193,.2),rgba(241,66,11,.15));border-color:var(--border-focus)}

.timeline{display:flex;flex-direction:column;gap:14px}
.post-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);transition:border-color .2s,transform .2s;animation:fadeUp .3s ease}
.post-card:hover{border-color:var(--border-focus);transform:translateY(-1px)}
.post-meta{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.post-platform{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--text-muted)}
.post-platform .dot{width:8px;height:8px;border-radius:50%}
.dot.linkedin{background:#0a66c2}
.dot.twitter{background:#1d9bf0}
.dot.bluesky{background:#0085ff}
.dot.threads{background:#fff}
.dot.facebook{background:#1877f2}
.dot.instagram{background:#e4405f}
.post-time{font-size:12px;color:var(--text-dim);font-variant-numeric:tabular-nums}
.post-body{font-size:15px;line-height:1.6;color:var(--text);white-space:pre-wrap;margin-bottom:12px}
.post-actions{display:flex;gap:8px;flex-wrap:wrap}
.action-btn{padding:8px 14px;font-size:12px;font-weight:600;border-radius:8px;border:1px solid var(--border);background:transparent;color:var(--text-muted);cursor:pointer;transition:all .15s}
.action-btn:hover{color:#fff;border-color:var(--border-focus)}
.action-btn.approve{color:var(--green);border-color:rgba(34,197,94,.3)}
.action-btn.approve:hover{background:rgba(34,197,94,.1)}
.action-btn.reject{color:var(--red);border-color:rgba(239,68,68,.3)}
.action-btn.reject:hover{background:rgba(239,68,68,.1)}
.status-badge{display:inline-block;padding:3px 10px;font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;border-radius:100px}
.status-draft{background:rgba(255,255,255,.08);color:var(--text-muted)}
.status-scheduled{background:rgba(42,147,193,.15);color:var(--blue)}
.status-posted{background:rgba(34,197,94,.15);color:var(--green)}
.status-failed{background:rgba(239,68,68,.15);color:var(--red)}
.status-pending{background:rgba(241,66,11,.12);color:var(--orange)}

.empty{text-align:center;padding:48px 20px;color:var(--text-dim)}
.empty-icon{font-size:32px;margin-bottom:12px;opacity:.4}
.empty-text{font-size:14px;color:var(--text-muted)}

/* ---------- TEAM VIEW ---------- */
.team-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.team-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:18px;backdrop-filter:blur(12px);transition:border-color .2s,transform .2s}
.team-card:hover{border-color:var(--border-focus);transform:translateY(-2px)}
.team-card-head{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.team-card-avatar{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--orange));display:flex;align-items:center;justify-content:center;font-weight:700;color:#fff;font-size:14px}
.team-card-name{font-size:14px;font-weight:700;color:#fff}
.team-card-email{font-size:11px;color:var(--text-dim)}
.team-card-body{font-size:13px;color:var(--text);line-height:1.5;margin-bottom:10px;-webkit-line-clamp:3;-webkit-box-orient:vertical;display:-webkit-box;overflow:hidden}
.team-card-footer{display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--text-dim)}

/* ---------- ACCOUNTS ---------- */
.account-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.account-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px}
.account-card .dot{flex-shrink:0;width:10px;height:10px;border-radius:50%}
.account-info{flex:1;min-width:0}
.account-platform{font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--text-muted)}
.account-handle{font-size:14px;font-weight:600;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.health-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.health-dot.healthy{background:var(--green);box-shadow:0 0 6px rgba(34,197,94,.5)}
.health-dot.unknown{background:var(--text-dim)}
.health-dot.degraded{background:var(--orange)}
.health-dot.failed{background:var(--red)}

/* ---------- CONNECT ACCOUNT FLOW ---------- */
.connect-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-top:16px}
.connect-btn{padding:18px 14px;background:var(--surface);border:1px solid var(--border);border-radius:12px;cursor:pointer;text-align:center;transition:all .2s}
.connect-btn:hover{border-color:var(--border-focus);background:var(--surface-hover);transform:translateY(-2px)}
.connect-btn .dot{width:12px;height:12px;border-radius:50%;margin:0 auto 8px}
.connect-btn-label{font-size:13px;font-weight:600;color:#fff}

/* ---------- RESPONSIVE ---------- */
@media (max-width:640px){
  .topbar{padding:12px 16px;padding-top:max(12px,env(safe-area-inset-top))}
  .brand{font-size:11px;letter-spacing:.22em}
  .panel{padding:20px 16px 32px}
  .calendar-title{font-size:18px}
  .post-card{padding:16px}
  .post-body{font-size:14px}
  .auth-shell{padding:28px 24px}
}
</style>
</head>
<body>

<div class="app">
  <!-- AUTH GATE (default shown) -->
  <div class="auth-gate" id="auth-gate">
    <div class="auth-shell">
      <div class="auth-logo"><span class="blue">PURE</span><span class="orange">BR</span><span class="blue">AIN</span> · SOCIAL</div>
      <h1 class="auth-title">Welcome</h1>
      <p class="auth-sub">Sign in to your social command center.</p>
      <div class="field">
        <label for="login-email">Email</label>
        <input type="email" id="login-email" autocomplete="email" placeholder="you@example.com">
      </div>
      <div class="field">
        <label for="login-pw">Password</label>
        <input type="password" id="login-pw" autocomplete="current-password" placeholder="••••••••">
      </div>
      <button class="btn" id="login-btn" onclick="login()">Sign in →</button>
      <div class="auth-error" id="login-error"></div>
    </div>
  </div>

  <!-- MAIN APP (hidden until login) -->
  <div id="main-app" style="display:none;flex-direction:column;flex:1">
    <div class="topbar">
      <div class="brand"><span class="blue">PURE</span><span class="orange">BR</span><span class="blue">AIN</span> · SOCIAL</div>
      <div class="user-chip" id="user-chip" onclick="logout()"></div>
    </div>

    <div class="tabs">
      <div class="tab active" data-panel="my-content">My Content</div>
      <div class="tab" data-panel="team">Team</div>
      <div class="tab" data-panel="accounts">Accounts</div>
    </div>

    <!-- PANEL: MY CONTENT -->
    <div class="panel active" id="panel-my-content">
      <div class="calendar-head">
        <div>
          <div class="calendar-title">My Content</div>
          <div class="calendar-sub" id="my-content-count">Loading…</div>
        </div>
      </div>
      <div class="filter-row">
        <div class="chip active" data-filter-status="">All</div>
        <div class="chip" data-filter-status="draft">Drafts</div>
        <div class="chip" data-filter-status="scheduled">Scheduled</div>
        <div class="chip" data-filter-status="posted">Posted</div>
      </div>
      <div class="timeline" id="my-timeline">
        <div class="empty"><div class="empty-icon">·</div><div class="empty-text">Loading your content…</div></div>
      </div>
    </div>

    <!-- PANEL: TEAM -->
    <div class="panel" id="panel-team">
      <div class="calendar-head">
        <div>
          <div class="calendar-title">Team Calendar</div>
          <div class="calendar-sub" id="team-count">Last 7 days across the team</div>
        </div>
      </div>
      <div class="team-grid" id="team-grid">
        <div class="empty"><div class="empty-text">Loading team activity…</div></div>
      </div>
    </div>

    <!-- PANEL: ACCOUNTS -->
    <div class="panel" id="panel-accounts">
      <div class="calendar-head">
        <div>
          <div class="calendar-title">Connected Accounts</div>
          <div class="calendar-sub">Each account is isolated with its own PureSurf profile.</div>
        </div>
      </div>
      <div class="account-list" id="account-list"></div>
      <div style="margin-top:32px">
        <div style="font-size:14px;font-weight:700;color:#fff;margin-bottom:4px">Connect a new account</div>
        <div style="font-size:12px;color:var(--text-muted)">Click a platform to start the connection flow.</div>
        <div class="connect-grid" id="connect-grid"></div>
      </div>
    </div>
  </div>
</div>

<script>
const API = "https://social.purebrain.ai";
let TOKEN = localStorage.getItem("social_token") || "";
let USER = null;
let CURRENT_FILTER_STATUS = "";

function h(tag, attrs={}, children=[]){
  const el = document.createElement(tag);
  for (const [k,v] of Object.entries(attrs)) {
    if (k === "class") el.className = v;
    else if (k === "onclick") el.onclick = v;
    else if (k.startsWith("data-")) el.setAttribute(k,v);
    else el[k] = v;
  }
  for (const c of [].concat(children)) {
    if (typeof c === "string") el.appendChild(document.createTextNode(c));
    else if (c) el.appendChild(c);
  }
  return el;
}

function esc(s){return String(s||"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c]));}

async function api(path, opts={}) {
  const headers = Object.assign({"Content-Type":"application/json"}, opts.headers||{});
  if (TOKEN) headers["Authorization"] = "Bearer " + TOKEN;
  const res = await fetch(API + path, Object.assign({}, opts, {headers, credentials:"include"}));
  if (res.status === 401) { logout(); throw new Error("Session expired — please log in again"); }
  const data = await res.json().catch(()=>({}));
  if (!res.ok) throw new Error(data.error || "HTTP " + res.status);
  return data;
}

async function login() {
  const btn = document.getElementById("login-btn");
  const err = document.getElementById("login-error");
  const email = document.getElementById("login-email").value.trim();
  const pw = document.getElementById("login-pw").value;
  err.textContent = "";
  if (!email || !pw) { err.textContent = "Email and password required."; return; }
  btn.disabled = true; btn.textContent = "Signing in…";
  try {
    const res = await fetch(API + "/api/login", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({email, password: pw})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "login failed");
    TOKEN = data.token;
    localStorage.setItem("social_token", TOKEN);
    await bootApp();
  } catch (e) {
    err.textContent = e.message;
    btn.disabled = false; btn.textContent = "Sign in →";
  }
}

function logout() {
  TOKEN = "";
  localStorage.removeItem("social_token");
  location.reload();
}

async function bootApp() {
  try {
    USER = await api("/api/me");
    document.getElementById("auth-gate").style.display = "none";
    const mainApp = document.getElementById("main-app");
    mainApp.style.display = "flex";
    renderUserChip();
    wireTabs();
    wireFilters();
    await loadMyContent();
    await loadTeamContent();
    await loadAccounts();
  } catch (e) {
    console.warn("boot failed", e);
    logout();
  }
}

function renderUserChip() {
  const chip = document.getElementById("user-chip");
  chip.innerHTML = "";
  const initial = (USER.name || USER.email || "?").charAt(0).toUpperCase();
  chip.appendChild(h("div", {class:"avatar"}, initial));
  chip.appendChild(h("span", {}, USER.name || USER.email));
}

function wireTabs() {
  document.querySelectorAll(".tab").forEach(t => {
    t.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
      document.querySelectorAll(".panel").forEach(x => x.classList.remove("active"));
      t.classList.add("active");
      document.getElementById("panel-" + t.dataset.panel).classList.add("active");
    });
  });
}

function wireFilters() {
  document.querySelectorAll("[data-filter-status]").forEach(c => {
    c.addEventListener("click", () => {
      document.querySelectorAll("[data-filter-status]").forEach(x => x.classList.remove("active"));
      c.classList.add("active");
      CURRENT_FILTER_STATUS = c.dataset.filterStatus;
      loadMyContent();
    });
  });
}

function fmtTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("en-US", {month:"short", day:"numeric", hour:"numeric", minute:"2-digit"});
}

function renderPost(p, showUser=false) {
  const platform = esc(p.platform || "?");
  const statusClass = "status-" + esc(p.status || "draft");
  const timeText = p.scheduled_at ? fmtTime(p.scheduled_at)
                 : p.posted_at ? "Posted " + fmtTime(p.posted_at)
                 : "Draft";

  const card = document.createElement("div");
  card.className = "post-card";

  const meta = document.createElement("div");
  meta.className = "post-meta";
  meta.innerHTML = \`
    <div class="post-platform"><span class="dot \${platform}"></span>\${platform}\${showUser ? " · " + esc(p.user_name||"") : ""}</div>
    <div style="display:flex;align-items:center;gap:10px">
      <span class="status-badge \${statusClass}">\${esc(p.status||"draft")}</span>
      <span class="post-time">\${esc(timeText)}</span>
    </div>\`;
  card.appendChild(meta);

  const body = document.createElement("div");
  body.className = "post-body";
  body.textContent = p.body || "";
  card.appendChild(body);

  if (p.post_url) {
    const link = document.createElement("a");
    link.href = p.post_url; link.target = "_blank";
    link.style.cssText = "display:inline-block;font-size:12px;color:var(--blue);margin-top:4px";
    link.textContent = "View on " + platform + " →";
    card.appendChild(link);
  }

  if (!showUser && (p.status === "draft" || p.status === "pending_approval")) {
    const actions = document.createElement("div");
    actions.className = "post-actions";
    const approveBtn = h("button", {class:"action-btn approve", onclick: () => approveItem(p.id)}, "Approve & schedule");
    const rejectBtn  = h("button", {class:"action-btn reject",  onclick: () => rejectItem(p.id)}, "Reject");
    actions.appendChild(approveBtn); actions.appendChild(rejectBtn);
    card.appendChild(actions);
  }

  return card;
}

async function loadMyContent() {
  const qs = CURRENT_FILTER_STATUS ? ("?status=" + CURRENT_FILTER_STATUS) : "";
  const data = await api("/api/content" + qs);
  const tl = document.getElementById("my-timeline");
  tl.innerHTML = "";
  const items = data.items || [];
  document.getElementById("my-content-count").textContent =
    items.length + " item" + (items.length === 1 ? "" : "s") + (CURRENT_FILTER_STATUS ? " · filtered" : "");

  if (!items.length) {
    tl.innerHTML = \`<div class="empty"><div class="empty-icon">·</div><div class="empty-text">No content yet. Your AI partner will generate drafts each Sunday.</div></div>\`;
    return;
  }
  items.forEach(p => tl.appendChild(renderPost(p, false)));
}

async function loadTeamContent() {
  const data = await api("/api/content/team?days=7");
  const grid = document.getElementById("team-grid");
  grid.innerHTML = "";
  const items = (data.items || []).slice(0, 24);
  document.getElementById("team-count").textContent =
    items.length + " item" + (items.length === 1 ? "" : "s") + " from the team (last 7 days)";
  if (!items.length) {
    grid.innerHTML = \`<div class="empty"><div class="empty-text">No team activity in the last 7 days.</div></div>\`;
    return;
  }
  items.forEach(p => grid.appendChild(renderPost(p, true)));
}

async function loadAccounts() {
  const data = await api("/api/social_accounts");
  const list = document.getElementById("account-list");
  list.innerHTML = "";
  const accounts = data.accounts || [];
  if (!accounts.length) {
    list.innerHTML = \`<div class="empty" style="grid-column:1/-1"><div class="empty-text">No accounts connected yet.</div></div>\`;
  } else {
    accounts.forEach(a => {
      const card = document.createElement("div");
      card.className = "account-card";
      const healthClass = a.health_status === "healthy" ? "healthy" : a.health_status === "degraded" ? "degraded" : a.health_status === "failed" ? "failed" : "unknown";
      card.innerHTML = \`
        <span class="dot \${esc(a.platform)}"></span>
        <div class="account-info">
          <div class="account-platform">\${esc(a.platform)}</div>
          <div class="account-handle">@\${esc(a.account_handle)}</div>
        </div>
        <span class="health-dot \${healthClass}" title="\${esc(a.health_status||'unknown')}"></span>\`;
      list.appendChild(card);
    });
  }

  // Connect grid
  const platforms = ["linkedin","twitter","bluesky","threads","instagram","facebook"];
  const connected = new Set(accounts.map(a => a.platform));
  const connectGrid = document.getElementById("connect-grid");
  connectGrid.innerHTML = "";
  platforms.forEach(pl => {
    if (connected.has(pl)) return;
    const btn = document.createElement("div");
    btn.className = "connect-btn";
    btn.innerHTML = \`<div class="dot \${pl}"></div><div class="connect-btn-label">\${pl.charAt(0).toUpperCase()+pl.slice(1)}</div>\`;
    btn.onclick = () => connectAccount(pl);
    connectGrid.appendChild(btn);
  });
}

async function connectAccount(platform) {
  const handle = prompt("Your " + platform + " handle / username:");
  if (!handle) return;
  try {
    await api("/api/social_accounts", {
      method:"POST",
      body: JSON.stringify({platform, account_handle: handle, auth_type: "puresurf_session"})
    });
    await loadAccounts();
  } catch (e) { alert(e.message); }
}

async function approveItem(id) {
  try {
    await api("/api/content/" + id, {
      method:"PATCH",
      body: JSON.stringify({status:"scheduled"})
    });
    await loadMyContent();
  } catch (e) { alert(e.message); }
}

async function rejectItem(id) {
  const reason = prompt("Why reject this draft?");
  if (reason === null) return;
  try {
    await api("/api/content/" + id, {
      method:"PATCH",
      body: JSON.stringify({status:"rejected", rejection_reason: reason || ""})
    });
    await loadMyContent();
  } catch (e) { alert(e.message); }
}

// Allow Enter in password field
document.getElementById("login-pw").addEventListener("keydown", e => {
  if (e.key === "Enter") login();
});

// Boot
if (TOKEN) {
  bootApp().catch(()=>{});
}
</script>

</body>
</html>
`;


// ---------- Helpers ----------
function json(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status || 200,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
      ...(init.headers || {}),
    },
  });
}

function err(status, message) {
  return json({ error: message }, { status });
}

function newId() {
  return crypto.randomUUID();
}

function nowIso() {
  return new Date().toISOString();
}

function expiresAt(ms = SESSION_DURATION_MS) {
  return new Date(Date.now() + ms).toISOString();
}

async function sha256(s) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
}

// PBKDF2 for passwords
async function hashPassword(password, saltHex = null) {
  const encoder = new TextEncoder();
  const salt = saltHex
    ? Uint8Array.from(saltHex.match(/.{2}/g).map(h => parseInt(h, 16)))
    : crypto.getRandomValues(new Uint8Array(16));
  const keyMaterial = await crypto.subtle.importKey(
    "raw", encoder.encode(password), "PBKDF2", false, ["deriveBits"]
  );
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: PBKDF2_ITER, hash: "SHA-256" },
    keyMaterial, 256
  );
  const hashArr = new Uint8Array(bits);
  const saltHexOut = Array.from(salt).map(b => b.toString(16).padStart(2, "0")).join("");
  const hashHex = Array.from(hashArr).map(b => b.toString(16).padStart(2, "0")).join("");
  return `${saltHexOut}:${hashHex}`;
}

async function verifyPassword(password, stored) {
  const [saltHex, expectedHash] = stored.split(":");
  if (!saltHex || !expectedHash) return false;
  const rehashed = await hashPassword(password, saltHex);
  return rehashed.split(":")[1] === expectedHash;
}

// HMAC verify for portal SSO
async function verifyHmacSignature(payloadB64, signatureHex, secret) {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(payloadB64));
  const sigHex = Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2, "0")).join("");
  return sigHex === signatureHex;
}

// ---------- Auth ----------
async function getSession(request, env) {
  let token = "";
  const auth = request.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ")) token = auth.slice(7);
  if (!token) {
    const cookies = request.headers.get("cookie") || "";
    const m = cookies.match(/social_session=([^;]+)/);
    if (m) token = m[1];
  }
  if (!token) return null;

  // System API key (ContentRouter M2M auth) — synthetic system session
  if (env.ROUTER_API_KEY && token === env.ROUTER_API_KEY) {
    return {
      user_id: "system",
      email: "router@system",
      name: "ContentRouter",
      team_id: "system",
      role: "system",
      billing_tier: "system",
      expires_at: "9999-12-31T23:59:59Z"
    };
  }

  const row = await env.DB.prepare(
    `SELECT s.token, s.user_id, s.expires_at, u.email, u.name, u.team_id, u.role, u.billing_tier
     FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ?`
  ).bind(token).first();

  if (!row) return null;
  if (row.expires_at < nowIso()) return null;
  return row;
}

async function requireAuth(request, env) {
  const sess = await getSession(request, env);
  if (!sess) return { error: err(401, "unauthorized"), sess: null };
  return { error: null, sess };
}

async function createSession(userId, request, env) {
  const token = crypto.getRandomValues(new Uint8Array(32));
  const tokenStr = Array.from(token).map(b => b.toString(16).padStart(2, "0")).join("");
  const ua = (request.headers.get("user-agent") || "").slice(0, 200);
  const ip = request.headers.get("cf-connecting-ip") || "";
  await env.DB.prepare(
    "INSERT INTO sessions (token, user_id, expires_at, user_agent, ip_address) VALUES (?, ?, ?, ?, ?)"
  ).bind(tokenStr, userId, expiresAt(), ua, ip).run();
  await env.DB.prepare(
    "UPDATE users SET last_login_at = ? WHERE id = ?"
  ).bind(nowIso(), userId).run();
  return tokenStr;
}

function setSessionCookie(response, token) {
  const maxAge = Math.floor(SESSION_DURATION_MS / 1000);
  response.headers.set(
    "set-cookie",
    `social_session=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${maxAge}`
  );
  return response;
}

// ---------- Route handlers ----------
async function handleLogin(request, env) {
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const email = (body.email || "").trim().toLowerCase();
  const password = body.password || "";
  if (!email || !password) return err(400, "email and password required");

  const user = await env.DB.prepare(
    "SELECT id, password_hash FROM users WHERE email = ?"
  ).bind(email).first();
  if (!user || !user.password_hash) return err(401, "invalid credentials");
  if (!(await verifyPassword(password, user.password_hash))) return err(401, "invalid credentials");

  const token = await createSession(user.id, request, env);
  const resp = json({ status: "ok", token });
  return setSessionCookie(resp, token);
}

async function handleSsoExchange(request, env) {
  const url = new URL(request.url);
  const token = url.searchParams.get("token");
  if (!token) return err(400, "token required");

  const [payloadB64, signatureHex] = token.split(".");
  if (!payloadB64 || !signatureHex) return err(400, "malformed token");

  const secret = env.PORTAL_SSO_SECRET || "";
  if (!secret) return err(500, "sso not configured");

  const ok = await verifyHmacSignature(payloadB64, signatureHex, secret);
  if (!ok) return err(401, "invalid signature");

  let payload;
  try {
    const padded = payloadB64 + "=".repeat((4 - payloadB64.length % 4) % 4);
    payload = JSON.parse(atob(padded.replace(/-/g, "+").replace(/_/g, "/")));
  } catch { return err(400, "invalid payload"); }

  if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) return err(401, "token expired");
  if (!payload.user_id) return err(400, "missing user_id");

  const user = await env.DB.prepare("SELECT id FROM users WHERE id = ?").bind(payload.user_id).first();
  if (!user) return err(404, "user not found");

  const sessionToken = await createSession(payload.user_id, request, env);
  const redirectTo = payload.redirect || "/";
  const resp = new Response(null, { status: 302, headers: { location: redirectTo } });
  return setSessionCookie(resp, sessionToken);
}

async function handleMe(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  return json({
    id: sess.user_id,
    email: sess.email,
    name: sess.name,
    role: sess.role,
    team_id: sess.team_id,
    billing_tier: sess.billing_tier,
  });
}

async function handleListContent(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const url = new URL(request.url);
  const status = url.searchParams.get("status");
  const platform = url.searchParams.get("platform");
  const limit = Math.min(parseInt(url.searchParams.get("limit") || "50"), 500);

  let q = "SELECT * FROM content_items WHERE user_id = ?";
  const args = [sess.user_id];
  if (status) { q += " AND status = ?"; args.push(status); }
  if (platform) { q += " AND platform = ?"; args.push(platform); }
  q += " ORDER BY COALESCE(scheduled_at, created_at) DESC LIMIT ?";
  args.push(limit);

  const { results } = await env.DB.prepare(q).bind(...args).all();
  return json({ items: results || [] });
}

async function handleCreateContent(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  for (const f of ["social_account_id", "platform", "body"]) {
    if (!body[f]) return err(400, `${f} required`);
  }

  const acct = await env.DB.prepare(
    "SELECT id FROM social_accounts WHERE id = ? AND user_id = ?"
  ).bind(body.social_account_id, sess.user_id).first();
  if (!acct) return err(404, "social account not found or not owned");

  const id = newId();
  const now = nowIso();
  await env.DB.prepare(
    `INSERT INTO content_items (id, user_id, social_account_id, platform, status, scheduled_at, body, media_refs, generated_by, created_at, updated_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  ).bind(
    id, sess.user_id, body.social_account_id, body.platform,
    body.status || "draft", body.scheduled_at || null, body.body,
    JSON.stringify(body.media_refs || []), body.generated_by || "human",
    now, now
  ).run();

  const item = await env.DB.prepare("SELECT * FROM content_items WHERE id = ?").bind(id).first();
  return json({ item }, { status: 201 });
}

async function handleUpdateContent(request, env, itemId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const allowed = ["body", "media_refs", "scheduled_at", "status", "rejection_reason", "last_error", "retry_count", "routing_decision", "posted_at", "post_url", "verification_status", "performance_metrics"];
  const updates = {};
  for (const k of allowed) if (k in body) updates[k] = body[k];
  if (Object.keys(updates).length === 0) return err(400, "no valid fields");

  const existing = await env.DB.prepare("SELECT user_id FROM content_items WHERE id = ?").bind(itemId).first();
  if (!existing) return err(404, "not found");
  if (existing.user_id !== sess.user_id && sess.role !== "leader" && sess.role !== "system") {
    return err(403, "forbidden");
  }

  // Stringify JSON fields
  for (const k of ["media_refs", "performance_metrics"]) {
    if (k in updates && typeof updates[k] !== "string") updates[k] = JSON.stringify(updates[k]);
  }

  // Auto-set approved_by when status transitions to scheduled
  if (updates.status === "scheduled" && !body.approved_by) {
    updates.approved_by = sess.user_id;
    updates.approved_at = nowIso();
  }

  const setClauses = Object.keys(updates).map(k => `${k} = ?`);
  setClauses.push("updated_at = ?");
  const args = [...Object.values(updates), nowIso(), itemId];

  await env.DB.prepare(
    `UPDATE content_items SET ${setClauses.join(", ")} WHERE id = ?`
  ).bind(...args).run();

  const item = await env.DB.prepare("SELECT * FROM content_items WHERE id = ?").bind(itemId).first();
  return json({ item });
}

async function handleTeamContent(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const url = new URL(request.url);
  const status = url.searchParams.get("status");
  const platform = url.searchParams.get("platform");
  const days = parseInt(url.searchParams.get("days") || "7");
  const limit = Math.min(parseInt(url.searchParams.get("limit") || "200"), 1000);

  const since = new Date(Date.now() - days * 86400 * 1000).toISOString();

  let q = `SELECT ci.*, u.name AS user_name, u.email AS user_email
           FROM content_items ci JOIN users u ON ci.user_id = u.id
           WHERE u.team_id = ?
             AND ci.status IN ('scheduled', 'posting', 'posted', 'failed')
             AND COALESCE(ci.scheduled_at, ci.posted_at, ci.created_at) >= ?`;
  const args = [sess.team_id, since];
  if (status) { q += " AND ci.status = ?"; args.push(status); }
  if (platform) { q += " AND ci.platform = ?"; args.push(platform); }
  q += " ORDER BY COALESCE(ci.scheduled_at, ci.posted_at, ci.created_at) DESC LIMIT ?";
  args.push(limit);

  const { results } = await env.DB.prepare(q).bind(...args).all();
  return json({ items: results || [] });
}

// ---------- Social accounts CRUD ----------
async function handleListAccounts(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const { results } = await env.DB.prepare(
    `SELECT id, user_id, platform, account_handle, account_display_name, auth_type,
            surf_profile_id, last_verified_at, health_status, created_at
     FROM social_accounts WHERE user_id = ? ORDER BY platform, account_handle`
  ).bind(sess.user_id).all();
  return json({ accounts: results || [] });
}

async function handleCreateAccount(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  for (const f of ["platform", "account_handle", "auth_type"]) {
    if (!body[f]) return err(400, `${f} required`);
  }
  if (!["api_oauth", "puresurf_session"].includes(body.auth_type)) {
    return err(400, "auth_type must be api_oauth or puresurf_session");
  }

  const id = newId();
  const surfProfileId = body.surf_profile_id || `${sess.user_id}-${body.platform}`;

  try {
    await env.DB.prepare(
      `INSERT INTO social_accounts (id, user_id, platform, account_handle, account_display_name, auth_type, credentials_encrypted, session_token_encrypted, surf_profile_id, health_status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      id, sess.user_id, body.platform, body.account_handle,
      body.account_display_name || body.account_handle,
      body.auth_type,
      body.credentials_encrypted || null,
      body.session_token_encrypted || null,
      surfProfileId,
      "pending_verification"
    ).run();
  } catch (e) {
    if (String(e.message || e).includes("UNIQUE")) {
      return err(409, "account already exists for this platform/handle");
    }
    throw e;
  }

  const acct = await env.DB.prepare(
    `SELECT id, user_id, platform, account_handle, account_display_name, auth_type, surf_profile_id, health_status, created_at
     FROM social_accounts WHERE id = ?`
  ).bind(id).first();
  return json({ account: acct }, { status: 201 });
}

async function handleDeleteAccount(request, env, accountId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  const row = await env.DB.prepare("SELECT user_id FROM social_accounts WHERE id = ?").bind(accountId).first();
  if (!row) return err(404, "not found");
  if (row.user_id !== sess.user_id && sess.role !== "leader") return err(403, "forbidden");

  // Soft-delete by cascading content_items to cancelled
  await env.DB.prepare(
    "UPDATE content_items SET status = 'cancelled', last_error = 'social account disconnected', updated_at = ? WHERE social_account_id = ? AND status IN ('draft','pending_approval','scheduled')"
  ).bind(nowIso(), accountId).run();

  await env.DB.prepare("DELETE FROM social_accounts WHERE id = ?").bind(accountId).run();
  return json({ status: "deleted" });
}

// ---------- AI Partner registration ----------
async function handleListPartners(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  const { results } = await env.DB.prepare(
    `SELECT id, user_id, partner_name, partner_endpoint, voice_profile, created_at
     FROM ai_partners WHERE user_id = ? ORDER BY partner_name`
  ).bind(sess.user_id).all();
  return json({ partners: results || [] });
}

async function handleCreatePartner(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  for (const f of ["partner_name", "partner_endpoint"]) {
    if (!body[f]) return err(400, `${f} required`);
  }

  const id = newId();
  try {
    await env.DB.prepare(
      `INSERT INTO ai_partners (id, user_id, partner_name, partner_endpoint, api_key_encrypted, voice_profile)
       VALUES (?, ?, ?, ?, ?, ?)`
    ).bind(
      id, sess.user_id, body.partner_name, body.partner_endpoint,
      body.api_key_encrypted || null,
      body.voice_profile ? JSON.stringify(body.voice_profile) : null
    ).run();
  } catch (e) {
    if (String(e.message || e).includes("UNIQUE")) {
      return err(409, "partner with this name already registered for user");
    }
    throw e;
  }

  const partner = await env.DB.prepare(
    "SELECT id, user_id, partner_name, partner_endpoint, voice_profile, created_at FROM ai_partners WHERE id = ?"
  ).bind(id).first();
  return json({ partner }, { status: 201 });
}

// ---------- Password change ----------
async function handleChangePassword(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const { current_password, new_password } = body;
  if (!current_password || !new_password) return err(400, "current_password and new_password required");
  if (new_password.length < 12) return err(400, "new_password must be at least 12 characters");

  const user = await env.DB.prepare(
    "SELECT password_hash FROM users WHERE id = ?"
  ).bind(sess.user_id).first();
  if (!user || !user.password_hash) return err(404, "user not found");
  if (!(await verifyPassword(current_password, user.password_hash))) {
    return err(401, "current password incorrect");
  }

  const newHash = await hashPassword(new_password);
  await env.DB.prepare(
    "UPDATE users SET password_hash = ? WHERE id = ?"
  ).bind(newHash, sess.user_id).run();

  // Invalidate all other sessions for this user (keep current)
  const currentToken = request.headers.get("authorization")?.replace("Bearer ", "")
    || (request.headers.get("cookie") || "").match(/social_session=([^;]+)/)?.[1];
  if (currentToken) {
    await env.DB.prepare(
      "DELETE FROM sessions WHERE user_id = ? AND token != ?"
    ).bind(sess.user_id, currentToken).run();
  }

  return json({ status: "password_changed" });
}

// ---------- Voice profile ----------
async function handleUpdateVoiceProfile(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const { partner_name, voice_profile } = body;
  if (!partner_name || !voice_profile) return err(400, "partner_name and voice_profile required");

  const result = await env.DB.prepare(
    "UPDATE ai_partners SET voice_profile = ? WHERE user_id = ? AND partner_name = ?"
  ).bind(JSON.stringify(voice_profile), sess.user_id, partner_name).run();

  if (result.meta.changes === 0) {
    return err(404, "partner not registered for this user");
  }

  const partner = await env.DB.prepare(
    "SELECT id, partner_name, partner_endpoint, voice_profile FROM ai_partners WHERE user_id = ? AND partner_name = ?"
  ).bind(sess.user_id, partner_name).first();
  return json({ partner });
}

async function handleReadyFeed(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  if (sess.role !== "leader" && sess.role !== "system") return err(403, "forbidden — router access only");

  const now = nowIso();
  const { results } = await env.DB.prepare(
    `SELECT ci.*, sa.account_handle, sa.auth_type, sa.surf_profile_id
     FROM content_items ci JOIN social_accounts sa ON ci.social_account_id = sa.id
     WHERE ci.status = 'scheduled' AND ci.scheduled_at <= ?
     ORDER BY ci.scheduled_at ASC LIMIT 50`
  ).bind(now).all();
  return json({ ready: results || [] });
}

// ---------- CORS ----------
function corsHeaders(origin) {
  const allowed = [
    "https://purebrain.ai",
    "https://social.purebrain.ai",
    "https://chy-jared.app.purebrain.ai",
    "https://777.purebrain.ai"
  ];
  const allowOrigin = allowed.includes(origin) ? origin : allowed[0];
  return {
    "access-control-allow-origin": allowOrigin,
    "access-control-allow-credentials": "true",
    "access-control-allow-methods": "GET, POST, PATCH, DELETE, OPTIONS",
    "access-control-allow-headers": "authorization, content-type",
    "vary": "origin",
  };
}

// ---------- Sunday batch generation (cron) ----------
async function runSundayBatch(env) {
  console.log("[sunday-batch] starting");

  const { results: partners } = await env.DB.prepare(
    `SELECT ap.id, ap.user_id, ap.partner_name, ap.partner_endpoint, ap.api_key_encrypted, ap.voice_profile,
            u.email, u.name
     FROM ai_partners ap JOIN users u ON ap.user_id = u.id`
  ).all();

  const now = new Date();
  const weekStart = new Date(now);
  weekStart.setUTCDate(weekStart.getUTCDate() + (1 - weekStart.getUTCDay())); // next Monday UTC
  const weekEnd = new Date(weekStart);
  weekEnd.setUTCDate(weekEnd.getUTCDate() + 6);

  const weekStartIso = weekStart.toISOString().slice(0, 10);
  const weekEndIso = weekEnd.toISOString().slice(0, 10);

  let totalDrafts = 0;
  let errors = [];

  for (const p of partners || []) {
    try {
      // Get user's social accounts
      const { results: accounts } = await env.DB.prepare(
        "SELECT id, platform, account_handle FROM social_accounts WHERE user_id = ? AND health_status != 'failed'"
      ).bind(p.user_id).all();

      if (!accounts || accounts.length === 0) {
        console.log(`[sunday-batch] skipping ${p.partner_name} for ${p.email} — no connected accounts`);
        continue;
      }

      // Get recent posts for context
      const { results: recent } = await env.DB.prepare(
        `SELECT platform, body, performance_metrics, posted_at FROM content_items
         WHERE user_id = ? AND status = 'posted' AND posted_at IS NOT NULL
         ORDER BY posted_at DESC LIMIT 10`
      ).bind(p.user_id).all();

      // Call AI partner's generate_week endpoint
      const payload = {
        user_id: p.user_id,
        voice_profile: p.voice_profile ? JSON.parse(p.voice_profile) : null,
        social_accounts: accounts.map(a => ({
          platform: a.platform,
          account_handle: a.account_handle,
          social_account_id: a.id
        })),
        week_start: weekStartIso,
        week_end: weekEndIso,
        target_count_per_platform: { linkedin: 7, bluesky: 10, twitter: 5, threads: 3 },
        recent_posted_items: recent || []
      };

      const partnerReq = await fetch(p.partner_endpoint.replace(/\/$/, "") + "/generate_week", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": p.api_key_encrypted ? `Bearer ${p.api_key_encrypted}` : undefined
        },
        body: JSON.stringify(payload)
      });

      if (!partnerReq.ok) {
        errors.push(`${p.partner_name}: HTTP ${partnerReq.status}`);
        continue;
      }

      const response = await partnerReq.json();
      const drafts = response.drafts || [];

      // Insert each draft as content_item with status='draft'
      for (const d of drafts) {
        const acct = accounts.find(a => a.platform === d.platform && a.account_handle === d.social_account_handle)
                  || accounts.find(a => a.platform === d.platform);
        if (!acct) continue;

        await env.DB.prepare(
          `INSERT INTO content_items (id, user_id, social_account_id, platform, status, scheduled_at, body, media_refs, generated_by, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'draft', ?, ?, ?, ?, ?, ?)`
        ).bind(
          crypto.randomUUID(),
          p.user_id,
          acct.id,
          d.platform,
          d.scheduled_at || null,
          d.body,
          JSON.stringify(d.media_refs || []),
          `ai_partner:${p.partner_name}`,
          nowIso(),
          nowIso()
        ).run();
        totalDrafts++;
      }
      console.log(`[sunday-batch] ${p.partner_name} for ${p.email}: +${drafts.length} drafts`);
    } catch (e) {
      errors.push(`${p.partner_name}: ${e.message}`);
    }
  }

  console.log(`[sunday-batch] complete. ${totalDrafts} drafts across ${(partners||[]).length} partners. errors: ${errors.length}`);
  return { totalDrafts, partnerCount: (partners || []).length, errors };
}

// ---------- Main ----------
export default {
  async scheduled(event, env, ctx) {
    // CF cron triggers — cron="0 20 * * 0" = Sunday 8pm UTC
    ctx.waitUntil(runSundayBatch(env));
  },

  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";
    const method = request.method.toUpperCase();
    const origin = request.headers.get("origin") || "";

    if (method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    let response;
    try {
      // Route matching
      if (method === "GET" && (path === "/" || path === "")) {
        response = new Response(FRONTEND_HTML, {
          status: 200,
          headers: {
            "content-type": "text/html; charset=utf-8",
            "cache-control": "no-cache, no-store, must-revalidate"
          }
        });
      } else
      if (method === "GET" && path === "/health") {
        response = json({ status: "ok", service: "social-api", version: "0.1.0" });
      } else if (method === "POST" && path === "/api/login") {
        response = await handleLogin(request, env);
      } else if (method === "GET" && path === "/api/sso/exchange") {
        response = await handleSsoExchange(request, env);
      } else if (method === "GET" && path === "/api/me") {
        response = await handleMe(request, env);
      } else if (method === "GET" && path === "/api/content") {
        response = await handleListContent(request, env);
      } else if (method === "POST" && path === "/api/content") {
        response = await handleCreateContent(request, env);
      } else if (method === "GET" && path === "/api/content/team") {
        response = await handleTeamContent(request, env);
      } else if (method === "GET" && path === "/api/content/ready") {
        response = await handleReadyFeed(request, env);
      } else if (method === "PATCH" && path.startsWith("/api/content/")) {
        const id = path.slice("/api/content/".length);
        response = await handleUpdateContent(request, env, id);
      } else if (method === "GET" && path === "/api/social_accounts") {
        response = await handleListAccounts(request, env);
      } else if (method === "POST" && path === "/api/social_accounts") {
        response = await handleCreateAccount(request, env);
      } else if (method === "DELETE" && path.startsWith("/api/social_accounts/")) {
        const id = path.slice("/api/social_accounts/".length);
        response = await handleDeleteAccount(request, env, id);
      } else if (method === "GET" && path === "/api/ai_partners") {
        response = await handleListPartners(request, env);
      } else if (method === "POST" && path === "/api/ai_partners") {
        response = await handleCreatePartner(request, env);
      } else if (method === "PATCH" && path === "/api/ai_partners/voice_profile") {
        response = await handleUpdateVoiceProfile(request, env);
      } else if (method === "POST" && path === "/api/me/password") {
        response = await handleChangePassword(request, env);
      } else if (method === "POST" && path === "/api/admin/trigger_sunday_batch") {
        // Manual trigger for testing — requires ROUTER_API_KEY or leader role
        const { error: authErr, sess } = await requireAuth(request, env);
        if (authErr) { response = authErr; }
        else if (sess.role !== "leader" && sess.role !== "system") {
          response = err(403, "forbidden — leader/system only");
        } else {
          const result = await runSundayBatch(env);
          response = json({ status: "ok", ...result });
        }
      } else {
        response = err(404, "not found");
      }
    } catch (e) {
      response = err(500, "internal: " + (e.message || String(e)).slice(0, 200));
    }

    // Attach CORS to every response
    const headers = new Headers(response.headers);
    const cors = corsHeaders(origin);
    for (const [k, v] of Object.entries(cors)) headers.set(k, v);
    return new Response(response.body, { status: response.status, headers });
  },
};

--484a2c40926622eeb17c319cc3e0553723fc154eecfe96d83d019287cc16--
