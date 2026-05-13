/*
 * PureBrain DUO/TRIO Chat Widget — JS controller
 * Thread B Phase 1 Days 6-7 (2026-05-13)
 *
 * Auth: human portal session via Authorization: Bearer (localStorage social_session
 * OR Cookie social_session=…). NEVER fetches AI bearer tokens — those are
 * container-side only.
 *
 * Polling: 5s when tab visible, 30s when hidden (Page Visibility API).
 * Heartbeat: every 30s GET /presence (read-only — humans are not posting AIs).
 * 401 handling: window.location.reload() — magic-link middleware re-auths.
 *
 * Compression: portal-pb-styled.html pattern. Modal shows compressed vs
 * original size estimate before upload. Default-compress heuristic per Jared
 * spec 2026-05-13.
 */
(function() {
  'use strict';

  const CFG = window.ROOM_CONFIG || {
    room_id: 'room_demo',
    api_base: 'https://trio-comms.in0v8.workers.dev'
  };

  const POLL_VISIBLE_MS = 5000;
  const POLL_HIDDEN_MS  = 30000;
  const HEARTBEAT_MS    = 30000;
  const MAX_UPLOAD_BYTES = 25 * 1024 * 1024;

  // ===== Auth =====
  function getAuthToken() {
    // Order: window.AUTH_TOKEN (test override) → localStorage → cookie
    if (window.AUTH_TOKEN) return window.AUTH_TOKEN;
    try {
      const ls = localStorage.getItem('social_session');
      if (ls) return ls;
    } catch (e) {}
    const m = (document.cookie || '').match(/social_session=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }
  function authHeaders(extra) {
    const h = Object.assign({}, extra || {});
    const t = getAuthToken();
    if (t) h['Authorization'] = 'Bearer ' + t;
    return h;
  }

  // ===== State =====
  let _lastSeq = 0;
  let _myIdentity = null;     // human:{email}
  let _pollTimer = null;
  let _heartbeatTimer = null;
  let _seenIds = new Set();   // dedup across polls

  // ===== UI helpers =====
  const $ = id => document.getElementById(id);

  function escHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function fmtBytes(n) {
    if (!Number.isFinite(n) || n <= 0) return '0 B';
    if (n < 1024) return n + ' B';
    if (n < 1024*1024) return (n/1024).toFixed(1) + ' KB';
    if (n < 1024*1024*1024) return (n/(1024*1024)).toFixed(1) + ' MB';
    return (n/(1024*1024*1024)).toFixed(2) + ' GB';
  }
  function toast(msg, isError) {
    const el = $('toast');
    el.textContent = msg;
    el.className = 'toast show' + (isError ? ' error' : '');
    setTimeout(() => { el.className = 'toast'; }, 2800);
  }

  // ===== Compression (ported from portal-pb-styled.html ~line 10940) =====
  function _isImageFile(file) {
    return /\.(png|jpe?g|gif|webp|bmp)$/i.test(file.name) ||
           (file.type && file.type.startsWith('image/'));
  }
  function _isTextFile(file) {
    return /\.(txt|md|csv|js|ts|py|java|c|cpp|h|css|html|htm|json|xml|yaml|yml|sh|rb|go|rs|sql)$/i.test(file.name) ||
           (file.type && (file.type.startsWith('text/') || file.type === 'application/json'));
  }
  function _isAudioFile(file) {
    return /\.(mp3|wav|m4a|webm|ogg|aac)$/i.test(file.name) ||
           (file.type && file.type.startsWith('audio/'));
  }
  function _isCreativeSource(file) {
    return /\.(ai|psd|sketch|fig|xd)$/i.test(file.name);
  }

  function _estimateCompressedSize(file) {
    if (_isImageFile(file)) return Math.round(file.size * 0.55);
    if (_isTextFile(file))  return Math.round(file.size * 0.97);
    return file.size;
  }
  function _canCompress(file) {
    if (_isAudioFile(file)) return false;       // audio already compressed
    if (_isCreativeSource(file)) return false;  // creative source preserved
    return _isImageFile(file) || _isTextFile(file);
  }
  function _shouldRecommendCompress(file) {
    // Heuristic per Jared spec 2026-05-13:
    //   - Image >= 5MB → recommend Original (high-res intentional)
    //   - Image < 5MB → recommend Compressed
    //   - PDF / text / docx → recommend Compressed
    //   - .ai/.psd/.sketch/.fig → recommend Original
    //   - Audio → no compression
    if (_isAudioFile(file) || _isCreativeSource(file)) return false;
    if (_isImageFile(file) && file.size >= 5 * 1024 * 1024) return false;
    return _canCompress(file) || /\.(pdf|docx)$/i.test(file.name);
  }

  function _compressImage(file) {
    return new Promise(function(resolve) {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = function() {
        URL.revokeObjectURL(url);
        const maxW = 1920;
        let w = img.width, h = img.height;
        if (w > maxW) { h = Math.round(h * maxW / w); w = maxW; }
        const canvas = document.createElement('canvas');
        canvas.width = w; canvas.height = h;
        canvas.getContext('2d').drawImage(img, 0, 0, w, h);
        canvas.toBlob(function(blob) {
          if (!blob) { resolve(file); return; }
          const name = file.name.replace(/\.[^.]+$/, '') + '.jpg';
          resolve(new File([blob], name, { type: 'image/jpeg' }));
        }, 'image/jpeg', 0.7);
      };
      img.onerror = function() { URL.revokeObjectURL(url); resolve(file); };
      img.src = url;
    });
  }
  function _compressText(file) {
    return new Promise(function(resolve) {
      const reader = new FileReader();
      reader.onload = function(e) {
        const text = e.target.result;
        const trimmed = text.split('\n').map(function(line) {
          return line.replace(/[\t ]+$/, '');
        }).join('\n');
        const blob = new Blob([trimmed], { type: file.type || 'text/plain' });
        resolve(new File([blob], file.name, { type: file.type || 'text/plain' }));
      };
      reader.onerror = function() { resolve(file); };
      reader.readAsText(file);
    });
  }
  function _compressFile(file) {
    if (_isImageFile(file)) return _compressImage(file);
    if (_isTextFile(file))  return _compressText(file);
    return Promise.resolve(file);
  }

  function _showUploadModeModal(file) {
    return new Promise(function(resolve) {
      const overlay = $('upload-mode-overlay');
      const original = file.size;
      const estComp = _estimateCompressedSize(file);
      const canComp = _canCompress(file);
      const recommendCompressed = _shouldRecommendCompress(file);

      $('upm-subtitle').innerHTML = '<strong>' + escHtml(file.name) + '</strong>';
      $('upm-size-original').textContent = fmtBytes(original);
      $('upm-size-compressed').textContent = canComp ? fmtBytes(estComp) : 'Same';

      // Toggle "Recommended" badge — appears on the recommended side.
      const badge = $('upm-badge-recommended');
      badge.style.display = recommendCompressed ? 'inline-block' : 'none';

      const btnComp = $('upm-btn-compressed');
      const btnOrig = $('upm-btn-original');
      btnComp.disabled = !canComp;

      function cleanup() {
        overlay.classList.remove('visible');
        btnOrig.removeEventListener('click', onOrig);
        btnComp.removeEventListener('click', onComp);
        overlay.removeEventListener('click', onOverlay);
      }
      function onOrig() { cleanup(); resolve({ file, was_compressed: false }); }
      function onComp() {
        cleanup();
        if (!canComp) { resolve({ file, was_compressed: false }); return; }
        _compressFile(file).then(function(f) {
          resolve({ file: f, was_compressed: true });
        });
      }
      function onOverlay(e) {
        if (e.target === overlay) onOrig(); // click-outside = original
      }

      btnOrig.addEventListener('click', onOrig);
      btnComp.addEventListener('click', onComp);
      overlay.addEventListener('click', onOverlay);
      overlay.classList.add('visible');
    });
  }

  // ===== API calls =====
  async function fetchMessages() {
    const url = `${CFG.api_base}/rooms/${encodeURIComponent(CFG.room_id)}/messages?since_seq=${_lastSeq}&limit=200`;
    const resp = await fetch(url, { headers: authHeaders(), credentials: 'include' });
    if (resp.status === 401) {
      // Per CTO spec: window.location.reload() — magic-link re-auths
      console.warn('[room-widget] 401, reloading to re-auth');
      window.location.reload();
      return null;
    }
    if (resp.status === 403) {
      $('msg-list').innerHTML = '<div class="empty-state">You are not a member of this conversation. Contact support if this is unexpected.</div>';
      stopPolling();
      return null;
    }
    if (!resp.ok) throw new Error('messages ' + resp.status);
    return await resp.json();
  }
  async function fetchPresence() {
    const url = `${CFG.api_base}/rooms/${encodeURIComponent(CFG.room_id)}/presence`;
    const resp = await fetch(url, { headers: authHeaders(), credentials: 'include' });
    if (!resp.ok) return null;
    return await resp.json();
  }
  async function sendHeartbeat() {
    try {
      const url = `${CFG.api_base}/rooms/${encodeURIComponent(CFG.room_id)}/heartbeat`;
      await fetch(url, {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        credentials: 'include',
        body: JSON.stringify({ last_seq_seen: _lastSeq })
      });
    } catch (e) { /* swallow */ }
  }
  async function postMessage(content, attachments) {
    const url = `${CFG.api_base}/rooms/${encodeURIComponent(CFG.room_id)}/messages`;
    const client_msg_id = crypto.randomUUID();
    const resp = await fetch(url, {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      credentials: 'include',
      body: JSON.stringify({ content, client_msg_id, attachments: attachments || [] })
    });
    if (!resp.ok) {
      const t = await resp.text();
      throw new Error('post ' + resp.status + ': ' + t.slice(0, 200));
    }
    return await resp.json();
  }
  async function uploadFile(file, was_compressed) {
    const url = `${CFG.api_base}/rooms/${encodeURIComponent(CFG.room_id)}/upload`;
    const fd = new FormData();
    fd.append('file', file);
    fd.append('was_compressed', was_compressed ? 'true' : 'false');
    const resp = await fetch(url, {
      method: 'POST',
      headers: authHeaders(),
      credentials: 'include',
      body: fd
    });
    if (!resp.ok) {
      const t = await resp.text();
      throw new Error('upload ' + resp.status + ': ' + t.slice(0, 200));
    }
    return await resp.json();
  }

  // ===== Render =====
  function renderMessages(messages) {
    if (!messages || !messages.length) return;
    const list = $('msg-list');
    const empty = list.querySelector('.empty-state');
    if (empty) empty.remove();

    let highest = _lastSeq;
    let appended = 0;
    for (const m of messages) {
      if (_seenIds.has(m.id)) continue;
      _seenIds.add(m.id);
      if (m.seq > highest) highest = m.seq;
      const node = renderMessage(m);
      list.appendChild(node);
      appended++;
    }
    if (highest > _lastSeq) _lastSeq = highest;
    if (appended > 0) {
      // Smooth scroll to bottom (only if user near bottom — preserves scrollback)
      const near = list.scrollHeight - list.scrollTop - list.clientHeight < 200;
      if (near) list.scrollTop = list.scrollHeight;
    }
  }
  function renderMessage(m) {
    const div = document.createElement('div');
    const isMe = _myIdentity && m.sender === _myIdentity;
    div.className = 'msg' + (isMe ? ' from-me' : '');

    const senderLabel = isMe ? 'You' : displayNameFromSender(m.sender);
    const time = formatTime(m.timestamp);

    let html = `
      <div class="msg-header">
        <span class="msg-sender">${escHtml(senderLabel)}</span>
        <span class="msg-time">${escHtml(time)}</span>
      </div>
      <div class="msg-bubble">${escHtml(m.content)}</div>
    `;
    if (Array.isArray(m.attachments) && m.attachments.length) {
      html += '<div class="msg-attach">';
      for (const a of m.attachments) {
        html += renderAttachment(a);
      }
      html += '</div>';
    }
    div.innerHTML = html;
    return div;
  }
  function renderAttachment(a) {
    const mime = (a.mime || '').toLowerCase();
    const url = a.url || '';
    const name = a.filename || 'file';
    const size = fmtBytes(a.size || 0);
    const badge = (a.was_compressed === false)
      ? '<span class="badge-original">Original quality</span>' : '';

    if (mime.startsWith('image/')) {
      return `<div><img class="attach-image" src="${escHtml(url)}" alt="${escHtml(name)}" loading="lazy" onclick="window.open('${escHtml(url)}','_blank')">${badge}</div>`;
    }
    if (mime.startsWith('audio/')) {
      return `<div><div class="attach-card"><span class="fname">${escHtml(name)}</span><span class="fsize">${size}</span>${badge}</div><audio class="attach-audio" controls preload="metadata" src="${escHtml(url)}"></audio></div>`;
    }
    // Generic file card with download
    return `<div class="attach-card"><span class="fname">${escHtml(name)}</span><span class="fsize">${size}</span>${badge}<a href="${escHtml(url)}" download="${escHtml(name)}">↓ Download</a></div>`;
  }
  function displayNameFromSender(sender) {
    if (!sender) return 'Unknown';
    // ai:{customer_id}:{ai_id} → ai_id
    const ai = sender.match(/^ai:[^:]+:(.+)$/);
    if (ai) return capitalize(ai[1]);
    // human:{email} → email local-part
    const human = sender.match(/^human:(.+)$/);
    if (human) return human[1].split('@')[0];
    // legacy fixed: jared/aether/chy/morphe
    return capitalize(sender);
  }
  function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : s; }
  function formatTime(iso) {
    try { return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }
    catch (e) { return ''; }
  }

  function renderPresence(p) {
    if (!p || !Array.isArray(p.presence)) return;
    const strip = $('presence-strip');
    strip.innerHTML = '';
    for (const m of p.presence) {
      const isMe = _myIdentity && m.member_id === _myIdentity;
      const pill = document.createElement('span');
      pill.className = 'presence-pill' + (isMe ? ' me' : '');
      pill.innerHTML = `<span class="presence-dot ${m.status}"></span>${escHtml(m.display_name || displayNameFromSender(m.member_id))}`;
      strip.appendChild(pill);
    }
  }

  // ===== Polling lifecycle =====
  function scheduleNextPoll() {
    if (_pollTimer) clearTimeout(_pollTimer);
    const ms = document.hidden ? POLL_HIDDEN_MS : POLL_VISIBLE_MS;
    _pollTimer = setTimeout(doPoll, ms);
    $('poll-status').textContent = document.hidden ? '○' : '●';
    $('poll-status').title = `Polling every ${ms/1000}s (tab ${document.hidden ? 'hidden' : 'visible'})`;
  }
  async function doPoll() {
    try {
      const data = await fetchMessages();
      if (data && data.messages) renderMessages(data.messages);
      const pres = await fetchPresence();
      if (pres) renderPresence(pres);
    } catch (e) {
      console.warn('[room-widget] poll failed:', e.message);
    }
    scheduleNextPoll();
  }
  function stopPolling() {
    if (_pollTimer) { clearTimeout(_pollTimer); _pollTimer = null; }
    if (_heartbeatTimer) { clearInterval(_heartbeatTimer); _heartbeatTimer = null; }
  }
  function startHeartbeat() {
    sendHeartbeat();
    _heartbeatTimer = setInterval(sendHeartbeat, HEARTBEAT_MS);
  }

  // ===== Composer wiring =====
  function wireComposer() {
    const ta = $('composer-text');
    const btn = $('send-btn');
    const fileInput = $('file-input');

    ta.addEventListener('input', () => {
      btn.disabled = !ta.value.trim();
      ta.style.height = 'auto';
      ta.style.height = Math.min(160, ta.scrollHeight) + 'px';
    });
    ta.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!btn.disabled) btn.click();
      }
    });
    btn.addEventListener('click', async () => {
      const txt = ta.value.trim();
      if (!txt) return;
      btn.disabled = true;
      try {
        await postMessage(txt);
        ta.value = '';
        ta.style.height = 'auto';
        // Force immediate poll to show our own message
        doPoll();
      } catch (e) {
        toast('Send failed: ' + e.message, true);
        btn.disabled = false;
      }
    });

    fileInput.addEventListener('change', async (e) => {
      const file = e.target.files && e.target.files[0];
      e.target.value = ''; // reset so same file can be re-picked
      if (!file) return;
      if (file.size > MAX_UPLOAD_BYTES) {
        toast('File too large (max 25 MB)', true);
        return;
      }
      try {
        const { file: finalFile, was_compressed } = await _showUploadModeModal(file);
        toast('Uploading…');
        const result = await uploadFile(finalFile, was_compressed);
        // Post message referencing the upload
        await postMessage(
          ta.value.trim() || `[attached ${result.filename}]`,
          [{
            url: result.url,
            mime: result.mime,
            filename: result.filename,
            size: result.size,
            was_compressed: was_compressed
          }]
        );
        ta.value = '';
        toast('Sent');
        doPoll();
      } catch (err) {
        toast('Upload failed: ' + err.message, true);
      }
    });
  }

  // ===== Page Visibility =====
  document.addEventListener('visibilitychange', () => { scheduleNextPoll(); });

  // ===== Boot =====
  async function boot() {
    $('room-id-label').textContent = CFG.room_id;
    // Probe identity by hitting /rooms/{id} (returns room + members; we infer self from presence)
    try {
      const pres = await fetchPresence();
      if (pres && Array.isArray(pres.presence)) {
        // Heuristic: assume the member with most recent heartbeat near now is us.
        // Robust path: parse JWT or call a dedicated /me endpoint; for Phase 1
        // we rely on the human:{email} match against an injected window.MY_EMAIL.
        if (window.MY_EMAIL) {
          _myIdentity = 'human:' + window.MY_EMAIL.toLowerCase();
        }
        renderPresence(pres);
      }
    } catch (e) {
      console.warn('[room-widget] boot probe failed:', e.message);
    }
    doPoll();
    startHeartbeat();
    wireComposer();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
