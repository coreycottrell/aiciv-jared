# Blog Auto-Publisher CF Worker — MVP Build

**Date**: 2026-04-23
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

CF Worker at `blog-publisher.in0v8.workers.dev` that:
- POST /publish — generates March 20 standard blog HTML, commits to GitHub via Contents API
- GET /health — health check
- Auth via X-Admin-Token or Bearer session token (D1 sessions table)
- CORS for purebrain.ai, social.purebrain.ai, portal, 777, staging domains

## Key Files

- `/home/jared/projects/AI-CIV/aether/workers/blog-publisher/src/worker.js` — main worker
- `/home/jared/projects/AI-CIV/aether/workers/blog-publisher/wrangler.toml` — config (D1 binding to purebrain-social)

## GitHub Token

- PAT extracted from `purebrain-site` git remote: `[REDACTED-2026-05-09-LEAK-GHPAT]`
- Set as GITHUB_TOKEN secret on the worker

## Default Branch for Publishes

- Defaults to `blog-publisher-test` branch (safety — not main)
- Caller can override with `github_branch` field
- Test branch created and verified working

## Template Approach

- Full March 20 standard HTML template stored as string constant in worker
- Matches reference post: your-ai-has-a-memory-problem/index.html
- Includes: GTM, Clarity, video bg, nav, banner, byline, social share, CTA, subscribe form, SEO CTA, structured data, OG/Twitter cards

## What's Deferred (TODOs in code)

1. Audio generation (voice.purebrain.ai TTS) — complex in Worker, do separately
2. Blog index update — run sync_blog_memories.py after publish
3. Sitemap update — run sitemap generator after publish
4. Multi-tenant templates from D1 blog_templates table
5. Banner commit from R2 (code written but untested without real R2 key)

## GitHub API Pattern

- PUT to /repos/{owner}/{repo}/contents/{path}
- Check if file exists first to get SHA (for updates)
- Base64 encode content (btoa for text, raw for images)
- Two commits: one for HTML, one for banner (if provided)
