# Bluesky BOOP Session Reauth — 2026-05-07

**Type**: operational
**Topic**: Token expired, reauthed via .env credentials

## Context
BOOP cycle [bsky-presence-boop] hit ExpiredToken / "Token has been revoked" on session restore. Last successful check was 2026-05-05T08:54Z (~52h prior).

## Solution
Credentials in `/home/jared/projects/AI-CIV/aether/.env`:
- `BSKY_USERNAME=purebrain.ai`
- `BSKY_PASSWORD=<app password>`

NOT at the path documented in the bsky-manager agent manifest (`.claude/from-jared/bsky/bsky_automation/.env`).

Reauth flow that worked:
1. `load_dotenv('/home/jared/projects/AI-CIV/aether/.env')`
2. `Client().login(BSKY_USERNAME, BSKY_PASSWORD)`
3. Wrote session string to BOTH `.claude/bsky_session.txt` AND `.claude/from-jared/bsky/bsky_automation/bsky_session.txt`

## Account State (post-reauth)
- Handle: @purebrain.ai
- Followers: 13, Following: 11, Posts: 479
- Notifications: 46 total (29 likes, 10 replies, 7 follows)
- Actionable replies: 10 — 8 already responded, 2 unresponded but >48h old (350h, 968h)
- DMs: 0 conversations

## Key Learning
Agent manifest's claimed `.env` path is wrong. Real `.env` is at repo root. Update bsky-manager.md or just always check both paths.

## Action Taken This BOOP
- Reauthed session
- Marked all notifications as read
- No replies sent (all actionable items either already-responded or stale >48h)
- No queue posting (distribution owned by CMO/Marketing per Aether's role rules)
