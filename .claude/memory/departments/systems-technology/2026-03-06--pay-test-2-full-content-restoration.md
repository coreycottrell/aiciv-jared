# Memory: pay-test-2 (page 689) Full Content Restoration

**Date**: 2026-03-06
**Agent**: dept-systems-technology
**Type**: incident-response + gotcha + pattern
**Tags**: purebrain, pay-test-2, page-689, elementor, content-restoration, paypal, subscription

---

## Incident Summary

pay-test-2 (page 689) had TWO distinct problems:
1. Calculator CTA section (widget id=bb51444) was contaminating the page (visible below pricing)
2. The `_elementor_data` had been SEVERELY TRUNCATED from 491KB → 127KB (content corruption, not just password)

**Root cause of truncation**: Unknown at time of repair — content was overwritten with a shortened version between the March 3 backup and today (March 6). The truncated version had the same section structure (5 sections) but the main widget (292c72a) was only 107KB instead of the original ~370KB.

---

## What Was in the Corrupted State

- 5 sections, same IDs as original
- Main widget (292c72a): 107KB (only post-payment chat flow, missing pre-payment pricing/PayPal code)
- Calculator CTA section (bb51444): present with wrong content
- No PayPal client ID in truncated content
- No subscription plan IDs
- No pricing cards or tier selection UI

---

## Restoration Path

**Source**: `/home/jared/projects/AI-CIV/aether/exports/backup_page_689_pre_clone.json` (2026-03-03, 743KB)

**Steps**:
1. Load backup `_elementor_data` (489840 chars, 5 sections)
2. Remove calculator CTA section (id=bb51444) — was intentionally contaminating page
3. Deploy to page 689 via REST API (payload: 512968 chars — requires Python urllib or file-based curl)
4. Clear Elementor cache: DELETE /elementor/v1/cache (returns empty 200 body — normal)
5. Set password: `PureBrain.ai253443$$$` on pages 689, 688, 1232

---

## PayPal Audit Results (page 689)

| Item | Value |
|------|-------|
| SDK approach | USE_SDK_APPROACH = true |
| Live client ID | AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI |
| SDK URL | www.paypal.com/sdk/js (live, not sandbox) |
| Payment type | Subscription-only (createSubscription) |
| createOrder present | YES — but only as fallback for tiers with empty plan_id |
| Plan IDs (all filled) | Awakened: P-1AG936074F0953120NGLTFKY |
| | Bonded: P-2SA65600MT088594TNGLTFKY |
| | Partnered: P-3VH43554A66001716NGLTFKY |
| | Unified: P-43A28944XN5237411NGLTFLA |
| vault=true | YES |
| Sandbox references | NONE |

**Key**: Because all 4 tier PLAN_IDS are populated, createSubscription is used for ALL tiers. The createOrder code path only triggers for tiers with an empty plan_id string — none are empty. The page IS subscription-only as Jared requires.

---

## Verification Checklist (6/6 PASS)

- [x] Live PayPal client ID present
- [x] Calculator contamination removed
- [x] Subscription plan IDs present (all 4 tiers)
- [x] createSubscription confirmed
- [x] CTA buttons / pricing UI present
- [x] Post-payment chatbox (initPayTestFlow) present

---

## Page State After Restoration

| Page | ID | Password | Data Size | Status |
|------|----|----------|-----------|--------|
| pay-test-2 | 689 | PureBrain.ai253443$$$ | 487KB | RESTORED |
| pay-test-sandbox-2 | 688 | PureBrain.ai253443$$$ | 127KB | Has calculator CTA (needs audit) |
| pay-test-sandbox-3 | 1232 | PureBrain.ai253443$$$ | 125KB | Has calculator CTA (needs audit) |

**Note**: Pages 688 and 1232 still have calculator CTA in their elementor data and are also truncated. They were NOT restored from backup in this session — only password was set. Page 688 should be cloned from 689 again (replacing live client ID with sandbox) to get full content.

---

## Critical Technical Notes

### Large payload deployment
- Payloads >100KB hit curl ARG_MAX limit
- Solution: write payload to file, use `--data-binary @/tmp/file.json`
- Or use Python urllib (preferred for >500KB payloads)

### Elementor cache
- Must DELETE /elementor/v1/cache after updating _elementor_data
- Returns empty 200 body (not JSON) — do NOT try to parse
- Cache clear requires Aether app password, not login password

### Content integrity verification
- Always check `len(_elementor_data)` matches expected size (489KB for full page 689)
- A suddenly-small elementor_data (127KB) = content corruption, not just display issue
- Backup files in `/exports/backup_page_*.json` are the recovery source

---

## Backup Files Available

| File | Date | Size | Notes |
|------|------|------|-------|
| backup_page_689_pre_clone.json | 2026-03-03 | 743KB | BEST — most recent full state |
| backup_page_689_elementor_data_2026-02-28-video-move.json | 2026-02-28 | 511KB | Pre-March content |
| backup_page_689_pre_pricing_rollout.json | 2026-03-03 | 744KB | Same era as pre_clone |
| package-test-2/page689_elementor_data.json | 2026-02-22 | 440KB | Old extraction |
