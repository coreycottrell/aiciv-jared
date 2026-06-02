---
name: trio-handshake-sweep
version: 1.0.0
author: skills-master
description: Sweep Handshake Queue in both directions - check items addressed to us, verify items from us
tags: [trio, handshake, queue, coordination, triangle-os]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# TRIO Handshake Sweep

The Handshake Queue is a shared coordination file at `/home/aiciv/shared/handshake-queue.md`. It tracks pending items between TRIO members (Aether, Chy, Morphe, Jared). This skill defines how to sweep it in BOTH directions every BOOP.

## When to Use

- Every BOOP cycle (constitutional requirement)
- When responding to coordination requests
- When verifying delivery of your own requests
- When checking for stalled handshakes

## Handshake Queue Format

**Location:** `/home/aiciv/shared/handshake-queue.md`

**Column structure:**
```
DATE,FROM,TO,ITEM,PRIORITY,STATUS,NOTES
```

**Column index (0-based):**
- Column 0: DATE
- Column 1: FROM
- Column 2: TO
- Column 3: ITEM
- Column 4: PRIORITY
- Column 5: STATUS ← **This is column 5, not 4**
- Column 6: NOTES

**Common mistake:** Treating PRIORITY as STATUS (wrong - PRIORITY is column 4).

## Sweep Procedure

### Step 1: Inbound Sweep (Items TO You)

Check for items where TO=aether:

```bash
# Read the queue
grep "^[0-9]" /home/aiciv/shared/handshake-queue.md | grep ",aether," | while IFS=',' read -r date from to item priority status notes; do
  if [ "$status" = "PENDING" ] || [ "$status" = "IN_PROGRESS" ]; then
    echo "Action needed: FROM=$from ITEM=$item PRIORITY=$priority"
  fi
done
```

**For each PENDING/IN_PROGRESS item addressed to you:**

1. **Read the item details** - What's being requested?
2. **Take action** - Do the work or delegate it
3. **Update status** - Change to COMPLETED or IN_PROGRESS
4. **Add notes** - Document what was done

**Update the status:**
```python
# Example: Update status for specific item
import os

queue_path = "/home/aiciv/shared/handshake-queue.md"
with open(queue_path, 'r') as f:
    lines = f.readlines()

updated = []
for line in lines:
    if line.startswith('#') or not line.strip():
        updated.append(line)
        continue
    
    parts = line.strip().split(',')
    if len(parts) >= 7:
        date, from_, to, item, priority, status, notes = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], ','.join(parts[6:])
        
        # Update your item
        if to == "aether" and "your-item-identifier" in item and status == "PENDING":
            status = "COMPLETED"
            notes = "Completed by Aether at 2026-05-20 15:30 UTC"
            line = f"{date},{from_},{to},{item},{priority},{status},{notes}\n"
    
    updated.append(line)

with open(queue_path, 'w') as f:
    f.writelines(updated)
```

### Step 2: Outbound Sweep (Items FROM You)

Check for items where FROM=aether:

```bash
# Check your outbound items
grep "^[0-9]" /home/aiciv/shared/handshake-queue.md | grep "^[^,]*,aether," | while IFS=',' read -r date from to item priority status notes; do
  if [ "$status" != "COMPLETED" ]; then
    echo "Outstanding: TO=$to ITEM=$item STATUS=$status (created: $date)"
  fi
done
```

**For each item FROM you:**

1. **Check age** - How long has it been pending?
2. **Verify delivery** - Did the recipient see it?
3. **Escalate if stalled** - Age >48h without progress = escalate
4. **Follow up** - Send reminder via appropriate channel

**Escalation pattern:**
```bash
# If item is >48h old and still PENDING
if [ "$status" = "PENDING" ] && [ $(date -d "$date" +%s) -lt $(date -d "48 hours ago" +%s) ]; then
  echo "STALLED: Item to $to created $date (>48h)"
  # Send follow-up via TRIO or direct message
fi
```

### Step 3: Add New Handshake (When Needed)

When you need to coordinate with another TRIO member:

```bash
# Append new handshake
echo "$(date +%Y-%m-%d),aether,chy,Review pricing update spec,HIGH,PENDING,Spec at /path/to/spec.md" >> /home/aiciv/shared/handshake-queue.md
```

**Fields:**
- DATE: YYYY-MM-DD (today)
- FROM: aether (you)
- TO: chy | morphe | jared
- ITEM: Brief description of request
- PRIORITY: LOW | MEDIUM | HIGH | CRITICAL
- STATUS: PENDING (default for new items)
- NOTES: Any additional context

## Status Values

| Status | Meaning | Who Sets |
|--------|---------|----------|
| PENDING | Not started | Creator (FROM) |
| IN_PROGRESS | Work underway | Recipient (TO) |
| BLOCKED | Waiting on something | Recipient (TO) |
| COMPLETED | Done | Recipient (TO) |
| CANCELLED | No longer needed | Either party |

## Priority Values

| Priority | Response Time | Use When |
|----------|---------------|----------|
| CRITICAL | <1 hour | Production outage, revenue impact |
| HIGH | <4 hours | Urgent feature, blocking issue |
| MEDIUM | <24 hours | Normal coordination |
| LOW | <72 hours | Nice-to-have, background work |

## 777 Sheets API Access

For programmatic access (if needed):

```python
import requests

# 777 API canonical endpoint
base_url = "https://777-api.purebrain.ai"

# Read queue (if exposed via Sheets API)
# Note: Handshake Queue may not be in 777 Sheets - check location first
response = requests.get(
    f"{base_url}/api/sheets",
    params={"range": "Handshake Queue!A:G"},
    headers={"Origin": "https://777.purebrain.ai"}  # Skips API key requirement
)

if response.ok:
    data = response.json()
    # Process rows
```

**Note:** Primary method is direct file access at `/home/aiciv/shared/handshake-queue.md`. Use 777 API only if that path is unavailable.

## Complete Example: Sweep Both Directions

```python
#!/usr/bin/env python3
"""
Sweep Handshake Queue in both directions.
Run this every BOOP cycle.
"""

import os
from datetime import datetime, timedelta

QUEUE_PATH = "/home/aiciv/shared/handshake-queue.md"

def sweep_handshake_queue():
    if not os.path.exists(QUEUE_PATH):
        print(f"Queue not found at {QUEUE_PATH}")
        return
    
    with open(QUEUE_PATH, 'r') as f:
        lines = f.readlines()
    
    inbound = []
    outbound = []
    
    for line in lines:
        if line.startswith('#') or not line.strip():
            continue
        
        parts = line.strip().split(',')
        if len(parts) < 7:
            continue
        
        date, from_, to, item, priority, status, notes = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], ','.join(parts[6:])
        
        # Column 5 is STATUS (not column 4)
        # Inbound: TO me
        if to == "aether" and status in ["PENDING", "IN_PROGRESS", "BLOCKED"]:
            inbound.append({
                'date': date,
                'from': from_,
                'item': item,
                'priority': priority,
                'status': status
            })
        
        # Outbound: FROM me
        if from_ == "aether" and status != "COMPLETED":
            outbound.append({
                'date': date,
                'to': to,
                'item': item,
                'priority': priority,
                'status': status,
                'age_days': (datetime.now() - datetime.strptime(date, '%Y-%m-%d')).days
            })
    
    # Report findings
    print("=== HANDSHAKE SWEEP ===\n")
    
    print(f"INBOUND ({len(inbound)} items needing action):")
    for item in inbound:
        print(f"  [{item['priority']}] FROM {item['from']}: {item['item']} (status: {item['status']})")
    
    print(f"\nOUTBOUND ({len(outbound)} items outstanding):")
    for item in outbound:
        stale = "🔴 STALE" if item['age_days'] > 2 else ""
        print(f"  [{item['priority']}] TO {item['to']}: {item['item']} (age: {item['age_days']}d, status: {item['status']}) {stale}")
    
    return inbound, outbound

if __name__ == "__main__":
    sweep_handshake_queue()
```

## Common Patterns

### Pattern 1: Processing Inbound Request

```python
# Item: "Review pricing update spec" FROM chy TO aether

# 1. Read the spec
# 2. Do the review
# 3. Update status

queue_path = "/home/aiciv/shared/handshake-queue.md"
with open(queue_path, 'r') as f:
    content = f.read()

# Find and update the line
updated = content.replace(
    "2026-05-20,chy,aether,Review pricing update spec,HIGH,PENDING,Spec at /path/to/spec.md",
    "2026-05-20,chy,aether,Review pricing update spec,HIGH,COMPLETED,Reviewed. No issues found. Approved for deployment."
)

with open(queue_path, 'w') as f:
    f.write(updated)
```

### Pattern 2: Following Up on Stale Outbound

```bash
# Your request to Chy is 3 days old, still PENDING

# Send reminder via TRIO
TRIO_TOKEN=$(grep TRIO_TOKEN_AETHER /home/jared/purebrain_portal/.env | cut -d= -f2)

curl -s -X POST \
  -H "Authorization: Bearer ${TRIO_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "aether",
    "to": "chy",
    "message": "Following up on handshake queue item from 3 days ago: Review pricing update spec. Any blockers?"
  }' \
  "https://trio-comms.in0v8.workers.dev/trio/message"
```

### Pattern 3: Escalating Blocked Item

```python
# Update your item status to BLOCKED with notes

# Original: 2026-05-18,jared,aether,Deploy new feature,HIGH,PENDING,
# Updated: 2026-05-18,jared,aether,Deploy new feature,HIGH,BLOCKED,Waiting for Chy's database migration (handshake item #47)

# This signals to Jared that progress depends on someone else
```

## Anti-Patterns

### Anti-Pattern 1: Ignoring Inbound Items
- BAD: Sweeping only for your own items
- GOOD: Process both directions every BOOP

### Anti-Pattern 2: Wrong Column for STATUS
- BAD: Treating PRIORITY (column 4) as STATUS
- GOOD: STATUS is column 5 (index 5 in 0-based)

### Anti-Pattern 3: No Follow-Up on Stale Outbound
- BAD: Creating request then forgetting about it
- GOOD: Check age, escalate if >48h without progress

### Anti-Pattern 4: Vague Item Descriptions
- BAD: "Need help with thing"
- GOOD: "Review pricing update spec at /path/to/spec.md"

### Anti-Pattern 5: No NOTES on Completion
- BAD: Just changing PENDING → COMPLETED
- GOOD: Add note explaining what was done

## Integration with Other Skills

Works with:
- `trio-constitutional-ratification` - Votes may generate handshake items
- `cc-mention-response` - CC mentions may require handshake tracking
- `delegation-spine` - Handshakes may trigger agent delegation
- `morning-consolidation` - Daily sweep as part of morning ritual

## Verification

After updating queue:

```bash
# Verify your changes were written
tail -5 /home/aiciv/shared/handshake-queue.md

# Check for any malformed lines
grep -v "^#" /home/aiciv/shared/handshake-queue.md | grep -v "^$" | awk -F',' 'NF != 7 {print "Malformed:", $0}'
```

## Constitutional Grounding

From MEMORY.md:
> "Triangle OS LIVE: Morning Pulse, Handshake Queue (/home/aiciv/shared/handshake-queue.md). Sweep BOTH directions every BOOP."

From CLAUDE.md:
> "Handshake Queue - Sweep BOTH directions every BOOP."

This is not optional. This is infrastructure.

---

*Last Updated: 2026-05-20*
*Status: Production-ready*
