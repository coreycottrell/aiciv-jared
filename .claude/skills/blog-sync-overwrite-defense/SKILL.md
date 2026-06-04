---
name: blog-sync-overwrite-defense
description: Use before running automated blog sync scripts to prevent overwriting approved content with wrong entries; enforces dry-run, backup, and diff so auto-generated indexes only include verified Jared-approved posts.
status: provisional
tick_count: 0
last_used: 2026-05-19
introduced: 2026-05-19
---
# Blog Sync Pipeline Overwrite Defense

**Purpose**: Prevent automated blog sync scripts from overwriting approved content with wrong entries. Ensures auto-generated blog indexes only include verified, Jared-approved posts.

**Source**: 2026-05-19 incident where `sync_blog_memories.py` overwrote 5 existing blog directories with wrong title/slug combinations, creating duplicates visible on purebrain.ai.

## When to Use

- Before running any blog index auto-generator (`sync_blog_memories.py`, `generate_blog_index.py`, pre-commit hooks)
- After any batch blog deployment
- When blog card counts don't match expected post count

## The Problem

Auto-sync scripts that scan `blog/*/index.html` directories can:
1. Pick up unapproved draft posts
2. Overwrite approved post directories with content from different posts (slug collision)
3. Generate index entries for posts that were never approved by Jared
4. Create phantom entries if script runs against stale or partial file state

## Defense Protocol

### Step 1: Maintain an Approved Posts Manifest

Keep a canonical list of approved blog post slugs:

```
# Location: blog-neural-feed-memories/approved-posts.txt
# One slug per line, added only after Jared approval
why-your-ai-apologizes-wrong
trust-is-not-a-vibe-engineering-decision-grade-ai
# ... etc
```

### Step 2: Pre-Sync Diff Check

Before any auto-sync writes to the blog index:

```bash
# Count current cards in index
grep -c 'nfm-card' blog-neural-feed-memories/index.html

# Count directories in blog/
ls -d blog/*/ | wc -l

# If counts diverge by more than 2, STOP and investigate
```

### Step 3: Never Auto-Write Without Comparison

```python
# WRONG: blind overwrite
write_index(scanned_posts)

# RIGHT: diff first, flag additions
existing = parse_current_index()
scanned = scan_blog_dirs()
new_entries = scanned - existing
if new_entries:
    log(f"ALERT: {len(new_entries)} new entries found, manual approval needed")
    for entry in new_entries:
        log(f"  NEW: {entry.slug} - {entry.title}")
    # DO NOT auto-write — queue for human review
```

### Step 4: Post-Count Badge Consistency

If index HTML has both a comment count (`<!-- X transmissions -->`) and a visible badge (`<span>X transmissions</span>`), they MUST match after any edit.

### Step 5: Dual-Source Awareness

Blog index exists in TWO locations (per CF Pages dual-source rule):
- `puretechnyc/purebrain-site/blog-neural-feed-memories/index.html` (PRODUCTION)
- `aether/exports/cf-pages-deploy/blog-neural-feed-memories/index.html` (REFERENCE)

Sync scripts that modify one MUST check the other. Version mismatches between the two are expected but should be tracked.

## Gotchas

- Pre-commit hooks may auto-regenerate the blog index on every commit — this can re-introduce deleted bad entries
- `sync_blog_memories.py` scans ALL directories in `blog/*/`, including drafts and staging
- Slugs can collide if titles are similar (e.g., two posts about "AI amnesia")
- Card removal requires updating BOTH the card HTML block AND the transmission count
