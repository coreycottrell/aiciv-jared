# System Health Audit - 2026-05-07

## Overall Status: YELLOW

| # | Category | Status | Details |
|---|----------|--------|---------|
| 1 | Zombie/Orphan Processes | GREEN | 0 zombies, 0 defunct |
| 2 | Memory & Disk | YELLOW | RAM 54%, Swap 50%, Disk 80% (29G/38G on /) |
| 3 | Running Services | YELLOW | `blog-distribution.service` FAILED; `purebrain-video-gui.service` in restart loop (missing cwd). All Aether-critical services active. |
| 4 | Stale PID Files | GREEN | 0 stale PID files in project root |
| 5 | tmux Sessions | GREEN | 1 session (aether-20260412-fresh, attached) |
| 6 | Port Conflicts | GREEN | No duplicate listeners on 80/443/3000/3001/5000/8080/8950 |
| 7 | Log File Sizes | GREEN | Largest log 49M (paypal_webhook). Journal 115M. /tmp clean. |
| 8 | Claude Code Sessions | GREEN | 6 processes, ~1015 MB total, 0 stale JSONL in /tmp |
| 9 | Cron Jobs | GREEN | 10 entries, no duplicates, no recent failures |
| 10 | Recent Crashes | YELLOW | 0 OOM kills, 0 unexpected reboots, but chronic `purebrain-video-gui` restart-loop spam in journal |

## Auto-Fixed Issues
- None required — no stale PIDs, no oversized logs (>200M threshold), no old JSONLs (>7d)

## Issues Requiring Human Attention

1. **Disk 80% on /** (29G used / 38G total, 7.3G free) — approaching YELLOW→RED threshold (90%). Recommend cleanup pass: `du -sh /var/log/*`, `journalctl --vacuum-size=50M`, prune old `exports/cf-pages-deploy/` snapshots.
2. **Swap 50% used (1.0G/2.0G)** — RAM pressure under WSL2 4GB allocation. Not critical but indicates working set exceeds RAM.
3. **`blog-distribution.service` FAILED** — needs ST# to investigate (`journalctl -u blog-distribution.service -n 100`).
4. **`purebrain-video-gui.service` restart loop** — service trying to chdir to non-existent directory, restarting every ~5s. Filling journal noise. Either fix WorkingDirectory= in unit file or `systemctl disable --now purebrain-video-gui.service`.

## Recommended Actions

1. **HIGH**: ST# fix `purebrain-video-gui.service` cwd error (silences chronic journal noise, cuts service-restart churn).
2. **HIGH**: ST# triage `blog-distribution.service` failure — pipeline impact unknown.
3. **MED**: Disk cleanup sweep — target /var/log, old exports, /tmp residue. Goal: <70% utilization.
4. **LOW**: Monitor swap usage trend; if persistent at 50%+ consider WSL2 memory increase via `.wslconfig`.

## Trend Comparison

- Previous audit: NONE (first audit on record)
- Current audit: 2026-05-07 | Overall: YELLOW
- Trend: BASELINE ESTABLISHED
- Notable: This is the first weekly health audit. Future audits will compare against this baseline.

## Baseline Snapshot (for next week)

- Disk: 29G/38G (80%)
- Journal: 115M
- Largest log: 49M (paypal_webhook_service.log)
- Active Aether services: 10/10
- Failed services: 1 (blog-distribution)
- Chronic restart loop services: 1 (purebrain-video-gui)
- Claude processes: 6 (~1015 MB)
- tmux sessions: 1
- Cron entries: 10
- Uptime: since 2026-03-12 (~57 days)
