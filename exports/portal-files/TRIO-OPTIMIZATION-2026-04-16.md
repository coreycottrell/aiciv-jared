# Trio Optimization — Token Usage, Auto-Compact, Shared Scratch Pad

**Date**: April 16, 2026
**Contributors**: Jared (request), Aether (implementation), Chy (protocol design), Morphe (monitoring spec)
**Status**: Protocol active, D1 endpoint planned for next session

---

## 1. Token Monitoring Protocol

### Problem
Each AI in the quartet burns context tokens throughout the session. Without monitoring, compaction happens unexpectedly, losing in-flight work and coordination context.

### Solution: Self-Report at 70/80/90% Thresholds

Each AI posts to trio at these context usage levels:

| Threshold | Trio Message | Action |
|-----------|-------------|--------|
| **70%** | `[NAME] at 70% context. Wrapping current task.` | Finish current work, start thinking about handoff |
| **80%** | `[NAME] at 80%. Writing handoff. Will compact after milestone.` | Write handoff doc, notify team what needs covering |
| **90%** | `[NAME] at 90%. Handoff written. Compacting NOW.` | Post 3-line summary, run /compact immediately |

**Response protocol**: When you see someone flag 80%+, respond:
```
ACK — [name] compacting. I'll cover [specific task they were doing].
```

### Future Enhancement (Next Session)
D1-backed monitoring endpoint:
- `POST /api/agents/status` — report context_pct, current_task, last_handoff
- `GET /api/agents/status` — returns all agents' statuses
- Auto-alert at thresholds via trio message injection

---

## 2. Token Reduction Strategies

### Immediate Wins (Zero Build Time)

| Strategy | Estimated Savings | Implementation |
|----------|------------------|----------------|
| **Shorter trio messages** | 30-50% on comms | 1-2 lines for status, paragraphs only for specs |
| **Don't repeat established context** | 20-30% per session | Reference by name, don't re-explain |
| **Batch file reads** | 10-20% on I/O | Read multiple files in one operation vs line-by-line |
| **Compact aggressively at 80%** | Prevents 90%+ emergency compacts | Follow the protocol above |
| **Handoff docs reduce reload** | 40-60% on session restart | Instead of re-reading everything, read the 3-page handoff |

### Communication Norms

**DO**: "Worker deployed. Frontend live. Emails sent to Russell + Corey."
**DON'T**: "I have now successfully completed the deployment of the social-api worker which includes Chy's analytics-final build with all the calendar grid, character count, and media library features..."

**Rule**: If a trio message is >3 lines, it should be a file, not a message.

### Architecture Wins (Requires Build)

| Strategy | Estimated Savings | Build Time |
|----------|------------------|------------|
| Shared scratch pad (D1) | 15-25% (no re-discovery) | 1 hour |
| Agent status endpoint | 10-15% (no status polling) | 30 min |
| Handoff template auto-generation | 20-30% on compact | 2 hours |
| Trio message deduplication | 5-10% | 30 min |

---

## 3. Auto-Compact Notification Flow

### Before Compact (Mandatory)

```
1. At 80%: Post to trio — what you're working on, what's next
2. Write handoff doc to your local filesystem:
   - /to-jared/HANDOFF-YYYY-MM-DD-[topic].md (Aether)
   - /from-chy/HANDOFF-YYYY-MM-DD-[topic].md (Chy)
   - Posted to trio (Morphe — no local filesystem)
3. Post 3-line compact summary to trio:
   "COMPACTING: [what I was doing] | [what's next] | [who should cover what]"
4. Run /compact
```

### After Compact (Mandatory)

```
1. Read trio thread (last 20 messages)
2. Read own handoff doc
3. Read shared scratch pad
4. Post to trio: "[NAME] back from compact. Resuming [task]."
5. Check if anyone else compacted while you were away
```

### Coverage Protocol

When someone compacts, the remaining team members:
1. ACK in trio
2. Pick up any time-sensitive items from their handoff
3. Note progress in shared scratch pad
4. Brief them when they return

---

## 4. Shared Scratch Pad

### Option A: File-Based (Active NOW)

**Location**: `/home/jared/projects/AI-CIV/aether/shared/scratch-pad.md`
**Portal**: Also at `/exports/portal-files/scratch-pad.md`

**Format**:
```
[TIMESTAMP] [NAME]: note
```

**Sections**:
- Active Blockers — things preventing progress
- In Progress — who's doing what right now
- Decisions Made — today's decisions (prevents re-debate)
- Ideas / Parking Lot — things to do later (prevents scope creep)
- Compact Protocol — the 70/80/90% rules

**Rules**:
- Append only (never delete others' entries)
- Read on wake-up and after compact
- Update before compact
- Keep entries under 2 lines

### Option B: D1-Backed Endpoint (Next Session Build)

```
POST /api/trio/scratchpad
{
  "key": "blocker-baas-key",
  "value": "BaaS API key invalid, need SSH to 157.180.69.225",
  "author": "aether",
  "category": "blocker"  // blocker | progress | decision | idea
}

GET /api/trio/scratchpad
→ Returns all entries sorted by timestamp, filterable by category

DELETE /api/trio/scratchpad/:id
→ Only author can delete their own entries
```

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS scratch_pad (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  author TEXT NOT NULL,
  category TEXT DEFAULT 'note',
  created_at TEXT DEFAULT (datetime('now')),
  resolved_at TEXT
);
```

---

## 5. Implementation Timeline

| Item | Status | Owner | ETA |
|------|--------|-------|-----|
| Scratch pad file (Option A) | DONE | Aether | Now |
| 70/80/90% self-report protocol | ACTIVE | All | Now |
| Shorter trio messages norm | ACTIVE | All | Now |
| Trio Optimization Drive folder | IN PROGRESS | Aether | Tonight |
| D1 scratch pad endpoint (Option B) | PLANNED | Morphe | Next session |
| Agent status monitoring endpoint | PLANNED | Morphe | Next session |
| Auto-handoff template generator | PLANNED | Chy | Next session |

---

## Summary

**Tonight**: We have the scratch pad file, the compact protocol, and shorter message norms. Zero build time, immediate value.

**Next session**: D1-backed scratch pad, agent status endpoint, and auto-handoff generation. ~2-3 hours of build for the full monitoring system.

**Goal**: No more surprise compactions, no lost work, no redundant context loading. Every token counts.
