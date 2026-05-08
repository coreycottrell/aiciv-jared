# LinkedIn Posts Log

Running record of scheduled LinkedIn posts + 5-stage SOP telemetry.

**Pipeline stages** (per `docs/LINKEDIN-AUTOMATION-PIPELINE.md`):
1. T-60min — **PRE-COMMENTS** on 3-5 ICP posts (linkedin_icp_commenter.py)
2. T-0    — **MAIN POST** (linkedin_scheduled_poster.py)
3. T+2min — **FIRST COMMENT** on own post (purebrain.ai/?ref=JAREDSB0)
4. T+30min — **POST-COMMENTS** on 3-5 ICP posts
5. T+60min — **REACTIONS** rotation on replies (Support/Celebrate/Insightful/Love, never Like)

Columns:
- `date` (ET)
- `slot` (8:30am / 11am / 1pm / 3pm)
- `title`
- `post_url`
- `pre_comments` (N succeeded / N attempted)
- `first_comment` (ok / fail / skipped)
- `post_comments` (N succeeded / N attempted)
- `reactions` (ok / fail / skipped)
- `notes`

---

| date | slot | title | post_url | pre_comments | first_comment | post_comments | reactions | notes |
|------|------|-------|----------|--------------|---------------|---------------|-----------|-------|
| — | — | (no posts logged yet) | — | — | — | — | — | Log initialized 2026-04-14 |

---

## How it's populated

- `linkedin_scheduled_poster.py` appends a row on every successful post (main post + first-comment)
- `linkedin_icp_commenter.py` appends `pre_comments` / `post_comments` / `reactions` fields when run with the matching slot context (future enhancement — currently logs to `logs/linkedin_icp_commenter.log`)

## Related logs

- `logs/linkedin_scheduled_poster.log` — main post + first-comment telemetry
- `logs/linkedin_icp_commenter.log` — pre/post ICP commenting + reaction telemetry
- `logs/linkedin-comments.log` — legacy comment scheduler (still running every 30min)
