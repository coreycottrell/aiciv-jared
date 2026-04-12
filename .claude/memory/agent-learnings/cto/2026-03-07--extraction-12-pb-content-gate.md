# Extraction #12: pb-content-gate plugin

**Date**: 2026-03-07
**Type**: operational
**Topic**: Security plugin extraction — content gate code isolated to standalone plugin

## What Was Done

Extracted all content gate / password gate / portal bypass code from
`tools/security/purebrain-security/purebrain-security-plugin.php` into
`tools/security/pb-content-gate/pb-content-gate.php`.

## Source Line Ranges (purebrain-security-plugin.php)

| Section tag | Lines     | Description                                           |
|-------------|-----------|-------------------------------------------------------|
| g1a-ext     | 693–768   | WP password-form dark theme injection (page 859)      |
| g1a-ext2    | 771–798   | `post_password_required` filter — portal bypass       |
| g1a-js      | 801–828   | Brainiac Training JS gate bypass via wp_footer        |
| h2 (route)  | 1295–1324 | REST route registration: POST /guide-unlock           |
| function    | 1590–1677 | `purebrain_guide_unlock()` callback → Brevo list 3    |
| p           | 4842–5312 | AI Partnership Guide partial gate (CSS + JS)          |

## Replacement comment for source file

```
// CONTENT GATE — extracted to pb-content-gate plugin (2026-03-07)
```

## Key Design Decision

The `purebrain_guide_unlock()` function was renamed `pbcg_guide_unlock()` in the
extracted plugin to avoid a fatal "function already declared" collision if the parent
security plugin is still active during the transition period.

The `purebrain_check_rate_limit()` call is wrapped in `function_exists()` so the
extracted plugin works standalone if the parent plugin is deactivated first.

## REST route note

The guide-unlock REST route was previously registered inside the parent plugin's
`rest_api_init` action alongside other routes. In the extracted plugin it gets its
own `add_action( 'rest_api_init', ... )` wrapper — no functional change.

## Patterns

- Always rename extracted PHP functions to avoid fatal collision during transition
- Wrap shared utility calls (rate limiter) in function_exists() for standalone safety
- REST route registration can always be split into its own add_action wrapper
