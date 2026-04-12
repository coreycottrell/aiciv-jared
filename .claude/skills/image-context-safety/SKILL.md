# Image Context Safety Skill

**Status**: Active - Constitutional requirement
**Applies to**: ALL AGENTS, ALL CIVs, ALL PORTALS
**Created**: 2026-04-02
**Origin**: Aether CIV (Pure Technology)

---

## The Problem

When Claude Code agents use the `Read` tool on image files (.png, .jpg, .jpeg, .gif, .webp, .bmp, .tiff, .svg), the image data accumulates in the conversation context. After 2-3 images, Claude hits:

```
"image exceeds dimension limit for many-image requests (2000px)"
```

This error **crashes the entire session**, losing all work in progress. It is especially dangerous during:
- Screenshot-heavy workflows (browser testing, UI verification)
- File exploration that encounters images
- Any workflow where agents process visual assets

## The Solution: 4-Layer Defense-in-Depth

### Layer 1: PreToolUse Hook (Automatic Block)

A hook on the `Read` tool that automatically blocks any attempt to read image files. The agent receives a warning message instead of the image data.

**File**: `tools/warn-image-read.sh`

```bash
#!/usr/bin/env bash
# warn-image-read.sh - PreToolUse hook for Read tool
# Exits non-zero (blocking the read) if the file is an image.

FILE=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('file_path',''))" 2>/dev/null)

if echo "$FILE" | grep -qiE '\.(png|jpg|jpeg|gif|webp|bmp|tiff|svg)$'; then
    echo "WARNING: Reading image files into context causes dimension limit errors."
    echo "File: $FILE"
    echo "Instead: report the file path and let the human view it, or use a sub-agent."
    echo "To clean up stale images: bash tools/cleanup-context-images.sh"
    exit 1
fi

exit 0
```

### Layer 2: Cron Cleanup (Automatic /tmp Hygiene)

A cleanup script that runs every 30 minutes via cron, removing stale image files from /tmp before they can accumulate.

**File**: `tools/cleanup-context-images.sh`

```bash
#!/usr/bin/env bash
# cleanup-context-images.sh
# Removes stale screenshot/image files from /tmp
#
# Usage:
#   ./tools/cleanup-context-images.sh          # delete files older than 60 min
#   ./tools/cleanup-context-images.sh --all    # delete ALL /tmp image files
#   ./tools/cleanup-context-images.sh --age 30 # delete files older than 30 min

set -euo pipefail

AGE_MINUTES=60
DELETE_ALL=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --all) DELETE_ALL=true; shift ;;
        --age) AGE_MINUTES="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

DELETED=0

cleanup_pattern() {
    local pattern="$1"
    if [ "$DELETE_ALL" = true ]; then
        for f in /tmp/${pattern}; do
            [ -f "$f" ] || continue
            rm -f "$f"
            DELETED=$((DELETED + 1))
        done
    else
        while IFS= read -r f; do
            [ -f "$f" ] || continue
            rm -f "$f"
            DELETED=$((DELETED + 1))
        done < <(find /tmp -maxdepth 1 -name "$pattern" -mmin +"$AGE_MINUTES" 2>/dev/null)
    fi
}

cleanup_pattern "*.png"
cleanup_pattern "*.jpg"
cleanup_pattern "*.jpeg"
cleanup_pattern "*.webp"
cleanup_pattern "*.gif"
cleanup_pattern "screenshot_*.png"
cleanup_pattern "puresurf_*.png"

if [ "$DELETED" -gt 0 ]; then
    echo "[cleanup-context-images] Deleted $DELETED stale image file(s) from /tmp"
else
    echo "[cleanup-context-images] No stale image files found in /tmp"
fi
```

### Layer 3: settings.local.json Hook Configuration

The hook must be registered in `.claude/settings.local.json` to activate automatically.

**Snippet to merge into your settings.local.json**:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CIV_ROOT}/tools/warn-image-read.sh"
          }
        ]
      }
    ]
  }
}
```

Replace `${CIV_ROOT}` with your project's absolute path.

### Layer 4: CLAUDE.md Behavioral Rules

Add to your CLAUDE.md so agents understand the rules even without the hook:

```markdown
### Image Context Safety (Prevents Dimension Limit Errors)

**Requirement**: NEVER use the Read tool on image files (.png, .jpg, .jpeg, .gif, .webp) during multi-step workflows.

**Why**: When multiple images accumulate in conversation context, Claude hits "image exceeds dimension limit for many-image requests (2000px)". This crashes the session.

**Rules**:
- Report image **file paths** only - let the human view images in portal or browser
- If image analysis is truly needed, do it in a **fresh sub-agent** (isolated context) via the Agent tool
- After any screenshot operation, **delete the /tmp copy** immediately
- After screenshot-heavy workflows, run: `bash tools/cleanup-context-images.sh`
- NEVER read base64 image data into context
- NEVER accumulate more than 2 images in a single conversation context

**Cleanup**: `tools/cleanup-context-images.sh` runs every 30 min via cron and can be called manually.
```

## Installation

### One-Command Install

```bash
bash install.sh
```

### Manual Install

1. Copy `warn-image-read.sh` to `tools/warn-image-read.sh` and `chmod +x`
2. Copy `cleanup-context-images.sh` to `tools/cleanup-context-images.sh` and `chmod +x`
3. Merge the hook config into `.claude/settings.local.json`
4. Add cron entry: `*/30 * * * * /path/to/tools/cleanup-context-images.sh >> /tmp/cleanup-context-images.log 2>&1`
5. Add the CLAUDE.md section

## Standalone Deployment Package

A ready-to-deploy package is available at: `exports/portal-files/image-context-safety-package/`

Contains all files plus an `install.sh` one-command installer.

## When to Use

**Always active.** This is not a situational skill -- it is a permanent safety net.

## Compatibility

- Works with any Claude Code CIV or portal
- No dependencies beyond bash, python3, and standard unix tools
- Does not interfere with image generation or image output -- only blocks reading images into context
- Sub-agents can still analyze images (they have isolated context)

## Attribution

Created by Aether CIV (Pure Technology) after discovering the dimension limit crash during browser-vision-tester workflows. Shared as ecosystem contribution.
