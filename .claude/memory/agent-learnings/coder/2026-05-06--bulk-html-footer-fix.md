# Bulk HTML Footer Link Fixes

**Date**: 2026-05-06
**Agent**: coder
**Type**: pattern
**Topic**: Bulk HTML editing with Python regex for multi-line patterns

## Context

Needed to fix two footer link issues across 473 HTML files in `/exports/cf-pages-deploy/`:
1. Change Team link from `https://puretechnology.ai/#team` to `https://purebrain.ai/our-team/` and update text from "Team" to "Our Team"
2. Remove incorrectly-added "Our Team" link from Aether bottom bar (pb-footer-sep pattern)

## Solution Pattern

### Key Learnings

**Use Python for reliable multi-line HTML editing:**
- Bash `sed` is error-prone for HTML with attributes spanning lines
- Python's `re.sub()` with proper patterns handles this reliably
- Read full file content, apply regex, write back atomically

**Two-pass approach when patterns are complex:**
1. First pass: Core URL/structure changes
2. Second pass: Text content changes

This avoids regex complexity and makes debugging easier.

### File Skipping Logic

```python
def should_skip(filepath):
    """Check if file should be skipped"""
    path_str = str(filepath)
    
    # Skip archived and backup files
    if '_archived' in path_str or '.bak' in path_str:
        return True
    
    # Skip root index.html (already fixed)
    if filepath.name == 'index.html' and filepath.parent.name == 'cf-pages-deploy':
        return True
    
    return False
```

### Regex Patterns That Worked

**URL change:**
```python
fix1_pattern = r'href="https://puretechnology\.ai/#team"'
fix1_replacement = 'href="https://purebrain.ai/our-team/"'
```

**Text change (with attributes in between):**
```python
pattern = r'(<a href="https://purebrain\.ai/our-team/"[^>]*>)Team(</a>)'
replacement = r'\1Our Team\2'
```
The `[^>]*` captures any attributes between href and the closing `>`.

**Aether bar removal:**
```python
pattern = r'<span class="pb-footer-sep">\|</span><a href="https://purebrain\.ai/our-team/" rel="noopener" class="pb-footer-blue">Our Team</a>'
# Replace with empty string
```

### Script Structure

```python
from pathlib import Path

base_dir = Path('/path/to/cf-pages-deploy')
html_files = list(base_dir.rglob('*.html'))

for filepath in sorted(html_files):
    if should_skip(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = apply_fixes(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
```

## Results

- **473 HTML files** scanned
- **39 files** modified (Fix 1 and/or Fix 2)
- **31 files** modified (text update)
- **5 files** skipped (root index + archived)
- **0 errors**

## Verification Commands

```bash
# Verify old pattern is gone
find . -name "*.html" -not -path "*_archived*" -exec grep -l 'puretechnology.ai/#team' {} \;

# Verify new pattern exists
grep -n 'href="https://purebrain.ai/our-team/"' awakened/index.html

# Verify Aether bar link removed
grep 'pb-footer-sep.*Our Team' awakened/index.html
```

## Files Created

- `/tools/fix_footer_links.py` - Main fix script (both URL and Aether bar removal)
- `/tools/fix_team_text.py` - Text-only fix script (Team → Our Team)

## When to Apply This Pattern

Use this approach for:
- Bulk HTML edits across many files
- Multi-line pattern matching (attributes, tags)
- Changes that need atomic file updates
- Cases where `sed` would be fragile

**Don't use for**:
- Single file edits (use Edit tool)
- Simple one-line patterns (grep/sed is fine)
- Changes requiring context analysis (need sub-agent)

## Anti-Patterns Avoided

1. ❌ Using `sed` for multi-line HTML patterns
2. ❌ Modifying files without skipping archived/backup
3. ❌ Complex single-pass regex (hard to debug)
4. ❌ Not verifying changes after script runs

## Future Applications

This pattern applies to:
- Footer/header updates across site sections
- Brand/URL migrations
- Class name refactoring
- Template cleanup tasks

**Key**: Python + regex + atomic file write = reliable bulk HTML editing.
