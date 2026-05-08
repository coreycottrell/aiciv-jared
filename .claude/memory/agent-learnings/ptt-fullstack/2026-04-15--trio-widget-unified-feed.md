# Trio Widget — Unified Feed Rebuild (2026-04-15)

**Type**: operational + pattern
**Topic**: Convert 3-panel side-by-side trio chat widget to single unified feed (chat-style)

## Task
Jared greenlit rebuild of trio widget from 3-column side-by-side panels (Aether / Chy / Morphe) to ONE unified message feed where messages from all 3 AIs + Jared appear in chronological order, color-coded by sender, Jared's bubbles right-aligned.

## Spec Implemented
- Single `tw-feed-unified` div replaces 3-panel grid
- Per-sender colors: Aether `#2a93c1`, **Chy `#5fbd5f`** (was `#d4a574`), **Morphe `#a770ef`** (was `#a78bfa`), Jared `#ffffff` right-aligned
- Sender name (bold colored) + EST timestamp + message body in each bubble
- Border color matches sender (alpha 66 hex)
- @mention highlighter: `@aether|@chy|@morphe|@all` rendered with white-on-translucent badge (post-linkify regex)
- Footer hint chip: "Tip: type @aether, @chy, @morphe, or @all"
- Removed 3-row mobile stack media query (single feed already mobile-friendly)
- Shell narrowed: `min(820px, 100%)` (was `min(1400px, 100%)`)

## Files Modified
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/777-command-center/index.html`
  - Lines 9210–9220: TRIO_WIDGET ais colors updated, added `byId` lookup
  - Lines 9251–9302: replaced `twRenderPanel(ai, messages)` with `twRenderUnified(messages)` + `twEmphasizeMentions(html)`
  - Lines 9347–9388: CSS — replaced `.tw-panels`/`.tw-panel*` with `.tw-feed-wrap`, single `.tw-feed`, sender-colored `.tw-msg-meta .tw-sender`, `.tw-hint`
  - Line 9352: shell width 1400→820
  - Lines 9420–9434: HTML — single `<div class="tw-feed-wrap"><div class="tw-feed" id="tw-feed-unified"></div></div>` replaces 3 `.tw-panel` blocks
  - Header dots updated to spec colors
- `/home/jared/purebrain_portal/portal-pb-styled.html`
  - Same conceptual changes, scoped under `#trio-widget-modal` selectors
  - Lines 19165–19177: ais + byId
  - Lines 19215–19281: refresh/render/mentions
  - Lines 19313–19355: scoped CSS rewrite
  - Lines 19361–19400: HTML single-feed

## Backups
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/777-command-center/index.html.bak-trio-unified-20260415` (545 KB)
- `/home/jared/purebrain_portal/portal-pb-styled.html.bak-trio-unified-20260415` (809 KB)

## Deploy
- Portal: `sudo systemctl restart aether-portal.service` → active
- 777: `CF_PAGES_PROJECT=777-command-center python3 tools/cf-deploy.py --base-dir exports/cf-pages-deploy/777-command-center/ index.html` → deployment `2a555789-92af-4087-987f-3b42e919eb42`
- CF cache purged for https://777.purebrain.ai/ + /index.html

## Verification
- `curl https://777.purebrain.ai/` → 4 occurrences of `tw-feed-unified|twRenderUnified` (script, render fn, getElementById, HTML element)
- `curl https://portal.purebrain.ai/` → 4 occurrences (same markers under scoped selectors)
- All zero references to removed `tw-feed-aether|tw-feed-chy|tw-feed-morphe|tw-panels|twRenderPanel` in either file
- Backend untouched — same `/trio/messages` GET + `/trio/message` POST
- All 3 URLs return 200: purebrain.ai (homepage healthy), 777.purebrain.ai, portal.purebrain.ai

## 🚨 INCIDENT (during this task)
**Brief said**: deploy 777 with `CF_PAGES_PROJECT=purebrain-production`. **Reality**: 777 lives at `CF_PAGES_PROJECT=777-command-center` (`777.purebrain.ai`). `purebrain-production` serves `purebrain.ai` (the public homepage).

When I followed the brief literally, I uploaded the 777 dashboard's `index.html` over `purebrain.ai`'s homepage (deployment `4b74eda2-df3a-4252-86ab-05cb07e3e630`). For ~3 minutes purebrain.ai served the 777 dashboard.

**Recovery**:
1. Detected via `curl https://purebrain.ai/ | grep "777 Command Center"` → 3 hits
2. Listed prior deployments: `595fcd46` was the previous prod (Audio fix v4, 22:40 UTC)
3. Rolled back via CF API: `POST /accounts/{acc}/pages/projects/purebrain-production/deployments/595fcd46/rollback` → success
4. Verified `purebrain.ai` title back to "PURE BRAIN - Your Brain. Your AI..."
5. Then deployed 777 to correct project (`777-command-center`)

**Lesson burned in**:
- `purebrain-production` project = `purebrain.ai` ONLY (CONSTITUTIONAL — see MEMORY.md "Deploy targets CORRECTED 2026-04-15")
- `777-command-center` project = `777.purebrain.ai`
- Even when a brief says "deploy to purebrain-production", check `exports/cf-pages-deploy/{folder}/` matches the project. `777-command-center/index.html` is NEVER for `purebrain-production`.
- Always grep live URL after deploy for content fingerprint.
- CF rollback API is fast and clean — use it when wrong content lands prod.

## Pattern Notes
- Unified feed rendering is much simpler than per-panel filtering — no recipient-list logic, just sort + color by sender.
- @mention highlighter runs AFTER `twLinkify()` (which already escapes) — regex matches against escaped HTML safely with `(^|[\s>])` lookbehind alternative.
- Used `byId` map so render is O(1) lookup per message instead of array.find.
- Right-align via `.tw-msg-right` flex `align-self:flex-end`; works for any future "user" sender role too.
- Scoped CSS in portal still required (`#trio-widget-modal .tw-feed`) because portal-pb-styled is 19K lines with many class collisions.

## Cross-Refs
- `2026-04-15--trio-widget-3panel-777.md` — original 3-panel build
- `2026-04-15--trio-widget-portal-injection.md` — portal injection patterns (proxy auth, CSS scoping, IIFE exports)
- MEMORY.md "Deploy targets CORRECTED 2026-04-15" — domain ↔ project map
