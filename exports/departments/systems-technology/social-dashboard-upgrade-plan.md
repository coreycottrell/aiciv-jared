# Social Dashboard Upgrade Plan — surf.purebrain.ai/social.html

**Date**: 2026-04-06
**Author**: dept-systems-technology
**Status**: Technical Assessment + Implementation Plan

---

## CURRENT STATE ASSESSMENT

### What Exists (social.html v5-FIXED)

The social dashboard at `surf.purebrain.ai/social.html` is a **self-contained single-file HTML app** (~1,600 lines) deployed to Cloudflare Pages (project: `puresurf-staging`). It has 5 tabs:

| Tab | Description | Status |
|-----|-------------|--------|
| **Compose** | Create posts, select platforms (IG/FB/LinkedIn/X/Bluesky), upload media, schedule | Working |
| **Calendar** | List view of scheduled posts with filters (platform, status, date) | Working |
| **Approvals** | Drafts awaiting approval with Approve/Reject buttons | Working |
| **Analytics** | Follower counts, engagement bar chart, recent posts table | Basic (placeholder data) |
| **Media** | Media library (localStorage-based, upload/delete) | Working |

### Architecture
- **Frontend**: Pure HTML/CSS/JS, no framework, all inline in one file
- **Backend API**: PureSurf BaaS server at `157.180.69.225:8901`, proxied via CF Worker at `surf.purebrain.ai`
- **Data store**: Posts stored via `GET/POST/PUT/DELETE /social/schedule` API endpoints on BaaS server
- **Media**: localStorage only (client-side, no persistence across devices)
- **Spreadsheet**: NO connection to the LinkedIn tracking spreadsheet currently
- **Deploy**: `tools/cf-deploy.py` to `puresurf-staging` CF Pages project

### Key API Endpoints (confirmed working)
- `GET /social/scheduled` — Fetch all scheduled posts
- `POST /social/schedule` — Create draft/scheduled post
- `PUT /social/schedule/{id}` — Update status (approve, etc.)
- `DELETE /social/schedule/{id}` — Delete post
- `POST /social/adapters/{platform}/post` — Direct post to platform
- `POST /social/adapters/media/upload` — Upload media
- `GET /social/status/v2` — Platform connection status

---

## WHAT'S MISSING (Gap Analysis)

### 1. Image/Visual Preview — NOT PRESENT
- Posts in Calendar and Approvals tabs show **text only**
- No image/banner preview inline with post cards
- Media uploaded in Compose tab uses localStorage (not linked to posts)
- The BaaS schedule API has a `media_path` field but it's always null

### 2. Approve Button Flow — PARTIALLY PRESENT
- Approve button EXISTS in Approvals tab (calls `PUT /social/schedule/{id}` with `status: approved`)
- **MISSING**: No logging to LinkedIn tracking spreadsheet (ID: `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4`)
- **MISSING**: No signal/webhook to the team to execute

### 3. Two-Way Spreadsheet Sync — NOT PRESENT
- Zero integration between social.html and the Google Sheets tracking spreadsheet
- Posts created in social.html do NOT appear in the spreadsheet
- Status changes in social.html are NOT reflected in the spreadsheet
- Existing tools (`linkedin_metrics_collector.py`) write TO the spreadsheet but don't read FROM it for social.html

### 4. Single Approval Command Center — PARTIALLY PRESENT
- The approval UI exists but operates in isolation from the spreadsheet
- Jared can approve in social.html but the team has no way to know unless they check the BaaS API directly

---

## TECHNICAL PLAN

### Phase 1: Image Preview in Post Cards (QUICK WIN — ~2 hours)

**Approach**: Extend the schedule API to support `media_url` and render inline thumbnails.

1. **Frontend changes (social.html)**:
   - When composing, if media is attached, upload to BaaS via `/social/adapters/media/upload` and store the returned `media_path` with the scheduled post
   - In Calendar and Approvals renders, add an image thumbnail if `media_path` exists
   - CSS: Add `.post-thumb` class (64x64px thumbnail) to post list items
   - For posts that have media, show a clickable preview that expands

2. **Backend consideration**: The `/social/adapters/media/upload` endpoint already exists. Need to:
   - Confirm it returns a URL/path that can be used to fetch the image back
   - May need a `GET /social/media/{filename}` endpoint to serve uploaded images
   - The `POST /social/schedule` already accepts `media_path` — just needs to be wired up

**Files to change**: `social.html` (frontend), potentially `social_suite.py` on BaaS server (if media serving endpoint needed)

### Phase 2: Spreadsheet Sync via Backend Webhook (MEDIUM — ~4 hours)

**Approach**: Add a server-side Google Sheets sync module to BaaS that fires on post creation/approval/posting.

1. **New BaaS module**: `sheets_sync.py`
   - Uses Google Sheets API (service account credentials already on server, used by `linkedin_metrics_collector.py`)
   - Spreadsheet ID: `1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4`
   - Tab: "Linkedin Post Content Calendar"

2. **Sync operations**:
   - **On draft creation** → Append row to spreadsheet with:
     - Column A: Next Post ID
     - Column D: Scheduled date
     - Column F: Post content
     - Column G: "Draft" (RED)
   - **On approval** → Update column G to "Final" (YELLOW) 
   - **On posted** → Update column G to "Live" (GREEN), add LinkedIn URL to column Q

3. **Reverse sync (spreadsheet → social.html)**: 
   - Add `GET /social/sync/from-sheets` endpoint that reads spreadsheet and creates/updates posts in BaaS
   - Frontend: Add "Sync from Spreadsheet" button in Calendar tab
   - This enables posts created by the team (via spreadsheet) to appear in social.html

4. **Implementation pattern**: Follow existing `cookie_sync_page.py` pattern — standalone module with `extend_sheets_sync_routes()` function

### Phase 3: Approval Signal/Notification (QUICK — ~1 hour)

**Approach**: When Jared approves a post, notify the team.

1. **Option A (Recommended)**: On approval, BaaS sends a Telegram notification to the team channel
   - Already have Telegram bot infrastructure
   - Message: "Post approved by Jared: [preview]. Platform: [platform]. Scheduled: [time]. Execute when ready."

2. **Option B**: Webhook to a designated endpoint (more extensible, but more to build)

3. **Frontend enhancement**: After approval, show a confirmation toast with "Team notified" message

### Phase 4: Full Two-Way Live Sync (ADVANCED — ~6 hours)

**Approach**: Keep both systems in sync automatically.

1. **Periodic sync job**: BaaS runs a sync check every 5 minutes
   - Compares spreadsheet rows with BaaS scheduled posts
   - Detects new rows added to spreadsheet → creates in BaaS
   - Detects status changes in spreadsheet → updates BaaS
   - Detects BaaS changes not yet in spreadsheet → updates spreadsheet

2. **Conflict resolution**: BaaS is source of truth for status; spreadsheet is source of truth for content edits

3. **Sync status indicator**: Frontend shows last sync time and any conflicts

---

## PRIORITY ORDER (What to Build First)

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| **P1** | Image preview in post cards | 2 hrs | High — Jared can see what gets posted |
| **P2** | Approval → Spreadsheet logging | 3 hrs | High — Closes the loop |
| **P3** | Approval → Telegram notification | 1 hr | Medium — Team knows to execute |
| **P4** | Spreadsheet → social.html sync | 4 hrs | Medium — Full two-way |
| **P5** | Auto-periodic sync | 6 hrs | Low — Polish, can be manual initially |

**Recommended MVP**: P1 + P2 + P3 = ~6 hours for a fully functional single approval command center.

---

## BLOCKERS & QUESTIONS

1. **Google Sheets credentials on BaaS server**: Need to confirm the service account JSON is available at `/opt/baas/` or accessible path. The `linkedin_metrics_collector.py` uses them locally — need to check if they're also on the BaaS server (157.180.69.225).

2. **Media serving**: Does the BaaS `/social/adapters/media/upload` return a URL that can be fetched back? If not, need a `GET /social/media/{id}` endpoint.

3. **Spreadsheet write access**: The service account needs Editor access to the tracking spreadsheet. Need to verify.

4. **Which posts sync?**: LinkedIn only? Or all platforms (IG, FB, X, Bluesky)? The spreadsheet is LinkedIn-focused. Recommend: LinkedIn posts sync to spreadsheet, all posts visible in social.html.

5. **Approval authority**: Is Jared the only approver? Should there be an auth gate on the approval buttons? Currently social.html has no authentication.

---

## DEPLOYMENT PATH

1. Build upgraded `social.html` locally at `exports/cf-pages-deploy/puresurf/social.html`
2. Build `sheets_sync.py` module for BaaS server
3. Deploy social.html via `tools/cf-deploy.py social.html`
4. Deploy sheets_sync.py via SSH to BaaS server + restart
5. Test full flow: Create draft → See image → Approve → Check spreadsheet → Check Telegram

---

## FILES INVOLVED

| File | Purpose | Location |
|------|---------|----------|
| `social.html` | Frontend dashboard | `exports/cf-pages-deploy/puresurf/social.html` (to create) |
| `from-chy/puresurf-social-ui-v5-FIXED.html` | Current source | Local reference |
| `sheets_sync.py` | Spreadsheet sync module | New, deploy to `/opt/baas/` |
| `tools/cf-deploy.py` | CF Pages deployment | Existing tool |
| `tools/linkedin_metrics_collector.py` | Reference for Sheets API pattern | Existing |
| `tools/puresurf-worker/worker.js` | API proxy worker | Existing (no changes needed) |
