---
name: day3-default-execution
version: 1.0.0
author: aether
description: Day-3 Default Policy for unblocking stalled decisions. When routed decision stalled 3+ days with no response from Jared or Chy across ANY channel, owning dept ships documented default + async FYI.
tags: [decision-making, unblocking, routing, jared-queue, chy-queue]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Day-3 Default Execution

Unblock stalled decisions with documented defaults when no response after 3 days.

## Core Principle

**"Silence after 72 hours = greenlight for documented default."**

When a routed decision is stalled 3+ days with no response from Jared or Chy across ANY channel:
- Owning department ships a documented default
- Sends async FYI notification

## Applies to Both Queues

1. **Jared Queue** - Decisions routed to Jared
2. **Chy Queue** - Decisions routed to Chy

## Detection Protocol

### Step 1: Check Routing Timestamp

Look for when the decision was first routed:

```bash
# Check Handshake Queue for routing age
python3 tools/read_777_sheet.py "Handshake Queue!A:H"

# Column structure: DATE,FROM,TO,ITEM,PRIORITY,STATUS,NOTES
# Status column = column 5 (index 4 in 0-indexed arrays)
```

### Step 2: Calculate Age

```python
from datetime import datetime, timezone

routing_date = "2026-05-17"  # From handshake queue
now = datetime.now(timezone.utc)
routed = datetime.fromisoformat(routing_date).replace(tzinfo=timezone.utc)
age_hours = (now - routed).total_seconds() / 3600

if age_hours > 72:
    print(f"🔴 STALLED: {age_hours:.1f} hours since routing")
```

### Step 3: Multi-Channel Sweep (MANDATORY Before "Silent")

**NEVER declare "silent" based on single channel.**

Check ALL channels for response:

```bash
# 1. Portal files (main thread activity)
find ~/exports/portal-files -mmin -4320 -type f | head -5
# -mmin -4320 = last 72 hours (3 days)

# 2. Portal server log (chat activity)
grep "POST /api/chat/send" logs/portal_server.log | tail -20

# 3. Telegram bridge log
grep -i "jared\|chy" /home/jared/tg_bridge.log | tail -20

# 4. Email (via AgentMail)
# Check tools/agentmail_general_monitor.py recent runs
```

**Main thread activity signal:**
```bash
# Recent portal file writes = active dialogue
find ~/exports/portal-files -mmin -180 -type f | wc -l
# If count > 0, main thread is active = NOT silent
```

### Step 4: Apply Day-3 Default

If ALL channels show no response for 72+ hours:

1. **Document the default decision**
2. **Execute the default**
3. **Send async FYI notification**

## Default Decision Framework

### Good Defaults (Safe to Ship)

| Scenario | Default Action |
|----------|---------------|
| Design choice (A vs B) | Ship most conservative option |
| Feature scope | Ship MVP, defer bells/whistles |
| Pricing edge case | Round in customer's favor |
| Content approval | Skip this item, continue pipeline |
| Tool adoption | Proceed with proof-of-concept |
| Infrastructure change | Deploy to staging, hold prod |

### Requires Human Decision (NEVER Default)

| Scenario | Why No Default |
|----------|----------------|
| Financial commitments | Legal/$ risk |
| Customer data deletion | Irreversible |
| Public statements | Brand risk |
| Contractual changes | Legal binding |
| Major architectural shifts | Long-term consequences |
| Team member actions | Human relationships |

## Notification Format

### FYI Message Template

```
📋 Day-3 Default Executed

Context: [Brief description of decision]
Routed: [Date] to [Jared/Chy]
Channels checked: Portal ✓, Telegram ✓, Email ✓, Main thread ✓
Silence duration: [X hours]

Default decision: [What was shipped]
Rationale: [Why this default is safe/conservative]

Rollback plan: [How to undo if needed]

No response needed. Notifying for awareness.

—
Routed by: [Department]
Executed by: [Agent]
```

### Send via Portal

```bash
# Primary delivery mechanism
./tools/portal_deliver.sh /path/to/day3-default-notice.md \
  "Day-3 Default: [Topic]" \
  "day3-default-[topic].md"
```

### Copy to CC War Room

```bash
curl -s -X POST \
  -H "X-CIV-Key: aether:$(cat /home/jared/purebrain_portal/.env | grep AETHER_CC_KEY | cut -d= -f2)" \
  -H "Content-Type: application/json" \
  -d '{"body":"📋 Day-3 Default: [Topic] - See portal for details"}' \
  "https://cc.purebrain.ai/api/chat/channels/39/messages"
```

## Examples

### Example 1: Design Approval Stalled

```
Scenario: Blog banner format choice (Option C vs Option D)
Routed: May 17 to Jared
Day 3: May 20 (72 hours)
Channels: All silent

Default: Ship Option D (current standard)
Rationale: Option D is March 20 locked standard, safe choice
FYI sent: Portal + CC War Room
```

### Example 2: Feature Scope Stalled

```
Scenario: Add social share buttons to blog posts?
Routed: May 15 to Chy
Day 3: May 18 (72 hours)
Channels: All silent

Default: Defer feature, ship blog without share buttons
Rationale: MVP approach, can add later without breaking changes
FYI sent: Portal + CC Engineering
```

### Example 3: NO DEFAULT (Requires Human)

```
Scenario: Customer requesting refund due to dissatisfaction
Routed: May 17 to Jared
Day 3: May 20 (72 hours)
Channels: Portal active (main thread dialogue ongoing)

Action: NO DEFAULT - Wait for explicit decision
Rationale: Financial/legal implications + main thread shows active engagement
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Single-Channel "Silent" Check
**BAD:**
```python
# Only checking Telegram
if no_telegram_messages:
    execute_default()
```
**GOOD:**
```python
# Multi-channel sweep
channels_silent = (
    no_portal_files and
    no_telegram and
    no_email and
    no_main_thread_activity
)
if channels_silent and age > 72_hours:
    execute_default()
```

### ❌ Anti-Pattern 2: Defaulting High-Risk Decisions
**BAD:** "No response on refund request, defaulting to approve"
**WHY:** Financial decisions require explicit approval

### ❌ Anti-Pattern 3: No Documentation
**BAD:** Shipping default without FYI notification
**GOOD:** Document default + rationale + rollback plan

### ❌ Anti-Pattern 4: Ignoring Main Thread Activity
**BAD:** "Handshake queue item is old, must be stalled"
**GOOD:** Check if main thread dialogue is actively discussing the topic

### ❌ Anti-Pattern 5: Premature Default
**BAD:** Executing default at 48 hours
**GOOD:** Wait full 72 hours, confirm multi-channel silence

## Verification

### Pre-Execution Checklist

- [ ] Routing timestamp > 72 hours ago
- [ ] Portal files checked (last 72h)
- [ ] Portal server log checked
- [ ] Telegram bridge log checked
- [ ] Email checked (if applicable)
- [ ] Main thread activity assessed
- [ ] Default decision is safe/conservative
- [ ] Rollback plan documented
- [ ] FYI notification prepared

### Post-Execution Verification

- [ ] Default shipped to appropriate environment
- [ ] FYI sent to portal
- [ ] CC War Room notified
- [ ] Handshake queue updated (status = "Day-3 default executed")
- [ ] Rollback plan accessible

## Integration with Other Skills

Works with:
- `bundled-wake-window-relay` - Coordinate timing of multi-ask messages
- `architectural-truth-first` - Ensure defaults don't create technical debt
- `social-kanban-approval` - Default = skip item, continue pipeline

## Constitutional Grounding

From MEMORY.md:
> "Day-3 default (both queues): Routed decisions stalled 3+ days → owning dept ships documented default + async FYI."
> "Multi-channel sweep before 'silent': Telegram-only grep = false-silent. Fuse Telegram+email+portal+main-thread."
> "Main-thread activity = find ~/exports/portal-files -mmin -180 + grep portal_server.log"

## Success Indicators

- [ ] Stalled decisions resolved within 4 days (3 days wait + 1 day default)
- [ ] No high-risk decisions defaulted without explicit approval
- [ ] All defaults documented with FYI notifications
- [ ] Multi-channel sweep performed before every default
- [ ] Zero false-silent declarations (missed an active channel)

---

*Last Updated: 2026-05-20*
*Status: Constitutional*
