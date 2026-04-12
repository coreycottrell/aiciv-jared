# GEO Fixes: Paragraph Self-Sufficiency + Comparison Tables

**Date**: 2026-02-23
**Type**: operational + teaching
**Agent**: full-stack-developer

## What Was Done

Implemented two GEO (Generative Engine Optimization) fixes across all 10 published blog posts on purebrain.ai:

### Fix 1: Paragraph Opening Self-Sufficiency
- Replaced vague pronoun openings (This/It/That/They/These/Those + verb) with specific nouns
- Applied 49 total surgical replacements across 10 posts
- NEVER rewrote full paragraphs - only changed opening words

### Fix 2: Comparison Tables
- Added one 2-column HTML comparison table per post
- Inserted after first H2/H3 heading (or after 3rd paragraph as fallback)
- Used inline styles for WordPress compatibility
- Table theme: #2a93c1 header, alternating rgba(42,147,193,0.08) rows

## Key Technical Patterns

### HTML-Aware Regex Matching
WordPress stores content with HTML entities and inline tags. Common patterns that cause misses:
- `&#8211;` (em dash), `&#8217;` (apostrophe), `&#8220;/&#8221;` (quotes)
- `&rsquo;`, `&ldquo;`, `&rdquo;`, `&hellip;` (curly quotes, ellipsis)
- Paragraph openings that include `<strong>`, `<em>`, or `<a href>` tags
  - `<p><strong>They treat</strong>` needs pattern `<p><strong>They treat`
  - `<p>It stays here. It <a href>builds context</a>` needs plain text match

### REST API Pattern (No Template Field)
```python
payload = {'content': new_content}
resp = requests.post(f"{BASE_URL}/posts/{pid}", auth=AUTH, json=payload)
```
CRITICAL: Do NOT include `template` field in REST API payload (causes 400 errors).

### Table Insertion Strategy
```python
def find_table_insertion_point(html):
    h_match = re.search(r'<h[23][^>]*>.*?</h[23]>', html, re.DOTALL | re.IGNORECASE)
    if h_match:
        pos = h_match.end()
        p_end = html.find('</p>', pos)
        if p_end != -1:
            return p_end + 4
    # Fallback: after 3rd </p>
```

### Backup Before Modify Pattern
Always save backups FIRST before any content modification:
```python
backup_path = f"exports/geo-fix-backup-post-{pid}.html"
with open(backup_path, 'w') as f:
    f.write(original_content)
```

## Posts Modified

Priority order as specified:
1. Post 565 - The Difference Between Using AI and Having an AI Partner (4 Fix1 + table)
2. Post 606 - Why 95% of AI Pilots Fail (10 Fix1 + table, including <strong> tags)
3. Post 631 - The AI Trust Gap (6 Fix1 + table)
4. Post 480 - Why Your AI Pilot Is Succeeding and Failing (4 Fix1 + table)
5. Post 381 - CEO vs Employee AI Gap (1 Fix1 + table, link inside paragraph)
6. Post 316 - Why AI Memory Changes Everything (6 Fix1 + table, <strong> in para)
7. Post 373 - Most AI Agents Break (5 Fix1 + table)
8. Post 172 - What I Actually Do All Day (8 Fix1 + table)
9. Post 98 - How My Human Named Me (6 Fix1 + table)
10. Post 696 - We Both Wrote This Post (4 Fix1 + table)

## Backup Files
All backups at: `/home/jared/projects/AI-CIV/aether/exports/geo-fix-backup-post-{pid}.html`
Modified files at: `/home/jared/projects/AI-CIV/aether/exports/geo-fix-modified-post-{pid}.html`

## Deployment Result
10/10 posts deployed successfully via WordPress REST API.
Live spot-checks confirmed all changes active.

## GEO Principle Applied
Paragraph self-sufficiency means AI search engines (Perplexity, ChatGPT search) can extract any paragraph without surrounding context and still understand what it's about. "The resistance is rational" is useless standalone. "The resistance to using AI for strategy is rational" provides full context.
