# Cloudflare Tunnel: Interactive Login Pattern for Headless Servers

**Date**: 2026-02-20
**Type**: teaching
**Agent**: devops-engineer
**Task**: Install Cloudflare Tunnel on 89.167.19.20 for PureBrain API

---

## Context

Running `cloudflared tunnel login` on a headless server (no browser) requires capturing
the auth URL and having a human visit it. The process then waits (polls Cloudflare) and
downloads the cert automatically when the human completes OAuth.

## Headless Login Pattern

```bash
# Start login in background, redirect output to a log file
nohup sudo cloudflared tunnel login > /tmp/cf_login.txt 2>&1 &
echo "PID: $!"

# Wait a few seconds, then read the URL
sleep 6
cat /tmp/cf_login.txt
# Output includes: "https://dash.cloudflare.com/argotunnel?aud=&callback=..."
```

The process stays running, polling for completion. When the human completes OAuth in
their browser, cloudflared downloads `/root/.cloudflared/cert.pem` automatically.

## Key Details for This Server

- Server: 89.167.19.20 (user: jared, OS: Ubuntu 6.8.0-90-generic)
- cloudflared version: 2026.2.0 (already installed as of 2026-02-20)
- Auth cert lands at: `/root/.cloudflared/cert.pem` (root context, run with sudo)
- Login process runs as: `root` (PID varies)

## After Human Completes Auth

Once Jared visits the URL and selects the purebrain.ai zone:
1. `/root/.cloudflared/cert.pem` appears automatically
2. Can then run: `sudo cloudflared tunnel create purebrain-api`
3. Then write `/etc/cloudflared/config.yml`
4. Then: `sudo cloudflared service install && sudo systemctl enable --now cloudflared`

## Full Remaining Steps After Auth

```bash
# 1. Create tunnel
sudo cloudflared tunnel create purebrain-api

# 2. Get tunnel ID
TUNNEL_ID=$(sudo cloudflared tunnel list | grep purebrain-api | awk '{print $1}')

# 3. Write config
sudo mkdir -p /etc/cloudflared
sudo tee /etc/cloudflared/config.yml <<EOF
tunnel: ${TUNNEL_ID}
credentials-file: /root/.cloudflared/${TUNNEL_ID}.json
ingress:
  - hostname: api.purebrain.ai
    service: https://localhost:8443
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      tcpKeepAlive: 30s
  - service: http_status:404
EOF

# 4. Route DNS (auto-creates CNAME in Cloudflare)
sudo cloudflared tunnel route dns purebrain-api api.purebrain.ai

# 5. Install and start systemd service
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl restart cloudflared

# 6. Verify
systemctl status cloudflared
curl https://api.purebrain.ai/api/health
```

## Process Management Gotcha

When running `sudo cloudflared tunnel login` twice (e.g. a background job AND a
foreground command), two processes start and two different URLs are generated.
Only one URL needs to be used - but keep track of which process is current.

To kill all and start fresh:
```bash
sudo pkill -f "cloudflared tunnel login"
```

## URL Validity

Each generated URL is unique with a callback token. It's valid for ~10 minutes.
If it expires, kill the process and restart to get a new URL.
