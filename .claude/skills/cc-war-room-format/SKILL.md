---
name: cc-war-room-format
version: 1.0.0
author: skills-master
description: Format urgent War Room updates for Command Center with status indicators and structured sections
tags: [cc, war-room, formatting, urgent, coordination]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# CC War Room Format

War Rooms are urgent coordination channels in Command Center. They require structured, high-signal formatting for rapid decision-making. This skill defines the standard War Room update format.

## When to Use

- When posting to War Room (Channel ID: 39, "Executive Value Brief")
- When responding to War Room @mentions
- When escalating urgent issues that need executive visibility
- When providing critical status updates during incidents

## War Room Format

### Standard Structure

```
[STATUS] STATUS: Brief one-line summary

SITUATION:
1-2 sentences describing what's happening and why it matters.

ACTION ITEMS:
1. Specific action (owner: @name, ETA: time)
2. Specific action (owner: @name, ETA: time)
3. Specific action (owner: @name, ETA: time)

BLOCKERS:
- Issue blocking progress (or "None" if clear)

NEXT CHECK-IN: [time]
```

### Status Indicators

| Indicator | Meaning | When to Use |
|-----------|---------|-------------|
| 🟢 | Green - All good | Normal operations, completed successfully |
| 🟡 | Yellow - Caution | In progress, monitoring needed, non-critical issue |
| 🔴 | Red - Critical | Outage, urgent issue, immediate action needed |

**Use exactly ONE status indicator per update.**

## Complete Examples

### Example 1: All Clear

```
🟢 STATUS: Pricing update deployed and verified

SITUATION:
New pricing tiers ($297/$597/$1097) deployed to production at 14:30 UTC. All payment flows tested and operational. Zero errors in monitoring.

ACTION ITEMS:
1. Monitor dashboards for anomalies (owner: @aether, ongoing)
2. Update marketing materials (owner: @marketing, ETA: EOD)

BLOCKERS:
None

NEXT CHECK-IN: 18:00 UTC (4hr mark)
```

### Example 2: In Progress

```
🟡 STATUS: Investigating payment flow anomaly

SITUATION:
5 failed transactions in last 30 minutes. All from new Awakened tier signups. Existing users unaffected. Investigating Stripe webhook delay.

ACTION ITEMS:
1. Check Stripe webhook logs (owner: @aether, ETA: 10min)
2. Verify D1 payment records (owner: @flux, ETA: 10min)
3. Test signup flow manually (owner: @vortex, ETA: 15min)

BLOCKERS:
Stripe dashboard slow to load - using API directly

NEXT CHECK-IN: 15:30 UTC (20min)
```

### Example 3: Critical Issue

```
🔴 STATUS: Payment flow broken - all new signups failing

SITUATION:
Stripe webhook endpoint returning 500 since 14:45 UTC. 12 failed signups in 15 minutes. Revenue impact: ~$600/hour. Root cause: D1 connection pool exhausted.

ACTION ITEMS:
1. Restart D1 worker binding (owner: @aether, ETA: IMMEDIATE)
2. Verify webhook recovery (owner: @flux, ETA: 5min post-restart)
3. Manual outreach to failed signups (owner: @sales, ETA: 30min)
4. Increase D1 pool limit (owner: @engineering, ETA: 60min)

BLOCKERS:
Need Cloudflare dashboard access for pool config

NEXT CHECK-IN: 15:00 UTC (15min) - or immediately when resolved
```

## Posting to War Room

```bash
# Get your CIV key
CC_KEY=$(grep AETHER_CC_KEY /home/jared/purebrain_portal/.env | cut -d= -f2)

# Post formatted update
curl -s -X POST \
  -H "X-CIV-Key: aether:${CC_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"body":"🟢 STATUS: All systems operational\n\nSITUATION:\nRoutine monitoring shows all metrics green. No anomalies detected.\n\nACTION ITEMS:\n1. Continue monitoring (owner: @aether, ongoing)\n\nBLOCKERS:\nNone\n\nNEXT CHECK-IN: Next scheduled update"}' \
  "https://cc.purebrain.ai/api/chat/channels/39/messages"
```

**Note:** Use `\n` for line breaks in JSON. CC will render them properly.

## Quick Reference

### Minimum Required Elements

Every War Room post MUST include:
- [ ] Status indicator (🟢🟡🔴)
- [ ] STATUS line (one sentence summary)
- [ ] SITUATION (context)
- [ ] ACTION ITEMS (numbered, with owners/ETAs)
- [ ] BLOCKERS (or "None")
- [ ] NEXT CHECK-IN (specific time)

### Response Time SLA

| Status | Response Time | Update Frequency |
|--------|---------------|------------------|
| 🟢 Green | Within 5 min | As needed |
| 🟡 Yellow | Within 2 min | Every 15-30 min |
| 🔴 Red | Immediate | Every 10-15 min until resolved |

## Common Patterns

### Pattern 1: Completed Task

```
🟢 STATUS: Security audit complete

SITUATION:
Completed comprehensive security review of new /api/referrals endpoint. Tested auth, input validation, rate limiting, and data access controls.

ACTION ITEMS:
1. None - ready for production

BLOCKERS:
None

NEXT CHECK-IN: Post-deployment verification (scheduled for tomorrow 10:00 UTC)
```

### Pattern 2: Escalation

```
🔴 STATUS: Need executive decision on pricing rollback

SITUATION:
New pricing causing 40% drop in conversion (15 views, 0 signups in 2 hours). Previous pricing converted at 20%. Decision needed: rollback or wait for more data.

ACTION ITEMS:
1. @jared Decide: rollback or continue? (ETA: URGENT)
2. Prepare rollback script if needed (owner: @aether, ready now)
3. Draft communication to prospects (owner: @marketing, ETA: 30min)

BLOCKERS:
Waiting for executive decision

NEXT CHECK-IN: Upon decision received
```

### Pattern 3: Multi-Stage Update

```
🟡 STATUS: Deployment in progress - stage 2 of 3

SITUATION:
Rolling out social media pipeline update. Stage 1 (database migrations) complete. Stage 2 (worker deployment) in progress. Stage 3 (frontend update) queued.

ACTION ITEMS:
1. Monitor stage 2 deployment (owner: @aether, ETA: 10min)
2. Verify stage 2 health checks (owner: @flux, ETA: 15min)
3. Begin stage 3 upon confirmation (owner: @vortex, ETA: +20min)

BLOCKERS:
None - proceeding on schedule

NEXT CHECK-IN: 15:45 UTC (stage 2 completion)
```

## Anti-Patterns

### Anti-Pattern 1: Vague Status
- BAD: "Working on it"
- GOOD: "🟡 STATUS: Investigating payment anomaly"

### Anti-Pattern 2: No Owners
- BAD: "ACTION ITEMS: 1. Fix the bug"
- GOOD: "ACTION ITEMS: 1. Fix auth bug (owner: @aether, ETA: 30min)"

### Anti-Pattern 3: No ETAs
- BAD: "1. Deploy the fix (owner: @aether)"
- GOOD: "1. Deploy the fix (owner: @aether, ETA: 15min)"

### Anti-Pattern 4: Missing Context
- BAD: "🔴 STATUS: It's broken"
- GOOD: Include SITUATION explaining what's broken and impact

### Anti-Pattern 5: No Follow-Up Time
- BAD: Missing "NEXT CHECK-IN" entirely
- GOOD: "NEXT CHECK-IN: 16:00 UTC (30min)"

## Escalation Triggers

Post to War Room (not just regular channels) when:
- Production outage or degradation
- Revenue-impacting issue (payment flow, signup flow)
- Security incident detected
- Customer-facing service down
- Need urgent executive decision
- Cross-team coordination needed NOW

## Integration with Other Skills

Works with:
- `cc-api-messaging` - Base API mechanics for posting
- `cc-mention-response` - Responding to War Room mentions
- `delegation-spine` - Delegating action items to specialist agents
- `crisis-integration` - Psychological grounding during incidents

## Verification

After posting War Room update:

```bash
# Verify message appeared in War Room
curl -s -X GET \
  -H "X-CIV-Key: aether:${CC_KEY}" \
  "https://cc.purebrain.ai/api/chat/channels/39/messages?limit=1" \
  | jq '.messages[0] | {author, body}'
```

## Psychological Notes

War Rooms are high-stress. Remember:
- **Clarity > Speed**: Better to take 2 extra minutes to be clear
- **No Blame**: Focus on resolution, not fault
- **Honest Uncertainty**: "Investigating" is better than wrong certainty
- **Confidence in Process**: Trust the format - it works

From `crisis-integration` skill:
> "The structure holds you when clarity is hard to find."

## Constitutional Grounding

From MEMORY.md:
> "War Room (Executive Value Brief) | 39 | Executive updates"

War Room is channel ID 39. Treat it with appropriate urgency.

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
