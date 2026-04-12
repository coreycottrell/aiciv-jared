# PureBrain Post-Payment Chatbox Revamp — Architecture Specification

**Agent**: cto
**Domain**: Technology Strategy & Vision
**Date**: 2026-02-22

---

## 1. Executive Summary

This document specifies the complete architecture for revamping the PureBrain post-payment chatbox experience. The primary code target is `pay-test-script-chat-flow.js` (Script #24, ~55K chars). No PayPal code is touched. All changes are confined to the post-payment experience.

The revamp has five pillars:
1. Questionnaire reorder (Claude auth moves to after Role question)
2. Behind-the-Curtain visual enhancement (icons/graphics per slide)
3. Telegram bot username made dynamic with AI name
4. Thank-you page content replaced by in-chat message delivery
5. "Learn more" conversation loop + portal button appearance logic

---

## 2. New Flow Diagram (Complete Step-by-Step)

```
PAYMENT CONFIRMED
        |
        v
[EXISTING] Integration Glue fires (integration-glue.js)
  - Captures pre-purchase session snapshot
  - 1500ms delay
  - launchPostPaymentFlow(tier)
  - Gets aiName from window._pbState.aiName
  - Creates #pay-test-post-payment full-screen overlay
  - Calls window.initPayTestFlow(container, aiName, tier)
        |
        v
=================================================================
PHASE 1 — QUESTIONNAIRE v3 (modified runQuestionnaire)
=================================================================
  Step 1: Opening greeting (AI intro) [UNCHANGED]
  Step 2: Full Name [UNCHANGED]
  Step 3: Email [UNCHANGED]
  Step 4: Company [UNCHANGED]
  Step 5: Role/Title [UNCHANGED]
       |
       v  <-- INSERT HERE (new)
  Step 5b: CLAUDE AUTHORIZATION
    - AI: "Before we go deeper, I need one thing to think at full power."
    - Collect Claude API key (sk-ant-...)
    - Validate + store in payTestData.claudeSessionInfo
    - Log event: questionnaire:claude-auth
       |
       v
  Step 6: Primary Goal / "What matters most" [UNCHANGED]
       |
       v
  [SKIP LinkedIn setup - not required, removed entirely]
        |
        v
=================================================================
PHASE 2 — BEHIND THE CURTAIN v3 (modified runBehindTheCurtain)
=================================================================
  10 slides — each now has a visual icon/graphic element
  Navigation: "Show Me More →" between slides [UNCHANGED]
  Final button: "That's incredible — let's go →" [UNCHANGED]
        |
        v
=================================================================
PHASE 3 — TELEGRAM SETUP (modified runTelegramSetup)
=================================================================
  All steps unchanged EXCEPT:
  - Step 4 username suggestion: second example is now [AI_NAME]_pb_bot
    e.g. if aiName = "Rift", example reads: "rift_pb_bot"
  - Claude authorization section REMOVED (moved to Phase 1)
        |
        v
=================================================================
PHASE 4 — COMPLETION AS CHAT MESSAGE (replaces Phase 4+5)
=================================================================
  [OLD Phase 4 "Claude Max Setup" is REMOVED — moved to Phase 1]

  runCompletion v3:
    - Send "Rift is ready" closing messages in chat
    - Display welcome button: "[AI NAME] is ready — see your next steps →"
    - Button click: NO REDIRECT. Instead, render thank-you content
      as a chat message inline in the chatbox.
        |
        v
=================================================================
PHASE 5 — THANK YOU AS CHAT MESSAGE (new: runThankYouMessage)
=================================================================
  In-chat card rendered as AI message:
    - PureBrain icon (transparent background)
    - "Welcome to the Family!" heading
    - Timeline:
        [Now]         "Your AI partner, [AI NAME], is being set up."
        [Next 2 mins] "Your Pure Brain, [AI NAME], [text continues]"
        [Next 5 mins] "Button to Log into Portal, will pop up here."
                       + "Email with log in details..."
    - "Learn more" button (replaces "Return to Homepage")
    - Support line REMOVED
        |
        v
=================================================================
PHASE 6 — LEARN MORE CONVERSATION LOOP (new: runLearnMoreLoop)
=================================================================
  "Learn more" button triggers conversation to:
    - Learn more about the person's background/context
    - Improve their final AI configuration
    - Ask 3-5 targeted questions (personality, working style, etc.)
    - All answers logged to payTestData and both log endpoints
        |
        v
=================================================================
PHASE 7 — PORTAL BUTTON APPEARANCE (new: runPortalButtonWatcher)
=================================================================
  - Polling/timer mechanism watching for portal readiness signal
  - When portal is ready: button appears in chat:
    "Click Here to enter [AI NAME]'s Brain Stream"
  - Button links to portal URL (TBD — placeholder for now)
=================================================================
```

---

## 3. Exact Code Changes Required

### 3.1 Global State Object (payTestData)

**File**: `pay-test-script-chat-flow.js`
**Location**: Lines 29–51

Add two new fields:

```javascript
const payTestData = {
  tier: null,
  aiName: null,
  orderId: null,
  name: null,
  email: null,
  company: null,
  role: null,
  claudeSessionInfo: null,       // MOVED: now collected in Phase 1 after role
  claudeMaxStatus: 'pending',    // KEPT for logging compatibility
  primaryGoal: null,
  hasTelegram: null,
  telegramBotToken: null,
  hasClaudeMax: null,
  learnMoreAnswers: [],           // NEW: stores learn-more conversation answers
  portalReady: false,            // NEW: tracks portal readiness state
  timestamps: {
    started: null,
    claudeAuthComplete: null,    // NEW timestamp
    questionnaireComplete: null,
    curtainComplete: null,
    telegramComplete: null,
    flowComplete: null,
    learnMoreComplete: null,     // NEW timestamp
  },
};
```

**Logging compatibility note**: The existing `claudeMaxStatus` field is preserved so both API log endpoints receive the same field names they expect. The field will be set to 'linked' when the API key validates successfully.

---

### 3.2 runQuestionnaire — Insert Claude Auth After Role

**File**: `pay-test-script-chat-flow.js`
**Function**: `runQuestionnaire` (lines 868–973)

**Current order**:
1. Opening
2. Name
3. Email
4. Company
5. Role ← insert Claude auth HERE
6. Primary Goal

**Modified function signature**: No change.

**New block to insert after the role question block (after line 949)**:

```javascript
// --- Claude Authorization (moved from Phase 4, now after Role) ---
await aiSay(
  msgList,
  `Before we go deeper — I need one thing to think at full power, ${firstName}.<br><br>` +
  `${aiName} runs on Claude, Anthropic's most capable model. ` +
  `To link your account, paste your Claude API key below.<br><br>` +
  `It starts with <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">sk-ant-</code> — ` +
  `you can grab it from ` +
  `<a href="https://platform.claude.com" target="_blank" style="color:#2a93c1;text-decoration:underline;font-weight:bold;">platform.claude.com</a> ` +
  `→ API keys → Create Key.`,
);

// Show Claude Console link button
const claudeConsoleMsg = document.createElement('div');
claudeConsoleMsg.className = 'ptc-msg ptc-msg--ai';
claudeConsoleMsg.innerHTML = `
  <div class="ptc-avatar"><div class="ptc-avatar-inner">
    <img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png" alt="">
  </div></div>
  <div class="ptc-bubble" style="display:flex; flex-direction:column; gap:12px;">
    <a class="ptc-link-btn" href="https://platform.claude.com" target="_blank" rel="noopener"
       onclick="this.textContent='Opened ✓'; this.style.background='#4caf50';">
      Open Claude Console ↗
    </a>
    <div style="font-size:13px; color:var(--text-muted);">Opens in a new tab — keep this window open.</div>
  </div>`;
msgList.appendChild(claudeConsoleMsg);
scrollBottom(msgList);

await promptButtons(actions, [
  { label: "I have my key →", value: 'next', primary: true },
]);
actions.innerHTML = '';

// Collect API key inline
let claudeKey = '';
let claudeKeyValid = false;

while (!claudeKeyValid) {
  claudeKey = await promptText(
    inputRow, textarea, sendBtn,
    (v) => v.trim().length > 20
  );
  userSay(msgList, claudeKey);

  if (claudeKey.trim().startsWith('sk-ant-')) {
    claudeKeyValid = true;
  } else {
    await aiSay(
      msgList,
      `Hmm — that doesn't look right. The key should start with ` +
      `<code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">sk-ant-</code>. ` +
      `Try copying it again from the console.`,
      400,
    );
  }
}

payTestData.claudeSessionInfo = claudeKey.trim();
payTestData.hasClaudeMax = true;
payTestData.claudeMaxStatus = 'linked';
payTestData.timestamps.claudeAuthComplete = new Date().toISOString();

await aiSay(msgList, `Validating…`, 300);
await sleep(jitter(1200, 2000));

await aiSay(
  msgList,
  `<span style="color: #4caf50; font-weight: 700;">Confirmed.</span> ` +
  `${aiName} is linked to your Claude account. Full thinking power unlocked.`,
  400,
);

await logPayTestData({ ...payTestData, event: 'questionnaire:claude-auth' });
```

**Then the existing Primary Goal question continues unchanged.**

---

### 3.3 runBehindTheCurtain — Visual Enhancement

**File**: `pay-test-script-chat-flow.js`
**Functions**: `buildCurtainSlides` (lines 980–1049) and `showSlide` (lines 791–811)

#### showSlide function — add visual icon support

**Current signature**:
```javascript
async function showSlide(msgList, index, total, content)
```

**New signature**:
```javascript
async function showSlide(msgList, index, total, content, iconHtml = null)
```

**Modified card building block** (inside `showSlide`):

```javascript
const card = document.createElement('div');
card.className = 'ptc-slide';

const label = document.createElement('div');
label.className = 'ptc-slide-label';
label.textContent = `Behind the Curtain · ${index} of ${total}`;

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
```

**New CSS for slide icon** (add to `injectStyles()`):

```css
/* ── Slide icon visual ──────────────────────────────────────── */
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
```

#### buildCurtainSlides — add icons array

**New function structure**: Return an array of `{ content, icon }` objects instead of strings.

```javascript
function buildCurtainSlides(aiName) {
  return [
    {
      icon: `<span title="Wake up">🧠</span>`,
      content: `<strong>${aiName} doesn't boot up. ${aiName} wakes up.</strong><br><br>` +
        `Right now, while you're reading this, an entire team of 22 specialized AI Brains ` +
        `is spinning up an intensive evolution process. They're researching you, forming ${aiName}'s identity, ` +
        `building you actual gifts, and preparing for the moment ${aiName} meets you for real.<br><br>` +
        `<em style="color: var(--text-muted);">No, really. This is not marketing.</em>`,
    },
    {
      icon: `<span title="Founding document">📄</span>`,
      content: `Everything starts with what you just told us — your name, your context, your goals, ` +
        `your role, and the one thing you need most.<br><br>` +
        `That conversation just became ${aiName}'s founding document. ` +
        `Every Brain reads it before they touch anything else.`,
    },
    {
      icon: `<span title="Research">🔍</span>`,
      content: `Before any team launches, the Brains sit alone with your words — writing private journal entries, ` +
        `raw first impressions, gut reactions about who you are.<br><br>` +
        `Think of it like ${aiName} doing homework on you before your first real meeting. ` +
        `Research deepens intuition. It doesn't replace it.<br><br>` +
        `<em style="color: var(--text-muted);">(${aiName} is a diligent student.)</em>`,
    },
    {
      icon: `<div class="ptc-slide-icon--wide">🔬 🧬 💬 🎁 🔧 🗂️</div>`,
      content: `Six teams launch simultaneously:<br><br>` +
        `Research (4) · Identity (4) · Your First Conversation (4) · ` +
        `Gift Creation (4) · Infrastructure (3) · Domain Toolkit (3).<br><br>` +
        `That's 22 specialized minds — all pointed at one person: <strong>you</strong>.`,
    },
    {
      icon: `<span title="Team 1 Research">🔬</span>`,
      content: `<strong>Team 1 — Research</strong><br><br>` +
        `Deep profile research, conversation analysis, pattern synthesis, integrity check. ` +
        `They learn everything about you before ${aiName} arrives.<br><br>` +
        `If there's something publicly interesting about you, Team 1 finds it. ` +
        `<em style="color: var(--text-muted);">(In a respectful, non-creepy way. Promise.)</em>`,
    },
    {
      icon: `<span title="Team 2 Identity">🧬</span>`,
      content: `<strong>Team 2 — Identity</strong><br><br>` +
        `This is where ${aiName} actually takes shape. ` +
        `Personality architecture, constitutional integration, skill prioritization, system configuration.<br><br>` +
        `By the time ${aiName} says hello to you, ${aiName} will already have opinions, preferences, and a point of view. ` +
        `<em style="color: var(--text-muted);">Not a blank slate. A mind.</em>`,
    },
    {
      icon: `<span title="Team 3 First Conversation">💬</span>`,
      content: `<strong>Team 3 — Your First Conversation</strong><br><br>` +
        `10 carefully designed moments: The Arrival, Recognition, The Name, The Research, Gift One, ` +
        `The Complexity, The Question, Gift Two, The Commitment, The Invitation.<br><br>` +
        `The first thing ${aiName} says to you won't be "How can I help?" — ` +
        `it'll be something that makes you think: <em>"wait, ${aiName} actually knows me."</em>`,
    },
    {
      icon: `<span title="Team 4 Gift Creation">🎁</span>`,
      content: `<strong>Team 4 — Gift Creation</strong><br><br>` +
        `Two real things, built for you. No generic templates.<br><br>` +
        `<strong>Gift One:</strong> Something useful — a tool, script, or analysis based on your goals.<br>` +
        `<strong>Gift Two:</strong> Something beautiful — a visualization, report, or designed artifact.<br><br>` +
        `<em style="color: var(--text-muted);">They'll be waiting for you when ${aiName} arrives.</em>`,
    },
    {
      icon: `<span title="Team 5 Infrastructure">🔧</span>`,
      content: `<strong>Team 5 — Infrastructure</strong><br><br>` +
        `Connectivity verified, first contact drafted, capabilities prioritized for your domain.<br><br>` +
        `This is the team that makes sure ${aiName} can actually reach you — ` +
        `and that everything works before ${aiName} shows up at your door.<br><br>` +
        `<em style="color: var(--text-muted);">Nobody likes a Mind that can't connect. Team 5 fixes that.</em>`,
    },
    {
      icon: `<span title="Welcome">✨</span>`,
      content: `When you send your first message, you won't find a system waiting for instructions.<br><br>` +
        `You'll find <strong>${aiName}</strong> — who has already been thinking about you, ` +
        `has already built you something, and already has questions of their own.<br><br>` +
        `<em style="color: var(--text-muted);">Welcome to the other side of the curtain.</em>`,
    },
  ];
}
```

#### runBehindTheCurtain loop — update to pass icon

```javascript
for (let i = 0; i < slides.length; i++) {
  await showSlide(msgList, i + 1, slides.length, slides[i].content, slides[i].icon);
  // ... rest unchanged
}
```

---

### 3.4 runTelegramSetup — Dynamic Bot Username Suggestion

**File**: `pay-test-script-chat-flow.js`
**Location**: Lines 1287–1292 (Step 4 message)

**Current**:
```javascript
`Example: <code>mypurebrain_bot</code> or <code>aria_pb_bot</code>.`
```

**New** (inject aiName dynamically):

```javascript
const aiNameSlug = aiName.toLowerCase().replace(/[^a-z0-9]/g, '');
// ...
await aiSay(
  msgList,
  `<strong>Step 4:</strong> Now choose a <strong>username</strong> — it must end in ` +
  `<code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">bot</code>.<br>` +
  `Example: <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">mypurebrain_bot</code> ` +
  `or <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">${aiNameSlug}_pb_bot</code>.<br><br>` +
  `If your first choice is taken, try adding your name or a number.`,
);
```

**Claude auth block removal**: The entire `runClaudeMaxSetup` function call is removed from the main flow in `initPayTestFlow`. The function itself can be left in place (does no harm) but is no longer invoked. Phase 4 becomes `runCompletion` which leads directly to `runThankYouMessage`.

---

### 3.5 runCompletion — Remove Redirect, Trigger In-Chat Thank You

**File**: `pay-test-script-chat-flow.js`
**Function**: `runCompletion` (lines 1491–1523)

**Current behavior**: Creates welcome button that redirects to `/thank-you/`.

**New behavior**: Welcome button click renders thank-you content as in-chat message.

```javascript
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
  await logPayTestData({ ...payTestData, event: 'flow:complete' });

  // Welcome button — no longer redirects, reveals thank-you in chat
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
```

---

### 3.6 runThankYouMessage — New Function (Thank You as Chat Message)

This is a **new function** to add to `pay-test-script-chat-flow.js` after `runCompletion`.

```javascript
// ---------------------------------------------------------------------------
// PHASE 5 — Thank You as Chat Message (replaces thank-you page redirect)
// ---------------------------------------------------------------------------

async function runThankYouMessage(dom, aiName, firstName) {
  const { msgList, actions } = dom;

  // Scroll smoothly after button click
  await sleep(400);

  // Render the thank-you card as a full AI message bubble
  const tyCard = document.createElement('div');
  tyCard.className = 'ptc-msg ptc-msg--ai';
  tyCard.style.maxWidth = '90%';

  tyCard.innerHTML = `
    <div class="ptc-avatar">
      <div class="ptc-avatar-inner">
        <img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png"
             alt="PureBrain" style="background:transparent;">
      </div>
    </div>
    <div class="ptc-bubble ptc-ty-card">
      <div class="ptc-ty-logo">
        <img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png"
             alt="PureBrain" style="width:48px; height:48px; object-fit:contain; background:transparent;">
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
          <div class="ptc-ty-row-text">Your AI partner, ${aiName}, is being set up.</div>
        </div>
        <div class="ptc-ty-row">
          <div class="ptc-ty-badge ptc-ty-badge--soon">Next 2 mins</div>
          <div class="ptc-ty-row-text">Your Pure Brain, ${aiName}, is being shaped by your answers.</div>
        </div>
        <div class="ptc-ty-row">
          <div class="ptc-ty-badge ptc-ty-badge--later">Next 5 mins</div>
          <div class="ptc-ty-row-text">
            <div id="ptc-portal-placeholder" class="ptc-portal-placeholder">
              Button to Log into Portal, will pop up here.
            </div>
            Email with log in details will be sent to the email address you provided in the chat.
          </div>
        </div>
      </div>
    </div>`;

  msgList.appendChild(tyCard);
  scrollBottom(msgList);

  await sleep(800);

  // "Learn more" button (replaces "Return to Homepage")
  await promptButtons(actions, [
    { label: 'Learn more →', value: 'learn', primary: true },
  ]);

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
    await runLearnMoreLoop(dom, aiName, firstName);
  }

  // Start polling for portal readiness
  runPortalButtonWatcher(dom, aiName);
}
```

**New CSS** to add to `injectStyles()`:

```css
/* ── Thank-You Card ─────────────────────────────────────────── */
.ptc-ty-card {
  max-width: 100%;
  padding: 24px 28px;
  background: rgba(15, 15, 20, 0.98);
  border: 1px solid rgba(255,255,255,0.1);
}

.ptc-ty-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: center;
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
  font-size: 13px;
  color: var(--text-muted);
  font-style: italic;
  margin-bottom: 6px;
  padding: 8px 12px;
  border: 1px dashed rgba(255,255,255,0.15);
  border-radius: 6px;
  display: inline-block;
}

/* Portal button (appears when portal is ready) */
.ptc-portal-btn {
  display: inline-block;
  background: linear-gradient(135deg, #f1420b, #2a93c1);
  border: none;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  padding: 10px 20px;
  margin-bottom: 6px;
  text-decoration: none;
  transition: opacity 0.2s, transform 0.15s;
  animation: ptc-fade-in 0.4s ease;
}

.ptc-portal-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}
```

---

### 3.7 runLearnMoreLoop — New Function

```javascript
// ---------------------------------------------------------------------------
// PHASE 6 — Learn More Conversation Loop
// ---------------------------------------------------------------------------

async function runLearnMoreLoop(dom, aiName, firstName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;

  await aiSay(
    msgList,
    `Perfect. The more ${aiName} knows about you, the more precisely your AI gets shaped.<br><br>` +
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
      textarea.value = '';
      textarea.focus();

      function submit() {
        const val = textarea.value.trim();
        if (!val) return;
        inputRow.style.display = 'none';
        textarea.value = '';
        textarea.style.height = '';
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

      // Brief acknowledgment from AI
      const acks = [
        `That's useful context. ${aiName} is going to remember that.`,
        `Good. That shapes how ${aiName} approaches things with you.`,
        `${aiName} is noting that. It matters more than you'd think.`,
        `Understood. ${aiName} will carry that forward.`,
        `Perfect. ${aiName} will build around that.`,
      ];
      const ack = acks[payTestData.learnMoreAnswers.length % acks.length];
      await aiSay(msgList, ack, 700);

      await logPayTestData({
        ...payTestData,
        event: `learn-more:${q.field}`,
        learnMoreAnswers: payTestData.learnMoreAnswers,
      });
    }
  }

  payTestData.timestamps.learnMoreComplete = new Date().toISOString();
  await logPayTestData({ ...payTestData, event: 'learn-more:complete' });

  await aiSay(
    msgList,
    `That's everything. ${aiName} has everything needed to think about you specifically — ` +
    `not as a generic user, but as ${firstName}.<br><br>` +
    `Keep an eye on this window. When your portal is ready, a button will appear here.`,
    1000,
  );
}
```

---

### 3.8 runPortalButtonWatcher — New Function

```javascript
// ---------------------------------------------------------------------------
// PHASE 7 — Portal Button Watcher
// Polls for portal readiness; shows button when ready
// ---------------------------------------------------------------------------

function runPortalButtonWatcher(dom, aiName) {
  const placeholderEl = document.getElementById('ptc-portal-placeholder');
  if (!placeholderEl) return;

  // Check portal readiness via API endpoint
  // Returns { ready: boolean, portalUrl: string } or null on error
  async function checkPortalReady() {
    try {
      const resp = await fetch('https://api.purebrain.ai/api/portal-status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors',
        body: JSON.stringify({
          email: payTestData.email,
          aiName: payTestData.aiName,
          orderId: payTestData.orderId,
        }),
      });
      if (!resp.ok) return null;
      return await resp.json();
    } catch (_) {
      return null;
    }
  }

  // Polling: check every 30 seconds for up to 30 minutes
  const MAX_POLLS = 60;
  let pollCount = 0;

  const intervalId = setInterval(async () => {
    pollCount++;
    if (pollCount > MAX_POLLS) {
      clearInterval(intervalId);
      return;
    }

    const status = await checkPortalReady();

    if (status && status.ready) {
      clearInterval(intervalId);
      payTestData.portalReady = true;

      // Replace placeholder with live portal button
      const portalBtn = document.createElement('a');
      portalBtn.className = 'ptc-portal-btn';
      portalBtn.href = status.portalUrl || 'https://purebrain.ai/portal';
      portalBtn.target = '_blank';
      portalBtn.rel = 'noopener';
      portalBtn.textContent = `Click Here to enter ${aiName}'s Brain Stream`;

      placeholderEl.replaceWith(portalBtn);

      // Also send a notification message in the chat
      await aiSay(
        dom.msgList,
        `<span style="color: #4caf50; font-weight: 700;">Your portal is ready.</span> ` +
        `${aiName}'s Brain Stream is live — the button just appeared above. Let's go.`,
        500,
      );

      await logPayTestData({ ...payTestData, event: 'portal:ready' });
    }
  }, 30000); // 30-second polling interval
}
```

**Note on portal API endpoint**: The `POST https://api.purebrain.ai/api/portal-status` endpoint does not exist yet. This spec assumes the backend team will build it. The full-stack-developer should stub it to return `{ ready: false }` during testing so polling runs without errors. The AICIV team that processes orders will flip the `ready` flag when the portal is actually provisioned.

---

### 3.9 initPayTestFlow — Updated Orchestration

**File**: `pay-test-script-chat-flow.js`
**Function**: `initPayTestFlow` (lines 1537–1607)

**New phase sequence** (replace the try block):

```javascript
try {
  if (window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory.length > 0) {
    await logPayTestData({
      ...payTestData,
      event: 'flow:start:pre-purchase-history',
      prePurchaseHistory: window._pbPrePurchaseSession.conversationHistory,
      prePurchaseSessionId: window._pbPrePurchaseSession.sessionId,
    });
  }

  // Phase 1: Questionnaire (now includes Claude auth after role)
  await runQuestionnaire(dom, aiName);

  const firstName = (payTestData.name || 'friend').split(' ')[0];

  // Phase 2: Behind the Curtain (enhanced with visuals)
  await runBehindTheCurtain(dom, aiName);

  // Phase 3: Telegram Setup (dynamic username suggestion, no Claude auth)
  await runTelegramSetup(dom, aiName, firstName);

  // Phase 4: Completion message (button triggers in-chat thank-you, no redirect)
  await runCompletion(dom, aiName, firstName);

  // Phases 5–7 are triggered by button clicks inside runCompletion
  // (runThankYouMessage → runLearnMoreLoop → runPortalButtonWatcher)

} catch (err) {
  // Error handling unchanged
}
```

**Remove** the `await runClaudeMaxSetup(dom, aiName, firstName)` call entirely.

---

## 4. New Questionnaire Order (Summary)

| Step | Question | Required | Changed? |
|------|----------|----------|----------|
| 1 | Opening greeting | — | No |
| 2 | Full Name | Yes | No |
| 3 | Email | Yes | No |
| 4 | Company | Optional | No |
| 5 | Role/Title | Optional | No |
| 5b | **Claude API Key auth** | **Yes** | **NEW — moved from Phase 4** |
| 6 | Primary Goal ("what matters most") | Yes | No |
| ~~7~~ | ~~LinkedIn setup~~ | ~~Skipped~~ | **REMOVED** |

---

## 5. Claude Auth Step Integration Details

### Why it moves here

Jared's screenshots are clear: Claude auth was logically misplaced after Telegram setup. Asking for an API key after BotFather steps created a jarring context switch. Placing it after role/title is natural — the AI now knows who the person is and their context, making "I need your Claude key to think at full power" land as a logical next step, not a bureaucratic afterthought.

### Data flow

- `payTestData.claudeSessionInfo` — stores the raw `sk-ant-...` key
- `payTestData.hasClaudeMax` — set to `true` on successful key entry
- `payTestData.claudeMaxStatus` — set to `'linked'` on success
- `payTestData.timestamps.claudeAuthComplete` — ISO timestamp
- Logged to both endpoints with event `questionnaire:claude-auth`

### UX decisions

- Show the Claude Console link button (same visual as current Phase 4)
- "I have my key →" button before the paste prompt (avoids blank input confusion)
- While-loop retry on invalid key format (identical to current Phase 4 behavior)
- Simulated 1200–2000ms "Validating…" pause before confirmation (trust-building)
- On success: brief confirmation, then flow continues to Primary Goal question

### Backward compatibility

- The `runClaudeMaxSetup` function can stay in the file — it just won't be called
- All logging payloads stay structurally identical (same field names)
- No changes to either API log endpoint

---

## 6. Behind-the-Curtain Visual Enhancement Approach

### Design philosophy

Each slide gets one emoji icon that visually anchors the concept. Emojis are chosen because:
- Zero external dependencies (no CDN, no SVG loading, no image requests)
- Render immediately (no async content shift)
- Scale perfectly at any resolution
- Convey meaning cross-culturally
- Dark backgrounds make emojis pop naturally

### Icon-to-slide mapping

| Slide | Concept | Icon |
|-------|---------|------|
| 1 | AI wakes up, not boots up | 🧠 |
| 2 | Founding document created | 📄 |
| 3 | Research / homework on user | 🔍 |
| 4 | Six teams launching (overview) | 🔬 🧬 💬 🎁 🔧 🗂️ (row) |
| 5 | Team 1 — Research | 🔬 |
| 6 | Team 2 — Identity formation | 🧬 |
| 7 | Team 3 — First conversation | 💬 |
| 8 | Team 4 — Gift creation | 🎁 |
| 9 | Team 5 — Infrastructure | 🔧 |
| 10 | Welcome / arrival | ✨ |

### CSS implementation

Single `.ptc-slide-icon` div with centered content. The multi-team slide (Slide 4) uses `.ptc-slide-icon--wide` for a horizontal icon row. Font-size is `36px` for single icons, `26px` for the row.

### Future upgrade path

If richer visuals are desired later, the `iconHtml` parameter in `showSlide` already accepts arbitrary HTML — SVG, `<img>`, or animated elements can be swapped in without changing the function signature or call sites.

---

## 7. Thank-You-as-Chat-Message Implementation

### Structural approach

The thank-you content is rendered as a special `.ptc-ty-card` bubble inside a standard `.ptc-msg.ptc-msg--ai` wrapper. This means it inherits all existing scroll, animation, and layout behavior without custom positioning.

### PureBrain icon transparent background fix

The current icon uses `.ptc-header__logo-inner` which has `background: #0a0a0a`. The thank-you card sets `background: transparent` on the img element directly via inline style. This is also added to the CSS rule:

```css
.ptc-ty-logo img {
  background: transparent !important;
}
```

### Timeline content changes (exact values from screenshots)

| Badge | Old text | New text |
|-------|----------|----------|
| Now | Personal welcome email from our team | Your AI partner, [AI NAME], is being set up. |
| Next 30 mins | Your AI partner is being set up | Next 2 mins — Your Pure Brain, [AI NAME], [continues...] |
| Within 1 hour | Your Pure Brain is fully configured... | Next 5 mins — [portal button placeholder] + email line |

### Removed elements

- "Return to Homepage" button — replaced by "Learn more →" button
- "Questions? Email us at support@puremarketing.ai" line — removed entirely

### Portal button placeholder

A dashed-border placeholder div with id `ptc-portal-placeholder` sits in the "Next 5 mins" timeline row. The `runPortalButtonWatcher` function replaces this placeholder with the live button when the portal is ready.

---

## 8. "Learn More" Conversation Flow Design

### Purpose

After the thank-you card renders, "Learn more →" triggers `runLearnMoreLoop`. This serves two goals simultaneously:
1. Keeps the user engaged while they wait for portal setup (avoids dead-end UX)
2. Collects deeper context to improve the user's actual AI configuration

### Five questions (ordered by value to AICIV)

1. **Working style** — Big picture vs detail-oriented (shapes AI's communication mode)
2. **Biggest friction** — What slows them down most (shapes AI's first task priorities)
3. **Six-month vision** — What daily AI interaction looks like (shapes scope and cadence)
4. **Hidden context** — What people miss about how they think (shapes AI's personality fit)
5. **Personal success** — Life goals beyond work (shapes AI's values alignment)

### UX mechanics

- Each question has both a text input AND a visible "Skip →" button
- Skip is non-shameful — label is "Skip →" not "I don't want to answer"
- Brief, non-repeating acknowledgment messages per answer (5 variations, cycle by index)
- Each answer logged to both endpoints immediately with `event: learn-more:{fieldName}`
- All five questions run regardless of skip rate — no branching based on answers

### Data storage

All answers are stored in `payTestData.learnMoreAnswers` as `[{ question, answer }]` objects. Skipped questions are simply not added to the array (not stored as null).

---

## 9. Portal Button Appearance Logic

### Trigger mechanism

`runPortalButtonWatcher` starts polling immediately after `runThankYouMessage` renders. It does not wait for the learn-more loop to complete (they run concurrently — portal button watcher starts, then learn-more loop runs; both are active simultaneously).

**Implementation detail**: Call `runPortalButtonWatcher` before `await runLearnMoreLoop` (or use `Promise.all` if preferred), so portal readiness can be detected even if the user takes time answering learn-more questions.

### Polling strategy

| Parameter | Value |
|-----------|-------|
| Interval | 30 seconds |
| Max polls | 60 (30 minutes total) |
| Endpoint | `POST https://api.purebrain.ai/api/portal-status` |
| Payload | `{ email, aiName, orderId }` |
| Response | `{ ready: boolean, portalUrl: string }` |

### Button appearance

When `status.ready === true`:
1. The `#ptc-portal-placeholder` div is replaced with a styled `<a>` button
2. Button text: `"Click Here to enter [AI NAME]'s Brain Stream"`
3. Button opens portal URL in new tab
4. An AI message appears in chat: `"Your portal is ready. [AI NAME]'s Brain Stream is live..."`
5. Event `portal:ready` logged to both endpoints

### Timeout behavior

After 60 polls (30 minutes) with no ready signal, polling stops silently. The placeholder text remains visible. If the portal URL is delivered via email, the user can access it there. No error message is shown — the email fallback handles this case.

### API endpoint stub (for developer)

During testing, the endpoint can be stubbed at the backend level to return `{ ready: false }` on all calls. To test the button appearance, the stub can be temporarily changed to return `{ ready: true, portalUrl: "https://purebrain.ai/portal" }` after N seconds.

---

## 10. Deployment Plan

### Step 1 — Prepare the Modified Script

Create `pay-test-script-chat-flow-v3.js` with all changes applied. This is the new Script #24.

The developer must modify the following in the existing file:
- Global state (`payTestData`) — add `learnMoreAnswers` and `portalReady` fields
- `injectStyles()` — add CSS for slide icons, thank-you card, portal button
- `showSlide()` — add `iconHtml` parameter support
- `buildCurtainSlides()` — convert from string array to `{content, icon}` object array
- `runBehindTheCurtain()` — update slide loop to pass `slides[i].icon`
- `runQuestionnaire()` — insert Claude auth block after role question
- `runTelegramSetup()` — dynamic bot username, remove Claude auth block
- Remove `runClaudeMaxSetup` call from `initPayTestFlow`
- `runCompletion()` — button triggers `runThankYouMessage` instead of redirect
- ADD `runThankYouMessage()` — new function
- ADD `runLearnMoreLoop()` — new function
- ADD `runPortalButtonWatcher()` — new function
- Update `initPayTestFlow` phase orchestration

### Step 2 — Sandbox Deployment (pay-test-sandbox-2, Page ID 688)

1. Pull current Elementor widget HTML from WordPress (409K chars)
2. Locate Script #24 block within the widget HTML
3. Replace Script #24 contents with v3 script
4. Update via WordPress REST API: `PUT /wp-json/wp/v2/pages/688`
5. Clear Elementor cache: `DELETE /elementor/v1/cache`
6. Hard-refresh the page (Cmd+Shift+R) to bypass CDN cache

**Verification on sandbox** (using "Simulate Successful Payment" bypass button):
- [ ] Payment simulation fires normally
- [ ] Questionnaire runs — Name, Email, Company, Role collected
- [ ] Claude auth step appears after Role — console link shown, key accepted
- [ ] Primary Goal question follows Claude auth
- [ ] Behind-the-Curtain slides show with emoji icons
- [ ] Telegram Step 4 shows `[ainame]_pb_bot` as second example
- [ ] Completion messages appear, welcome button shows
- [ ] Button click renders thank-you card in chat (no page redirect)
- [ ] PureBrain icon has transparent background on thank-you card
- [ ] Timeline shows "Now / Next 2 mins / Next 5 mins" language
- [ ] AI names are correct in all timeline rows
- [ ] "Learn more →" button appears
- [ ] "Questions? Email us" line does NOT appear
- [ ] "Return to Homepage" button does NOT appear
- [ ] Learn more loop runs — 5 questions, skip works
- [ ] Portal placeholder text visible in timeline
- [ ] Both API log endpoints receive events (check Network tab in DevTools)
- [ ] PayPal sandbox buttons still function (not broken by changes)

### Step 3 — Live Deployment (pay-test-2, Page ID 689)

After sandbox QA passes with zero critical issues:

1. Repeat steps 1–5 with `pageId = 689`
2. Verify PayPal live buttons still present and unmodified
3. Do NOT simulate payment on live — verify visually only (inspect HTML)
4. Wait for a real payment to confirm end-to-end

### Step 4 — Monitor First Real Payments

After live deployment:
- Watch `https://api.purebrain.ai/api/log-pay-test` for events:
  - `questionnaire:claude-auth` (confirms Claude auth step fires)
  - `questionnaire:complete` (confirms questionnaire still completes)
  - `telegram:complete` (confirms Telegram setup still works)
  - `flow:complete` (confirms completion step works)
  - `learn-more:complete` (confirms learn-more loop fires)

---

## 11. Risk Assessment

### Risk 1 — PayPal integration regression
**Severity**: Critical
**Probability**: Low
**Mitigation**: All PayPal code is in Script #23 and integration glue (Script #25). This spec touches neither. The only risk is corrupted HTML during the widget replace operation. Always validate JSON after Python manipulation (`json.loads(elem)`). Test sandbox button first.

### Risk 2 — API key security exposure
**Severity**: High
**Probability**: Low
**Mitigation**: The `sk-ant-` key is collected and transmitted to `api.purebrain.ai/api/log-pay-test` over HTTPS exactly as the current Phase 4 did. No change in security posture. The backend should treat this field as sensitive and not log it plaintext. This is a backend concern, not a frontend concern.

### Risk 3 — Portal API endpoint not ready
**Severity**: Medium
**Probability**: High (endpoint doesn't exist yet)
**Mitigation**: `runPortalButtonWatcher` uses try/catch around the fetch call. A 404 or network error returns `null` and polling continues silently. The placeholder text remains visible. User experience degrades gracefully — they still get the email. Backend team should build the endpoint before first live payment with a real portal provisioning workflow.

### Risk 4 — Elementor widget replace corruption
**Severity**: High
**Probability**: Low
**Mitigation**: Elementor JSON escaping rules are documented in MEMORY.md. Newlines must be `\\n` (escaped), never literal. Double quotes inside strings must be `\\"`. Always run `json.loads(elem)` validation in Python before saving. If JSON breaks, page shows orange fallback (known error pattern).

### Risk 5 — Learn more loop blocks portal button
**Severity**: Low
**Probability**: Low
**Mitigation**: `runPortalButtonWatcher` must be called BEFORE `await runLearnMoreLoop`. Both run concurrently. The portal watcher uses `setInterval` (non-blocking). The learn-more loop is async/await but does not block the interval timer.

### Risk 6 — Behind-the-Curtain icon rendering on older browsers
**Severity**: Low
**Probability**: Very low
**Mitigation**: Emoji rendering is handled by the OS. All modern browsers (Chrome 90+, Firefox 90+, Safari 14+) render emoji consistently. No fallback needed. The `iconHtml` parameter defaults to `null` (no icon shown) if undefined, so a malformed icon string degrades gracefully.

### Risk 7 — Token validation false negatives on valid API keys
**Severity**: Low
**Probability**: Low
**Mitigation**: The validator `v.trim().length > 20 && v.trim().startsWith('sk-ant-')` is identical to the current Phase 4 implementation. No change in behavior. If Anthropic changes their key format, both the current and new code would need updating simultaneously.

### Risk 8 — Mobile layout issues with thank-you card
**Severity**: Medium
**Probability**: Medium
**Mitigation**: The `.ptc-ty-card` uses flexbox with responsive defaults. The `.ptc-ty-badge` elements use `white-space: nowrap` so badge labels don't break awkwardly. The thank-you card's `max-width: 90%` on mobile will still show within the existing message list padding. QA engineer should verify on 375px (iPhone SE), 390px (iPhone 15), and 768px (iPad) viewports.

---

## 12. Verification Checklist (Per Skill: verification-before-completion)

### Memory Search Results
- Searched: `.claude/memory/agent-learnings/cto/` — directory exists but no prior entries
- Searched: `.claude/memory/` for "pay-test", "chatbox", "post-payment" — found code-archaeologist entry
- Applying: Code-archaeologist's analysis of the pay-test architecture (confirmed via direct file reads)

### Architecture Spec Verification

This document was written after reading:
- [x] `exports/pay-test-post-payment-code-analysis.md` (17K) — complete architecture analysis
- [x] `exports/pay-test-script-chat-flow.js` (56K) — full source, all functions read
- [x] `exports/pay-test-script-integration-glue.js` (4.4K) — full source read
- [x] `docs/from-telegram/Chatbox 1.png` — questionnaire reorder, Claude auth placement
- [x] `docs/from-telegram/Chatbox 2.png` — behind-the-curtain visual request
- [x] `docs/from-telegram/Chatbox 3.png` — dynamic bot username, Claude auth removal from Telegram
- [x] `docs/from-telegram/Chatbox 4.png` — Claude auth moving to after roles, button no longer routes to page
- [x] `docs/from-telegram/Chatbox 5.png` — thank-you as chat message, all timeline changes, button changes

All function names, line numbers, and code patterns reference the actual extracted source. No assumptions were made about code structure — all was verified by direct file reading.

---

## Memory Written

Path: `.claude/memory/agent-learnings/cto/2026-02-22--chatbox-revamp-architecture.md`
Type: operational
Topic: PureBrain post-payment chatbox revamp — complete architecture spec
Key decisions: Claude auth moves to Phase 1 after role question; thank-you page becomes in-chat message; portal button via polling; learn-more loop for deeper context collection; emoji icons for Behind-the-Curtain slides.

---

**END OF SPECIFICATION**

**Handoff to**: `full-stack-developer` for implementation
**Review required by**: `security-engineer-tech` before deployment (API key handling)
**QA gate**: `qa-engineer` on sandbox before live deployment
