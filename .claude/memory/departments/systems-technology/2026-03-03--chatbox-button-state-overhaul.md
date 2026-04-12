# Systems & Technology Memory
## Task: Post-Payment Chatbox Button State Overhaul
**Date**: 2026-03-03
**Pages**: 1232 (pay-test-sandbox-3), 688 (pay-test-2), 689 (pay-test-sandbox-2)
**Status**: COMPLETE — All PASS

---

## What Was Done

### Change 1 (All 3 pages)
Text replacement in BOTH `content.raw` AND `meta._elementor_data`:
- Old: `a button will appear here`
- New: `the button below will light up.`

### Change 2 (Page 1232 only — Brain Stream button section)
Replaced CSS/JS so the button:
1. Starts visible but greyed out (was `display: none`)
2. Lights up with PT Blue/Orange blink animation when magic link arrives
3. Is NOT clickable until activated

**CSS Changes:**
- `#pb-brain-stream-wrapper`: `display: none` -> `display: block; opacity: 0.35; filter: grayscale(0.7) brightness(0.6); pointer-events: none`
- `#pb-brain-stream-wrapper.pb-bs-active`: `opacity: 1; filter: none; pointer-events: auto`
- `#pb-brain-stream-btn` (default): `background: #333333; cursor: not-allowed; pointer-events: none`
- `.pb-bs-active #pb-brain-stream-btn`: Activates with `pb-bs-blink` + `pb-bs-pulse` animations
- `@keyframes pb-bs-blink`: Alternates between PT Blue (#2a93c1) and PT Orange (#f1420b)
- `@keyframes pb-bs-pulse`: Updated to use PT Blue/Orange instead of amber

**JS Changes:**
- `showBrainStreamButton()`: Replaced `wrapper.style.display = 'block'` + opacity/transform manipulation with `wrapper.classList.add('pb-bs-active')`
- URL assignment and AI name update preserved
- `scrollIntoView` timing changed from 450ms to 300ms

---

## Key Technical Findings

### Pages 688 and 689 use a DIFFERENT button system
- `#pb-brain-stream-wrapper` exists ONLY on page 1232
- Pages 688/689 use `ptc-portal-btn` / `ptc-portal-placeholder` system
- Brain Stream CSS/JS changes do NOT apply to 688/689

### String matching in _elementor_data
- `_elementor_data` stores JS as JSON-within-JSON
- Newlines appear as literal `\n` (backslash-n, 2 chars), NOT actual newlines
- In Python source, write `'\\n'` to match (which produces a 2-char sequence)
- Verified by: `repr(elem_data[idx:idx+40])` showing `\\n` in the repr output

### Critical deployment pattern
1. Back up all pages FIRST (full JSON from `?context=edit`)
2. Modify BOTH `content.raw` AND `meta._elementor_data`
3. Push via POST to `/wp-json/wp/v2/pages/{id}` with `json={"content": ..., "meta": {"_elementor_data": ...}}`
4. Clear Elementor cache: `DELETE /wp-json/elementor/v1/cache`
5. Verify by fetching page again and checking both fields

---

## Backup Location
`/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/backup-2026-03-03-chatbox-button/`
- `page-1232-backup.json`
- `page-688-backup.json`
- `page-689-backup.json`
- `apply-chatbox-changes.py` (the deployment script)
