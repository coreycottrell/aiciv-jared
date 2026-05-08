# Home Experiment UX Clone Deployed (2026-04-15)

**Type**: operational
**Topic**: Cloned purebrain.ai homepage to `/home-experiment/` with 7 UX quick wins from audit

## What happened
Jared approved cloning the production home (`exports/cf-pages-deploy/index.html`, 16,359 lines, 644KB)
to `exports/cf-pages-deploy/home-experiment/index.html` for UX experimentation without
touching production. Applied 7 quick wins from overnight UX audit.

## Key learnings

### Pages project ownership matters for deploy URLs
- `purebrain.ai/*` is served by the **`purebrain-production`** project, NOT `purebrain-staging`.
- `staging.purebrain.ai/*` is served by **`purebrain-staging-new`** (separate project).
- `cf-deploy.py` defaults to `CF_PAGES_PROJECT=purebrain-staging` which lives at
  `https://purebrain-staging.pages.dev/*`.
- So deploying `home-experiment/index.html` with default settings puts it at
  `https://purebrain-staging.pages.dev/home-experiment/` — **NOT** at `purebrain.ai/home-experiment/`.
- When Jared asks for a path under `purebrain.ai/*`, must deploy to `purebrain-production` explicitly.

### Cloudflare purge API quirk
- The call `{"purge_everything": false, "prefixes": [...]}` fails with code 1092 because the API
  rejects `purge_everything` together with any other selector.
- Correct form: `{"prefixes": ["purebrain.ai/home-experiment"]}` (no `purge_everything` key at all).

### Image CLS fix pattern
- Added width/height to 34 `<img loading="lazy">` tags lacking dimensions via regex sub.
- Pattern: match `<img[^>]*loading="lazy"[^>]*>`, skip if already has width/height, else append
  default `width="800" height="800"`. Browsers still use CSS sizing; the attrs just provide
  aspect-ratio hint to prevent CLS.

### Section swap via Python
- To move testimonials before "What Happens Next", found both blocks by comment markers
  (`<!-- WHAT HAPPENS NEXT -->` and `<!-- TESTIMONIALS -->`), located their `<section>` open
  and `\n    </section>` close, then reassembled: before + testi + between + timeline + rest.
  Much safer than sed for nested HTML.

## Files
- Clone: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/home-experiment/index.html`
- Backup: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html.bak-2026-04-15-pre-experiment`
- Edit script: `/tmp/apply_ux_experiment.py`
- Deployment ID: `8e1269d0-c88c-4998-b597-d86eb49bf1ab`
- Live URL: `https://purebrain-staging.pages.dev/home-experiment/`

## 7 Quick Wins applied
1. Single-CTA gate (email-first form replaces "Awaken Your PURE BRAIN" button)
2. `@media (prefers-reduced-motion: reduce)` CSS
3. Sticky skinny nav (brand + 4 anchor links + Start CTA)
4. Section order flip (testimonials before "What Happens Next")
5. Marquee → static 5-item trust strip
6. Skip-to-main-content link (visually hidden until focused)
7. width/height attrs on 34+ `<img>` tags

Payment pipeline (58 PayPal references) intact per Jared's rule.
