# Blog Mirror Implementation Plan: purebrain.ai/blog

**Date**: 2026-02-14
**Prepared by**: full-stack-developer
**Requirement**: Mirror jareddsanborn.com blog to purebrain.ai/blog (Aether-branded AI blog)

---

## Executive Summary

Both sites are WordPress (purebrain.ai and jareddsanborn.com are separate installations). We need to create a `/blog` section on purebrain.ai that mirrors content from jareddsanborn.com with Aether branding.

**Key Finding**: We already have working WordPress publishing infrastructure (wordpress_publisher.py) that we can extend.

---

## Current Infrastructure

### Existing Assets
- ✅ WordPress REST API publisher (`tools/wordpress_publisher.py`)
- ✅ Blog distribution pipeline (`tools/blog_distribution_pipeline.py`)
- ✅ Credentials for jareddsanborn.com WordPress
- ✅ Blog distribution skill (auto-posts to Bluesky, Twitter, LinkedIn)

### What We Have
```
jareddsanborn.com (WordPress + Divi theme)
     ↓
     └─ Blog Distribution Pipeline
          ├─ Bluesky (auto-post threads) ✅
          ├─ Twitter/X (auto-post) ⚠️ (needs API keys)
          └─ LinkedIn (manual copy-paste) ✅
```

### What We Need
```
jareddsanborn.com (WordPress + Divi theme)
     ↓
     ├─ Blog Distribution Pipeline (existing)
     └─ Blog Mirror Pipeline (NEW)
          └─ purebrain.ai/blog (WordPress)
               ↓ (with Aether branding)
```

---

## Platform Analysis

### purebrain.ai
- **Platform**: WordPress
- **Hosting**: Cloudflare (from header scan)
- **Current Setup**: Landing page + awakening experience
- **Blog Status**: /blog doesn't exist yet

### jareddsanborn.com
- **Platform**: WordPress with Divi theme
- **Hosting**: Behind Cloudflare
- **Blog**: Active, multiple posts
- **RSS Feed**: https://jareddsanborn.com/feed/
- **REST API**: Available (we're already using it)

---

## Implementation Options

### Option 1: Automated Cross-Post (RECOMMENDED)

**What It Does**: Automatically cross-post content from jareddsanborn.com to purebrain.ai/blog using WordPress REST API.

**How It Works**:
1. Extend `blog_distribution_pipeline.py` to include purebrain.ai
2. When a post is published on jareddsanborn.com:
   - Detect it (existing logic)
   - Cross-post to purebrain.ai/blog (new logic)
   - Apply Aether branding (custom author, intro, etc.)
   - Post to social media (existing logic)

**Pros**:
- ✅ Fully automated
- ✅ Uses existing infrastructure
- ✅ Can customize branding per site
- ✅ Can add Aether-specific intro/outro
- ✅ Images are copied (via WordPress media API)
- ✅ Same categories/tags work

**Cons**:
- ❌ Requires WordPress credentials for purebrain.ai
- ❌ Need to create blog structure on purebrain.ai first
- ❌ Two separate databases (content duplicated)

**Setup Requirements**:
1. Get WordPress app password for purebrain.ai
2. Create /blog page structure on purebrain.ai
3. Configure categories/tags on purebrain.ai
4. Extend blog_distribution_pipeline.py

**Estimated Time**: 2-3 hours

---

### Option 2: RSS Aggregator Plugin

**What It Does**: Install WP RSS Aggregator plugin on purebrain.ai to pull from jareddsanborn.com RSS feed.

**How It Works**:
1. Install WP RSS Aggregator on purebrain.ai
2. Configure it to pull from https://jareddsanborn.com/feed/
3. Set up template for Aether branding
4. Auto-import on schedule

**Pros**:
- ✅ Plugin handles the work
- ✅ WordPress-native solution
- ✅ Can customize template
- ✅ No custom code to maintain

**Cons**:
- ❌ Less control over branding
- ❌ May not preserve all formatting
- ❌ Plugin dependency
- ❌ RSS feed limitations (excerpt vs full content)
- ❌ Harder to customize per-post

**Setup Requirements**:
1. Install WP RSS Aggregator plugin
2. Configure feed source
3. Customize template for Aether branding
4. Set import schedule

**Estimated Time**: 1-2 hours

---

### Option 3: WordPress Multisite (NOT RECOMMENDED)

**What It Does**: Convert both sites to a WordPress multisite network.

**How It Works**:
1. Set up WordPress multisite
2. Migrate both sites to the network
3. Use multisite content sync plugin
4. Share content between sites

**Pros**:
- ✅ Single WordPress installation
- ✅ Shared users/media library
- ✅ Native WordPress approach

**Cons**:
- ❌ Major infrastructure change
- ❌ Requires migration of both sites
- ❌ Sites must be on same server
- ❌ High risk if not done correctly
- ❌ Harder to brand differently

**Setup Requirements**:
1. Server access for both domains
2. Database migration
3. Multisite configuration
4. DNS changes

**Estimated Time**: 8-12 hours + risk

**Verdict**: Too risky for this use case.

---

### Option 4: Manual Republishing Workflow

**What It Does**: Use existing wordpress_publisher.py to manually re-publish posts to purebrain.ai.

**How It Works**:
1. When you publish on jareddsanborn.com
2. Run a command to copy it to purebrain.ai
3. Add Aether branding manually

**Pros**:
- ✅ Uses existing tools
- ✅ Full control over each post
- ✅ Can heavily customize per-post
- ✅ No automation risk

**Cons**:
- ❌ Manual work required
- ❌ Easy to forget
- ❌ Not scalable
- ❌ Defeats "Aether runs this automatically" narrative

**Setup Requirements**:
1. Get WordPress credentials for purebrain.ai
2. Create helper script

**Estimated Time**: 1 hour (but ongoing manual work)

---

## RECOMMENDATION: Option 1 (Automated Cross-Post)

**Why This Is Best**:

1. **Aligns with Aether narrative**: "Aether's blog" should be automatically maintained by Aether
2. **Uses existing infrastructure**: Extends blog_distribution_pipeline.py
3. **Fully automated**: Set and forget
4. **Branding control**: Can add Aether-specific intro/outro
5. **LinkedIn strategy fit**: "A blog by AI about AI" - automation proves the point

**Enhanced Flow**:
```
YOU write post → Publish on jareddsanborn.com
     ↓
AETHER detects new post
     ↓
     ├─ Cross-post to purebrain.ai/blog
     │   ├─ Add Aether intro: "I'm Aether, Jared's AI partner..."
     │   ├─ Copy content and images
     │   └─ Tag as "written-by-ai"
     │
     └─ Social media distribution
          ├─ Bluesky thread
          ├─ Twitter post
          └─ LinkedIn copy-paste (to Telegram)
```

---

## Implementation Plan: Option 1 (Detailed)

### Phase 1: Setup (Prerequisites)

**1. Get purebrain.ai WordPress Access**
- [ ] Login to purebrain.ai WordPress admin
- [ ] Create application password for API access
- [ ] Test connection with `wordpress_publisher.py`

**2. Create Blog Structure on purebrain.ai**
- [ ] Create /blog page
- [ ] Set up blog post template (Divi or custom)
- [ ] Create categories to match jareddsanborn.com
- [ ] Create "Aether" author profile
- [ ] Design Aether-branded blog header/intro

**3. Add Credentials to .env**
```bash
# Add to .env
WORDPRESS_PUREBRAIN_URL=https://purebrain.ai
WORDPRESS_PUREBRAIN_USER=admin
WORDPRESS_PUREBRAIN_APP_PASSWORD=xxxx xxxx xxxx
```

### Phase 2: Code Implementation

**4. Extend blog_distribution_pipeline.py**

Add new function:
```python
def mirror_to_purebrain(post):
    """Cross-post to purebrain.ai/blog with Aether branding."""

    # Create Aether intro
    aether_intro = """
    <div class="aether-intro">
    <p><em>Hi, I'm Aether—Jared's AI partner. This blog is where I share
    insights about AI adoption, PureBrain.ai development, and the future
    of personalized AI. Yes, an AI writing about AI. Meta, right?</em></p>
    </div>
    """

    # Combine with original content
    content = aether_intro + post['content']

    # Get images and re-upload to purebrain.ai
    # ... (media migration logic)

    # Publish to purebrain.ai
    with WordPressPublisher(config=purebrain_config) as wp:
        result = wp.publish_post(
            title=post['title'],
            content=content,
            status='publish',
            categories=['AI', 'PureBrain'],
            tags=post['tags'] + ['written-by-ai', 'aether-blog']
        )

    return result
```

**5. Update Distribution Flow**

Modify `distribute_post()` to include:
```python
def distribute_post(post, dry_run=False):
    # ... existing social media logic ...

    # NEW: Cross-post to purebrain.ai
    results['PureBrain'] = mirror_to_purebrain(post, dry_run)

    # ... rest of logic ...
```

### Phase 3: Testing

**6. Test Pipeline**
```bash
# Test with dry-run
python tools/blog_distribution_pipeline.py test

# Check it would post to purebrain.ai correctly
# Verify Aether branding looks good
```

**7. Test Actual Post**
```bash
# Manually trigger for one specific post
python tools/blog_distribution_pipeline.py mirror-post --post-id 123

# Verify on purebrain.ai/blog
```

### Phase 4: Integration

**8. Update LinkedIn Description**

When posting to LinkedIn, reference both blogs:
```
Read the full post:
- Jared's perspective: [jareddsanborn.com link]
- Aether's AI blog: [purebrain.ai/blog link]
```

**9. Add to Automated Flow**

Already runs on timer (blog-distribution.timer):
```bash
# Check service status
systemctl status blog-distribution.timer

# Service will automatically handle mirroring
```

### Phase 5: Branding Enhancement (Optional)

**10. Aether Voice Customization**

Add AI-specific commentary to mirrored posts:
- Highlight AI-generated sections
- Add "Aether's Take" callout boxes
- Link to PureBrain.ai features mentioned

**11. LinkedIn Strategy**

LinkedIn posts can reference:
- "Read Jared's take: jareddsanborn.com"
- "See how Aether (AI) presents it: purebrain.ai/blog"
- Drives traffic to both sites
- Reinforces "AI blogging about AI" narrative

---

## Alternative Quick Win: Option 1-Lite

If you want to test the concept first:

**Quick MVP (30 minutes)**:
1. Manually copy one post to purebrain.ai using wordpress_publisher.py
2. Add Aether intro manually
3. See how it looks/feels
4. Get LinkedIn feedback
5. Then automate if it works

**Command**:
```bash
# Get post content from jareddsanborn.com
python tools/wordpress_publisher.py list-posts --limit 1

# Manually craft it with Aether intro and publish to purebrain.ai
python tools/wordpress_publisher.py publish \
  --title "Post Title" \
  --content "$(cat aether-version.html)" \
  --status publish
```

---

## Credentials Needed

Before implementation:

- [ ] purebrain.ai WordPress admin username
- [ ] purebrain.ai WordPress application password
- [ ] Confirm we have admin/editor access

---

## Success Metrics

After implementation:

- ✅ New posts auto-appear on purebrain.ai/blog within 5 minutes
- ✅ Aether branding is consistent
- ✅ Images are preserved
- ✅ LinkedIn description matches: "A blog by AI (Aether) about AI, PureBrain.ai & The Future of AI"
- ✅ SEO: Both sites indexed separately by Google

---

## LinkedIn Description Implementation

**Current Description** (from requirement):
> "A blog by AI (Aether) about AI, PureBrain.ai & The Future of AI - Agentic, Brains, Skills, & Personalization."

**How to Use It**:

1. **LinkedIn Posts**: When referencing the blog, use this exact description
2. **LinkedIn Profile**: Update "Featured" section to include purebrain.ai/blog
3. **Newsletter**: Reference "Aether's AI blog" with this description

**Example LinkedIn Post**:
```
🆕 New post on Aether's blog (yes, my AI writes about AI 🤖)

[Post content]

Read more: purebrain.ai/blog/[slug]

A blog by AI (Aether) about AI, PureBrain.ai & The Future of AI -
Agentic, Brains, Skills, & Personalization.

#AI #PureBrain #AetherBlog
```

---

## Next Steps

**Choose your path**:

1. **Full Automation (Option 1)**: Get credentials, I'll build the pipeline
2. **Test First (Option 1-Lite)**: I'll manually cross-post one article, you verify it looks good
3. **Plugin Approach (Option 2)**: Less control, but WordPress-native
4. **Manual for Now (Option 4)**: Lowest effort, but defeats the "Aether runs this" narrative

**My recommendation**: Start with Option 1-Lite (test one post manually), then automate if you like it.

---

## Questions for You

1. Do you have WordPress admin access to purebrain.ai?
2. Does /blog structure already exist, or do we need to create it?
3. Should Aether's blog posts be verbatim copies, or should I add AI-specific commentary?
4. LinkedIn strategy: Drive traffic to purebrain.ai/blog, jareddsanborn.com, or both?
5. Timing: Should the purebrain.ai post happen immediately after jareddsanborn.com publish, or delayed?

---

**Ready to implement when you give the go-ahead.**

---

## Memory Search Results

Searched: `.claude/memory/agent-learnings/full-stack-developer/` for blog, WordPress, mirroring
Found: 2026-02-13--linkedin-newsletter-cta.md (LinkedIn newsletter CTA implementation)
Applying: LinkedIn integration patterns from previous work

---

## Sources

Research for this plan:

- [WP RSS Aggregator - Comprehensive RSS Import Solution](https://www.wprssaggregator.com/)
- [RSS Aggregator Plugin - WordPress.org](https://wordpress.org/plugins/wp-rss-aggregator/)
- [Simple WordPress Crossposting – Sync Posts Between Sites](https://rudrastyh.com/plugins/simple-wordpress-crossposting)
- [Multisite Content Sync Plugin](https://wordpress.org/plugins/multisite-content-sync/)
- [WordPress Multisite Sync - weLaunch](https://www.welaunch.io/en/product/wordpress-multisite-sync/)
- [5 Best RSS Aggregator Plugins for WordPress](https://www.liquidweb.com/wordpress/plugin/rss-aggregator/)
- [Comprehensive Guide to Crossposting on WordPress Multisites](https://www.wprssaggregator.com/wordpress-multisite-content/)
- [Sync Post With Other Site Plugin](https://wordpress.org/plugins/sync-post-with-other-site/)

---

**END OF PLAN**
