#!/bin/bash
# =============================================================================
# PureBrain Customer SSH Keypair Provisioning
# =============================================================================
# Purpose: Generate a unique ed25519 SSH keypair for each portal customer,
#          store the private key in the ops vault, and output the public key
#          for injection into the customer's authorized_keys.
#
# Usage:
#   ./tools/ssh-keypair-provision.sh CUSTOMER_ID [CUSTOMER_EMAIL]
#   ./tools/ssh-keypair-provision.sh revoke CUSTOMER_ID
#   ./tools/ssh-keypair-provision.sh list
#   ./tools/ssh-keypair-provision.sh audit
#
# Examples:
#   ./tools/ssh-keypair-provision.sh cust_abc123 "user@example.com"
#   ./tools/ssh-keypair-provision.sh revoke cust_abc123
#   ./tools/ssh-keypair-provision.sh list
#
# Vault location: /home/jared/projects/AI-CIV/aether/.ops-vault/ssh-keys/
# Audit log:     /home/jared/projects/AI-CIV/aether/.ops-vault/audit.log
# =============================================================================

set -euo pipefail

# --- Configuration ---
CIV_ROOT="/home/jared/projects/AI-CIV/aether"
VAULT_DIR="$CIV_ROOT/.ops-vault/ssh-keys"
AUDIT_LOG="$CIV_ROOT/.ops-vault/audit.log"
KEY_PREFIX="purebrain-support"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()    { echo -e "${BLUE}[provision]${NC} $1"; }
ok()     { echo -e "${GREEN}[  OK  ]${NC} $1"; }
warn()   { echo -e "${YELLOW}[ WARN ]${NC} $1"; }
fail()   { echo -e "${RED}[ FAIL ]${NC} $1"; exit 1; }

# --- Audit ---
audit_entry() {
    local action="$1"
    local customer_id="$2"
    local detail="${3:-}"
    local operator
    operator=$(whoami)
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "${timestamp} | ${operator} | ${action} | ${customer_id} | ${detail}" >> "$AUDIT_LOG"
}

# --- Init vault directory ---
init_vault() {
    mkdir -p "$VAULT_DIR"
    chmod 700 "$VAULT_DIR"
    # Ensure vault is git-ignored
    if [ -f "$CIV_ROOT/.gitignore" ]; then
        if ! grep -q "^\.ops-vault" "$CIV_ROOT/.gitignore"; then
            echo ".ops-vault/" >> "$CIV_ROOT/.gitignore"
            log "Added .ops-vault/ to .gitignore"
        fi
    fi
}

# --- Provision a new keypair ---
provision() {
    local customer_id="${1:?Customer ID required}"
    local customer_email="${2:-unknown}"

    local key_name="${KEY_PREFIX}-${customer_id}"
    local private_key_path="$VAULT_DIR/${key_name}"
    local public_key_path="$VAULT_DIR/${key_name}.pub"
    local meta_path="$VAULT_DIR/${key_name}.meta"

    # Guard: don't overwrite an existing active key
    if [ -f "$private_key_path" ]; then
        warn "Key already exists for customer: $customer_id"
        warn "If you need to rotate, revoke first: $0 revoke $customer_id"
        exit 1
    fi

    log "Generating ed25519 keypair for: $customer_id"
    init_vault

    # Generate keypair — no passphrase (ops automation needs non-interactive access)
    ssh-keygen -t ed25519 \
        -C "${key_name}" \
        -f "$private_key_path" \
        -N "" \
        -q

    chmod 600 "$private_key_path"
    chmod 644 "$public_key_path"

    # Write metadata
    cat > "$meta_path" <<EOF
{
  "customer_id": "${customer_id}",
  "customer_email": "${customer_email}",
  "key_name": "${key_name}",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "created_by": "$(whoami)",
  "key_type": "ed25519",
  "status": "active",
  "revoked_at": null,
  "revocation_reason": null
}
EOF
    chmod 600 "$meta_path"

    audit_entry "PROVISION" "$customer_id" "email=${customer_email} key=${key_name}"

    echo ""
    ok "Keypair provisioned: $key_name"
    echo ""
    echo "  Private key (ops vault): $private_key_path"
    echo "  Public key:              $public_key_path"
    echo ""
    echo "--- PUBLIC KEY (inject into customer authorized_keys) ---"
    cat "$public_key_path"
    echo "---------------------------------------------------------"
    echo ""
    log "Next step: add the public key to the customer machine's ~/.ssh/authorized_keys"
    log "Use: ssh-copy-id -i $public_key_path USER@CUSTOMER_HOST"
    log "Or bundle it into the customer's PureBrain portal setup script."
}

# --- Revoke a keypair ---
revoke() {
    local customer_id="${1:?Customer ID required}"
    local reason="${2:-manual revocation}"

    local key_name="${KEY_PREFIX}-${customer_id}"
    local private_key_path="$VAULT_DIR/${key_name}"
    local public_key_path="$VAULT_DIR/${key_name}.pub"
    local meta_path="$VAULT_DIR/${key_name}.meta"
    local revoked_dir="$VAULT_DIR/revoked"

    if [ ! -f "$private_key_path" ]; then
        warn "No active key found for customer: $customer_id"
        exit 1
    fi

    mkdir -p "$revoked_dir"
    chmod 700 "$revoked_dir"

    local ts
    ts=$(date -u +"%Y%m%dT%H%M%SZ")

    # Move keys to revoked directory (preserve for audit, not deleted)
    mv "$private_key_path" "$revoked_dir/${key_name}-${ts}.revoked"
    mv "$public_key_path"  "$revoked_dir/${key_name}-${ts}.pub.revoked"

    # Update metadata
    if [ -f "$meta_path" ]; then
        python3 -c "
import json, sys
with open('${meta_path}') as f:
    m = json.load(f)
m['status'] = 'revoked'
m['revoked_at'] = '$(date -u +"%Y-%m-%dT%H:%M:%SZ")'
m['revocation_reason'] = '${reason}'
with open('${meta_path}', 'w') as f:
    json.dump(m, f, indent=2)
print('Metadata updated.')
" 2>/dev/null || echo "Note: metadata update skipped (python3 not available)"
    fi

    audit_entry "REVOKE" "$customer_id" "reason=${reason}"

    ok "Key revoked for customer: $customer_id"
    warn "MANUAL ACTION REQUIRED: Remove the public key from the customer's ~/.ssh/authorized_keys"
    echo ""
    echo "The public key fingerprint to remove was:"
    cat "$revoked_dir/${key_name}-${ts}.pub.revoked" 2>/dev/null || echo "(see revoked dir)"
    echo ""
    echo "Run on the customer's machine:"
    echo "  ssh USER@CUSTOMER_HOST 'grep -v \"${key_name}\" ~/.ssh/authorized_keys > /tmp/ak && mv /tmp/ak ~/.ssh/authorized_keys'"
}

# --- List all keys ---
list_keys() {
    init_vault
    echo ""
    echo "=== PureBrain SSH Key Inventory ==="
    echo ""

    local count=0
    for meta in "$VAULT_DIR"/*.meta; do
        [ -e "$meta" ] || continue
        count=$((count + 1))
        echo "--- Key $count ---"
        python3 -c "
import json
with open('${meta}') as f:
    m = json.load(f)
print(f'  Customer ID : {m[\"customer_id\"]}')
print(f'  Email       : {m[\"customer_email\"]}')
print(f'  Key Name    : {m[\"key_name\"]}')
print(f'  Status      : {m[\"status\"]}')
print(f'  Created     : {m[\"created_at\"]}')
if m.get('revoked_at'):
    print(f'  Revoked     : {m[\"revoked_at\"]} ({m[\"revocation_reason\"]})')
" 2>/dev/null || cat "$meta"
        echo ""
    done

    if [ $count -eq 0 ]; then
        log "No keys provisioned yet."
    else
        ok "$count key(s) found."
    fi
}

# --- Audit log view ---
audit_view() {
    if [ ! -f "$AUDIT_LOG" ]; then
        warn "No audit log found yet."
        exit 0
    fi

    echo ""
    echo "=== PureBrain SSH Key Audit Log ==="
    echo "Format: timestamp | operator | action | customer_id | detail"
    echo ""
    cat "$AUDIT_LOG"
}

# --- SSH config snippet for ops ---
# Prints a ready-to-paste SSH config block for connecting to a customer
connect_info() {
    local customer_id="${1:?Customer ID required}"
    local customer_host="${2:?Customer host/IP required}"
    local customer_user="${3:-jared}"
    local customer_port="${4:-22}"

    local key_name="${KEY_PREFIX}-${customer_id}"
    local private_key_path="$VAULT_DIR/${key_name}"

    if [ ! -f "$private_key_path" ]; then
        fail "No active private key found for customer: $customer_id"
    fi

    echo ""
    echo "=== SSH Config Block for $customer_id ==="
    echo ""
    cat <<EOF
# Add to ~/.ssh/config for easy access:
Host purebrain-${customer_id}
    HostName ${customer_host}
    User ${customer_user}
    Port ${customer_port}
    IdentityFile ${private_key_path}
    IdentitiesOnly yes
    ConnectTimeout 10
EOF
    echo ""
    echo "One-liner to test connection:"
    echo "  ssh -i ${private_key_path} -p ${customer_port} ${customer_user}@${customer_host} 'echo connected'"
    echo ""
}

# =============================================================================
# Main
# =============================================================================

COMMAND="${1:-help}"

case "$COMMAND" in
    revoke)
        revoke "${2:?revoke requires CUSTOMER_ID}" "${3:-manual revocation}"
        ;;
    list)
        list_keys
        ;;
    audit)
        audit_view
        ;;
    connect-info)
        connect_info "$2" "$3" "${4:-jared}" "${5:-22}"
        ;;
    help|--help|-h)
        echo ""
        echo "PureBrain SSH Keypair Provisioning Tool"
        echo ""
        echo "Usage:"
        echo "  $0 CUSTOMER_ID [EMAIL]            Provision new keypair"
        echo "  $0 revoke CUSTOMER_ID [REASON]    Revoke customer's key"
        echo "  $0 list                           List all provisioned keys"
        echo "  $0 audit                          Show audit log"
        echo "  $0 connect-info CID HOST [USER] [PORT]  SSH config for customer"
        echo ""
        echo "Vault: $VAULT_DIR"
        echo "Audit: $AUDIT_LOG"
        echo ""
        ;;
    *)
        # Default: provision
        provision "$1" "${2:-unknown}"
        ;;
esac
