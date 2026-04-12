#!/bin/bash
#
# Setup Let's Encrypt Certificate for PureBrain API Server (FALLBACK)
#
# Run this script ON THE 89.167.19.20 SERVER (not on the dev machine).
#
# This is the FALLBACK option if Cloudflare Tunnel doesn't work.
# Option B (Cloudflare Tunnel) is preferred. Use this only if tunnel fails.
#
# Prerequisites BEFORE running this script:
#   1. Jared has added an A record in Cloudflare DNS:
#      Type: A, Name: api, IPv4: 89.167.19.20, Proxy: DNS only (gray cloud)
#   2. DNS has propagated (verify: dig +short api.purebrain.ai -> should return 89.167.19.20)
#   3. Port 80 must be accessible from the internet (certbot HTTP challenge)
#
# What this script does:
#   1. Installs certbot
#   2. Gets a Let's Encrypt cert for api.purebrain.ai (standalone mode, uses port 80)
#   3. Updates the purebrain_log_server to use the new cert
#   4. Sets up cron for auto-renewal
#
# Usage:
#   chmod +x setup-letsencrypt.sh
#   sudo ./setup-letsencrypt.sh
#
# ============================================================

set -euo pipefail

DOMAIN="api.purebrain.ai"
CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"
AETHER_ROOT="/home/jared/projects/AI-CIV/aether"
ENV_FILE="${AETHER_ROOT}/.env"
SERVICE_FILE="/etc/systemd/system/purebrain-log-server.service"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${BLUE}==== $1 ====${NC}"; }

# ============================================================
# Step 0: Verify prerequisites
# ============================================================
log_step "Step 0: Verifying prerequisites"

if [ "$EUID" -ne 0 ]; then
    log_error "Must run as root (use sudo)"
    exit 1
fi

# Check DNS resolves correctly
log_info "Checking DNS for ${DOMAIN}..."
RESOLVED_IP=$(dig +short "${DOMAIN}" 2>/dev/null | head -1 || true)
SERVER_IP=$(curl -s https://ipinfo.io/ip 2>/dev/null || hostname -I | awk '{print $1}')

if [ -z "${RESOLVED_IP}" ]; then
    log_error "DNS not found for ${DOMAIN}"
    log_error "Jared must add an A record in Cloudflare DNS first:"
    log_error "  Type: A, Name: api, IPv4: ${SERVER_IP}, Proxy: DNS only (gray cloud)"
    exit 1
fi

if [ "${RESOLVED_IP}" != "${SERVER_IP}" ]; then
    log_warn "DNS ${DOMAIN} -> ${RESOLVED_IP}"
    log_warn "This server's IP: ${SERVER_IP}"
    log_warn "These should match. If Cloudflare is proxied (orange cloud), turn it to DNS only (gray cloud) first."
    echo "Continue anyway? (y/N)"
    read -r CONTINUE
    if [ "${CONTINUE}" != "y" ]; then
        exit 1
    fi
else
    log_info "DNS OK: ${DOMAIN} -> ${RESOLVED_IP}"
fi

# Check port 80 is available for certbot standalone mode
if ss -tlnp | grep -q ':80 '; then
    log_warn "Something is already using port 80. certbot standalone mode needs port 80 free."
    log_warn "Stop whatever is using port 80 before continuing."
    ss -tlnp | grep ':80 '
    echo "Continue anyway? (y/N)"
    read -r CONTINUE
    if [ "${CONTINUE}" != "y" ]; then
        exit 1
    fi
fi

# ============================================================
# Step 1: Install certbot
# ============================================================
log_step "Step 1: Installing certbot"

if command -v certbot &>/dev/null; then
    log_info "certbot already installed: $(certbot --version)"
else
    if command -v apt-get &>/dev/null; then
        log_info "Installing certbot via apt..."
        apt-get update -qq
        apt-get install -y certbot
    elif command -v snap &>/dev/null; then
        log_info "Installing certbot via snap..."
        snap install --classic certbot
        ln -sf /snap/bin/certbot /usr/bin/certbot
    else
        log_error "Cannot install certbot. Please install it manually."
        exit 1
    fi
    log_info "certbot installed: $(certbot --version)"
fi

# ============================================================
# Step 2: Get Let's Encrypt certificate
# ============================================================
log_step "Step 2: Getting Let's Encrypt certificate for ${DOMAIN}"

if [ -d "${CERT_DIR}" ]; then
    log_info "Certificate already exists at ${CERT_DIR}"
    log_info "Certificate details:"
    openssl x509 -in "${CERT_DIR}/cert.pem" -noout -subject -issuer -dates
else
    log_info "Requesting certificate via certbot standalone mode..."
    log_info "certbot will temporarily listen on port 80 to verify domain ownership."
    certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "jaredcmusic@gmail.com" \
        -d "${DOMAIN}"

    if [ -d "${CERT_DIR}" ]; then
        log_info "Certificate obtained successfully!"
        log_info "Certificate details:"
        openssl x509 -in "${CERT_DIR}/cert.pem" -noout -subject -issuer -dates
    else
        log_error "Certificate not found at ${CERT_DIR} after certbot run."
        exit 1
    fi
fi

FULLCHAIN="${CERT_DIR}/fullchain.pem"
PRIVKEY="${CERT_DIR}/privkey.pem"

# ============================================================
# Step 3: Update server configuration to use new cert
# ============================================================
log_step "Step 3: Updating server to use Let's Encrypt certificate"

# Update .env file with new cert paths
if [ -f "${ENV_FILE}" ]; then
    log_info "Updating cert paths in .env..."
    # Remove old SSL cert lines if they exist
    sed -i '/^SSL_CERT_FILE=/d' "${ENV_FILE}"
    sed -i '/^SSL_KEY_FILE=/d' "${ENV_FILE}"
    # Add new cert paths
    echo "SSL_CERT_FILE=${FULLCHAIN}" >> "${ENV_FILE}"
    echo "SSL_KEY_FILE=${PRIVKEY}" >> "${ENV_FILE}"
    log_info "Updated .env with new cert paths"
else
    log_warn ".env not found at ${ENV_FILE}"
    log_warn "Manually export before starting server:"
    log_warn "  export SSL_CERT_FILE=${FULLCHAIN}"
    log_warn "  export SSL_KEY_FILE=${PRIVKEY}"
fi

# ============================================================
# Step 4: Install systemd service with new cert
# ============================================================
log_step "Step 4: Installing/updating systemd service"

cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=PureBrain API Log Server (HTTPS)
After=network.target
Documentation=https://purebrain.ai

[Service]
Type=simple
User=jared
WorkingDirectory=${AETHER_ROOT}
Environment=SSL_CERT_FILE=${FULLCHAIN}
Environment=SSL_KEY_FILE=${PRIVKEY}
Environment=PUREBRAIN_LOG_PORT=8443
ExecStart=${AETHER_ROOT}/venv/bin/python3 ${AETHER_ROOT}/tools/purebrain_log_server.py
Restart=always
RestartSec=10
StandardOutput=append:${AETHER_ROOT}/logs/purebrain_log_server.log
StandardError=append:${AETHER_ROOT}/logs/purebrain_log_server.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable purebrain-log-server
systemctl restart purebrain-log-server

sleep 3
if systemctl is-active --quiet purebrain-log-server; then
    log_info "purebrain-log-server service is running with Let's Encrypt cert!"
else
    log_error "Service failed to start. Check: journalctl -u purebrain-log-server -n 50"
    exit 1
fi

# ============================================================
# Step 5: Set up auto-renewal
# ============================================================
log_step "Step 5: Setting up auto-renewal"

# Create renewal hook to restart the server after cert renewal
RENEWAL_HOOK_DIR="/etc/letsencrypt/renewal-hooks/post"
mkdir -p "${RENEWAL_HOOK_DIR}"

cat > "${RENEWAL_HOOK_DIR}/restart-purebrain-server.sh" <<'EOF'
#!/bin/bash
# Restart purebrain log server after cert renewal
systemctl restart purebrain-log-server
echo "PureBrain log server restarted with renewed cert at $(date)" >> /var/log/letsencrypt-renewal.log
EOF
chmod +x "${RENEWAL_HOOK_DIR}/restart-purebrain-server.sh"
log_info "Auto-renewal hook installed at ${RENEWAL_HOOK_DIR}/restart-purebrain-server.sh"

# Set up systemd timer for certbot (preferred over cron on modern systems)
if ! systemctl is-enabled --quiet certbot.timer 2>/dev/null; then
    # Some systems have the timer pre-installed
    log_info "Certbot timer status:"
    systemctl status certbot.timer --no-pager 2>/dev/null || log_warn "certbot.timer not found - cert renewal will be via snap/cron"
fi

# Test dry run renewal
log_info "Testing cert renewal (dry run)..."
certbot renew --dry-run --quiet && log_info "Dry run renewal OK" || log_warn "Dry run had issues - check certbot logs"

# ============================================================
# Step 6: Test the new endpoint
# ============================================================
log_step "Step 6: Testing new endpoint"

log_info "Testing with new certificate..."
TEST_RESULT=$(curl -s "https://${DOMAIN}/api/health" 2>/dev/null || echo "FAILED")

if echo "${TEST_RESULT}" | grep -q '"status"'; then
    log_info "SUCCESS! Endpoint working with trusted cert: ${TEST_RESULT}"
else
    log_warn "Test returned: ${TEST_RESULT}"
    log_warn "May need to wait for DNS propagation if Cloudflare proxy is orange cloud."
    log_warn "Test with: curl https://${DOMAIN}/api/health"
fi

# ============================================================
# Step 7: Update Cloudflare proxy status (optional but recommended)
# ============================================================
log_step "Step 7: Cloudflare proxy status"

log_warn "OPTIONAL MANUAL STEP:"
log_warn "After verifying the cert works, you can switch the Cloudflare DNS record"
log_warn "from 'DNS only' (gray cloud) to 'Proxied' (orange cloud) for:"
log_warn "  - DDoS protection"
log_warn "  - CDN caching"
log_warn "  - Cloudflare WAF"
log_warn ""
log_warn "Note: If you switch to Proxied, Let's Encrypt auto-renewal via standalone"
log_warn "mode may stop working (port 80 blocked by Cloudflare proxy)."
log_warn "In that case, switch to certbot DNS challenge or switch to Cloudflare Tunnel."

# ============================================================
# Summary
# ============================================================
log_step "Setup Complete - Summary"

echo ""
echo -e "${GREEN}Let's Encrypt certificate setup complete!${NC}"
echo ""
echo "Certificate Details:"
openssl x509 -in "${FULLCHAIN}" -noout -subject -issuer -dates
echo ""
echo "Service Status:"
systemctl status purebrain-log-server --no-pager -l | head -10
echo ""
echo "Endpoint:"
echo "  https://${DOMAIN}/api/health"
echo "  https://${DOMAIN}/api/log-conversation"
echo "  https://${DOMAIN}/api/verify-payment"
echo ""
echo "Next step: Run on dev machine to update WordPress pages:"
echo "  python3 /home/jared/projects/AI-CIV/aether/tools/security/update-endpoint-urls.py"
