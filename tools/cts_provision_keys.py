#!/usr/bin/env python3
"""
CTS SSH Keypair Provisioning Script
Client Tech Support Team — Pure Technology

Generates Ed25519 SSH keypairs per customer for remote portal support.
Stores private keys in exports/departments/client-tech-support/keys/ (gitignored).
Auto-updates the SSH key registry markdown.

Usage:
    python3 tools/cts_provision_keys.py provision --name joe --server-ip 37.27.237.109 --ssh-port 2219 --ssh-user root
    python3 tools/cts_provision_keys.py list
    python3 tools/cts_provision_keys.py show --name joe
    python3 tools/cts_provision_keys.py revoke --name joe

Author: dept-systems-technology / client-tech-support-team
Created: 2026-03-16
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CIV_ROOT = Path(__file__).parent.parent
KEYS_DIR = CIV_ROOT / "exports" / "departments" / "client-tech-support" / "keys"
PUBKEYS_DIR = CIV_ROOT / "exports" / "departments" / "client-tech-support" / "pubkeys"
REGISTRY_FILE = CIV_ROOT / "exports" / "departments" / "client-tech-support" / "ssh-key-registry.md"
REGISTRY_META = CIV_ROOT / "exports" / "departments" / "client-tech-support" / "keys" / "_registry.json"
LOG_FILE = CIV_ROOT / "logs" / "cts_actions.log"
ROTATION_DAYS = 90


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log_action(action: str, customer: str, detail: str = ""):
    """Append to CTS action log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    operator = os.environ.get("USER", "aether")
    entry = f"{ts} | {operator} | {action} | {customer} | {detail}\n"
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(f"[log] {entry.strip()}")


def load_registry_meta() -> dict:
    """Load the machine-readable registry JSON."""
    if REGISTRY_META.exists():
        return json.loads(REGISTRY_META.read_text())
    return {"customers": {}}


def save_registry_meta(data: dict):
    """Save the machine-readable registry JSON."""
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    KEYS_DIR.chmod(0o700)
    REGISTRY_META.write_text(json.dumps(data, indent=2))
    REGISTRY_META.chmod(0o600)


def get_key_fingerprint(pub_key_path: Path) -> str:
    """Get the SHA256 fingerprint of a public key."""
    try:
        result = subprocess.run(
            ["ssh-keygen", "-lf", str(pub_key_path)],
            capture_output=True, text=True, check=True
        )
        # Output: "256 SHA256:xxxx comment (ED25519)"
        parts = result.stdout.strip().split()
        return parts[1] if len(parts) >= 2 else "unknown"
    except subprocess.CalledProcessError:
        return "unknown"


def update_markdown_registry(registry_data: dict):
    """Regenerate the human-readable SSH key registry markdown."""
    lines = [
        "# PureBrain Customer SSH Key Registry",
        "",
        "**Maintained by**: client-tech-support-team",
        f"**Last Updated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "**Purpose**: Track all support SSH keypairs for active PureBrain portal customers",
        "",
        "---",
        "",
        "## Registry",
        "",
        "| Customer | Slug | Host | SSH Port | SSH User | Key Fingerprint | Provisioned | Last Rotation | Next Rotation | Status | Notes |",
        "|----------|------|------|----------|----------|-----------------|-------------|---------------|---------------|--------|-------|",
    ]

    customers = registry_data.get("customers", {})
    if customers:
        for slug, info in customers.items():
            lines.append(
                f"| {info.get('customer_name', slug)} "
                f"| {slug} "
                f"| {info.get('server_ip', 'TBD')} "
                f"| {info.get('ssh_port', 22)} "
                f"| {info.get('ssh_user', 'TBD')} "
                f"| {info.get('fingerprint', 'TBD')} "
                f"| {info.get('created_date', 'TBD')} "
                f"| {info.get('last_rotation', '—')} "
                f"| {info.get('next_rotation', 'TBD')} "
                f"| {info.get('status', 'unknown')} "
                f"| {info.get('notes', '')} |"
            )
    else:
        lines.append("| (no customers provisioned yet) | | | | | | | | | | |")

    lines += [
        "",
        "---",
        "",
        "## Status Definitions",
        "",
        "| Status | Meaning |",
        "|--------|---------|",
        "| `pending-install` | Keypair generated, public key not yet confirmed installed on customer server |",
        "| `active` | Public key installed and verified, connection confirmed |",
        "| `rotation-due` | Past next rotation date, needs new keypair provisioned |",
        "| `revoked` | Key removed from customer server, no longer valid |",
        "| `offboarded` | Customer no longer active, key revoked |",
        "",
        "---",
        "",
        "## Key Storage Location",
        "",
        "Private keys (gitignored):",
        "```",
        "exports/departments/client-tech-support/keys/{slug}_portal",
        "```",
        "",
        "Public keys (safe to share):",
        "```",
        "exports/departments/client-tech-support/pubkeys/{slug}_portal.pub",
        "```",
        "",
        "---",
        "",
        "## Rotation Schedule",
        "",
        "- Standard rotation: every 90 days",
        "- Post-incident: immediate",
        "- Offboarding: within 24 hours",
        "",
        "---",
        "",
        "## Installation Instructions Template (Send to Customer)",
        "",
        "```",
        "Subject: PureBrain Support Access Setup",
        "",
        "Hi [Customer Name],",
        "",
        "To enable our support team to assist you remotely if your PureBrain portal",
        "ever needs attention, please add the following public key to your server.",
        "",
        "Run this on your server as the user we should connect as:",
        "",
        "mkdir -p ~/.ssh",
        'echo "[PUBLIC_KEY_CONTENT]" >> ~/.ssh/authorized_keys',
        "chmod 700 ~/.ssh",
        "chmod 600 ~/.ssh/authorized_keys",
        "",
        "Once done, please reply to confirm and we will verify the connection from our end.",
        "",
        "Thank you,",
        "PureBrain Client Support",
        "```",
    ]

    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text("\n".join(lines) + "\n")
    print(f"[registry] Updated: {REGISTRY_FILE}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_provision(args):
    """Generate a new Ed25519 keypair for a customer."""
    slug = f"{args.name.lower().replace(' ', '_')}_portal"
    private_key_path = KEYS_DIR / slug
    public_key_path = PUBKEYS_DIR / f"{slug}.pub"

    # Guard: don't overwrite existing key
    if private_key_path.exists():
        print(f"[ERROR] Key already exists for '{args.name}' at {private_key_path}")
        print(f"        If you need to rotate, run: python3 {__file__} revoke --name {args.name}")
        sys.exit(1)

    # Create directories with secure permissions
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    KEYS_DIR.chmod(0o700)
    PUBKEYS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate the keypair
    comment = f"purebrain-support-{slug}"
    print(f"[provision] Generating ed25519 keypair for customer: {args.name} (slug: {slug})")

    # Generate to a temp location in KEYS_DIR, then copy pub to PUBKEYS_DIR
    result = subprocess.run(
        [
            "ssh-keygen",
            "-t", "ed25519",
            "-C", comment,
            "-f", str(private_key_path),
            "-N", "",  # no passphrase — ops automation needs non-interactive access
            "-q",
        ],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"[ERROR] ssh-keygen failed: {result.stderr}")
        sys.exit(1)

    # The public key is generated at private_key_path + ".pub" by ssh-keygen
    generated_pub = Path(str(private_key_path) + ".pub")

    # Secure the private key
    private_key_path.chmod(0o600)
    generated_pub.chmod(0o644)

    # Copy public key to pubkeys dir (shareable)
    pub_content = generated_pub.read_text()
    public_key_path.write_text(pub_content)
    public_key_path.chmod(0o644)

    # Get fingerprint
    fingerprint = get_key_fingerprint(generated_pub)

    # Build metadata
    created_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    next_rotation = (datetime.now(timezone.utc) + timedelta(days=ROTATION_DAYS)).strftime("%Y-%m-%d")

    customer_record = {
        "customer_name": args.name,
        "slug": slug,
        "server_ip": args.server_ip or "TBD",
        "ssh_port": args.ssh_port or 22,
        "ssh_user": args.ssh_user or "TBD",
        "fingerprint": fingerprint,
        "created_date": created_date,
        "last_rotation": "—",
        "next_rotation": next_rotation,
        "status": "pending-install",
        "private_key_path": str(private_key_path),
        "public_key_path": str(public_key_path),
        "notes": f"Provisioned {created_date}. Awaiting customer install confirmation.",
    }

    # Update registry
    registry_data = load_registry_meta()
    registry_data["customers"][slug] = customer_record
    save_registry_meta(registry_data)
    update_markdown_registry(registry_data)

    log_action("PROVISION", slug, f"server={args.server_ip} port={args.ssh_port} user={args.ssh_user}")

    # Output the public key for delivery to customer
    print()
    print("=" * 60)
    print(f"  KEYPAIR PROVISIONED: {slug}")
    print("=" * 60)
    print(f"  Customer   : {args.name}")
    print(f"  Server     : {args.server_ip}:{args.ssh_port}")
    print(f"  SSH User   : {args.ssh_user}")
    print(f"  Fingerprint: {fingerprint}")
    print(f"  Status     : pending-install")
    print(f"  Rotation   : {next_rotation}")
    print()
    print("  Private key (KEEP SECRET):")
    print(f"    {private_key_path}")
    print()
    print("  Public key (send to customer):")
    print(f"    {public_key_path}")
    print()
    print("  --- PUBLIC KEY CONTENT (copy to customer's authorized_keys) ---")
    print(pub_content.strip())
    print("  ----------------------------------------------------------------")
    print()
    print("  NEXT STEPS:")
    print(f"  1. Send public key above to {args.name}")
    print(f"  2. Ask them to run:")
    print(f"       mkdir -p ~/.ssh && echo \"<public_key>\" >> ~/.ssh/authorized_keys")
    print(f"       chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys")
    print(f"  3. Verify connection:")
    print(f"       ssh -i {private_key_path} -p {args.ssh_port} {args.ssh_user}@{args.server_ip} 'echo connected'")
    print(f"  4. Update registry status to 'active' once confirmed")
    print()


def cmd_list(args):
    """List all provisioned customers."""
    registry_data = load_registry_meta()
    customers = registry_data.get("customers", {})

    if not customers:
        print("[list] No customers provisioned yet.")
        return

    print()
    print("=" * 70)
    print("  CTS SSH KEY REGISTRY")
    print("=" * 70)
    for slug, info in customers.items():
        print(f"  Customer : {info.get('customer_name', slug)} ({slug})")
        print(f"  Server   : {info.get('server_ip', 'TBD')}:{info.get('ssh_port', '?')}")
        print(f"  User     : {info.get('ssh_user', 'TBD')}")
        print(f"  Status   : {info.get('status', 'unknown')}")
        print(f"  Created  : {info.get('created_date', 'TBD')}")
        print(f"  Rotation : {info.get('next_rotation', 'TBD')}")
        print(f"  Fingerprint: {info.get('fingerprint', 'TBD')}")
        print()


def cmd_show(args):
    """Show a specific customer's key details."""
    slug = f"{args.name.lower().replace(' ', '_')}_portal"
    registry_data = load_registry_meta()
    info = registry_data.get("customers", {}).get(slug)

    if not info:
        print(f"[ERROR] No customer found with slug '{slug}'. Try: python3 {__file__} list")
        sys.exit(1)

    pub_path = Path(info["public_key_path"])
    print()
    print(f"  Customer : {info['customer_name']}")
    print(f"  Slug     : {slug}")
    print(f"  Server   : {info['server_ip']}:{info['ssh_port']}")
    print(f"  User     : {info['ssh_user']}")
    print(f"  Status   : {info['status']}")
    print(f"  Fingerprint: {info['fingerprint']}")
    print(f"  Created  : {info['created_date']}")
    print(f"  Rotation : {info['next_rotation']}")
    print()
    if pub_path.exists():
        print("  Public Key:")
        print(f"    {pub_path.read_text().strip()}")
    else:
        print(f"  [WARNING] Public key file not found at {pub_path}")
    print()
    print(f"  Connect command:")
    print(f"    ssh -i {info['private_key_path']} -p {info['ssh_port']} {info['ssh_user']}@{info['server_ip']} 'echo connected'")
    print()


def cmd_mark_active(args):
    """Mark a customer's key as active (connection verified)."""
    slug = f"{args.name.lower().replace(' ', '_')}_portal"
    registry_data = load_registry_meta()

    if slug not in registry_data.get("customers", {}):
        print(f"[ERROR] No customer found with slug '{slug}'.")
        sys.exit(1)

    registry_data["customers"][slug]["status"] = "active"
    registry_data["customers"][slug]["notes"] = f"Connection verified. Active since {datetime.now(timezone.utc).strftime('%Y-%m-%d')}."
    save_registry_meta(registry_data)
    update_markdown_registry(registry_data)
    log_action("MARK_ACTIVE", slug, "connection verified")
    print(f"[ok] {slug} marked as active.")


def cmd_revoke(args):
    """Revoke a customer's keypair."""
    slug = f"{args.name.lower().replace(' ', '_')}_portal"
    registry_data = load_registry_meta()

    if slug not in registry_data.get("customers", {}):
        print(f"[ERROR] No customer found with slug '{slug}'.")
        sys.exit(1)

    info = registry_data["customers"][slug]
    private_key_path = Path(info["private_key_path"])

    # Move private key to revoked dir
    revoked_dir = KEYS_DIR / "revoked"
    revoked_dir.mkdir(exist_ok=True)
    revoked_dir.chmod(0o700)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    if private_key_path.exists():
        dest = revoked_dir / f"{slug}-{ts}.revoked"
        private_key_path.rename(dest)
        dest.chmod(0o600)
        print(f"[revoke] Private key moved to: {dest}")

    pub_path = Path(str(private_key_path) + ".pub")
    if pub_path.exists():
        dest_pub = revoked_dir / f"{slug}-{ts}.pub.revoked"
        pub_path.rename(dest_pub)
        print(f"[revoke] ssh-keygen pub moved to: {dest_pub}")

    # Update registry
    registry_data["customers"][slug]["status"] = "revoked"
    registry_data["customers"][slug]["notes"] = f"Revoked {datetime.now(timezone.utc).strftime('%Y-%m-%d')}. Reason: {args.reason or 'manual'}."
    save_registry_meta(registry_data)
    update_markdown_registry(registry_data)

    log_action("REVOKE", slug, f"reason={args.reason or 'manual'}")

    print()
    print(f"[ok] Key revoked for: {info['customer_name']}")
    print()
    print("  MANUAL ACTION REQUIRED:")
    print(f"  Remove the public key from {info['server_ip']} authorized_keys:")
    pub_content = info.get("fingerprint", "(see revoked dir)")
    print(f"  ssh USER@{info['server_ip']} -p {info['ssh_port']} \\")
    print(f"    'grep -v \"{slug}\" ~/.ssh/authorized_keys > /tmp/ak && mv /tmp/ak ~/.ssh/authorized_keys'")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CTS SSH Keypair Provisioning — Pure Technology Client Tech Support"
    )
    sub = parser.add_subparsers(dest="command")

    # provision
    p_provision = sub.add_parser("provision", help="Generate new keypair for a customer")
    p_provision.add_argument("--name", required=True, help="Customer name (e.g. 'joe', 'nathan')")
    p_provision.add_argument("--server-ip", default=None, help="Customer server IP or hostname")
    p_provision.add_argument("--ssh-port", type=int, default=22, help="SSH port (default: 22)")
    p_provision.add_argument("--ssh-user", default="root", help="SSH user on customer server")

    # list
    sub.add_parser("list", help="List all provisioned customers")

    # show
    p_show = sub.add_parser("show", help="Show details for a specific customer")
    p_show.add_argument("--name", required=True, help="Customer name")

    # mark-active
    p_active = sub.add_parser("mark-active", help="Mark customer key as active (confirmed installed)")
    p_active.add_argument("--name", required=True, help="Customer name")

    # revoke
    p_revoke = sub.add_parser("revoke", help="Revoke a customer's keypair")
    p_revoke.add_argument("--name", required=True, help="Customer name")
    p_revoke.add_argument("--reason", default="manual revocation", help="Reason for revocation")

    args = parser.parse_args()

    if args.command == "provision":
        cmd_provision(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "mark-active":
        cmd_mark_active(args)
    elif args.command == "revoke":
        cmd_revoke(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
