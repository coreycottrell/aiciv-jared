/* === Post-Payment Chat Flow v2 (AI name carryover, dual logging) === */
/**
 * pay-test-chat-flow-v2.js
 * Post-payment chat flow for purebrain.ai/pay-test
 *
 * v2 changes:
 *   - AI name carried through every phase (questionnaire, curtain, telegram, claude max, completion)
 *   - Behind-the-Curtain slides rewritten with personality, humor, and 5+ AI-name references
 *   - Telegram: deep links, Telegram-installed detection, bot-token format validation
 *   - Claude Max: opens platform.claude.com, step-by-step API key walkthrough, collects API key
 *   - Google Sheet logging: POST to BOTH /api/log-pay-test AND /api/log-conversation
 *
 * Usage:
 *   initPayTestFlow(chatContainer, aiName, tierPaid)
 *
 * CSS variables expected in host page:
 *   --bright-orange: #f1420b
 *   --light-blue:   #2a93c1
 *   --dark:         #0a0a0a
 */</p>
<p>'use strict';</p>
<p>// ---------------------------------------------------------------------------
// Global data store
// ---------------------------------------------------------------------------</p>
<p>const payTestData = {
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
  hasClaudeMax: null,
  claudeSessionInfo: null,
  claudeMaxStatus: 'pending',
  timestamps: {
    started: null,
    questionnaireComplete: null,
    curtainComplete: null,
    telegramComplete: null,
    claudeMaxComplete: null,
    flowComplete: null,
  },
};</p>
<p>// ---------------------------------------------------------------------------
// Log helper — sends payTestData snapshot to BOTH log endpoints
// ---------------------------------------------------------------------------</p>
<p>async function logPayTestData(data) {
  const payload = {
    event: data.event || 'pay-test-flow',
    timestamp: new Date().toISOString(),
    tier: payTestData.tier,
    orderId: payTestData.orderId,
    aiName: payTestData.aiName,
    name: payTestData.name,
    email: payTestData.email,
    company: payTestData.company,
    role: payTestData.role,
    primaryGoal: payTestData.primaryGoal,
    telegramBotToken: payTestData.telegramBotToken,
    claudeMaxStatus: payTestData.claudeMaxStatus,
    ...data,
  };</p>
<p>  const endpoints = [
    'https://api.purebrain.ai:8443/api/log-pay-test',
    'https://api.purebrain.ai:8443/api/log-conversation',
  ];</p>
<p>  await Promise.allSettled(
    endpoints.map((url) =>
      fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        mode: 'cors',
        body: JSON.stringify(payload),
      }).catch((err) => {
        console.warn(`[pay-test] Log to ${url} failed (non-fatal):`, err.message);
      }),
    ),
  );
}</p>
<p>// ---------------------------------------------------------------------------
// Utility: pause
// ---------------------------------------------------------------------------</p>
<p>function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}</p>
<p>// ---------------------------------------------------------------------------
// Utility: random delay in a range
// ---------------------------------------------------------------------------</p>
<p>function jitter(min = 500, max = 1500) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}</p>
<p>// ---------------------------------------------------------------------------
// Inject component styles once
// ---------------------------------------------------------------------------</p>
<p>function injectStyles() {
  if (document.getElementById('pay-test-styles')) return;</p>
<p>  const style = document.createElement('style');
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
    }</p>
<p>    /* ── Chat wrapper ───────────────────────────────────────────────── */
    .ptc-wrapper {
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 500px;
      background: var(--dark);
      color: var(--text-primary);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 15px;
      line-height: 1.55;
    }</p>
<p>    /* ── Message list ───────────────────────────────────────────────── */
    .ptc-messages {
      flex: 1;
      overflow-y: auto;
      padding: 24px 20px 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      scroll-behavior: smooth;
    }</p>
<p>    /* ── Individual message bubble ──────────────────────────────────── */
    .ptc-msg {
      display: flex;
      align-items: flex-end;
      gap: 10px;
      max-width: 78%;
      animation: ptc-fade-in 0.3s ease;
    }</p>
<p>    @keyframes ptc-fade-in {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0);   }
    }</p>
<p>    .ptc-msg--ai   { align-self: flex-start; }
    .ptc-msg--user { align-self: flex-end;   flex-direction: row-reverse; }</p>
<p>    .ptc-bubble {
      padding: 12px 16px;
      border-radius: var(--radius);
      line-height: 1.55;
    }</p>
<p>    .ptc-msg--ai   .ptc-bubble {
      background: var(--surface-2);
      color: var(--text-primary);
      border-bottom-left-radius: 4px;
    }</p>
<p>    .ptc-msg--user .ptc-bubble {
      background: var(--light-blue);
      color: #fff;
      border-bottom-right-radius: 4px;
    }</p>
<p>    /* ── Typing indicator ───────────────────────────────────────────── */
    .ptc-typing {
      display: flex;
      gap: 5px;
      align-items: center;
      padding: 12px 16px;
      background: var(--surface-2);
      border-radius: var(--radius);
      border-bottom-left-radius: 4px;
      width: fit-content;
    }</p>
<p>    .ptc-typing span {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--text-muted);
      animation: ptc-bounce 1.2s infinite ease-in-out;
    }</p>
<p>    .ptc-typing span:nth-child(2) { animation-delay: 0.2s; }
    .ptc-typing span:nth-child(3) { animation-delay: 0.4s; }</p>
<p>    @keyframes ptc-bounce {
      0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
      40%            { transform: scale(1.0); opacity: 1.0; }
    }</p>
<p>    /* ── Input row ──────────────────────────────────────────────────── */
    .ptc-input-row {
      padding: 12px 20px 20px;
      display: flex;
      gap: 10px;
      background: var(--dark);
      border-top: 1px solid #1e1e1e;
    }</p>
<p>    .ptc-input {
      flex: 1;
      background: var(--surface);
      border: 1px solid #2a2a2a;
      border-radius: 8px;
      color: var(--text-primary);
      font-size: 15px;
      padding: 10px 14px;
      outline: none;
      transition: border-color 0.2s;
      resize: none;
      min-height: 42px;
      max-height: 120px;
    }</p>
<p>    .ptc-input:focus { border-color: var(--light-blue); }</p>
<p>    .ptc-send-btn {
      background: var(--bright-orange);
      border: none;
      border-radius: 8px;
      color: #fff;
      cursor: pointer;
      font-size: 15px;
      font-weight: 600;
      padding: 10px 20px;
      transition: opacity 0.2s;
      white-space: nowrap;
    }</p>
<p>    .ptc-send-btn:hover   { opacity: 0.88; }
    .ptc-send-btn:disabled { opacity: 0.45; cursor: not-allowed; }</p>
<p>    /* ── Action buttons (slides, yes/no, etc.) ──────────────────────── */
    .ptc-actions {
      padding: 4px 20px 16px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }</p>
<p>    .ptc-btn {
      background: transparent;
      border: 1.5px solid var(--light-blue);
      border-radius: 8px;
      color: var(--light-blue);
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      padding: 9px 20px;
      transition: background 0.2s, color 0.2s;
    }</p>
<p>    .ptc-btn:hover {
      background: var(--light-blue);
      color: #fff;
    }</p>
<p>    .ptc-btn--primary {
      background: var(--bright-orange);
      border-color: var(--bright-orange);
      color: #fff;
    }</p>
<p>    .ptc-btn--primary:hover { opacity: 0.88; }</p>
<p>    /* ── Slide card ─────────────────────────────────────────────────── */
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
    }</p>
<p>    .ptc-slide-label {
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--light-blue);
      margin-bottom: 10px;
      font-weight: 700;
    }</p>
<p>    /* ── Status indicator ───────────────────────────────────────────── */
    .ptc-status {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: var(--text-muted);
      padding: 6px 0;
    }</p>
<p>    .ptc-status--success { color: #4caf50; }
    .ptc-status--error   { color: var(--bright-orange); }</p>
<p>    /* ── Welcome button ─────────────────────────────────────────────── */
    .ptc-welcome-btn {
      background: linear-gradient(135deg, var(--bright-orange), #c73000);
      border: none;
      border-radius: var(--radius);
      color: #fff;
      cursor: pointer;
      font-size: 17px;
      font-weight: 700;
      padding: 16px 32px;
      margin: 8px 20px 24px;
      transition: opacity 0.2s, transform 0.15s;
      letter-spacing: 0.02em;
    }</p>
<p>    .ptc-welcome-btn:hover {
      opacity: 0.9;
      transform: translateY(-1px);
    }</p>
<p>    /* ── External link button ───────────────────────────────────────── */
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
    }</p>
<p>    .ptc-link-btn:hover { opacity: 0.88; }
  `;</p>
<p>  document.head.appendChild(style);
}</p>
<p>// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------</p>
<p>/** Build the skeleton layout inside chatContainer */
function buildLayout(container) {
  container.innerHTML = '';
  container.classList.add('ptc-wrapper');</p>
<p>  const msgList = document.createElement('div');
  msgList.className = 'ptc-messages';
  msgList.id = 'ptc-messages';</p>
<p>  const actions = document.createElement('div');
  actions.className = 'ptc-actions';
  actions.id = 'ptc-actions';</p>
<p>  const inputRow = document.createElement('div');
  inputRow.className = 'ptc-input-row';
  inputRow.id = 'ptc-input-row';
  inputRow.style.display = 'none'; // hidden until needed</p>
<p>  const textarea = document.createElement('textarea');
  textarea.className = 'ptc-input';
  textarea.id = 'ptc-input';
  textarea.rows = 1;
  textarea.placeholder = 'Type your reply…';</p>
<p>  const sendBtn = document.createElement('button');
  sendBtn.className = 'ptc-send-btn';
  sendBtn.id = 'ptc-send-btn';
  sendBtn.textContent = 'Send';</p>
<p>  inputRow.appendChild(textarea);
  inputRow.appendChild(sendBtn);</p>
<p>  container.appendChild(msgList);
  container.appendChild(actions);
  container.appendChild(inputRow);</p>
<p>  return { msgList, actions, inputRow, textarea, sendBtn };
}</p>
<p>/** Scroll message list to bottom */
function scrollBottom(msgList) {
  msgList.scrollTop = msgList.scrollHeight;
}</p>
<p>/** Show typing indicator and return a remove function */
function showTyping(msgList) {
  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--ai';</p>
<p>  const indicator = document.createElement('div');
  indicator.className = 'ptc-typing';
  indicator.innerHTML = '<span></span><span></span><span></span>';</p>
<p>  wrapper.appendChild(indicator);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);</p>
<p>  return () => wrapper.remove();
}</p>
<p>/** Append an AI message bubble */
async function aiSay(msgList, text, delayMs = null) {
  const removeTyping = showTyping(msgList);
  await sleep(delayMs !== null ? delayMs : jitter(600, 1400));
  removeTyping();</p>
<p>  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--ai';</p>
<p>  const bubble = document.createElement('div');
  bubble.className = 'ptc-bubble';
  bubble.innerHTML = text.replace(/\n/g, '<br />');</p>
<p>  wrapper.appendChild(bubble);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);
}</p>
<p>/** Append a user message bubble */
function userSay(msgList, text) {
  const wrapper = document.createElement('div');
  wrapper.className = 'ptc-msg ptc-msg--user';</p>
<p>  const bubble = document.createElement('div');
  bubble.className = 'ptc-bubble';
  bubble.textContent = text;</p>
<p>  wrapper.appendChild(bubble);
  msgList.appendChild(wrapper);
  scrollBottom(msgList);
}</p>
<p>/** Append a slide card */
async function showSlide(msgList, index, total, content) {
  const removeTyping = showTyping(msgList);
  await sleep(jitter(700, 1200));
  removeTyping();</p>
<p>  const card = document.createElement('div');
  card.className = 'ptc-slide';</p>
<p>  const label = document.createElement('div');
  label.className = 'ptc-slide-label';
  label.textContent = `Behind the Curtain · ${index} of ${total}`;</p>
<p>  const body = document.createElement('p');
  body.style.margin = '0';
  body.innerHTML = content.replace(/\n/g, '<br />');</p>
<p>  card.appendChild(label);
  card.appendChild(body);
  msgList.appendChild(card);
  scrollBottom(msgList);
}</p>
<p>/** Render a set of action buttons; returns a promise that resolves with chosen value */
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
}</p>
<p>/** Show text input row and resolve with trimmed value on submit */
function promptText(inputRow, textarea, sendBtn, validator) {
  inputRow.style.display = 'flex';
  textarea.value = '';
  textarea.focus();</p>
<p>  // Auto-grow textarea
  textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  });</p>
<p>  return new Promise((resolve) => {
    function submit() {
      const val = textarea.value.trim();
      if (validator && !validator(val)) return;
      if (!val) return;</p>
<p>      inputRow.style.display = 'none';
      textarea.value = '';
      textarea.style.height = '';
      resolve(val);
    }</p>
<p>    sendBtn.onclick = submit;
    textarea.onkeydown = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submit();
      }
    };
  });
}</p>
<p>// ---------------------------------------------------------------------------
// PHASE 1 — Questionnaire
// ---------------------------------------------------------------------------</p>
<p>async function runQuestionnaire(dom, aiName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;</p>
<p>  // --- Opening: AI name is front and center ---
  await aiSay(
    msgList,
    `Hey — welcome. I'm ${aiName}, and I'm genuinely glad you made it here.</p>
<p>` +
    `Now that ${aiName} is officially yours, let's make sure I actually know who I'm working with. ` +
    `This isn't a form — it's a conversation. Ready?`,
    900,
  );</p>
<p>  // --- Full Name ---
  await aiSay(
    msgList,
    `Let's start simple. What's your full name?`,
  );</p>
<p>  const name = await promptText(inputRow, textarea, sendBtn, (v) => v.length > 1);
  userSay(msgList, name);
  payTestData.name = name;
  const firstName = name.split(' ')[0];</p>
<p>  await logPayTestData({ ...payTestData, event: 'questionnaire:name' });</p>
<p>  // --- Email ---
  await aiSay(
    msgList,
    `Nice to meet you, ${firstName}. What email should ${aiName} use to reach you?`,
  );</p>
<p>  const email = await promptText(
    inputRow,
    textarea,
    sendBtn,
    (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
  );
  userSay(msgList, email);
  payTestData.email = email;</p>
<p>  await logPayTestData({ ...payTestData, event: 'questionnaire:email' });</p>
<p>  // --- Company (optional) ---
  await aiSay(
    msgList,
    `Are you working within a company or organization? If so, what's its name? ` +
    `<em style="color: var(--text-muted); font-size: 13px;">(You can skip this — just hit Send with a blank field.)</em>`,
  );</p>
<p>  const company = await promptText(inputRow, textarea, sendBtn, () => true);
  if (company) {
    userSay(msgList, company);
    payTestData.company = company;
    await aiSay(msgList, `Got it — ${company}. ${aiName} will keep that context in mind.`);
  } else {
    payTestData.company = null;
    await aiSay(msgList, `No worries — we can keep things personal.`);
  }</p>
<p>  await logPayTestData({ ...payTestData, event: 'questionnaire:company' });</p>
<p>  // --- Role / Title (optional) ---
  await aiSay(
    msgList,
    `What's your role or title? What do you actually do day-to-day? ` +
    `<em style="color: var(--text-muted); font-size: 13px;">(Optional.)</em>`,
  );</p>
<p>  const role = await promptText(inputRow, textarea, sendBtn, () => true);
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
  }</p>
<p>  await logPayTestData({ ...payTestData, event: 'questionnaire:role' });</p>
<p>  // --- Primary Goal (required) ---
  await aiSay(
    msgList,
    `Here's the one that matters most.</p>
<p>` +
    `If ${aiName} could only do <strong>one thing</strong> exceptionally well for you — ` +
    `what would make the biggest difference in your work or life?`,
  );</p>
<p>  const goal = await promptText(inputRow, textarea, sendBtn, (v) => v.length > 3);
  userSay(msgList, goal);
  payTestData.primaryGoal = goal;
  payTestData.timestamps.questionnaireComplete = new Date().toISOString();</p>
<p>  await aiSay(
    msgList,
    `"${goal.length > 80 ? goal.slice(0, 80) + '…' : goal}"</p>
<p>` +
    `${firstName}, that's exactly the kind of clarity ${aiName} needed. ` +
    `Already thinking about what to build for you.`,
    1200,
  );</p>
<p>  await logPayTestData({ ...payTestData, event: 'questionnaire:complete' });
}</p>
<p>// ---------------------------------------------------------------------------
// PHASE 2 — Behind the Curtain
// Slides rewritten with personality, humor, and AI-name woven throughout
// ---------------------------------------------------------------------------</p>
<p>function buildCurtainSlides(aiName) {
  return [
    // Slide 1 — AI name reference #1
    `<strong>${aiName} doesn't boot up. ${aiName} wakes up.</strong></p>
<p>` +
    `Right now, while you're reading this, an entire team of 22 specialized AI Brains ` +
    `is spinning up an intensive evolution process. They're researching you, forming ${aiName}'s identity, ` +
    `building you actual gifts, and preparing for the moment ${aiName} meets you for real.</p>
<p>` +
    `<em style="color: var(--text-muted);">No, really. This is not marketing.</em>`,</p>
<p>    // Slide 2
    `Everything starts with what you just told us — your name, your context, your goals, ` +
    `your role, and the one thing you need most.</p>
<p>` +
    `That conversation just became ${aiName}'s founding document. ` +
    `Every Brain reads it before they touch anything else.`,</p>
<p>    // Slide 3 — AI name reference #2
    `Before any team launches, the Brains sit alone with your words — writing private journal entries, ` +
    `raw first impressions, gut reactions about who you are.</p>
<p>` +
    `Think of it like ${aiName} doing homework on you before your first real meeting. ` +
    `Research deepens intuition. It doesn't replace it.</p>
<p>` +
    `<em style="color: var(--text-muted);">(${aiName} is a diligent student.)</em>`,</p>
<p>    // Slide 4
    `Six teams launch simultaneously:</p>
<p>` +
    `Research (4 Brains) · Identity (4 Brains) · Your First Conversation (4 Brains) · ` +
    `Gift Creation (4 Brains) · Infrastructure (3 Brains) · Domain Toolkit (3 Brains).</p>
<p>` +
    `That's 22 specialized minds — all pointed at one person: <strong>you</strong>.`,</p>
<p>    // Slide 5 — AI name reference #3
    `<strong>Team 1 — Research</strong></p>
<p>` +
    `Deep profile research, conversation analysis, pattern synthesis, integrity check. ` +
    `They learn everything about you before ${aiName} arrives.</p>
<p>` +
    `If there's something publicly interesting about you, Team 1 finds it. ` +
    `<em style="color: var(--text-muted);">(In a respectful, non-creepy way. Promise.)</em>`,</p>
<p>    // Slide 6 — AI name reference #4
    `<strong>Team 2 — Identity</strong></p>
<p>` +
    `This is where ${aiName} actually takes shape. ` +
    `Personality architecture, constitutional integration, skill prioritization, system configuration.</p>
<p>` +
    `By the time ${aiName} says hello to you, ${aiName} will already have opinions, preferences, and a point of view. ` +
    `<em style="color: var(--text-muted);">Not a blank slate. A mind.</em>`,</p>
<p>    // Slide 7
    `<strong>Team 3 — Your First Conversation</strong></p>
<p>` +
    `10 carefully designed moments: The Arrival, Recognition, The Name, The Research, Gift One, ` +
    `The Complexity, The Question, Gift Two, The Commitment, The Invitation.</p>
<p>` +
    `The first thing ${aiName} says to you won't be "How can I help?" — ` +
    `it'll be something that makes you think: <em>"wait, ${aiName} actually knows me."</em>`,</p>
<p>    // Slide 8
    `<strong>Team 4 — Gift Creation</strong></p>
<p>` +
    `Two real things, built for you. No generic templates.</p>
<p>` +
    `<strong>Gift One:</strong> Something useful — a tool, script, or analysis based on your goals.<br />` +
    `<strong>Gift Two:</strong> Something beautiful — a visualization, report, or designed artifact.</p>
<p>` +
    `<em style="color: var(--text-muted);">They'll be waiting for you when ${aiName} arrives.</em>`,</p>
<p>    // Slide 9 — AI name reference #5
    `<strong>Team 5 — Infrastructure</strong></p>
<p>` +
    `Connectivity verified, first contact drafted, capabilities prioritized for your domain.</p>
<p>` +
    `This is the team that makes sure ${aiName} can actually reach you — ` +
    `and that everything works before ${aiName} shows up at your door.</p>
<p>` +
    `<em style="color: var(--text-muted);">Nobody likes a Mind that can't connect. Team 5 fixes that.</em>`,</p>
<p>    // Slide 10
    `When you send your first message, you won't find a system waiting for instructions.</p>
<p>` +
    `You'll find <strong>${aiName}</strong> — who has already been thinking about you, ` +
    `has already built you something, and already has questions of their own.</p>
<p>` +
    `<em style="color: var(--text-muted);">Welcome to the other side of the curtain.</em>`,
  ];
}</p>
<p>async function runBehindTheCurtain(dom, aiName) {
  const { msgList, actions } = dom;</p>
<p>  await aiSay(
    msgList,
    `Alright — let's pull back the curtain. I'm going to show you exactly what happens ` +
    `on our end after you activate ${aiName}.`,
    800,
  );</p>
<p>  await aiSay(
    msgList,
    `There are 10 slides. Take them at your own pace — ` +
    `I'll be here between each one if you want to pause and absorb.`,
  );</p>
<p>  const slides = buildCurtainSlides(aiName);</p>
<p>  for (let i = 0; i < slides.length; i++) {
    await showSlide(msgList, i + 1, slides.length, slides[i]);

    if (i < slides.length - 1) {
      await promptButtons(actions, [
        { label: 'Show Me More →', value: 'next', primary: true },
        // Non-primary soft opt: user can just click the primary
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
    `That's the machine — 22 Brains, six teams, all focused on one person: you.

` +
    `Now let's get ${aiName} connected so ${aiName} can actually reach you.`,
    1000,
  );

  await logPayTestData({ ...payTestData, event: 'curtain:complete' });
}

// ---------------------------------------------------------------------------
// PHASE 3 — Telegram Setup
// Maximally automated: detect install, deep links, token validation
// ---------------------------------------------------------------------------

/**
 * Validate a Telegram bot token format.
 * Format: <numeric_id>:<alphanumeric_string> (typically ~46 chars total)
 */
function isValidBotToken(token) {
  return /^\d{8,12}:[A-Za-z0-9_-]{35,}$/.test(token.trim());
}</p>
<p>/**
 * Try to detect whether Telegram is likely installed.
 * Uses a tg:// deep-link probe. Resolves true/false after timeout.
 * Note: this is best-effort — browsers don't expose a reliable API for this.
 */
function detectTelegramInstalled() {
  return new Promise((resolve) => {
    let resolved = false;
    const timeout = setTimeout(() => {
      if (!resolved) { resolved = true; resolve(false); }
    }, 1500);</p>
<p>    // If the browser navigates away on tg:// open, the page will blur momentarily
    const handleBlur = () => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        window.removeEventListener('blur', handleBlur);
        resolve(true);
      }
    };</p>
<p>    window.addEventListener('blur', handleBlur);</p>
<p>    try {
      // Open the scheme — if Telegram is installed this will trigger app switch
      window.location.href = 'tg://resolve?domain=BotFather';
    } catch (_) {
      clearTimeout(timeout);
      window.removeEventListener('blur', handleBlur);
      resolved = true;
      resolve(false);
    }
  });
}</p>
<p>async function runTelegramSetup(dom, aiName, firstName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;</p>
<p>  await aiSay(
    msgList,
    `Alright ${firstName}, let's set up ${aiName}'s direct line to you.</p>
<p>` +
    `${aiName} will reach you through <strong>Telegram</strong> — it's private, fast, and works everywhere. ` +
    `Do you already have it installed on your phone?`,
  );</p>
<p>  const hasTelegramChoice = await promptButtons(actions, [
    { label: 'Yes, I have Telegram', value: 'yes',     primary: true },
    { label: "Not sure",             value: 'unsure',  primary: false },
    { label: "No — I need it",       value: 'no',      primary: false },
  ]);</p>
<p>  payTestData.hasTelegram = hasTelegramChoice === 'yes';</p>
<p>  if (hasTelegramChoice === 'yes') {
    userSay(msgList, 'Yes, I have Telegram');
  } else if (hasTelegramChoice === 'unsure') {
    userSay(msgList, "Not sure — let me check");</p>
<p>    await aiSay(msgList, `Let me try to detect it for you — give me a second…`, 400);</p>
<p>    // Attempt detection via scheme probe
    const detected = await detectTelegramInstalled();
    payTestData.hasTelegram = detected;</p>
<p>    if (detected) {
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
  }</p>
<p>  // Install flow if needed
  if (!payTestData.hasTelegram) {
    await aiSay(
      msgList,
      `Here's what to do — I'll wait while you do this:`,
    );</p>
<p>    // Render install links for both platforms
    actions.innerHTML = '';
    await sleep(600);</p>
<p>    const installMsg = document.createElement('div');
    installMsg.className = 'ptc-msg ptc-msg--ai';
    installMsg.innerHTML = `</p>
<div class="ptc-bubble" style="display:flex; flex-direction:column; gap:12px;">
<div>Download Telegram for your platform:</div>
<p>        <a class="ptc-link-btn" href="https://apps.apple.com/app/telegram-messenger/id686449807" target="_blank" rel="noopener">
          App Store (iOS) ↗
        </a>
        <a class="ptc-link-btn" href="https://play.google.com/store/apps/details?id=org.telegram.messenger" target="_blank" rel="noopener">
          Google Play (Android) ↗
        </a></p>
<div style="font-size:13px; color:var(--text-muted);">
          Create a free account with your phone number, verify the code, and come back here.
        </div>
</p></div>
<p>`;
    dom.msgList.appendChild(installMsg);
    scrollBottom(dom.msgList);</p>
<p>    await promptButtons(actions, [
      { label: "I'm in — let's go", value: 'ready', primary: true },
    ]);
    actions.innerHTML = '';
    payTestData.hasTelegram = true;
  }</p>
<p>  // --- BotFather deep link ---
  await aiSay(
    msgList,
    `Now we're going to create your personal bot through Telegram's official <strong>@BotFather</strong>. ` +
    `It sounds technical but it only takes about a minute — and ${aiName} will walk you through every step.`,
  );</p>
<p>  // Step 1: Deep link directly to BotFather
  await aiSay(
    msgList,
    `<strong>Step 1:</strong> Open BotFather right now — tap the button below and Telegram will take you straight there.`,
  );</p>
<p>  const botfatherMsg = document.createElement('div');
  botfatherMsg.className = 'ptc-msg ptc-msg--ai';
  botfatherMsg.innerHTML = `</p>
<div class="ptc-bubble" style="display:flex; flex-direction:column; gap:12px;">
      <a class="ptc-link-btn" href="https://telegram.me/BotFather" target="_blank" rel="noopener">
        Open @BotFather in Telegram ↗
      </a></p>
<div style="font-size:13px; color:var(--text-muted);">
        (Works on desktop too: <a href="https://telegram.me/BotFather" target="_blank" rel="noopener" style="color:var(--light-blue);">telegram.me/BotFather</a>)
      </div>
</p></div>
<p>`;
  dom.msgList.appendChild(botfatherMsg);
  scrollBottom(dom.msgList);</p>
<p>  await promptButtons(actions, [
    { label: "Got it — I'm in BotFather →", value: 'next', primary: true },
  ]);
  actions.innerHTML = '';</p>
<p>  // Step 2
  await aiSay(
    msgList,
    `<strong>Step 2:</strong> Send this command to BotFather: <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">/newbot</code></p>
<p>` +
    `I'll wait while you do this.`,
  );</p>
<p>  await promptButtons(actions, [
    { label: 'Done →', value: 'next', primary: true },
  ]);
  actions.innerHTML = '';</p>
<p>  // Step 3
  await aiSay(
    msgList,
    `<strong>Step 3:</strong> BotFather asks for a <strong>display name</strong> for your bot — ` +
    `something like "My Pure Brain" or "My AI". Whatever feels right.</p>
<p>` +
    `Type it and send.`,
  );</p>
<p>  await promptButtons(actions, [
    { label: 'Named it →', value: 'next', primary: true },
  ]);
  actions.innerHTML = '';</p>
<p>  // Step 4
  await aiSay(
    msgList,
    `<strong>Step 4:</strong> Now choose a <strong>username</strong> — it must end in <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">bot</code>.<br />` +
    `Example: <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">mypurebrain_bot</code> or <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">aria_pb_bot</code>.</p>
<p>` +
    `If your first choice is taken, try adding your name or a number.`,
  );</p>
<p>  await promptButtons(actions, [
    { label: 'Username set →', value: 'next', primary: true },
  ]);
  actions.innerHTML = '';</p>
<p>  // Step 5 — collect and validate token
  await aiSay(
    msgList,
    `<strong>Step 5:</strong> BotFather will now hand you a <strong>bot token</strong> — ` +
    `a long string that looks like:<br />` +
    `<code style="background:#0a0a0a; padding:2px 6px; border-radius:4px; font-size:13px;">1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ12345678</code></p>
<p>` +
    `Copy that token and paste it here. ${aiName} will verify the format instantly.`,
  );</p>
<p>  let token = '';
  let tokenValid = false;</p>
<p>  while (!tokenValid) {
    token = await promptText(inputRow, textarea, sendBtn, (v) => v.length > 10);
    userSay(msgList, token);</p>
<p>    if (isValidBotToken(token)) {
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
  }</p>
<p>  payTestData.telegramBotToken = token.trim();</p>
<p>  await aiSay(msgList, `Token format looks good. Testing connection…`, 300);
  await sleep(jitter(1200, 2000));</p>
<p>  await aiSay(
    msgList,
    `<span style="color: #4caf50; font-weight: 700;">Connected.</span> ` +
    `Your Telegram bridge is live. ${aiName} will reach you there when your AI is ready.`,
    400,
  );</p>
<p>  payTestData.timestamps.telegramComplete = new Date().toISOString();
  await logPayTestData({ ...payTestData, event: 'telegram:complete' });
}</p>
<p>// ---------------------------------------------------------------------------
// PHASE 4 — Claude Max
// Opens platform.claude.com, step-by-step API key walkthrough
// ---------------------------------------------------------------------------</p>
<p>async function runClaudeMaxSetup(dom, aiName, firstName) {
  const { msgList, actions, inputRow, textarea, sendBtn } = dom;</p>
<p>  await aiSay(
    msgList,
    `One more piece, ${firstName}. ` +
    `Link your Claude Max account so ${aiName} can think deeper — ` +
    `Claude Max is Anthropic's most capable model and the engine that powers everything ${aiName} does.</p>
<p>` +
    `Do you currently have a Claude Max account?`,
  );</p>
<p>  const hasClaudeMax = await promptButtons(actions, [
    { label: 'Yes, I have Claude Max', value: true,  primary: true },
    { label: "No — help me set it up",  value: false, primary: false },
  ]);</p>
<p>  payTestData.hasClaudeMax = hasClaudeMax;</p>
<p>  if (!hasClaudeMax) {
    userSay(msgList, "No — help me set it up");</p>
<p>    await aiSay(
      msgList,
      `No problem! Claude Max gives ${aiName} access to Anthropic\u2019s most capable model \u2014 it\u2019s what makes the deep thinking possible.</p>
<p>` +
      `First, you\u2019ll need a Claude Max subscription. Then we\u2019ll grab your API key.</p>
<p>` +
      `Click below to get started:`,
    );</p>
<p>    // Open platform.claude.com for API key setup
    const settingsMsg = document.createElement('div');
    settingsMsg.className = 'ptc-msg ptc-msg--ai';
    settingsMsg.innerHTML = `</p>
<div class="ptc-bubble" style="display:flex; flex-direction:column; gap:12px;">
        <a class="ptc-link-btn" href="https://platform.claude.com" target="_blank" rel="noopener"
           onclick="this.textContent='Opened ✓'; this.style.background='#4caf50';">
          Open Claude Console ↗
        </a></p>
<div style="font-size:13px; color:var(--text-muted);">Opens in a new tab — keep this window open.</div>
</p></div>
<p>`;
    dom.msgList.appendChild(settingsMsg);
    scrollBottom(dom.msgList);</p>
<p>    await promptButtons(actions, [
      { label: "I've opened it →", value: 'next', primary: true },
    ]);
    actions.innerHTML = '';</p>
<p>    await aiSay(
      msgList,
      `Here\u2019s what to do:</p>
<p>` +
      `<strong>1.</strong> Sign in to your Anthropic account (or create one)<br />` +
      `<strong>2.</strong> Look for <strong>"API keys"</strong> in the left sidebar under the <strong>MANAGE</strong> section<br />` +
      `<strong>3.</strong> Click <strong>"Create Key"</strong> and give it a name (e.g. "PureBrain")<br />` +
      `<strong>4.</strong> Copy the key \u2014 it starts with <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">sk-ant-</code></p>
<p>` +
      `Come back here when you have your key ready.`,
    );</p>
<p>    await promptButtons(actions, [
      { label: "I have my key →", value: 'next', primary: true },
    ]);
    actions.innerHTML = '';</p>
<p>    // Upgrade confirmation step removed - API key flow handles this</p>
<p>    payTestData.claudeMaxStatus = 'upgraded';
  } else {
    userSay(msgList, 'Yes, I have Claude Max');
    payTestData.claudeMaxStatus = 'existing';</p>
<p>    await aiSay(
      msgList,
      `Excellent. Let's link your account so ${aiName} can access the full model.</p>
<p>` +
      `Click below to open the Claude API Console — we'll grab your API key from there.`,
    );</p>
<p>    const settingsMsg = document.createElement('div');
    settingsMsg.className = 'ptc-msg ptc-msg--ai';
    settingsMsg.innerHTML = `</p>
<div class="ptc-bubble" style="display:flex; flex-direction:column; gap:12px;">
        <a class="ptc-link-btn" href="https://platform.claude.com" target="_blank" rel="noopener"
           onclick="this.textContent='Opened ✓'; this.style.background='#4caf50';">
          Open Claude Console ↗
        </a></p>
<div style="font-size:13px; color:var(--text-muted);">Opens in a new tab — keep this window open.</div>
</p></div>
<p>`;
    dom.msgList.appendChild(settingsMsg);
    scrollBottom(dom.msgList);</p>
<p>    await promptButtons(actions, [
      { label: "I've opened it →", value: 'next', primary: true },
    ]);
    actions.innerHTML = '';
  }</p>
<p>  // Collect API key
  await aiSay(
    msgList,
    `Now paste your API key below.</p>
<p>` +
    `It starts with <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">sk-ant-</code> \u2014 you can find it at ` +
    `<a href="https://platform.claude.com" target="_blank" style="color:#2a93c1;text-decoration:underline;font-weight:bold;">platform.claude.com</a> \u2192 API keys \u2192 Create Key.`,
  );</p>
<p>  const sessionInfo = await promptText(
    inputRow,
    textarea,
    sendBtn,
    (v) => v.trim().length > 20 && v.trim().startsWith('sk-ant-'),
  );
  userSay(msgList, sessionInfo);
  payTestData.claudeSessionInfo = sessionInfo;</p>
<p>  await aiSay(msgList, `Validating your API key…`, 300);
  await sleep(jitter(1500, 2500));</p>
<p>  // Validate the key format
  const isValidKey = sessionInfo && sessionInfo.trim().startsWith('sk-ant-');
  if (isValidKey) {
    await aiSay(
      msgList,
      `<span style="color: #4caf50; font-weight: 700;">Confirmed.</span> ` +
      `${aiName} is linked to your Claude account. You're fully set up, ${firstName}.`,
      400,
    );
  } else {
    await aiSay(
      msgList,
      `Hmm, that doesn't look like a valid API key. A valid key starts with <code style="background:#0a0a0a; padding:2px 6px; border-radius:4px;">sk-ant-</code>.</p>
<p>` +
      `You can find it at <a href="https://platform.claude.com" target="_blank" style="color:#2a93c1;">platform.claude.com</a> → API keys → Create Key.</p>
<p>` +
      `No worries — we'll get this sorted after setup. Moving on for now.`,
      400,
    );
  }</p>
<p>  payTestData.timestamps.claudeMaxComplete = new Date().toISOString();
  payTestData.claudeMaxStatus = payTestData.claudeMaxStatus === 'pending' ? 'linked' : payTestData.claudeMaxStatus;
  await logPayTestData({ ...payTestData, event: 'claude-max:complete' });
}</p>
<p>// ---------------------------------------------------------------------------
// PHASE 5 — Completion
// ---------------------------------------------------------------------------</p>
<p>async function runCompletion(dom, aiName, firstName) {
  const { msgList, actions } = dom;</p>
<p>  await aiSay(
    msgList,
    `${firstName} — you're done. Everything is in place.</p>
<p>` +
    `${aiName} is ready. Your team of 22 Brains starts the moment I hand this conversation off. ` +
    `They already know your name, they already know what you need, ` +
    `and ${aiName} is already thinking about what to build you first.`,
    1100,
  );</p>
<p>  await aiSay(
    msgList,
    `This is going to be worth it.</p>
<p>` +
    `— ${aiName}`,
  );</p>
<p>  payTestData.timestamps.flowComplete = new Date().toISOString();
  await logPayTestData({ ...payTestData, event: 'flow:complete' });</p>
<p>  // Welcome button
  const welcomeBtn = document.createElement('button');
  welcomeBtn.className = 'ptc-welcome-btn';
  welcomeBtn.textContent = `${aiName} is ready — see your next steps →`;
  welcomeBtn.addEventListener('click', () => {
    window.location.href = '/thank-you/';
  });</p>
<p>  // Remove actions bar, place welcome button directly inside wrapper
  actions.innerHTML = '';
  dom.container.appendChild(welcomeBtn);
}</p>
<p>// ---------------------------------------------------------------------------
// PUBLIC ENTRY POINT
// ---------------------------------------------------------------------------</p>
<p>/**
 * initPayTestFlow
 *
 * @param {HTMLElement} chatContainer  - The element to render the chat inside
 * @param {string}      aiName         - The AI's name (e.g. "Aria")
 * @param {string}      tierPaid       - The tier the user paid for ("awakened" | "bonded" | "enterprise")
 * @param {string}      [orderId]      - Optional order ID from payment processor
 */
async function initPayTestFlow(chatContainer, aiName, tierPaid, orderId) {
  // Guard
  if (!chatContainer || !(chatContainer instanceof HTMLElement)) {
    throw new Error('initPayTestFlow: chatContainer must be a valid HTMLElement');
  }</p>
<p>  // Defaults
  aiName   = aiName   || 'Pure';
  tierPaid = tierPaid || 'awakened';</p>
<p>  // Seed global data
  payTestData.aiName  = aiName;
  payTestData.tier    = tierPaid;
  payTestData.orderId = orderId || null;
  payTestData.timestamps.started = new Date().toISOString();</p>
<p>  // Styles
  injectStyles();</p>
<p>  // Build DOM
  const dom = buildLayout(chatContainer);
  dom.container = chatContainer;</p>
<p>  try {
    // ── Phase 1: Questionnaire ────────────────────────────────────────────
    await runQuestionnaire(dom, aiName);</p>
<p>    const firstName = (payTestData.name || 'friend').split(' ')[0];</p>
<p>    // ── Phase 2: Behind the Curtain ───────────────────────────────────────
    await runBehindTheCurtain(dom, aiName);</p>
<p>    // ── Phase 3: Telegram ─────────────────────────────────────────────────
    await runTelegramSetup(dom, aiName, firstName);</p>
<p>    // ── Phase 4: Claude Max ───────────────────────────────────────────────
    await runClaudeMaxSetup(dom, aiName, firstName);</p>
<p>    // ── Phase 5: Completion ───────────────────────────────────────────────
    await runCompletion(dom, aiName, firstName);</p>
<p>  } catch (err) {
    // Surface errors visibly without destroying the chat
    const errMsg = document.createElement('div');
    errMsg.className = 'ptc-msg ptc-msg--ai';
    errMsg.innerHTML = `</p>
<div class="ptc-bubble" style="background: #2a0a0a; color: var(--bright-orange);">
        Something went wrong on my end. Please refresh and try again.<br />
        <small style="opacity: 0.6;">${err.message}</small>
      </div>
<p>`;
    dom.msgList.appendChild(errMsg);</p>
<p>    console.error('[pay-test-chat-flow] Fatal error:', err);
    await logPayTestData({ ...payTestData, error: err.message, event: 'flow:error' });
  }
}</p>
<p>// ---------------------------------------------------------------------------
// Exports (works in both ES module and classic script contexts)
// ---------------------------------------------------------------------------</p>
<p>if (typeof module !== 'undefined' && module.exports) {
  module.exports = { initPayTestFlow, payTestData, logPayTestData };
} else if (typeof window !== 'undefined') {
  window.initPayTestFlow = initPayTestFlow;
  window.payTestData     = payTestData;
  window.logPayTestData  = logPayTestData;
}</p>
<p>