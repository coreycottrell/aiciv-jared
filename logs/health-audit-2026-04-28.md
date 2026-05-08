# System Health Audit - 2026-04-28

## Overall Status: YELLOW

| # | Category | Status | Details |
|---|----------|--------|---------|
| 1 | Zombie/Orphan Processes | GREEN | 0 zombies |
| 2 | Memory & Disk | YELLOW | RAM 64% (2.4/3.7G), Swap 41% (830M/2G), Disk 68% |
| 3 | Running Services | RED | blog-distribution.service failed; aether-telegram.service inactive (bridge running via standalone PID file) |
| 4 | Stale PID Files | GREEN | 0 stale (.boop_executor.pid + .telegram_bridge.pid both alive) |
| 5 | tmux Sessions | GREEN | 1 active (aether-20260412-fresh) |
| 6 | Port Conflicts | GREEN | No duplicate listeners on 80/443/3000/3001/5000/8080/8950 |
| 7 | Log File Sizes | GREEN | Largest 31M (paypal_webhook), journal 90.9M, no logs >100M |
| 8 | Claude Code Sessions | GREEN | 9 processes / 1652MB; 73 stale JSONLs PRUNED |
| 9 | Cron Jobs | GREEN | 10 entries, 0 duplicates, no recent errors |
| 10 | Recent Crashes | YELLOW | 0 OOM, 0 reboots, but 39034 errors - almost all from purebrain-video-gui CHDIR crash loop |

## Auto-Fixed Issues
- Pruned 73 stale JSONL files (>7 days old) from /tmp

## Issues Requiring Human Attention

### 1. [RED] blog-distribution.service failing
- JSONDecodeError on tools/blog_distribution_pipeline.py check
- Last failure: 2026-04-28 20:52:31 UTC
- Likely cause: corrupt or empty JSON state file
- Action: Fix corrupt state file OR systemctl disable --now blog-distribution.timer if deprecated

### 2. [RED] purebrain-video-gui.service CHDIR crash loop
- Working directory /home/jared/projects/AI-CIV/aether/tools/video-pipeline/gui does NOT exist
- Auto-restarting every ~5 seconds -> ~39,000 failures in 7 days (source of journal noise)
- Action: systemctl disable --now purebrain-video-gui.service immediately

### 3. [YELLOW] aether-telegram.service inactive
- CLAUDE.md states this should be enabled for auto-restart on crash/reboot
- Currently disabled/inactive - bridge running via standalone PID 1203631
- Telegram FUNCTIONAL but no documented persistence guarantee
- Action: Re-enable systemd unit OR update CLAUDE.md to reflect new pattern

### 4. [YELLOW] Swap at 41%
- 830MB of 2GB swap, RAM 64%, host is small (3.7G total)
- 9 Claude processes consuming 1.65GB - sustainable but trending

## Recommended Actions (Prioritized)
1. NOW: systemctl disable --now purebrain-video-gui.service
2. NOW: Investigate/disable blog-distribution.service
3. TODAY: Decide aether-telegram.service path
4. THIS WEEK: Monitor swap, consider trimming Claude footprint

## Trend Comparison
- Previous audit: NONE (first weekly health check baseline)
- Current audit: 2026-04-28 | Overall: YELLOW
- Trend: BASELINE established

## Notes
- Customer-facing services (aether-portal, cloudflared, nginx) all healthy
- 73 stale JSONLs in 7 days suggests /tmp pruning should run more often than weekly
- NOTE: Could not write to .claude/memory/health-audits/ (permission denied) - saved here instead
