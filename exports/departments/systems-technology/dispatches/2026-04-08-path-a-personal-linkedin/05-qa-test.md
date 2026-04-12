# Wave 3: QA TEST (Live Fire)

**Agent**: qa-engineer
**Wave**: 3 of 4 (BUILD -> SECURITY -> **QA** -> SHIP)
**Priority**: P1 CRITICAL - SHIP TODAY
**From**: dept-systems-technology
**Date**: 2026-04-08
**Blocked by**: Wave 2 security APPROVED verdict
**Blocks**: Wave 4 (remaining Apr 9 posts)

## Objective

Validate the deployed Worker endpoint and social publisher with a LIVE fire on today's 88% post.

## Prerequisites (verify before starting)

- [ ] Security verdict = APPROVED (read `SECURITY-REVIEW.md`)
- [ ] Worker deployed (Jared ran `npx wrangler deploy`)
- [ ] `INTERNAL_AUTH_TOKEN` secret set in Worker AND `.env`
- [ ] `social-publisher.service` installed and running: `systemctl status social-publisher.service`
- [ ] Log file writable: `ls -la logs/social_publisher.log`

## Test 1: Smoke Curl on New Endpoint

```bash
source /home/jared/projects/AI-CIV/aether/.env
curl -sv -X POST https://apex.purebrain.ai/api/linkedin/post-with-image \
  -H "X-Internal-Auth: ${INTERNAL_AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "QA smoke test — please ignore",
    "image_url": "https://purebrain.ai/blog/88-percent-ai-agent-security-incident/banner.png"
  }'
```

**PASS CRITERIA:** HTTP 200 with `success: true` and a valid `post_url`.

**DO NOT RUN THIS TEST WITH PRODUCTION CONTENT** — use a throwaway text. If it posts successfully, immediately delete it from Jared's LinkedIn feed via manual navigation (note the post URN for deletion).

Actually: BETTER — skip the smoke test as a separate post. Go directly to Test 2 with the real 88% content. One fire, not two.

## Test 2: Live Fire — 88% Post

**Post ID**: `post-1775568187`

**Content**:
```
88% of companies had an AI agent security incident last year. Not from sophisticated attacks. From human error. The gap between what we spend on technology and what we invest in human judgment keeps widening.

Full breakdown on The Neural Feed today: https://purebrain.ai/blog/88-percent-ai-agent-security-incident/

#AI #AISecurity #Enterprise #PureBrain #TheNeuralFeed
```

**Image**: `https://purebrain.ai/blog/88-percent-ai-agent-security-incident/banner.png`

### Fire Method: via the Publisher (not direct curl)

This tests the full end-to-end flow exactly as Apr 9 posts will fire.

1. Verify the post is in the schedule at `https://surf.purebrain.ai/social/scheduled` with:
   - `auto_publish: true`
   - `status: "approved"`
   - `scheduled_time: <= now>`
   - `linkedin_post_url: null`

2. Tail the publisher log:
   ```bash
   tail -f /home/jared/projects/AI-CIV/aether/logs/social_publisher.log
   ```

3. Wait up to 60s for the next polling cycle to fire it.

4. If the schedule doesn't have the post with auto_publish=true, temporarily PATCH it (document the patch in your report), let it fire, then revert.

### Pass Criteria

- [ ] Post appears on Jared's LinkedIn feed (visual confirmation — screenshot URL, do NOT use `Read` on image files)
- [ ] Image renders correctly (not cropped weirdly, banner displays)
- [ ] `linkedin_post_url` written back to social schedule entry
- [ ] `logs/social_publisher.log` shows the success line
- [ ] No errors in `logs/social_publisher.systemd.log`
- [ ] `social.html` dashboard reflects the published status

### Failure Criteria

If ANY of:
- Worker returns 4xx/5xx
- Publisher logs "Publish failed"
- Post doesn't appear on LinkedIn within 2 minutes
- Image is broken or missing
- Telegram alert fires

**STOP.** Capture:
- Full log output
- Worker response body
- Timestamp
- Current state of the schedule entry

Report back to dept-systems-technology IMMEDIATELY. Do not attempt manual workaround.

## Test 3: Verify Remaining Apr 9 Posts

If Test 2 passes, verify the schedule has Apr 9 3pm and Apr 9 7pm posts queued correctly:

- [ ] Both have `auto_publish: true`
- [ ] Both have `status: "approved"`
- [ ] Both have valid `banner_url`
- [ ] Both have non-empty `content`

Do NOT fire these manually. Let the publisher fire them on schedule. Leave the service running.

## Deliverables

1. `exports/departments/systems-technology/dispatches/2026-04-08-path-a-personal-linkedin/QA-RESULTS.md` with pass/fail for each test and the LinkedIn post URL
2. Log excerpts showing the successful publish
3. Memory written to `.claude/memory/agent-learnings/qa-engineer/2026-04-08--linkedin-publisher-live-fire.md`

## Image Safety Protocol

**DO NOT use the `Read` tool on any image files.** Visual confirmation is done by navigating to the LinkedIn URL and verifying — do not pull banner PNG into agent context.
