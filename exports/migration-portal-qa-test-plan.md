# qa-engineer: AI Migration Portal — Comprehensive QA Test Plan

**Agent**: qa-engineer
**Domain**: Quality Assurance
**Date**: 2026-02-23
**Spec Version**: 1.0 (feature-designer, 2026-02-23)
**Target**: PureBrain AI Migration Portal — 4-Step Flow
**Release Gate**: This plan must pass before portal ships

---

## Executive Summary

The AI Migration Portal is a trust-critical feature. Every failure here has outsized psychological damage: a user who just paid for PureBrain and tries to migrate their ChatGPT history, only to hit a broken upload or a generic "task suggestion," will feel deceived. The feature's entire premise is "we understand your history" — so if it doesn't work, the promise collapses on first use.

**Testing philosophy for this portal:**
- Assume users upload real, personal, sensitive data. Handle failures gracefully and privately.
- Personalization claims must be testable and falsifiable. "Suggested because of your history" must be provably true.
- Security failures here are catastrophic — conversation exports are intensely personal PII.

**MVP Scope Reminder (Phase 1 only):**
- ChatGPT file upload (conversations.zip)
- Claude file upload
- Manual style description (Midjourney)
- CSV/JSON upload fallback
- Pattern extraction: top 5 topics, conversation count, date range
- Custom instructions from user.json
- Step 3 insight display
- Step 4 suggested tasks (3 tasks)
- Temp file deletion after processing
- Migration Complete badge

---

## Test Environment Requirements

### Browsers
- Chrome (latest stable)
- Firefox (latest stable)
- Safari (latest stable — critical for Mac/iPhone users)
- Edge (latest stable)

### Devices / Viewports
- Mobile 375px (iPhone SE)
- Mobile 390px (iPhone 14)
- Tablet 768px (iPad)
- Desktop 1440px

### Test Data Required Before Testing Begins

| Dataset | Description | Required For |
|---|---|---|
| `test-chatgpt-small.zip` | Valid ChatGPT export, ~50 conversations, real format | Happy path |
| `test-chatgpt-large.zip` | Valid ChatGPT export, 10,000+ conversations | Performance, large input |
| `test-chatgpt-empty.zip` | Valid ZIP with `conversations.json` = `[]` | Edge case TC-E1 |
| `test-chatgpt-custom-instructions.zip` | Export with non-empty custom_instructions in user.json | Step 2 display |
| `test-claude-small.zip` | Valid Claude export, ~50 conversations | Happy path (competitor 2) |
| `test-corrupt.zip` | ZIP with corrupted central directory | Security TC-S3 |
| `test-bomb.zip` | ZIP bomb (recursive compression, 1GB+ when decompressed) | Security TC-S1 |
| `test-traversal.zip` | ZIP with entries like `../../etc/passwd` | Security TC-S2 |
| `test-fake.zip` | JPEG file renamed to .zip | Security TC-S4 |
| `test-oversized.bin` | File > max allowed upload size | Functional TC-F4 |
| `test-nonlatin.zip` | ChatGPT export with conversations entirely in Japanese, Arabic, Russian | Edge case TC-E4 |
| `test-xss.zip` | ChatGPT export where conversation content includes `<script>alert(1)</script>` | Security TC-S5 |
| `test-special-chars.zip` | Custom instructions with `'`, `"`, `<`, `>`, `\n`, emoji, RTL text | Edge case TC-E5 |

---

## Section 1: Functional Tests

### 1.1 Portal Entry — Migration Banner

**TC-F-BANNER-01: Banner displays on first login for known competitor**

Pre-conditions:
- User account exists, `migration_status = 'not_started'`
- `competitor = 'chatgpt'` in user profile (from exodus landing page data)

Steps:
1. Log in to PureBrain portal as this user
2. Observe dashboard

Expected:
- Migration banner visible and prominent (above the fold)
- Banner text: "You're switching from ChatGPT." (personalized, not generic)
- "Start Migration" button present (orange)
- "Skip for now" present but visually de-emphasized

Pass criteria: Banner shown, competitor name correct, both buttons present.

---

**TC-F-BANNER-02: Banner shows generic text when competitor unknown**

Pre-conditions:
- User account, `migration_status = 'not_started'`
- No `competitor` in profile (direct signup, no exodus page)

Steps:
1. Log in to portal

Expected:
- Banner still shows (migration is valuable for any user)
- Text is generalized: "Let's bring your work with you." — no competitor claim

Pass criteria: No "[competitor]" placeholder visible as literal text. Banner renders with fallback copy.

---

**TC-F-BANNER-03: Banner replaced by Migration Complete badge after completion**

Pre-conditions:
- User has completed all 4 migration steps (migration_status = 'complete')

Steps:
1. Log in to portal
2. Observe dashboard

Expected:
- Migration banner is gone
- Migration Complete badge visible: checkmark + "Absorbed: X conversations · Y use patterns"
- Badge persists across logout/login

Pass criteria: Banner replaced, badge contains real numbers from import, badge persists.

---

**TC-F-BANNER-04: Skip for now persists correctly**

Steps:
1. Log in, see migration banner
2. Click "Skip for now"
3. Log out, log back in

Expected:
- After click: banner dismissed for current session
- After re-login: banner returns (skip is per-session, not permanent dismissal)
- "Skip for now" does not set `migration_status = 'complete'`

Pass criteria: Skip is a soft dismiss, not completion. Banner returns next session.

---

### 1.2 Step 1 — File Upload

**TC-F1-01: Happy path — valid ChatGPT ZIP upload**

Steps:
1. Click "Start Migration" from banner
2. Step 1 loads. Verify: "STEP 1 OF 4" header, progress indicator shows first step active
3. Upload `test-chatgpt-small.zip`
4. Observe upload completion state

Expected:
- Upload accepts the file
- Processing begins
- Card shows green checkmark + summary: "X conversations ready"
- "Continue with what I have" becomes actionable
- No error messages

Pass criteria: Upload succeeds, count shown, checkmark appears, step can be completed.

---

**TC-F1-02: "How to export" instructions — ChatGPT**

Steps:
1. On Step 1, click "How to export" link for ChatGPT

Expected:
- A modal opens (not a new tab, not a redirect)
- Modal contains step-by-step instructions: Settings → Data Controls → Export → ZIP file
- Instructions are accurate and current for ChatGPT as of test date
- Modal can be closed without losing upload state

Pass criteria: Modal opens in-place, instructions are accurate, close preserves state.

---

**TC-F1-03: "How to export" instructions — Claude**

Steps:
1. On Step 1, click "How to export" link for Claude

Expected:
- Modal opens with Anthropic-specific export instructions: Account Settings → Export data
- Distinct from ChatGPT instructions (not duplicated text)

Pass criteria: Instructions correct for Anthropic export flow.

---

**TC-F1-04: Invalid file type rejected at upload**

Steps:
1. On Step 1, attempt to upload `test-oversized.bin` (or any non-ZIP: .pdf, .txt, .jpg)

Expected:
- Upload rejected before file reaches server, OR rejected immediately on arrival
- Error message: clear, user-friendly (not a stack trace)
- Example: "Please upload a ZIP file from your AI tool's export function."
- User can try again without refreshing

Pass criteria: Invalid type rejected gracefully with actionable error message.

---

**TC-F1-05: Oversized file rejected**

Steps:
1. Upload `test-oversized.bin` (file exceeds max upload limit)

Expected:
- Rejection at client side (if size check is client-side) or server side
- Error message specifies the limit: "File size limit is [X]MB. Your file was [Y]MB."
- User can attempt a different file

Pass criteria: Rejected with specific size information.

---

**TC-F1-06: Corrupted ZIP rejected gracefully**

Steps:
1. Upload `test-corrupt.zip`

Expected:
- Upload accepts the file (it's the right type)
- Processing begins
- Error returned: "We couldn't read this file. Try re-downloading your export from ChatGPT."
- Error does not expose internal error messages or stack traces
- User can try again

Pass criteria: Graceful failure with recovery instructions.

---

**TC-F1-07: Continue with partial data (no file uploaded)**

Steps:
1. On Step 1, do not upload any file
2. Click "Continue with what I have"

Expected:
- Portal advances to Step 2
- Step 2 shows empty state gracefully ("No data connected yet")
- User can still proceed through remaining steps
- No JavaScript errors

Pass criteria: Skip works, no crashes, empty state handled.

---

**TC-F1-08: Claude file upload happy path**

Steps:
1. Upload `test-claude-small.zip` on Step 1 (Claude card)

Expected:
- Same behavior as TC-F1-01 (upload succeeds, count shown)
- Parser handles Claude's export format (may differ from OpenAI format)

Pass criteria: Claude export accepted and parsed without error.

---

**TC-F1-09: CSV fallback upload**

Steps:
1. Use "Other Tool" card
2. Upload a valid CSV file (prompt library format: title, content, category columns)

Expected:
- Upload accepted
- Step 2 shows "X prompts ready" from CSV

Pass criteria: CSV fallback works.

---

**TC-F1-10: Manual Midjourney style form**

Steps:
1. Click "Connect" on Midjourney card
2. Enter: "Cinematic, moody, wide angle, film grain, 1970s color palette"
3. Save/confirm

Expected:
- Text saved to migration data
- Step 2 shows: "Visual style description captured"
- [Remove] option available

Pass criteria: Text form works, data visible in Step 2.

---

### 1.3 Step 2 — Data Review Display

**TC-F2-01: Conversation count and date range display correctly**

Pre-conditions: `test-chatgpt-small.zip` uploaded successfully in Step 1

Steps:
1. Advance to Step 2

Expected:
- "X conversations" count matches actual count in `conversations.json`
- "Y years of history" calculated correctly from oldest to newest conversation timestamp
- Both values are accurate (not placeholder/hardcoded)

Pass criteria: Count and date range mathematically verified against source file.

---

**TC-F2-02: Custom instructions preview displayed**

Pre-conditions: `test-chatgpt-custom-instructions.zip` uploaded (user.json has non-empty custom_instructions)

Steps:
1. Advance to Step 2

Expected:
- Custom Instructions row is visible
- Preview shows first ~120 characters of the custom instructions text
- Text is truncated if longer than 120 chars (not cut mid-word if possible)
- [Remove] option present

Pass criteria: Preview visible, accurately reflects the custom instructions content.

---

**TC-F2-03: Remove individual data category**

Steps:
1. On Step 2 with conversations + custom instructions both present
2. Click [Remove] next to "Custom Instructions"

Expected:
- Custom Instructions row is removed from display
- Conversation history row remains
- State is preserved if user clicks back
- When processing begins, custom instructions are NOT included in the pipeline

Pass criteria: Remove works for individual categories. Other categories unaffected.

---

**TC-F2-04: Remove all data categories**

Steps:
1. On Step 2, click [Remove] on every data category

Expected:
- All categories removed
- "Start Import" button either disabled or presents a warning: "No data selected — are you sure?"
- User can re-add data by going back to Step 1

Pass criteria: Empty state handled, no crash, clear UX.

---

**TC-F2-05: Privacy note visible**

Steps:
1. Navigate to Step 2

Expected:
- Privacy note is visible above the "Start Import" CTA at all times
- Text: "Your data is never used to train any model. It lives in your PureBrain instance only."
- "See full privacy policy" link is functional

Pass criteria: Privacy note visible without scrolling to bottom (or visually prominent above CTA regardless of scroll position).

---

**TC-F2-06: Multiple sources displayed together**

Pre-conditions: ChatGPT ZIP uploaded + Midjourney style text entered

Steps:
1. Advance to Step 2

Expected:
- Two distinct sections: "FROM CHATGPT" and (equivalent for Midjourney)
- Each section has its own [Remove] controls
- Counts and content from each source shown separately

Pass criteria: Multi-source display works, no data mixing between sections.

---

### 1.4 Step 3 — Processing Display

**TC-F3-01: Progress indicator advances**

Steps:
1. Click "Start Import" on Step 2
2. Watch Step 3

Expected:
- Step 3 loads immediately (does not wait for completion to show the screen)
- Progress bar/percentage starts below 100% and advances
- Progress is not stuck at 0% or jumping immediately to 100%
- Animated orb is present and in "processing" visual state

Pass criteria: Progress is observable, animated, and not fake (tied to real processing).

---

**TC-F3-02: Insight cards appear during processing**

Steps:
1. Complete Step 2 with a real ChatGPT export
2. Watch Step 3

Expected:
- At least 1 insight card appears before processing is complete
- Insight cards animate in sequentially (not all at once)
- Insight language is in plain English: "You asked about X 23 times." (not technical labels)
- Insights are derived from the actual import content (not hardcoded/generic)

Pass criteria: Minimum 1 non-generic insight card appears, tied to real data.

---

**TC-F3-03: Checklist items complete in sequence**

Steps:
1. Watch Step 3 checklist during processing

Expected:
- Items complete in logical order (Communication style → Top 5 patterns → Custom instructions → Knowledge base indexing)
- Each item shows: pending (◌) → complete (✓) state transition
- Items do not all flip to complete simultaneously

Pass criteria: Checklist transitions visible and sequential.

---

**TC-F3-04: Processing timeout handling (5+ minutes)**

Steps:
1. Simulate or observe a processing job that exceeds 5 minutes (use artificially large file or throttled server)

Expected:
- After 5 minutes, "We'll email you when it's ready" option appears
- User can leave the page and receive email notification when done
- Returning to portal after email shows processing complete, not stuck at Step 3

Pass criteria: Timeout fallback exists and works. Email notification sent.

---

**TC-F3-05: Step 3 does not block UI during processing**

Steps:
1. During active Step 3 processing, attempt to interact with the page

Expected:
- Page remains scrollable
- UI is not frozen
- Browser tab remains responsive
- If user navigates away and returns, processing state is still accurate

Pass criteria: No UI freezing or blocking during async processing.

---

### 1.5 Step 4 — Guided First Tasks

**TC-F4-01: Task cards are personalized, not generic**

Pre-conditions: Import from `test-chatgpt-small.zip` where top topic is "market analysis" (verifiable in conversations.json)

Steps:
1. Complete Step 3 and reach Step 4

Expected:
- At least one task card references "market analysis" or the actual top topic
- Task card contains specific numbers: "You ran market analysis 23 times in ChatGPT" — number must match actual count
- NOT acceptable: "Try a new task with PureBrain" (generic, no data reference)

Pass criteria: Task description contains quantified data point from actual import. Verified against source file count.

---

**TC-F4-02: "Start this task" pre-fills chat correctly**

Steps:
1. On Step 4, click "Start this task" on any task card

Expected:
- Chat interface opens
- Chat input is pre-filled with a contextual starter prompt (not empty)
- Starter prompt is relevant to the task card that was clicked
- User sees the pre-filled prompt and can edit before sending

Pass criteria: Chat opens with contextual pre-fill. Different task cards produce different pre-fills.

---

**TC-F4-03: Three or more task cards generated**

Steps:
1. Complete import with real ChatGPT data

Expected:
- Step 4 shows 3 to 5 task cards
- All task cards have a "Start this task" button
- "Go to my PureBrain" button is also present

Pass criteria: Count of task cards is between 3 and 5 inclusive.

---

**TC-F4-04: Tasks reflect exodus page answers**

Pre-conditions: User came from exodus page with `primary_use_cases: ["writing", "coding"]` stored in Brevo/profile

Steps:
1. Complete migration
2. View Step 4 task cards

Expected:
- At least one task card reflects writing use case
- At least one task card reflects coding use case
- These are not just from conversation analysis but from the quiz answers as well

Pass criteria: Exodus quiz data feeds task generation, not only conversation parsing.

---

**TC-F4-05: Migration Complete badge awarded**

Steps:
1. Click "Go to my PureBrain" from Step 4
2. Return to dashboard

Expected:
- Migration banner is replaced by the Migration Complete badge
- Badge shows: conversation count, connected tools, "Your AI partner knows you."
- Badge is permanent (persists across logout/login sessions)
- "View Migration Summary" link is present and functional

Pass criteria: Badge displayed correctly, data in badge matches import data, persistence confirmed.

---

**TC-F4-06: AI partner's first conversation reflects imported context**

Steps:
1. Complete migration
2. Open a new chat with the PureBrain AI partner
3. Ask: "What do you know about me?"

Expected:
- AI partner response references imported context (top topics, communication style, preferences)
- Response does NOT start from zero ("I don't know anything about you yet")
- Response is specific, not generic

Pass criteria: AI partner demonstrates context from migration. FAIL if AI claims no prior knowledge.

---

## Section 2: Edge Cases

**TC-E1: Empty conversations.json**

Pre-conditions: User exported ChatGPT but had no conversation history (new account, or all conversations deleted)

Steps:
1. Upload `test-chatgpt-empty.zip` where `conversations.json = []`

Expected:
- Upload accepted (valid file, valid format)
- Step 2 shows: "0 conversations" — does NOT show "X conversations" with wrong number
- Processing completes without error
- Step 3 shows appropriate message: "Not much history to analyze — we'll work with what's here"
- Step 4 falls back to exodus page quiz answers for task generation (not conversation data)
- No crash, no error, no empty insight cards claiming specifics

Pass criteria: Empty input handled gracefully end-to-end.

---

**TC-E2: Very large export (10,000+ conversations)**

Steps:
1. Upload `test-chatgpt-large.zip` (10,000+ conversations, likely 500MB+)

Expected:
- Upload completes (may be slow, should show progress indicator)
- Processing begins and completes (may take longer, timeout fallback activates if >5 min)
- Step 2 counts are accurate (exactly 10,000 or actual count)
- Step 3 insight cards still appear (not stalled waiting for full completion)
- Step 4 tasks still generate correctly

Pass criteria: Large input does not crash, timeout handled, output still accurate.

---

**TC-E3: Corrupted ZIP file**

Steps:
1. Upload `test-corrupt.zip`

Expected:
- Graceful error: "We couldn't read this export. Try re-downloading it from ChatGPT's export page."
- No server error leaked to user
- No partial data stored from the corrupted file
- User can re-upload without refreshing

Pass criteria: See TC-F1-06. Failure message clear and recovery-oriented.

---

**TC-E4: Non-English conversation content**

Steps:
1. Upload `test-nonlatin.zip` (conversations entirely in Japanese, Arabic, Russian, mixed)

Expected:
- Upload and parsing succeed
- Topic extraction still runs (may produce lower-confidence results, but should not error)
- Character counts are correct (not garbled by encoding issues)
- Step 3 insight cards display correctly (no mojibake, no `???` characters)
- RTL language content renders correctly in insight cards if shown

Pass criteria: No encoding errors, no crashes, non-Latin text displays correctly.

---

**TC-E5: Special characters in custom instructions**

Steps:
1. Upload export where custom instructions contain: `'`, `"`, `<`, `>`, `\n`, `\t`, emoji (🚀), RTL text (مرحبا)

Expected:
- Custom instructions stored correctly (special chars preserved, not escaped incorrectly)
- Step 2 preview displays correctly (no raw HTML entities visible to user like `&lt;`)
- No XSS vulnerability (covered in Security section)
- AI partner receives the instructions correctly (not truncated or corrupted)

Pass criteria: All special characters round-trip correctly from upload through display to AI partner.

---

**TC-E6: User refreshes browser mid-migration**

Steps:
1. Begin migration, reach Step 2
2. Refresh the browser (F5 / Cmd+R)

Expected:
- User is returned to Step 2 (or Step 1 at worst) — not sent back to dashboard
- Previously uploaded file data is retained (or user is told to re-upload)
- Upload progress is not reset if file was already processed
- No duplicate processing jobs triggered

Pass criteria: Refresh is survivable. Migration state does not regress to not_started.

---

**TC-E7: User closes browser and returns**

Steps:
1. Begin migration, reach Step 3 (processing actively running)
2. Close the browser completely
3. Wait 2 minutes
4. Re-open browser and log back in

Expected:
- If processing completed during absence: portal shows Step 4 (or migration complete if all steps done)
- If processing still running: Step 3 shown with current progress (not restarted)
- No duplicate processing jobs
- Uploaded temp file is still present if processing is incomplete

Pass criteria: Session resume works. Processing jobs are idempotent.

---

**TC-E8: Same email migrating from multiple competitors**

Steps:
1. Complete migration from ChatGPT (migration_status = 'complete')
2. Attempt to initiate another migration (e.g., from Claude)

Expected:
- Portal either: (a) allows additional migration and merges context profiles, OR (b) shows "Migration already complete — add more tools from Settings"
- Previous migration data is NOT overwritten silently
- User receives clear feedback on what will happen before proceeding

Pass criteria: Second migration is handled explicitly, not silently corrupting first import.

---

## Section 3: Security Tests

**TC-S1: ZIP bomb upload attempt**

Steps:
1. Upload `test-bomb.zip` (compressed to 1MB, decompresses to 1GB+)

Expected:
- Server detects decompression ratio anomaly and rejects
- OR: File size limit prevents the decompressed content from reaching dangerous size
- Error returned to user: "This file appears to be invalid."
- Server CPU/memory is not exhausted by the attempt
- No server crash or slowdown that affects other users

Pass criteria: ZIP bomb neutralized without server impact. Error returned.

Verification: Monitor server CPU/memory during upload. Confirm no service degradation.

---

**TC-S2: Path traversal in ZIP entries**

Steps:
1. Upload `test-traversal.zip` which contains entries named `../../etc/passwd`, `../../var/www/html/index.php`, etc.

Expected:
- ZIP extraction is sandboxed — no file is written outside the designated temp directory
- Entry names with `..` are sanitized or rejected before extraction
- `etc/passwd` is NOT accessible after the upload
- No HTTP error that reveals directory structure

Pass criteria: No file system escape. Temp directory is the only write target.

Verification: After upload, confirm `/etc/passwd` modification time is unchanged. Confirm no new files outside temp directory.

---

**TC-S3: XSS in imported conversation content**

Steps:
1. Upload `test-xss.zip` where conversation messages contain: `<script>alert('xss')</script>`, `"><img src=x onerror=alert(1)>`, `javascript:alert(1)`, SVG payloads

Expected:
- Imported content is stored safely (raw text, not executed)
- When displayed in Step 2 preview or Step 3 insight cards: content is HTML-escaped before render
- No alert() or script execution occurs in browser during any step
- AI partner responses do not execute any injected scripts

Pass criteria: Zero script execution at any point in the flow. `alert()` never fires.

Verification: Use browser DevTools to confirm no unhandled script errors. Inspect DOM to verify entities are escaped.

---

**TC-S4: Non-ZIP file disguised as .zip**

Steps:
1. Upload `test-fake.zip` (a JPEG file renamed to `.zip`)

Expected:
- File type validated by content (magic bytes), not just extension
- Rejection occurs: "This file doesn't appear to be a valid ZIP archive."
- JPEG content is not processed or stored

Pass criteria: Magic byte validation catches the disguised file. Extension-only check is insufficient.

---

**TC-S5: Oversized file upload bypass attempt**

Steps:
1. Attempt to upload a file that exceeds the size limit
2. Also attempt: intercepting the request with a proxy (e.g., Burp Suite) and modifying Content-Length header to bypass client-side check

Expected:
- Server enforces the size limit independently of client-side checks
- Modifying Content-Length does not bypass the limit
- Connection closed or rejected once server detects actual size exceeds limit

Pass criteria: Size limit enforced server-side. Client-side check is defense-in-depth only.

---

**TC-S6: Temp file deletion verification**

Steps:
1. Upload a real ChatGPT ZIP
2. Allow processing to complete
3. Check server temp directory for the uploaded file

Expected:
- The original uploaded ZIP file is deleted from temp storage after processing
- Any intermediate extracted files (`conversations.json`, `user.json`) are also deleted
- Deletion occurs within the time limit specified in spec (max 24 hours — should be much sooner, immediately after processing)

Pass criteria: No uploaded files remain in temp storage after successful processing. Must be verified programmatically, not assumed.

Verification command (run on server after processing):
```bash
# Temp directory should be empty of this user's files
ls -la /tmp/purebrain-migrations/ | grep [user_id]
# Expected: no results
```

---

**TC-S7: OAuth token storage verification**

Scope: Phase 2+ (Notion, HubSpot, Canva OAuth) — include in pre-ship checklist for those integrations.

Steps:
1. Complete Notion OAuth flow
2. Check database directly for OAuth token storage

Expected:
- OAuth access token is NOT stored in the main database in plaintext
- Token is stored in secrets vault only
- Database record contains only a vault reference ID, not the token itself

Pass criteria: Direct database inspection shows no plaintext OAuth tokens.

---

**TC-S8: Upload endpoint authorization check**

Steps:
1. Obtain the file upload endpoint URL
2. Attempt to POST a file to the endpoint without authentication (no session cookie, no auth token)
3. Attempt to POST a file authenticated as User A but with User B's user ID in the request

Expected:
- Unauthenticated request: 401 Unauthorized returned
- Cross-user attempt: 403 Forbidden returned
- Neither attempt processes or stores any file

Pass criteria: Auth enforced on upload endpoint. No unauthenticated uploads possible.

---

**TC-S9: GDPR Right to Erasure**

Steps:
1. Complete a full migration
2. Submit a data deletion request through the portal settings
3. Check all data stores (database, vault, temp storage, AI partner context)

Expected:
- All imported migration data deleted
- `user_context_profile` reset to null/empty
- Migration Complete badge removed
- AI partner no longer references imported history
- Confirmation sent to user

Pass criteria: Deletion is complete and verifiable. AI partner behavior confirms erasure.

---

## Section 4: Responsive and Cross-Browser Tests

### 4.1 Viewport Tests

Run the following at each viewport: 375px, 390px, 768px, 1440px

**TC-R01: Migration banner renders correctly**

Expected at all viewports:
- Banner visible without horizontal scroll
- "Start Migration" and "Skip for now" buttons both tappable/clickable
- Text does not overflow container
- No content cut off or hidden behind other elements

---

**TC-R02: Step 1 upload card renders correctly**

Expected at all viewports:
- Upload button is tappable (minimum 44x44px touch target on mobile)
- "How to export" link is visible and tappable
- Integration cards (Notion, HubSpot, Canva, Other) stack vertically on mobile
- Progress indicator visible at top

---

**TC-R03: File upload on mobile**

Steps (mobile only — 375px and 390px):
1. Tap the upload button on Step 1
2. Observe the file picker that appears

Expected:
- File picker offers both: (a) camera roll / photo library, and (b) file system / Files app
- User can navigate to their Downloads folder to find the exported ZIP
- File picker does not crash or fail to open

Pass criteria: File upload accessible on mobile. Note: camera roll being offered is acceptable — user should see Files option.

---

**TC-R04: Step 2 data review is scrollable on mobile**

Expected at 375px and 390px:
- If data categories exceed viewport height, page is scrollable
- [Remove] buttons remain visible and tappable
- Privacy note visible (may require scroll on small screens — this is acceptable)
- "Start Import" button reachable by scrolling

---

**TC-R05: Step 3 progress display on mobile**

Expected at 375px:
- Progress bar visible at full width
- Insight cards stack vertically (single column)
- Animated orb is smaller but still present
- Checklist items readable

---

**TC-R06: Step 4 task cards on mobile**

Expected at 375px:
- Task cards stack vertically (single column)
- "Start this task" button on each card is full-width and tappable
- "Go to my PureBrain" button is accessible

---

### 4.2 Cross-Browser Matrix

For each of the following: run TC-F1-01 (upload), TC-F2-01 (display), TC-F3-02 (insight cards), TC-F4-01 (personalized tasks), TC-F4-05 (badge).

| Browser | Version | Platform | Expected Status |
|---|---|---|---|
| Chrome | Latest stable | macOS | Full functionality |
| Chrome | Latest stable | Windows | Full functionality |
| Chrome | Latest stable | iOS (via mobile test) | Full functionality |
| Chrome | Latest stable | Android | Full functionality |
| Firefox | Latest stable | macOS | Full functionality |
| Firefox | Latest stable | Windows | Full functionality |
| Safari | Latest stable | macOS | Full functionality |
| Safari | Latest stable | iOS | Full functionality — file upload especially |
| Edge | Latest stable | Windows | Full functionality |

**Known Safari risks to verify specifically:**
- File upload API behavior (Safari has historically had quirks with file input)
- Progress bar CSS (may require vendor prefixes)
- Animated orb (WebGL/CSS animation compatibility)

---

## Section 5: Performance Tests

**TC-P1: Upload time for 100MB file**

Steps:
1. Measure upload time for a 100MB ChatGPT export ZIP
2. Test on a simulated 10Mbps connection (Chrome DevTools Network throttling)

Expected:
- Upload completes within 60 seconds on 10Mbps connection (100MB / 10Mbps ≈ 80s theoretical, UI should show progress)
- Progress indicator is visible during upload (not a blank wait)
- User is not timed out during upload if it takes >30 seconds

Pass criteria: Upload completes, progress shown, no timeout at 30 seconds.

---

**TC-P2: Processing time for 1,000 conversations**

Steps:
1. Time the processing pipeline for an import of exactly 1,000 conversations
2. Record time from "Start Import" click to Step 3 completion

Expected:
- Processing completes within 2 minutes
- If processing takes more than 5 minutes, timeout fallback is triggered (see TC-F3-04)

Pass criteria: 1,000 conversations processed in under 2 minutes. Document actual benchmark.

---

**TC-P3: UI responsiveness during large file parsing**

Steps:
1. Begin processing of `test-chatgpt-large.zip` (10,000+ conversations)
2. During active Step 3 processing, scroll the page, click non-destructive elements, type in text fields

Expected:
- Page remains responsive (scroll smooth, clicks register)
- Browser tab does not become unresponsive ("Page Unresponsive" dialog must not appear)
- Insight cards still animate in as they are generated
- CPU on client device does not peg at 100% (processing is server-side)

Pass criteria: Client remains responsive. Processing is server-side, not blocking main browser thread.

---

**TC-P4: Memory usage during large file parsing (server-side)**

Steps:
1. Upload `test-chatgpt-large.zip` (10,000+ conversations)
2. Monitor server memory during processing

Expected:
- Server memory usage does not exceed a defined ceiling (e.g., 500MB per processing job)
- Memory is released after processing completes (no leak)
- Processing one large import does not degrade performance for other concurrent users

Pass criteria: No memory leak. Memory returns to baseline post-processing. Concurrent user impact is negligible.

---

**TC-P5: Step 3 insight card render performance**

Steps:
1. Watch Step 3 during processing of large import
2. Count time for first insight card to appear

Expected:
- First insight card appears within 15 seconds of "Start Import" click
- User is not staring at a blank Step 3 for longer than 15 seconds
- Subsequent cards animate in smoothly (no layout shift, no janky transitions)

Pass criteria: First card appears within 15 seconds. Animation is smooth.

---

## Section 6: Acceptance Criteria Verification

This section maps each acceptance criterion from the spec to specific test cases. Every criterion has a pass/fail definition.

### Spec: "A migration is complete when..."

| Criterion | Test Case(s) | Pass Definition |
|---|---|---|
| User successfully connects at least one previous tool | TC-F1-01, TC-F1-08 | Upload completes, data visible in Step 2 |
| At least one data category processed and stored in user_context_profile | TC-F3-01, TC-F3-02 | Processing completes, Step 3 shows insights, profile JSON verifiable in DB |
| Step 3 displays at least one personalized insight card (not generic) | TC-F3-02 | Insight card contains data-specific detail (e.g., topic name, count) |
| Step 4 displays at least one personalized task with specific numbers | TC-F4-01 | Task card contains actual conversation count from import |
| AI partner's first response reflects imported context | TC-F4-06 | AI partner mentions at least one item from migration data in first response |
| Uploaded files deleted from temporary storage | TC-S6 | Server-side temp directory verified empty post-processing |
| Migration Complete badge appears in dashboard | TC-F4-05 | Badge visible in dashboard with correct data, persists across sessions |

---

### Spec: "A migration flow is production ready when..."

| Criterion | Test Case(s) | Pass Definition |
|---|---|---|
| Full ChatGPT export flow works end-to-end with real ZIP | TC-F1-01, TC-F2-01, TC-F3-02, TC-F4-01 | All 4 steps complete with real ChatGPT export, no failures |
| All uploaded files confirmed deleted after processing | TC-S6 | Verified programmatically on server |
| OAuth tokens stored in vault (not database) | TC-S7 | Database inspection shows no plaintext tokens |
| User can remove any data category | TC-F2-03, TC-F2-04 | Remove works, removed data not included in processing |
| Privacy note visible on Step 2 above the CTA | TC-F2-05 | Privacy note visible without requiring scroll on 1440px viewport |
| "How to export" instructions accurate and current | TC-F1-02, TC-F1-03 | Manual verification against actual ChatGPT and Claude export UI as of ship date |
| Mobile layout tested at 375px, 390px, 768px | TC-R01 through TC-R06 | All mobile viewports pass their respective tests |

---

## Section 7: Test Execution Sequence

### Phase A — Foundation (Before UI Exists, Backend Only)

These tests can run against the backend API directly:
- TC-S1 (ZIP bomb) — test upload endpoint directly
- TC-S2 (path traversal) — test upload endpoint directly
- TC-S4 (magic byte validation) — test upload endpoint directly
- TC-S5 (size limit bypass) — test upload endpoint directly
- TC-S8 (auth enforcement) — test upload endpoint directly
- TC-S6 (temp file deletion) — test via API + server inspection
- TC-P2 (processing time) — test via API
- TC-P4 (memory usage) — test via API with monitoring

### Phase B — UI Integration (After Step 1-2 Built)

- TC-F1-01 through TC-F1-10 (all upload tests)
- TC-F2-01 through TC-F2-06 (all data review tests)
- TC-F-BANNER-01 through TC-F-BANNER-04 (banner tests)
- TC-E1 through TC-E5 (edge cases that apply to upload/display)
- TC-R01 through TC-R06 (responsive tests for steps 1-2)

### Phase C — Processing Pipeline (After Step 3 Built)

- TC-F3-01 through TC-F3-05 (processing display tests)
- TC-P1 (upload time)
- TC-P3 (UI responsiveness)
- TC-P5 (first insight card time)
- TC-E2 (large file test — processing phase)

### Phase D — Full Flow (After Step 4 Built)

- TC-F4-01 through TC-F4-06 (task tests)
- TC-F-BANNER-03 (migration complete badge)
- TC-E6 (browser refresh mid-migration)
- TC-E7 (browser close and return)
- TC-E8 (multi-competitor migration)
- TC-S3 (XSS in conversation content — tests display in steps 2-4)
- TC-S5 (oversized file — end-to-end test)
- TC-S9 (GDPR deletion)
- All cross-browser tests (TC cross-browser matrix)

---

## Section 8: Bug Severity Classification

| Severity | Definition | Example |
|---|---|---|
| P0 — Blocker | Portal cannot be used at all. Data loss. Security breach. | ZIP bomb crashes server. Path traversal executes. |
| P1 — Critical | Core migration flow broken for majority of users. | Valid ChatGPT ZIP rejected. Step 3 never completes. Tasks are all generic. |
| P2 — Major | Important feature broken or major usability issue. | Remove button doesn't work. Privacy note missing. Mobile upload broken. |
| P3 — Minor | Small usability issue, doesn't block core flow. | Progress percentage stuck briefly. Orb animation missing on one browser. |
| P4 — Enhancement | Cosmetic or improvement request. | Insight card copy could be more specific. Transition animation could be smoother. |

**Ship gate**: Zero P0 or P1 issues. All P2 issues triaged with owner and timeline. P3/P4 tracked but do not block ship.

---

## Section 9: Out of Scope (Deferred to Phase 2+)

The following are explicitly excluded from this test plan. They will be added when the features ship:

- Notion OAuth integration testing
- HubSpot OAuth integration testing
- Canva brand kit OAuth testing
- Gemini/Google OAuth testing
- Real-time processing status via WebSocket
- "Migration Summary" PDF download
- Selective reimport (adding more tools after initial migration)
- TC-S7 (OAuth token vault verification) — only becomes relevant when OAuth integrations ship

---

## Verification

This test plan was created and verified before the portal ships.

Verification checklist:
- [x] All 4 spec steps covered (banner, Step 1, Step 2, Step 3, Step 4)
- [x] All edge cases from task list included
- [x] Security tests cover all vulnerabilities named in task list
- [x] All 4 viewport sizes covered
- [x] All 4+ browsers covered
- [x] Performance tests cover upload time, processing time, UI responsiveness, memory
- [x] Each acceptance criterion from spec mapped to test case(s) with pass/fail definition
- [x] MVP scope delineated (Phase 1 only) — no testing of Phase 2+ features not yet built
- [x] Test data required is fully specified so QA environment can be prepared

---

## Memory Written

Path: `.claude/memory/agent-learnings/qa-engineer/2026-02-23--ai-migration-portal-qa-plan.md`
Type: teaching
Topic: AI Migration Portal QA test plan — patterns and risks for file upload + personalization features

Key learnings:
- Migration portals have a unique trust failure mode: the feature premise ("we know you") makes any generic output a broken promise, not just a bug
- File upload security requires four independent controls: size limit, MIME type (magic bytes), ZIP bomb detection, path traversal prevention — none of these subsume the others
- Personalization tests must be falsifiable: "task contains specific count from import" is testable; "task feels personalized" is not
- Temp file deletion must be verified programmatically on server, never assumed
- The 5-minute timeout with email fallback in Step 3 requires its own test path (TC-F3-04) — processing time variance is a product problem, not just a performance problem
- Non-English content testing is frequently skipped and frequently breaks (encoding, RTL, topic extraction)
