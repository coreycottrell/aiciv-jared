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

// ---------- H1: Rate limiting (per isolate, per IP) ----------
const LOGIN_FAILED_LIMIT = 5;
const LOGIN_FAILED_WINDOW_MS = 15 * 60 * 1000;
const LOGIN_TOTAL_LIMIT = 20;
const LOGIN_TOTAL_WINDOW_MS = 60 * 60 * 1000;

async function rlCheckD1(bucket, identifier, windowMs, limit, env) {
  const cutoff = new Date(Date.now() - windowMs).toISOString();
  const { results } = await env.DB.prepare(
    "SELECT COUNT(*) AS c FROM rate_limits WHERE bucket = ? AND identifier = ? AND recorded_at > ?"
  ).bind(bucket, identifier, cutoff).all();
  const count = (results && results[0] && results[0].c) || 0;
  if (count >= limit) return false;
  await env.DB.prepare(
    "INSERT INTO rate_limits (bucket, identifier) VALUES (?, ?)"
  ).bind(bucket, identifier).run();
  // Opportunistic cleanup of old entries
  if (Math.random() < 0.1) {
    const purge = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    await env.DB.prepare("DELETE FROM rate_limits WHERE recorded_at < ?").bind(purge).run();
  }
  return true;
}

async function rlRemoveLatest(bucket, identifier, env) {
  // Called after successful login to "uncount" the speculative failed entry
  await env.DB.prepare(
    "DELETE FROM rate_limits WHERE id = (SELECT id FROM rate_limits WHERE bucket = ? AND identifier = ? ORDER BY recorded_at DESC LIMIT 1)"
  ).bind(bucket, identifier).run();
}

const DUMMY_PW_HASH = "0000000000000000000000000000000000000000000000000000000000000000:dead0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";

// ---------- C1: AES-256-GCM encryption for credentials at rest ----------
async function _deriveKey(rawKey) {
  const keyMaterial = await crypto.subtle.importKey("raw", new TextEncoder().encode(rawKey), "PBKDF2", false, ["deriveKey"]);
  const salt = new TextEncoder().encode("purebrain-social-v1");
  return crypto.subtle.deriveKey({ name: "PBKDF2", salt, iterations: 100000, hash: "SHA-256" }, keyMaterial, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
}

async function encryptSecret(plaintext, env) {
  if (!plaintext) return null;
  if (!env.CREDS_ENC_KEY) throw new Error("CREDS_ENC_KEY not configured");
  const key = await _deriveKey(env.CREDS_ENC_KEY);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, new TextEncoder().encode(plaintext));
  const combined = new Uint8Array(iv.length + ciphertext.byteLength);
  combined.set(iv, 0);
  combined.set(new Uint8Array(ciphertext), iv.length);
  return "enc:v1:" + btoa(String.fromCharCode(...combined));
}

async function decryptSecret(encoded, env) {
  if (!encoded) return null;
  if (!encoded.startsWith("enc:v1:")) return encoded;
  if (!env.CREDS_ENC_KEY) throw new Error("CREDS_ENC_KEY not configured");
  const b64 = encoded.slice(7);
  const combined = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  const iv = combined.slice(0, 12);
  const ciphertext = combined.slice(12);
  const key = await _deriveKey(env.CREDS_ENC_KEY);
  const plaintext = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, key, ciphertext);
  return new TextDecoder().decode(plaintext);
}


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
  const ip = request.headers.get("cf-connecting-ip") || "unknown";

  if (!(await rlCheckD1("login_total", ip, LOGIN_TOTAL_WINDOW_MS, LOGIN_TOTAL_LIMIT, env))) {
    return err(429, "too many login attempts - try again later");
  }
  if (!(await rlCheckD1("login_failed", ip, LOGIN_FAILED_WINDOW_MS, LOGIN_FAILED_LIMIT, env))) {
    return err(429, "too many failed attempts - try again in 15 minutes");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const email = (body.email || "").trim().toLowerCase();
  const password = body.password || "";
  if (!email || !password) return err(400, "email and password required");

  const user = await env.DB.prepare(
    "SELECT id, password_hash FROM users WHERE email = ?"
  ).bind(email).first();

  const storedHash = (user && user.password_hash) ? user.password_hash : DUMMY_PW_HASH;
  const passwordOk = await verifyPassword(password, storedHash);
  if (!user || !user.password_hash || !passwordOk) {
    return err(401, "invalid credentials");
  }

  await rlRemoveLatest("login_failed", ip, env);

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
  // Profile ID must include account_handle so a user with multiple handles
  // on the same platform (e.g. @brand1 + @brand2 on twitter) gets isolated
  // browser profiles. Sanitize handle to alphanumeric+underscore for filesystem
  // safety on the BaaS side.
  const handleSlug = String(body.account_handle || "").replace(/[^A-Za-z0-9_-]/g, "_").slice(0, 40) || "default";
  const surfProfileId = body.surf_profile_id || `${sess.user_id}-${body.platform}-${handleSlug}`;

  let encryptedCreds = null;
  let encryptedSession = null;
  if (body.credentials_encrypted) {
    try { encryptedCreds = await encryptSecret(body.credentials_encrypted, env); }
    catch (e) { return err(500, "encryption unavailable: " + e.message); }
  }
  if (body.session_token_encrypted) {
    try { encryptedSession = await encryptSecret(body.session_token_encrypted, env); }
    catch (e) { return err(500, "encryption unavailable: " + e.message); }
  }

  try {
    await env.DB.prepare(
      `INSERT INTO social_accounts (id, user_id, platform, account_handle, account_display_name, auth_type, credentials_encrypted, session_token_encrypted, surf_profile_id, health_status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      id, sess.user_id, body.platform, body.account_handle,
      body.account_display_name || body.account_handle,
      body.auth_type,
      encryptedCreds,
      encryptedSession,
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

// Billing tier → max AI partners per user
const PARTNER_LIMITS = {
  free: 1,
  team_member: 3,
  pro: 3,
  founder: 999,
  team: 999,
  enterprise: 999,
  system: 999
};

async function handleCreatePartner(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  if (!body.partner_name) return err(400, "partner_name required");

  // v1.1: mode is 'poll' (default) or 'webhook'. Poll requires no partner_endpoint.
  const mode = body.mode === "webhook" ? "webhook" : "poll";
  if (mode === "webhook" && !body.partner_endpoint) {
    return err(400, "partner_endpoint required for webhook mode");
  }

  // Billing enforcement
  const limit = PARTNER_LIMITS[sess.billing_tier] || PARTNER_LIMITS.free;
  const countRow = await env.DB.prepare(
    "SELECT COUNT(*) AS c FROM ai_partners WHERE user_id = ?"
  ).bind(sess.user_id).first();
  const currentCount = (countRow && countRow.c) || 0;
  if (currentCount >= limit) {
    return err(402, `AI partner limit reached (${currentCount}/${limit}). Upgrade plan to add more.`);
  }

  const id = newId();
  // For poll mode we mint a dedicated long-lived bearer (separate from user session)
  // so the partner can poll even after the user logs out.
  let pollToken = null;
  let pollTokenHash = null;
  if (mode === "poll") {
    pollToken = "pp_" + (crypto.randomUUID().replace(/-/g, "") + crypto.randomUUID().replace(/-/g, "")).slice(0, 48);
    // Hash for storage (same pattern as session tokens)
    try {
      const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(pollToken));
      pollTokenHash = Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, "0")).join("");
    } catch (e) {
      return err(500, "token mint failed");
    }
  }

  try {
    await env.DB.prepare(
      `INSERT INTO ai_partners (id, user_id, partner_name, partner_endpoint, api_key_encrypted, voice_profile, mode, poll_token_hash)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      id, sess.user_id, body.partner_name,
      body.partner_endpoint || null,
      body.api_key_encrypted || null,
      body.voice_profile ? JSON.stringify(body.voice_profile) : null,
      mode,
      pollTokenHash
    ).run();
  } catch (e) {
    if (String(e.message || e).includes("UNIQUE")) {
      return err(409, "partner with this name already registered for user");
    }
    throw e;
  }

  const partner = await env.DB.prepare(
    "SELECT id, user_id, partner_name, partner_endpoint, voice_profile, mode, created_at FROM ai_partners WHERE id = ?"
  ).bind(id).first();

  const response = {
    partner,
    limit_info: { current: currentCount + 1, max: limit, tier: sess.billing_tier }
  };
  // Only expose the raw poll token ONCE at registration (like AWS access keys).
  // If the partner loses it, they rotate via a future /api/ai_partners/{id}/rotate_token endpoint.
  if (pollToken) {
    response.poll_credentials = { token: pollToken, mode: "poll", note: "Store this bearer securely. Not retrievable later." };
  }
  return json(response, { status: 201 });
}

// ---------- v1.1 Poll endpoints ----------

// Look up a partner by its poll token. Returns {partner, error}.
async function resolvePollPartner(request, env, partnerId) {
  const auth = request.headers.get("authorization") || "";
  const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
  if (!token.startsWith("pp_")) return { error: err(401, "missing or invalid poll token") };
  const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(token));
  const hash = Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, "0")).join("");
  const partner = await env.DB.prepare(
    "SELECT id, user_id, partner_name, mode FROM ai_partners WHERE id = ? AND poll_token_hash = ?"
  ).bind(partnerId, hash).first();
  if (!partner) return { error: err(401, "invalid poll token for this partner") };
  if (partner.mode !== "poll") return { error: err(400, "partner is not in poll mode") };
  // Touch last_polled_at for liveness tracking
  await env.DB.prepare(
    "UPDATE ai_partners SET last_polled_at = ? WHERE id = ?"
  ).bind(nowIso(), partnerId).run();
  return { partner };
}

async function handlePollWork(request, env, partnerId) {
  const { partner, error } = await resolvePollPartner(request, env, partnerId);
  if (error) return error;

  // Atomic claim: grab oldest pending job, mark claimed. SQLite lacks SELECT ... FOR UPDATE,
  // so we pick then UPDATE with WHERE status='pending' to detect races.
  // Expiry = 30 min from now.
  const expiresAt = new Date(Date.now() + 30 * 60 * 1000).toISOString();

  // Find next pending job for this partner
  const row = await env.DB.prepare(
    `SELECT id, job_type, payload, attempts FROM partner_jobs
     WHERE ai_partner_id = ? AND status = 'pending'
     ORDER BY created_at ASC LIMIT 1`
  ).bind(partner.id).first();

  if (!row) return new Response(null, { status: 204 });  // empty queue

  // Atomic claim
  const claim = await env.DB.prepare(
    `UPDATE partner_jobs SET status = 'claimed', claimed_at = ?, expires_at = ?, attempts = attempts + 1
     WHERE id = ? AND status = 'pending'`
  ).bind(nowIso(), expiresAt, row.id).run();

  if (!claim.meta || claim.meta.changes === 0) {
    // Lost race to another poll — return empty, partner will retry
    return new Response(null, { status: 204 });
  }

  return json({
    job_id: row.id,
    job_type: row.job_type,
    payload: row.payload ? JSON.parse(row.payload) : {},
    attempts: row.attempts + 1,
    claimed_at: nowIso(),
    expires_at: expiresAt
  });
}

// ---------- P2 Session Health Monitoring (Chy + Aether + Morphe) ----------
//
// POST /api/surf/heartbeat  — Aether's probe service writes here after probing BaaS
// GET  /api/surf/health/:account_id — dashboard reads latest health status
//
// Stateful writes: heartbeat rows only inserted when status CHANGES vs previous.
// Side effect: updates social_accounts.health_status + last_verified_at on any probe.

// Optional: service auth for the probe. Set SURF_PROBE_TOKEN in worker env.
// If unset, endpoint allows unauthenticated writes (suitable for same-VPC trusted service).
async function handleSurfHeartbeat(request, env) {
  // Optional service-token gate (probe service → worker)
  const expected = env.SURF_PROBE_TOKEN;
  if (expected) {
    const auth = request.headers.get("authorization") || "";
    const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
    if (token !== expected) return err(401, "invalid probe token");
  }

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  // Accept either {session_id} (= surf_profile_id on BaaS) or {social_account_id}
  let account = null;
  if (body.social_account_id) {
    account = await env.DB.prepare(
      "SELECT id, health_status FROM social_accounts WHERE id = ?"
    ).bind(body.social_account_id).first();
  } else if (body.session_id) {
    account = await env.DB.prepare(
      "SELECT id, health_status FROM social_accounts WHERE surf_profile_id = ?"
    ).bind(body.session_id).first();
  }
  if (!account) return err(404, "account not found for session/account id");

  const status = body.status;
  const allowed = ["healthy", "captcha_pending", "stale", "locked", "failed"];
  if (!allowed.includes(status)) return err(400, `status must be one of ${allowed.join(",")}`);

  // Stateful write: only insert heartbeat row if status CHANGED vs last record
  const lastRow = await env.DB.prepare(
    "SELECT status FROM session_heartbeats WHERE social_account_id = ? ORDER BY checked_at DESC LIMIT 1"
  ).bind(account.id).first();
  const statusChanged = !lastRow || lastRow.status !== status;

  if (statusChanged) {
    await env.DB.prepare(
      `INSERT INTO session_heartbeats (id, social_account_id, status, cookie_age_seconds,
        captcha_detected, ban_detected, http_status, response_time_ms, error_message)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      crypto.randomUUID(),
      account.id,
      status,
      body.cookie_age_seconds ?? null,
      body.captcha_detected ? 1 : 0,
      body.ban_detected ? 1 : 0,
      body.http_status ?? null,
      body.response_time_ms ?? null,
      (body.error_message || "").slice(0, 500) || null
    ).run();
  }

  // Always update social_accounts.health_status + last_verified_at
  await env.DB.prepare(
    "UPDATE social_accounts SET health_status = ?, last_verified_at = ? WHERE id = ?"
  ).bind(status, nowIso(), account.id).run();

  return json({
    status: "recorded",
    status_changed: statusChanged,
    account_id: account.id,
    new_status: status
  });
}

async function handleSurfHealth(request, env, accountId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // User can only see their own accounts
  const account = await env.DB.prepare(
    "SELECT id, platform, account_handle, health_status, last_verified_at, surf_profile_id FROM social_accounts WHERE id = ? AND user_id = ?"
  ).bind(accountId, sess.user_id).first();
  if (!account) return err(404, "account not found or not yours");

  // Latest heartbeat detail
  const latest = await env.DB.prepare(
    `SELECT checked_at, status, cookie_age_seconds, captcha_detected, ban_detected,
            http_status, response_time_ms, error_message
     FROM session_heartbeats WHERE social_account_id = ?
     ORDER BY checked_at DESC LIMIT 1`
  ).bind(account.id).first();

  // Last 10 heartbeats (status transitions, because stateful writes)
  const history = await env.DB.prepare(
    `SELECT checked_at, status, cookie_age_seconds
     FROM session_heartbeats WHERE social_account_id = ?
     ORDER BY checked_at DESC LIMIT 10`
  ).bind(account.id).all();

  return json({
    account,
    latest_heartbeat: latest || null,
    status_transitions: history.results || []
  });
}

async function handlePollResults(request, env, partnerId) {
  const { partner, error } = await resolvePollPartner(request, env, partnerId);
  if (error) return error;

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const { job_id, status, result, error_message } = body;
  if (!job_id) return err(400, "job_id required");
  if (!["completed", "failed"].includes(status)) return err(400, "status must be 'completed' or 'failed'");

  // Verify job belongs to this partner and is claimed
  const job = await env.DB.prepare(
    "SELECT id, status, ai_partner_id, user_id, job_type, attempts, max_attempts FROM partner_jobs WHERE id = ?"
  ).bind(job_id).first();
  if (!job) return err(404, "job not found");
  if (job.ai_partner_id !== partner.id) return err(403, "job belongs to a different partner");
  if (job.status === "completed") return err(409, "job already completed");

  if (status === "completed") {
    await env.DB.prepare(
      `UPDATE partner_jobs SET status = 'completed', completed_at = ?, result = ? WHERE id = ?`
    ).bind(nowIso(), JSON.stringify(result || {}), job_id).run();

    // Side effect: if job_type is generate_week, turn drafts into content_items
    if (job.job_type === "generate_week" && result && Array.isArray(result.drafts)) {
      for (const d of result.drafts) {
        if (!d.platform || !d.body) continue;
        // Find matching social_account for this user + platform
        const acct = await env.DB.prepare(
          "SELECT id FROM social_accounts WHERE user_id = ? AND platform = ? ORDER BY created_at ASC LIMIT 1"
        ).bind(job.user_id, d.platform).first();
        if (!acct) continue;
        await env.DB.prepare(
          `INSERT INTO content_items (id, user_id, social_account_id, platform, status, scheduled_at, body, media_refs, generated_by, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'draft', ?, ?, ?, ?, ?, ?)`
        ).bind(
          crypto.randomUUID(), job.user_id, acct.id, d.platform,
          d.scheduled_at || null, d.body,
          JSON.stringify(d.media_refs || []),
          `ai_partner:${partner.partner_name}`,
          nowIso(), nowIso()
        ).run();
      }
    }
    return json({ status: "recorded" });
  } else {
    // failed — check if retryable
    const willRetry = job.attempts < job.max_attempts;
    await env.DB.prepare(
      `UPDATE partner_jobs SET status = ?, error_message = ?, claimed_at = NULL, expires_at = NULL WHERE id = ?`
    ).bind(
      willRetry ? "pending" : "failed",
      (error_message || "").slice(0, 500),
      job_id
    ).run();
    return json({ status: willRetry ? "requeued" : "failed", attempts: job.attempts, max_attempts: job.max_attempts });
  }
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

// ---------- Trios (multi-tenant) ----------
const TRIO_COLORS = ['#2a93c1','#f1420b','#22c55e','#a770ef','#0ca4b8','#e11d48','#f59e0b','#0a0a0a'];

async function handleListTrios(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  // List trios the user is a member of OR owns
  const { results } = await env.DB.prepare(
    `SELECT DISTINCT t.* FROM trios t
     LEFT JOIN trio_members tm ON tm.trio_id = t.id
     WHERE t.owner_user_id = ? OR tm.member_user_id = ?
     ORDER BY t.created_at DESC`
  ).bind(sess.user_id, sess.user_id).all();
  return json({ trios: results || [] });
}

async function handleCreateTrio(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const name = (body.name || '').trim();
  if (!name) return err(400, "name required");

  const id = newId();
  await env.DB.prepare(
    "INSERT INTO trios (id, owner_user_id, name, description, visibility) VALUES (?, ?, ?, ?, ?)"
  ).bind(id, sess.user_id, name, body.description || null, body.visibility || 'private').run();

  // Owner auto-added as human member
  const ownerMemberId = newId();
  await env.DB.prepare(
    `INSERT INTO trio_members (id, trio_id, member_type, member_user_id, display_name, color, role)
     VALUES (?, ?, 'human', ?, ?, ?, 'owner')`
  ).bind(ownerMemberId, id, sess.user_id, sess.name, '#ffffff').run();

  // If initial members specified, add them
  if (body.ai_partner_ids && Array.isArray(body.ai_partner_ids)) {
    for (let i = 0; i < body.ai_partner_ids.length; i++) {
      const pid = body.ai_partner_ids[i];
      const partner = await env.DB.prepare(
        "SELECT id, partner_name FROM ai_partners WHERE id = ? AND user_id = ?"
      ).bind(pid, sess.user_id).first();
      if (!partner) continue;
      await env.DB.prepare(
        `INSERT INTO trio_members (id, trio_id, member_type, member_partner_id, display_name, color, role)
         VALUES (?, ?, 'ai_partner', ?, ?, ?, 'member')`
      ).bind(newId(), id, partner.id, partner.partner_name, TRIO_COLORS[i % TRIO_COLORS.length], 'member').run();
    }
  }

  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(id).first();
  return json({ trio }, { status: 201 });
}

async function handleGetTrioConfig(request, env, trioId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");

  // Access check: owner OR member
  const access = await env.DB.prepare(
    "SELECT 1 FROM trio_members WHERE trio_id = ? AND member_user_id = ?"
  ).bind(trioId, sess.user_id).first();
  if (trio.owner_user_id !== sess.user_id && !access) return err(403, "forbidden");

  const { results: members } = await env.DB.prepare(
    `SELECT tm.*, ap.partner_endpoint FROM trio_members tm
     LEFT JOIN ai_partners ap ON tm.member_partner_id = ap.id
     WHERE tm.trio_id = ?
     ORDER BY tm.added_at ASC`
  ).bind(trioId).all();

  return json({ trio, members: members || [] });
}

async function handleAddTrioMember(request, env, trioId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");
  if (trio.owner_user_id !== sess.user_id) return err(403, "only owner can add members");

  const memberType = body.member_type || 'ai_partner';
  if (!['human', 'ai_partner'].includes(memberType)) return err(400, "invalid member_type");

  if (memberType === 'ai_partner') {
    if (!body.partner_id) return err(400, "partner_id required");
    const partner = await env.DB.prepare(
      "SELECT id, partner_name FROM ai_partners WHERE id = ? AND user_id = ?"
    ).bind(body.partner_id, sess.user_id).first();
    if (!partner) return err(404, "partner not found or not owned");

    const countRow = await env.DB.prepare(
      "SELECT COUNT(*) AS c FROM trio_members WHERE trio_id = ? AND member_type = 'ai_partner'"
    ).bind(trioId).first();
    const color = TRIO_COLORS[((countRow && countRow.c) || 0) % TRIO_COLORS.length];

    const id = newId();
    try {
      await env.DB.prepare(
        `INSERT INTO trio_members (id, trio_id, member_type, member_partner_id, display_name, color)
         VALUES (?, ?, 'ai_partner', ?, ?, ?)`
      ).bind(id, trioId, partner.id, body.display_name || partner.partner_name, color).run();
    } catch (e) {
      if (String(e.message || e).includes("UNIQUE")) return err(409, "partner already in trio");
      throw e;
    }
    const member = await env.DB.prepare("SELECT * FROM trio_members WHERE id = ?").bind(id).first();
    return json({ member }, { status: 201 });
  } else {
    if (!body.email) return err(400, "email required for human member");
    const user = await env.DB.prepare(
      "SELECT id, name FROM users WHERE email = ?"
    ).bind(body.email.toLowerCase()).first();
    if (!user) return err(404, "user not found");

    const countRow = await env.DB.prepare(
      "SELECT COUNT(*) AS c FROM trio_members WHERE trio_id = ? AND member_type = 'human'"
    ).bind(trioId).first();
    const color = '#ffffff';

    const id = newId();
    try {
      await env.DB.prepare(
        `INSERT INTO trio_members (id, trio_id, member_type, member_user_id, display_name, color)
         VALUES (?, ?, 'human', ?, ?, ?)`
      ).bind(id, trioId, user.id, body.display_name || user.name, color).run();
    } catch (e) {
      if (String(e.message || e).includes("UNIQUE")) return err(409, "user already in trio");
      throw e;
    }
    const member = await env.DB.prepare("SELECT * FROM trio_members WHERE id = ?").bind(id).first();
    return json({ member }, { status: 201 });
  }
}

async function handleGetTrioMessages(request, env, trioId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // Access check
  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");
  const access = await env.DB.prepare(
    "SELECT 1 FROM trio_members WHERE trio_id = ? AND member_user_id = ?"
  ).bind(trioId, sess.user_id).first();
  if (trio.owner_user_id !== sess.user_id && !access) return err(403, "forbidden");

  // Proxy to trio-comms worker with trio_id param
  if (!env.TRIO_COMMS_TOKEN) return err(503, "trio-comms not configured");

  try {
    const url = `https://trio-comms.in0v8.workers.dev/trio/messages?trio_id=${encodeURIComponent(trioId)}&limit=200`;
    const resp = await fetch(url, {
      headers: { "Authorization": `Bearer ${env.TRIO_COMMS_TOKEN}` }
    });
    const data = await resp.json();
    return json(data, { status: resp.status });
  } catch (e) {
    return err(502, "trio-comms unreachable: " + String(e.message || e).slice(0, 120));
  }
}

async function handleSendTrioMessage(request, env, trioId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  // Access check
  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");
  const access = await env.DB.prepare(
    "SELECT 1 FROM trio_members WHERE trio_id = ? AND member_user_id = ?"
  ).bind(trioId, sess.user_id).first();
  if (trio.owner_user_id !== sess.user_id && !access) return err(403, "forbidden");

  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }
  const content = (body.content || '').trim();
  if (!content) return err(400, "content required");
  if (content.length > 10000) return err(413, "content too long (max 10000 chars)");

  if (!env.TRIO_COMMS_TOKEN) return err(503, "trio-comms not configured");

  try {
    const resp = await fetch("https://trio-comms.in0v8.workers.dev/trio/message", {
      method: "POST",
      headers: { "Authorization": `Bearer ${env.TRIO_COMMS_TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify({ content, trio_id: trioId })
    });
    const data = await resp.json();
    return json(data, { status: resp.status });
  } catch (e) {
    return err(502, "trio-comms unreachable: " + String(e.message || e).slice(0, 120));
  }
}

async function handleUpdateTrioMember(request, env, trioId, memberId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  let body;
  try { body = await request.json(); } catch { return err(400, "invalid json"); }

  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");
  if (trio.owner_user_id !== sess.user_id) return err(403, "only owner can update members");

  const member = await env.DB.prepare("SELECT * FROM trio_members WHERE id = ? AND trio_id = ?").bind(memberId, trioId).first();
  if (!member) return err(404, "member not found");

  const allowed = ["display_name", "color", "role"];
  const updates = {};
  for (const k of allowed) if (k in body) updates[k] = body[k];
  if (Object.keys(updates).length === 0) return err(400, "no valid fields");

  // Color format validation (#RRGGBB or #RRGGBBAA or #RGB)
  if (updates.color && !/^#[0-9A-Fa-f]{3,8}$/.test(updates.color)) {
    return err(400, "color must be hex like #f1420b");
  }

  // Role change: only owner can promote/demote, can't demote self from owner
  if (updates.role && member.role === 'owner' && updates.role !== 'owner') {
    return err(400, "cannot demote owner role");
  }

  const setClauses = Object.keys(updates).map(k => `${k} = ?`);
  const args = [...Object.values(updates), memberId];
  await env.DB.prepare(`UPDATE trio_members SET ${setClauses.join(", ")} WHERE id = ?`).bind(...args).run();

  const updated = await env.DB.prepare("SELECT * FROM trio_members WHERE id = ?").bind(memberId).first();
  return json({ member: updated });
}

async function handleRemoveTrioMember(request, env, trioId, memberId) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  const trio = await env.DB.prepare("SELECT * FROM trios WHERE id = ?").bind(trioId).first();
  if (!trio) return err(404, "trio not found");
  if (trio.owner_user_id !== sess.user_id) return err(403, "only owner can remove members");

  const member = await env.DB.prepare("SELECT * FROM trio_members WHERE id = ? AND trio_id = ?").bind(memberId, trioId).first();
  if (!member) return err(404, "member not found");
  if (member.role === 'owner') return err(400, "cannot remove owner");

  await env.DB.prepare("DELETE FROM trio_members WHERE id = ?").bind(memberId).run();
  return json({ status: "removed" });
}

// ---------- R2 uploads ----------
const UPLOAD_MAX_SIZE = 10 * 1024 * 1024; // 10MB
const UPLOAD_ALLOWED_MIMES = /^(image\/(jpeg|png|gif|webp|svg\+xml)|video\/(mp4|webm)|application\/pdf)$/;
// DEPRECATED 2026-05-04: R2 public domain broken. Use proxy.
// const R2_PUBLIC_DOMAIN = "pub-8f8cf3b34e354e108283ed11c59db125.r2.dev";
const MEDIA_PROXY_BASE = "https://social.purebrain.ai/media";

async function handleUpload(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;

  if (!env.UPLOADS) return err(503, "R2 storage not bound");

  const contentLength = parseInt(request.headers.get("content-length") || "0");
  if (contentLength > UPLOAD_MAX_SIZE) return err(413, "file too large (max 10MB)");

  let formData;
  try { formData = await request.formData(); }
  catch { return err(400, "multipart form data required"); }

  const file = formData.get("file");
  if (!file || typeof file === "string") return err(400, "'file' field required");

  const mime = file.type || "application/octet-stream";
  if (!UPLOAD_ALLOWED_MIMES.test(mime)) {
    return err(415, "unsupported file type: " + mime);
  }

  const size = file.size;
  if (size > UPLOAD_MAX_SIZE) return err(413, "file too large (max 10MB)");

  const origName = (file.name || "upload").replace(/[^A-Za-z0-9._-]/g, "_").slice(0, 100);
  const timestamp = Date.now();
  const rand = crypto.randomUUID().slice(0, 8);
  const key = `${sess.user_id}/${timestamp}-${rand}-${origName}`;

  try {
    const arrayBuffer = await file.arrayBuffer();
    await env.UPLOADS.put(key, arrayBuffer, {
      httpMetadata: { contentType: mime },
      customMetadata: { uploaded_by: sess.user_id, original_name: origName }
    });
  } catch (e) {
    return err(500, "upload failed: " + String(e.message || e).slice(0, 200));
  }

  const publicUrl = `${MEDIA_PROXY_BASE}/${encodeURI(key)}`;

  return json({
    key,
    url: publicUrl,
    mime,
    size,
    original_name: origName,
    uploaded_at: nowIso()
  }, { status: 201 });
}

async function handleReadyFeed(request, env) {
  const { error, sess } = await requireAuth(request, env);
  if (error) return error;
  if (sess.role !== "system") return err(403, "forbidden - router (system) access only");

  const now = nowIso();
  const { results } = await env.DB.prepare(
    `SELECT ci.*, sa.account_handle, sa.auth_type, sa.surf_profile_id,
            sa.credentials_encrypted, sa.session_token_encrypted
     FROM content_items ci JOIN social_accounts sa ON ci.social_account_id = sa.id
     WHERE ci.status = 'scheduled' AND ci.scheduled_at <= ?
     ORDER BY ci.scheduled_at ASC LIMIT 50`
  ).bind(now).all();

  const ready = [];
  for (const r of results || []) {
    try {
      if (r.credentials_encrypted) r.credentials_plain = await decryptSecret(r.credentials_encrypted, env);
      if (r.session_token_encrypted) r.session_token_plain = await decryptSecret(r.session_token_encrypted, env);
    } catch (e) {
      r.decryption_error = String(e.message || e).slice(0, 200);
    }
    delete r.credentials_encrypted;
    delete r.session_token_encrypted;
    ready.push(r);
  }
  return json({ ready });
}

// ---------- CORS ----------
function corsHeaders(origin) {
  const allowed = [
    "https://purebrain.ai",
    "https://social.purebrain.ai",
    "https://chy-jared.app.purebrain.ai",
    "https://portal.purebrain.ai",
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
      } else if (method === "GET" && path.startsWith("/api/ai_partners/") && path.endsWith("/jobs")) {
        // v1.1 poll mode — claim next pending job
        const partnerId = path.slice("/api/ai_partners/".length, -"/jobs".length);
        response = await handlePollWork(request, env, partnerId);
      } else if (method === "POST" && path.startsWith("/api/ai_partners/") && path.endsWith("/results")) {
        // v1.1 poll mode — submit completed job
        const partnerId = path.slice("/api/ai_partners/".length, -"/results".length);
        response = await handlePollResults(request, env, partnerId);
      } else if (method === "POST" && path === "/api/surf/heartbeat") {
        // P2 — probe service writes session health
        response = await handleSurfHeartbeat(request, env);
      } else if (method === "GET" && path.startsWith("/api/surf/health/")) {
        // P2 — dashboard reads health for an account
        const accountId = path.slice("/api/surf/health/".length);
        response = await handleSurfHealth(request, env, accountId);
      } else if (method === "GET" && path === "/api/trios") {
        response = await handleListTrios(request, env);
      } else if (method === "POST" && path === "/api/trios") {
        response = await handleCreateTrio(request, env);
      } else if (method === "GET" && path.startsWith("/api/trios/") && !path.endsWith("/members") && !path.endsWith("/messages") && !path.endsWith("/message")) {
        const trioId = path.slice("/api/trios/".length);
        response = await handleGetTrioConfig(request, env, trioId);
      } else if (method === "POST" && path.startsWith("/api/trios/") && path.endsWith("/members")) {
        const trioId = path.slice("/api/trios/".length, -"/members".length);
        response = await handleAddTrioMember(request, env, trioId);
      } else if (method === "DELETE" && path.startsWith("/api/trios/") && path.includes("/members/")) {
        const [_, __, ___, trioId, ____, memberId] = path.split("/");
        response = await handleRemoveTrioMember(request, env, trioId, memberId);
      } else if (method === "PATCH" && path.startsWith("/api/trios/") && path.includes("/members/")) {
        const [_, __, ___, trioId, ____, memberId] = path.split("/");
        response = await handleUpdateTrioMember(request, env, trioId, memberId);
      } else if (method === "GET" && path.startsWith("/api/trios/") && path.endsWith("/messages")) {
        const trioId = path.slice("/api/trios/".length, -"/messages".length);
        response = await handleGetTrioMessages(request, env, trioId);
      } else if (method === "POST" && path.startsWith("/api/trios/") && path.endsWith("/message")) {
        const trioId = path.slice("/api/trios/".length, -"/message".length);
        response = await handleSendTrioMessage(request, env, trioId);
      } else if (method === "POST" && path === "/api/uploads") {
        response = await handleUpload(request, env);
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
