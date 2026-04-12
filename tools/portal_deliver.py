#!/usr/bin/env python3
"""portal_deliver.py -- Deliver files to the PureBrain Portal with downloadable previews.

Usage:
    python3 tools/portal_deliver.py /path/to/file.md "Optional caption"
    python3 tools/portal_deliver.py /path/to/file.png --name "custom-name.png"

    # Deliver multiple files:
    python3 tools/portal_deliver.py /path/to/a.md /path/to/b.png --message "Overnight deliverables"

    # From Python:
    from tools.portal_deliver import deliver_file
    deliver_file("/path/to/file.md", message="Ready for review")

This is the CANONICAL method for delivering files to the portal.
Uses /api/deliverable which creates proper [PORTAL_FILE:] download cards.
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path


def _get_portal_token() -> str:
    for p in [
        Path.home() / "purebrain_portal" / ".portal-token",
        Path.home() / "projects" / "AI-CIV" / "aether" / "exports" / "app-purebrain-ai-full-repo" / "portal-server" / ".portal-token",
    ]:
        if p.exists():
            return p.read_text().strip()
    raise RuntimeError("No portal token found")


def deliver_file(
    file_path: str,
    message: str = "",
    display_name: str = "",
    port: int = 8097,
) -> dict:
    """Deliver a file to the portal with a downloadable preview card.

    Args:
        file_path: Absolute path to the file.
        message: Optional caption shown above the download card.
        display_name: Optional custom display name (defaults to basename).
        port: Portal server port (default 8097).

    Returns:
        dict with 'ok', 'filename', 'url' keys on success.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        RuntimeError: If delivery fails.
    """
    fp = Path(file_path).resolve()
    if not fp.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not display_name:
        display_name = fp.name

    token = _get_portal_token()
    payload = json.dumps({
        "path": str(fp),
        "name": display_name,
        "message": message,
    }).encode()

    req = urllib.request.Request(
        f"http://localhost:{port}/api/deliverable",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"Portal delivery failed (HTTP {e.code}): {body}")
    except Exception as e:
        raise RuntimeError(f"Portal delivery failed: {e}")

    if not data.get("ok"):
        raise RuntimeError(f"Portal delivery error: {data.get('error', 'unknown')}")

    return data


def deliver_many(file_paths: list, message: str = "", port: int = 8097) -> list:
    """Deliver multiple files. Returns list of results."""
    results = []
    for fp in file_paths:
        try:
            r = deliver_file(fp, message=message, port=port)
            results.append({"file": fp, "ok": True, **r})
            print(f"  OK: {Path(fp).name}")
        except Exception as e:
            results.append({"file": fp, "ok": False, "error": str(e)})
            print(f"  FAIL: {Path(fp).name} -- {e}")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deliver files to PureBrain Portal")
    parser.add_argument("files", nargs="+", help="File path(s) to deliver")
    parser.add_argument("-m", "--message", default="", help="Caption message")
    parser.add_argument("-n", "--name", default="", help="Custom display name (single file only)")
    parser.add_argument("-p", "--port", type=int, default=8097, help="Portal port")
    args = parser.parse_args()

    if len(args.files) == 1:
        try:
            result = deliver_file(args.files[0], message=args.message, display_name=args.name, port=args.port)
            print(f"OK: Delivered '{result['filename']}' -> {result['url']}")
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        results = deliver_many(args.files, message=args.message, port=args.port)
        ok = sum(1 for r in results if r["ok"])
        print(f"\nDelivered {ok}/{len(results)} files.")
        if ok < len(results):
            sys.exit(1)
