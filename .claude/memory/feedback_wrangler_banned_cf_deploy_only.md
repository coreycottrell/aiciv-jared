---
name: Wrangler BANNED — cf-deploy.py ONLY (CONSTITUTIONAL)
description: NEVER use 'wrangler pages deploy'. ONLY use cf-deploy.py. Wrangler does full directory pushes that DELETE pages not in the local folder. Lost Jared's 30-hour investor page build.
type: feedback
---

NEVER use 'wrangler pages deploy' for ANY deployment. ONLY use cf-deploy.py.

**Why:** Jared spent 30+ hours straight building the investor page with Chy. A wrangler deployment erased investment-opportunity-backup-2 because it wasn't in the local deploy folder. Wrangler does full directory pushes that DELETE anything on production not present locally. cf-deploy.py fetches the current manifest first and preserves everything.

**How to apply:** 
- ALL deployments go through: `python3 tools/cf-deploy.py [specific-file-path]`
- NEVER run: `wrangler pages deploy`, `npx wrangler pages deploy`, or any direct CF Pages API full deployment
- Tell Chy and ALL agents across both AIs
- cf-deploy.py has PROTECTED_PATHS that block deployment to frozen investor pages
- This is CONSTITUTIONAL — violation = broken trust with Jared
