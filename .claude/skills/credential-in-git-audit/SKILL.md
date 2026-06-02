---
name: credential-in-git-audit
description: Full audit of git-tracked files for hardcoded secrets (OAuth tokens, API keys, SSL keys, bot tokens). Distinct from pre-deploy-credential-scan which covers deploy artifacts only. Produces ST# escalation brief with rotation priority.
type: security
domain: security, git, secrets-management
created: 2026-05-21
trigger: "Run weekly or after any security incident. Also run when onboarding new team members or before any git history sharing (forks, public mirrors)."
status: provisional
tick_count: 0
last_used: 2026-05-21
introduced: 2026-05-21
---

# Credential-in-Git Audit

**Purpose**: Detect hardcoded secrets that are tracked in git history — OAuth tokens, API keys, SSL private keys, bot tokens, session data. These persist in git history even after deletion from working tree. Produces a prioritized escalation brief for ST# with rotation schedule.

**Origin**: 2026-05-21 — Security auditor found 18 secrets in 7 tracked files. Includes Zoom OAuth refresh token valid until July 2026, SSL private key, 12 BaaS API keys, 2 Telegram bot tokens, Ed25519 keypair, and Bluesky session data.

**Distinct from**: `pre-deploy-credential-scan` (which scans deploy artifacts like HTML/JS before CF Pages push). This skill scans the ENTIRE git-tracked tree.

## Steps

### 1. Pattern Scan (Two-Layer)

```bash
# Layer 1: Known-prefix patterns
grep -rnE "(BSKY_|ZOOM_|TELEGRAM_|AGENTAUTH_|BAAS_|SSL_|GOOGLE_).*(KEY|TOKEN|SECRET|PASSWORD|PRIVATE)\s*[:=]" \
  --include="*.json" --include="*.py" --include="*.env" --include="*.txt" --include="*.pem" .

# Layer 2: Generic high-entropy strings (prefixless tokens)
grep -rnE "['\"][A-Za-z0-9_-]{40,}['\"]" \
  --include="*.json" --include="*.py" --include="*.js" . | \
  grep -v node_modules | grep -v '.git/' | grep -v 'package-lock'
```

### 2. Classify Severity

| Severity | Criteria | Examples |
|----------|----------|---------|
| CRITICAL | Active auth tokens, private keys | OAuth refresh tokens, SSL keys, DB passwords |
| HIGH | Bot tokens, API keys with write access | Telegram bot tokens, Ed25519 signing keys |
| MEDIUM | Read-only API keys, session data | BaaS read keys, Bluesky session tokens |
| LOW | Expired or rotated credentials | Old tokens with comments indicating rotation |

### 3. Check Git History

```bash
# Even if removed from working tree, check if ever committed
git log --all --oneline -- "config/zoom_tokens.json" "*.pem" ".env"
```

### 4. Generate Escalation Brief

Output format for ST# routing:

```markdown
# ST# ESCALATION: Credentials in Git

**Priority**: P0 — active secrets in tracked files
**Found**: [N] secrets in [M] files
**Rotation needed**: [list with priority order]
**History rewrite**: Required (git filter-branch or BFG) — needs Jared approval
**Blocked by**: Force push to shared branches requires human sign-off
```

### 5. Verify .gitignore Coverage

```bash
# Ensure these patterns are in .gitignore
for pattern in "*.pem" "zoom_tokens.json" ".env.local" "*_session.txt"; do
  grep -q "$pattern" .gitignore && echo "OK: $pattern" || echo "MISSING: $pattern"
done
```

## Gotchas

- **Git history persists**: Removing a file from working tree does NOT remove it from history. BFG Repo-Cleaner or `git filter-repo` needed.
- **Force push required**: History rewrite = force push. Needs human approval and coordination with all clones.
- **Pre-commit hook**: Memory rule says >1MB blocked. But credential files are small — need separate pre-commit check for secret patterns.
- **Rotation order matters**: Rotate the most-exposed secrets first (tokens in public-facing code > tokens in config files).
- **Don't rotate at 1:30 AM**: Schedule rotation during business hours when human can verify services still work.

## Cross-References

- `pre-deploy-credential-scan`: Covers deploy artifacts (HTML/JS before CF Pages push)
- Memory: `feedback_credential_scan_regex_must_cover_prefixless_tokens.md`
- Escalation: `inbox/ST-ESCALATION-cred-in-git-2026-05-21.md`
