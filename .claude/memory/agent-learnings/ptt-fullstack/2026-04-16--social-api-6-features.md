# social-api: 6 Features Built and Deployed

**Date**: 2026-04-16
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

6 features added to `workers/social-api/src/worker.js` (single-file CF Worker with embedded HTML frontend):

### Feature 1: Connect LinkedIn + Bluesky Accounts
- Modal-based connect flow (replaces old `prompt()` approach)
- Bluesky: tests connection live via `com.atproto.server.createSession` XRPC call, then saves encrypted credentials
- LinkedIn: accepts OAuth2 access token, stores encrypted via AES-256-GCM
- Generic fallback for other platforms (PureSurf session mode)

### Feature 2: Content Type Selector
- Dropdown in compose form: Post (default), Blog, Thread (future), Carousel (future)
- Saved to `content_type` column in D1 (migration 0008 already existed)
- Shown in post cards as label next to platform name

### Feature 3: Post Preview
- Live preview panel in compose modal (grid layout: form left, preview right)
- LinkedIn preview: dark card with engagement buttons (Like/Comment/Repost/Send)
- Bluesky preview: dark card with Reply/Repost/Like
- Character count with platform limits (LinkedIn 3000, Bluesky 300, Twitter 280, etc.)
- Color-coded warnings (yellow at 90%, red when over)

### Feature 4: Template Library
- New "Templates" tab with 5 pre-built templates
- Templates: Product Update, Customer Story, Industry Insight, Contrarian Take, Calculator Promo
- Click template populates compose form
- Stored in localStorage (D1 migration deferred)

### Feature 5: Multi-User Team Access
- Settings tab with Team section (visible only to owner/leader/admin)
- `POST /api/users/create` endpoint (admin-only, creates user on same team)
- `GET /api/users/team` endpoint (lists team members)
- Admin content view: `?view=all` on `/api/content` shows all team content

### Feature 6: Image Upload on Compose
- Upload zone with drag-to-click in compose form
- Uses existing `POST /api/uploads` (R2 bucket: purebrain-uploads)
- Shows local preview immediately, then uploads to R2
- Progress bar with shimmer animation
- Populates `media_refs` array on content creation
- Images shown in post cards and preview panel

## Key Patterns
- Template literal escaping: `\${}` and backticks must be escaped inside FRONTEND_HTML
- The `esc()` function with `\\"` for quote escaping inside template literal
- `apiRaw()` for FormData uploads (no Content-Type header auto-set)
- Compose platform dropdown value format: `accountId|platformName`

## File
- `/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js`
- Deployed to: `https://social.purebrain.ai`
