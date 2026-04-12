---
name: CF Pages Deploy Target
description: Deploy target is purebrain-staging NOT purebrain - DNS CNAME points to purebrain-staging.pages.dev
type: feedback
---

Deploy target is purebrain-staging, NOT purebrain.

**Why:** DNS CNAME for purebrain.ai points to purebrain-staging.pages.dev. Deploying to wrong project name = content not on live site.

**How to apply:** Always use --project-name purebrain-staging in wrangler deploy commands.
