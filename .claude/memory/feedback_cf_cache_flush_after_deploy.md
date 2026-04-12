---
name: CF Cache Flush After Deploy
description: Must flush Cloudflare cache after EVERY CF Pages deploy or changes won't appear
type: feedback
---

Flush Cloudflare cache after EVERY CF Pages deploy.

**Why:** Cloudflare aggressively caches pages. Without flushing, visitors see stale content even after successful deploy.

**How to apply:** After every wrangler deploy, purge the CF cache via API or dashboard.
