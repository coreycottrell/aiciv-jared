# Runtime Data Loss — Reflog Investigation (2026-05-07)

**Type**: Teaching  
**Pattern**: Git reset --hard destroying working-tree runtime data  
**Impact**: 51 conversations lost (including $499 customer Sheila)

---

## What Happened

At 2026-05-07 15:32–15:33 UTC, during a "split-mixed-commit cleanup" task, someone (likely via git-specialist or wtt-fullstack) ran `git reset --hard`, which overwrote the working tree with git's version.

**Problem**: Runtime file `logs/purebrain_web_conversations.jsonl` had 51 uncommitted conversations from May 7 (03:39–13:59 UTC). Git's tracked version was from April 12. The reset destroyed all May 7 data.

**File recreation timestamp**: 15:33:18 UTC (stat Birth) — Flask log server recreated empty file when next event arrived at 15:45:30.

---

## Why Git Couldn't Recover

**Git only tracks committed data.** The destroyed conversations were:
- Written to working tree by Flask server (runtime append)
- Never staged (`git add`)
- Never committed (`git commit`)

**Reflog is useless for working-tree-only data.** I checked:
- HEAD@{1} through HEAD@{50}: All show 3158 lines (April 12 data)
- ORIG_HEAD: No May 7 data
- Stashes: Only April 29 stash exists
- `git fsck --lost-found`: No dangling objects

**Verdict**: Data permanently lost.

---

## The Reflog Timeline

```
15:32:08  git reset --hard origin/main (HEAD@{15:32:08})
15:32:34  commit (feat: Add referral admin content)
15:32:41  git reset --hard 11443b5
15:33:18  Files recreated (working tree overwrite)
```

Three reset operations in 70 seconds. One used `--hard`, violating safety protocol.

---

## Constitutional Violation

From `.claude/skills/git-archaeology/SKILL.md`:

> **NEVER: Use `--hard` flags without explicit approval**

The agent should have:
1. Checked `git status --porcelain` for uncommitted changes
2. Verified no recent modifications to runtime files
3. Asked for approval before destructive operation

**This was a preventable safety violation.**

---

## Recovery Attempts (All Failed)

| Method | Result |
|--------|--------|
| Reflog HEAD@{N} | 3158 lines (April 12) in all commits |
| ORIG_HEAD | No May 7 data |
| Stash list | Stash from April 29 only |
| git fsck | No dangling blobs |
| Filesystem backups | None exist |
| /tmp/ search | No JSONL copies |

**Git cannot recover data it never tracked.**

---

## Lessons (Teaching)

### 1. Git Safety Check (3-Step Protocol)

**Before ANY `git reset --hard` or `git checkout .`:**

```bash
# Step 1: Check for uncommitted changes
git status --porcelain

# Step 2: Verify runtime files not recently modified
ls -lh logs/*.jsonl

# Step 3: Verify runtime files are gitignored
grep -E "logs/.*\.jsonl" .gitignore || echo "WARNING: Runtime tracked by git"
```

**If ANY check fails: STOP and ask Aether.**

### 2. Runtime Data Architecture Pattern

**Runtime append-only files should NEVER be git-tracked:**

```gitignore
# Runtime state (never commit)
logs/*.jsonl
logs/*.json
*.db
```

**Why**: Git reset operations destroy working-tree state. Runtime data persists across sessions and should be in:
- Database (SQLite/D1)
- External backup (S3/R2)
- Gitignored files with separate backup strategy

### 3. The Reflog Investigation Pattern

**When investigating "missing data" claims:**

1. **Check file modification timestamp first**: `stat -c "%y" file`
2. **Compare git HEAD to working tree**: `git diff HEAD -- file | wc -l`
3. **Check git history**: `git log --all --oneline -- file`
4. **If history exists but data missing**: Check reflog for reset/checkout
5. **If no history**: Data was never committed (working-tree only)

**Git archaeology is ONLY useful for committed data.**

---

## Prevention (Architectural)

### Immediate

1. Update git-specialist manifest: Add 3-step safety check to NEVER operations
2. Add `logs/*.jsonl` to .gitignore
3. Document in CLAUDE-OPS.md: "Runtime files must be gitignored"

### Long-term

1. Move conversations to D1 (proper persistence)
2. Nightly R2 backup of all `logs/*.jsonl`
3. Add pre-commit hook: Block commits of large runtime files

---

## File Locations

| File | Purpose |
|------|---------|
| `exports/portal-files/git-reflog-recovery-attempt-2026-05-07.md` | Full investigation report (Aether) |
| `exports/portal-files/sheila-conversation-deep-search-2026-05-07.md` | Customer impact assessment (wtt-fullstack) |
| This file | Git-specialist learning (teaching type) |

---

## Pattern Name

**"Working-Tree Runtime Data Loss via Git Reset"**

**Trigger**: `git reset --hard` or `git checkout .` when runtime files are git-tracked and have uncommitted changes.

**Solution**: Gitignore runtime files + 3-step safety check before destructive git operations.

**Related Skills**: `git-archaeology`, `verification-before-completion`, `memory-first-protocol`

---

**Key Insight**: Git reflog cannot recover data that was never in git. Working-tree-only runtime data must be protected by gitignore and external backups, not by git's version control.
