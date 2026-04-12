# Code Archaeology Memory: PureBrain Portal Build

**Date**: 2026-02-24
**Type**: operational
**Topic**: app.purebrain.ai portal codebase technology catalog

## Context

Analyzed `/tmp/app-purebrain-ai/Testing-Purebrain/` — the full portal build
extracted for educational code catalog purposes.

## Architecture Discovery

This is a "tmux bridge" architecture — unique and worth remembering. The gateway
does NOT call any AI API directly. It injects text into a tmux session where a
Claude Code instance is running, captures the terminal output, and serves it to
a web frontend. The AI "thinks" in a persistent terminal. The web layer is just
a window into that terminal.

Key insight: "The gateway is a bridge, not a brain. The AICIV decides."

## Tech Stack Summary

- Backend: Python 3.11, FastAPI + Uvicorn + Gunicorn, Pydantic, stdlib only
- Frontend: Single 13,525-line self-contained HTML file (CSS + JS embedded)
- JS Patches: 3 IIFE-pattern JavaScript files for terminal, artifacts, commands
- Testing: Playwright (Node.js ESM .mjs) + vanilla Python test runner (no pytest)
- Infrastructure: Docker, systemd service, bash deploy script
- Config: JSON-based (aiciv-config.json, aiciv-auth.json)

## Notable Pattern

Multi-AICIV support: one gateway can proxy to up to 10 separate AI instances
via SSH tunnels to different VPS machines, each on a different port.

## File Counts

- .py: 3 files (aiciv_gateway.py=4153 lines, test_webhook.py=381, app.py=3)
- .js: 3 patch files (~2,523 lines total)
- .mjs: 16 test files (8 top-level + 14 spec + helpers + config)
- .html: 1 file (13,525 lines — the entire frontend)
- .json: 3 config files
- .md: 14+ documentation files
- .sh: 1 deploy script
- Dockerfile: 1
- .service: 1 systemd unit
- .env.template: 1

## When To Apply This Knowledge

When analyzing similar "terminal proxy" or "AI bridge" architectures.
When someone asks about headless Claude/AI integration patterns.
Pattern is reusable: tmux + WebSocket + polling = zero-latency AI web portal.
