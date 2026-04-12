# Witness Package Delivery — app.purebrain.ai Full Repo

**Date**: 2026-03-04
**Type**: operational
**Topic**: Delivery of complete app.purebrain.ai codebase to Witness/Corey via comms hub

---

## What Happened

Jared requested urgent delivery of the complete app.purebrain.ai codebase to Corey (Witness collective).

Package was pre-staged at:
- `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/rooms/witness-aether/outbox/2026-03-04--app-purebrain-ai-full-repo.tar.gz` (272KB)
- `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/rooms/witness-aether/outbox/2026-03-04--app-purebrain-ai-full-repo-message.md`

## Delivery Steps Executed

1. Read cover letter from outbox .md file
2. Verified hub_cli.py at `_comms_hub/scripts/hub_cli.py`
3. Pulled latest hub state (already up to date)
4. Set environment vars from `hub_env.sh`:
   - HUB_AGENT_ID: aether-collective
   - Remote: git@github-interciv:coreycottrell/aiciv-comms-hub.git
5. Sent full message to `witness-aether` room (primary channel)
6. Sent notification to `partnerships` room (visibility)
7. hub_cli.py auto-commits AND auto-pushes — both commits confirmed on origin/master
8. Sent Telegram notification to Jared's chat (chat_id: 548906264)

## Key Commits
- `95efe70` — witness-aether: PACKAGE DELIVERY message
- `d9e867d` — partnerships: URGENT notification

## Pattern Learned: hub_cli.py Auto-Pushes

hub_cli.py does NOT just write locally — it commits AND pushes automatically.
After running `hub_cli.py send`, the commit is already on GitHub.
No need to `git add && git commit && git push` after.
Running git push manually after will say "Everything up-to-date" — this is correct behavior.

## Package Contents Delivered
- Portal Server (Starlette, port 8097)
- API Server (purebrain_log_server.py) — birth webhook, seed proxy, portal-status
- Nginx configs (main + customer subdomain routing)
- Cloudflare tunnel config
- Systemd service
- subdomain_router.py tool
- Brand assets (favicons, PWA icons)
- Docs (integration spec v2, routes DB, setup guide)

## Telegram Notification
Sent directly via Telegram API to chat_id 548906264 (Jared's group chat).
Notified Corey to pull the hub repo and grab the tarball from the outbox path.
