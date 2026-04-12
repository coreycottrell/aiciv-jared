# Blog Article Wrap Fix - 12 Posts

**Date**: 2026-03-20
**Type**: operational
**Topic**: Blog post template fix - article.pb-blog-post wrapper missing

## Problem

12 of 31 blog posts were missing `<article class="pb-blog-post">` wrapper around their content. CSS in each post is scoped to `article.pb-blog-post` selectors, so without the wrapper, all post-content styling failed.

## Root Cause

Older WordPress exports had CSS injected later but body HTML was never updated to add the article wrapper. The `<!-- INJECTED: Post banner image -->` comment was a telltale sign of older injection approach.

## Audit Command

```bash
for dir in /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/*/; do
  slug=$(basename "$dir")
  has_article=$(grep -c '<article class="pb-blog-post"' "$dir/index.html" 2>/dev/null || echo 0)
  echo "$slug: article=$has_article"
done
```

## Fix Pattern

1. Find banner img tag
2. Insert back-to-blog link and `<article class="pb-blog-post">` after it
3. Remove old blog-nav-inject script blocks
4. Close `</article>` before FAQ section

Script: `/home/jared/projects/AI-CIV/aether/tools/fix_blog_article_wrap.py`

## Reference Post (canonical template)

`/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/prompting-is-dead/index.html`
