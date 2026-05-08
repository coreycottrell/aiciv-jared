#!/usr/bin/env python3
"""
brainiac_weekly_module_builder.py

Weekly BOOP entrypoint: detect the next Brainiac module number from the
LIVE page (not hardcoded), and build module N+1.

Usage:
    python3 tools/brainiac_weekly_module_builder.py            # full run
    python3 tools/brainiac_weekly_module_builder.py --dry-run  # detect only
    python3 tools/brainiac_weekly_module_builder.py --force N  # force specific N

Design notes
------------
- Live page is the source of truth: https://purebrain.ai/brainiac-mastermind-training/?bypass=portal
- We parse `Launch Module N` occurrences and take max(N). Target = max + 1.
- Idempotent guard: if target module directory already exists locally OR target
  already appears on live page, SKIP and log.
- Content generation: delegates to the `brainiac-training-pipeline` skill by
  copying the Module 2 directory as a scaffold and logging a TODO for editorial
  fill-in. We do NOT fabricate a full module body autonomously. That requires
  Aether (Co-CEO) + Jared review per the review_flow.
- Deploy: uses tools/cf-deploy.py (never wrangler directly) and runs
  tools/pre-deploy-sync.sh first.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path("/home/jared/projects/AI-CIV/aether")
DEPLOY_DIR = REPO_ROOT / "exports" / "cf-pages-deploy" / "brainiac-mastermind-training"
LIVE_URL = "https://purebrain.ai/brainiac-mastermind-training/?bypass=portal"
MEMORY_DIR = REPO_ROOT / ".claude" / "memory" / "agent-learnings" / "ptt-fullstack"
BUILD_LOG = REPO_ROOT / "exports" / "brainiac-training" / "weekly-builder-log.jsonl"
SCAFFOLD_SOURCE = DEPLOY_DIR / "brainiac-module-2-ai-workflows"  # template

MODULE_LAUNCH_RE = re.compile(r"Launch Module\s+(\d+)", re.IGNORECASE)
MODULE_SLUG_RE = re.compile(r"brainiac-module-(\d+)-[a-z0-9-]+")


def fetch_live_page(timeout: int = 15) -> str:
    req = urllib.request.Request(LIVE_URL, headers={"User-Agent": "aether-brainiac-builder/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def detect_max_module_on_live(html: str) -> int:
    nums = [int(m.group(1)) for m in MODULE_LAUNCH_RE.finditer(html)]
    nums += [int(m.group(1)) for m in MODULE_SLUG_RE.finditer(html)]
    return max(nums) if nums else 0


def detect_max_module_local() -> int:
    if not DEPLOY_DIR.exists():
        return 0
    nums = []
    for p in DEPLOY_DIR.iterdir():
        m = re.match(r"brainiac-module-(\d+)-", p.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else 0


def module_dir_exists(n: int) -> Path | None:
    if not DEPLOY_DIR.exists():
        return None
    for p in DEPLOY_DIR.iterdir():
        m = re.match(rf"brainiac-module-{n}-", p.name)
        if m:
            return p
    return None


def detect_next_module() -> dict:
    """Return {next: int, live_max: int, local_max: int, already_exists: bool}."""
    try:
        html = fetch_live_page()
        live_max = detect_max_module_on_live(html)
        live_err = None
    except Exception as e:  # network failure fallback
        live_max = 0
        live_err = str(e)
    local_max = detect_max_module_local()
    baseline = max(live_max, local_max)
    target = baseline + 1
    existing = module_dir_exists(target)
    return {
        "next": target,
        "live_max": live_max,
        "local_max": local_max,
        "baseline": baseline,
        "already_exists": existing is not None,
        "existing_path": str(existing) if existing else None,
        "live_fetch_error": live_err,
    }


def build_module(n: int, dry_run: bool = False) -> dict:
    """Scaffold module N directory from the Module 2 template.

    Actual editorial content (topic, copy, transcript, AI training snippet) is
    filled in by Aether + `brainiac-training-pipeline` skill downstream. This
    function only guarantees the scaffold + idempotency + deploy plumbing.
    """
    if not SCAFFOLD_SOURCE.exists():
        return {"ok": False, "error": f"scaffold source missing: {SCAFFOLD_SOURCE}"}

    target_slug = f"brainiac-module-{n}-scaffold"
    target_dir = DEPLOY_DIR / target_slug

    existing = module_dir_exists(n)
    if existing is not None:
        return {"ok": False, "skipped": True, "reason": "already_exists", "path": str(existing)}

    if dry_run:
        return {"ok": True, "dry_run": True, "would_create": str(target_dir)}

    shutil.copytree(SCAFFOLD_SOURCE, target_dir)
    # Drop a marker so humans (Aether) know this needs editorial fill-in.
    marker = target_dir / "SCAFFOLD_PENDING_EDITORIAL.md"
    marker.write_text(
        f"# Module {n} Scaffold\n\n"
        f"Created: {dt.datetime.utcnow().isoformat()}Z\n"
        f"Source template: {SCAFFOLD_SOURCE.name}\n\n"
        f"NEXT STEPS (Aether + brainiac-training-pipeline skill):\n"
        f"1. Pick topic for Module {n} (next in series)\n"
        f"2. Rename directory to brainiac-module-{n}-<slug>\n"
        f"3. Rewrite index.html with Module {n} content\n"
        f"4. Generate AI training snippet via brainiac-training-pipeline skill\n"
        f"5. Update /brainiac-mastermind-training/index.html with new card + Launch link\n"
        f"6. Deploy via tools/cf-deploy.py (NOT wrangler)\n"
    )
    return {"ok": True, "created": str(target_dir)}


def run_pre_deploy_sync() -> tuple[bool, str]:
    script = REPO_ROOT / "tools" / "pre-deploy-sync.sh"
    if not script.exists():
        return False, f"missing: {script}"
    try:
        r = subprocess.run(["bash", str(script)], capture_output=True, text=True, timeout=180)
        return r.returncode == 0, (r.stdout + r.stderr)[-2000:]
    except Exception as e:
        return False, str(e)


def run_cf_deploy() -> tuple[bool, str]:
    script = REPO_ROOT / "tools" / "cf-deploy.py"
    if not script.exists():
        return False, f"missing: {script}"
    try:
        r = subprocess.run(
            ["python3", str(script), "--path", str(DEPLOY_DIR)],
            capture_output=True, text=True, timeout=300,
        )
        return r.returncode == 0, (r.stdout + r.stderr)[-2000:]
    except Exception as e:
        return False, str(e)


def log_event(event: dict) -> None:
    BUILD_LOG.parent.mkdir(parents=True, exist_ok=True)
    event = {"ts": dt.datetime.utcnow().isoformat() + "Z", **event}
    with BUILD_LOG.open("a") as f:
        f.write(json.dumps(event) + "\n")


def write_memory(event: dict) -> Path:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    date = dt.date.today().isoformat()
    n = event.get("target_module", "unknown")
    path = MEMORY_DIR / f"{date}--brainiac-weekly-build-module-{n}.md"
    path.write_text(
        f"---\n"
        f"type: operational\n"
        f"topic: Brainiac weekly BOOP build for module {n}\n"
        f"---\n\n"
        f"```json\n{json.dumps(event, indent=2)}\n```\n"
    )
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", type=int, help="Force build specific module number")
    ap.add_argument("--no-deploy", action="store_true", help="Build scaffold but skip CF deploy")
    args = ap.parse_args()

    detection = detect_next_module()
    target = args.force if args.force else detection["next"]

    print(f"[detect] live_max={detection['live_max']} local_max={detection['local_max']} "
          f"baseline={detection['baseline']} next={detection['next']} "
          f"already_exists={detection['already_exists']}")
    if detection.get("live_fetch_error"):
        print(f"[warn]   live fetch error: {detection['live_fetch_error']}")

    action = "build"
    if detection["already_exists"] and not args.force:
        action = "skip"

    print(f"Next module: {target} / Already exists: {detection['already_exists']} / Action: {action}")

    if args.dry_run:
        log_event({"mode": "dry-run", "target_module": target, **detection})
        return 0

    if action == "skip":
        event = {"mode": "skip", "target_module": target, "reason": "module_already_exists", **detection}
        log_event(event)
        write_memory(event)
        print("[skip] module already exists; no build, no deploy.")
        return 0

    build_res = build_module(target, dry_run=False)
    print(f"[build] {build_res}")
    if not build_res.get("ok"):
        log_event({"mode": "build-fail", "target_module": target, "build": build_res, **detection})
        return 2

    deploy_res = {"skipped": True}
    sync_res = {"skipped": True}
    if not args.no_deploy:
        ok, out = run_pre_deploy_sync()
        sync_res = {"ok": ok, "tail": out}
        print(f"[pre-deploy-sync] ok={ok}")
        if ok:
            ok2, out2 = run_cf_deploy()
            deploy_res = {"ok": ok2, "tail": out2}
            print(f"[cf-deploy] ok={ok2}")

    event = {
        "mode": "build",
        "target_module": target,
        "detection": detection,
        "build": build_res,
        "pre_deploy_sync": sync_res,
        "cf_deploy": deploy_res,
    }
    log_event(event)
    mem = write_memory(event)
    print(f"[memory] wrote {mem}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
