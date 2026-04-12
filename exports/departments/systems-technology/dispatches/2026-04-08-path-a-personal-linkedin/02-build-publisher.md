# Wave 1b: BUILD - Python Social Publisher Service

**Agent**: full-stack-developer
**Wave**: 1 of 4 (BUILD -> SECURITY -> QA -> SHIP)
**Priority**: P1 CRITICAL - SHIP TODAY
**From**: dept-systems-technology
**Date**: 2026-04-08

## Objective

Build a Python long-running poller that fires scheduled LinkedIn posts through the new `/api/linkedin/post-with-image` Worker endpoint.

## File to Create

`/home/jared/projects/AI-CIV/aether/tools/social_publisher.py`

## Behavior Spec

- Poll `https://surf.purebrain.ai/social/scheduled` every 60 seconds
- For each post where:
  - `auto_publish == True`
  - `status == "approved"`
  - `scheduled_time <= now()` (UTC)
  - `linkedin_post_url` is empty/null
  
  Fire through the apex Worker:

```python
response = requests.post(
    "https://apex.purebrain.ai/api/linkedin/post-with-image",
    headers={
        "X-Internal-Auth": INTERNAL_AUTH_TOKEN,
        "Content-Type": "application/json",
    },
    json={"text": post["content"], "image_url": post["banner_url"]},
    timeout=30,
)
```

On success: `PATCH`/`PUT` back to the social schedule endpoint with:

```json
{
  "status": "published",
  "publish_status": "published",
  "linkedin_post_url": "<post_url>",
  "updated_at": "<ISO8601>"
}
```

On failure: log to `logs/social_publisher.log`, send Telegram alert, do NOT mark published, do NOT retry in the same cycle (next cycle will retry naturally).

## Safety Features (ALL REQUIRED)

1. **Idempotency**: skip any post where `linkedin_post_url` is already set (belt + suspenders)
2. **Rate limit**: max 5 posts/hour tracked locally in a small JSON state file at `/home/jared/projects/AI-CIV/aether/.social_publisher_state.json`
3. **Kill switch**: check for file `/home/jared/projects/AI-CIV/aether/.social_publisher_disabled` at the top of each cycle; if present, sleep and skip the cycle entirely
4. **Dry run**: `--dry-run` CLI flag that logs the intended POST but does not fire
5. **Logging**: structured logs (timestamp, level, post_id, action, result) to `/home/jared/projects/AI-CIV/aether/logs/social_publisher.log` via rotating handler (10MB, 5 backups)
6. **Secret loading**: read `INTERNAL_AUTH_TOKEN` from `.env` via `python-dotenv`, never hardcode
7. **Signal handling**: graceful shutdown on SIGTERM/SIGINT (finish current cycle, then exit)
8. **Error isolation**: one failing post must not crash the loop; wrap per-post logic in try/except

## Telegram Alert Helper

Reuse existing pattern from codebase:

```python
import json, urllib.request

def telegram_alert(msg: str):
    try:
        with open("/home/jared/projects/AI-CIV/aether/config/telegram_config.json") as f:
            token = json.load(f)["bot_token"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": "548906264", "text": msg}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass  # never let telegram failures break the loop
```

## CLI Interface

```
python3 tools/social_publisher.py              # normal run
python3 tools/social_publisher.py --dry-run    # simulate only
python3 tools/social_publisher.py --once       # single cycle then exit (for cron/debug)
```

## Constraints

- Python 3 stdlib + `requests` + `python-dotenv` only. No heavy deps.
- Must be systemd-friendly (no daemonization, foreground process)
- Logs to file AND stdout (systemd captures stdout)
- Must handle `surf.purebrain.ai` being temporarily down (log, continue)

## Deliverables

1. `tools/social_publisher.py` fully implemented
2. Sample log output showing one dry-run cycle
3. State file schema documented at the top of the file
4. Memory written to `.claude/memory/agent-learnings/full-stack-developer/2026-04-08--social-publisher-service.md`

## Verification Required

- Run `python3 tools/social_publisher.py --dry-run --once` and show the output
- Show the logs directory has the new log file
- Confirm no secrets leaked in the log
