# Metis Headshot Generation via FLUX Pro

**Date**: 2026-05-02
**Type**: operational
**Agent**: 3d-design-specialist

## Context
Generated a new headshot for Metis (General Counsel, male, distinguished older gentleman) on the PureBrain team page.

## Workflow
1. Used FLUX 1.1 Pro via Replicate API (`black-forest-labs/flux-1.1-pro`)
2. Prompt: professional headshot portrait, distinguished older gentleman, late 50s, silver gray hair, dark navy suit, dark studio background
3. Output: 1024x1024 webp, converted to JPG via PIL
4. Uploaded to R2 at `face-avatars/metis-avatar.jpg`
5. Deployed headshots + our-team via cf-deploy.py to purebrain-production
6. Flushed CF cache for /our-team/ and /headshots/metis-avatar.jpg

## Key Details
- Replicate prediction ID: hq5zztbjyhrmy0cxzk6vgehfyc
- R2 path: face-avatars/metis-avatar.jpg
- Local path: exports/cf-pages-deploy/headshots/metis-avatar.jpg
- Both HTML files (aether repo + purebrain-site) already had correct img src pointing to R2
- No HTML changes needed -- R2 file replacement was sufficient

## Gotcha
- Vira's team card also references `metis-avatar.jpg` (line 676 in both HTML files). This is a pre-existing bug where Vira was given Metis's image URL instead of her own. Replacing metis-avatar.jpg on R2 affects Vira's display too.
- FLUX outputs webp by default -- need PIL conversion to JPG for consistency
