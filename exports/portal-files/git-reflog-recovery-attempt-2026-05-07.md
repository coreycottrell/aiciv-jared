# Git Reflog Recovery Attempt — 2026-05-07

**Investigation Status**: COMPLETE  
**Data Recovery Status**: **NOT RECOVERABLE via git**  
**Root Cause Identified**: YES

---

## Summary

The 51 conversations from May 7, 2026 (03:39–13:59 UTC), including Sheila's $499 Couplify awakening, were **never committed to git** and were lost when the working-tree file `logs/purebrain_web_conversations.jsonl` was recreated at **15:33:18 UTC**.

**Recovery Verdict**: Data is **permanently lost**. Git archaeology cannot recover data that was never in version control.

---

## Reflog Analysis — The Destructive Event

### Critical Timestamps (all UTC)

```
11:54:35  Sheila payment (PayPal subscription I-RBXHJ68JCJPL)
13:59:00  Last "Logged conversation" entry before wipe (per log_server.log)
15:32:08  git reset --hard origin/main (HEAD@{2026-05-07 15:32:08})
15:32:34  commit (feat: Add referral admin content)
15:32:41  git reset --hard 11443b5
15:33:18  FILE RECREATED (stat Birth timestamp on all 4 runtime files)
```

### The Reflog Evidence

```bash
95499ee HEAD@{2026-05-07 15:32:08}: reset: moving to origin/main
11443b5 HEAD@{2026-05-07 15:32:34}: commit: feat: Add referral admin + partner CF Pages content
11443b5 HEAD@{2026-05-07 15:32:41}: reset: moving to 11443b58...
11443b5 HEAD@{2026-05-07 15:33:18}: reset: moving to HEAD
```

**The smoking gun**: Three reset operations in 70 seconds (15:32:08 → 15:32:41 → 15:33:18). One of these was likely `git reset --hard`, which **overwrites the working tree** with the git-tracked version.

### What Git Knew vs Working Tree

| State | Lines | Last Entry Date | Location |
|-------|-------|-----------------|----------|
| **git HEAD** (all commits) | 3158 | 2026-04-12 | All reachable commits |
| **Working tree before wipe** | 3158 + 51 = **3209** (estimated) | 2026-05-07 13:59 | LOST — never committed |
| **Working tree after 15:33** | 3158 | 2026-04-12 | Recreated from git |
| **Working tree now** | 3168 | 2026-05-07 16:59 | New data post-wipe |

**51 conversations existed only in working tree and were destroyed by the reset operation.**

---

## Recovery Attempt Results

### Checked Locations

| Source | May 7 Data? | Result |
|--------|-------------|--------|
| `HEAD` through `HEAD@{50}` | **NO** | All commits: 3158 lines, last entry 2026-04-12 |
| `ORIG_HEAD` | **NO** | 0 May 7 entries |
| `git stash list` (2 stashes) | **NO** | Stash@{0} from 2026-04-29 (4299 lines, no May 7) |
| `git fsck --lost-found` | **NO** | No dangling blobs found |
| Filesystem backups (`.orig`, `.backup`) | **NO** | No backup files exist |
| `/tmp/` | **NO** | No conversation JSONL copies |

### Why Git Cannot Help

**Git only tracks committed data.** The destroyed conversations were:
1. Written to working-tree file by Flask log server
2. **Never staged** (`git add`)
3. **Never committed** (`git commit`)
4. Destroyed by `git reset --hard` before being tracked

**Git's reflog and fsck are useless for working-tree-only data.**

---

## Responsible Agent/Operation

### The Split-Mixed-Commit Cleanup (Task #16)

From Aether's session around 15:25–15:33 UTC, handling a "split mixed commit" issue. The task likely involved:

1. Resetting to clean state (`git reset --hard origin/main` at 15:32:08)
2. Cherry-picking/committing specific changes (11443b5 at 15:32:34)
3. Additional reset operations (15:32:41, 15:33:18)

**Agent**: Unknown (likely `wtt-fullstack` or `git-specialist` invoked by Aether)  
**Command**: `git reset --hard` (inferred — the only command that recreates working-tree files)

### The Constitutional Violation

From `.claude/skills/git-archaeology/SKILL.md`:

> **NEVER:**
> - Use `--hard` flags without explicit approval
> - Execute `git reset --hard` on shared branches

**The agent violated safety protocol** by running `git reset --hard` without verifying working-tree state or checking for uncommitted runtime data.

---

## Why The File Was Recreated at 15:33:18

**Hypothesis**: After the `git reset --hard` at 15:32, the Flask log server was still running. When the next conversation event arrived (first traffic after wipe at 15:45:30), the server **opened the file in append mode**, which recreated it because Python's `open(..., 'a')` creates missing files.

**Evidence**:
- File Birth timestamp: 2026-05-07 15:33:18 (per `stat`)
- First post-wipe entry: 2026-05-07 15:45:30 (consent event)
- 4 runtime files share same 15:33 timestamp: `purebrain_web_conversations.jsonl`, `seed_events.jsonl`, `seed_sent_uuids.json`, `payer_emails_by_uuid.json`

**All 4 files were wiped by the reset and recreated by their respective services.**

---

## Recovery Options (None Via Git)

### What WOULD Have Worked (Prevention)

1. **Gitignore runtime files** — Prevent them from being tracked, avoiding reset impact
2. **External backup** — Nightly S3/R2 upload of `logs/*.jsonl`
3. **Database persistence** — Store conversations in SQLite/D1, not append-only JSONL
4. **Pre-reset verification** — Check `git status --porcelain` for working-tree changes before reset

### What CANNOT Work (Recovery)

- ❌ Git reflog (data never committed)
- ❌ Git fsck (no objects to recover)
- ❌ Stash (no stash created at that time)
- ❌ Filesystem undelete (Linux ext4 doesn't support reliable undelete, and file was overwritten)

**The data is gone.**

---

## Customer Impact

**Sheila / Jay Whitehurst (Couplify)**:
- $499 paid (subscription I-RBXHJ68JCJPL)
- AI name chosen: "Keeper" (inferred from log server events)
- Awakening conversation: **LOST**
- Email never sent (seed dispatcher used wrong match, sent "Torque" seed from different conversation)

**Recovery action**: Ask Sheila to redo awakening conversation. No git recovery possible.

---

## Recommendations (Prevent Recurrence)

### 1. Immediate (Constitutional)

**Ban `git reset --hard` without explicit 3-step safety check:**
```bash
# Before ANY git reset --hard:
1. git status --porcelain  # Check for uncommitted changes
2. grep -E "logs/.*\.jsonl" .gitignore || echo "WARNING: Runtime files tracked by git"
3. ls -lh logs/*.jsonl  # Verify no recent modifications
```

### 2. Architecture (Week 1)

**Move runtime state OUT of git-tracked files:**
- Option A: Gitignore `logs/*.jsonl` (simplest)
- Option B: Store conversations in D1 (proper solution)
- Option C: External backup (S3/R2 nightly snapshot)

### 3. Agent Training

**Update `git-specialist` manifest safety rules:**
```yaml
NEVER operations:
  - git reset --hard (without 3-step check)
  - git checkout . (without working-tree verification)
  - git clean -f (without dry-run first)
```

---

## Final Answer

| Question | Answer |
|----------|--------|
| **Recoverable via git?** | **NO** |
| **Why not?** | Data never committed, only in working tree |
| **Destructive operation?** | `git reset --hard` (15:32–15:33 UTC) |
| **Responsible agent?** | Unknown (invoked during split-commit cleanup) |
| **Recovery command?** | None — data permanently lost |
| **Customer impact?** | 51 conversations lost, including Sheila ($499 payer) |

**The reflog shows the WHEN and HOW, but cannot show the WHAT (the lost data) because git never knew about it.**

---

**Deliverable Complete**: Read-only investigation, no git state modified.  
**Memory Write Required**: Yes — this pattern must not repeat.
