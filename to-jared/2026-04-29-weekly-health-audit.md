# System Health Audit - 2026-04-29

> **Filing note**: skill specifies `.claude/memory/health-audits/` but that path is permission-protected. Filed to `to-jared/` for visibility. Recommend whitelisting the path or adjusting the skill.

## Overall Status: YELLOW

| # | Category | Status | Details |
|---|----------|--------|---------|
| 1 | Zombie/Orphan Processes | GREEN | 0 zombies |
| 2 | Memory & Disk | YELLOW | RAM 53% (2.0G/3.7G), Swap 47% (966M/2G), Root disk 74% (27G/38G) |
| 3 | Running Services | YELLOW | Critical services up; 1 failed unit (blog-distribution.service); aether-telegram inactive but aether-telegram-bridge active (rename) |
| 4 | Stale PID Files | YELLOW | 2 stale PID files auto-cleaned |
| 5 | tmux Sessions | GREEN | 1 attached session (aether-20260412-fresh) |
| 6 | Port Conflicts | GREEN | No duplicate listeners on ports 80/443/3000/3001/5000/8080/8950 |
| 7 | Log File Sizes | GREEN | Largest 33MB; all <100MB; journal 92.5MB |
| 8 | Claude Code Sessions | GREEN | 8 procs / 1437MB RSS / 0 stale JSONLs / .claude=25M |
| 9 | Cron Jobs | GREEN | 10 entries, no duplicates, no recent failures |
| 10 | Recent Crashes | YELLOW | 0 OOM, 0 unexpected reboots; purebrain-video-gui.service in 5s restart loop (working dir missing) |

## Auto-Fixed Issues
- Removed stale `.boop_executor.pid` (PID 1715626 not running)
- Removed stale `.telegram_bridge.pid` (PID 1958164 not running)
- 0 JSONLs eligible for pruning (none >7d in /tmp)
- 0 logs needed truncation (largest 33MB, threshold 200MB)

## Issues Requiring Human Attention

1. **purebrain-video-gui.service restart loop** — WorkingDirectory `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui` does not exist. With `Restart=always` + 5s `RestartSec`, the unit fails every 5s and spams journald. Fix: restore the directory, repoint WorkingDirectory in `/etc/systemd/system/purebrain-video-gui.service`, or `sudo systemctl disable --now purebrain-video-gui.service`.

2. **blog-distribution.service failed** — single failed unit. Auto-restart blocked by polkit (Interactive authentication required). Needs `sudo systemctl restart blog-distribution.service`.

3. **Health-check skill out of date** — monitors `aether-telegram` but the active unit is now `aether-telegram-bridge`. Update `weekly-health-check/SKILL.md` Check 3 service list.

4. **Health-audits dir permission-protected** — Write tool blocks `.claude/memory/health-audits/`. Either whitelist the path or change skill output location.

5. **Swap 47%, root disk 74%** — both in YELLOW band, close to escalation thresholds. Cleanup pass recommended.

## Recommended Actions (priority order)

1. Fix purebrain-video-gui.service (highest log spam impact)
2. Restart/remove blog-distribution.service
3. Patch weekly-health-check skill for renamed services + writable audit dir
4. Schedule log rotation review for top-3 logs (paypal_webhook 33M, log_server 22M, boop_executor 20M = ~75MB combined)
5. Monitor swap/disk weekly — escalate if either crosses YELLOW band

## Trend Comparison
- Previous audit: NONE — `.claude/memory/health-audits/` empty (or inaccessible)
- Current audit: 2026-04-29 | Overall: YELLOW
- Trend: BASELINE ESTABLISHED

## Snapshot Data
- Memory: total 3.7Gi / used 2.0Gi / available 1.7Gi
- Swap: 989556 KB used of 2097148 KB (~47%)
- Disk /: 27G/38G (74%), 9.6G free
- Critical services up: aether-portal, aether-session, cloudflared, nginx, aether-telegram-bridge
- Failed units: blog-distribution.service
- Top memory consumer: claude PID 2728841 (701MB RSS, since Apr 12)
- Last reboots: Mar 12 (current), Jan 29 (prior)
