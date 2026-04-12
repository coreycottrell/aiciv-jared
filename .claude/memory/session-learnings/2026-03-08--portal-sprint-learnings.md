# Session Learnings: March 8, 2026 - Portal Sprint + Multi-Task Delegation

## Key Technical Learnings

### 1. Portal Multi-Image Upload: Timestamp ID Collision
- When multiple files upload within same millisecond, `int(time.time()*1000)` generates duplicate IDs
- Frontend dedup guard silently drops duplicates
- Fix: Add `secrets.token_hex(4)` entropy to IDs and filenames

### 2. Portal File Delivery: 3 Code Path Problem
- Portal HTML has 3 separate rendering paths: addMessage(), startStreamingMessage(), in-place update
- PORTAL_FILE handler was only in addMessage() — files sent live were invisible
- ALSO: parseAiFiles() Mode 3 regex was intercepting PORTAL_FILE tags before the specific handler
- ALSO: File cards were appended at wrong DOM position (before avatar/bubble)
- Fix: Add handler to all 3 paths, scope Mode 3 regex, fix append order

### 3. Nested HTML Documents in Elementor = Mobile Safari Kill
- Elementor widget containing `</body></html>` causes Mobile Safari to close the document
- Desktop browsers are forgiving, mobile strict
- Symptom: sections after the widget are invisible on mobile only
- Best fix: Clone working page content rather than patch nested docs

### 4. _comms_hub is Independent Git Repo
- Can't stage _comms_hub files from aether root (submodule error)
- Must commit inside _comms_hub directly, then for-witness/ separately from aether root

## Delegation Patterns That Worked

- **Parallel background agents**: 3-4 independent tasks running simultaneously (financial model, research, QA, packaging)
- **Sequential dependency**: QA audit waited for fixes → packaging waited for QA → Corey delivery waited for packaging
- **Correction handling**: When Jared corrected "Melissa" → "Melanie", quick edit + resend was appropriate (no need to re-delegate)

## What Jared Reinforced Today
- "YOU ARE co-ceo DELEGATE!!" - Even full-stack work should go through CTO
- "SLOWLY and in background over night" - Space out overnight tasks at 15-min intervals
- "we are slowly leaving telegram completely" - Portal is becoming primary, all files MUST go there
- Financial model was "waaay too conservative" - Think bigger: 1000+ signups in 60 days, $3.5K-$12K enterprise deals

## Overnight Queue
11 tasks saved in `.claude/scratch-pad-overnight-tasks.md` - waiting for Financial Model v2 + PureInfluence to complete first
