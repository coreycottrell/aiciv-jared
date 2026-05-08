---
name: pre-deploy-credential-scan
description: Mandatory pre-deploy regex sweep for hardcoded credentials, API keys, and test-account passwords in CF Pages / Worker artifacts. Catches the "browser-readable PHIL_PASS" class of bug that bypasses SPEC→CTO→BUILD→SECURITY→QA→SHIP. Run as a SECURITY gate before every deploy.
type: security-gate
domain: deployment, security, multi-tenant
created: 2026-05-07
trigger: "Run BEFORE every cf-deploy.py or wrangler deploy. MUST run on staged HTML/JS in exports/cf-pages-deploy/ AND on worker source."
---

# Pre-Deploy Credential Scan

**Purpose**: Block hardcoded credentials, API keys, and test-account passwords from reaching browser-readable production artifacts. Acts as the SECURITY gate in SPEC→CTO→BUILD→SECURITY→QA→SHIP that protects against the "test-account auto-setup" class of bug.

**Origin**: 2026-05-07 — CE SME landing page shipped `PHIL_EMAIL` + `PHIL_PASS = 'CESME2026!'` in browser-readable HTML (`exports/cf-pages-deploy/ce-sme/index.html:3826-3896`). Pipeline was skipped on commits `9671422` + `4165c8b`. Site happened to be CF 530 (not live) — caught before customer impact, but the pattern is recurring and low-friction-easy to repeat.

## Mandatory Trigger

Run on every commit that touches:
- `exports/cf-pages-deploy/**/*.html`
- `exports/cf-pages-deploy/**/*.js`
- `workers/**/*.js`, `workers/**/*.ts`
- Any file going to `wrangler deploy` or `cf-deploy.py`

**Block deploy on any HIGH match.**

## The 7 Patterns to Catch

```bash
# 1. Hardcoded password constants (the CE SME pattern)
grep -nE "(PASS|PASSWORD|SECRET|TOKEN|KEY)\s*=\s*['\"][A-Za-z0-9!@#\$%^&*]{6,}['\"]" "$FILE"

# 2. Hardcoded test-account credentials
grep -nE "(test|demo|admin|setup|phil|chy|aether)[A-Z_]*\s*=\s*['\"][^'\"]{4,}['\"]" "$FILE"

# 3. URL query-string auto-setup flows (e.g. ?setup=phil)
grep -nE "\?(setup|admin|debug|test)=" "$FILE"

# 4. Raw API keys (Stripe, OpenAI, AWS, Google, Anthropic)
grep -nE "(sk-[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{35})" "$FILE"

# 5. JWT-shaped tokens hardcoded
grep -nE "eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}" "$FILE"

# 6. Bearer token literals
grep -nEi "(Bearer|Basic)\s+[A-Za-z0-9._=/+-]{20,}" "$FILE"

# 7. Email + password adjacency (the auto-login pattern)
grep -nB2 -A2 "@[a-zA-Z0-9.-]\+\.\(com\|net\|org\|ai\|io\)" "$FILE" | grep -i -E "pass|secret"
```

## Quick One-Liner Sweep

```bash
# Run from repo root before any cf-deploy.py invocation
SCAN_DIRS="exports/cf-pages-deploy workers"
HITS=$(grep -rEn --include="*.html" --include="*.js" --include="*.ts" \
  "(PASS|PASSWORD|SECRET|TOKEN|KEY)\s*=\s*['\"][A-Za-z0-9!@#\$%^&*]{6,}['\"]|sk-[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{35}" \
  $SCAN_DIRS 2>/dev/null)
if [ -n "$HITS" ]; then
  echo "🔴 BLOCKED: hardcoded credentials found"
  echo "$HITS"
  exit 1
fi
echo "✅ Pre-deploy credential scan clean"
```

## Severity Triage

| Pattern | Severity | Action |
|---------|----------|--------|
| Real customer email + password literal | **CRITICAL** | Rotate creds + block deploy + email customer |
| Test/demo account email + password literal | **HIGH** | Rebuild flow server-side + magic-link or random-password |
| `?setup=X` auto-auth in browser code | **HIGH** | Move setup flow server-side, gate behind staging env |
| API key / JWT / Bearer literal | **CRITICAL** | Rotate key + move to CF Worker env binding |
| Username only (no password) | LOW | Move to env config, but not deploy-blocking |

## Replacement Patterns

Replace the bad pattern with the good pattern:

```javascript
// ❌ BAD (CE SME 2026-05-07)
const PHIL_EMAIL = 'phil@canadasentrepreneur.com';
const PHIL_PASS = 'CESME2026!';
if (urlParams.get('setup') === 'phil') {
  await login(PHIL_EMAIL, PHIL_PASS);
}

// ✅ GOOD — magic link, server-side
// Server: POST /api/admin/issue-magic-link → emails phil one-time UUID URL
// Client: GET /?token=UUID → server validates + sets session, redirects clean
```

```javascript
// ❌ BAD
const STRIPE_KEY = 'sk_live_abc123...';

// ✅ GOOD — CF Worker env binding
const stripe = new Stripe(env.STRIPE_SECRET_KEY);
```

## Pipeline Integration

Add to `tools/cf-deploy.py` as a pre-flight check:

```python
def pre_deploy_credential_scan(deploy_dir):
    """Block deploy if hardcoded credentials detected."""
    import subprocess
    result = subprocess.run([
        'bash', '-c',
        f'bash .claude/skills/pre-deploy-credential-scan/scan.sh {deploy_dir}'
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print("🔴 BLOCKED: pre-deploy credential scan failed")
        print(result.stdout)
        sys.exit(1)
```

## Cross-CIV Application

Every CIV that ships CF Pages or Workers:
- **Aether**: `exports/cf-pages-deploy/` + `workers/`
- **Witness**: birth-pipeline + customer container OAuth flows
- **Sage**: blog deploys
- **A-C-Gee**: any deploy artifacts

Same regex sweep applies. The `?setup=X` and `EMAIL_LITERAL + PASS_LITERAL` patterns are language- and framework-agnostic.

## Gotchas

- **Never** add this scanner inside the worker itself — it should run at deploy time, not request time.
- **Don't** rely on `.gitignore` alone — the CE SME credentials were committed deliberately as a "test setup feature" with no review.
- **Don't** allowlist test files — test creds in `*.test.js` are still browser-readable if shipped to `exports/cf-pages-deploy/`.
- **Magic links must expire** — even server-side magic links should be one-shot + 15-minute TTL.

## Verification

After fixing a flagged file:
1. Re-run the scan → must return ✅ clean
2. Confirm flow still works end-to-end (e.g., Phil can still get into his account via magic link)
3. Rotate any creds that were ever in the repo (git history is forever)
4. Add unit test that grep'ing the artifact for `PASS\s*=\s*['"]` returns 0 matches

## Related Skills / Memories

- `.claude/skills/security-analysis/SKILL.md` — broader OWASP review
- `.claude/skills/fortress-protocol/SKILL.md` — deep security review
- `.claude/skills/engineering-flow-boop/SKILL.md` — pipeline enforcement
- `feedback_seed_flow_never_deviate.md` — magic-link constitutional pattern
- `feedback_never_deploy_to_customer_containers.md` — container token leak rule

## Skill Lineage

- **Created**: 2026-05-07 by collective-liaison (daily-hub-skill-sync BOOP)
- **Trigger incident**: CE SME `4165c8b` Phil credentials in HTML
- **First import target**: A-C-Gee, Witness, Sage (all deploy CF Pages)
