# WordPress CTA Standardization via REST API

**Date**: 2026-02-18
**Type**: operational
**Topic**: Standardizing blog post CTAs across purebrain.ai WordPress site

---

## Task Summary

Updated 5 blog posts on purebrain.ai to use a standard CTA block. Each post had a different ending pattern that needed to be detected and replaced.

## What Worked

### Fetch with `?context=edit`
Using `?context=edit` query parameter on the REST API returns raw (non-rendered) post content, which is essential for making accurate string replacements without HTML entity interference.

```python
resp = requests.get(f'{base}/posts/{pid}?context=edit', auth=auth)
content = post['content']['raw']  # Raw HTML, not rendered
```

### Pattern-Specific Markers
Each post had a different CTA structure. Using exact string markers (not regex) was more reliable:
- Post 373 (no CTA): Just appended after `content.rstrip()`
- Post 172: Marker was `<hr />\n<p><em>Want to see what this kind of partnership`
- Post 381: Marker was `<p><strong>Ready to awaken your AI partner?</strong>`
- Post 316: Same marker as 381
- Post 98: Marker was `<p><em>Ready to awaken your own AI partner?`

### Idempotency Check
Always check `'blog-cta-block' in content` before modifying to prevent double-adding.

### Update via POST (not PUT)
WordPress REST API uses `POST` (not `PUT`) to update existing posts:
```python
resp = requests.post(f'{base}/posts/{pid}', auth=auth, json={'content': updated})
```

## Verification Approach

After all updates, re-fetched each post and checked:
1. `blog-cta-block` class present
2. New landing page URL (`purebrain.ai/purebrain-4/`) present
3. New button text (`Start Your AI Partnership`) present
4. Old patterns absent (`Begin the process`, `Explore the possibilities`, LinkedIn newsletter links)

All 5 posts passed all checks.

## Auth Pattern

Basic auth with WordPress application passwords:
```python
auth = ('Username', 'AppPassword')
requests.get(url, auth=auth)
```

## Rate Limiting

3 seconds between API calls was sufficient - no 429 responses encountered.

## Site Details

- Site: https://purebrain.ai
- REST API base: https://purebrain.ai/wp-json/wp/v2
- Auth user: Aether
- Posts updated: 373, 172, 381, 316, 98
