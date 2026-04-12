# Memory: Chatbox v4.3 — Birth Init Moved to Phase 1, API Key Flow Removed

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Architectural refactor of Witness birth pipeline — runBirthInit moved from Phase 5 to Phase 1 (after Q4/role)

---

## What Changed

### Removed: Claude API Key Collection Flow
The entire "sk-ant-" API key collection block was removed from Phase 1 Step 5b:
- Removed "Before we go deeper" Keen message asking for API key
- Removed "Open Claude Console" button (link to platform.claude.com)
- Removed key input/masking/validation loop (sk-ant- prefix check)
- Removed `claudeSessionInfo` from `payTestData`
- Removed `claudeMaxStatus`, `hasClaudeMax`, `claudeAuthComplete` fields
- Approximately 80 lines of API key logic removed
- "I have my key →" button KEPT but repurposed: now triggers OAuth code input in Birth Init

### Moved: runBirthInit() fires in Phase 1 (after Q4), not Phase 5
Previously: `runBirthInit()` called at start of `runThankYouMessage()` (Phase 5)
Now: `runBirthInit()` called in `runQuestionnaire()` after Q4 role acknowledgment, before Step 6 (Primary Goal)

New Phase 1 flow:
1. Q1: Full name
2. Q2: Email
3. Q3: Company (optional)
4. Q4: Role/title (optional)
5. **Step 5b: runBirthInit() — Witness OAuth setup**
   - Keen: "One more step to complete [AI Name]'s setup, [firstName]. I need to link [AI Name]'s intelligence now..."
   - POST /api/birth/start → wait up to 180s → OAuth URL
   - Show "Authorize [AI Name]'s AI Brain →" button + "Opens in a new tab — keep this window open"
   - "I have my key →" button → activates code input
   - User pastes authorization code → POST /api/birth/code → confirmation
   - Keen: "[AI Name]'s connection is established. The intelligence link is live — let's keep going."
6. Q5: Primary Goal

### Phase 5 (runThankYouMessage) Simplified
- Removed: `await runBirthInit(dom, aiName, firstName);`
- Added comment: `// v4.3: runBirthInit() already fired in Phase 1`
- `runPortalButtonWatcher()` still starts when user clicks "Learn more →" — unchanged

### Background Portal Polling
- `runPortalButtonWatcher()` starts after "Learn more →" click in Phase 5
- At that point, `payTestData.containerName` is already set (from Phase 1 Birth Init)
- The watcher polls `/api/birth/portal-status/{container}` every 30s, up to 30 min
- "Enter [AI Name]'s Brain Stream" portal button appears when ready — unchanged

---

## Script Size Delta

| Version | Chars |
|---------|-------|
| v4.2    | 84,839 chars (84,839 bytes) |
| v4.3    | 82,443 chars |
| Delta   | -2,396 chars (removed API key flow, added v4.3 comments and new UX copy) |

Note: The block replacement was 83,022 chars (old) → 82,462 chars (new script block including `<script>` tags).

---

## Deploy Verification

Both pages passed ALL checks:

### Page 688 (pay-test-sandbox-2) — ALL CHECKS PASSED
- `_elementor_data`: Chat Flow v4.3 ✓ | runBirthInit ✓ | runPortalButtonWatcher ✓ | HTTPS host ✓ | No plain HTTP IP ✓ | sanitizeText ✓ | sk-ant- removed ✓ | Birth init Phase 1 ✓
- `content.raw`: Chat Flow v4.3 ✓ | sk-ant- removed ✓

### Page 689 (pay-test-2 / live) — ALL CHECKS PASSED
- `_elementor_data`: All 8 checks passed
- `content.raw`: Both checks passed

---

## Why This Change Matters

The original Phase 5 placement of runBirthInit had a UX problem: users had already gone through the full questionnaire, Behind the Curtain, and Telegram setup before being asked to do the OAuth flow. By moving it to Phase 1, users link the AI's intelligence immediately after giving their basic context, before learning more about what's happening. This creates better narrative flow: "tell me about yourself → let me connect [AI Name]'s intelligence → now tell me your goal."

---

## Key Implementation Notes

### containerName availability
At Phase 1 Step 5b, all data needed for `/birth/start` is available:
- `firstName` (from Q1 name split)
- `payTestData.email` (from Q2)
- `payTestData.containerName` (derived in runBirthInit from `window._pbContainerName` or `purebrain-{firstName}`)

### "I have my key →" button repurposed
The button text is identical to the removed API key flow but now triggers the OAuth code input. The UX is: user sees OAuth button → clicks to open Claude → comes back → clicks "I have my key →" → types the authorization code.

### promptButtons() used for "I have my key →"
Uses the existing `promptButtons(actions, [{label: 'I have my key →', value: 'next', primary: true}])` pattern. This was already styled as a primary button.

### Security patches remain 100% intact
All v4.2 security fixes preserved:
- sanitizeText() applied at all entry points
- OAuth URL validation (HTTPS + claude.ai/anthropic.com domains only)
- containerName allowlist (lowercase alphanum + hyphens, max 64 chars)
- No plain HTTP IP
- No payTestData on window

---

## Deploy Script Updates

Updated `tools/deploy_chatbox_v4.py`:
1. Now updates BOTH `_elementor_data` AND `content.raw` (v4.2 lesson applied)
2. Verifies both storage locations after deploy
3. Pre-flight checks updated: `'Chat Flow v4.3'`, `'sk-ant-' not in V4_JS`, `'Step 5b: Witness Birth Init' in V4_JS`
4. 8 verification checks per page instead of 6

---

## Files Changed

- `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js` (v4.3)
- `/home/jared/projects/AI-CIV/aether/tools/deploy_chatbox_v4.py` (v4.3 markers + content.raw update)

---

## Related Memory

- `.claude/memory/agent-learnings/full-stack-developer/2026-02-24--chatbox-v42-dual-storage-deploy-pattern.md` (why both storage locations must be updated)
- `.claude/memory/agent-learnings/full-stack-developer/2026-02-24--chatbox-v42-security-fixes.md` (security patches that remain in v4.3)
- `.claude/memory/agent-learnings/full-stack-developer/2026-02-24--witness-birth-pipeline-chatbox-v4.md` (original v4 implementation)
