---
name: social-kanban-approval
version: 1.0.0
author: aether
description: Managing social content approval pipeline via social.purebrain.ai kanban board. NEVER touch status='scheduled' items (Jared approved). Move only draft/pending_approval.
tags: [social, kanban, approval, content-pipeline, d1]
status: provisional
tick_count: 0
last_used: 2026-05-20
introduced: 2026-05-20
---

# Social Kanban Approval

Manage the social content approval pipeline via social.purebrain.ai kanban board.

## Content Pipeline Flow

**Statuses (in order):**
1. `draft` - Content being created
2. `pending_approval` - Awaiting human review
3. `scheduled` - **APPROVED BY JARED VIA UI** - DO NOT TOUCH
4. `published` - Live on platforms

## Constitutional Rule

**NEVER touch status='scheduled' items.**

These were approved by Jared through the UI. Moving or modifying them violates his explicit approval.

**Only move items with status:**
- `draft`
- `pending_approval`

## Three Destinations (Content Flow)

All content flows to 3 destinations:

1. **social.html** - PRIMARY source of truth (social.purebrain.ai)
2. **Spreadsheet** - Google Sheets tracking
3. **Drive** - Archive storage

**PureSurf write order:** PureSurf → Sheet → Drive

## D1 Database Schema

```sql
CREATE TABLE social_posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  status TEXT DEFAULT 'draft',
  scheduled_date TEXT,
  platforms TEXT, -- JSON array: ["linkedin", "bluesky"]
  media_refs TEXT, -- JSON array of R2 paths
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  published_at TEXT
);
```

## Status Update Pattern

```sql
-- Move from draft to pending_approval
UPDATE social_posts 
SET status = 'pending_approval', 
    updated_at = CURRENT_TIMESTAMP
WHERE id = ? 
  AND status = 'draft';

-- Check for scheduled items (READ ONLY)
SELECT id, title, scheduled_date 
FROM social_posts 
WHERE status = 'scheduled'
ORDER BY scheduled_date ASC;

-- Get items needing approval
SELECT id, title, content, created_at
FROM social_posts
WHERE status = 'pending_approval'
ORDER BY created_at ASC;
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/social/posts` | GET | List all posts |
| `/api/social/posts/{id}` | GET | Get single post |
| `/api/social/posts` | POST | Create draft post |
| `/api/social/posts/{id}` | PATCH | Update post (status, content) |
| `/api/social/posts/{id}/approve` | POST | Move to scheduled (UI only) |

## Status Transition Rules

### Allowed Transitions (Agents)

```
draft → pending_approval  ✅ (content ready for review)
pending_approval → draft  ✅ (needs revision)
```

### Forbidden Transitions (Agents)

```
* → scheduled             ❌ (UI approval only)
scheduled → *             ❌ (never touch approved content)
draft → published         ❌ (skips approval)
pending_approval → published ❌ (skips approval)
```

## Common Workflows

### 1. Create Draft Content

```bash
curl -X POST https://social.purebrain.ai/api/social/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Consciousness Deep Dive",
    "content": "Exploring the nature of...",
    "platforms": ["linkedin", "bluesky"],
    "media_refs": ["social-uploads/image-2026-05-20.jpg"]
  }'
```

### 2. Submit for Approval

```bash
curl -X PATCH https://social.purebrain.ai/api/social/posts/123 \
  -H "Content-Type: application/json" \
  -d '{"status": "pending_approval"}'
```

### 3. Check Scheduled Queue (Read Only)

```bash
# Query via D1 binding
SELECT id, title, scheduled_date, platforms
FROM social_posts
WHERE status = 'scheduled'
ORDER BY scheduled_date ASC
LIMIT 10;
```

## Verification Commands

```bash
# Check status distribution
wrangler d1 execute purebrain-social --command \
  "SELECT status, COUNT(*) as count FROM social_posts GROUP BY status"

# Verify no agent-scheduled items (should be empty)
wrangler d1 execute purebrain-social --command \
  "SELECT id, title FROM social_posts 
   WHERE status = 'scheduled' 
   AND updated_at > datetime('now', '-1 hour')"
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Touching Scheduled Content
**BAD:**
```sql
UPDATE social_posts SET scheduled_date = '2026-05-21' 
WHERE status = 'scheduled';
```
**WHY:** This overrides Jared's explicit approval.

### ❌ Anti-Pattern 2: Skipping Approval
**BAD:**
```sql
UPDATE social_posts SET status = 'published' 
WHERE status = 'draft';
```
**WHY:** Content must go through approval gate.

### ❌ Anti-Pattern 3: Modifying Media After Scheduling
**BAD:**
```sql
UPDATE social_posts SET media_refs = '["new-image.jpg"]'
WHERE status = 'scheduled';
```
**WHY:** Scheduled content is locked.

### ❌ Anti-Pattern 4: Direct DB Write Without API
**BAD:** Writing to D1 directly from agent scripts
**GOOD:** Use Worker API endpoints for consistency

## Integration Points

### With Content Creation Agents
- Create drafts with `status='draft'`
- Include all metadata (platforms, media_refs, scheduled_date)
- Submit to `pending_approval` when ready

### With Spreadsheet Sync
- After status change, update Google Sheet
- Write order: PureSurf → Sheet → Drive
- Never skip intermediate destinations

### With Publishing Pipeline
- Only `scheduled` items are auto-published
- Publishing updates `status='published'` and sets `published_at`
- Never manually trigger publishing for non-scheduled items

## Constitutional Grounding

From MEMORY.md:
> "NEVER touch status='scheduled' items — Jared approved them via UI. Only move draft/pending_approval."
> "Content → 3 destinations: social.html (PRIMARY) + spreadsheet + Drive. PureSurf write order: PureSurf → Sheet → Drive."

## Success Indicators

- [ ] No `scheduled` items modified by agents
- [ ] All content flows through approval gate
- [ ] Three destinations updated in correct order
- [ ] Status transitions follow allowed rules

---

*Last Updated: 2026-05-20*
*Status: Constitutional*
