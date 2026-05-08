# LinkedIn Links Added to Our Team Page

**Date**: 2026-04-27
**Task**: Add LinkedIn profile links for all team members with LinkedIn profiles
**Type**: teaching

## What Was Done

Added LinkedIn profile links to 37 team members on `/our-team/index.html`.

### Approach

**Programmatic insertion via Python script** (faster and more reliable than 37 individual sed commands):

1. Created dict mapping names → LinkedIn URLs
2. Used regex to find `<div class="team-name">{name}</div>` + following `<div class="team-role">...</div>`
3. Inserted LinkedIn link after role div
4. Verified AI partners excluded (they have `ai-badge` class, different structure)

### Implementation

```python
# Pattern that worked
pattern = rf'(<div class="team-name">{re.escape(name)}</div>\s*<div class="team-role">.*?</div>)'

# Replacement
linkedin_link = f'\n        <a href="{url}" target="_blank" rel="noopener" style="color: #2a93c1; font-size: 13px; text-decoration: none; margin-top: 8px; display: inline-block;">LinkedIn →</a>'
```

### Link Format

- **Color**: `#2a93c1` (PureBrain blue)
- **Text**: "LinkedIn →"
- **Target**: `_blank` (new tab)
- **Security**: `rel="noopener"` (prevents window.opener access)
- **Placement**: After `team-role` div, before `team-bio`
- **Styling**: Inline for simplicity, small font (13px), 8px top margin

### Verification

- Spot-checked Jared Sanborn, Melanie Salvador
- Confirmed AI partners (Aether, Chy) don't have LinkedIn links
- 37 links added (all provided profiles)

### Git Flow

```bash
cd /home/jared/purebrain-site
git add our-team/index.html
git commit -m "feat: Add LinkedIn links (37 profiles) to team + advisors"
git push origin main
```

**Commit**: `5087fc0ba71c387f97b9330439f2d42c85516951`

## Key Learnings

### Pattern for Bulk HTML Modifications

**Python script > manual sed commands** when adding 30+ similar changes:
- Single source of truth (LINKEDIN_PROFILES dict)
- Regex pattern reusable across all entries
- Atomic operation (all-or-nothing)
- Easy to verify (count before/after)
- Faster execution

### HTML Manipulation Best Practices

1. **Read full file** before modifying
2. **Keep original** for comparison
3. **Count changes** to verify all entries processed
4. **Spot-check** 2-3 examples after
5. **Delete temp script** after success

### Team Page Structure

Team cards have consistent structure:
```html
<div class="team-card">
  <div class="team-photo-wrapper">...</div>
  [<div class="ai-badge">AI Partner</div>]  <!-- Only for AI -->
  <div class="team-name">Name</div>
  <div class="team-role">Role</div>
  <div class="team-bio">Bio text...</div>
</div>
```

AI partners have `ai-badge` div, humans don't. This structural difference prevented AI partners from getting LinkedIn links (which was desired behavior).

## Files Modified

- `/home/jared/purebrain-site/our-team/index.html` - 37 insertions

## What Would Speed This Up Next Time

- **Reusable script**: Save pattern in `tools/add_team_links.py` with CLI args
- **Data file**: Keep team members + profiles in JSON/CSV for easier updates
- **Validation**: Add link checking (verify URLs return 200) before insertion
