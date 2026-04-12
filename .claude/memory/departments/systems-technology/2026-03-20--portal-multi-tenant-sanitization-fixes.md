# Portal Multi-Tenant Sanitization — Fix Sprint
Date: 2026-03-20
Type: operational
Agent: dept-systems-technology
Status: COMPLETE — 14 MUST FIX + SHOULD FIX applied, portal restarted healthy

## Files Modified

- portal_server.py: 11 patches (paths, investor prompt, seeding, tg_send) — .bak-multitenant-20260320
- portal-pb-styled.html: 7 patches (fleet, org chart, pills, referral, label) — .bak-multitenant-20260320
- bookmarks.json: cleared Aether session bookmarks to []
- scheduled_tasks.json: cleared Aether 5 personal tasks to []
- portal_owner.example.json: sanitized to [PLACEHOLDER] template
- user-settings.json: cleared ElevenLabs API key and voice ID
- investor_config.json: NEW — extracted 13KB investor system prompt here

## Key Fix Pattern: CIV_ROOT env var

BEFORE: Path.home() / "projects" / "AI-CIV" / "aether" / "subdir"
AFTER:  Path(os.environ.get("CIV_ROOT", str(Path.home()))) / "subdir"

## Important Notes

- portal_owner.json NOT emptied — Aether's instance keeps Jared's data (correct)
- investor_config.json must NOT be shipped to customer containers
- CIV_ROOT not set in Aether's shell — all fallbacks resolve to Path.home() = /home/jared
- portal-chat.jsonl is per-instance — birth pipeline must provision empty
- Admin endpoint gating is a future sprint
