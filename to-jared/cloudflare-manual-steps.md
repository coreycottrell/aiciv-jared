# Cloudflare Manual Steps - Quick Reference

**Date**: 2026-02-20
**For**: Jared
**Time needed**: ~5 minutes total

---

## 1. Disable TLS 1.0 and 1.1 (LOW-003) - 1 minute

1. Log into https://dash.cloudflare.com
2. Select **purebrain.ai** zone
3. Go to **SSL/TLS** > **Edge Certificates**
4. Find **Minimum TLS Version**
5. Change from TLS 1.0 to **TLS 1.2**
6. Save

This blocks all connections using outdated TLS versions (required for PCI DSS compliance).

---

## 2. (OPTIONAL) Security Headers via Cloudflare Transform Rules

The WordPress plugin v1.2.0 already adds all security headers. But if you want belt-and-suspenders coverage at the Cloudflare edge too:

1. Go to **Rules** > **Transform Rules** > **Modify Response Header**
2. Create rule: "PureBrain Security Headers"
3. Match: `hostname eq "purebrain.ai"`
4. Add these headers (Set dynamic):

| Header | Value |
|--------|-------|
| Strict-Transport-Security | `max-age=31536000; includeSubDomains` |
| X-Content-Type-Options | `nosniff` |
| X-Frame-Options | `SAMEORIGIN` |
| Permissions-Policy | `camera=(), microphone=(), geolocation=()` |

**Note**: Skip CSP in Cloudflare - the WordPress plugin handles it in report-only mode first to avoid breaking anything.

---

## 3. (OPTIONAL) Restrict wp-login.php Access

For extra protection on the admin login page, you can add a Cloudflare Access rule:

1. Go to **Zero Trust** > **Access** > **Applications**
2. Create Application > Self-hosted
3. Application domain: `purebrain.ai/wp-login.php`
4. Add policy: Allow only your email address
5. This forces email verification before anyone can even see the login page

**Alternative**: Install "WPS Hide Login" plugin to change `/wp-login.php` to a secret URL.

---

## Summary of What's Already Done (No Action Needed)

| Finding | Status | How |
|---------|--------|-----|
| CRIT-001 (API proxy) | Ready to deploy | Cloudflare Worker secured code |
| HIGH-001 (user enum) | In plugin v1.2 | REST + ?author= blocked |
| HIGH-002 (backdoor) | LIVE FIX APPLIED | Removed from pages 11, 439, 468 |
| HIGH-003 (cookies) | In plugin v1.2 | Secure + HttpOnly + SameSite |
| MED-001 (versions) | In plugin v1.2 | Generator + ver= stripped |
| MED-002 (staging pages) | Agent working now | Password-protect + noindex |
| MED-003 (headers) | In plugin v1.2 | All 6 headers + CSP report-only |
| MED-004 (privacy) | Files sent | privacy-policy.html + data-policy.html |
| LOW-001 (login errors) | In plugin v1.2 | Generic error message |
| LOW-002 (admin user) | In plugin v1.2 | User enum blocked |
| LOW-003 (TLS 1.0) | JARED ACTION | Cloudflare dashboard (see above) |
