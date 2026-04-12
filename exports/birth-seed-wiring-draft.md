# full-stack-developer: /birth/seed Wiring Draft

**Agent**: full-stack-developer
**Domain**: Full Stack Development
**Date**: 2026-02-27

---

## Summary

Research-only analysis of the chatbox flow:complete trigger and what /birth/seed wiring would look like. No files were deployed or modified.

---

## 1. Data Available at flow:complete

The `flow:complete` event fires inside `runCompletion()` at line 9915-9916 of both page content files. At that exact moment, the following fields are populated in `payTestData`:

### Fields guaranteed populated by flow:complete

| Field | Source | Notes |
|---|---|---|
| `payTestData.aiName` | initPayTestFlow() param | Sanitized via sanitizeText() |
| `payTestData.tier` | initPayTestFlow() param | Same as `tierPaid` (they are the same variable, stored as `tier`) |
| `payTestData.orderId` | initPayTestFlow() param | May be null |
| `payTestData.name` | Phase 1 Q1 questionnaire | User's first name |
| `payTestData.email` | Phase 1 Q2 questionnaire | User's email |
| `payTestData.company` | Phase 1 Q3 questionnaire | May be null (user can skip) |
| `payTestData.role` | Phase 1 Q4 questionnaire | May be null (user can skip) |
| `payTestData.primaryGoal` | Phase 1 Q5 (after birth init) | Free-text goal |
| `payTestData.hasTelegram` | Phase 3 Telegram setup | boolean |
| `payTestData.containerName` | From /birth/start server response | Set in Phase 1 after Q4 |
| `payTestData.birthAuthenticated` | After /birth/code | true if OAuth completed |
| `payTestData.timestamps.birthStarted` | Phase 1 | ISO string |
| `payTestData.timestamps.birthAuthenticated` | Phase 1 | ISO string |
| `payTestData.prePurchaseSessionId` | Pre-purchase chat session | May be null |
| `payTestData.prePurchaseHistory` | Pre-purchase chat session | May be empty array |

### Fields NOT yet populated at flow:complete

| Field | When Populated | Notes |
|---|---|---|
| `payTestData.learnMoreAnswers` | Phase 6 (AFTER flow:complete) | Empty array `[]` at flow:complete — learn-more hasn't run yet |
| `payTestData.telegramBotToken` | Phase 3 | Present but STRIPPED by logPayTestData (sensitive) |
| `payTestData.timestamps.learnMoreComplete` | Phase 6 | null at flow:complete |

### Critical finding: learnMoreAnswers timing

The call order in the main flow is:
```
initPayTestFlow()
  → runQuestionnaire()         [Phase 1: name, email, company, role, birth init, primary goal]
  → runBehindTheCurtain()      [Phase 2: slides]
  → runTelegramSetup()         [Phase 3: telegram bot token]
  → runCompletion()            [Phase 4: *** flow:complete fires here ***]
      → user clicks button
      → runThankYouMessage()   [Phase 5: thank-you card]
          → user clicks "Learn more"
          → runLearnMoreLoop() [Phase 6: 5 optional questions → learnMoreAnswers populated]
```

`/birth/seed` at `flow:complete` means `learnMoreAnswers` will always be empty. If Witness needs the learn-more answers, the call should move to AFTER `runLearnMoreLoop()` completes (at `learn-more:complete`).

**Recommendation**: Call `/birth/seed` at `learn-more:complete` (line 10124-10125), not at `flow:complete`. All data including learnMoreAnswers will be available then.

If it must fire at `flow:complete` (before learn-more), that is still valid — it just won't include learnMoreAnswers. A second call or update at learn-more:complete could supplement.

---

## 2. Conversation History Construction

The current `logPayTestData()` already builds a `conversationHistory` array for the `/api/log-conversation` endpoint. The same logic should be used for `/birth/seed`. The array structure:

```javascript
// Pre-purchase chat (from before payment)
const preMsgs = payTestData.prePurchaseHistory ||
                window._pbPrePurchaseSession?.conversationHistory ||
                [];

// Onboarding Q&A (reconstructed from payTestData fields)
const onboardingMsgs = [];
if (payTestData.name)        { onboardingMsgs.push({role:'assistant',content:'What is your name?'});
                               onboardingMsgs.push({role:'user',content:payTestData.name}); }
if (payTestData.email)       { onboardingMsgs.push({role:'assistant',content:'What email should we use to reach you?'});
                               onboardingMsgs.push({role:'user',content:payTestData.email}); }
if (payTestData.company)     { onboardingMsgs.push({role:'assistant',content:'Are you working within a company or organization?'});
                               onboardingMsgs.push({role:'user',content:payTestData.company}); }
if (payTestData.role)        { onboardingMsgs.push({role:'assistant',content:'What is your role or title?'});
                               onboardingMsgs.push({role:'user',content:payTestData.role}); }
if (payTestData.primaryGoal) { onboardingMsgs.push({role:'assistant',content:'If your AI could do one thing exceptionally well for you, what would it be?'});
                               onboardingMsgs.push({role:'user',content:payTestData.primaryGoal}); }

// Learn-more answers (if calling from learn-more:complete)
if (payTestData.learnMoreAnswers && payTestData.learnMoreAnswers.length > 0) {
  for (const lm of payTestData.learnMoreAnswers) {
    onboardingMsgs.push({role:'assistant', content: `[Learn more: ${lm.question}]`});
    onboardingMsgs.push({role:'user', content: lm.answer});
  }
}

const conversationHistory = [...preMsgs, ...onboardingMsgs];
```

The format `{role: 'assistant'|'user', content: string}` matches the existing `/api/log-conversation` pattern.

---

## 3. Exact Insertion Point in the JS

### Option A: At flow:complete (no learnMoreAnswers)

Insert immediately after line 9916 in `runCompletion()`:

```javascript
payTestData.timestamps.flowComplete = new Date().toISOString();
await logPayTestData({ ...payTestData, event: 'flow:complete' });

// ── NEW: POST seed data to Witness /birth/seed ──────────────────────────────
// Only call if birth authenticated successfully and container name is known.
if (payTestData.containerName && payTestData.birthAuthenticated) {
  await callBirthSeed('flow:complete');
}
// ────────────────────────────────────────────────────────────────────────────

// Welcome button — v3: NO redirect; click triggers in-chat thank-you
const welcomeBtn = document.createElement('button');
```

### Option B: At learn-more:complete (RECOMMENDED — includes all data)

Insert after line 10125 in `runLearnMoreLoop()`:

```javascript
payTestData.timestamps.learnMoreComplete = new Date().toISOString();
await logPayTestData({ ...payTestData, event: 'learn-more:complete' });

// ── NEW: POST seed data to Witness /birth/seed ──────────────────────────────
// Fires here (after learn-more) so learnMoreAnswers are included.
if (payTestData.containerName && payTestData.birthAuthenticated) {
  await callBirthSeed('learn-more:complete');
}
// ────────────────────────────────────────────────────────────────────────────
```

---

## 4. Draft JavaScript: callBirthSeed()

This function should be added alongside the existing birth-related functions (near line 10147, after the `WITNESS_WEBHOOK_HOST` constant).

```javascript
// ---------------------------------------------------------------------------
// /birth/seed — send full conversation + seed data to Witness
// Called after learn-more completes (or at flow:complete if learn-more skipped)
// ---------------------------------------------------------------------------

async function callBirthSeed(triggerEvent) {
  if (!payTestData.containerName) {
    console.warn('[ptc-v4] callBirthSeed: no containerName, skipping');
    return;
  }

  // Build conversation history — same logic as logPayTestData()
  const preMsgs = (payTestData.prePurchaseHistory && payTestData.prePurchaseHistory.length)
    ? payTestData.prePurchaseHistory
    : ((window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory)
        ? window._pbPrePurchaseSession.conversationHistory
        : []);

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
    onboardingMsgs.push({ role: 'assistant', content: 'If your AI could do one thing exceptionally well for you, what would it be?' });
    onboardingMsgs.push({ role: 'user', content: payTestData.primaryGoal });
  }

  // Include learn-more answers if available
  if (payTestData.learnMoreAnswers && payTestData.learnMoreAnswers.length > 0) {
    for (const lm of payTestData.learnMoreAnswers) {
      onboardingMsgs.push({ role: 'assistant', content: `[Learn more: ${lm.question}]` });
      onboardingMsgs.push({ role: 'user', content: lm.answer });
    }
  }

  const conversationHistory = [...preMsgs, ...onboardingMsgs];

  // Build seed payload — matches proposed /birth/seed spec
  const seedPayload = {
    container:        payTestData.containerName,
    name:             payTestData.name             || null,
    email:            payTestData.email            || null,
    company:          payTestData.company          || null,
    role:             payTestData.role             || null,
    primaryGoal:      payTestData.primaryGoal      || null,
    aiName:           payTestData.aiName           || null,
    tier:             payTestData.tier             || null,   // same as tierPaid — stored as payTestData.tier
    orderId:          payTestData.orderId          || null,
    conversationHistory: conversationHistory.length ? conversationHistory : [
      { role: 'user', content: '[Post-payment onboarding - no chat history captured]' }
    ],
    // Supplemental metadata (Witness can ignore if not needed)
    triggerEvent:     triggerEvent,
    timestamps:       payTestData.timestamps,
  };

  console.log('[ptc-v4] callBirthSeed: posting seed to Witness', {
    container: seedPayload.container,
    msgCount: conversationHistory.length,
    trigger: triggerEvent,
  });

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

    const resp = await fetch(`${WITNESS_WEBHOOK_HOST}/api/birth/seed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(seedPayload),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!resp.ok) {
      const errBody = await resp.json().catch(() => ({}));
      console.error('[ptc-v4] /birth/seed failed:', resp.status, errBody);
      // Non-fatal — log but don't throw. Portal polling continues regardless.
      await logPayTestData({ ...payTestData, event: 'birth:seed:failed', error: errBody.error || `HTTP ${resp.status}` });
      return;
    }

    const seedResp = await resp.json();
    console.log('[ptc-v4] /birth/seed success:', seedResp);
    await logPayTestData({ ...payTestData, event: 'birth:seed:sent', msgCount: conversationHistory.length });

  } catch (err) {
    // Non-fatal — timeout or network error. Log and continue.
    console.error('[ptc-v4] /birth/seed error:', err.message);
    await logPayTestData({ ...payTestData, event: 'birth:seed:error', error: err.message });
  }
}
```

### Key design decisions in this draft

1. **Non-fatal errors**: `/birth/seed` failures are logged but do NOT throw. The portal polling continues regardless. Witness receiving seed is a "best effort" — the container is already allocated from `/birth/start`.

2. **Uses `WITNESS_WEBHOOK_HOST`**: Already defined as `'https://89.167.19.20:8443'` — same constant used by `/birth/start` and `/birth/code`. No new host needed.

3. **`tier` vs `tierPaid`**: The spec says `tier: payTestData.tierPaid` but `tierPaid` is NOT a field on the `payTestData` object. The function receives `tierPaid` as a local parameter in `initPayTestFlow()`, but stores it as `payTestData.tier`. Use `payTestData.tier` in the seed payload.

4. **30s timeout**: Reasonable for a seed delivery. Not as long as `/birth/start` (45s) since Witness shouldn't need to do heavy work on receipt.

5. **Sanitization**: `aiName` is already sanitized via `sanitizeText()` at entry. Other fields are plain strings from user input — Witness should sanitize on its end. The existing `logPayTestData` approach does not re-sanitize before logging, so staying consistent here.

---

## 5. Draft Python Proxy Endpoint for purebrain_log_server.py

This follows the exact pattern used by `proxy_birth_start()` and `proxy_birth_code()`.

Add after the existing `proxy_birth_code()` function (around line 1698 in the server file) and update the docstring at the top.

### Constants to add (near line 122)

```python
WITNESS_SEED_TIMEOUT = 30       # /birth/seed: 30s — delivering conversation history
BIRTH_SEED_RATE_MAX = 10        # /seed: 10 calls/min per IP (one per customer per session)
```

### Route to add

```python
@app.route('/api/proxy/birth/seed', methods=['POST', 'OPTIONS'])
@app.route('/api/birth/seed', methods=['POST', 'OPTIONS'])
def proxy_birth_seed():
    """
    Proxy POST /api/birth/seed to Witness.

    Receives the full conversation history + seed data from the chatbox
    after the customer completes the onboarding flow. Forwards to Witness
    so it can configure the customer's container with their context.

    Expected request body:
    {
        "container": "aiciv-XX",
        "name": "...",
        "email": "...",
        "company": "...",          # optional
        "role": "...",             # optional
        "primaryGoal": "...",
        "aiName": "...",
        "tier": "awakened|bonded|partnered|unified",
        "orderId": "...",          # optional
        "conversationHistory": [   # array of {role, content} messages
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."},
            ...
        ],
        "triggerEvent": "learn-more:complete",  # optional metadata
        "timestamps": {...}                      # optional metadata
    }

    Expected Witness response:
    {
        "status": "seeded",
        "container": "aiciv-XX"
    }
    """
    if request.method == 'OPTIONS':
        return '', 204

    client_ip = _get_real_client_ip()

    # SEC-004: Reject oversized bodies
    # Conversation history can be large — allow up to 512KB
    if request.content_length and request.content_length > 524288:
        return jsonify({'error': 'Request body too large'}), 413

    # Rate limiting — one seed per session is expected; 10/min is generous
    if not _check_birth_rate_limit(client_ip, 'seed', BIRTH_SEED_RATE_MAX):
        logger.warning(
            f'proxy/birth/seed rate-limited: ip={client_ip}'
        )
        return jsonify({
            'error': 'Too many requests',
            'details': f'Maximum {BIRTH_SEED_RATE_MAX} seed calls per minute',
        }), 429

    raw = request.get_data()
    if not raw or not raw.strip():
        return jsonify({'error': 'Missing request body'}), 400

    try:
        body = json.loads(raw)
    except Exception:
        return jsonify({'error': 'Invalid JSON body'}), 400

    # Validate required fields
    container = body.get('container', '')
    if not container or not _CONTAINER_NAME_RE.match(container):
        logger.warning(
            f'proxy/birth/seed: invalid container name '
            f'"{str(container)[:60]}" from ip={client_ip}'
        )
        return jsonify({'error': 'Invalid or missing container name'}), 400

    # Log locally for our records before forwarding
    logger.info(
        f'proxy/birth/seed: forwarding container={container} '
        f'msg_count={len(body.get("conversationHistory", []))} '
        f'(ip={client_ip})'
    )

    resp_data, status_code = _proxy_to_witness(
        method='POST',
        path='/api/birth/seed',
        body=raw,
        timeout=WITNESS_SEED_TIMEOUT,
    )

    return jsonify(resp_data), status_code
```

### Docstring line to add at top of file (in the existing list)

```
- POST /api/proxy/birth/seed - Proxy to Witness birth seed endpoint (delivers conversation history)
- POST /api/birth/seed - Alias for /api/proxy/birth/seed
```

---

## 6. Data Availability Summary

| Data point | Available at flow:complete | Available at learn-more:complete | Notes |
|---|---|---|---|
| `container` | YES | YES | From /birth/start server response |
| `name` | YES | YES | Q1 |
| `email` | YES | YES | Q2 |
| `company` | YES (may be null) | YES (may be null) | Q3, optional |
| `role` | YES (may be null) | YES (may be null) | Q4, optional |
| `primaryGoal` | YES | YES | Q5 |
| `aiName` | YES | YES | From initPayTestFlow() |
| `tier` | YES | YES | From initPayTestFlow() as `tierPaid`, stored as `payTestData.tier` |
| `orderId` | YES (may be null) | YES (may be null) | From initPayTestFlow() |
| `conversationHistory` (pre-purchase) | YES | YES | From window._pbPrePurchaseSession |
| `conversationHistory` (onboarding Q&A) | YES | YES | Reconstructed from payTestData fields |
| `learnMoreAnswers` | NO — empty array | YES | Phase 6 runs AFTER flow:complete |
| `hasTelegram` | YES | YES | Phase 3 result |
| `telegramBotToken` | YES (sensitive — STRIP) | YES (sensitive — STRIP) | Never send to Witness |

---

## 7. Sandbox vs Production Differences

Both page 688 (sandbox) and page 689 (production) use `WITNESS_WEBHOOK_HOST = 'https://89.167.19.20:8443'` as of v4.5+. The code is functionally identical. The `/birth/seed` call should work the same on both pages.

The proxy server (`purebrain_log_server.py`) handles both pages — the single `/api/birth/seed` endpoint on the proxy server will serve both.

---

## 8. Open Questions for Witness

Before implementing, confirm with Witness:

1. **When should /birth/seed fire?** At `flow:complete` (no learn-more answers) or at `learn-more:complete` (full data including learn-more answers)?

2. **What is the expected Witness response format?** The draft assumes `{"status": "seeded", "container": "aiciv-XX"}` but this needs to be confirmed.

3. **Is /birth/seed idempotent?** If the chatbox retries on network error, will a second POST with the same container cause problems?

4. **Does Witness need `learnMoreAnswers` as a separate structured field**, or is embedding them as messages in `conversationHistory` sufficient?

5. **What is the expected timeout?** Draft uses 30s — is this enough for Witness to process the conversation history?

---

## Memory Written

Path: `.claude/memory/agent-learnings/full-stack-developer/2026-02-27--birth-seed-chatbox-wiring-analysis.md`
Type: teaching
Topic: /birth/seed endpoint wiring analysis — chatbox data flow, timing, and proxy pattern

Key learnings captured:
- `learnMoreAnswers` is empty at `flow:complete` — seed call should be at `learn-more:complete` if those answers are needed
- `tierPaid` is NOT a payTestData field — it is stored as `payTestData.tier`
- Both pages 688 and 689 use the same WITNESS_WEBHOOK_HOST (89.167.19.20:8443)
- The proxy pattern in purebrain_log_server.py is well-established — new birth endpoints follow exactly the same structure using `_proxy_to_witness()` and `_check_birth_rate_limit()`
- conversationHistory already being built for /api/log-conversation — reuse same logic for /birth/seed
- Body size limit should be 512KB (not 65536) to accommodate large conversation histories
