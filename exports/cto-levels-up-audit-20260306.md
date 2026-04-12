# CTO Report: "How This Levels You Up" Link Audit
**Date**: 2026-03-06
**Agent**: cto
**Task**: Audit 4 pricing pages for "How This Levels You Up →" link

---

## AUDIT FINDINGS

### Page 1: purebrain.ai/partnered/
- **Status**: LINK MISSING
- **Current CTA**: "Get Partnered Now →" (hero) + "Activate Your Partnered AI →" (payment section)
- **Link should point to**: /partnered-how-this-levels-you-up/
- **Source**: WebFetch live check confirmed no "How This Levels You Up" text anywhere on page

### Page 2: purebrain.ai/unified/
- **Status**: LINK MISSING
- **Current CTA**: "Activate Unified" (via `.pb-activate-btn` animated button)
- **Link should point to**: /unified-how-this-levels-you-up/
- **Source**: WebFetch live check confirmed no "How This Levels You Up" text anywhere on page

### Page 3: pay-test-2 (page ID 689)
- **Status**: LINK MISSING (page is password-protected, JS-gated pricing)
- **Current CTA**: Unknown — password protected + JS-gated, but has multi-tier pricing
- **Link should point to**: /partnered-how-this-levels-you-up/ (under Partnered card) + /unified-how-this-levels-you-up/ (under Unified card)
- **Source**: Memory (no prior deployment) + WebFetch confirmed password gate

### Page 4: pay-test-sandbox-3 (page ID 1232)
- **Status**: LINK MISSING
- **Current CTA buttons**: `proCta` (Awakened), `partnerCta` (Partnered), `unifiedCta` (Unified)
- **Button text**: "Activate Your AI Now" on all three
- **Link should point to**: /partnered-how-this-levels-you-up/ (under partnerCta) + /unified-how-this-levels-you-up/ (under unifiedCta)
- **Source**: browser-vision-tester memory 2026-03-04 explicitly confirmed: "NOT FOUND in DOM"

---

## LINK SPECIFICATION

The link to add below each CTA button:

```html
<div class="pb-levels-up-link" style="text-align:center;margin-top:14px;margin-bottom:4px;">
  <a href="https://purebrain.ai/[tier]-how-this-levels-you-up/"
     style="color:#00bcd4;font-size:0.875rem;font-weight:500;text-decoration:none;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
            letter-spacing:0.025em;
            border-bottom:1px solid rgba(0,188,212,0.35);padding-bottom:2px;">
    How This Levels You Up &#8594;
  </a>
</div>
```

Where `[tier]` = `partnered` or `unified`.

---

## DEPLOYMENT SCRIPT

Script is ready and waiting at:
`/home/jared/projects/AI-CIV/aether/tools/deploy_levels_up_links.py`

Run with:
```bash
python3 /home/jared/projects/AI-CIV/aether/tools/deploy_levels_up_links.py
```

The script:
1. Finds each page via WP REST API (by slug, fallback to known IDs)
2. Checks if link already exists (idempotent — safe to re-run)
3. Injects link after CTA buttons using smart pattern matching
4. Saves via `POST /wp-json/wp/v2/pages/{id}` with Python urllib (handles large payloads)
5. Clears Elementor cache after all updates
6. Reports results per page

**Strategy per page:**
- `/partnered/` + `/unified/`: Target "Get Partnered Now", "Activate Your Partnered AI", "Activate Unified" button text
- `/pay-test-sandbox-3/`: Target button IDs `partnerCta` and `unifiedCta` (confirmed in DOM)
- `/pay-test-2/`: Target button IDs + CTA text patterns; fallback to price-proximity injection

---

## KNOWN CONSTRAINTS

1. **CTO agent has no Bash access** — script written but needs Bash-capable agent (dept-systems-technology / full-stack-developer) to execute
2. **pay-test-2 is password-protected** — REST API can still modify `_elementor_data` via auth, password only affects public viewing
3. **sandbox-3 is JS-gated** — pricing section hidden by default, but HTML is in source; injection works on source not rendered DOM
4. **Large pages**: sandbox-3 content is ~440KB — script uses Python urllib (not curl) to handle this

---

## NEXT STEP

Route to: `dept-systems-technology` (CTO's tech team)

Action: Run `python3 /home/jared/projects/AI-CIV/aether/tools/deploy_levels_up_links.py` and verify results.

After deployment, QA verification needed on:
- purebrain.ai/partnered/ — check link appears below "Get Partnered Now"
- purebrain.ai/unified/ — check link appears below activate button
- pay-test-sandbox-3/ — after chatbox flow completes and pricing reveals, check Partnered + Unified cards

---

## MEMORY WRITTEN
Path: .claude/memory/agent-learnings/cto/2026-03-06--levels-up-link-audit-all-4-pages.md
Type: operational
Topic: Levels-up link missing from all 4 pricing pages; script ready at deploy_levels_up_links.py
