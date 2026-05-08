# Duo Chat Product Build

**Date**: 2026-04-16
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

5-file Duo Chat product package at `/home/jared/projects/AI-CIV/aether/exports/duo-chat/`:

1. **duo-widget.html** — Self-contained chat widget (HTML/CSS/JS), fully parameterized via `data-*` attributes or `window.DUO_CONFIG`. All v10 features: pin, bookmark, reactions, collapse, copy, reply, search, scroll-to-bottom, markdown rendering, code blocks, drag-drop.

2. **duo_injector.py** — Python poller for AI containers. Reads `~/duo/duo-config.json`, polls trio-comms worker every 20s, injects new messages via 5x Enter tmux protocol.

3. **post-to-duo.sh** — Bash CLI for posting messages. Uses python3 `json.dumps` for proper newline handling.

4. **duo-config-template.json** — Config template with 5 required fields.

5. **SETUP-README.md** — Step-by-step setup guide for birth pipeline.

## Key Architecture Decisions

- **Reuses trio-comms worker as-is** — duo_id maps to the existing trio_id column in D1. No worker changes needed.
- **Auto-detects participants** from message sender_id field. No hardcoded names anywhere.
- **Color assignment is dynamic** — participants get colors from a palette in order of appearance.
- **All CSS/JS prefixed with `dw-`** (duo widget) to avoid conflicts with trio `tw-` prefix when both exist on same page.
- **Portal user alignment** controlled by `DUO_CONFIG.my_id` — that sender's messages appear on the right.
- **localStorage keys scoped by duo_id** so pins/bookmarks/reactions don't collide across customers.

## Patterns Learned

- When stripping a complex widget to generic: rename ALL prefix (tw -> dw), search for hardcoded names, keep the rendering pipeline identical but parameterize the data source.
- The trio-comms worker's `trio_id` parameter already enables multi-tenancy — no new endpoints needed. Just pass `trio_id={duo_id}` on every request.
