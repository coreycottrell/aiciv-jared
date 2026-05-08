# Full Site Audit — purebrain.ai
**Date**: 2026-04-17 11:25 UTC
**Auditor**: Aether

## WORKING PAGES (confirmed serving real content)

| Page | Title | Status |
|------|-------|--------|
| `/` (homepage) | PURE BRAIN - Your Brain. Your AI... | OK |
| `/insiders/` | Insiders Only | OK |
| `/awakened/` | Awaken Yours Today! | OK |
| `/partnered/` | Awaken Yours Today! | OK |
| `/unified/` | Awaken Yours Today! | OK |
| `/refer/` | Refer & Earn | OK |
| `/blog/` | The Neural Feed – Blog | OK |
| `/blog-neural-feed-memories/` | The Neural Feed Memories | OK |
| `/thank-you/` | Welcome to the Partnership | OK (but magic link poller shows NOT_READY for Joseph — Witness issue, not deploy issue) |
| `/ai-tool-stack-calculator/` | Free Software Tool Stack Calculator | OK |
| `/investor-intelligence/` | Investor Intelligence — The Age of AI Agents | OK (JUST RESTORED) |
| `/pitch-v2/` | PureBrain.ai Series A Investor Pitch Deck | OK (JUST RESTORED) |
| `/investment-opportunity/` | Pure Technology — Investment Opportunity | OK (served by WordPress) |
| `/meeting-strategy/` | PureBrain Meeting Architecture v2 | OK (served by WordPress) |

## BROKEN PAGES (serving homepage fallback)

These pages have local files in our CF Pages deploy but are serving the WordPress homepage instead of their own content. They need git-based restoration (same method used for investor-intelligence + pitch-v2).

### Priority 1: Payment Test Pages
| Page | Local File Exists | Action Needed |
|------|------------------|---------------|
| `/home-test/` | YES | Restore via git deploy |
| `/home-test-sandbox/` | YES | Restore via git deploy |
| `/home-test-live-1/` | YES | Restore via git deploy |

### Priority 2: Active Product Pages
| Page | Local File Exists | Action Needed |
|------|------------------|---------------|
| `/brainiac-module-1-foundations/` | YES | Restore via git deploy |
| `/creator/` | YES | Restore — this is creator.purebrain.ai content |
| `/ceo-dashboard/` | YES | Restore |
| `/777-command-center/` | YES | Restore — this is 777.purebrain.ai content |

### Priority 3: Guardian/Avatar Pages
| Page | Local File Exists | Action Needed |
|------|------------------|---------------|
| `/aether-guardian/` | YES | Restore if still needed |
| `/chy-guardian/` | YES | Restore if still needed |
| `/invest/` | YES | Restore if still needed |

### Lower Priority: Old Iterations (may not need restoring)
These are old build iterations. Many were experimental. Review before restoring:

- `/3d-brain/` through `/3d-homepage-v3/` (6 pages) — old 3D experiments
- `/avatar-prototypes/` through `/avatar-v7-gleb/` (8 pages) — avatar iterations
- `/investors-v5-fluid/` through `/investors-v16/` (12 pages) — old investor page versions
- `/homepage-clone-test/`, `/homepage-clone-v2/` — test clones
- `/48-hour-trial/` — old trial page
- `/education-portal/` — old education page
- `/fundraising-plan/` — old fundraising page
- Various client-specific pages (hunden, baystate, billie, duckdive, etc.)

**Total old iterations: ~100+ pages** — recommend NOT restoring unless specifically needed.

## SUMMARY

| Category | Count | Status |
|----------|-------|--------|
| Working correctly | 14 | No action needed |
| Priority 1 (test pages) | 3 | RESTORE NOW |
| Priority 2 (product pages) | 4 | RESTORE SOON |
| Priority 3 (guardians) | 3 | RESTORE IF NEEDED |
| Old iterations | ~100+ | DO NOT RESTORE (unless requested) |

## RECOMMENDED ACTION

1. Restore 3 home-test pages (Priority 1) — needed for payment testing
2. Restore 4 product pages (Priority 2) — active features
3. Ask Jared about Priority 3 before restoring
4. Leave old iterations alone

All restores use the same constitutional git method: one page at a time, verify before next.
