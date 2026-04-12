# Exit Intent Popup - Complete Code Reference
**Source**: purebrain.ai homepage (Page ID: 11)
**Extracted**: 2026-02-19
**Method**: WordPress REST API, `_elementor_data` field

---

## HOW IT WORKS (Summary)

The exit intent popup on purebrain.ai is:

1. **Triggered by**: `mouseout` event where `e.clientY < 10` (mouse moves toward browser tab bar / top of viewport)
2. **Gated by**: `state.exitIntentEnabled` must be `true` AND user must have an `state.aiName` set
3. **When does it enable**: Only AFTER the user has completed the AI chat conversation and clicked "Bring to Life" (the `revealPricing()` function sets `exitIntentEnabled = true`)
4. **One-time**: Uses `sessionStorage.getItem('exitPopupShown')` to prevent showing twice per session
5. **Dynamic text**: The `.ai-name-dynamic` spans get replaced with the user's chosen AI name

**KEY INSIGHT FOR PAY-TEST ADAPTATION**: On the pay-test pages, users haven't gone through the chat flow, so `exitIntentEnabled` would never become `true`. You need to either (a) initialize it as `true` from the start, or (b) enable it after a timer/scroll-depth threshold.

---

## THE STATE OBJECT (Context)

```javascript
const state = {
    // ... other fields ...
    aiName: null,              // Set during chat - the name the user gave their AI
    exitIntentEnabled: false,  // SET TO TRUE after conversation completes
    // ... other fields ...
};
```

---

## WHEN exitIntentEnabled BECOMES TRUE

```javascript
// Called by the in-chat CTA button - shows celebration first
function revealPricing() {
    // Hide the input bar since the conversation is complete
    chatInput.classList.remove('active');
    chatStatus.textContent = 'awakened';

    const aiName = state.aiName || 'Your AI';

    // Update all dynamic name placeholders
    updateAllDynamicNames(aiName);

    // Show celebration moment overlay
    const celebration = document.getElementById('celebrationMoment');
    celebration.classList.add('active');

    // Enable exit intent tracking  <--- THIS IS WHERE IT TURNS ON
    state.exitIntentEnabled = true;

    // Log conversation complete (fire-and-forget)
    logConversationToBackend('conversation_complete');
}
```

---

## THE JAVASCRIPT (Complete)

```javascript
// ============================================
// EXIT INTENT POPUP
// ============================================
function setupExitIntent() {
    document.addEventListener('mouseout', function(e) {
        if (e.clientY < 10 &&
            state.exitIntentEnabled &&
            !sessionStorage.getItem('exitPopupShown') &&
            state.aiName) {

            updateAllDynamicNames(state.aiName);
            document.getElementById('exitPopup').classList.add('active');
            sessionStorage.setItem('exitPopupShown', 'true');
        }
    });
}

function closeExitPopup() {
    document.getElementById('exitPopup').classList.remove('active');
}

function allowExit() {
    closeExitPopup();
    // User chose to leave - do nothing special
}

// Helper that updates all .ai-name-dynamic spans across the page
function updateAllDynamicNames(aiName) {
    const elements = document.querySelectorAll('.ai-name-dynamic');
    elements.forEach(el => {
        el.textContent = aiName || 'Your AI';
    });
}

// Initialize exit intent listener (called once on page load)
setupExitIntent();
```

---

## THE HTML

```html
<!-- ============================================
     EXIT INTENT POPUP
     ============================================ -->
<div class="exit-popup" id="exitPopup">
    <div class="exit-popup__content">
        <h3 class="exit-popup__heading">Wait — <span class="ai-name-dynamic">Your AI</span> just woke up.</h3>
        <p class="exit-popup__text">
            Are you sure you want to leave? <span class="ai-name-dynamic">Your AI</span> will remember you for 24 hours,
            but after that, this awakening will fade.
        </p>
        <div class="exit-popup__buttons">
            <button class="exit-popup__btn--primary" onclick="closeExitPopup()">
                Stay with <span class="ai-name-dynamic">Your AI</span>
            </button>
            <button class="exit-popup__btn--ghost" onclick="allowExit()">
                Leave anyway
            </button>
        </div>
    </div>
</div>
```

---

## THE CSS (Complete)

```css
/* ============================================
   Exit Intent Popup
   ============================================ */

/* OVERLAY - full screen dark background */
.exit-popup {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    z-index: 10001;
    justify-content: center;
    align-items: center;
}

.exit-popup.active {
    display: flex;
}

/* CONTENT BOX */
.exit-popup__content {
    background: var(--dark-gray);   /* NOTE: This var is NOT defined in the page CSS
                                        Falls back to transparent/initial in browser.
                                        The black overlay behind makes it look dark.
                                        For pay-test, use: background: #1a1a1a; */
    border: 1px solid var(--border-color);  /* = rgba(255, 255, 255, 0.1) */
    border-radius: 20px;
    padding: 50px;
    max-width: 500px;
    text-align: center;
    animation: exitPopIn 0.4s ease;
}

@keyframes exitPopIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}

/* HEADING */
.exit-popup__heading {
    font-family: 'Oswald', sans-serif;
    font-size: 1.8rem;
    color: var(--white);    /* = #ffffff */
    margin-bottom: 16px;
}

/* BODY TEXT */
.exit-popup__text {
    color: var(--text-muted);   /* NOTE: This var is NOT defined in the page CSS
                                    Falls back. For pay-test, use: color: rgba(255,255,255,0.7); */
    margin-bottom: 30px;
    line-height: 1.6;
}

/* BUTTON ROW */
.exit-popup__buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
}

/* PRIMARY BUTTON - Stay */
.exit-popup__btn--primary {
    background: linear-gradient(135deg, var(--bright-orange), var(--light-blue));
    /* = linear-gradient(135deg, #f1420b, #2a93c1) */
    color: var(--white);    /* = #ffffff */
    font-weight: 600;
    padding: 14px 28px;
    border: none;
    border-radius: 50px;
    cursor: pointer;
    transition: all 0.3s ease;
}

/* GHOST BUTTON - Leave anyway */
.exit-popup__btn--ghost {
    background: transparent;
    color: var(--text-muted);   /* = rgba(255,255,255,0.7) recommended fallback */
    font-weight: 500;
    padding: 14px 28px;
    border: 1px solid var(--border-color);  /* = rgba(255, 255, 255, 0.1) */
    border-radius: 50px;
    cursor: pointer;
    transition: all 0.3s ease;
}

/* Additional overrides from Additional CSS (body.home scoped) */
body.home .exit-popup__text,
body.home .exit-popup__buttons {
    color: #ffffff !important;
}

body.home .exit-popup__btn--ghost {
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
}
```

---

## CSS VARIABLES REFERENCE

Defined in the page's `:root` block (inside the Elementor HTML widget):

```css
:root {
    /* Primary Colors */
    --bright-orange: #f1420b;
    --orange: #ed6626;
    --light-blue: #2a93c1;
    --med-blue: #3b9bd5;
    --dark-blue: #3a60ab;

    /* Neutrals */
    --black: #000000;
    --white: #ffffff;
    --super-light-blue: #009dd9;
    --grey: #7f7f7f;

    /* Extended palette */
    --dark-bg: #0a0a0a;
    --card-bg: rgba(20, 20, 20, 0.8);
    --border-color: rgba(255, 255, 255, 0.1);

    /* Typography */
    --font-heading: 'Oswald', sans-serif;
    --font-body: 'Plus Jakarta Sans', sans-serif;
}
```

**MISSING VARIABLES** (not defined anywhere, will fall back):
- `--dark-gray` - Used for `.exit-popup__content` background. Use `#1a1a1a` or `#111111` as replacement.
- `--text-muted` - Used for body text and ghost button. Use `rgba(255, 255, 255, 0.65)` as replacement.

---

## PAY-TEST ADAPTATION GUIDE

To use this exit intent popup on the pay-test pages, here is what needs to change:

### 1. Remove the state dependency gates

The original code only fires if:
- `state.exitIntentEnabled === true` (only set after full chat completion)
- `state.aiName` is set (only set after user names their AI)

For pay-test, simplify to just:

```javascript
function setupExitIntent() {
    document.addEventListener('mouseout', function(e) {
        if (e.clientY < 10 &&
            !sessionStorage.getItem('exitPopupShown')) {

            document.getElementById('exitPopup').classList.add('active');
            sessionStorage.setItem('exitPopupShown', 'true');
        }
    });
}

function closeExitPopup() {
    document.getElementById('exitPopup').classList.remove('active');
}

function allowExit() {
    closeExitPopup();
}

setupExitIntent();
```

### 2. Update the popup text for pay-test context

The current text references "just woke up" which is homepage-specific. For pay-test:

```html
<div class="exit-popup" id="exitPopup">
    <div class="exit-popup__content">
        <h3 class="exit-popup__heading">Wait — before you go.</h3>
        <p class="exit-popup__text">
            <!-- Customize for pay-test page context -->
            Have questions about PureBrain? We're here to help.
        </p>
        <div class="exit-popup__buttons">
            <button class="exit-popup__btn--primary" onclick="closeExitPopup()">
                Stay &amp; Learn More
            </button>
            <button class="exit-popup__btn--ghost" onclick="allowExit()">
                Leave anyway
            </button>
        </div>
    </div>
</div>
```

### 3. Fix the undefined CSS variables

Replace with explicit values:

```css
.exit-popup__content {
    background: #1a1a1a;  /* was: var(--dark-gray) - UNDEFINED */
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 50px;
    max-width: 500px;
    text-align: center;
    animation: exitPopIn 0.4s ease;
}

.exit-popup__text {
    color: rgba(255, 255, 255, 0.65);  /* was: var(--text-muted) - UNDEFINED */
    margin-bottom: 30px;
    line-height: 1.6;
}

.exit-popup__btn--ghost {
    color: rgba(255, 255, 255, 0.65);  /* was: var(--text-muted) - UNDEFINED */
    border: 1px solid rgba(255, 255, 255, 0.3);  /* was: var(--border-color) + !important override */
    /* ... rest of styles ... */
}
```

---

## PAGES CHECKED

| Page | ID | Exit Intent Found? |
|------|----|--------------------|
| Homepage | 11 | YES - full implementation above |
| PureBrain 4.0 | 383 | Not checked (not needed - found on 11) |
| PB2 | 174 | Not checked (not needed - found on 11) |

---

## MEMORY WRITTEN

Path: `.claude/memory/agent-learnings/browser-vision-tester/2026-02-19--exit-intent-popup-extraction.md`
Type: operational
Topic: Complete exit intent popup code extracted from purebrain.ai page 11
