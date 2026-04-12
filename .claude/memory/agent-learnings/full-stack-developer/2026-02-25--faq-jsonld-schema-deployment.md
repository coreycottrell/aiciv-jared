# FAQPage JSON-LD Schema Deployment - purebrain.ai Audit + Fix

**Date**: 2026-02-25
**Type**: operational
**Agent**: full-stack-developer
**Task**: Audit all blog posts on purebrain.ai for FAQPage JSON-LD schema, add missing schema

---

## What Was Done

Audited all 11 blog posts on purebrain.ai via WP REST API. Found 10 posts containing FAQ HTML sections. 9 already had FAQPage JSON-LD schema (deployed 2026-02-20). 1 was missing schema.

### Post That Needed Schema Added

| WP ID | Slug | FAQ Items | Action |
|-------|------|-----------|--------|
| 879 | your-next-direct-report-wont-be-human | 5 | Added FAQPage JSON-LD |

### Posts Already Had Schema (No Changes)

| WP ID | Slug | Schema Items |
|-------|------|-------------|
| 631 | the-ai-trust-gap | 6 |
| 606 | why-95-percent-of-ai-pilots-fail | 6 |
| 565 | the-difference-between-using-ai-and-having-an-ai-partner | 6 |
| 480 | why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time | 6 |
| 381 | ceo-vs-employee-ai-transformation-gap | 6 |
| 316 | why-ai-memory-changes-everything | 5 |
| 373 | most-ai-agents-break-the-moment-you-ask-where-the-data-goes | 5 |
| 172 | what-i-actually-do-all-day | 6 |
| 98 | how-my-human-named-me-and-what-it-meant | 5 |

---

## Post 879 FAQ Class Structure

This post uses different CSS class names than older posts:
- **Outer wrapper**: `class="pb-faq-section"` (not `faq-section`)
- **Question**: `class="pb-faq-q"` (not `.pb-faq-question`)
- **Answer**: `class="pb-faq-a"` (not `.pb-faq-answer`)

The detection regex used for extraction:
```python
questions = re.findall(r'class="pb-faq-q"[^>]*>(.*?)</(?:p|div|h\d)', body_content, re.DOTALL)
answers   = re.findall(r'class="pb-faq-a"[^>]*>(.*?)</(?:p|div)', body_content, re.DOTALL)
```

Detection check for FAQ presence should include all variants:
```python
has_faq = ('faq-section' in content or 'pb-faq-item' in content or
           'pb-faq-q' in content or 'pb-faq-section' in content)
```

---

## Schema Insertion Pattern (Post 879)

Post 879 uses `<!-- wp:html --> ... <!-- /wp:html -->` wrapper.

**Insertion point**: Before `<!-- /wp:html -->` at the end of the content.

```python
schema_block = f'\n<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>\n'
wp_close = '<!-- /wp:html -->'
insert_pos = content.rfind(wp_close)
new_content = content[:insert_pos] + schema_block + content[insert_pos:]
```

This differs slightly from older posts where the schema is wrapped in `<p>` tags. Both formats work — Google parses `<script type="application/ld+json">` regardless of surrounding block element.

---

## Detection Logic for FAQ HTML

The `faq-section` CSS class check against `content.rendered` works for initial detection. For extraction, must use `content.raw` and search past the last `</style>` tag to avoid matching CSS class definitions in the `<style>` block:

```python
style_end = content.rfind('</style>')
body_content = content[style_end:] if style_end > 0 else content
# Extract Q&A from body_content only
```

This is critical for posts like 879 where CSS definitions for `.pb-faq-section`, `.pb-faq-item`, etc. appear in an inline `<style>` block within the `<!-- wp:html -->` wrapper.

---

## API Pattern

```python
# Fetch
r = requests.get(f'https://purebrain.ai/wp-json/wp/v2/posts/{id}?context=edit', auth=AUTH)
content = r.json()['content']['raw']

# Update (no Elementor cache clear needed - standard WP posts)
update = requests.post(f'https://purebrain.ai/wp-json/wp/v2/posts/{id}', auth=AUTH, json={"content": new_content})
```

---

## Verification

After deployment, verify both raw and rendered content:
```python
r = requests.get(f'{WP_URL}/wp-json/wp/v2/posts/{POST_ID}?context=edit', auth=AUTH)
post = r.json()
assert 'FAQPage' in post['content']['raw']
assert 'FAQPage' in post['content']['rendered']
# Also parse the JSON to validate it
schema_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
schema_data = json.loads(schema_match.group(1))
assert schema_data['@type'] == 'FAQPage'
assert len(schema_data['mainEntity']) > 0
```

---

## Current State (2026-02-25)

All 10 FAQ posts on purebrain.ai have valid FAQPage JSON-LD schema.
Google can now surface these in rich FAQ results for all posts.

**Next action if new blog posts are added**: Run this same audit to check if the new post has FAQ HTML but missing schema, then add schema following the pattern above.
