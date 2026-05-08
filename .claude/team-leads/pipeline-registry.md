# Pipeline Registry — Automated Zero-Cost Workflows

Scripts that run on loops/crons without consuming model tokens. Only escalate to agents on exceptions.

| Pipeline | File | Port | What It Does | Restart Command |
|----------|------|------|-------------|-----------------|
| BOOP Executor | tools/boop_executor.py | N/A | Fires scheduled tasks (BOOPs) every 5min | `nohup python3 tools/boop_executor.py >> logs/boop_executor.log 2>&1 &` |
| AgentMail Monitor | tools/agentmail_monitor.py | N/A | Watches seed inbox for Witness magic links, rewrites domains | `nohup python3 tools/agentmail_monitor.py >> logs/agentmail_monitor.log 2>&1 &` |
| AgentMail General | tools/agentmail_general_monitor.py | N/A | Monitors general inbox, categorizes, alerts | `nohup python3 tools/agentmail_general_monitor.py >> logs/agentmail_general.log 2>&1 &` |
| PayPal Auto-Split | tools/paypal_auto_split.py --webhook | 8960 | PayPal webhook handler + revenue split + commission recording | `nohup python3 tools/paypal_auto_split.py --webhook >> logs/paypal_webhook.log 2>&1 &` |
| Log Server | tools/purebrain_log_server.py | 8443 | Payment logging, seed emails, client tracking | `nohup python3 tools/purebrain_log_server.py >> logs/log_server.log 2>&1 &` |
| Telegram Bridge | tools/telegram_bridge.py | N/A | 2-way Telegram sync (system notifications only) | `nohup python3 tools/telegram_bridge.py >> logs/telegram_bridge.log 2>&1 &` |
| Portal Server | purebrain_portal/portal_server.py | 8097 | Admin portal, referral system, client management | `nohup python3 portal_server.py >> portal_server.log 2>&1 &` |
| Creator AI | tools/creator-ai/main.py | 8871 | Social/creator AI interface | Check systemd or manual start |

## Escalation Rules
- Pipeline script errors → check logs first, restart if transient
- Repeated failures (3+) → escalate to ST# for investigation
- Payment-related failures → escalate IMMEDIATELY to ST# + notify Jared
- New capability needed → propose as pipeline BEFORE building as agent (zero-cost first)
