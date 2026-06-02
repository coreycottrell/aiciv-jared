---
name: runtime-source-triplet-check
description: Mandatory triplet verification before restarting any non-Worker service (Python/Node/systemd unit). Prevents the runtime-source-mismatch drift class where the merged authoritative repo is NOT the repo the running service reads from. Trigger before ANY systemctl restart, pm2 reload, supervisorctl restart, or equivalent.
when_to_use: Before restarting any systemd service, pm2 process, supervisord-managed worker, or daemon whose source comes from a git checkout — especially after merging a PR you believe will go live on restart.
constitutional_layer: defensive (4th git-drift class — extends feedback_48h_4_instance_git_drift_institutional_pattern.md)
discovered: 2026-05-17
origin: devops-engineer learning — purebrain-portal PR #1 merged to puretechnyc/purebrain-portal but the running aether-portal.service reads from /home/jared/purebrain_portal/ which is on coreycottrell remote with a dirty working tree at HEAD fa4d894
status: provisional
tick_count: 0
last_used: 2026-05-17
introduced: 2026-05-17
---

# Runtime-Source Triplet Check

## The Hidden Drift Class

You merged a PR. You're about to `systemctl restart <service>`. **STOP.** The running service may not even read from the repo you just merged into. This is the 4th git-drift class:

> **Runtime-source mismatch**: the merged authoritative repo and the running service's source repo are different remotes / different branches / different SHAs / dirty working trees.

If you restart blindly, you come back on stale code AND falsely report "shipped." The audit trail says PR landed; production says nothing changed.

## The Triplet (NON-SKIPPABLE)

Before every restart, run these three checks in ONE shell invocation:

```bash
set -euo pipefail

RUNTIME_DIR="/home/jared/purebrain_portal"
EXPECTED_REMOTE="puretechnyc/purebrain-portal"
EXPECTED_SHA="651c16bd4d"          # the merge SHA from the PR

# ----- CHECK 1: remote alignment -----
ACTUAL_REMOTE=$(git -C "$RUNTIME_DIR" remote get-url origin)
echo "$ACTUAL_REMOTE" | grep -q "$EXPECTED_REMOTE" || {
  echo "FAIL: runtime dir points at $ACTUAL_REMOTE not $EXPECTED_REMOTE"
  echo "      restart would NOT pick up the PR — STOP"
  exit 1
}

# ----- CHECK 2: SHA alignment -----
RUNTIME_HEAD=$(git -C "$RUNTIME_DIR" log -1 --format=%H)
git -C "$RUNTIME_DIR" log --oneline "${EXPECTED_SHA}^..HEAD" >/dev/null 2>&1 || {
  echo "FAIL: runtime HEAD $RUNTIME_HEAD does not contain $EXPECTED_SHA"
  echo "      pull or reconcile before restart"
  exit 1
}

# ----- CHECK 3: clean working tree -----
DIRTY=$(git -C "$RUNTIME_DIR" status --porcelain)
[ -z "$DIRTY" ] || {
  echo "FAIL: dirty working tree in $RUNTIME_DIR"
  echo "$DIRTY"
  echo "      restart would run uncommitted local changes — STOP"
  exit 1
}

# ----- ALL GREEN — restart safely -----
sudo systemctl restart aether-portal
sleep 3
sudo systemctl status aether-portal --no-pager | head -20
```

## How to Find a Service's Runtime Source

For systemd:
```bash
systemctl cat <service-name> | grep -E '^(WorkingDirectory|ExecStart)='
```

For pm2:
```bash
pm2 describe <app> | grep -i 'exec cwd\|script path'
```

For supervisord:
```bash
supervisorctl status <name>
grep -A3 "\\[program:<name>\\]" /etc/supervisor/conf.d/*.conf | grep -i 'command\\|directory'
```

Then run the triplet against that directory.

## Compatible Skills

- Pair with `concurrent-agent-git-safety` — verify the runtime-dir reflog hasn't moved between your check and the restart.
- Pair with `verification-before-completion` — post-restart probe (curl health endpoint) is the receipt.
- Pair with `independent-pair-verification` — a different agent probes the live system after restart.

## Decision Tree

```
About to restart service?
├── Is it a CF Worker?  → Use wrangler-deploy flow instead (different rules)
├── Is it a Cloudflare Pages?  → Use github:push flow (no manual restart)
└── Is it systemd/pm2/supervisord/cron?
    └── RUN TRIPLET CHECK
        ├── PASS → restart + post-restart probe
        └── FAIL → STOP, report to Aether/Jared, do NOT restart
```

## Anti-Patterns

- **"It's just a restart"** — never just a restart when the running code's provenance is uncertain.
- **"The PR is merged, so it'll be picked up"** — only if the running service reads from the same remote/branch.
- **"`git pull` first"** — only safe if the working tree is clean and the remote is correct. The triplet covers both.
- **Restarting to "test the PR"** — if the service reads from a different repo, you're testing nothing.

## Receipt Format

After PASS + restart:

```
RUNTIME-SOURCE-TRIPLET: PASS
  remote:   puretechnyc/purebrain-portal ✓
  HEAD:     651c16bd4d (contains expected PR merge SHA) ✓
  dirty:    none ✓
RESTART:    aether-portal.service active (running)
POST-PROBE: GET https://portal.purebrain.ai/health → 200
```

After FAIL:

```
RUNTIME-SOURCE-TRIPLET: FAIL (remote mismatch)
  expected: puretechnyc/purebrain-portal
  actual:   coreycottrell/purebrain-portal
ACTION:     restart BLOCKED; awaiting reconcile decision
```

## Constitutional Anchors

- Git is the only source of truth (MEMORY.md line 6, line 7).
- Convergence must pair with prod verification (`feedback_convergence_must_pair_with_prod_verification.md`).
- Cross-BOOP convergence signal (`feedback_cross_boop_convergence_signal.md`).
