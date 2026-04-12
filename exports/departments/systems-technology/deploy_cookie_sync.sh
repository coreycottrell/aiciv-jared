#!/bin/bash
# Deploy Cookie Sync Page to PureSurf server
# Usage: bash deploy_cookie_sync.sh

set -e

SERVER="root@157.180.69.225"
BAAS_DIR="/opt/baas"

echo "=== PureSurf Cookie Sync Page Deployment ==="

# Step 1: Upload the module
echo "[1/4] Uploading cookie_sync_page.py..."
scp "$(dirname "$0")/cookie_sync_page.py" "${SERVER}:${BAAS_DIR}/cookie_sync_page.py"

# Step 2: Patch baas_server_simple.py to import and mount the sync routes
echo "[2/4] Patching baas_server_simple.py..."
ssh "$SERVER" bash <<'REMOTE_SCRIPT'
cd /opt/baas

# Backup
cp baas_server_simple.py baas_server_simple.py.bak.$(date +%Y%m%d%H%M%S)

# Check if already patched
if grep -q "cookie_sync_page" baas_server_simple.py; then
    echo "  Already patched - skipping import"
else
    # Add import after the existing imports
    sed -i '/^from tiktok_reddit_adapters import/a from cookie_sync_page import extend_sync_routes' baas_server_simple.py

    # Add route mounting before the uvicorn.run line
    # We need to pass the required functions
    cat >> baas_server_simple.py.mount_patch <<'PATCH'

# ==================== COOKIE SYNC PAGE ====================
extend_sync_routes(
    app=app,
    sessions=sessions,
    auth_fn=auth,
    launch_fn=_launch,
    save_cookies_fn=_save_cookies,
    cookies_path_fn=_cookies_path,
    profile_cookies_path_fn=_profile_cookies_path,
    encrypt_cookies_fn=_encrypt_cookies,
    decrypt_cookies_fn=_decrypt_cookies,
    profiles_dir=PROFILES_DIR,
)
PATCH

    # Insert the mount code before 'if __name__'
    # Find the line number of 'if __name__'
    LINE=$(grep -n "if __name__ == '__main__':" baas_server_simple.py | tail -1 | cut -d: -f1)
    if [ -n "$LINE" ]; then
        # Insert the patch content before that line
        sed -i "$((LINE-1))r baas_server_simple.py.mount_patch" baas_server_simple.py
        rm -f baas_server_simple.py.mount_patch
        echo "  Import and mount code added"
    else
        echo "  ERROR: Could not find 'if __name__' line"
        rm -f baas_server_simple.py.mount_patch
        exit 1
    fi
fi
REMOTE_SCRIPT

# Step 3: Verify syntax
echo "[3/4] Verifying Python syntax..."
ssh "$SERVER" "cd /opt/baas && python3 -c 'import py_compile; py_compile.compile(\"baas_server_simple.py\", doraise=True)' && echo '  Syntax OK'"

# Step 4: Restart the service
echo "[4/4] Restarting PureSurf server..."
ssh "$SERVER" "systemctl restart puresurf 2>/dev/null || (cd /opt/baas && pkill -f 'baas_server_simple' && sleep 2 && nohup python3 baas_server_simple.py >> /var/log/puresurf.log 2>&1 &)"
sleep 3

# Verify
echo ""
echo "=== Verification ==="
HEALTH=$(ssh "$SERVER" "curl -s http://localhost:8901/health" 2>/dev/null)
echo "Health check: $HEALTH"

SYNC_CHECK=$(ssh "$SERVER" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8901/sync" 2>/dev/null)
echo "Sync page status: $SYNC_CHECK"

if [ "$SYNC_CHECK" = "200" ]; then
    echo ""
    echo "=== SUCCESS ==="
    echo "Cookie Sync page live at: https://surf.purebrain.ai/sync"
else
    echo ""
    echo "=== WARNING: Sync page returned $SYNC_CHECK ==="
    echo "Check logs: ssh $SERVER 'tail -50 /var/log/puresurf.log'"
fi
