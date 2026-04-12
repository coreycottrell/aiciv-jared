# PATH A Personal LinkedIn Publisher — Pipeline Tracker

**Owner**: dept-systems-technology
**Approved**: Jared, 2026-04-08
**Must Ship**: TODAY
**Rule**: BUILD -> SECURITY -> QA -> SHIP (no shortcuts)

## Wave Status

| Wave | Task | Agent | Status | Dispatch Brief |
|------|------|-------|--------|----------------|
| 1a | Extend apex Worker with `/api/linkedin/post-with-image` | full-stack-developer | DISPATCHED | `01-build-worker.md` |
| 1b | Build `tools/social_publisher.py` poller | full-stack-developer | DISPATCHED | `02-build-publisher.md` |
| 1c | Systemd unit + deploy runbook | devops-engineer | DISPATCHED | `03-devops-systemd.md` |
| 2 | Security review of Wave 1 outputs | security-engineer-tech | BLOCKED on Wave 1 | `04-security-review.md` |
| 3 | Live fire on 88% post via publisher | qa-engineer | BLOCKED on Wave 2 | `05-qa-test.md` |
| 4 | Deploy + enable + monitor Apr 9 3pm/7pm | devops-engineer | BLOCKED on Wave 3 | (to follow QA pass) |

## Critical Path

1. Wave 1a + 1b + 1c run in parallel (independent deliverables)
2. Wave 2 starts ONLY when all three 1x complete
3. Wave 3 starts ONLY when Wave 2 returns APPROVED
4. Wave 4 starts ONLY when Wave 3 returns all-pass on 88% live fire

## Phase 2 (Deferred — NOT in this dispatch)

- Org page posting (requires LinkedIn product approval)
- Adding `w_organization_social` scope
- Org URN discovery
- Second endpoint for org posts

## Ship Definition (Wave 4 complete)

- [ ] Worker deployed, new endpoint live
- [ ] Publisher service running under systemd
- [ ] 88% post live on Jared's personal LinkedIn with URL captured
- [ ] Social schedule dashboard reflects published status
- [ ] Apr 9 3pm + 7pm posts queued and will auto-fire
- [ ] No Telegram alerts / no errors in logs
- [ ] Monitoring tail shows clean polling cycles

## Report Back to Jared (via Aether)

When Wave 4 completes, dept-systems-technology reports upward:
- Worker deploy status + endpoint URL
- Publisher service status
- 88% post LinkedIn URL
- Log excerpt showing polling
- Apr 9 3pm/7pm queue status
- Kill switch location for emergency stop
