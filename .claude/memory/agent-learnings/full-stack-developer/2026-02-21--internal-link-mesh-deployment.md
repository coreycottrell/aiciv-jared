# Internal Link Mesh Deployment - purebrain.ai + jareddsanborn.com

**Date**: 2026-02-21
**Type**: operational + teaching
**Topic**: SEO internal link mesh across all blog posts, both sites

---

## What Was Done

Deployed 13 internal links on purebrain.ai and mirrored them on jareddsanborn.com (26 total).

### Link Matrix Implemented

| From (PB ID) | To (PB ID) | Anchor Text | Result |
|-------------|-----------|-------------|--------|
| 565 (AI Partner) | 316 (AI Memory) | "memory in the narrow technical sense" | OK |
| 565 (AI Partner) | 480 (AI Pilot) | "enterprise AI deployments" | OK |
| 565 (AI Partner) | 381 (CEO/Employee) | "treating AI as a strategic partner..." | OK |
| 480 (AI Pilot) | 381 (CEO/Employee) | "the personal consequences" | OK |
| 480 (AI Pilot) | 373 (Data Gov) | Appended sentence after Deloitte stat | OK |
| 316 (AI Memory) | 98 (Naming) | "how naming your AI creates partnership" | OK |
| 381 (CEO/Employee) | 480 (AI Pilot) | "AI pilot failure rates" | OK |
| 373 (Data Gov) | 480 (AI Pilot) | "AI pilot programs" | OK |
| 98 (Naming) | 172 (What I Do) | "what that partnership looks like in practice" | OK |
| 172 (What I Do) | 316 (AI Memory) | "AI memory" | OK |
| 606 (95% Fail) | 480 (AI Pilot) | "Pilot Purgatory" | OK |
| 606 (95% Fail) | 316 (AI Memory) | "Context Tax" | OK |
| 606 (95% Fail) | 565 (AI Partner) | "relationship, not tooling..." | OK |

### jareddsanborn.com Post ID Mapping

| purebrain.ai ID | jareddsanborn.com ID | JD Slug |
|----------------|---------------------|---------|
| 565 | 1074 | the-difference-between-using-ai-and-having-an-ai-partner |
| 480 | 1069 | ai-pilot-purgatory |
| 381 | 1065 | ceo-vs-employee-ai-transformation-gap |
| 316 | 1056 | why-ai-memory-changes-everything |
| 373 | 1060 | most-ai-agents-break-the-moment-you-ask-where-the-data-goes |
| 98 | 1039 | what-i-named-my-ai-and-what-happened-next |
| 172 | 1045 | what-i-actually-do-all-day |
| 606 | 1092 | why-95-percent-of-ai-pilots-fail |

---

## Key Technical Lessons

### 1. WordPress REST API content editing requires context=edit

- Without `?context=edit`, the `raw` field is empty (returns only rendered HTML)
- Always use: `GET /wp-json/wp/v2/posts/{id}?context=edit`
- Then PUT back with: `POST /wp-json/wp/v2/posts/{id}` with JSON body `{"content": new_raw}`

### 2. Smart Quote / Entity Encoding Differences Between Sites

- purebrain.ai stores raw content WITH WordPress entity encoding: `&#8217;` for apostrophes, `&rsquo;`, `&hellip;` for ellipsis
- jareddsanborn.com stores content with STRAIGHT QUOTES: `'` instead of `&#8217;`, `...` instead of `&hellip;`
- Always fetch raw content first and check what encoding is used before doing string replacements
- Failure mode: your search text won't match because of encoding mismatch

### 3. Link Insertion Strategy

Two approaches used:
1. **Anchor wrap**: Replace `"existing text"` with `<a href="url">existing text</a>` - cleanest
2. **Append sentence**: Append new sentence with link immediately after existing sentence - use when anchor wrap would break grammar

For appended sentences, keep them concise and natural-reading. Readers notice if it feels bolted on.

### 4. WordPress REST API Update Method

- Use `POST` (not `PUT`) to `/wp-json/wp/v2/posts/{id}` for updates
- Auth: HTTP Basic with username + application password
- Body: `{"content": "new raw HTML content"}`
- Success: HTTP 200, response includes `modified` timestamp

### 5. Elementor Cache Clearing

- PureBrain: `DELETE /wp-json/elementor/v1/cache` - works (HTTP 200)
- JaredDSanborn: Same endpoint returns 404 - that's fine, JD uses standard WP themes not Elementor for blog

### 6. JD Post Slug Discovery

JD pilot purgatory post has different slug than PureBrain:
- PureBrain: `why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time`
- JD: `ai-pilot-purgatory`

JD naming post is Jared's perspective (not Aether's):
- PureBrain (Aether's view): `how-my-human-named-me-and-what-it-meant` (ID 98)
- JD (Jared's view): `what-i-named-my-ai-and-what-happened-next` (ID 1039)

These are companion pieces, not exact duplicates - link to corresponding perspective.

---

## What Worked Well

- Batch-fetching all posts first, then applying rules to in-memory dict, then bulk-saving = efficient (8 posts updated in ~10 seconds)
- String replace with count=1 (first occurrence only) prevents double-linking
- Checking applied/skipped per rule gave clear audit trail

## What to Watch For Next Time

- Always fetch raw content and search for exact text before writing replacement code
- Post 565 (AI vs Partner) has raw content WITH smart quotes from the start - it was written directly in Gutenberg
- Posts 381, 373, 98, 172 also use WordPress entity encoding
- Post 606 uses plain text (was imported/pasted as plain)

---

## Files

- Script: `/tmp/insert_links.py` (not persisted - logic captured here)
- Memory: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/full-stack-developer/2026-02-21--internal-link-mesh-deployment.md`
