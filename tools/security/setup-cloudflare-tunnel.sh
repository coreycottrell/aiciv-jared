#!/bin/bash
#
# Setup Cloudflare Tunnel for PureBrain API Server
#
# Run this script ON THE 89.167.19.20 SERVER (not on the dev machine).
#
# What this script does:
#   1. Installs cloudflared
#   2. Authenticates with Cloudflare (opens browser or shows URL)
#   3. Creates a named tunnel: "purebrain-api"
#   4. Configures the tunnel to forward https://api.purebrain.ai -> localhost:8443
#   5. Installs cloudflared as a systemd service (auto-restart on reboot)
#
# Prerequisites:
#   - You must be logged in as a user with sudo
#   - The 89.167.19.20 server must have internet access
#   - You must have Cloudflare access for the purebrain.ai zone
#
# After running this script, Jared must:
#   1. Complete the browser auth step (URL printed by script)
#   2. Add CNAME in Cloudflare DNS: api.purebrain.ai -> <tunnel-id>.cfargotunnel.com
#
# Usage:
#   chmod +x setup-cloudflare-tunnel.sh
#   sudo ./setup-cloudflare-tunnel.sh
#
# ============================================================

set -euo pipefail

TUNNEL_NAME="purebrain-api"
SERVICE_HOSTNAME="api.purebrain.ai"
LOCAL_URL="https://localhost:8443"
CLOUDFLARED_CONFIG_DIR="/etc/cloudflared"
CLOUDFLARED_CONFIG_FILE="${CLOUDFLARED_CONFIG_DIR}/config.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${BLUE}==== $1 ====${NC}"; }

# ============================================================
# Step 1: Check we're running with sudo
# ============================================================
log_step "Step 1: Checking permissions"

if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

log_info "Running as root. Good."

# ============================================================
# Step 2: Install cloudflared
# ============================================================
log_step "Step 2: Installing cloudflared"

if command -v cloudflared &>/dev/null; then
    log_info "cloudflared already installed: $(cloudflared --version)"
else
    log_info "Downloading and installing cloudflared..."

    # Detect architecture
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)   CF_ARCH="amd64" ;;
        aarch64)  CF_ARCH="arm64" ;;
        armv7l)   CF_ARCH="armv7" ;;
        *)
            log_error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac

    log_info "Architecture: ${ARCH} -> cloudflared arch: ${CF_ARCH}"

    # Try package manager first (Debian/Ubuntu)
    if command -v apt-get &>/dev/null; then
        log_info "Using apt to install cloudflared..."
        # Add Cloudflare's package repository
        mkdir -p /etc/apt/keyrings
        curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | \
            tee /etc/apt/keyrings/cloudflare-main.gpg >/dev/null
        echo "deb [signed-by=/etc/apt/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | \
            tee /etc/apt/sources.list.d/cloudflared.list
        apt-get update -qq
        apt-get install -y cloudflared
    else
        # Fallback: download binary directly
        log_info "Downloading cloudflared binary directly..."
        CF_VERSION=$(curl -s https://api.github.com/repos/cloudflare/cloudflared/releases/latest | \
            grep '"tag_name"' | cut -d'"' -f4)
        CF_URL="https://github.com/cloudflare/cloudflared/releases/download/${CF_VERSION}/cloudflared-linux-${CF_ARCH}"
        curl -fsSL "${CF_URL}" -o /usr/local/bin/cloudflared
        chmod +x /usr/local/bin/cloudflared
    fi

    log_info "cloudflared installed: $(cloudflared --version)"
fi

# ============================================================
# Step 3: Authenticate with Cloudflare
# ============================================================
log_step "Step 3: Authenticating with Cloudflare"

CERT_FILE="/root/.cloudflared/cert.pem"

if [ -f "${CERT_FILE}" ]; then
    log_info "Cloudflare credentials already exist at ${CERT_FILE}"
    log_info "Skipping authentication step."
else
    log_warn "You need to authenticate cloudflared with your Cloudflare account."
    log_warn ""
    log_warn "This will print a URL. Open it in a browser and log in to Cloudflare."
    log_warn "Select the purebrain.ai zone when prompted."
    log_warn ""
    echo "Press Enter to continue..."
    read -r

    # Run login — this opens a browser or prints a URL
    cloudflared tunnel login

    if [ ! -f "${CERT_FILE}" ]; then
        log_error "Authentication failed. cert.pem not found at ${CERT_FILE}"
        log_error "Please re-run this script after completing the Cloudflare login."
        exit 1
    fi

    log_info "Authentication successful."
fi

# ============================================================
# Step 4: Create the tunnel
# ============================================================
log_step "Step 4: Creating tunnel: ${TUNNEL_NAME}"

# Check if tunnel already exists
EXISTING_TUNNEL=$(cloudflared tunnel list 2>/dev/null | grep "${TUNNEL_NAME}" | awk '{print $1}' || true)

if [ -n "${EXISTING_TUNNEL}" ]; then
    log_info "Tunnel '${TUNNEL_NAME}' already exists with ID: ${EXISTING_TUNNEL}"
    TUNNEL_ID="${EXISTING_TUNNEL}"
else
    log_info "Creating new tunnel: ${TUNNEL_NAME}"
    cloudflared tunnel create "${TUNNEL_NAME}"
    TUNNEL_ID=$(cloudflared tunnel list 2>/dev/null | grep "${TUNNEL_NAME}" | awk '{print $1}')
    log_info "Tunnel created with ID: ${TUNNEL_ID}"
fi

# Find the credentials file
CREDENTIALS_FILE="/root/.cloudflared/${TUNNEL_ID}.json"
if [ ! -f "${CREDENTIALS_FILE}" ]; then
    log_error "Tunnel credentials file not found: ${CREDENTIALS_FILE}"
    log_error "Something went wrong with tunnel creation."
    exit 1
fi
log_info "Credentials file: ${CREDENTIALS_FILE}"

# ============================================================
# Step 5: Write tunnel configuration
# ============================================================
log_step "Step 5: Writing tunnel configuration"

mkdir -p "${CLOUDFLARED_CONFIG_DIR}"

cat > "${CLOUDFLARED_CONFIG_FILE}" <<EOF
# Cloudflare Tunnel configuration for PureBrain API
# Auto-generated by setup-cloudflare-tunnel.sh on $(date)

tunnel: ${TUNNEL_ID}
credentials-file: ${CREDENTIALS_FILE}

# Ingress rules: route traffic to local server
ingress:
  - hostname: ${SERVICE_HOSTNAME}
    service: ${LOCAL_URL}
    originRequest:
      # Skip TLS verification for the local self-signed cert
      # This is safe because it's localhost traffic (not going over the internet)
      noTLSVerify: true
      connectTimeout: 30s
      tcpKeepAlive: 30s

  # Catch-all rule (required by cloudflared)
  - service: http_status:404
EOF

log_info "Config written to: ${CLOUDFLARED_CONFIG_FILE}"
cat "${CLOUDFLARED_CONFIG_FILE}"

# ============================================================
# Step 6: Route DNS (via Cloudflare)
# ============================================================
log_step "Step 6: Adding DNS route"

log_info "Creating DNS CNAME: ${SERVICE_HOSTNAME} -> ${TUNNEL_ID}.cfargotunnel.com"

# This creates the CNAME in Cloudflare automatically
cloudflared tunnel route dns "${TUNNEL_NAME}" "${SERVICE_HOSTNAME}" || {
    log_warn "Automatic DNS routing failed (may already exist or need manual setup)."
    log_warn ""
    log_warn "MANUAL STEP REQUIRED:"
    log_warn "  1. Log into https://dash.cloudflare.com"
    log_warn "  2. Go to purebrain.ai zone -> DNS"
    log_warn "  3. Add CNAME record:"
    log_warn "     Name: api"
    log_warn "     Target: ${TUNNEL_ID}.cfargotunnel.com"
    log_warn "     Proxy status: Proxied (orange cloud)"
    log_warn ""
}

# ============================================================
# Step 7: Install as systemd service
# ============================================================
log_step "Step 7: Installing cloudflared as systemd service"

# cloudflared has a built-in service installer
cloudflared service install || log_warn "Service install had a warning (may already be installed)"

# Ensure the config is in the right place for the service
SERVICE_CONFIG="/etc/cloudflared/config.yml"
if [ "${CLOUDFLARED_CONFIG_FILE}" != "${SERVICE_CONFIG}" ]; then
    cp "${CLOUDFLARED_CONFIG_FILE}" "${SERVICE_CONFIG}"
fi

# Start and enable the service
systemctl enable cloudflared
systemctl restart cloudflared

# Check status
sleep 3
if systemctl is-active --quiet cloudflared; then
    log_info "cloudflared service is running!"
else
    log_error "cloudflared service failed to start. Check: journalctl -u cloudflared -n 50"
fi

# ============================================================
# Step 8: Test the tunnel
# ============================================================
log_step "Step 8: Testing the tunnel"

log_info "Waiting 10 seconds for tunnel to establish..."
sleep 10

log_info "Testing local endpoint..."
LOCAL_TEST=$(curl -sk https://localhost:8443/api/health 2>/dev/null || echo "FAILED")
if echo "${LOCAL_TEST}" | grep -q '"status"'; then
    log_info "Local endpoint OK: ${LOCAL_TEST}"
else
    log_warn "Local endpoint test failed. Is purebrain_log_server.py running?"
    log_warn "Start it with: cd /home/jared/projects/AI-CIV/aether && ./tools/launch_purebrain_log_server.sh start"
fi

log_info "Testing tunnel endpoint (DNS propagation may take a few minutes)..."
TUNNEL_TEST=$(curl -s "https://${SERVICE_HOSTNAME}/api/health" 2>/dev/null || echo "PENDING")
if echo "${TUNNEL_TEST}" | grep -q '"status"'; then
    log_info "Tunnel endpoint OK: ${TUNNEL_TEST}"
else
    log_warn "Tunnel test returned: ${TUNNEL_TEST}"
    log_warn "This is normal if DNS is still propagating. Try again in 2-5 minutes:"
    log_warn "  curl https://${SERVICE_HOSTNAME}/api/health"
fi

# ============================================================
# Summary
# ============================================================
log_step "Setup Complete - Summary"

echo ""
echo -e "${GREEN}Cloudflare Tunnel setup complete!${NC}"
echo ""
echo "Tunnel Details:"
echo "  Tunnel Name:  ${TUNNEL_NAME}"
echo "  Tunnel ID:    ${TUNNEL_ID}"
echo "  Public URL:   https://${SERVICE_HOSTNAME}"
echo "  Backend:      ${LOCAL_URL}"
echo ""
echo "Service Status:"
systemctl status cloudflared --no-pager -l | head -15
echo ""
echo "Next Steps (if DNS CNAME was not auto-created above):"
echo "  1. Log into https://dash.cloudflare.com -> purebrain.ai -> DNS"
echo "  2. Add CNAME: api -> ${TUNNEL_ID}.cfargotunnel.com (Proxied)"
echo ""
echo "After DNS propagates, run on dev machine:"
echo "  python3 tools/security/update-endpoint-urls.py"
echo ""
echo "Verify with:"
echo "  curl https://${SERVICE_HOSTNAME}/api/health"
