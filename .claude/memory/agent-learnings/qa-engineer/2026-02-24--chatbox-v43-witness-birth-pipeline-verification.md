# QA Memory: Chatbox v4.3 Witness Birth Pipeline Verification

**Date**: 2026-02-24
**Agent**: qa-engineer
**Type**: operational
**Topic**: Chatbox v4.3 deployment verification — pages 688 and 689

---

## What Was Verified

Post-Payment Chat Flow script v4.3 (Witness Birth Pipeline) deployed to:
- Page 688 (sandbox): purebrain.ai/pay-test-sandbox-2/
- Page 689 (live): purebrain.ai/pay-test/

## Verification Method

WP REST API with `context=edit` bypasses CDN cache for authoritative content check.
HTML entities in WordPress raw content require `html.unescape()` before string matching.

## All 8 Checks — BOTH PAGES PASS

1. v4.3 marker present — PASS (found in comment header and inline comments)
2. No sk-ant- API key — PASS (API key flow removed in v4.3)
3. Open Claude Console not in functional code — PASS (appears only in changelog comment documenting what was removed)
4. startData.container present — PASS (server-authoritative containerName fix)
5. runBirthInit present — PASS (moved to Phase 1 after Q4)
6. sanitizeText present — PASS (v4.2 security feature retained)
7. WITNESS_WEBHOOK_HOST = 'https://api.purebrain.ai' — PASS (no http fleet IP)
8. Script size 82,915 chars — PASS (within 82k-83k target range)

## Key Lesson: False Positive on "Open Claude Console" Check

The original check `'Open Claude Console' not in content` returned False (failing) because
the string appears in a changelog comment:
```
* Removed: "Open Claude Console" button (link to platform.claude.com)
```

The correct check is: string exists AND it's only inside a `/* ... */` comment block,
never as functional button/click handler code. Pattern:
```python
occ_in_comment = bool(re.search(r'\*\s+[^\n]*Open Claude Console', main_script))
occ_total = main_script.count('Open Claude Console')
c3 = occ_in_comment and occ_total == 1
```

## Script Structure Note

Page content contains 26 script blocks. The chat flow script is the largest at 82,915 chars.
Multiple smaller scripts exist (PayPal, Elementor, etc.). Always target the 80k+ block
for chat flow verification.

## Outcome

CLEARED FOR SHIP. Both pages verified. Security had pre-approved the build.
