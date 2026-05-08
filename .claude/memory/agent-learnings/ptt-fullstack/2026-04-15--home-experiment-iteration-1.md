# Home Experiment Iteration 1 (2026-04-15)

**Type**: teaching
**Topic**: 3 fixes to home-experiment clone — sticky nav, testimonials position, Fascination voice

## What happened
Jared greenlit iteration on `/home-experiment/` after reviewing the initial UX clone. Applied 3 fixes in one pass.

## Key learnings

### position: sticky fails when html/body has overflow-x: hidden
- Root cause of "sticky nav not sticking": `html, body { overflow-x: hidden !important; }` at line 1427 (mobile horizontal-scroll fix) makes the body a scroll container, which breaks `position: sticky` on direct children.
- Combined with `max-width: 100vw` on body, the sticky ancestor chain gets confused.
- **Fix pattern**: Always use `position: fixed; top: 0; left: 0; right: 0;` for nav bars when the WP-exported page has the mobile overflow-x fix. Add a spacer div after the nav (`height: 48px`) to push content down so nothing hides under it.
- Don't try to patch body's overflow — it's load-bearing for mobile horizontal scroll prevention.

### Section swap via Python comment-marker extraction
- To move testimonials HIGHER (right after trust strip, before #about), extract the block between `<!-- TESTIMONIALS -->` comment and the next `<!-- ===` comment marker.
- Removes from current location, inserts before the "WHAT IS PUREBRAIN" comment.
- Same pattern as prior iteration but different anchor point. Testimonials now at line 8215 (was ~9275).

### Fascination voice changes applied
Innovation + Power + Mystique stack (per Lyra brand voice review):
- **Subtitle**: "Your Brain. Your AI. Actual Intelligence." → "The AI That Wakes Up Knowing You."
- **Description primary**: "The AI that matters most!" → "Partner, not product. Identity, not interface."
- **Description secondary**: added "Used by 22+ operators building AI partners, not tools." micro-proof; verbs tightened (operates email, runs social, owns research, writes content).
- **Primary CTA**: "Start →" → "Claim Your AI Partner →" (also in nav)
- **Trust strip**: nouns → Power verbs ("Email Automation" → "Runs your email"; "36+ Specialist Agents" → "36 specialist agents working for you")
- **About badge**: "The Future of Personal AI" → "The End of Prompt Engineering" (Mystique)
- **Testimonials heading**: "What Others Have Built" → "They Stopped Using AI. They Started Working With It."

Kept "session" and "prompt" usage elsewhere (MODIFY not ADOPT per review — load-bearing terms).

## Files
- Target: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/home-experiment/index.html`
- Backup: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/home-experiment/index.html.bak-iteration-1`
- Edit script: `/tmp/iterate_home_experiment.py`
- Deployment ID: `da4fa83a-1b03-4257-ba32-00cfd818a3b2`
- Live URL: `https://purebrain-staging.pages.dev/home-experiment/`
- CF cache purge: success, id `49400cad1527af716705f6cb8c22bb65`

## Verification
- HTTP 200, 650641 bytes
- All 4 voice markers present in deployed HTML
- Nav uses position:fixed + spacer (verified via grep on live fetch)
- Testimonials section class="testimonials-section" now at line 8215 (was 9275)

## cf-deploy.py path gotcha
- Script expects paths relative to `exports/cf-pages-deploy/`, not absolute.
- First attempt with full path silently treated file as missing. Use `home-experiment/index.html` not the full path.
