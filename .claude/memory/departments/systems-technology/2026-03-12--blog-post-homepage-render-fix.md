# Blog Post Rendering as Homepage - Root Cause & Fix

**Date**: 2026-03-12
**Agent**: dept-systems-technology
**Severity**: P1 - Live site broken
**URL affected**: purebrain.ai/blog/your-ai-has-no-idea-who-you-are/

## Root Cause

purebrain.ai DNS (Cloudflare zone 49400cad...) has a CNAME record pointing to `purebrain-staging.pages.dev` (NOT `purebrain.pages.dev`).

The purebrain-staging CF Pages project receives deployments separately from purebrain (production). The blog post commit was added to the repo but git push FAILED due to 2GB pack size limit (venv/docs committed to git). Instead, CF Pages deployed via direct upload to `purebrain` (production) project — but the live site runs on `purebrain-staging`.

## Architecture Discovery

| Component | Value |
|-----------|-------|
| purebrain.ai DNS | CNAME → purebrain-staging.pages.dev |
| purebrain-staging custom domains | purebrain.ai, www.purebrain.ai |
| purebrain (prod) custom domains | none (only purebrain.pages.dev) |
| Deploy method | Wrangler Direct Upload (no git) |
| CF Zone ID | 49400cad1527af716705f6cb8c22bb65 |
| CF Account ID | d526a3e9498dd167509003004df03290 |
| CF Pages Token | HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_ |

## Fix Applied

Deployed exports/cf-pages-deploy to purebrain-staging via wrangler:

```bash
CLOUDFLARE_ACCOUNT_ID=d526a3e9498dd167509003004df03290 \
CLOUDFLARE_API_TOKEN=HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_ \
npx wrangler pages deploy /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy \
  --project-name=purebrain-staging \
  --branch=main \
  --commit-dirty=true
```

Deployment completed in ~20s. New deployment: 7cf2e26a.purebrain-staging.pages.dev

## Critical Rule Going Forward

**ALL CF Pages deploys MUST target `purebrain-staging` (not `purebrain`) because that's the live site.**

The naming is backwards: "staging" is live, "purebrain" is not used for the custom domain.

## Git Push Failure (Separate Issue)

The repo has 28 unpushed commits and 26k+ files tracked. venv/ and docs/ with large binaries (~2GB) prevent pushing. This is a technical debt item - git is NOT the deploy mechanism for CF Pages here.

## Verification

- purebrain.ai/blog/your-ai-has-no-idea-who-you-are/ - CORRECT (pb-blog-post, correct title)
- Homepage, compare, blog index - all working
- Pay test pages - working
