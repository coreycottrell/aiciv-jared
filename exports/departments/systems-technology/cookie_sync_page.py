"""PureSurf Cookie Sync Page — Mobile-friendly proxy login for cookie capture.

Flow:
1. User visits /sync on their phone
2. Enters API key, selects profile + platform
3. PureSurf creates a server-side browser session
4. User types credentials via the sync page
5. PureSurf types them into the real browser
6. Cookies are captured server-side (including httpOnly)
7. User sees confirmation

Mounts on the main FastAPI app via extend_sync_routes(app, sessions, auth, ...).
"""

import asyncio
import base64
import json
import logging
import os
import time
from typing import Dict, Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

log = logging.getLogger('baas.sync')

# ==================== PLATFORM CONFIGS ====================
PLATFORMS = {
    'linkedin': {
        'name': 'LinkedIn',
        'icon': 'fab fa-linkedin',
        'color': '#0A66C2',
        'login_url': 'https://www.linkedin.com/login',
        'selectors': {
            'username': '#username',
            'password': '#password',
            'submit': 'button[type="submit"]',
            '2fa_input': '#input__phone_verification_pin',
            '2fa_submit': '#two-step-submit-button',
        },
        'success_indicators': ['/feed', '/mynetwork', '/in/'],
        'cookie_domain': '.linkedin.com',
        'key_cookies': ['li_at', 'JSESSIONID', 'li_mc'],
    },
    'twitter': {
        'name': 'Twitter / X',
        'icon': 'fab fa-x-twitter',
        'color': '#000000',
        'login_url': 'https://x.com/i/flow/login',
        'selectors': {
            'username': 'input[autocomplete="username"]',
            'password': 'input[autocomplete="current-password"]',
            'submit': '[data-testid="LoginForm_Login_Button"]',
            'username_next': 'button:has-text("Next")',
        },
        'success_indicators': ['/home', '/compose'],
        'cookie_domain': '.x.com',
        'key_cookies': ['auth_token', 'ct0', 'twid'],
    },
    'facebook': {
        'name': 'Facebook',
        'icon': 'fab fa-facebook',
        'color': '#1877F2',
        'login_url': 'https://www.facebook.com/login',
        'selectors': {
            'username': '#email',
            'password': '#pass',
            'submit': 'button[name="login"]',
        },
        'success_indicators': ['/home.php', '/?sk='],
        'cookie_domain': '.facebook.com',
        'key_cookies': ['c_user', 'xs', 'datr'],
    },
    'instagram': {
        'name': 'Instagram',
        'icon': 'fab fa-instagram',
        'color': '#E4405F',
        'login_url': 'https://www.instagram.com/accounts/login/',
        'selectors': {
            'username': 'input[name="username"]',
            'password': 'input[name="password"]',
            'submit': 'button[type="submit"]',
        },
        'success_indicators': ['instagram.com/'],
        'cookie_domain': '.instagram.com',
        'key_cookies': ['sessionid', 'csrftoken', 'ds_user_id'],
    },
    'google': {
        'name': 'Google',
        'icon': 'fab fa-google',
        'color': '#4285F4',
        'login_url': 'https://accounts.google.com/signin',
        'selectors': {
            'username': 'input[type="email"]',
            'password': 'input[type="password"]',
            'username_next': '#identifierNext button',
            'password_next': '#passwordNext button',
        },
        'success_indicators': ['myaccount.google.com', 'mail.google.com'],
        'cookie_domain': '.google.com',
        'key_cookies': ['SID', '__Secure-3PSID', 'SSID'],
    },
}

# ==================== SYNC PAGE HTML ====================
SYNC_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>PureSurf - Cookie Sync</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#080a12;--surface:#0f1219;--card:#151a24;
  --border:#1e2533;--text:#e0e4ec;--dim:#6b7280;
  --accent:#3b82f6;--accent-glow:rgba(59,130,246,0.15);
  --success:#22c55e;--error:#ef4444;--warn:#f59e0b;
}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;min-height:100vh;-webkit-font-smoothing:antialiased}
.container{max-width:480px;margin:0 auto;padding:16px;padding-bottom:env(safe-area-inset-bottom,16px)}
.header{text-align:center;padding:24px 0 16px}
.header h1{font-size:22px;font-weight:700;letter-spacing:-0.3px}
.header h1 span{color:var(--accent)}
.header p{color:var(--dim);font-size:13px;margin-top:4px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:12px}
.card-title{font-size:14px;font-weight:600;color:var(--dim);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px}
label{display:block;font-size:13px;color:var(--dim);margin-bottom:6px}
input[type="text"],input[type="password"],select{
  width:100%;padding:12px 14px;background:var(--surface);border:1px solid var(--border);
  border-radius:8px;color:var(--text);font-size:16px;outline:none;
  -webkit-appearance:none;appearance:none;
}
input:focus,select:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow)}
select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M6 8L1 3h10z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center;padding-right:36px}
.platform-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.platform-btn{
  display:flex;align-items:center;gap:10px;padding:14px;
  background:var(--surface);border:2px solid var(--border);border-radius:10px;
  color:var(--text);font-size:15px;font-weight:500;cursor:pointer;
  transition:all 0.15s;-webkit-tap-highlight-color:transparent;
}
.platform-btn:active{transform:scale(0.97)}
.platform-btn.selected{border-color:var(--accent);background:var(--accent-glow)}
.platform-btn i{font-size:20px;width:24px;text-align:center}
.btn{
  width:100%;padding:14px;border:none;border-radius:10px;
  font-size:16px;font-weight:600;cursor:pointer;
  transition:all 0.15s;-webkit-tap-highlight-color:transparent;
}
.btn:active{transform:scale(0.98)}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:disabled{background:#1e3a5f;color:#4a6a8f;cursor:not-allowed}
.btn-success{background:var(--success);color:#fff}
.btn-danger{background:var(--error);color:#fff}
.screenshot-box{
  width:100%;aspect-ratio:16/10;background:var(--surface);border:1px solid var(--border);
  border-radius:8px;overflow:hidden;position:relative;margin-bottom:12px;
}
.screenshot-box img{width:100%;height:100%;object-fit:contain}
.screenshot-box .placeholder{
  position:absolute;inset:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;color:var(--dim);gap:8px;
}
.screenshot-box .placeholder i{font-size:32px}
.status-bar{
  display:flex;align-items:center;gap:8px;padding:10px 14px;
  border-radius:8px;font-size:14px;margin-bottom:12px;
}
.status-bar.info{background:rgba(59,130,246,0.1);color:var(--accent)}
.status-bar.success{background:rgba(34,197,94,0.1);color:var(--success)}
.status-bar.error{background:rgba(239,68,68,0.1);color:var(--error)}
.status-bar.warn{background:rgba(245,158,11,0.1);color:var(--warn)}
.status-bar i{font-size:16px;flex-shrink:0}
.spinner{display:inline-block;width:18px;height:18px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin 0.6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.step{display:none}.step.active{display:block}
.cookie-list{font-size:13px;color:var(--dim);max-height:120px;overflow-y:auto;padding:8px;background:var(--surface);border-radius:6px;margin-top:8px}
.cookie-item{padding:4px 0;border-bottom:1px solid var(--border)}
.cookie-item:last-child{border:none}
.cookie-name{color:var(--success);font-family:monospace}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600}
.badge-success{background:rgba(34,197,94,0.15);color:var(--success)}
.badge-key{background:rgba(245,158,11,0.15);color:var(--warn)}
.hidden{display:none!important}
.input-group{margin-bottom:12px}
.secure-note{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--dim);margin-top:6px}
.secure-note i{color:var(--success)}
</style>
</head>
<body>
<div class="container">

<!-- HEADER -->
<div class="header">
  <h1><i class="fas fa-shield-halved" style="color:var(--accent);margin-right:6px"></i>Pure<span>Surf</span> Sync</h1>
  <p>Sync browser cookies from any device</p>
</div>

<!-- STEP 1: AUTH + PROFILE + PLATFORM -->
<div id="step-auth" class="step active">
  <div class="card">
    <div class="card-title">1. Connect</div>
    <div class="input-group">
      <label>API Key</label>
      <input type="password" id="api-key" placeholder="Enter your PureSurf API key" autocomplete="off">
    </div>
    <div class="input-group">
      <label>Profile</label>
      <select id="profile-select" disabled>
        <option value="">Enter API key first</option>
      </select>
    </div>
  </div>

  <div class="card">
    <div class="card-title">2. Select Platform</div>
    <div class="platform-grid" id="platform-grid"></div>
  </div>

  <button class="btn btn-primary" id="btn-start" disabled onclick="startSync()">
    <i class="fas fa-play"></i> Start Sync
  </button>
</div>

<!-- STEP 2: LOGIN -->
<div id="step-login" class="step">
  <div id="status-login" class="status-bar info">
    <div class="spinner"></div>
    <span>Connecting to <span id="platform-label"></span>...</span>
  </div>

  <div class="screenshot-box" id="screenshot-box">
    <div class="placeholder" id="screenshot-placeholder">
      <i class="fas fa-desktop"></i>
      <span>Browser view loading...</span>
    </div>
    <img id="screenshot-img" class="hidden" alt="Browser view">
  </div>

  <div class="card" id="cred-card">
    <div class="card-title">Enter Credentials</div>
    <div class="input-group">
      <label id="username-label">Email or Username</label>
      <input type="text" id="input-username" placeholder="Enter your email or username" autocomplete="email">
    </div>
    <div class="input-group">
      <label>Password</label>
      <input type="password" id="input-password" placeholder="Enter your password" autocomplete="current-password">
    </div>
    <div class="secure-note">
      <i class="fas fa-lock"></i>
      Credentials are typed directly into the browser, not stored
    </div>
    <button class="btn btn-primary" style="margin-top:12px" id="btn-login" onclick="submitCredentials()">
      <i class="fas fa-sign-in-alt"></i> Log In
    </button>
  </div>

  <!-- 2FA section (hidden by default) -->
  <div class="card hidden" id="twofa-card">
    <div class="card-title">Two-Factor Authentication</div>
    <div class="input-group">
      <label>Verification Code</label>
      <input type="text" id="input-2fa" placeholder="Enter code from SMS or app" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code">
    </div>
    <button class="btn btn-primary" style="margin-top:8px" id="btn-2fa" onclick="submit2FA()">
      <i class="fas fa-check-circle"></i> Verify
    </button>
  </div>

  <button class="btn btn-danger" style="margin-top:8px" onclick="cancelSync()">
    <i class="fas fa-times"></i> Cancel
  </button>
</div>

<!-- STEP 3: RESULT -->
<div id="step-result" class="step">
  <div id="status-result" class="status-bar success">
    <i class="fas fa-check-circle"></i>
    <span id="result-text">Cookies synced successfully!</span>
  </div>

  <div class="card">
    <div class="card-title">Sync Summary</div>
    <div style="display:flex;justify-content:space-between;margin-bottom:8px">
      <span>Profile</span><span id="result-profile" style="font-weight:600"></span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:8px">
      <span>Platform</span><span id="result-platform" style="font-weight:600"></span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:8px">
      <span>Cookies Captured</span><span id="result-count" class="badge badge-success"></span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:8px">
      <span>Key Cookies</span><span id="result-key" class="badge badge-key"></span>
    </div>
    <div id="cookie-details" class="cookie-list"></div>
  </div>

  <button class="btn btn-primary" onclick="resetSync()">
    <i class="fas fa-redo"></i> Sync Another Platform
  </button>
</div>

</div>

<script>
const API_BASE = '';
let state = {
  apiKey: '',
  profile: '',
  platform: '',
  sessionId: '',
  screenshotInterval: null,
};

const PLATFORMS = PLATFORM_DATA_PLACEHOLDER;

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
  buildPlatformGrid();
  document.getElementById('api-key').addEventListener('input', onApiKeyChange);
  document.getElementById('profile-select').addEventListener('change', checkReady);
});

function buildPlatformGrid() {
  const grid = document.getElementById('platform-grid');
  for (const [key, p] of Object.entries(PLATFORMS)) {
    const btn = document.createElement('button');
    btn.className = 'platform-btn';
    btn.dataset.platform = key;
    btn.innerHTML = `<i class="${p.icon}" style="color:${p.color}"></i>${p.name}`;
    btn.onclick = () => selectPlatform(key);
    grid.appendChild(btn);
  }
}

function selectPlatform(key) {
  document.querySelectorAll('.platform-btn').forEach(b => b.classList.remove('selected'));
  document.querySelector(`[data-platform="${key}"]`).classList.add('selected');
  state.platform = key;
  checkReady();
}

let apiKeyTimer = null;
function onApiKeyChange(e) {
  clearTimeout(apiKeyTimer);
  const key = e.target.value.trim();
  if (key.length >= 8) {
    apiKeyTimer = setTimeout(() => loadProfiles(key), 500);
  }
}

async function loadProfiles(key) {
  const sel = document.getElementById('profile-select');
  try {
    const res = await fetch(`${API_BASE}/api/v1/profiles`, {headers: {'x-api-key': key}});
    if (!res.ok) {sel.innerHTML = '<option value="">Invalid API key</option>'; return;}
    const data = await res.json();
    state.apiKey = key;
    sel.disabled = false;
    sel.innerHTML = '<option value="">Select a profile...</option>';
    (data.profiles || []).forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.name;
      const status = p.has_cookies ? ' (has cookies)' : '';
      const active = p.has_active_session ? ' [ACTIVE]' : '';
      opt.textContent = p.name + status + active;
      sel.appendChild(opt);
    });
    // Also add "Create New" option
    sel.innerHTML += '<option value="__new__">+ Create New Profile</option>';
    sel.onchange = () => {
      if (sel.value === '__new__') {
        const name = prompt('Profile name (lowercase, no spaces):');
        if (name && /^[a-z0-9_-]+$/.test(name)) {
          const opt = document.createElement('option');
          opt.value = name;
          opt.textContent = name + ' (new)';
          sel.insertBefore(opt, sel.lastElementChild);
          sel.value = name;
        } else if (name) {
          alert('Invalid name. Use lowercase letters, numbers, hyphens, underscores.');
          sel.value = '';
        } else {
          sel.value = '';
        }
      }
      state.profile = sel.value === '__new__' ? '' : sel.value;
      checkReady();
    };
  } catch (err) {
    sel.innerHTML = '<option value="">Connection error</option>';
  }
}

function checkReady() {
  state.profile = document.getElementById('profile-select').value;
  const ready = state.apiKey && state.profile && state.profile !== '__new__' && state.platform;
  document.getElementById('btn-start').disabled = !ready;
}

// ==================== SYNC FLOW ====================
async function startSync() {
  showStep('step-login');
  const platform = PLATFORMS[state.platform];
  document.getElementById('platform-label').textContent = platform.name;
  setStatus('status-login', 'info', `<div class="spinner"></div><span>Creating browser session for ${platform.name}...</span>`);

  try {
    const res = await fetch(`${API_BASE}/sync/start`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'x-api-key': state.apiKey},
      body: JSON.stringify({profile: state.profile, platform: state.platform}),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to start sync');

    state.sessionId = data.session_id;
    setStatus('status-login', 'info', `<i class="fas fa-desktop"></i><span>Login page loaded. Enter your ${platform.name} credentials below.</span>`);

    // Show screenshot
    if (data.screenshot) {
      showScreenshot(data.screenshot);
    }

    // Start screenshot polling
    startScreenshotPolling();

    // Show credential inputs
    document.getElementById('cred-card').classList.remove('hidden');
    document.getElementById('input-username').focus();

  } catch (err) {
    setStatus('status-login', 'error', `<i class="fas fa-exclamation-triangle"></i><span>${err.message}</span>`);
  }
}

async function submitCredentials() {
  const username = document.getElementById('input-username').value.trim();
  const password = document.getElementById('input-password').value;
  if (!username || !password) return;

  const btn = document.getElementById('btn-login');
  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Logging in...';
  setStatus('status-login', 'info', '<div class="spinner"></div><span>Typing credentials and logging in...</span>');

  try {
    const res = await fetch(`${API_BASE}/sync/credentials`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'x-api-key': state.apiKey},
      body: JSON.stringify({
        session_id: state.sessionId,
        username: username,
        password: password,
        platform: state.platform,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');

    if (data.screenshot) showScreenshot(data.screenshot);

    if (data.status === 'needs_2fa') {
      setStatus('status-login', 'warn', '<i class="fas fa-shield-alt"></i><span>Two-factor authentication required. Enter your code.</span>');
      document.getElementById('cred-card').classList.add('hidden');
      document.getElementById('twofa-card').classList.remove('hidden');
      document.getElementById('input-2fa').focus();
    } else if (data.status === 'needs_username_next') {
      // Twitter-style: username first, then password
      setStatus('status-login', 'info', '<div class="spinner"></div><span>Username submitted. Entering password...</span>');
      // Auto-send password after username step
      const res2 = await fetch(`${API_BASE}/sync/password`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'x-api-key': state.apiKey},
        body: JSON.stringify({
          session_id: state.sessionId,
          password: password,
          platform: state.platform,
        }),
      });
      const data2 = await res2.json();
      if (data2.screenshot) showScreenshot(data2.screenshot);
      if (data2.status === 'needs_2fa') {
        setStatus('status-login', 'warn', '<i class="fas fa-shield-alt"></i><span>Two-factor authentication required.</span>');
        document.getElementById('cred-card').classList.add('hidden');
        document.getElementById('twofa-card').classList.remove('hidden');
        document.getElementById('input-2fa').focus();
      } else if (data2.status === 'success') {
        completeSync(data2);
      } else {
        throw new Error(data2.message || 'Login may have failed. Check the browser view.');
      }
    } else if (data.status === 'success') {
      completeSync(data);
    } else {
      throw new Error(data.message || 'Unexpected response. Check the browser view.');
    }
  } catch (err) {
    setStatus('status-login', 'error', `<i class="fas fa-exclamation-triangle"></i><span>${err.message}</span>`);
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Retry Login';
  }
}

async function submit2FA() {
  const code = document.getElementById('input-2fa').value.trim();
  if (!code) return;

  const btn = document.getElementById('btn-2fa');
  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Verifying...';

  try {
    const res = await fetch(`${API_BASE}/sync/2fa`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'x-api-key': state.apiKey},
      body: JSON.stringify({
        session_id: state.sessionId,
        code: code,
        platform: state.platform,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || '2FA verification failed');

    if (data.screenshot) showScreenshot(data.screenshot);

    if (data.status === 'success') {
      completeSync(data);
    } else {
      throw new Error(data.message || '2FA may have failed. Check the browser view.');
    }
  } catch (err) {
    setStatus('status-login', 'error', `<i class="fas fa-exclamation-triangle"></i><span>${err.message}</span>`);
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-check-circle"></i> Retry Verify';
  }
}

function completeSync(data) {
  stopScreenshotPolling();
  showStep('step-result');

  const platform = PLATFORMS[state.platform];
  document.getElementById('result-profile').textContent = state.profile;
  document.getElementById('result-platform').textContent = platform.name;
  document.getElementById('result-count').textContent = data.cookies_captured || 0;

  // Key cookies found
  const keyFound = data.key_cookies_found || [];
  document.getElementById('result-key').textContent = keyFound.length + ' / ' + (platform.key_cookies || []).length;

  // Cookie domain list
  const details = document.getElementById('cookie-details');
  if (data.domains && data.domains.length) {
    details.innerHTML = data.domains.map(d =>
      `<div class="cookie-item"><span class="cookie-name">${d.domain}</span> - ${d.count} cookies</div>`
    ).join('');
  }

  if (data.status === 'success') {
    setStatus('status-result', 'success', `<i class="fas fa-check-circle"></i><span>Cookies synced to profile "${state.profile}"!</span>`);
  }
}

async function cancelSync() {
  stopScreenshotPolling();
  if (state.sessionId) {
    try {
      await fetch(`${API_BASE}/sync/cancel`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'x-api-key': state.apiKey},
        body: JSON.stringify({session_id: state.sessionId}),
      });
    } catch (e) {}
  }
  resetSync();
}

function resetSync() {
  stopScreenshotPolling();
  state.sessionId = '';
  document.getElementById('input-username').value = '';
  document.getElementById('input-password').value = '';
  document.getElementById('input-2fa').value = '';
  document.getElementById('cred-card').classList.remove('hidden');
  document.getElementById('twofa-card').classList.add('hidden');
  document.getElementById('btn-login').disabled = false;
  document.getElementById('btn-login').innerHTML = '<i class="fas fa-sign-in-alt"></i> Log In';
  document.getElementById('btn-2fa').disabled = false;
  document.getElementById('btn-2fa').innerHTML = '<i class="fas fa-check-circle"></i> Verify';
  document.getElementById('screenshot-img').classList.add('hidden');
  document.getElementById('screenshot-placeholder').classList.remove('hidden');
  showStep('step-auth');
}

// ==================== HELPERS ====================
function showStep(stepId) {
  document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
  document.getElementById(stepId).classList.add('active');
}

function setStatus(id, type, html) {
  const el = document.getElementById(id);
  el.className = 'status-bar ' + type;
  el.innerHTML = html;
}

function showScreenshot(b64) {
  const img = document.getElementById('screenshot-img');
  const placeholder = document.getElementById('screenshot-placeholder');
  img.src = 'data:image/png;base64,' + b64;
  img.classList.remove('hidden');
  placeholder.classList.add('hidden');
}

function startScreenshotPolling() {
  state.screenshotInterval = setInterval(async () => {
    if (!state.sessionId) return;
    try {
      const res = await fetch(`${API_BASE}/sync/screenshot?session_id=${state.sessionId}`, {
        headers: {'x-api-key': state.apiKey},
      });
      if (res.ok) {
        const data = await res.json();
        if (data.screenshot) showScreenshot(data.screenshot);
      }
    } catch (e) {}
  }, 3000);
}

function stopScreenshotPolling() {
  if (state.screenshotInterval) {
    clearInterval(state.screenshotInterval);
    state.screenshotInterval = null;
  }
}
</script>
</body>
</html>"""


# ==================== REQUEST MODELS ====================
class SyncStartReq(BaseModel):
    profile: str
    platform: str

class SyncCredentialsReq(BaseModel):
    session_id: str
    username: str
    password: str
    platform: str

class SyncPasswordReq(BaseModel):
    session_id: str
    password: str
    platform: str

class Sync2FAReq(BaseModel):
    session_id: str
    code: str
    platform: str

class SyncCancelReq(BaseModel):
    session_id: str


# Track active sync sessions (separate from regular sessions to avoid conflicts)
_sync_sessions: Dict[str, dict] = {}


def extend_sync_routes(app: FastAPI, sessions: dict, auth_fn, launch_fn,
                       save_cookies_fn, cookies_path_fn, profile_cookies_path_fn,
                       encrypt_cookies_fn, decrypt_cookies_fn, profiles_dir: str):
    """Mount all /sync routes on the main FastAPI app.

    Args:
        app: The FastAPI app instance
        sessions: The global sessions dict
        auth_fn: The auth(api_key) function
        launch_fn: The _launch(sid, proxy, device) coroutine
        save_cookies_fn: The _save_cookies(sid, page) coroutine
        cookies_path_fn: The _cookies_path(sid) function
        profile_cookies_path_fn: The _profile_cookies_path(name) function
        encrypt_cookies_fn: The _encrypt_cookies(data) function
        decrypt_cookies_fn: The _decrypt_cookies(raw) function
        profiles_dir: Path to profiles directory
    """

    @app.get('/sync', response_class=HTMLResponse)
    async def sync_page():
        """Serve the mobile-friendly cookie sync page."""
        # Inject platform data into the HTML
        platform_json = json.dumps({k: {
            'name': v['name'], 'icon': v['icon'], 'color': v['color'],
            'key_cookies': v.get('key_cookies', []),
        } for k, v in PLATFORMS.items()})
        html = SYNC_PAGE_HTML.replace('PLATFORM_DATA_PLACEHOLDER', platform_json)
        return HTMLResponse(content=html)

    @app.post('/sync/start')
    async def sync_start(req: SyncStartReq, x_api_key: str = Header(None)):
        """Create a browser session and navigate to the platform's login page."""
        u = auth_fn(x_api_key)

        if req.platform not in PLATFORMS:
            raise HTTPException(400, f'Unknown platform: {req.platform}')

        platform = PLATFORMS[req.platform]
        profile_name = req.profile

        # Check if profile already has an active session
        if profile_name in sessions:
            raise HTTPException(409, f'Profile "{profile_name}" already has an active session. Close it first or use a different profile.')

        # Check max sessions
        if len(sessions) >= 10:
            raise HTTPException(429, 'Maximum sessions reached. Close an existing session first.')

        log.info(f'Sync: Starting {req.platform} login for profile {profile_name} (user: {u["user"]})')

        try:
            ctx, page = await launch_fn(profile_name, proxy=None, device=None)
            sessions[profile_name] = {
                'ctx': ctx, 'page': page, 'user': u['user'],
                'created': time.time(), 'last_active': time.time(),
                'proxy': None, 'device': None,
                'profile_name': profile_name,
                '_sync_mode': True,
            }

            # Navigate to login page
            await page.goto(platform['login_url'], wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(1.5)  # Let page render

            # Take screenshot
            img_bytes = await page.screenshot()
            b64 = base64.b64encode(img_bytes).decode()

            _sync_sessions[profile_name] = {
                'platform': req.platform,
                'started': time.time(),
                'state': 'awaiting_credentials',
            }

            return {
                'session_id': profile_name,
                'status': 'login_page_loaded',
                'screenshot': b64,
                'platform': req.platform,
            }

        except Exception as e:
            # Clean up on failure
            if profile_name in sessions:
                try:
                    await sessions[profile_name]['ctx'].close()
                except:
                    pass
                del sessions[profile_name]
            log.error(f'Sync start failed: {e}')
            raise HTTPException(500, f'Failed to create browser session: {str(e)}')

    @app.post('/sync/credentials')
    async def sync_credentials(req: SyncCredentialsReq, x_api_key: str = Header(None)):
        """Type credentials into the browser and attempt login."""
        auth_fn(x_api_key)
        sid = req.session_id

        s = sessions.get(sid)
        if not s:
            raise HTTPException(404, 'Sync session not found')

        if req.platform not in PLATFORMS:
            raise HTTPException(400, f'Unknown platform: {req.platform}')

        platform = PLATFORMS[req.platform]
        page = s['page']
        s['last_active'] = time.time()
        selectors = platform['selectors']

        try:
            # Type username
            username_sel = selectors.get('username')
            if username_sel:
                await page.wait_for_selector(username_sel, timeout=10000)
                await page.fill(username_sel, req.username)
                await asyncio.sleep(0.3)

            # For platforms with separate username/password steps (Twitter, Google)
            username_next = selectors.get('username_next')
            if username_next:
                try:
                    next_btn = await page.query_selector(username_next)
                    if next_btn:
                        await next_btn.click()
                        await asyncio.sleep(2)
                        # Take screenshot after username step
                        img = await page.screenshot()
                        b64 = base64.b64encode(img).decode()
                        return {
                            'status': 'needs_username_next',
                            'message': 'Username submitted. Password step next.',
                            'screenshot': b64,
                        }
                except Exception as e:
                    log.warning(f'Username next click failed: {e}')

            # Type password
            password_sel = selectors.get('password')
            if password_sel:
                try:
                    await page.wait_for_selector(password_sel, timeout=5000)
                    await page.fill(password_sel, req.password)
                    await asyncio.sleep(0.3)
                except Exception as e:
                    log.warning(f'Password field not found: {e}')

            # Click submit
            submit_sel = selectors.get('submit')
            if submit_sel:
                try:
                    submit_btn = await page.query_selector(submit_sel)
                    if submit_btn:
                        await submit_btn.click()
                except Exception as e:
                    log.warning(f'Submit click failed, trying Enter key: {e}')
                    await page.keyboard.press('Enter')

            # Wait for navigation
            await asyncio.sleep(3)

            # Check result
            return await _check_login_result(page, platform, sid, sessions,
                                             save_cookies_fn, profile_cookies_path_fn,
                                             encrypt_cookies_fn, profiles_dir)

        except Exception as e:
            img = await page.screenshot()
            b64 = base64.b64encode(img).decode()
            return {
                'status': 'error',
                'message': f'Login attempt error: {str(e)}',
                'screenshot': b64,
            }

    @app.post('/sync/password')
    async def sync_password(req: SyncPasswordReq, x_api_key: str = Header(None)):
        """Submit password in a separate step (Twitter/Google-style login)."""
        auth_fn(x_api_key)
        sid = req.session_id

        s = sessions.get(sid)
        if not s:
            raise HTTPException(404, 'Sync session not found')

        platform = PLATFORMS[req.platform]
        page = s['page']
        s['last_active'] = time.time()
        selectors = platform['selectors']

        try:
            # Wait for password field to appear
            password_sel = selectors.get('password')
            if password_sel:
                await page.wait_for_selector(password_sel, timeout=10000)
                await page.fill(password_sel, req.password)
                await asyncio.sleep(0.3)

            # Click submit or password next
            password_next = selectors.get('password_next')
            submit_sel = selectors.get('submit')
            click_sel = password_next or submit_sel
            if click_sel:
                try:
                    btn = await page.query_selector(click_sel)
                    if btn:
                        await btn.click()
                except:
                    await page.keyboard.press('Enter')
            else:
                await page.keyboard.press('Enter')

            await asyncio.sleep(3)

            return await _check_login_result(page, platform, sid, sessions,
                                             save_cookies_fn, profile_cookies_path_fn,
                                             encrypt_cookies_fn, profiles_dir)

        except Exception as e:
            img = await page.screenshot()
            b64 = base64.b64encode(img).decode()
            return {
                'status': 'error',
                'message': f'Password step error: {str(e)}',
                'screenshot': b64,
            }

    @app.post('/sync/2fa')
    async def sync_2fa(req: Sync2FAReq, x_api_key: str = Header(None)):
        """Submit 2FA verification code."""
        auth_fn(x_api_key)
        sid = req.session_id

        s = sessions.get(sid)
        if not s:
            raise HTTPException(404, 'Sync session not found')

        platform = PLATFORMS[req.platform]
        page = s['page']
        s['last_active'] = time.time()
        selectors = platform['selectors']

        try:
            # Try platform-specific 2FA selectors first
            tfa_input = selectors.get('2fa_input')
            if tfa_input:
                try:
                    await page.wait_for_selector(tfa_input, timeout=5000)
                    await page.fill(tfa_input, req.code)
                except:
                    # Fallback: find any visible input
                    await _type_into_visible_input(page, req.code)
            else:
                await _type_into_visible_input(page, req.code)

            await asyncio.sleep(0.5)

            # Submit 2FA
            tfa_submit = selectors.get('2fa_submit')
            if tfa_submit:
                try:
                    btn = await page.query_selector(tfa_submit)
                    if btn:
                        await btn.click()
                except:
                    await page.keyboard.press('Enter')
            else:
                await page.keyboard.press('Enter')

            await asyncio.sleep(3)

            return await _check_login_result(page, platform, sid, sessions,
                                             save_cookies_fn, profile_cookies_path_fn,
                                             encrypt_cookies_fn, profiles_dir)

        except Exception as e:
            img = await page.screenshot()
            b64 = base64.b64encode(img).decode()
            return {
                'status': 'error',
                'message': f'2FA error: {str(e)}',
                'screenshot': b64,
            }

    @app.get('/sync/screenshot')
    async def sync_screenshot(session_id: str, x_api_key: str = Header(None)):
        """Get a fresh screenshot of the sync session browser."""
        auth_fn(x_api_key)
        s = sessions.get(session_id)
        if not s:
            raise HTTPException(404, 'Session not found')
        s['last_active'] = time.time()
        img = await s['page'].screenshot()
        b64 = base64.b64encode(img).decode()
        return {'screenshot': b64}

    @app.post('/sync/cancel')
    async def sync_cancel(req: SyncCancelReq, x_api_key: str = Header(None)):
        """Cancel a sync session and close the browser."""
        auth_fn(x_api_key)
        sid = req.session_id
        s = sessions.get(sid)
        if s:
            try:
                await s['ctx'].close()
            except:
                pass
            del sessions[sid]
        if sid in _sync_sessions:
            del _sync_sessions[sid]
        return {'status': 'cancelled'}


async def _type_into_visible_input(page, text):
    """Fallback: find the first visible text/number input and type into it."""
    inputs = await page.query_selector_all('input[type="text"], input[type="tel"], input[type="number"], input:not([type])')
    for inp in inputs:
        if await inp.is_visible():
            await inp.fill(text)
            return
    # Last resort: just type
    await page.keyboard.type(text)


async def _check_login_result(page, platform, sid, sessions_dict,
                               save_cookies_fn, profile_cookies_path_fn,
                               encrypt_cookies_fn, profiles_dir):
    """Check if login succeeded, handle 2FA detection, save cookies on success."""
    current_url = page.url
    title = await page.title()

    # Check for 2FA indicators
    tfa_indicators = [
        'verification', 'verify', 'two-factor', '2fa', 'challenge',
        'security code', 'authenticat', 'confirm',
    ]
    page_text = (title + ' ' + current_url).lower()

    # Also check page content for 2FA
    try:
        body_text = await page.evaluate('document.body ? document.body.innerText.substring(0, 2000) : ""')
        page_text += ' ' + body_text.lower()
    except:
        pass

    is_2fa = any(ind in page_text for ind in tfa_indicators)

    # Check for success indicators
    is_success = any(ind in current_url for ind in platform.get('success_indicators', []))

    img = await page.screenshot()
    b64 = base64.b64encode(img).decode()

    if is_success:
        # Login successful - save cookies
        cookies = await page.context.cookies()
        cookie_count = len(cookies)

        # Identify key cookies
        key_cookie_names = platform.get('key_cookies', [])
        key_found = [c['name'] for c in cookies if c['name'] in key_cookie_names]

        # Save to profile storage
        cp = profile_cookies_path_fn(sid)
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        with open(cp, 'wb') as f:
            f.write(encrypt_cookies_fn(cookies))

        # Save sync metadata
        meta_path = os.path.join(os.path.dirname(cp), 'cookie_sync_meta.json')
        domains = {}
        for c in cookies:
            d = c.get('domain', '')
            domains[d] = domains.get(d, 0) + 1

        meta = {
            'last_sync': time.time(),
            'last_sync_count': cookie_count,
            'total_cookies': cookie_count,
            'domains': list(domains.keys()),
            'sync_source': 'mobile_sync_page',
            'platform': platform['name'],
            'key_cookies_found': key_found,
        }
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)

        log.info(f'Sync SUCCESS: {cookie_count} cookies saved for profile {sid} ({platform["name"]}). Key cookies: {key_found}')

        # Close the sync session browser
        try:
            await sessions_dict[sid]['ctx'].close()
        except:
            pass
        if sid in sessions_dict:
            del sessions_dict[sid]
        if sid in _sync_sessions:
            del _sync_sessions[sid]

        return {
            'status': 'success',
            'cookies_captured': cookie_count,
            'key_cookies_found': key_found,
            'domains': [{'domain': d, 'count': c} for d, c in domains.items()],
            'screenshot': b64,
            'url': current_url,
        }

    elif is_2fa:
        if sid in _sync_sessions:
            _sync_sessions[sid]['state'] = 'awaiting_2fa'
        return {
            'status': 'needs_2fa',
            'message': 'Two-factor authentication detected.',
            'screenshot': b64,
            'url': current_url,
        }

    else:
        # Unclear - might be an error page or slow redirect
        return {
            'status': 'unknown',
            'message': f'Login status unclear. Page: {title}. Check the browser view and try again.',
            'screenshot': b64,
            'url': current_url,
        }
