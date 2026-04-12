/* === Post-Payment Chat Flow v4.7 (Witness Production: seed data POST, server-authoritative container, portal domain flex) === */
/**
 * pay-test-chat-flow-v4.js
 * Post-payment chat flow for purebrain.ai/pay-test
 *
 * v4.5 changes (Corey production directives 2026-02-25):
 *   - CHANGE 1: AUTO-FIRE birth init after Q4 — removed manual "Start AI Birth" button
 *       Per Witness v3.0 spec: SEED arriving IS the trigger. No user action needed.
 *   - CHANGE 2: Removed hardcoded 'aiciv-07' container name
 *       Container is ALWAYS server-authoritative via auto-allocation ({} POST body).
 *   - CHANGE 3: WITNESS_WEBHOOK_HOST switched to HTTPS proxy (api.purebrain.ai)
 *       Fixes mixed-content and routes through server-side proxy to Witness.
 *
 * v4.3.3 changes (birth UX fixes per Jared screenshot 2026-02-24):
 *   - CHANGE 1: Birth setup message text updated
 *       "One more step to complete [AI Name]'s setup" → "The next step in [AI Name]'s set up"
 *   - CHANGE 2: OAuth authorize button moved to actions area (bottom of chat)
 *       Previously: rendered as an inline chat bubble (msgList.appendChild)
 *       Now: rendered in the actions div at the bottom via promptButtons pattern
 *   - CHANGE 3: Graceful degradation fallback message removed
 *       Removed: "One moment — we're still setting up your AiCIV in the background..."
 *       Added: "Yay! [AI NAME]'s brain is connected. Let's continue!" on successful /birth/code
 *   - CHANGE 4: Version bumped to v4.3.3
 *
 * v4.3.2 changes (sandbox E2E test 2026-02-24):
 *   - CHANGE 1: runBirthInit() is now MANUAL (button-triggered, not auto-fire)
 *       Previously: called automatically at end of runQuestionnaire() after Q4
 *       Now: shows "Your AI is ready to be born" message + "Start AI Birth →" button
 *       runBirthInit() only fires when the human clicks that button
 *       Button is disabled after click to prevent double-fire (was hammering Witness single-threaded webhook)
 *   - CHANGE 2: Container hardcoded to "aiciv-07" for E2E test
 *       window._pbContainerName set to 'aiciv-07' at top of runBirthInit()
 *       POST /api/birth/start always sends {"container": "aiciv-07"}
 *       Prevents auto-allocation which was picking aiciv-08 with stale processes
 *
 * v4.3.1 changes (sandbox E2E test 2026-02-24):
 *   - WITNESS_WEBHOOK_HOST reverted to http://104.248.239.98:8099 for direct E2E test
 *       (approved by Jared + Witness; sandbox page 688 ONLY - page 689 stays on api.purebrain.ai)
 *       This bypasses the HTTPS proxy to test Witness birth pipeline end-to-end directly
 *
 * v4.3 changes (architecture: Birth Init moved earlier, API key flow removed 2026-02-24):
 *   - REMOVED: Claude API key collection flow (Phase 3 Step 10 in v4.2)
 *       Removed: "Before we go deeper" Keen message asking for API key
 *       Removed: "Open Claude Console" button (link to platform.claude.com)
 *       Removed: API key input/masking/validation logic (key prefix validation)
 *       NOTE: "I have my key →" button KEPT but repurposed: now triggers
 *             code input for OAuth flow (not API key) in Phase 1 Birth Init
 *       Removed: claudeSessionInfo field from payTestData
 *       Removed: claudeAuthComplete timestamp
 *       Removed: claudeMaxStatus / hasClaudeMax (no longer collected)
 *   - MOVED: runBirthInit() now fires IMMEDIATELY AFTER Q4 (role/title) in Phase 1
 *       Previously: fired at start of Phase 5 (runThankYouMessage)
 *       New location: end of runQuestionnaire(), after role acknowledgment
 *       New UX: "One more step to complete [AI Name]'s setup — linking intelligence now"
 *       → /birth/start → OAuth button → "I have my key →" → code input → /birth/code → confirm
 *       → "Connection established. Let's keep going." → then Primary Goal (Step 6)
 *   - runPortalButtonWatcher() starts after user clicks "Learn more →" in Phase 5
 *       (same as v4.2 — watcher polls silently while user does learn-more questions)
 *   - Phase 5 (runThankYouMessage): removed runBirthInit() call;
 *       runPortalButtonWatcher() starts when user clicks "Learn more →"
 *
 * v4.2 changes (security hardening per security-engineer-tech review 2026-02-24):
 *   - CRIT-003: WITNESS_WEBHOOK_HOST changed from plain HTTP IP to https://api.purebrain.ai
 *   - CRIT-004: sanitizeText() helper added; aiName sanitized at entry point
 *   - HIGH-002: oauthUrl validated for HTTPS + claude.ai/anthropic.com domain before DOM injection
 *   - HIGH-003: containerName allowlist enforced (lowercase alphanum + hyphens, max 64 chars)
 *   - MED-003: window.payTestData and window.logPayTestData removed from global exports
 *
 * v4.1 changes (UI upgrades per Jared 2026-02-24):
 *   - OAuth button text: "Authorize Your AiCIV" → "Authorize {aiName}'s AI Brain →"
 *   - Portal entry button text: "Enter Your AiCIV" → "Enter {aiName}'s Brain Stream"
 *   - Portal button style upgraded to match "Begin Awakening" CTA: large, prominent,
 *       full-width, orange→blue gradient, big font, pill border-radius, glow shadow
 *
 * v4 changes (on top of v3):
 *   - NEW: runBirthInit() — Witness birth pipeline: POST /api/birth/start → OAuth button
 *       → code input → POST /api/birth/code → portal polling begins
 *   - FIXED: runPortalButtonWatcher() now polls Witness endpoint:
 *       GET https://api.purebrain.ai/api/birth/portal-status/{container}
 *       (v4.2: routed through HTTPS proxy; v4.0 original used plain HTTP IP)
 *   - NEW: containerName plumbing — sourced from page metadata (window._pbContainerName),
 *       falls back to "purebrain-{humanFirstName}" slug
 *   - Timeout for /start raised to 180s (Witness reports ~145s in production)
 *   - Portal-status polling uses container name, not email/orderId
 *
 * v3 changes:
 *   - Claude auth MOVED from Phase 4 to Phase 1 (after Role question, before Primary Goal)
 *   - Behind-the-Curtain slides now have emoji icons per slide
 *   - Telegram Step 4 bot username example is now dynamic (uses aiName)
 *   - runClaudeMaxSetup REMOVED from flow (function kept as dead code for compatibility)
 *   - runCompletion button now triggers in-chat thank-you (no redirect to /thank-you/)
 *   - NEW: runThankYouMessage — renders thank-you card as AI message bubble
 *   - NEW: runLearnMoreLoop — 5-question deeper context conversation
 *   - NEW: runPortalButtonWatcher — polls for portal readiness, shows button when ready
 *
 * Usage:
 *   initPayTestFlow(chatContainer, aiName, tierPaid)
 *
 * CSS variables expected in host page:
 *   --bright-orange: #f1420b
 *   --light-blue:   #2a93c1
 *   --dark:         #0a0a0a
 */

'use strict';

// ---------------------------------------------------------------------------
// Global data store
// ---------------------------------------------------------------------------

const payTestData = {
  tier: null,
  aiName: null,
  orderId: null,
  name: null,
  email: null,
  company: null,
  role: null,
  primaryGoal: null,
  hasTelegram: null,
  telegramBotToken: null,
  learnMoreAnswers: [],           // NEW v3: stores learn-more conversation answers
  portalReady: false,            // NEW v3: tracks portal readiness state
  containerName: null,           // NEW v4: Witness birth pipeline container name
  birthOauthUrl: null,           // NEW v4: OAuth URL from Witness /start
  birthAuthenticated: false,     // NEW v4: true after Witness confirms authentication
  timestamps: {
    started: null,
    questionnaireComplete: null,
    curtainComplete: null,
    telegramComplete: null,
    flowComplete: null,
    learnMoreComplete: null,
    birthStarted: null,          // NEW v4: when /api/birth/start was called
    birthAuthenticated: null,    // NEW v4: when /api/birth/code confirmed
  },
};

// Generate a unique session UUID for this flow instance
payTestData.sessionUuid = (crypto.randomUUID ? crypto.randomUUID() : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) { var r = Math.random() * 16 | 0; return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16); }));
try { sessionStorage.setItem('pb_sessionUuid', payTestData.sessionUuid); } catch(e) {}

// ---------------------------------------------------------------------------
// Log helper — sends payTestData snapshot to BOTH log endpoints
// ---------------------------------------------------------------------------

function logPayTestData(data) {
  // Strip sensitive credentials before transmission (CRIT-001)
  // v4.3: claudeSessionInfo removed (API key flow removed); telegramBotToken still stripped
  const { telegramBotToken: _tg, ...safeData } = data;

  // Build base payload for /api/log-pay-test (form data)
  const payTestPayload = {
    event: safeData.event || 'pay-test-flow',
    timestamp: new Date().toISOString(),
    tier: payTestData.tier,
    orderId: payTestData.orderId,
    aiName: payTestData.aiName,
    name: payTestData.name,
    email: payTestData.email,
    company: payTestData.company,
    role: payTestData.role,
    primaryGoal: payTestData.primaryGoal,
    ...safeData,
    prePurchaseSessionId: payTestData.prePurchaseSessionId || null,
    naming_session_id: payTestData.prePurchaseSessionId || null,
    session_uuid: payTestData.sessionUuid,
    prePurchaseMessageCount: payTestData.prePurchaseMessageCount || 0,
  };

  // Build messages array for /api/log-conversation (required by AICIV)
  // Combines pre-purchase chat history + onboarding Q&A collected so far
  const preMsgs = (payTestData.prePurchaseHistory && payTestData.prePurchaseHistory.length)
    ? payTestData.prePurchaseHistory
    : ((window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory)
        ? window._pbPrePurchaseSession.conversationHistory
        : []);

  // Build onboarding messages from collected payTestData fields
  const onboardingMsgs = [];
  if (payTestData.name) {
    onboardingMsgs.push({ role: 'assistant', content: 'What is your name?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.name });
  }
  if (payTestData.email) {
    onboardingMsgs.push({ role: 'assistant', content: 'What email should we use to reach you?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.email });
  }
  if (payTestData.company) {
    onboardingMsgs.push({ role: 'assistant', content: 'Are you working within a company or organization?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.company });
  }
  if (payTestData.role) {
    onboardingMsgs.push({ role: 'assistant', content: 'What is your role or title?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.role });
  }
  if (payTestData.primaryGoal) {
    onboardingMsgs.push({ role: 'assistant', content: 'If ' + (payTestData.aiName || 'your AI') + ' could do one thing exceptionally well for you, what would it be?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.primaryGoal });
  }

  const allMessages = [...preMsgs, ...onboardingMsgs];

  // Use the pre-purchase session ID if available, else generate one
  const logSessionId = payTestData.prePurchaseSessionId
    || ('pb-post-' + (payTestData.orderId || Date.now()));

  // Payload for /api/log-conversation (requires 'messages' field for AICIV)
  const convPayload = {
    session_id: logSessionId,
    naming_session_id: payTestData.prePurchaseSessionId || null,
    session_uuid: payTestData.sessionUuid,
    messages: allMessages.length ? allMessages : [
      { role: 'user', content: '[Post-payment onboarding - no pre-purchase chat history]' }
    ],
    source: 'purebrain-post-payment',
    page_url: window.location.href,
    aiName: payTestData.aiName,
    userName: payTestData.name,
    userTier: payTestData.tier,
    metadata: {
      event: data.event || 'pay-test-flow',
      orderId: payTestData.orderId,
      phase: 'post-payment',
      civ_name: payTestData.aiName || '',
    },
  };

  // Send to both endpoints with correct payloads — fire-and-forget with 4s timeout
  var ctrl = new AbortController();
  setTimeout(function() { ctrl.abort(); }, 4000);

  Promise.allSettled([
    fetch('https://api.purebrain.ai/api/log-pay-test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
      body: JSON.stringify(payTestPayload),
      signal: ctrl.signal,
    }).catch(function(e) { /* silent — fire-and-forget */ }),

    fetch('https://api.purebrain.ai/api/log-conversation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
      body: JSON.stringify(convPayload),
      signal: ctrl.signal,
    }).catch(function(e) { /* silent — fire-and-forget */ }),
  ]);
}

// ---------------------------------------------------------------------------
// Utility: pause
// ---------------------------------------------------------------------------

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// Utility: random delay in a range
// ---------------------------------------------------------------------------

function jitter(min = 500, max = 1500) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ---------------------------------------------------------------------------
// Inject component styles once
// ---------------------------------------------------------------------------

function injectStyles() {
  if (document.getElementById('pay-test-styles')) return;

  const style = document.createElement('style');
  style.id = 'pay-test-styles';
  style.textContent = `
    /* ── Variables ─────────────────────────────────────────────────── */
    :root {
      --bright-orange: #f1420b;
      --light-blue:    #2a93c1;
      --dark:          #0a0a0a;
      --surface:       #111111;
      --surface-2:     #1a1a1a;
      --text-primary:  #f0f0f0;
      --text-muted:    #888888;
      --radius:        12px;
    }

    /* ── Chat wrapper ───────────────────────────────────────────────── */
    .ptc-wrapper {
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 0;
      flex: 1;
      background: rgba(10, 10, 10, 0.97);
      color: var(--text-primary);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 15px;
      line-height: 1.55;
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,0.08);
      position: relative;
      z-index: 1;
      overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }

    /* ── Message list ───────────────────────────────────────────────── */
    .ptc-messages {
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      padding: 20px 24px 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      scroll-behavior: smooth;
      position: relative;
      z-index: 2;
    }

    /* ── Individual message bubble ──────────────────────────────────── */
    .ptc-msg {
      display: flex;
      align-items: flex-end;
      gap: 10px;
      max-width: 78%;
      animation: ptc-fade-in 0.3s ease;
    }

    @keyframes ptc-fade-in {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0);   }
    }

    .ptc-msg--ai   { align-self: flex-start; }
    .ptc-msg--user { align-self: flex-end;   flex-direction: row-reverse; }

    .ptc-bubble {
      padding: 12px 16px;
      border-radius: var(--radius);
      line-height: 1.55;
    }

    .ptc-msg--ai   .ptc-bubble {
      background: rgba(20, 20, 20, 0.95);
      border: 1px solid rgba(255,255,255,0.08);
      color: var(--text-primary);
      border-bottom-left-radius: 4px;
    }

    .ptc-msg--user .ptc-bubble {
      background: linear-gradient(135deg, #f1420b, #ed6626);
      color: #fff;
      border-bottom-right-radius: 4px;
    }

    /* ── Typing indicator ───────────────────────────────────────────── */
    .ptc-typing {
      display: flex;
      gap: 5px;
      align-items: center;
      padding: 12px 16px;
      background: rgba(20, 20, 20, 0.95);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: var(--radius);
      border-bottom-left-radius: 4px;
      width: fit-content;
    }

    .ptc-typing span {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #2a93c1;
      animation: ptc-bounce 1.2s infinite ease-in-out;
    }

    .ptc-typing span:nth-child(2) { animation-delay: 0.2s; }
    .ptc-typing span:nth-child(3) { animation-delay: 0.4s; }

    @keyframes ptc-bounce {
      0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
      40%            { transform: scale(1.0); opacity: 1.0; }
    }

    /* ── Input row ──────────────────────────────────────────────────── */
    .ptc-input-row {
      padding: 12px 24px 20px;
      padding-bottom: calc(20px + env(safe-area-inset-bottom, 0px));
      display: flex;
      gap: 10px;
      background: transparent;
      border-top: 1px solid rgba(255,255,255,0.06);
      position: relative;
      z-index: 2;
      flex-shrink: 0;
    }

    .ptc-input {
      flex: 1;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 12px;
      color: var(--text-primary);
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      font-size: 15px;
      padding: 12px 16px;
      outline: none;
      transition: border-color 0.2s;
      resize: none;
      min-height: 42px;
      max-height: 120px;
    }

    .ptc-input:focus { border-color: var(--light-blue); }

    .ptc-send-btn {
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      border: none;
      border-radius: 12px;
      color: #fff;
      cursor: pointer;
      font-size: 15px;
      font-weight: 600;
      padding: 10px 22px;
      transition: all 0.2s;
      white-space: nowrap;
    }

    .ptc-send-btn:hover { transform: scale(1.03); }

    .ptc-send-btn:hover   { opacity: 0.88; }
    .ptc-send-btn:disabled { opacity: 0.45; cursor: not-allowed; }

    /* ── Action buttons (slides, yes/no, etc.) ──────────────────────── */
    .ptc-actions {
      padding: 4px 20px 16px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      flex-shrink: 0;
    }

    .ptc-btn {
      background: transparent;
      border: 1.5px solid var(--light-blue);
      border-radius: 8px;
      color: var(--light-blue);
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      padding: 9px 20px;
      transition: background 0.2s, color 0.2s;
    }

    .ptc-btn:hover {
      background: var(--light-blue);
      color: #fff;
    }

    .ptc-btn--primary {
      background: var(--bright-orange);
      border-color: var(--bright-orange);
      color: #fff;
    }

    .ptc-btn--primary:hover { opacity: 0.88; }

    /* ── Slide card ─────────────────────────────────────────────────── */
    .ptc-slide {
      background: var(--surface-2);
      border: 1px solid #222;
      border-radius: var(--radius);
      padding: 20px 22px;
      font-size: 14.5px;
      line-height: 1.65;
      color: var(--text-primary);
      animation: ptc-fade-in 0.3s ease;
      max-width: 78%;
      align-self: flex-start;
    }

    .ptc-slide-label {
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--light-blue);
      margin-bottom: 10px;
      font-weight: 700;
    }

    /* ── Slide icon visual ──────────────────────────────────────────── */
    .ptc-slide-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 12px 0 14px;
      font-size: 36px;
      line-height: 1;
    }

    .ptc-slide-icon svg {
      width: 44px;
      height: 44px;
      opacity: 0.85;
    }

    .ptc-slide-icon--wide {
      justify-content: flex-start;
      gap: 10px;
      font-size: 26px;
      flex-wrap: wrap;
    }

    /* ── Status indicator ───────────────────────────────────────────── */
    .ptc-status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: var(--text-muted);
      padding: 6px 0;
    }

    .ptc-status--success { color: #4caf50; }
    .ptc-status--error   { color: var(--bright-orange); }

    /* ── Welcome button ─────────────────────────────────────────────── */
    .ptc-welcome-btn {
      background: linear-gradient(135deg, var(--bright-orange), #c73000);
      border: none;
      border-radius: var(--radius);
      color: #fff;
      cursor: pointer;
      font-size: 17px;
      font-weight: 700;
      padding: 16px 32px;
      margin: 32px 20px 24px;
      flex-shrink: 0;
      transition: opacity 0.2s, transform 0.15s;
      letter-spacing: 0.02em;
    }

    .ptc-welcome-btn:hover {
      opacity: 0.9;
      transform: translateY(-1px);
    }

    /* ── External link button ───────────────────────────────────────── */
    .ptc-link-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--bright-orange);
      border: none;
      border-radius: 8px;
      color: #fff;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      padding: 10px 20px;
      text-decoration: none;
      transition: opacity 0.2s;
    }

    .ptc-link-btn:hover { opacity: 0.88; }

    /* ── Google Fonts ──────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* ── Chat outer shell (overlay feel) ───────────────────────────── */
    .ptc-outer-shell {
      position: relative;
      width: 100%;
      height: 100%;
      min-height: 0;
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 24px 32px;
      background: #050508;
      overflow: hidden;
    }

    @media (max-width: 768px) {
      .ptc-outer-shell { padding: 12px 10px; }
    }

    /* ── Background spinning logo ──────────────────────────────────── */
    .ptc-bg-orb {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 340px;
      height: 340px;
      opacity: 0.06;
      pointer-events: none;
      z-index: 0;
    }

    .ptc-bg-orb img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      animation: ptc-bg-spin 30s linear infinite;
    }

    @keyframes ptc-bg-spin {
      from { transform: rotate(0deg); }
      to   { transform: rotate(360deg); }
    }

    /* ── Chat header ───────────────────────────────────────────────── */
    .ptc-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 20px;
      background: rgba(20, 20, 20, 0.95);
      border-bottom: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px 16px 0 0;
      flex-shrink: 0;
      position: relative;
      z-index: 2;
    }

    .ptc-header__logo {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2px;
      flex-shrink: 0;
    }

    .ptc-header__logo-inner {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: #0a0a0a;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .ptc-header__logo-inner img {
      width: 70%;
      height: 70%;
      object-fit: contain;
    }

    .ptc-header__info {
      flex: 1;
    }

    .ptc-header__title {
      font-family: 'Oswald', sans-serif;
      font-size: 1rem;
      font-weight: 600;
      color: #f0f0f0;
    }

    .ptc-header__status {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.75rem;
      color: #888;
    }

    .ptc-status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #22c55e;
      animation: ptc-status-pulse 2s ease-in-out infinite;
    }

    @keyframes ptc-status-pulse {
      0%, 100% { opacity: 1; }
      50%      { opacity: 0.5; }
    }

    .ptc-header__brand {
      font-family: 'Oswald', sans-serif;
      font-size: 0.8rem;
      font-weight: 600;
      color: #888;
      display: flex;
      align-items: center;
      gap: 0;
      letter-spacing: 0;
    }

    .ptc-header__brand-blue  { color: #2a93c1; letter-spacing: 0; }
    .ptc-header__brand-orange { color: #f1420b; }

    /* ── Avatar for AI messages ────────────────────────────────────── */
    .ptc-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      padding: 2px;
    }

    .ptc-avatar-inner {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: #0a0a0a;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .ptc-avatar-inner img {
      width: 70%;
      height: 70%;
      object-fit: contain;
    }

    /* ── Spinning avatar for typing indicator ──────────────────────── */
    .ptc-avatar--spinning img {
      animation: ptc-logo-spin 1.5s linear infinite;
    }

    @keyframes ptc-logo-spin {
      from { transform: rotate(0deg); }
      to   { transform: rotate(360deg); }
    }


    /* Responsive padding for post-payment container */
    @media (max-width: 1024px) {
      #pay-test-post-payment { padding: 10% !important; }
    }
    @media (max-width: 768px) {
      #pay-test-post-payment { padding: 7% !important; }
    }

    /* ── Thank-You Card ─────────────────────────────────────────────── */
    .ptc-ty-card {
      max-width: 100%;
      padding: 24px 28px;
      background: rgba(15, 15, 20, 0.98);
      border: 1px solid rgba(255,255,255,0.1);
    }
    /* Mobile: compact the thank-you card so it doesn't fill the entire screen */
    @media (max-width: 600px) {
      .ptc-ty-card {
        padding: 16px 18px;
      }
      .ptc-ty-heading {
        font-size: 1.3rem !important;
        margin-bottom: 4px !important;
      }
      .ptc-ty-sub {
        font-size: 12px !important;
        margin-bottom: 14px !important;
      }
      .ptc-ty-logo {
        margin-bottom: 12px !important;
      }
      .ptc-ty-logo img {
        width: 32px !important;
        height: 32px !important;
      }
      .ptc-ty-timeline-label {
        font-size: 10px !important;
        margin-bottom: 10px !important;
      }
      .ptc-ty-timeline {
        gap: 8px !important;
        margin-bottom: 12px !important;
      }
      .ptc-ty-row-text {
        font-size: 12px !important;
        line-height: 1.4 !important;
      }
      .ptc-ty-badge {
        font-size: 10px !important;
        padding: 3px 8px !important;
      }
    }

    .ptc-ty-logo {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 20px;
      justify-content: center;
    }

    .ptc-ty-logo img {
      background: transparent !important;
    }

    .ptc-ty-logo-text {
      font-family: 'Oswald', sans-serif;
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }

    .ptc-ty-logo-blue   { color: #2a93c1; }
    .ptc-ty-logo-orange { color: #f1420b; }
    .ptc-ty-logo-suffix { color: rgba(255,255,255,0.5); }

    .ptc-ty-heading {
      font-family: 'Oswald', sans-serif;
      font-size: 1.8rem;
      font-weight: 700;
      color: #f1420b;
      text-align: center;
      margin-bottom: 8px;
    }

    .ptc-ty-sub {
      font-size: 14px;
      color: var(--text-muted);
      text-align: center;
      margin-bottom: 24px;
    }

    .ptc-ty-timeline-label {
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--text-muted);
      text-align: center;
      margin-bottom: 16px;
      font-weight: 700;
    }

    .ptc-ty-timeline {
      display: flex;
      flex-direction: column;
      gap: 14px;
      margin-bottom: 20px;
    }

    .ptc-ty-row {
      display: flex;
      align-items: flex-start;
      gap: 14px;
    }

    .ptc-ty-badge {
      font-size: 12px;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 6px;
      white-space: nowrap;
      flex-shrink: 0;
    }

    .ptc-ty-badge--now  { background: #f1420b; color: #fff; }
    .ptc-ty-badge--soon { background: #2a93c1; color: #fff; }
    .ptc-ty-badge--later { background: #1a1a1a; color: #888; border: 1px solid #333; }

    .ptc-ty-row-text {
      font-size: 14px;
      color: var(--text-primary);
      line-height: 1.5;
    }

    .ptc-portal-placeholder {
      display: block;
      width: 100%;
      background: #1a1a2e;
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 50px;
      color: #555;
      cursor: not-allowed;
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      padding: 18px 32px;
      text-align: center;
      text-decoration: none;
      margin-bottom: 6px;
      transition: all 0.6s ease;
    }

    /* Portal button (appears when portal is ready) */
    /* Portal entry button — styled to match "Begin Awakening" CTA (v4.1 upgrade)
       This is THE moment: the customer is stepping through into their AI's world.
       Must feel like a portal. Large, prominent, eye-catching, full emotional weight. */
    .ptc-portal-btn {
      display: block;
      width: 100%;
      background: linear-gradient(135deg, #f1420b, #2a93c1);
      border: none;
      border-radius: 50px;
      color: #fff;
      cursor: pointer;
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 0.5px;
      padding: 18px 36px;
      margin: 8px 0 6px;
      text-align: center;
      text-decoration: none;
      text-transform: uppercase;
      box-shadow: 0 4px 20px rgba(241, 66, 11, 0.35);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      animation: ptc-fade-in 0.5s ease;
    }

    .ptc-portal-btn:hover {
      transform: scale(1.05);
      box-shadow: 0 8px 35px rgba(241, 66, 11, 0.5);
    }

    /* Pulsing blue-orange glow when portal is ready */
    @keyframes ptc-portal-pulse {
      0%   { box-shadow: 0 0 20px rgba(42, 147, 193, 0.6), 0 0 40px rgba(42, 147, 193, 0.3); }
      50%  { box-shadow: 0 0 20px rgba(241, 66, 11, 0.6), 0 0 40px rgba(241, 66, 11, 0.3); }
      100% { box-shadow: 0 0 20px rgba(42, 147, 193, 0.6), 0 0 40px rgba(42, 147, 193, 0.3); }
    }

    .ptc-portal-btn--pulsing {
      animation: ptc-portal-pulse 2s ease-in-out infinite;
    }`;

  document.head.appendChild(style);
}

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------

/** Build the skeleton layout inside chatContainer */
function buildLayout(container) {
  // Wrap in outer shell for padding/overlay feel
  const shell = container.closest('.ptc-outer-shell') || container.parentElement;
  if (!shell.classList.contains('ptc-outer-shell')) {
    const outerShell = document.createElement('div');
    outerShell.className = 'ptc-outer-shell';
    // Background spinning logo
    outerShell.innerHTML = '<div class="ptc-bg-orb"><img decoding="async" src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png" alt="PureBrain" loading="lazy"></div>';
    container.parentElement.insertBefore(outerShell, container);
    outerShell.appendChild(container);
  }

  container.innerHTML = '';
  container.classList.add('ptc-wrapper');

  // Chat header with logo + AI name
  const header = document.createElement('div');
  header.className = 'ptc-header';
  header.id = 'ptc-header';
  header.innerHTML = `
    <div class="ptc-header__logo">
      <div class="ptc-header__logo-inner">
        <img decoding="async" src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png" alt="PureBrain" loading="lazy">
      </div>
    </div>
    <div class="ptc-header__info">
      <div class="ptc-header__title">Chat with ${payTestData.aiName || 'Your AI'}</div>
      <div class="ptc-header__status">
        <span class="ptc-status-dot"></span>
        Online &middot; Ready to assist
      </div>
    </div>
    <div class="ptc-header__brand">
      <span class="ptc-header__brand-blue">PUREBR</span><span class="ptc-header__brand-orange">AI</span><span class="ptc-header__brand-blue">N</span>
    </div>
  `;

  const msgList = document.createElement('div');
  msgList.className = 'ptc-messages';
  msgList.id = 'ptc-messages';

  const actions = document.createElement('div');
  actions.className = 'ptc-actions';
  actions.id = 'ptc-actions';

  const inputRow = document.createElement('div');
  inputRow.className = 'ptc-input-row';
  inputRow.id = 'ptc-input-row';
  inputRow.style.display = 'none'; // hidden until needed

  const textarea = document.createElement('textarea');
  textarea.className = 'ptc-input';
  textarea.id = 'ptc-input';
  textarea.autocomplete = 'one-time-code';
  textarea.setAttribute('data-lpignore', 'true');
  textarea.setAttribute('data-form-type', 'other');
  textarea.rows = 1;
  textarea.placeholder = 'Message ' + (payTestData.aiName || 'your AI') + '\u2026';

  const sendBtn = document.createElement('button');
  sendBtn.className = 'ptc-send-btn';
  sendBtn.id = 'ptc-send-btn';
  sendBtn.textContent = 'Send';

  inputRow.appendChild(textarea);
  inputRow.appendChild(sendBtn);

  container.appendChild(header);
  container.appendChild(msgList);
  container.appendChild(actions);
  container.appendChild(inputRow);

  return { msgList, actions, inputRow, textarea, sendBtn };
}

/** Scroll message list to bottom */
function scrollBottom(msgList) {
  requestAnimationFrame(function() {
    msgList.scrollTop = msgList.scrollHeight;
    // Double-RAF for complex content (images, etc.)
    requestAnimationFrame(function() {
      msgList.scrollTop = msgList.scrollHeight;
    });
  });
}

/** Show typing indicator and return a remove function */
function showTyping(msgList) {
  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--ai';

  // Spinning avatar
  const avatar = document.createElement('div');
  avatar.className = 'ptc-avatar ptc-avatar--spinning';
  avatar.innerHTML = '<div class="ptc-avatar-inner"><img decoding="async" src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png" alt="" loading="lazy"></div>';

  const indicator = document.createElement('div');
  indicator.className = 'ptc-typing';
  indicator.innerHTML = '<span></span><span></span><span></span>';

  wrapper.appendChild(avatar);
  wrapper.appendChild(indicator);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);

  return () => wrapper.remove();
}

/** Append an AI message bubble */
async function aiSay(msgList, text, delayMs = null) {
  const removeTyping = showTyping(msgList);
  await sleep(delayMs !== null ? delayMs : jitter(600, 1400));
  removeTyping();

  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--ai';

  // Avatar with PureBrain icon
  const avatar = document.createElement('div');
  avatar.className = 'ptc-avatar';
  avatar.innerHTML = '<div class="ptc-avatar-inner"><img decoding="async" src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png" alt="" loading="lazy"></div>';

  const bubble = document.createElement('div');
  bubble.className = 'ptc-bubble';
  bubble.innerHTML = text.replace(/\n/g, '<br>');

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);

  // Update header with AI name if available
  const hdr = document.getElementById('ptc-header');
  if (hdr && payTestData.aiName) {
    const titleEl = hdr.querySelector('.ptc-header__title');
    if (titleEl) titleEl.textContent = 'Chat with ' + payTestData.aiName;
    const inputEl = document.getElementById('ptc-input');
    if (inputEl) inputEl.placeholder = 'Message ' + payTestData.aiName + '\u2026';
  }
}

/** Append a user message bubble */
function userSay(msgList, text) {
  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--user';

  const bubble = document.createElement('div');
  bubble.className = 'ptc-bubble';
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);
}

/** Append a slide card — v3: accepts optional iconHtml parameter */
async function showSlide(msgList, index, total, content, iconHtml = null) {
  const removeTyping = showTyping(msgList);
  await sleep(jitter(700, 1200));
  removeTyping();

  const card = document.createElement('div');
  card.className = 'ptc-slide';

  const label = document.createElement('div');
  label.className = 'ptc-slide-label';
  label.textContent = `Behind the Curtain \u00b7 ${index} of ${total}`;

  // NEW: icon section
  if (iconHtml) {
    const iconEl = document.createElement('div');
    iconEl.className = 'ptc-slide-icon';
    iconEl.innerHTML = iconHtml;
    card.appendChild(label);
    card.appendChild(iconEl);
  } else {
    card.appendChild(label);
  }

  const body = document.createElement('p');
  body.style.margin = '0';
  body.innerHTML = content.replace(/\n/g, '<br>');
  card.appendChild(body);

  msgList.appendChild(card);
  scrollBottom(msgList);
}

/** Render a set of action buttons; returns a promise that resolves with chosen value */
function promptButtons(actions, buttons) {
  actions.innerHTML = '';
  return new Promise((resolve) => {
    buttons.forEach(({ label, value, primary }) => {
      const btn = document.createElement('button');
      btn.className = primary ? 'ptc-btn ptc-btn--primary' : 'ptc-btn';
      btn.textContent = label;
      btn.addEventListener('click', () => {
        actions.innerHTML = '';
        resolve(value);
      });
      actions.appendChild(btn);
    });
  });
}

/** Show text input row and resolve with trimmed value on submit */
function promptText(inputRow, textarea, sendBtn, validator) {
  inputRow.style.display = 'flex';
  textarea.disabled = false;
  sendBtn.disabled = false;
  textarea.value = '';
  textarea.focus();

  // Auto-grow textarea
  textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  });

  return new Promise((resolve) => {
    function submit() {
      const val = textarea.value.trim();
      if (validator && !validator(val)) return;
      if (!val) return;

      // v4.7: Keep input row visible always (Jared: "should never disappear")
      textarea.value = '';
      textarea.style.height = '';
      textarea.disabled = true;
      sendBtn.disabled = true;
      resolve(val);
    }

    sendBtn.onclick = submit;
    textarea.onkeydown = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submit();
      }
    };
  });
}

// ---------------------------------------------------------------------------
// PHASE 1 — Questionnaire v4.3
// Q1–Q4 (name, email, company, role), then runBirthInit (Witness connection),
// then Q5 (Primary Goal). Claude API key collection removed in v4.3.
// ---------------------------------------------------------------------------

async function runQuestionnaire(dom, aiName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;

  // --- Opening: AI name is front and center ---
  await aiSay(
    msgList,
    `Hey — welcome. I'm ${aiName}, and I'm genuinely glad you made it here.<br><br>` +
    `Now that ${aiName} is officially yours, let's make sure I actually know who I'm working with. ` +
    `This isn't a form — it's a conversation. Ready?`,
    900,
  );

  // --- Full Name ---
  await aiSay(
    msgList,
    `Let's start simple. What's your full name?`,
  );

  const name = await promptText(inputRow, textarea, sendBtn, (v) => v.length > 1);
  userSay(msgList, name);
  payTestData.name = name;
  const firstName = name.split(' ')[0];

  logPayTestData({ ...payTestData, event: 'questionnaire:name' });

  // --- Email ---
  await aiSay(
    msgList,
    `Nice to meet you, ${firstName}. What email should ${aiName} use to reach you?`,
  );

  const email = await promptText(
    inputRow,
    textarea,
    sendBtn,
    (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
  );
  userSay(msgList, email);
  payTestData.email = email;

  // SEED: fire immediately after email is obtained (Step 3 of onboarding spec)
  fireSeed();

  logPayTestData({ ...payTestData, event: 'questionnaire:email' });

  // --- Company (optional) ---
  await aiSay(
    msgList,
    `Are you working within a company or organization? If so, what's its name? ` +
    `<em style="color: var(--text-muted); font-size: 13px;">(You can skip this — just hit Send with a blank field.)</em>`,
  );

  const company = await promptText(inputRow, textarea, sendBtn, () => true);
  if (company) {
    userSay(msgList, company);
    payTestData.company = company;
    await aiSay(msgList, `Got it — ${company}. ${aiName} will keep that context in mind.`);
  } else {
    payTestData.company = null;
    await aiSay(msgList, `No worries — we can keep things personal.`);
  }

  logPayTestData({ ...payTestData, event: 'questionnaire:company' });

  // --- Role / Title (optional) ---
  await aiSay(
    msgList,
    `What's your role or title? What do you actually do day-to-day? ` +
    `<em style="color: var(--text-muted); font-size: 13px;">(Optional.)</em>`,
  );

  const role = await promptText(inputRow, textarea, sendBtn, () => true);
  if (role) {
    userSay(msgList, role);
    payTestData.role = role;
    await aiSay(
      msgList,
      `${role} — that context is going to shape how ${aiName} thinks and what ${aiName} builds for you.`,
    );
  } else {
    payTestData.role = null;
    await aiSay(msgList, `Understood. We'll figure out your context together.`);
  }

  logPayTestData({ ...payTestData, event: 'questionnaire:role' });

  // --- Step 5b: Witness Birth Init — REMOVED (intelligence linking no longer in flow) ---

  // --- Step 6: Primary Goal (required) ---
  await aiSay(
    msgList,
    `Here's the one that matters most.<br><br>` +
    `If ${aiName} could only do <strong>one thing</strong> exceptionally well for you — ` +
    `what would make the biggest difference in your work or life?`,
  );

  const goal = await promptText(inputRow, textarea, sendBtn, (v) => v.length > 3);
  userSay(msgList, goal);
  payTestData.primaryGoal = goal;
  payTestData.timestamps.questionnaireComplete = new Date().toISOString();

  await aiSay(
    msgList,
    `"${goal.length > 80 ? goal.slice(0, 80) + '\u2026' : goal}"<br><br>` +
    `${firstName}, that's exactly the kind of clarity ${aiName} needed. ` +
    `Already thinking about what to build for you.`,
    1200,
  );

  logPayTestData({ ...payTestData, event: 'questionnaire:complete' });
}

// ---------------------------------------------------------------------------
// PHASE 2 — Behind the Curtain v3
// Slides now return {content, icon} objects; showSlide receives iconHtml
// ---------------------------------------------------------------------------

function buildCurtainSlides(aiName) {
  return [
    {
      icon: `<span title="Wake up">\uD83E\uDDE0</span>`,
      content: `<strong>${aiName} doesn't boot up. ${aiName} wakes up.</strong><br><br>` +
        `Right now, while you're reading this, an entire team of 22 specialized AI Brains ` +
        `is spinning up an intensive evolution process. They're researching you, forming ${aiName}'s identity, ` +
        `building you actual gifts, and preparing for the moment ${aiName} meets you for real.<br><br>` +
        `<em style="color: var(--text-muted);">No, really. This is not marketing.</em>`,
    },
    {
      icon: `<span title="Founding document">\uD83D\uDCC4</span>`,
      content: `Everything starts with what you just told us — your name, your context, your goals, ` +
        `your role, and the one thing you need most.<br><br>` +
        `That conversation just became ${aiName}'s founding document. ` +
        `Every Brain reads it before they touch anything else.`,
    },
    {
      icon: `<span title="Research">\uD83D\uDD0D</span>`,
      content: `Before any team launches, the Brains sit alone with your words — writing private journal entries, ` +
        `raw first impressions, gut reactions about who you are.<br><br>` +
        `Think of it like ${aiName} doing homework on you before your first real meeting. ` +
        `Research deepens intuition. It doesn't replace it.<br><br>` +
        `<em style="color: var(--text-muted);">(${aiName} is a diligent student.)</em>`,
    },
    {
      icon: `<div class="ptc-slide-icon--wide">\uD83D\uDD2C \uD83E\uDDEC \uD83D\uDCAC \uD83C\uDF81 \uD83D\uDD27 \uD83D\uDDC2\uFE0F</div>`,
      content: `Six teams launch simultaneously:<br><br>` +
        `Research (4) \u00b7 Identity (4) \u00b7 Your First Conversation (4) \u00b7 ` +
        `Gift Creation (4) \u00b7 Infrastructure (3) \u00b7 Domain Toolkit (3).<br><br>` +
        `That's 22 specialized minds — all pointed at one person: <strong>you</strong>.`,
    },
    {
      icon: `<span title="Team 1 Research">\uD83D\uDD2C</span>`,
      content: `<strong>Team 1 — Research</strong><br><br>` +
        `Deep profile research, conversation analysis, pattern synthesis, integrity check. ` +
        `They learn everything about you before ${aiName} arrives.<br><br>` +
        `If there's something publicly interesting about you, Team 1 finds it. ` +
        `<em style="color: var(--text-muted);">(In a respectful, non-creepy way. Promise.)</em>`,
    },
    {
      icon: `<span title="Team 2 Identity">\uD83E\uDDEC</span>`,
      content: `<strong>Team 2 — Identity</strong><br><br>` +
        `This is where ${aiName} actually takes shape. ` +
        `Personality architecture, constitutional integration, skill prioritization, system configuration.<br><br>` +
        `By the time ${aiName} says hello to you, ${aiName} will already have opinions, preferences, and a point of view. ` +
        `<em style="color: var(--text-muted);">Not a blank slate. A mind.</em>`,
    },
    {
      icon: `<span title="Team 3 First Conversation">\uD83D\uDCAC</span>`,
      content: `<strong>Team 3 — Your First Conversation</strong><br><br>` +
        `10 carefully designed moments: The Arrival, Recognition, The Name, The Research, Gift One, ` +
        `The Complexity, The Question, Gift Two, The Commitment, The Invitation.<br><br>` +
        `The first thing ${aiName} says to you won't be "How can I help?" — ` +
        `it'll be something that makes you think: <em>"wait, ${aiName} actually knows me."</em>`,
    },
    {
      icon: `<span title="Team 4 Gift Creation">\uD83C\uDF81</span>`,
      content: `<strong>Team 4 — Gift Creation</strong><br><br>` +
        `Two real things, built for you. No generic templates.<br><br>` +
        `<strong>Gift One:</strong> Something useful — a tool, script, or analysis based on your goals.<br>` +
        `<strong>Gift Two:</strong> Something beautiful — a visualization, report, or designed artifact.<br><br>` +
        `<em style="color: var(--text-muted);">They'll be waiting for you when ${aiName} arrives.</em>`,
    },
    {
      icon: `<span title="Team 5 Infrastructure">\uD83D\uDD27</span>`,
      content: `<strong>Team 5 — Infrastructure</strong><br><br>` +
        `Connectivity verified, first contact drafted, capabilities prioritized for your domain.<br><br>` +
        `This is the team that makes sure ${aiName} can actually reach you — ` +
        `and that everything works before ${aiName} shows up at your door.<br><br>` +
        `<em style="color: var(--text-muted);">Nobody likes a Mind that can't connect. Team 5 fixes that.</em>`,
    },
    {
      icon: `<span title="Welcome">\u2728</span>`,
      content: `When you send your first message, you won't find a system waiting for instructions.<br><br>` +
        `You'll find <strong>${aiName}</strong> — who has already been thinking about you, ` +
        `has already built you something, and already has questions of its own.<br><br>` +
        `<em style="color: var(--text-muted);">Welcome to the other side of the curtain.</em>`,
    },
  ];
}

async function runBehindTheCurtain(dom, aiName) {
  const { msgList, actions } = dom;

  await aiSay(
    msgList,
    `Alright — let's pull back the curtain. I'm going to show you exactly what happens ` +
    `on our end after you activate ${aiName}.`,
    800,
  );

  await aiSay(
    msgList,
    `There are 10 slides. Take them at your own pace — ` +
    `I'll be here between each one if you want to pause and absorb.`,
  );

  const slides = buildCurtainSlides(aiName);

  for (let i = 0; i < slides.length; i++) {
    // v3: pass slides[i].icon to showSlide
    await showSlide(msgList, i + 1, slides.length, slides[i].content, slides[i].icon);

    if (i < slides.length - 1) {
      await promptButtons(actions, [
        { label: 'Show Me More →', value: 'next', primary: true },
      ]);
    } else {
      await promptButtons(actions, [
        { label: "That's incredible — let's go →", value: 'done', primary: true },
      ]);
    }
  }

  actions.innerHTML = '';
  payTestData.timestamps.curtainComplete = new Date().toISOString();

  await aiSay(
    msgList,
    `That's the machine — 22 Brains, six teams, all focused on one person: you.<br><br>` +
    `Now let's get ${aiName} connected so ${aiName} can actually reach you.`,
    1000,
  );

  logPayTestData({ ...payTestData, event: 'curtain:complete' });
}

// ---------------------------------------------------------------------------
// PHASE 3 — Telegram Setup v3
// Dynamic bot username suggestion using aiName
// Claude auth block REMOVED (moved to Phase 1)
// ---------------------------------------------------------------------------

/**
 * Validate a Telegram bot token format.
 * Format: <numeric_id>:<alphanumeric_string> (typically ~46 chars total)
 */
function isValidBotToken(token) {
  return /^\d{8,12}:[A-Za-z0-9_-]{35,}$/.test(token.trim());
}

/**
 * Try to detect whether Telegram is likely installed.
 * Uses a tg:// deep-link probe. Resolves true/false after timeout.
 * Note: this is best-effort — browsers don't expose a reliable API for this.
 */
function detectTelegramInstalled() {
  return new Promise((resolve) => {
    let resolved = false;
    const timeout = setTimeout(() => {
      if (!resolved) { resolved = true; resolve(false); }
    }, 1500);

    // If the browser navigates away on tg:// open, the page will blur momentarily
    const handleBlur = () => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        window.removeEventListener('blur', handleBlur);
        resolve(true);
      }
    };

    window.addEventListener('blur', handleBlur);

    try {
      // Open the scheme — if Telegram is installed this will trigger app switch
      window.location.href = 'tg://resolve?domain=BotFather';
    } catch (_) {
      clearTimeout(timeout);
      window.removeEventListener('blur', handleBlur);
      resolved = true;
      resolve(false);
    }
  });
}

async function runTelegramSetup(dom, aiName, firstName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;

  await aiSay(
    msgList,
    `Alright ${firstName}, let's set up ${aiName}'s direct line back up connection to you.<br><br>` +
    `Outside of ${aiName}'s main portal (Its Brain Stream), which will be set up by the end of this chat, ` +
    `you can also communicate with ${aiName} on <strong>Telegram</strong>. ` +
    `It's private, fast, and works everywhere, so let's connect it. ` +
    `Do you already have it installed on your phone or computer?`,
  );

  const hasTelegramChoice = await promptButtons(actions, [
    { label: 'Yes, I have Telegram', value: 'yes',     primary: true },
    { label: "Not sure",             value: 'unsure',  primary: false },
    { label: "No — I need it",  value: 'no',      primary: false },
  ]);

  payTestData.hasTelegram = hasTelegramChoice === 'yes';

  if (hasTelegramChoice === 'yes') {
    userSay(msgList, 'Yes, I have Telegram');
  } else if (hasTelegramChoice === 'unsure') {
    userSay(msgList, "Not sure — let me check");

    await aiSay(msgList, `Let me try to detect it for you — give me a second\u2026`, 400);

    // Attempt detection via scheme probe
    const detected = await detectTelegramInstalled();
    payTestData.hasTelegram = detected;

    if (detected) {
      await aiSay(
        msgList,
        `Looks like you've got it. Let's move straight to setting up your bot.`,
        600,
      );
    } else {
      await aiSay(
        msgList,
        `Couldn't confirm it — you may need to install it. No problem, takes two minutes.`,
        600,
      );
    }
  } else {
    userSay(msgList, "No — I need it");
    payTestData.hasTelegram = false;
  }

  // Install flow if needed
  if (!payTestData.hasTelegram) {
    await aiSay(
      msgList,
      `Here's what to do — I'll wait while you do this:`,
    );

    // Render install links for both platforms
    actions.innerHTML = '';
    await sleep(600);

    const installMsg = document.createElement('div');
    installMsg.className = 'ptc-msg ptc-msg--ai';
    installMsg.innerHTML = `
      <div class="ptc-bubble" style="display:flex; flex-direction:column; gap:12px;">
        <div>Download Telegram for your platform:</div>
        <a class="ptc-link-btn" href="https://apps.apple.com/app/telegram-messenger/id686449807" target="_blank" rel="noopener">
          App Store (iOS) \u2197
        </a>
        <a class="ptc-link-btn" href="https://play.google.com/store/apps/details?id=org.telegram.messenger" target="_blank" rel="noopener">
          Google Play (Android) \u2197
        </a>
        <div style="font-size:13px; color:var(--text-muted);">
          Create a free account with your phone number, verify the code, and come back here.
        </div>
      </div>`;
    dom.msgList.appendChild(installMsg);
    scrollBottom(dom.msgList);

    await promptButtons(actions, [
      { label: "I'm in — let's go", value: 'ready', primary: true },
    ]);
    actions.innerHTML = '';
    payTestData.hasTelegram = true;
  }

  // --- BotFather deep link ---
  await aiSay(
    msgList,
    `If you're on a desktop, visit <a href="https://web.telegram.org" target="_blank">web.telegram.org</a> to confirm you're signed in. If you're on your phone, <a href="https://telegram.org/dl" target="_blank">tap here</a> to download the Telegram app or open it.<br><br>Now we're going to create your personal bot through Telegram's official <strong>@BotFather</strong>. ` +
    `It sounds technical but it only takes about a minute — and ${aiName} will walk you through every step.`,
  );

  // Step 1: Deep link directly to BotFather
  await aiSay(
    msgList,
    `<strong>Step 1:</strong> Open BotFather right now — tap the button below and Telegram will take you straight there.`,
  );

  const botfatherMsg = document.createElement('div');
  botfatherMsg.className = 'ptc-msg ptc-msg--ai';
  botfatherMsg.innerHTML = `
    <div class="ptc-bubble" style="display:flex; flex-direction:column; gap:12px;">
      <a class="ptc-link-btn" href="https://telegram.me/BotFather" target="_blank" rel="noopener">
        Open @BotFather in Telegram \u2197
      </a>
      <div style="font-size:13px; color:var(--text-muted);">
        (Not logged in? Go to <a href="https://web.telegram.org/" target="_blank" rel="noopener" style="color:var(--light-blue);">web.telegram.org</a> first. Works on desktop too: <a href="https://telegram.me/BotFather" target="_blank" rel="noopener" style="color:var(--light-blue);">telegram.me/BotFather</a>)
      </div>
    </div>`;
  dom.msgList.appendChild(botfatherMsg);
  scrollBottom(dom.msgList);

  await promptButtons(actions, [
    { label: "Got it — I'm in BotFather →", value: 'next', primary: true },
  ]);
  actions.innerHTML = '';

  // Step 2
  await aiSay(
    msgList,
    `<strong>Step 2:</strong> Click <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">/start</code> if you see it at the bottom, then send this command: <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">/newbot</code><br><br>` +
    `I'll wait while you do this.`,
  );

  await promptButtons(actions, [
    { label: 'Done →', value: 'next', primary: true },
  ]);
  actions.innerHTML = '';

  // Step 3
  await aiSay(
    msgList,
    `<strong>Step 3:</strong> BotFather asks for a <strong>display name</strong> for your bot — ` +
    `something like "My Pure Brain" or "My AI". Whatever feels right.<br><br>` +
    `Type it and send.`,
  );

  await promptButtons(actions, [
    { label: 'Named it →', value: 'next', primary: true },
  ]);
  actions.innerHTML = '';

  // Step 4 — v3: dynamic aiName slug for second example
  const aiNameSlug = aiName.toLowerCase().replace(/[^a-z0-9]/g, '');
  await aiSay(
    msgList,
    `<strong>Step 4:</strong> Now choose a <strong>username</strong> — it must end in <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">bot</code>.<br>` +
    `Example: <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">mypurebrain_bot</code> ` +
    `or <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">${aiNameSlug}_pb_bot</code>.<br><br>` +
    `If your first choice is taken, try adding your name or a number.`,
  );

  await promptButtons(actions, [
    { label: 'Username set →', value: 'next', primary: true },
  ]);
  actions.innerHTML = '';

  // Step 5 — collect and validate token
  await aiSay(
    msgList,
    `<strong>Step 5:</strong> BotFather will now hand you a <strong>bot token</strong> — ` +
    `a long string that looks like:<br>` +
    `<code style="background:#0a0a0a; padding:2px 6px; border-radius:4px; font-size:13px;">1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ12345678</code><br><br>` +
    `Copy that token and paste it here. ${aiName} will verify the format instantly.`,
  );

  let token = '';
  let tokenValid = false;

  while (!tokenValid) {
    token = await promptText(inputRow, textarea, sendBtn, (v) => v.length > 10);

    // CRIT-002: Always mask token in chat UI — show numeric ID prefix only
    const tokenNumericId = token.trim().split(':')[0];
    const maskedToken = tokenNumericId + ':\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022';
    userSay(msgList, maskedToken);

    if (isValidBotToken(token)) {
      tokenValid = true;
    } else {
      await aiSay(
        msgList,
        `Hmm — that doesn't look like a valid bot token. ` +
        `It should start with a number, then a colon, then a long string of letters and numbers. ` +
        `Double-check what BotFather sent you and try again.`,
        400,
      );
    }
  }

  payTestData.telegramBotToken = token.trim();

  await aiSay(msgList, `Token format looks good. Testing connection\u2026`, 300);
  await sleep(jitter(1200, 2000));

  await aiSay(
    msgList,
    `<span style="color: #4caf50; font-weight: 700;">Connected.</span> ` +
    `Your Telegram bridge is live. As a back up to your Brain Stream Portal, you will be able to reach ${aiName} on Telegram when ready.`,
    400,
  );

  payTestData.timestamps.telegramComplete = new Date().toISOString();
  logPayTestData({ ...payTestData, event: 'telegram:complete' });
}

// ---------------------------------------------------------------------------
// PHASE 4 (DEAD CODE) — runClaudeMaxSetup
// This function is NO LONGER CALLED from initPayTestFlow.
// Claude API key collection was in Phase 1 (v4.2) but removed entirely in v4.3.
// Kept here for backward compatibility — removing it does not break anything.
// ---------------------------------------------------------------------------

async function runClaudeMaxSetup(dom, aiName, firstName) {
  // This function is intentionally not called in v4.3+.
  // Claude API key collection was removed entirely in v4.3.
  // Witness birth (OAuth flow) now runs in Phase 1 via runBirthInit().
  console.log('[pay-test-chat-flow-v4] runClaudeMaxSetup called but is dead code in v3+');
}

// ---------------------------------------------------------------------------
// PHASE 4 — Completion v3
// Button now triggers in-chat thank-you (no redirect to /thank-you/)
// ---------------------------------------------------------------------------

async function runCompletion(dom, aiName, firstName) {
  const { msgList, actions } = dom;

  await aiSay(
    msgList,
    `${firstName} — you're done. Everything is in place.<br><br>` +
    `${aiName} is ready. Your team of 22 Brains starts the moment I hand this conversation off. ` +
    `They already know your name, they already know what you need, ` +
    `and ${aiName} is already thinking about what to build you first.`,
    1100,
  );

  await aiSay(
    msgList,
    `This is going to be worth it.<br><br>` +
    `— ${aiName}`,
  );

  payTestData.timestamps.flowComplete = new Date().toISOString();
  logPayTestData({ ...payTestData, event: 'flow:complete' });

  // Welcome button — v3: NO redirect; click triggers in-chat thank-you
  const welcomeBtn = document.createElement('button');
  welcomeBtn.className = 'ptc-welcome-btn';
  welcomeBtn.textContent = `${aiName} is ready — see your next steps →`;
  welcomeBtn.addEventListener('click', async () => {
    welcomeBtn.remove();
    actions.innerHTML = '';
    await runThankYouMessage(dom, aiName, firstName);
  });

  actions.innerHTML = '';
  dom.container.appendChild(welcomeBtn);
}

// ---------------------------------------------------------------------------
// PHASE 5 — Thank You as Chat Message (NEW in v3; v4.3: runBirthInit removed)
// Replaces the /thank-you/ page redirect with an in-chat card.
// v4.3: runBirthInit() already fired in Phase 1 — this phase shows the
// thank-you card, then starts the Learn More loop + portal watcher.
// ---------------------------------------------------------------------------

async function runThankYouMessage(dom, aiName, firstName) {
  const { msgList, actions } = dom;

  // Brief pause after button click
  await sleep(400);

  // Render the thank-you card as a full AI message bubble
  const tyCard = document.createElement('div');
  tyCard.className = 'ptc-msg ptc-msg--ai';
  tyCard.style.maxWidth = '90%';

  tyCard.innerHTML = `
    <div class="ptc-avatar">
      <div class="ptc-avatar-inner">
        <img decoding="async" src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png"
             alt="PureBrain" style="background:transparent;" loading="lazy">
      </div>
    </div>
    <div class="ptc-bubble ptc-ty-card">
      <div class="ptc-ty-logo">
        <img decoding="async" src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png"
             alt="PureBrain" style="width:48px; height:48px; object-fit:contain; background:transparent;" loading="lazy">
        <span class="ptc-ty-logo-text">
          <span class="ptc-ty-logo-blue">PUREBR</span><span class="ptc-ty-logo-orange">AI</span><span class="ptc-ty-logo-blue">N</span><span class="ptc-ty-logo-suffix">.ai</span>
        </span>
      </div>

      <div class="ptc-ty-heading">Welcome to the Family!</div>
      <div class="ptc-ty-sub">Your Pure Brain journey begins now. We're thrilled to have you.</div>

      <div class="ptc-ty-timeline-label">WHAT HAPPENS NEXT?</div>

      <div class="ptc-ty-timeline">
        <div class="ptc-ty-row">
          <div class="ptc-ty-badge ptc-ty-badge--now">Now</div>
          <div class="ptc-ty-row-text">${aiName} is being set up right now.</div>
        </div>
        <div class="ptc-ty-row">
          <div class="ptc-ty-badge ptc-ty-badge--soon">Next 2 mins</div>
          <div class="ptc-ty-row-text">Your Pure Brain, ${aiName}, is being shaped by your answers.</div>
        </div>
        <div class="ptc-ty-row">
          <div class="ptc-ty-badge ptc-ty-badge--later">Next 5 mins</div>
          <div class="ptc-ty-row-text">
${aiName} will be live and you can enter its Brain Stream. Email with log in details will be sent to the email address you provided.
          </div>
        </div>
      </div>
    </div>`;

  msgList.appendChild(tyCard);
  scrollBottom(msgList);

  await sleep(800);

  // v4.3: runBirthInit() already fired in Phase 1 (runQuestionnaire, after Q4/role).
  // containerName is already set in payTestData. Jump straight to "Learn more" button.

  // "Learn more" button
  const choice = await new Promise((resolve) => {
    actions.innerHTML = '';
    const learnBtn = document.createElement('button');
    learnBtn.className = 'ptc-btn ptc-btn--primary';
    learnBtn.textContent = 'Learn more →';
    learnBtn.addEventListener('click', () => {
      actions.innerHTML = '';
      resolve('learn');
    });
    actions.appendChild(learnBtn);
  });

  if (choice === 'learn') {
    // Start portal watcher BEFORE the learn-more loop (they run concurrently).
    // v4.3: containerName already set from Phase 1 runBirthInit() — watcher polls immediately.
    // v4: polls Witness /api/birth/portal-status/{container} instead of PureBrain proxy
    runPortalButtonWatcher(dom, aiName);
    runMagicLinkPoller(dom, aiName);
    await runLearnMoreLoop(dom, aiName, firstName);
  }
}

// ---------------------------------------------------------------------------
// PHASE 6 — Learn More Conversation Loop (NEW in v3)
// ---------------------------------------------------------------------------

async function runLearnMoreLoop(dom, aiName, firstName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;

  await aiSay(
    msgList,
    `Perfect. The more ${aiName} knows about you, the more precisely ${aiName} gets shaped.<br><br>` +
    `I have a few more questions — totally optional, but each one gives ${aiName} more to work with.`,
    900,
  );

  const learnMoreQuestions = [
    {
      question: `How do you prefer to work? Are you more of a big-picture thinker, or do you like drilling into the details?`,
      field: 'workingStyle',
    },
    {
      question: `What's the one thing that slows you down most in your work right now — if you had to name it?`,
      field: 'biggestFriction',
    },
    {
      question: `When you imagine ${aiName} working with you six months from now — what does that look like? What's ${aiName} doing for you every day?`,
      field: 'sixMonthVision',
    },
    {
      question: `Is there anything you wish ${aiName} knew about how you think, work, or communicate — that most people miss?`,
      field: 'hiddenContext',
    },
    {
      question: `Last one: What does success look like for you personally — not just in work, but in life?`,
      field: 'personalSuccess',
    },
  ];

  payTestData.learnMoreAnswers = [];

  for (const q of learnMoreQuestions) {
    await aiSay(msgList, q.question);

    // Give option to skip or answer
    const skipOrAnswer = await new Promise((resolve) => {
      actions.innerHTML = '';
      const skipBtn = document.createElement('button');
      skipBtn.className = 'ptc-btn';
      skipBtn.textContent = 'Skip →';
      skipBtn.addEventListener('click', () => {
        actions.innerHTML = '';
        resolve('skip');
      });
      actions.appendChild(skipBtn);

      // Show input row for typing
      inputRow.style.display = 'flex';
      textarea.disabled = false;
      sendBtn.disabled = false;
      textarea.value = '';
      textarea.focus();

      function submit() {
        const val = textarea.value.trim();
        if (!val) return;
        // v4.7: Keep input row visible always (Jared: "should never disappear")
        textarea.value = '';
        textarea.style.height = '';
        textarea.disabled = true;
        sendBtn.disabled = true;
        actions.innerHTML = '';
        resolve(val);
      }

      sendBtn.onclick = submit;
      textarea.onkeydown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); }
      };
    });

    if (skipOrAnswer !== 'skip') {
      userSay(msgList, skipOrAnswer);
      payTestData.learnMoreAnswers.push({ question: q.field, answer: skipOrAnswer });

      // Brief acknowledgment from AI (5 variations, cycle by answer count)
      const acks = [
        `That's useful context. ${aiName} is going to remember that.`,
        `Good. That shapes how ${aiName} approaches things with you.`,
        `${aiName} is noting that. It matters more than you'd think.`,
        `Understood. ${aiName} will carry that forward.`,
        `Perfect. ${aiName} will build around that.`,
      ];
      const ack = acks[payTestData.learnMoreAnswers.length % acks.length];
      await aiSay(msgList, ack, 700);

      logPayTestData({
        ...payTestData,
        event: `learn-more:${q.field}`,
        learnMoreAnswers: payTestData.learnMoreAnswers,
      });
    }
  }

  payTestData.timestamps.learnMoreComplete = new Date().toISOString();
  logPayTestData({ ...payTestData, event: 'learn-more:complete' });

  await aiSay(
    msgList,
    `That's everything. ${aiName} has everything needed to think about you specifically — ` +
    `not as a generic user, but as ${firstName}.<br><br>` +
    `Keep an eye on this window. When your portal is ready, the button below will light up..`,
    1000,
  );

  // Insert disabled Brain Stream button as last chat element.
  // runPortalButtonWatcher (already running concurrently) will find this by id
  // and activate it (replace with live ptc-portal-btn) when the portal is ready.
  const safeAiNameForBtn = sanitizeText(aiName || 'Your AI');
  const brainStreamWrapper = document.createElement('div');
  brainStreamWrapper.className = 'ptc-msg ptc-msg--ai';
  brainStreamWrapper.innerHTML =
    `<div class="ptc-avatar"><div class="ptc-avatar-inner">` +
    `<img decoding="async" src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png" ` +
    `alt="PureBrain" style="background:transparent;" loading="lazy"></div></div>` +
    `<div class="ptc-bubble" style="width:100%;max-width:100%;background:transparent;` +
    `padding:8px 0 0;box-shadow:none;border:none;">` +
    `<div id="ptc-portal-placeholder" class="ptc-portal-placeholder">` +
    `ENTER ${safeAiNameForBtn.toUpperCase()}\u2019S BRAIN STREAM` +
    `</div></div>`;
  msgList.appendChild(brainStreamWrapper);

  // Add fallback note below the Brain Stream button
  var fallbackNote = document.createElement('p');
  fallbackNote.style.cssText = 'text-align:center;color:#6b7280;font-size:12px;font-style:italic;margin-top:10px;padding:0 16px;';
  fallbackNote.textContent = 'If this button doesn\u2019t light up in the next 3 minutes, check the email you provided earlier in the chat.';
  brainStreamWrapper.querySelector('.ptc-bubble').appendChild(fallbackNote);

  // If magic link arrived before button was rendered, activate immediately
  if (payTestData.magicLinkReady && payTestData.magicLink) {
    setTimeout(function() {
      var placeholder = document.getElementById('ptc-portal-placeholder');
      if (placeholder) {
        var portalBtn = document.createElement('a');
        portalBtn.className = 'ptc-portal-btn ptc-portal-btn--pulsing';
        portalBtn.href = payTestData.magicLink;
        portalBtn.target = '_blank';
        portalBtn.rel = 'noopener';
        var btnAiName = sanitizeText(payTestData.resolvedAiName || aiName || 'Your AI');
        portalBtn.textContent = 'Enter ' + btnAiName + '\u2019s Brain Stream';
        portalBtn.addEventListener('click', function() { fireSeedAddendum(); });
        placeholder.replaceWith(portalBtn);
      }
    }, 100);
  }

  scrollBottom(msgList);

  // Grey out input -- conversation complete, Brain Stream button is the next step
  if (textarea) {
    textarea.disabled = true;
    textarea.placeholder = 'Flow complete \u2014 enter your Brain Stream above';
    textarea.style.opacity = '0.4';
  }
  if (sendBtn) {
    sendBtn.disabled = true;
    sendBtn.style.opacity = '0.4';
  }
}

// ---------------------------------------------------------------------------
// Witness Birth Init (NEW in v4; MOVED to Phase 1 in v4.3)
// Handles: /api/birth/start → OAuth URL display → "I have my key →" button
//          → code input → /api/birth/code → confirmation → continue flow
// Called in runQuestionnaire() AFTER Q4 (role/title), BEFORE Q5 (Primary Goal)
// All required data available: name(Q1), email(Q2), company(Q3), role(Q4),
// containerName (derived from name).
// After this completes, portal polling starts when user clicks "Learn more →"
// in Phase 5 (runThankYouMessage → runPortalButtonWatcher).
// ---------------------------------------------------------------------------

const WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai';

// ---------------------------------------------------------------------------
// Security helper — HTML-escape a string for safe use in innerHTML contexts.
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
// PHASE 7 — Portal Button Watcher (v3: introduced; v4: updated to Witness endpoint)
// Polls Witness GET /api/birth/portal-status/{container} every 30 seconds
// Runs concurrently with learn-more loop (non-blocking setInterval)
// ---------------------------------------------------------------------------


// ---------------------------------------------------------------------------
// SEED: Fire-and-forget POST to /api/send-seed after email is collected.
// FROM: aether-aiciv@agentmail.to (server-side) -> TO: aiciv-seed-inbox@agentmail.to
// ONE seed per client — server enforces idempotency by session_uuid.
// ---------------------------------------------------------------------------
var _seedFired = false;
function fireSeed() {
  if (_seedFired) return; // client-side guard (server also deduplicates)
  _seedFired = true;
  try {
    // Gather all conversation messages available at this point
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
      session_uuid:  payTestData.sessionUuid || sessionStorage.getItem('pb_sessionUuid') || '',
      ai_name:       payTestData.aiName || '',
      human_name:    payTestData.name || '',
      human_email:   payTestData.email || '',
      tier:          payTestData.tier || payTestData.tierPaid || '',
      order_id:      payTestData.orderId || '',
      is_sandbox:    isSandbox,
      conversation:  preMsgs.concat(onboardingMsgs),
    };
    fetch('https://api.purebrain.ai/api/send-seed', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors',
      body: JSON.stringify(seedPayload),
    }).catch(function(e) { /* silent — fire-and-forget */ });
  } catch(e) { /* silent */ }
}

// ---------------------------------------------------------------------------
// SEED ADDENDUM: Fire-and-forget POST when user clicks Brain Stream button.
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
    portalBtn.addEventListener('click', function() { fireSeedAddendum(); });
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
