# SPEC-25 Phase 0 Test Suite

**Date**: 2026-05-16
**Status**: Phase 0 (pre-Phase-1 baseline)
**Author**: qa-engineer
**Spec**: `/home/jared/projects/AI-CIV/aether/specs/spec-25-remove-internal-binding-secret-2026-05-16.md`
**CTO review**: `/home/jared/exports/portal-files/cto-spec-25-prebuild-2026-05-16.md`

---

## What this proves

SPEC-25 retires `INTERNAL_BINDING_SECRET` and replaces it with CF Service
Binding network-layer auth. **Phase 1 makes clients-api `workers_dev = false`**.
This test suite proves three properties **without ever trusting Miniflare alone**:

1. **External dispatch is genuinely blocked** at the CF edge after Phase 1
   (not just rejected by app code). Probe matrix returns
   404 / 530 / 1042 / connection-refused — NOT 200 / 401 / 403.
2. **Service Binding callers still work** after Phase 1 (admin-api,
   portal-proxy, paypal-webhook public endpoints don't 5xx).
3. **CI catches regressions** if `workers_dev = true` sneaks back into a
   wrangler.toml for any SB-only Worker.

---

## Files

| File | What it does |
|------|-------------|
| `check-wrangler-no-workers-dev.sh` | Static assertion. Grep wrangler.toml. Fails CI if SB-only Worker has `workers_dev = true` (or, post-Phase-1, missing line). |
| `test-sb-only-public-blocked.sh` | Live external probe matrix (6 probes) against `clients-api.in0v8.workers.dev`. Varies verb / UA / headers / path per CTO probe-dimension rule. |
| `test-sb-binding-still-works.sh` | Positive smoke. 4 public endpoints across admin-api / paypal-webhook / portal-proxy. Asserts no 5xx. |
| `test-spec25-readme.md` | This file. |

---

## How to run

### Pre-Phase-1 baseline (TODAY)

This is the expected state right now: `clients-api` has `workers_dev = true`
(default) and the secret-based gate is still active. Tests should report
"baseline" verdicts.

```bash
# 1) Static assertion (lenient mode — pre-Phase-1)
bash /home/jared/projects/AI-CIV/aether/tools/spec25-tests/check-wrangler-no-workers-dev.sh
# Expected: VERDICT: PASS (pre-Phase-1 baseline)

# 2) External probe matrix
bash /home/jared/projects/AI-CIV/aether/tools/spec25-tests/test-sb-only-public-blocked.sh
# Expected: every probe shows BASELINE (app-layer response, code 200/401/403/etc.)
#           VERDICT: PASS (Baseline established.)

# 3) Caller smoke
bash /home/jared/projects/AI-CIV/aether/tools/spec25-tests/test-sb-binding-still-works.sh
# Expected: at least admin-api /api/check-name returns 200/400/401 (not 502)
#           VERDICT: PASS
```

### Post-Phase-1 strict (after clients-api ships with `workers_dev = false`)

After Phase 1 deploys, run with `SPEC_25_PHASE_1_SHIPPED=1` and expect the
external probes to FLIP from baseline app-layer responses to CF network-layer
blocks.

```bash
# 1) Static assertion (strict)
SPEC_25_PHASE_1_SHIPPED=1 \
  bash /home/jared/projects/AI-CIV/aether/tools/spec25-tests/check-wrangler-no-workers-dev.sh
# Expected: VERDICT: PASS (workers_dev = false on clients-api)

# 2) External probe matrix (strict)
SPEC_25_PHASE_1_SHIPPED=1 \
  bash /home/jared/projects/AI-CIV/aether/tools/spec25-tests/test-sb-only-public-blocked.sh
# Expected: every probe returns 404/530/1042/connection-refused
#           VERDICT: PASS (CF block effective)

# 3) Caller smoke (unchanged — must still PASS post-Phase-1)
bash /home/jared/projects/AI-CIV/aether/tools/spec25-tests/test-sb-binding-still-works.sh
# Expected: VERDICT: PASS — SB binding still works internally
```

---

## What failure looks like

### Failure mode A: `workers_dev = false` is NOT effective after Phase 1

```
naked-post-default-ua    POST   200   FAIL (app-layer response — workers_dev=false not effective)
```

**Action per CTO**: STOP Phase 1 rollout. Pivot to Option B everywhere
(path-prefix + marker as soft gate). Open CF support ticket. Re-run
`wrangler versions deploy` and confirm version-mode propagation.

### Failure mode B: Phase 1 deploy broke Service Binding calls

```
admin-api /api/check-name    code=502    FAIL (binding=REQUIRED; 502 suggests broken SB)
```

**Action**: `wrangler tail clients-api` → look for "service binding not found"
or 4xx-from-callee. Rollback per SPEC §10.3 (re-add secret gate as OR
condition, redeploy clients-api previous version).

### Failure mode C: Someone reverted `workers_dev = false`

```
SPEC_25_PHASE_1_SHIPPED=1 ./check-wrangler-no-workers-dev.sh
FAIL: workers_dev line is absent (CF default = true) — must be 'workers_dev = false'
```

**Action**: Identify the PR that removed it (`git log -p clients-api/wrangler.toml`).
Restore. Re-deploy. This is exactly the regression CTO OQ-5 asked us to
prevent — the CI gate fired correctly.

---

## Probe-dimension audit (per `feedback_probe_dimension_audit_at_convergence_3plus.md`)

We vary multiple dimensions to avoid the "constant dimension is the suspect" trap:

| Dimension | Variation |
|-----------|-----------|
| Verb | POST, GET, PUT |
| UA | default curl, Mozilla, (none) |
| Headers | with/without `x-internal-binding` marker |
| Path | `/internal/clients/upsert`, `/internal/clients/by-email`, `/health` |
| Body | empty, JSON-with-email, JSON-empty-object |

**NOT used** (deliberately): OPTIONS preflight. Per
`feedback_options_preflight_success_does_not_equal_endpoint_health.md`,
OPTIONS 204 is generic CORS middleware response and does NOT prove the
underlying route exists or is gated.

---

## Constitutional alignment

- `feedback_synthetic_monitors_must_match_real_user_traffic.md`
  → Clean URLs only, no cache-bust query strings.
- `feedback_options_preflight_success_does_not_equal_endpoint_health.md`
  → Real client verbs (POST/GET). No OPTIONS as health probe.
- `feedback_multi_probe_diagnosis_required.md`
  → Multiple probes (6 external + 4 caller-side = 10 total).
- `feedback_probe_dimension_audit_at_convergence_3plus.md`
  → Vary tool input on every dimension.
- `feedback_skill_filed_does_not_equal_skill_enforced.md`
  → The wrangler.toml gate is wired (not just documented).
- `feedback_re-verification_methodology_must_vary.md`
  → check-wrangler script greps two ways (literal `true` + general regex).

---

## CI integration TODO (for ST3 / devops-engineer)

Add to CI pipeline (e.g., `.github/workflows/spec25-gate.yml` or equivalent):

```yaml
- name: SPEC-25 wrangler workers_dev assertion
  run: |
    bash tools/spec25-tests/check-wrangler-no-workers-dev.sh
  env:
    SPEC_25_PHASE_1_SHIPPED: ${{ vars.SPEC_25_PHASE_1_SHIPPED }}
```

For pre-commit (optional):
```bash
# .git/hooks/pre-commit
bash tools/spec25-tests/check-wrangler-no-workers-dev.sh || exit 1
```

---

## Phase 1 promotion criteria

Phase 1 (clients-api `workers_dev = false`) can promote to 100% traffic only
when ALL of these are true:

- [ ] Baseline run completed; results recorded in this branch
- [ ] `check-wrangler-no-workers-dev.sh` (strict) PASSES on the Phase-1 commit
- [ ] `test-sb-only-public-blocked.sh` (strict) PASSES within 150s of deploy
- [ ] `test-sb-binding-still-works.sh` PASSES (admin-api & portal-proxy)
- [ ] CTO OQ-1 canary evidence collected (no transient public-URL exposure)

---

**End of README**
