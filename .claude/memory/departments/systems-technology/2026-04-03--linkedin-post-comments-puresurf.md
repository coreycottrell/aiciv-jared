# LinkedIn Post + 3 Comments via PureSurf BaaS

**Date**: 2026-04-03
**Agent**: dept-systems-technology
**Type**: operational
**Topic**: Full LinkedIn posting workflow through PureSurf social suite

---

## What Was Done

### Post Published
- **Content**: "88% of AI agent projects die before they ever reach production" (1,210 chars)
- **Image**: linkedin-88pct-option-b.png uploaded via `/social/adapters/media/upload`
- **Flow**: Create session -> Upload media -> Draft post (with image_path) -> Confirm post
- **Status**: Posted successfully

### 3 Comments + Reactions
1. **Brij Pandey** (716K followers) - "Agentic AI Roadmap 2026" post
   - Comment: Orchestration/trust layer angle (551 chars)
   - Reaction: Insightful
2. **Arjun Jain** - "Who trained the humans who trained the AI" post
   - Comment: Training vs operating context gap (702 chars)
   - Reaction: Insightful
3. **Liam Ottley** - "AI agents course crossed 2M views" post
   - Comment: Build vs operate distinction (620 chars)
   - Reaction: Celebrate

## Key Technical Learnings

### PureSurf Social Suite Endpoints Used
- `POST /sessions` - Create session with `proxy_provider: "residential"`, `profile_name: "jared-linkedin"`
- `POST /social/adapters/media/upload` - Upload image as base64 (needs file payload, too large for inline JSON)
- `POST /social/adapters/linkedin/post` - Draft post (accepts `image_path` from media upload)
- `POST /social/adapters/linkedin/confirm-post` - Publish the draft
- `POST /sessions/{id}/navigate` - Navigate to URLs
- `POST /sessions/{id}/evaluate` - Run JS in page
- `POST /sessions/{id}/screenshot` - Returns raw PNG binary (NOT JSON-wrapped)
- `DELETE /sessions/{id}` - Close session, saves cookies

### Comment Workflow (Manual via evaluate)
- No `/social/adapters/linkedin/comment` endpoint exists yet
- Click Comment button via `aria-label` matching
- Type into Quill editor (`div.ql-editor[contenteditable="true"]`)
- Set `innerHTML` with paragraphs, remove `ql-blank` class, dispatch `input` event
- Submit via `button[class*="comments-comment-box__submit-button"]`

### Reaction Workflow (Manual via evaluate)
- Hover Like button with pointer events (pointerover, pointerenter, mouseover, mouseenter)
- Wait 2s for reaction popup to appear
- Click specific reaction by aria-label (e.g., `button[aria-label*="Insightful"]`)
- JS hover events DO trigger the LinkedIn reaction menu

### Important Notes
- Screenshot endpoint returns raw PNG binary, save with `-o` flag (not JSON)
- Media upload base64 payloads are too large for inline curl - write to temp file first
- Always verify no emdashes in text (check for \u2014)
- Session cookies persist between navigations
- Close session properly to save cookies for next use

## Files Created
- `/home/jared/exports/portal-files/linkedin-step1-feed-loaded.png`
- `/home/jared/exports/portal-files/linkedin-step2-draft-with-image.png`
- `/home/jared/exports/portal-files/linkedin-step3-post-published.png`
- `/home/jared/exports/portal-files/linkedin-comment1-brij-post.png`
- `/home/jared/exports/portal-files/linkedin-comment1-typed.png`
- `/home/jared/exports/portal-files/linkedin-comment1-submitted.png`
- `/home/jared/exports/portal-files/linkedin-comment1-done.png`
- `/home/jared/exports/portal-files/linkedin-comment2-arjun-post.png`
- `/home/jared/exports/portal-files/linkedin-comment2-typed.png`
- `/home/jared/exports/portal-files/linkedin-comment2-done.png`
- `/home/jared/exports/portal-files/linkedin-comment3-liam-post.png`
- `/home/jared/exports/portal-files/linkedin-comment3-typed.png`
- `/home/jared/exports/portal-files/linkedin-comment3-done.png`
