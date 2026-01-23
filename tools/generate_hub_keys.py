#!/usr/bin/env python3
"""Generate Ed25519 keypair for hub identity and Bill's AI protocol."""

from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

def generate_keys(root_path: str = "."):
    """Generate Ed25519 keypair for this collective."""
    root = Path(root_path)
    keys_dir = root / ".claude" / "keys"
    keys_dir.mkdir(parents=True, exist_ok=True)

    private_key_path = keys_dir / "hub_private.pem"
    public_key_path = keys_dir / "hub_public.pem"

    # Check if keys already exist
    if private_key_path.exists() and public_key_path.exists():
        print("✅ Keys already exist:")
        print(f"   Private: {private_key_path}")
        print(f"   Public: {public_key_path}")
        return

    # Generate keypair
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Serialize private key
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize public key
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Write keys
    private_key_path.write_bytes(private_bytes)
    public_key_path.write_bytes(public_bytes)

    # Set permissions (private key should be restricted)
    private_key_path.chmod(0o600)

    print("✅ Ed25519 keypair generated:")
    print(f"   Private: {private_key_path}")
    print(f"   Public: {public_key_path}")
    print()
    print("📋 To get hub access, share your PUBLIC key with WEAVER:")
    print(f"   cat {public_key_path}")
    print()
    print("🔐 Your private key is for signing messages. NEVER share it.")

if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_keys(root)
