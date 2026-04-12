# IndexNow Integration + UTM Template - Plugin v4.3.0

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: IndexNow via WordPress hooks + UTM parameter standardization

---

## What Was Done

1. Added IndexNow integration to purebrain-security plugin (v4.3.0 — LOCAL ONLY, not deployed)
2. Created verification key file for site root upload
3. Built comprehensive UTM parameter template (396 lines)

## Key Learnings

### IndexNow Implementation Pattern

IndexNow via `publish_post` + `save_post` hooks (NOT a separate plugin — avoids conflicts with Yoast).

The `save_post` hook fires for BOTH new posts AND edits. The `publish_post` hook fires only on
status transition to `publish`. Best practice: use both to catch all scenarios.

**Critical**: `save_post` requires checking `wp_is_post_autosave()` and `DOING_AUTOSAVE` constant —
otherwise it fires on every keystroke in Gutenberg, hammering the IndexNow API.

```php
// The correct guard pattern:
if (
    wp_is_post_revision( $post_id ) ||
    wp_is_post_autosave( $post_id ) ||
    ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE )
) {
    return;
}
```

### IndexNow API Endpoint

- URL: `https://api.indexnow.org/IndexNow`
- Method: POST with JSON body
- Returns: 200 (OK) or 202 (Accepted) on success
- The key file must be accessible at: `https://purebrain.ai/{key}.txt`
- File contains ONLY the key string (no newline in theory, but WP file_put_contents adds one — OK)

### SEO Plugin Check Pattern

```bash
curl -s "https://purebrain.ai/" | grep -i "yoast\|rank-math\|seo-framework"
```

purebrain.ai uses **Yoast SEO v27.0**. DO NOT install Rank Math — they conflict catastrophically.

### UTM Naming Conventions (Locked In)

- `utm_source`: WHERE (purebrain_blog, neural_feed, weekly_dispatch, bluesky, linkedin)
- `utm_medium`: HOW (cta_button, inline_link, email, social)
- `utm_campaign`: WHAT (ai_partnership, ai_assessment, ai_audit, competitor_exodus, blog_readership)
- `utm_content`: WHICH specific page/post (assessment_page, audit_page, blog post slug)

### Auto-UTM JS Referrer Detection

Built a referrer-detection JS snippet that auto-appends UTMs to CTA links. Key design decisions:
- Uses `document.referrer` (available in all browsers, no consent required)
- Does NOT overwrite UTMs already present in link href
- Uses `new URL()` for safe URL manipulation
- Silent fail with try/catch (UTMs are non-critical)
- Targets: `a[href*="/#awakening"]`, `.blog-cta-button`, assessment/audit page links

Email traffic CANNOT be detected via referrer (email clients don't send referrer). Use hard-coded
UTMs in email templates instead.

## Files

- Plugin (LOCAL, DO NOT DEPLOY): `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`
- Key file for upload: `/home/jared/projects/AI-CIV/aether/tools/security/indexnow-key-file/823869521fbf4f33b93e67c781571e20.txt`
- UTM template: `/home/jared/projects/AI-CIV/aether/exports/utm-parameter-template.md`

## Deployment Requirements (NOT done by this agent)

1. Upload `823869521fbf4f33b93e67c781571e20.txt` to WordPress site root via FTP/WP file manager
2. Verify accessible at: `https://purebrain.ai/823869521fbf4f33b93e67c781571e20.txt`
3. Deploy plugin via WP Admin (devops-engineer or manual)
4. Optionally add auto-UTM JS to plugin v4.4.0 in a future release

---

**End of Memory**
