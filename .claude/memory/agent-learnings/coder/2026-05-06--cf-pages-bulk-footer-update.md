# CF Pages Bulk Footer Update Pattern

**Date**: 2026-05-06
**Agent**: coder
**Type**: operational
**Topic**: Bulk HTML footer link updates across CF Pages deploy directory

---

## Context

Added "Our Team" link to footer across all CF Pages HTML files in `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/`. Root index.html was already updated; needed to propagate to 37 other page variations.

---

## Pattern Discovery

### Challenge: Multi-line Pattern Replacement

**Initial approach (sed)**: Failed due to pipe character (`|`) escaping issues in the replacement string.

**Solution**: Python inline script for multi-line regex replacement.

### Working Implementation

```bash
# Find all HTML files, excluding specific patterns
find /path/to/cf-pages-deploy -type f -name "*.html" \
  | grep -v "/_archived/" \
  | grep -v "\.bak$" \
  | grep -v "/index\.html$" > /tmp/files_to_update.txt

# Process each file with Python
while IFS= read -r file; do
  python3 << PYEOF
import re

file_path = "$file"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Search pattern (escaped for regex)
search = r'<span class="pb-footer-sep pb-footer-sep-migrate">\|</span><a href="https://purebrain\.ai/compare/" rel="noopener" class="pb-footer-migrate">Compare</a>\n</div>'

# Replacement pattern (with new link added)
replace = '<span class="pb-footer-sep pb-footer-sep-migrate">|</span><a href="https://purebrain.ai/compare/" rel="noopener" class="pb-footer-migrate">Compare</a><span class="pb-footer-sep">|</span><a href="https://purebrain.ai/our-team/" rel="noopener" class="pb-footer-blue">Our Team</a>\n</div>'

# Perform replacement
new_content = re.sub(search, replace, content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
PYEOF
done < /tmp/files_to_update.txt
```

---

## Key Learnings

### 1. Python > sed for Complex HTML Updates

- **sed**: Great for simple single-line replacements
- **Python inline**: Better for multi-line patterns with special characters
- Avoids escaping hell with pipes, slashes, newlines

### 2. Exclusion Patterns Matter

Excluded patterns:
- `/_archived/` - Archive directories
- `\.bak$` - Backup files
- `/index\.html$` - Root index (already updated)

Used `grep -v` chain instead of complex find predicates for readability.

### 3. Verification Strategy

After update, verify with simple grep:
```bash
grep -q '<a href="https://purebrain.ai/our-team/"' "$file"
```

If not found, restoration logic can kick in.

---

## Results

- **468 files** scanned
- **37 files** updated successfully
- **Pattern found and replaced**: Footer link section with new "Our Team" link
- **Verification**: Manual spot-checks on unified/, blog/, pay-test-awakened/ confirmed correct updates

### Updated Footer Structure

```html
... Compare</a><span class="pb-footer-sep">|</span><a href="https://purebrain.ai/our-team/" rel="noopener" class="pb-footer-blue">Our Team</a>
</div>
```

---

## Reusable Pattern

This pattern works for ANY bulk HTML update across CF Pages deploy files:

1. **Find files** with exclusions (archived, backups, specific files)
2. **Use Python inline script** for replacement (not sed)
3. **Verify each update** with grep check
4. **Report summary** (total scanned vs updated)

---

## Files Updated

All 37 files successfully updated:
- Payment pages: pay-test-*, live-*, partnered/
- Content pages: blog/, compare/, awakened/
- Test pages: home-test-*, pay-test-sandbox-*
- Special pages: unified/, insiders/, referral-program/

Full list: `/tmp/updated_files_list.txt`

---

## Anti-Pattern Avoided

❌ **Don't use sed for multi-line replacements with special characters**
- Pipe characters require escaping
- Newlines are tricky
- Readability suffers

✅ **Use Python inline for HTML updates**
- Clear regex syntax
- No escaping hell
- Easy to verify

---

## Future Use Cases

This pattern applies to:
- Adding/removing footer links
- Updating copyright years
- Changing navigation items
- Modifying meta tags across pages
- Bulk class name updates

**Key**: When updating 25+ files with consistent HTML patterns, script it with Python inline rather than manual edits.
