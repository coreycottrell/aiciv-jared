# Neural Feed Brevo Verification - All Forms Confirmed Live

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Verified all Neural Feed subscribe forms are wired to Brevo List 3

## Summary

Full audit of every Neural Feed signup point on purebrain.ai. All active forms confirmed
connected to Brevo List 3. Two live API tests passed. Subscriber count verified.

## Form Inventory

1. **/blog/ - #nf-subscribe-form**: Calls `api.brevo.com/v3/contacts` DIRECTLY from client-side JS
   - List ID: 3
   - Source attribute: 'purebrain-blog'
   - No proxy, direct Brevo API call

2. **Blog posts (all) - pb-lead-inline**: Scroll-triggered at 50% depth
   - Posts to `wp-json/pb-security/v1/subscribe`
   - Plugin proxies server-side to Brevo List 3

3. **Blog posts (all) - pb-lead-bar**: Sticky bar at 85% depth
   - Same endpoint as inline
   - Won't show if user already subscribed via inline

4. **/about-aether/ - standalone form**: `#about-aether-email`
   - Posts to `wp-json/pb-security/v1/subscribe`
   - Same plugin proxy

5. **Homepage waitlist**: Goes to Google Forms only - NOT a Neural Feed form

## Key Technical Details

- Plugin file: `tools/security/purebrain-security/purebrain-security-plugin.php`
- Subscribe handler: `purebrain_brevo_subscribe()` at line ~903
- Rate limit: 5 requests/IP/minute
- Fail-closed: returns 503 if BREVO_API_KEY missing from wp-config

## Brevo List 3 Status Post-Verification

- Name: "The Neural Feed - Blog Subscribers"
- Subscribers: 6 (4 real + 2 test from this verification)
- Real subscribers: jaredsanborn@yahoo.com, jared@puretechnology.nyc, purebrain@puremarketing.ai
- Welcome sequence automation ID: 4, running on purebrain_log_server

## Test Commands

```bash
# Test direct Brevo (blog listing form)
curl -X POST -H "api-key: KEY" -H "Content-Type: application/json" \
  -d '{"email":"test@x.com","listIds":[3],"updateEnabled":true}' \
  "https://api.brevo.com/v3/contacts"

# Test plugin endpoint (blog posts, about-aether)
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"test@x.com"}' \
  "https://purebrain.ai/wp-json/pb-security/v1/subscribe"

# Check List 3 status
curl -H "api-key: KEY" "https://api.brevo.com/v3/contacts/lists/3"
```
