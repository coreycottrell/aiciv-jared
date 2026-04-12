/**
 * PureSurf Cookie Sync — Popup Controller
 *
 * Captures cookies from the active tab's domain and pushes them to the
 * PureSurf BaaS API via PUT /api/v1/profiles/{profileName}/cookies.
 */

// ── DOM refs ──────────────────────────────────────────────────────────
const $profileSelect   = document.getElementById('profileSelect');
const $btnAdd          = document.getElementById('btnAddProfile');
const $btnDelete       = document.getElementById('btnDeleteProfile');
const $configPanel     = document.getElementById('configPanel');
const $configInput     = document.getElementById('configInput');
const $btnSave         = document.getElementById('btnSaveConfig');
const $btnCancel       = document.getElementById('btnCancelConfig');
const $tabFavicon      = document.getElementById('tabFavicon');
const $tabDomain       = document.getElementById('tabDomain');
const $tabUrl          = document.getElementById('tabUrl');
const $syncBtn         = document.getElementById('syncBtn');
const $errorBanner     = document.getElementById('errorBanner');
const $statusCard      = document.getElementById('statusCard');
const $statusResult    = document.getElementById('statusResult');
const $statusCount     = document.getElementById('statusCount');
const $statusTotal     = document.getElementById('statusTotal');
const $statusDomains   = document.getElementById('statusDomains');
const $statusProfile   = document.getElementById('statusProfile');
const $statusTime      = document.getElementById('statusTime');

// ── State ─────────────────────────────────────────────────────────────
let profiles = {};       // { id: { apiUrl, apiKey, profileName, label } }
let activeProfileId = null;
let currentDomain = null;

// ── Storage helpers ───────────────────────────────────────────────────
async function loadProfiles() {
  const data = await chrome.storage.local.get(['puresurf_profiles', 'puresurf_active']);
  profiles = data.puresurf_profiles || {};
  activeProfileId = data.puresurf_active || null;
}

async function saveProfiles() {
  await chrome.storage.local.set({
    puresurf_profiles: profiles,
    puresurf_active: activeProfileId,
  });
}

// ── UI helpers ────────────────────────────────────────────────────────
function renderProfileSelect() {
  $profileSelect.innerHTML = '';
  const ids = Object.keys(profiles);

  if (ids.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = '-- No profiles configured --';
    $profileSelect.appendChild(opt);
    $syncBtn.disabled = true;
    return;
  }

  ids.forEach(id => {
    const p = profiles[id];
    const opt = document.createElement('option');
    opt.value = id;
    opt.textContent = p.label || p.profileName;
    $profileSelect.appendChild(opt);
  });

  // Restore active or pick first
  if (activeProfileId && profiles[activeProfileId]) {
    $profileSelect.value = activeProfileId;
  } else {
    activeProfileId = ids[0];
    $profileSelect.value = activeProfileId;
  }

  $syncBtn.disabled = !currentDomain;
}

function showError(msg) {
  $errorBanner.textContent = msg;
  $errorBanner.classList.add('visible');
  setTimeout(() => $errorBanner.classList.remove('visible'), 8000);
}

function clearError() {
  $errorBanner.classList.remove('visible');
}

function showStatus(data) {
  $statusCard.classList.add('visible');
  $statusResult.textContent = data.status === 'synced' ? 'Success' : data.status;
  $statusResult.className = 'status-value ' + (data.status === 'synced' ? 'success' : 'error');
  $statusCount.textContent = data.cookies_synced;
  $statusTotal.textContent = data.total_stored;
  $statusDomains.textContent = (data.domains || []).join(', ') || '-';
  $statusProfile.textContent = data.profile;
  $statusTime.textContent = new Date().toLocaleTimeString();
}

// ── Tab info ──────────────────────────────────────────────────────────
async function loadCurrentTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.url) {
    $tabDomain.textContent = 'No tab detected';
    return;
  }

  try {
    const url = new URL(tab.url);
    currentDomain = url.hostname;
    $tabDomain.textContent = currentDomain;
    $tabUrl.textContent = tab.url.length > 60 ? tab.url.slice(0, 60) + '...' : tab.url;
    $tabFavicon.src = tab.favIconUrl || 'icons/icon16.png';
    $tabFavicon.onerror = () => { $tabFavicon.src = 'icons/icon16.png'; };

    // Highlight matching preset
    document.querySelectorAll('.preset-btn').forEach(btn => {
      const pd = btn.dataset.domain;
      if (currentDomain.includes(pd)) {
        btn.classList.add('active');
      }
    });

    // Enable sync if we have a profile
    if (activeProfileId && profiles[activeProfileId]) {
      $syncBtn.disabled = false;
    }
  } catch {
    $tabDomain.textContent = 'Cannot read tab URL';
  }
}

// ── Cookie capture ────────────────────────────────────────────────────
async function captureCookies(domain) {
  // Get cookies for the domain and common subdomains
  const baseDomain = domain.replace(/^www\./, '');
  const dotDomain = '.' + baseDomain;

  // Strategy 1: By domain name
  const cookies = await chrome.cookies.getAll({ domain: baseDomain });

  // Strategy 2: By dot-prefixed domain for broader match
  const dotCookies = await chrome.cookies.getAll({ domain: dotDomain });

  // Strategy 3: By URL (catches cookies that domain-matching misses, including httpOnly)
  const urlCookies = await chrome.cookies.getAll({ url: `https://${baseDomain}` });
  const wwwCookies = await chrome.cookies.getAll({ url: `https://www.${baseDomain}` });

  // Strategy 5: Explicitly capture critical httpOnly cookies by name
  const criticalCookies = ['li_at', 'JSESSIONID', 'bscookie', 'lidc', 'bcookie', 'li_gc', 'li_mc'];
  for (const name of criticalCookies) {
    const explicit = await chrome.cookies.getAll({ domain: baseDomain, name: name });
    const explicitDot = await chrome.cookies.getAll({ domain: dotDomain, name: name });
    const explicitWww = await chrome.cookies.getAll({ domain: 'www.' + baseDomain, name: name });
    cookies.push(...explicit, ...explicitDot, ...explicitWww);
  }

  // Merge and deduplicate by name+domain+path
  const seen = new Set();
  const merged = [];

  for (const c of [...cookies, ...dotCookies, ...urlCookies, ...wwwCookies]) {
    const key = `${c.name}|${c.domain}|${c.path}`;
    if (seen.has(key)) continue;
    seen.add(key);

    // Convert Chrome cookie format to Playwright/PureSurf format
    const cookie = {
      name: c.name,
      value: c.value,
      domain: c.domain,
      path: c.path || '/',
      httpOnly: c.httpOnly || false,
      secure: c.secure || false,
      sameSite: c.sameSite === 'no_restriction' ? 'None'
               : c.sameSite === 'lax' ? 'Lax'
               : c.sameSite === 'strict' ? 'Strict'
               : 'Lax',
    };

    // Only include expiration for persistent cookies
    if (c.expirationDate) {
      cookie.expires = c.expirationDate;
    }

    merged.push(cookie);
  }

  return merged;
}

// ── Sync to PureSurf ──────────────────────────────────────────────────
async function syncCookies() {
  clearError();

  if (!activeProfileId || !profiles[activeProfileId]) {
    showError('No profile selected. Add a profile config first.');
    return;
  }

  if (!currentDomain) {
    showError('Cannot detect current tab domain.');
    return;
  }

  const profile = profiles[activeProfileId];
  const { apiUrl, apiKey, profileName } = profile;

  if (!apiUrl || !apiKey || !profileName) {
    showError('Profile config incomplete. Need apiUrl, apiKey, and profileName.');
    return;
  }

  // Start loading state
  $syncBtn.classList.add('loading');
  $syncBtn.disabled = true;

  try {
    // 1. Capture cookies
    const cookies = await captureCookies(currentDomain);

    if (cookies.length === 0) {
      showError(`No cookies found for ${currentDomain}. Make sure you are logged in.`);
      return;
    }

    // 2. Push to PureSurf API
    const url = `${apiUrl.replace(/\/+$/, '')}/api/v1/profiles/${encodeURIComponent(profileName)}/cookies`;

    const resp = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Api-Key': apiKey,
      },
      body: JSON.stringify({ cookies }),
    });

    if (!resp.ok) {
      const errText = await resp.text().catch(() => 'Unknown error');
      throw new Error(`API error ${resp.status}: ${errText}`);
    }

    const result = await resp.json();

    // 3. Show success
    showStatus(result);

    // 4. Save last sync info to storage
    await chrome.storage.local.set({
      [`puresurf_last_sync_${activeProfileId}`]: {
        domain: currentDomain,
        count: result.cookies_synced,
        total: result.total_stored,
        time: Date.now(),
      },
    });

  } catch (err) {
    showError(`Sync failed: ${err.message}`);
  } finally {
    $syncBtn.classList.remove('loading');
    $syncBtn.disabled = false;
  }
}

// ── Config panel ──────────────────────────────────────────────────────
function openConfigPanel() {
  $configPanel.classList.add('visible');
  $configInput.value = '';
  $configInput.focus();
}

function closeConfigPanel() {
  $configPanel.classList.remove('visible');
  $configInput.value = '';
}

function saveConfig() {
  let config;
  try {
    config = JSON.parse($configInput.value.trim());
  } catch {
    showError('Invalid JSON. Paste the config object from your PureSurf dashboard.');
    return;
  }

  // Validate required fields
  if (!config.apiUrl || !config.apiKey || !config.profileName) {
    showError('Config must include apiUrl, apiKey, and profileName.');
    return;
  }

  // Generate an ID
  const id = 'p_' + Date.now().toString(36);

  profiles[id] = {
    apiUrl: config.apiUrl,
    apiKey: config.apiKey,
    profileName: config.profileName,
    label: config.label || config.profileName,
  };

  activeProfileId = id;
  saveProfiles();
  renderProfileSelect();
  closeConfigPanel();
  clearError();
}

function deleteActiveProfile() {
  if (!activeProfileId || !profiles[activeProfileId]) return;
  const label = profiles[activeProfileId].label || profiles[activeProfileId].profileName;
  if (!confirm(`Delete profile "${label}"?`)) return;

  delete profiles[activeProfileId];
  const ids = Object.keys(profiles);
  activeProfileId = ids.length > 0 ? ids[0] : null;
  saveProfiles();
  renderProfileSelect();
}

// ── Platform preset buttons ───────────────────────────────────────────
function handlePresetClick(e) {
  const btn = e.currentTarget;
  const domain = btn.dataset.domain;

  // Open the platform in a new tab if not already on it
  if (!currentDomain || !currentDomain.includes(domain)) {
    chrome.tabs.create({ url: `https://www.${domain}` });
    window.close(); // Close popup — user will click again after logging in
    return;
  }

  // If already on the domain, just trigger sync
  syncCookies();
}

// ── Event listeners ───────────────────────────────────────────────────
$btnAdd.addEventListener('click', openConfigPanel);
$btnCancel.addEventListener('click', closeConfigPanel);
$btnSave.addEventListener('click', saveConfig);
$btnDelete.addEventListener('click', deleteActiveProfile);
$syncBtn.addEventListener('click', syncCookies);

$profileSelect.addEventListener('change', () => {
  activeProfileId = $profileSelect.value;
  saveProfiles();
});

document.querySelectorAll('.preset-btn').forEach(btn => {
  btn.addEventListener('click', handlePresetClick);
});

// ── Init ──────────────────────────────────────────────────────────────
(async () => {
  await loadProfiles();
  renderProfileSelect();
  await loadCurrentTab();

  // Load last sync info for active profile
  if (activeProfileId) {
    const data = await chrome.storage.local.get(`puresurf_last_sync_${activeProfileId}`);
    const last = data[`puresurf_last_sync_${activeProfileId}`];
    if (last) {
      $statusCard.classList.add('visible');
      $statusResult.textContent = 'Previous sync';
      $statusResult.className = 'status-value success';
      $statusCount.textContent = last.count;
      $statusTotal.textContent = last.total;
      $statusDomains.textContent = last.domain;
      $statusProfile.textContent = profiles[activeProfileId]?.profileName || '-';
      $statusTime.textContent = new Date(last.time).toLocaleString();
    }
  }
})();
