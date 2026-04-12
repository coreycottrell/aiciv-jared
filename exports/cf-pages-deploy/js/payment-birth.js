/* payment-birth.js - Birth/Naming initialization flow */
/* Extracted 2026-04-01 */
// Returns an HTML-encoded string (e.g. "<script>" → "&lt;script&gt;").
// Limited to 60 chars to prevent UI overflow from injected values.
// ---------------------------------------------------------------------------
function sanitizeText(str) {
  const d = document.createElement('div');
  d.textContent = typeof str === 'string' ? str.slice(0, 60) : '';
  return d.innerHTML; // returns HTML-escaped string safe for innerHTML
}

async function runBirthInit(dom, aiName, firstName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;

  // v4.7: Keep input row visible always (Jared: "should never disappear")
  inputRow.style.display = 'flex';
  textarea.disabled = true;
  sendBtn.disabled = true;

  // Sanitize caller-supplied strings before any DOM use (CRIT-004)
  const safeAiName    = sanitizeText(aiName    || 'Your AiCIV');
  const safeFirstName = sanitizeText(firstName || '');

  // v4.6: Container name is 100% server-authoritative (Witness auto-allocation).
  // We send seed data (name, email) to /birth/start. Witness allocates container + returns it.
  // NO client-side container generation. Container comes ONLY from /start response.
  payTestData.containerName = null; // cleared — will be set from server response only
  payTestData.timestamps.birthStarted = new Date().toISOString();

  logPayTestData({ ...payTestData, event: 'birth:init:start' });

  // ── Step 1: Call /api/birth/start (up to 180s — Witness says ~145s in production) ──
  // v4.3: context message tailored for Phase 1 (after role, before primary goal)
  await aiSay(
    msgList,
    `The next step in ${safeAiName}\u2019s set up, ${firstName}.<br><br>` +
    `I need to link ${safeAiName}\u2019s intelligence now — this takes about 30 seconds. ` +
    `Reaching out to ${safeAiName}\u2019s network\u2026`,
    800,
  );

  let oauthUrl = null;

  // v4.7: Birth/start with retry loop — shows feedback on failure instead of silent exit
  const MAX_BIRTH_RETRIES = 3;
  for (let attempt = 1; attempt <= MAX_BIRTH_RETRIES; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 45000); // v4.7: 45s timeout (was 180s)

      // v4.6: Send seed data — Witness uses this to allocate container + start orchestrator
      const startResp = await fetch(`${WITNESS_WEBHOOK_HOST}/api/birth/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: payTestData.name || firstName,
          email: payTestData.email || '',
          human_name: payTestData.name || firstName,
          tier: payTestData.tierPaid || 'awakened',
          ai_name: payTestData.aiName || '',
          name_suffix: payTestData.nameSuffix || null,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!startResp.ok) {
        const errBody = await startResp.json().catch(() => ({}));
        throw new Error(errBody.error || `HTTP ${startResp.status} from /birth/start`);
      }

      const startData = await startResp.json();

      if (startData.status !== 'url_ready' || !startData.oauth_url) {
        throw new Error(`Unexpected start response: ${JSON.stringify(startData)}`);
      }

      // HIGH-002: Validate oauth URL before DOM injection
      // Must be HTTPS and originate from claude.ai or anthropic.com
      try {
        const oauthUrlParsed = new URL(startData.oauth_url);
        if (!['https:'].includes(oauthUrlParsed.protocol) ||
            !['claude.ai', 'www.claude.ai', 'anthropic.com'].some(
              h => oauthUrlParsed.hostname === h || oauthUrlParsed.hostname.endsWith('.' + h)
            )) {
          throw new Error('OAuth URL failed domain validation: ' + oauthUrlParsed.hostname);
        }
      } catch (e) {
        throw new Error('Invalid OAuth URL from Witness: ' + e.message);
      }
      oauthUrl = startData.oauth_url;
      payTestData.birthOauthUrl = oauthUrl;

      // v4.6: Container name MUST come from server response. No client fallback.
      if (startData.container && typeof startData.container === 'string') {
        const serverContainerName = startData.container.toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 64);
        payTestData.containerName = serverContainerName; // server is authoritative — ONLY source
      } else {
        throw new Error('Server /birth/start did not return a container name');
      }

      logPayTestData({ ...payTestData, event: 'birth:start:url_ready', containerName: payTestData.containerName });
      break; // success — exit retry loop

    } catch (err) {
      console.error(`[ptc-v4] birth/start attempt ${attempt}/${MAX_BIRTH_RETRIES} failed:`, err.message);
      logPayTestData({ ...payTestData, event: 'birth:start:failed', error: err.message, attempt });

      if (attempt < MAX_BIRTH_RETRIES) {
        // v4.7: Show feedback and retry button instead of silent failure
        await aiSay(
          msgList,
          `Still connecting to ${safeAiName}\u2019s network\u2026 attempt ${attempt} timed out. Trying again.`,
          500,
        );
        // Brief pause before retry
        await new Promise(r => setTimeout(r, 2000));
      } else {
        // v4.7: Final failure — show error message with retry button
        await aiSay(
          msgList,
          `${safeAiName}\u2019s network is temporarily unavailable. ` +
          `This can happen during high traffic. Tap the button below to try again.`,
          500,
        );

        // Show retry button in actions area
        const retryResult = await new Promise((resolve) => {
          actions.innerHTML = '';
          const retryBtn = document.createElement('button');
          retryBtn.className = 'ptc-btn ptc-btn--primary';
          retryBtn.textContent = 'Retry Connection →';
          retryBtn.addEventListener('click', () => {
            actions.innerHTML = '';
            resolve('retry');
          });

          const skipBtn = document.createElement('button');
          skipBtn.className = 'ptc-btn';
          skipBtn.textContent = 'Continue without linking';
          skipBtn.style.marginLeft = '8px';
          skipBtn.addEventListener('click', () => {
            actions.innerHTML = '';
            resolve('skip');
          });

          actions.appendChild(retryBtn);
          actions.appendChild(skipBtn);
        });

        if (retryResult === 'retry') {
          // Recursive retry — restart the whole birth init
          return runBirthInit(dom, aiName, firstName);
        } else {
          // Skip — continue flow without birth
          await aiSay(
            msgList,
            `No problem — ${safeAiName} will keep working on connecting in the background. ` +
            `You can continue setting up.`,
            500,
          );
          return;
        }
      }
    }
  }

  // ── Step 2: Show OAuth button + instruction ──
  // v4.3: message tailored for Phase 1 context (setting up AI before primary goal)
  await aiSay(
    msgList,
    `${safeAiName}\u2019s AI brain is ready to link! Tap the button below to authorize on Claude — ` +
    `then come back here with the code.`,
    500,
  );

  // ── v4.3.3: OAuth authorize button rendered in actions area (bottom of chat), not as a chat bubble ──
  // CRIT-004 / HIGH-002: Build via DOM API — no unsanitized values in innerHTML template literals.
  // Previously this rendered as a ptc-msg--ai chat bubble; moved to actions div per Jared screenshot.
  await new Promise((resolve) => {
    actions.innerHTML = '';
    const oauthLink = document.createElement('a');
    oauthLink.className = 'ptc-link-btn ptc-oauth-link';
    oauthLink.target = '_blank';
    oauthLink.rel = 'noopener';
    // Set href and text via DOM API — prevents XSS from safeAiName or oauthUrl (CRIT-004 / HIGH-002)
    oauthLink.href = oauthUrl; // already validated above
    oauthLink.textContent = `Authorize ${safeAiName}\u2019s AI Brain →`;
    oauthLink.style.cssText = 'display:block; margin-bottom:8px;';
    oauthLink.addEventListener('click', function () {
      this.textContent = 'Opened \u2713 — come back here with the code';
      this.style.background = '#4caf50';
    });

    const hintDiv = document.createElement('div');
    hintDiv.style.cssText = 'font-size:13px; color:var(--text-muted); margin-bottom:8px;';
    hintDiv.textContent = 'Opens in a new tab — keep this window open.';

    // ── Step 3: "I have my key →" button — activates the code input ──
    // User clicks this AFTER they've authorized on Claude and have the code in hand.
    const haveKeyBtn = document.createElement('button');
    haveKeyBtn.className = 'ptc-btn ptc-btn--primary';
    haveKeyBtn.textContent = 'I have my key →';
    haveKeyBtn.addEventListener('click', () => {
      actions.innerHTML = '';
      resolve();
    });

    actions.appendChild(oauthLink);
    actions.appendChild(hintDiv);
    actions.appendChild(haveKeyBtn);
  });
  actions.innerHTML = '';

  // ── Step 4: Collect the auth code ──
  await aiSay(
    msgList,
    `You\u2019ll see a short authorization code on claude.ai. ` +
    `Paste it here and I\u2019ll complete ${safeAiName}\u2019s connection.`,
    400,
  );

  // Show input for code
  // promptText won't resolve until validator passes (length > 4, no newlines)
  textarea.placeholder = 'Paste your code here\u2026';
  const authCode = await promptText(
    inputRow, textarea, sendBtn,
    (v) => v.trim().length > 4 && !/\n/.test(v.trim()),
  );
  textarea.placeholder = '';

  userSay(msgList, '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022 [auth code received]');

  const trimmedCode = authCode.trim();

  // ── Step 5: POST the code to Witness (/api/birth/code) ──
  await aiSay(msgList, `Connecting ${safeAiName}\u2019s account\u2026`, 300);

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 120s per contract

    const codeResp = await fetch(`${WITNESS_WEBHOOK_HOST}/api/birth/code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ container: payTestData.containerName, auth_code: trimmedCode }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!codeResp.ok) {
      const errBody = await codeResp.json().catch(() => ({}));
      throw new Error(errBody.error || `HTTP ${codeResp.status} from /birth/code`);
    }

    const codeData = await codeResp.json();

    if (codeData.status !== 'authenticated') {
      throw new Error(`Unexpected code response: ${JSON.stringify(codeData)}`);
    }

    payTestData.birthAuthenticated = true;
    payTestData.timestamps.birthAuthenticated = new Date().toISOString();

    logPayTestData({ ...payTestData, event: 'birth:authenticated' });

    // v4.3.3: Post-auth success message — "Yay! brain is connected. Let's continue!"
    // Portal button message deferred to Phase 5/7 (runPortalButtonWatcher)
    await aiSay(
      msgList,
      `Yay! ${safeAiName}\u2019s brain is connected. Let\u2019s continue!`,
      600,
    );

  } catch (err) {
    console.error('[ptc-v4] birth/code failed:', err.message);
    logPayTestData({ ...payTestData, event: 'birth:code:failed', error: err.message });

    await aiSay(
      msgList,
      `There was a hiccup connecting your authorization. ` +
      `${safeAiName} is still being set up — you\u2019ll receive an email with portal access details. ` +
      `If you need help, reach out to <a href="mailto:jared@puretechnology.nyc" style="color:#2a93c1;">jared@puretechnology.nyc</a>.`,
      600,
    );
  }
}

// ---------------------------------------------------------------------------
// SEED: Fire-and-forget POST to /api/send-seed after email is collected.
// FROM: aether-aiciv@agentmail.to (server-side) -> TO: aiciv-seed-inbox@agentmail.to
// ONE seed per client — server enforces idempotency by session_uuid.
// ---------------------------------------------------------------------------
var _seedFired = false;
function fireSeed() {
  if (_seedFired) return;
  _seedFired = true;
  try {
    var preMsgs = (payTestData.prePurchaseHistory && payTestData.prePurchaseHistory.length)
      ? payTestData.prePurchaseHistory
      : ((window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory)
          ? window._pbPrePurchaseSession.conversationHistory
          : []);
    var onboardingMsgs = [];
    if (payTestData.name) {
      onboardingMsgs.push({ role: 'assistant', content: 'What is your full name?' });
      onboardingMsgs.push({ role: 'user', content: payTestData.name });
    }
    if (payTestData.email) {
      onboardingMsgs.push({ role: 'assistant', content: 'What email should ' + (payTestData.aiName || 'your AI') + ' use to reach you?' });
      onboardingMsgs.push({ role: 'user', content: payTestData.email });
    }
    var isSandbox = !!(window.location.href.indexOf('sandbox') !== -1 || window.location.href.indexOf('pay-test') !== -1);
    var seedPayload = {
      session_uuid: payTestData.sessionUuid,
      ai_name:      payTestData.aiName || '',
      human_name:   payTestData.name || '',
      human_email:  payTestData.email || '',
      tier:         payTestData.tier || payTestData.tierPaid || '',
      order_id:     payTestData.orderId || '',
      is_sandbox:   isSandbox,
      conversation: preMsgs.concat(onboardingMsgs),
    };
    fetch('https://api.purebrain.ai/api/send-seed', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
      body: JSON.stringify(seedPayload),
    }).catch(function(e) { /* silent */ });
  } catch(e) { /* silent */ }
}

// ---------------------------------------------------------------------------
// Seed Addendum — fire-and-forget POST to /api/seed-addendum
// Sends all post-email data collected during the flow to /api/seed-addendum.
// ---------------------------------------------------------------------------
var _addendumFired = false;
function fireSeedAddendum() {
  if (_addendumFired) return; // client-side guard — prevents double-fire
  _addendumFired = true;
  try {
    // Build post-email conversation: company/role/goal/learn-more as structured messages
    var postEmailMsgs = [];
    if (payTestData.company !== undefined && payTestData.company !== null) {
      postEmailMsgs.push({ role: 'assistant', content: 'Are you working within a company or organization?' });
      postEmailMsgs.push({ role: 'user', content: payTestData.company || '(skipped)' });
    }
    if (payTestData.role !== undefined && payTestData.role !== null) {
      postEmailMsgs.push({ role: 'assistant', content: 'What is your role?' });
      postEmailMsgs.push({ role: 'user', content: payTestData.role || '(skipped)' });
    }
    if (payTestData.primaryGoal !== undefined && payTestData.primaryGoal !== null) {
      postEmailMsgs.push({ role: 'assistant', content: 'What is your primary goal for your AI?' });
      postEmailMsgs.push({ role: 'user', content: payTestData.primaryGoal || '(skipped)' });
    }
    if (Array.isArray(payTestData.learnMoreAnswers)) {
      payTestData.learnMoreAnswers.forEach(function(qa) {
        if (qa && qa.question) {
          postEmailMsgs.push({ role: 'assistant', content: qa.question });
          postEmailMsgs.push({ role: 'user', content: qa.answer || '(skipped)' });
        }
      });
    }
    var addendumPayload = {
      event: 'seed-addendum',
      session_uuid: payTestData.sessionUuid,
      aiName: payTestData.aiName,
      name: payTestData.name,
      email: payTestData.email,
      tier: payTestData.tier,
      company: payTestData.company,
      role: payTestData.role,
      primaryGoal: payTestData.primaryGoal,
      orderId: payTestData.orderId,
      learnMoreAnswers: payTestData.learnMoreAnswers || [],
      magicLink: payTestData.magicLink || '',
      prePurchaseSessionId: payTestData.prePurchaseSessionId || null,
      naming_session_id: payTestData.prePurchaseSessionId || null,
      name_suffix: payTestData.nameSuffix || null,
      conversation: postEmailMsgs,
      timestamp: new Date().toISOString(),
      page_url: window.location.href,
    };
    fetch('https://api.purebrain.ai/api/seed-addendum', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
      body: JSON.stringify(addendumPayload),
    }).catch(function(e) { /* silent — fire-and-forget */ });
  } catch(e) { /* silent */ }
}

// ---------------------------------------------------------------------------
// PHASE 7 — Portal Button Watcher (v3: introduced; v4: updated to Witness endpoint)
// Polls Witness GET /api/birth/portal-status/{container} every 30 seconds
// Runs concurrently with learn-more loop (non-blocking setInterval)
// ---------------------------------------------------------------------------

function runPortalButtonWatcher(dom, aiName) {
  // CRIT-004: Sanitize aiName before any DOM use
  const safeAiName = sanitizeText(aiName || 'Your AiCIV');

  const placeholderEl = document.getElementById('ptc-portal-placeholder');
  if (!placeholderEl) return;

  const containerName = payTestData.containerName;
  if (!containerName) {
    console.warn('[ptc-v4] runPortalButtonWatcher: no containerName in payTestData, skipping');
    return;
  }

  // Check portal readiness via Witness endpoint
  // Returns { ready: boolean, portalUrl: string } or null on error
  async function checkPortalReady() {
    try {
      const resp = await fetch(
        `${WITNESS_WEBHOOK_HOST}/api/birth/portal-status/${encodeURIComponent(containerName)}`,
        { method: 'GET', mode: 'cors' },
      );
      if (!resp.ok) return null;
      return await resp.json();
    } catch (_) {
      return null;
    }
  }

  // Polling: check every 30 seconds for up to 30 minutes (60 polls)
  const MAX_POLLS = 60;
  let pollCount = 0;

  const intervalId = setInterval(async () => {
    pollCount++;

    if (pollCount > MAX_POLLS) {
      clearInterval(intervalId);
      // Timeout fallback — show email message
      const currentPlaceholder = document.getElementById('ptc-portal-placeholder');
      if (currentPlaceholder) {
        const fallbackMsg = document.createElement('div');
        fallbackMsg.style.cssText = 'font-size:13px; color:var(--text-muted); padding:8px 0;';
        fallbackMsg.textContent = safeAiName + ' is still finishing up. Check your email for portal access.';
        currentPlaceholder.replaceWith(fallbackMsg);
      }
      logPayTestData({ ...payTestData, event: 'portal:timeout', containerName });
      return;
    }

    const status = await checkPortalReady();

    if (status && status.ready) {
      clearInterval(intervalId);
      payTestData.portalReady = true;

      // DON'T activate button from Witness poller — the magic link poller
      // has the correct app.purebrain.ai URL from our email pipeline.
      // This poller only confirms the portal is READY.
      // If the magic link poller already activated the button, nothing more to do.
      // If not, the magic link poller will activate it shortly with the correct URL.
      if (payTestData.magicLink) {
        // Magic link already available — activate now with the correct URL
        const currentPlaceholder = document.getElementById('ptc-portal-placeholder');
        if (currentPlaceholder) {
          const portalBtn = document.createElement('a');
          portalBtn.className = 'ptc-portal-btn ptc-portal-btn--pulsing';
          portalBtn.href = payTestData.magicLink;
          portalBtn.target = '_blank';
          portalBtn.rel = 'noopener';
          portalBtn.textContent = `Enter ${safeAiName}\u2019s Brain Stream`;
          portalBtn.addEventListener('click', function() { fireSeedAddendum(); });
          currentPlaceholder.replaceWith(portalBtn);
        }
      }

      // Also send a notification message in the chat
      // safeAiName is HTML-escaped so safe to interpolate into innerHTML string
      await aiSay(
        dom.msgList,
        `<span style="color: #4caf50; font-weight: 700;">${safeAiName} is ready.</span> ` +
        `${safeAiName}\u2019s portal is live \u2014 the button above just lit up. Let\u2019s go.`,
        500,
      );

      // Disable message input — flow is complete, Brain Stream button is the end
      if (dom.textarea) {
        dom.textarea.disabled = true;
        dom.textarea.placeholder = 'Flow complete \u2014 enter your Brain Stream above';
        dom.textarea.style.opacity = '0.4';
      }
      if (dom.sendBtn) {
        dom.sendBtn.disabled = true;
        dom.sendBtn.style.opacity = '0.4';
      }

      logPayTestData({ ...payTestData, event: 'portal:ready', containerName });
    }
  }, 30000); // 30-second polling interval
}

// ---------------------------------------------------------------------------
// Magic Link Poller — polls /api/magic-link/{uuid} every 5s after flow complete
// Runs CONCURRENTLY with runPortalButtonWatcher (both race to light up button).
// Whichever fires first activates the Brain Stream button.
// ---------------------------------------------------------------------------

function runMagicLinkPoller(dom, aiName) {
  const uuid = payTestData.sessionUuid;
  if (!uuid) {
    console.warn('[ptc] runMagicLinkPoller: no sessionUuid in payTestData, skipping');
    return;
  }

  const API_BASE = 'https://api.purebrain.ai';
  const MAX_POLLS = 360; // 30 minutes at 5s intervals
  let pollCount = 0;
  let stopped = false;

  async function checkMagicLink() {
    try {
      const emailParam = payTestData.email ? `?email=${encodeURIComponent(payTestData.email)}` : '';
      const resp = await fetch(
        `${API_BASE}/api/magic-link/${encodeURIComponent(uuid)}${emailParam}`,
        { method: 'GET', mode: 'cors' }
      );
      if (!resp.ok) return null;
      return await resp.json();
    } catch (_) {
      return null;
    }
  }

  function activateButton(magicLink, resolvedAiName) {
    if (stopped) return;
    stopped = true;

    const safeAiName = sanitizeText(resolvedAiName || aiName || 'Your AI');

    // HIGH-001: Validate portal URL — prevent open redirect
    let safePortalUrl = 'https://purebrain.ai/portal';
    try {
      const parsed = new URL(magicLink);
      const allowedDomains = ['purebrain.ai', 'puremarketing.ai', 'aiciv.dev', 'ai-civ.com'];
      const domainOk = parsed.protocol === 'https:' &&
        allowedDomains.some(d => parsed.hostname === d || parsed.hostname.endsWith('.' + d));
      if (domainOk) safePortalUrl = magicLink;
    } catch (_) {}

    const currentPlaceholder = document.getElementById('ptc-portal-placeholder');
    if (!currentPlaceholder) {
      // Button not rendered yet — store for immediate activation when it appears
      payTestData.magicLinkReady = true;
      payTestData.magicLink = magicLink;
      payTestData.resolvedAiName = resolvedAiName;
      return;
    }

    const portalBtn = document.createElement('a');
    portalBtn.className = 'ptc-portal-btn ptc-portal-btn--pulsing';
    portalBtn.href = safePortalUrl;
    portalBtn.target = '_blank';
    portalBtn.rel = 'noopener';
    portalBtn.textContent = `Enter ${safeAiName}’s Brain Stream`;
    portalBtn.addEventListener(‘click’, function() { fireSeedAddendum(); });
    currentPlaceholder.replaceWith(portalBtn);

    aiSay(
      dom.msgList,
      `<span style="color: #4caf50; font-weight: 700;">${safeAiName} is ready.</span> ` +
      `${safeAiName}’s portal is live — the button above just lit up. Let’s go.`,
      500
    ).catch(function() {});

    if (dom.textarea) {
      dom.textarea.disabled = true;
      dom.textarea.placeholder = 'Flow complete — enter your Brain Stream above';
      dom.textarea.style.opacity = '0.4';
    }
    if (dom.sendBtn) {
      dom.sendBtn.disabled = true;
      dom.sendBtn.style.opacity = '0.4';
    }
  }

  const intervalId = setInterval(async function() {
    if (stopped) { clearInterval(intervalId); return; }

    pollCount++;
    if (pollCount > MAX_POLLS) {
      clearInterval(intervalId);
      return;
    }

    const result = await checkMagicLink();
    if (result && result.status === 'ready' && result.magic_link) {
      clearInterval(intervalId);
      const resolvedAiName = result.ai_name || aiName;
      activateButton(result.magic_link, resolvedAiName);
      payTestData.magicLinkReceived = true;
      payTestData.magicLink = result.magic_link;
    }
  }, 5000); // 5-second polling
}



// ---------------------------------------------------------------------------
// PUBLIC ENTRY POINT
// ---------------------------------------------------------------------------

/**
 * initPayTestFlow v4
 *
 * @param {HTMLElement} chatContainer  - The element to render the chat inside
 * @param {string}      aiName         - The AI's name (e.g. "Aria")
 * @param {string}      tierPaid       - The tier the user paid for ("awakened" | "bonded" | "enterprise")
 * @param {string}      [orderId]      - Optional order ID from payment processor
 *
 * Page-level hooks (set before calling this function):
 *   window._pbContainerName   - Container name from Witness (e.g. "witness-corey").
 *                               If not set, falls back to "purebrain-{firstName}".
 *   window._pbPrePurchaseSession - Pre-purchase chat session object (v3 feature, unchanged)
 */
async function initPayTestFlow(chatContainer, aiName, tierPaid, orderId) {
  // Guard
  if (!chatContainer || !(chatContainer instanceof HTMLElement)) {
    throw new Error('initPayTestFlow: chatContainer must be a valid HTMLElement');
  }

  // Defaults
  // CRIT-004: Sanitize aiName at entry point — all downstream innerHTML uses are then safe
  aiName   = sanitizeText(aiName   || 'Pure');
  tierPaid = tierPaid || 'awakened';

  // Seed global data
  payTestData.aiName  = aiName;
  payTestData.tier    = tierPaid;
  payTestData.orderId = orderId || null;
  payTestData.timestamps.started = new Date().toISOString();

  if (window._pbPrePurchaseSession) {
    payTestData.prePurchaseSessionId = window._pbPrePurchaseSession.sessionId;
    payTestData.prePurchaseHistory = window._pbPrePurchaseSession.conversationHistory;
    payTestData.prePurchaseMessageCount = window._pbPrePurchaseSession.messageCount;
  }

  // Styles
  injectStyles();

  // Build DOM
  const dom = buildLayout(chatContainer);
  dom.container = chatContainer;

  // START MAGIC LINK POLLER EARLY — right after payment confirmed so button is
  // already pulsing by the time the user reaches it. activateButton() will store
  // the link in payTestData.magicLinkReady if the placeholder is not yet rendered.
  runMagicLinkPoller(dom, aiName);

  try {
    if (window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory.length > 0) {
      logPayTestData({
        ...payTestData,
        event: 'flow:start:pre-purchase-history',
        prePurchaseHistory: window._pbPrePurchaseSession.conversationHistory,
        prePurchaseSessionId: window._pbPrePurchaseSession.sessionId,
      });
    }

    // Phase 1: Questionnaire v4.3
    //   Q1 name → Q2 email → Q3 company → Q4 role
    //   → runBirthInit (Witness OAuth) → Q5 primary goal
    await runQuestionnaire(dom, aiName);

    const firstName = (payTestData.name || 'friend').split(' ')[0];

    // Phase 2: Behind the Curtain (enhanced with emoji icons per slide)
    await runBehindTheCurtain(dom, aiName);

    // Phase 3: Telegram Setup — REMOVED (no longer needed in flow)
    // Phase 4: Completion message (button triggers in-chat thank-you, no redirect)
    await runCompletion(dom, aiName, firstName);

    // Phases 5–7 are triggered by button clicks inside runCompletion:
    // runThankYouMessage → Learn More button →
    //   runPortalButtonWatcher (concurrent, uses containerName from Phase 1) + runLearnMoreLoop

  } catch (err) {
    // Surface errors visibly without destroying the chat
    const errMsg = document.createElement('div');
    errMsg.className = 'ptc-msg ptc-msg--ai';
    const errBubble = document.createElement('div');
    errBubble.className = 'ptc-bubble';
    errBubble.style.background = '#2a0a0a';
    errBubble.style.color = 'var(--bright-orange)';
    errBubble.textContent = 'Something went wrong on my end. Please refresh and try again.';
    errMsg.appendChild(errBubble);
    dom.msgList.appendChild(errMsg);

    console.error('[pay-test-chat-flow-v4] Fatal error:', err);
    logPayTestData({ ...payTestData, error: err.message, event: 'flow:error' });
  }
}

// ---------------------------------------------------------------------------
// Exports (works in both ES module and classic script contexts)
// ---------------------------------------------------------------------------

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { initPayTestFlow, payTestData, logPayTestData };
} else if (typeof window !== 'undefined') {
  // MED-003: Only expose the public entry point on window.
  // payTestData and logPayTestData contain sensitive user data (email, name, containerName,
  // birthOauthUrl) and must not be readable by third-party scripts/extensions.
  window.initPayTestFlow = initPayTestFlow;
}