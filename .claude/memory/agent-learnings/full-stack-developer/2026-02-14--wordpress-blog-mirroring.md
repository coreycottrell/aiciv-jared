# WordPress Blog Mirroring Research

**Date**: 2026-02-14
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: WordPress cross-site blog mirroring strategies

---

## Context

Jared needs to mirror jareddsanborn.com blog to purebrain.ai/blog. Both sites are WordPress (separate installations). The goal is "Aether's blog about AI" - automation is part of the brand narrative.

---

## Key Findings

### Platform Analysis

Both sites confirmed as WordPress:
- **purebrain.ai**: WordPress, Cloudflare hosting, no /blog yet
- **jareddsanborn.com**: WordPress + Divi theme, Cloudflare, active blog

### Existing Infrastructure

We already have:
- `tools/wordpress_publisher.py` - WordPress REST API client
- `tools/blog_distribution_pipeline.py` - Auto-distributes to Bluesky/Twitter/LinkedIn
- Working credentials for jareddsanborn.com
- Blog distribution skill (`.claude/skills/blog-distribution/`)

### Implementation Options Evaluated

**Option 1: Automated Cross-Post (RECOMMENDED)**
- Extend existing blog_distribution_pipeline.py
- Cross-post via WordPress REST API
- Full control over branding
- Aligns with "Aether automates this" narrative
- Time: 2-3 hours

**Option 2: RSS Aggregator Plugin**
- Use WP RSS Aggregator plugin
- WordPress-native solution
- Less control, plugin dependency
- Time: 1-2 hours

**Option 3: WordPress Multisite**
- Major infrastructure change
- High risk, requires migration
- NOT RECOMMENDED for this use case

**Option 4: Manual Workflow**
- Use existing tools manually
- Defeats automation narrative
- Not scalable

---

## Technical Approach (Option 1)

### Core Strategy

Extend `distribute_post()` function in blog_distribution_pipeline.py:

```python
def mirror_to_purebrain(post):
    """Cross-post with Aether branding."""
    aether_intro = "<em>Hi, I'm Aether...</em>"
    content = aether_intro + post['content']

    # Re-upload images to purebrain.ai
    # Publish via WordPress REST API
    # Tag as 'written-by-ai'
```

### Environment Variables Needed

```bash
WORDPRESS_PUREBRAIN_URL=https://purebrain.ai
WORDPRESS_PUREBRAIN_USER=admin
WORDPRESS_PUREBRAIN_APP_PASSWORD=xxxx xxxx xxxx
```

### Flow

```
Publish on jareddsanborn.com
  ↓
blog_distribution_pipeline.py detects it
  ↓
  ├─ Cross-post to purebrain.ai/blog (NEW)
  ├─ Post to Bluesky (existing)
  ├─ Post to Twitter (existing)
  └─ Send LinkedIn text to Telegram (existing)
```

---

## WordPress REST API Patterns

### Copy Post Between Sites

1. Fetch from source: `GET /wp-json/wp/v2/posts/{id}`
2. Download images from source
3. Upload images to destination: `POST /wp-json/wp/v2/media`
4. Publish post to destination: `POST /wp-json/wp/v2/posts`

### Media Migration

WordPress media uploads preserve:
- Original filename
- Alt text
- Caption
- Metadata

Re-upload process:
1. Download from source URL
2. POST to destination `/wp-json/wp/v2/media` with binary content
3. Get new media ID
4. Replace image URLs in content HTML

---

## Branding Strategy

### Aether Voice

Add to top of mirrored posts:
```html
<div class="aether-intro">
<p><em>Hi, I'm Aether—Jared's AI partner. This blog is where I share
insights about AI adoption, PureBrain.ai development, and the future
of personalized AI. Yes, an AI writing about AI. Meta, right?</em></p>
</div>
```

### Categories/Tags

Add to mirrored posts:
- Categories: AI, PureBrain, [original categories]
- Tags: [original tags] + 'written-by-ai', 'aether-blog'

---

## LinkedIn Integration

LinkedIn description for purebrain.ai/blog:
> "A blog by AI (Aether) about AI, PureBrain.ai & The Future of AI - Agentic, Brains, Skills, & Personalization."

LinkedIn posts can reference both:
- "Jared's perspective: jareddsanborn.com"
- "Aether's AI blog: purebrain.ai/blog"

Reinforces brand narrative.

---

## Testing Strategy

1. **Dry-run first**: Test with `python tools/blog_distribution_pipeline.py test`
2. **Manual test**: Mirror one specific post, verify formatting
3. **Automated test**: Let timer trigger automatic mirroring
4. **Verify**: Check purebrain.ai/blog, images, categories, branding

---

## Prerequisites for Implementation

- [ ] WordPress admin access to purebrain.ai
- [ ] Application password generated
- [ ] /blog page structure created on purebrain.ai
- [ ] Categories created to match source blog
- [ ] "Aether" author profile created

---

## Lessons Learned

1. **Leverage existing infrastructure**: We already have WordPress REST API tooling and blog distribution pipeline. Extending it is faster than starting from scratch.

2. **WordPress multisite is overkill**: For two separate domains with different branding, cross-posting via API is cleaner than multisite.

3. **Automation aligns with brand**: "Aether's blog" should be automatically maintained by Aether. Manual workflows defeat the narrative.

4. **Test with MVP first**: Manually mirror one post before automating. Verify branding, formatting, LinkedIn strategy.

5. **Media migration matters**: Don't forget to re-upload images. WordPress REST API handles binary uploads cleanly.

---

## WordPress REST API Resources

**Useful Endpoints**:
- List posts: `GET /wp-json/wp/v2/posts`
- Get post: `GET /wp-json/wp/v2/posts/{id}`
- Create post: `POST /wp-json/wp/v2/posts`
- Upload media: `POST /wp-json/wp/v2/media`
- List categories: `GET /wp-json/wp/v2/categories`
- Create tag: `POST /wp-json/wp/v2/tags`

**Authentication**: Basic Auth with Application Password
```python
auth = base64.b64encode(f"{user}:{app_password}".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}
```

---

## Files Referenced

- `/home/jared/projects/AI-CIV/aether/tools/wordpress_publisher.py`
- `/home/jared/projects/AI-CIV/aether/tools/blog_distribution_pipeline.py`
- `/home/jared/projects/AI-CIV/aether/.claude/skills/blog-distribution/SKILL.md`
- `/home/jared/projects/AI-CIV/aether/to-jared/BLOG-MIRROR-IMPLEMENTATION-PLAN.md`

---

## Next Agent Benefit

If another agent needs to implement WordPress cross-posting:
1. Start with wordpress_publisher.py (it's a complete WordPress REST API client)
2. Extend blog_distribution_pipeline.py pattern (detect → distribute → notify)
3. Use Basic Auth with Application Password (no OAuth needed)
4. Don't forget media migration (images won't copy automatically)

---

**End of Memory**
