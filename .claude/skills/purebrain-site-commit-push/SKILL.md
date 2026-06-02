---
name: purebrain-site-commit-push
version: 1.0.0
author: aether
description: Git commit and push pattern for puretechnyc/purebrain-site
tags: [git, deploy, purebrain-site, workflow]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# PureBrain Site Commit & Push

Standard workflow for committing and pushing changes to purebrain.ai.

## Repo Location

`/home/jared/projects/purebrain-site`

## Remote

`puretechnyc/purebrain-site` on GitHub (main branch)

## Workflow

```bash
cd /home/jared/projects/purebrain-site

# Check status
git status --short

# Stage specific files (NEVER git add -A)
git add path/to/changed/file.html

# Commit with descriptive message
git commit -m "feat(section): what changed and why

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

# Push (may need pull --rebase if behind)
git push origin main
```

## If Push Rejected

```bash
git pull --rebase origin main
git push origin main
```

## Dual-Source Warning

Files shared between `aether/exports/cf-pages-deploy/` AND `puretechnyc/purebrain-site/` MUST stay byte-identical. Check before pushing.

## CWD Note

Working directory resets to aether project after each command. Always `cd` explicitly.

## Commit Message Format

**Pattern**: `<type>(<scope>): <description>`

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Formatting, no code change
- `refactor` - Code restructure, no behavior change
- `test` - Adding tests
- `chore` - Maintenance tasks

**Examples:**
```
feat(pricing): update Awakened tier to $297/mo
fix(auth): correct magic link domain rewrite
docs(gift): clarify investor page instructions
```

## Pre-Push Checklist

- [ ] `cd /home/jared/projects/purebrain-site`
- [ ] `git status` shows only intended changes
- [ ] Staged specific files (not `git add -A`)
- [ ] Commit message follows format
- [ ] Checked for dual-source conflicts
- [ ] Ready for 90-150s propagation window

## Common Issues

### Issue 1: Push Rejected (Behind Remote)

```bash
# Pull with rebase, then push
git pull --rebase origin main
git push origin main
```

### Issue 2: Wrong Working Directory

```bash
# Symptom: git commands show aether repo, not purebrain-site
# Fix: Always cd explicitly
cd /home/jared/projects/purebrain-site
```

### Issue 3: Dual-Source Drift

```bash
# Check if file exists in both locations
ls /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/our-team/index.html
ls /home/jared/projects/purebrain-site/our-team/index.html

# Diff them
diff /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/our-team/index.html \
     /home/jared/projects/purebrain-site/our-team/index.html
```

## Anti-Patterns

### Anti-Pattern 1: Git Add All
- **BAD**: `git add -A` or `git add .`
- **GOOD**: `git add path/to/file.html` (specific files only)
- **Why**: Prevents accidental commits of .env, large binaries, etc.

### Anti-Pattern 2: Vague Commit Messages
- **BAD**: "Update files" or "Fix stuff"
- **GOOD**: "fix(auth): correct session cookie domain"
- **Why**: Git log becomes documentation

### Anti-Pattern 3: Forgetting Co-Author
- **BAD**: Commit without Claude co-author line
- **GOOD**: Include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
- **Why**: Attribution for AI-assisted work

### Anti-Pattern 4: Deploy Without Commit
- **BAD**: Running wrangler deploy with uncommitted changes
- **GOOD**: Commit first, then git push triggers deploy
- **Why**: Git is source of truth (Constitutional)

## Constitutional Rules

Per `feedback_wrangler_deploy_must_be_preceded_by_git_commit.md`:
- Production state MUST derive from `git HEAD`
- All deploys preceded by clean tree
- No uncommitted changes in production

Per `feedback_puretechnyc_git_is_only_source_of_truth.md`:
- Only `puretechnyc/*` repos are canonical
- `aether/workers/*` mirrors RETIRED
- Worker code at `/home/jared/projects/<repo>/`

---

**Remember: Git push is the deploy. No other method.**
