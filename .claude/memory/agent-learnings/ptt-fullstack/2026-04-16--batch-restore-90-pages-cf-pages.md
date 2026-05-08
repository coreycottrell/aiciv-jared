---
type: operational
topic: Batch restore ~90 broken pages on purebrain.ai via cf-deploy.py
date: 2026-04-16
---

# Batch Restore ~90 Broken Pages on purebrain.ai

## What Happened

~90 pages on purebrain.ai were serving the root index.html (homepage fallback) instead of their real content. Deployed all pages in a single batch using `cf-deploy.py` targeting `purebrain-production`.

## Key Findings

### Git Repo Does NOT Exist
- `git@github-interciv:puretechnyc/purebrain-site.git` returns "Repository not found"
- The SSH key authenticates as `coreycottrell` but no such repo exists
- The "git-only deploys" mentioned in handoff docs is aspirational, not current reality
- **Working method**: `CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py`

### cf-deploy.py Batch Capabilities
- Accepts multiple directory paths as arguments (e.g., `pitch/ creator/ invest/`)
- Directories include all files recursively (index.html + assets)
- Hash-based dedup means already-uploaded files are skipped (0 uploads if hashes match)
- Manifest preservation keeps all existing files intact
- Protected paths (investment-opportunity/) are auto-preserved

### Deployment Stats
- **90 directories** with source files found (out of 93 requested)
- **228 new files, 2 changed** files deployed
- **665 total files** in deployment after merge
- **3 missing**: investment-opportunity-backup, investment-opportunity-backup-2, 2/ (no local source)
- Deployment ID: `178be8b3-fd95-4f0e-bb29-b8bf589772c2`

### Verification Method
- Check `<title>` tag via curl - homepage fallback has generic "PURE BRAIN" title
- Real pages have specific titles (e.g., "PureBrain.ai Series A Investor Pitch Deck")
- 22 pages spot-checked, all serving correct content
- Homepage + /refer/ + /blog/ + /insiders/ + /awakened/ all verified intact

## Source Files
- All at: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/{path}/index.html`

## For Next Time
- Always use `CF_PAGES_PROJECT=purebrain-production` (not default staging)
- Run `--dry-run` first to verify scope
- Use `--verify` flag for deploy-target-map checking
- Purge CF cache after deployment: zone ID `49400cad1527af716705f6cb8c22bb65`
