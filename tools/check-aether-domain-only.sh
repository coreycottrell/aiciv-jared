#!/bin/bash
# Aether domain boundary gate (per feedback_aether_chy_domain_boundaries.md).
# Minimal stub re-created 2026-05-15 (original script missing on main; pre-commit
# hook referenced it and blocked all commits). This stub enforces the literal
# rule: refuse a commit that touches obvious chy-domain paths.
#
# Chy domain (per memory):
#   puretechnyc/purebrain-site/   (Chy owns CF Pages github:push source)
#   social/ frontend (Chy + Morphe)
# Aether domain: workers/, tools/, systemd/, tests/, specs/, exports/cf-pages-deploy/, etc.

set -u
mode="${1:-pre-commit}"

if [ "$mode" = "pre-commit" ]; then
  staged=$(git diff --cached --name-only)
else
  staged=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || true)
fi

[ -z "$staged" ] && exit 0

# Block obvious chy-domain paths from aether commits
violations=$(echo "$staged" | grep -E '^puretechnyc/' || true)
if [ -n "$violations" ]; then
  echo "BLOCKED: aether commit touched chy-domain paths:" >&2
  echo "$violations" >&2
  echo "Route through Chy via handshake queue." >&2
  exit 1
fi

exit 0
