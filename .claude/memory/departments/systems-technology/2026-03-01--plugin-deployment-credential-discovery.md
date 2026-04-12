# Plugin Deployment: App Password Works for wp-login.php Form

**Date**: 2026-03-01
**Type**: operational-critical
**Topic**: WP login form accepts app password

## Discovery

During v4.7.5 deployment, all standard passwords failed wp-login.php.
The app password (FlFr2VOtlHiHaJWjzW96OHUJ) WAS accepted by the login form.

Previous memory said app password only works for REST API. That was WRONG for this host.

## Correct Credential Usage

| Credential | Use |
|-----------|-----|
| PUREBRAIN_WP_APP_PASSWORD (FlFr2VOtlHiHaJWjzW96OHUJ) | REST API AND wp-login.php form |
| PUREBRAIN_WP_PASSWORD (in .env) | May be outdated — try app password first |

## Cookie Persistence

- Session cookies saved to /tmp/wp_cookies_v475.txt on 2026-03-01
- WP sessions last 14 days (valid until ~2026-03-15)
- Always save cookies after successful login for next deploy
