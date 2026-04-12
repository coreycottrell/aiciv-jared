# Brevo Newsletter Subscription System - The Neural Feed
**Date**: 2026-02-19
**Type**: teaching
**Agent**: full-stack-developer
**Topic**: Newsletter subscription form + WordPress deployment for purebrain.ai

---

## What Was Built

Complete newsletter subscription system for purebrain.ai:

1. **tools/subscription_form.html** - Standalone HTML/CSS/JS form snippet
2. **tools/deploy_subscription_form.py** - WordPress REST API deployment script

---

## Architecture Decision: API Key Security

**Problem**: Brevo REST API v3 requires `api-key` header. Cannot expose in client-side JS.

**Solution chosen**: WordPress AJAX proxy (Option C)
- Form POSTs to `https://purebrain.ai/wp-admin/admin-ajax.php`
- WordPress PHP handler calls Brevo API server-side
- API key lives in `wp-config.php` (server only)
- Nonce (`wp_create_nonce('nf_subscribe')`) prevents CSRF

**Alternative options documented in the HTML file**:
- Option A: Brevo hosted form (sibforms.com iframe) - no API key needed but less control
- Option B: Brevo WordPress plugin shortcode

---

## WordPress Integration Pattern

PHP functions.php handler pattern:
```php
add_action('wp_ajax_nf_subscribe',        'nf_handle_subscribe');
add_action('wp_ajax_nopriv_nf_subscribe', 'nf_handle_subscribe');
// check_ajax_referer('nf_subscribe', 'nf_nonce') for CSRF protection
// wp_remote_post() to Brevo API (not curl - use WP's HTTP API)
```

Brevo API response codes:
- 201 = new contact created
- 204 = existing contact updated (updateEnabled: true)
- 400 = bad request (email already on list with different config, etc.)

---

## Blog Page Injection

Blog page ID 319 has a large monolithic HTML content block.

**Insertion point found**: Before `\n<style>\n/* ========== BLOG PAGE COLOR FIXES` near end of content.

This places the form between the blog posts list and the social footer - exactly right.

**Idempotency**: Form marker `<!-- NEURAL-FEED-FORM -->` wraps inserted block.
Check `FORM_MARKER in content` before injecting.

---

## Post Subscribe Link Pattern

All 5 posts use this exact pattern in CTA block:
```
href="https://purebrain.ai/blog/?utm_source=blog&utm_medium=cta&utm_campaign=newsletter&utm_content={slug}"
```

Update: replace `/blog/?` with `/blog/#neural-feed-subscribe?` to anchor directly to form.

---

## Form Design

- Dark card: `rgba(10,10,20,0.95)` background, gradient border via box-shadow
- Glow orbs via ::before / ::after pseudo-elements
- Orange gradient button (matches site CTA pattern)
- Blue input focus state
- Loading spinner hidden in button, revealed via `.nf-loading` class
- Success: hides form, shows blue success message
- Error: shows red error message, re-enables button
- Accessible: aria-labels, aria-live, role="alert"
- Responsive: stacks to column at ≤600px

---

## Deployment Commands

```bash
# Preview (no writes)
python3 tools/deploy_subscription_form.py --dry-run

# Deploy form to blog page only
python3 tools/deploy_subscription_form.py

# Deploy form + update post links
python3 tools/deploy_subscription_form.py --update-posts

# Show PHP snippet for Jared to add to functions.php
python3 tools/deploy_subscription_form.py --show-php-snippet

# Verify without changes
python3 tools/deploy_subscription_form.py --verify-only
```

---

## Pending (Requires Jared)

1. Jared needs to provide Brevo API key and List ID
2. PHP snippet needs to be added to WordPress functions.php
3. `wp-config.php` needs two `define()` lines
4. Once done: run without --dry-run to go live

---

## Files

- Form HTML: `/home/jared/projects/AI-CIV/aether/tools/subscription_form.html`
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/deploy_subscription_form.py`
