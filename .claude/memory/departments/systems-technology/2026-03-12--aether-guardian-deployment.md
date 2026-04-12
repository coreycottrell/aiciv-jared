# Aether Guardian Deployment — 2026-03-12

## Summary
Deployed the Aether Guardian management page to purebrain.ai/aether-guardian/

## What Was Built
- Password-protected management page for Jared to SSH into and manage Aether
- Three sections: Health Check, Live Monitoring, Restart
- Modeled on russellkorus.com/keel/ (Keel Guardian)
- Dark theme (#080a12), PureBrain blue/orange colors
- Copy-to-clipboard buttons for all commands

## Infrastructure Found (Aether's Actual Setup)
- Server IP: 89.167.19.20 (Hetzner VPS)
- SSH user: jared
- Restart script: tools/aether-restart.sh (self-healing, creates aether-recovery-YYYYMMDD-HHMM session)
- tmux sessions: numbered (45, 47, 49, 52, 56) + "aether-unified"
- Systemd services: aether-session, aether-telegram, aether-portal, aether-comms-gateway, aether-logserver
- launch_primary_visible.sh: for manual starts
- NO restart-self.sh (uses aether-restart.sh instead)

## Deployment Method
- WP REST API BLOCKED by Cloudflare WAF on purebrain.ai (405 on all POST requests)
- WP login page (/wp-login.php) also intercepted by CF WAF (returns frontend HTML)
- Solution: Deployed via CF Pages Direct Upload using wrangler CLI
- CF Pages project: "purebrain" (account: d526a3e9498dd167509003004df03290)
- Token env var: CF_PAGES_TOKEN

## Deploy Command
```bash
cd /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy
CLOUDFLARE_API_TOKEN="HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_" \
npx wrangler pages deploy . --project-name=purebrain --branch=main --commit-dirty=true
```

## Files
- CF Pages source: exports/cf-pages-deploy/aether-guardian/index.html
- WP HTML version: exports/departments/systems-technology/aether-guardian.html
- Deploy script: tools/deploy_aether_guardian.py (Playwright, not working due to CF WAF)

## Notes
- CF email obfuscation: CF protects user@IP patterns in HTML. Works correctly in real browsers (CF JS decodes it client-side). For future builds, use JavaScript to assemble SSH addresses to avoid obfuscation issues.
- Password: purebrain2026

## Live URL
https://purebrain.ai/aether-guardian/
