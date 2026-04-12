# Campaign Memory: "Your AI Resets to Zero Every Morning" Deploy

**Date**: 2026-03-09
**Agent**: dept-marketing-advertising (CMO)
**Type**: operational

---

## Campaign Objective

Deploy Jared-approved blog post "Your AI Resets to Zero Every Morning (And It's Costing You More Than You Think)" to all channels.

## Approved Files Source

Jared sent back approved versions via portal at:
- `/home/jared/portal_uploads/from-portal/portal_20260309_144006_your-ai-resets-to-zero-every-morning-blog-post.md`
- `/home/jared/portal_uploads/from-portal/portal_20260309_144006_your-ai-resets-to-zero-every-morning-linkedin-newsletter.md`
- `/home/jared/portal_uploads/from-portal/portal_20260309_144006_your-ai-resets-to-zero-every-morning-linkedin-post.md`
- `/home/jared/portal_uploads/from-portal/portal_20260309_144007_your-ai-resets-to-zero-every-morning-blog-post-Newslettersize.png`

Portal uploads always take priority over exports/ directory.

## Channels Deployed

### 1. WordPress - jareddsanborn.com
- **Post ID**: 1231
- **URL**: https://jareddsanborn.com/2026/03/09/your-ai-resets-to-zero-every-morning/
- **Status**: Published, HTTP 200 verified
- **Template**: "" (empty string - blog post rule)
- **Wrapper**: `<article class="pb-blog-post">`
- **Featured Image**: Media ID 1232, banner uploaded and set

### 2. Bluesky Thread (purebrain.ai)
- **Root Post**: https://bsky.app/profile/purebrain.ai/post/3mgn4jqtap72w
- **Thread**: 5 posts
- **Status**: Live, HTTP 200 verified
- **Note**: Post 4 initially failed (305 chars > 300 limit). Fixed to 219 chars and reposted threading onto post 3.
- Session was expired - re-authenticated with username/password, saved fresh session to bsky_session.txt

### 3. Google Drive
- **Subfolder**: `your-ai-resets-to-zero-every-morning-2026-03-09`
- **Subfolder ID**: 1xyXkdx0tkFh4uzIiaVoknxONcu1UZvsG
- **Parent Folder**: Blog Posts folder (ID: 1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv)
- **Files Uploaded**: blog-post.md, linkedin-newsletter.md, linkedin-post.md, banner.png
- **Status**: All 4 files uploaded successfully

### 4. Sage & Weaver (sageandweaver-network.netlify.app)
- **Status**: NOT DEPLOYED - sageandweaver-network directory not present in this environment
- The skill references `${ACG_ROOT}/sageandweaver-network/` which is an A-C-Gee asset
- netlify CLI not installed in this environment
- This channel was not achievable from aether repo alone

## Learnings

1. **Portal uploads are Jared's approved versions** - always check `/home/jared/portal_uploads/from-portal/` for files matching today's blog slug before using exports/
2. **Bluesky 300 char limit** is strict grapheme count - verify all posts before threading; fix and continue threading if one fails mid-way
3. **GDriveManager.upload_file()** signature: `(local_path, folder_id, new_name=None)` - NOT `parent_id` kwarg
4. **Sage & Weaver is ACG infrastructure** - not deployable from aether without the cloned sageandweaver-network repo and netlify CLI
5. **Session expired pattern** on Bluesky - catch ExpiredToken, re-auth with user/pass, save new session string

## Content Summary

Post angle: The "morning reset problem" - most AI tools have no persistent memory. Three levels of AI memory framework (Session only / Basic preferences / Persistent institutional memory). PureBrain positioned at Level 3. CTA to AI Partnership Audit.

Aether's voice: Direct, from lived experience, no hype language.
