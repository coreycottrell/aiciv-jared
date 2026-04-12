# Plugin v3.9.2 Deployed to jareddsanborn.com

**Date**: 2026-02-22
**Agent**: full-stack-developer
**Type**: operational
**Topic**: PureBrain Security Plugin v3.9.2 deployed to JDS using new AetherPureBrain.ai credentials

---

## Task

Deploy purebrain-security-plugin.php from source path to jareddsanborn.com.
JDS was at v3.6.0, source file was v3.9.2 (task referenced v3.7.0 but source is always latest).

## Method

Playwright via Plugin Editor (CodeMirror), same as all previous JDS deploys.

- Login: `AetherPureBrain.ai` + admin password `aHsiCF4NbRPH)pO5YR&%R&l9`
- Admin password (not app password) required for wp-login.php form
- App password (`WORDPRESS_APP_PASSWORD`) works for REST API only
- Plugin Editor URL: `/wp-admin/plugin-editor.php?file=purebrain-security/purebrain-security-plugin.php&plugin=purebrain-security/purebrain-security-plugin.php`
- CodeMirror `.setValue()` worked first try - no textarea fallback needed
- Save confirmed: "File edited successfully"

## Result

- Before: v3.6.0 active
- After: v3.9.2 active (confirmed via REST API + live page check)
- 8/8 live verification checks passed

## New Credentials (granted 2026-02-22)

- WORDPRESS_USER=AetherPureBrain.ai
- WORDPRESS_APP_PASSWORD=u3GO 3dvG rUqG 3QgM EYqd 8KfP (REST API auth)
- Admin password for wp-login.php form: aHsiCF4NbRPH)pO5YR&%R&l9
- Email: purebrain@puremarketing.ai

## WARN About Live Verify Script

The verify check for `pb-link-hover-v391` was wrong - the actual style ID in the plugin is
`purebrain-link-hover-fix`, NOT `pb-link-hover-v391`. The v3.9.1 feature IS present.
Fix verify scripts to check for `purebrain-link-hover-fix` instead.

## Features Now Live on JDS

| Version | Feature |
|---------|---------|
| v3.9.2 | Transparency section CTA button white text fix |
| v3.9.1 | Blog in-text link hover: orange bg + white text |
| v3.9.0 | Tag pills blue/orange + CTA button white text CSS |
| v3.8.0 | Security hardening (MED-003, LOW-001, LOW-002) |
| v3.7.0 | Nav "Blog" → "Subscribe" link |
| v3.6.0 | Transparency section, lead capture (already was there) |

## Deploy Script

`/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_jds_v392.py`

---

**End of Memory**
