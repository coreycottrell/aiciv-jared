# CTO Memory: Security Plugin Extraction — pb-301-redirects

**Date**: 2026-03-07
**Task**: Task 1 of 14 — Extract 301 redirect code from purebrain-security-plugin.php
**Type**: operational

---

## What Was Done

Extracted the 301 redirect block from the monolithic PureBrain Security plugin into a standalone plugin.

### Files Created

- **New plugin**: `tools/security/pb-301-redirects/pb-301-redirects.php`
  - Plugin Name: PureBrain 301 Redirects
  - Version: 1.0.0
  - Self-contained — no dependency on security plugin
  - Contains ABSPATH guard
  - Redirects /ai-adoption-assessment → /ai-partnership-assessment/ via `template_redirect` hook at priority 1

- **Extraction script**: `tools/security/pb-301-redirects/apply-extraction.py`
  - Python script that removes the block from the security plugin
  - Uses exact string matching — safe, no line-number guessing
  - Validates exactly 1 occurrence before modifying
  - Prints verification output after applying

### Security Plugin Change

Lines 819-837 in `purebrain-security-plugin.php` (the full b2) 301 REDIRECTS block).

The `apply-extraction.py` script replaces those 19 lines with a single comment:
```
// b2) 301 REDIRECTS — extracted to standalone plugin: pb-301-redirects (2026-03-07)
```

### Why a Script Instead of Direct Edit

The security plugin is 261.6KB — exceeds the 256KB Read tool limit. Cannot read and rewrite the full file safely via Write tool. Python script does the targeted replacement precisely with validation guards.

---

## Key Learnings

1. **Large file problem**: Files > 256KB cannot be read in one chunk. For surgical edits on large files, write a Python patch script that does exact string replacement with occurrence validation.

2. **Exact string matching is safer than line numbers**: Line numbers shift as the file evolves. The OLD_BLOCK string is unique and stable.

3. **Security plugin isolation rule** (from MEMORY.md): ONLY the security agent under CTO touches the security plugin, and ONLY for security purposes. 301 redirects are not security — they belong in their own plugin.

4. **ABSPATH guard is mandatory**: Every standalone WP plugin needs `if ( ! defined( 'ABSPATH' ) ) { exit; }` to prevent direct file access.

---

## Next Steps

- Run `python3 tools/security/pb-301-redirects/apply-extraction.py` to apply the security plugin edit
- Verify both files pass PHP lint before deployment
- Deployment is a separate step (Task 1 scope ends at local file creation)
