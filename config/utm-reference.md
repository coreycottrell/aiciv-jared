# content-specialist: UTM Parameter Master Reference

**Agent**: content-specialist
**Domain**: Content Creation & Storytelling
**Date**: 2026-02-23

---

# PureBrain.ai UTM Parameter Master Reference

**Purpose**: Governs all UTM parameters across every PureBrain touchpoint. Use this document when creating any link that will appear in email, social media, blog posts, or landing pages.

**Rule of thumb**: If the link leaves PureBrain.ai or arrives from an external source, it gets a UTM tag.

---

## Why UTM Discipline Matters

Without consistent UTM parameters, Google Analytics 4 cannot tell you whether a conversion came from a newsletter, a LinkedIn post, or an organic blog visit. Every link from every channel needs a consistent, parseable UTM structure.

A single broken or inconsistent tag silently corrupts your attribution data. Follow this reference exactly.

---

## UTM Framework Architecture

```
utm_source   = WHERE the traffic comes from (the platform or property)
utm_medium   = HOW it arrived (the channel type)
utm_campaign = WHAT campaign sent it (the specific initiative)
utm_content  = WHICH specific element was clicked (for A/B testing)
utm_term     = (optional) WHAT search term triggered it — paid search only
```

**Full URL structure:**
```
https://purebrain.ai/[path]/?utm_source=[source]&utm_medium=[medium]&utm_campaign=[campaign]&utm_content=[content]
```

---

## Master Parameter Reference Tables

### Sources (`utm_source`) — WHERE traffic comes from

| Value | Use When |
|-------|----------|
| `newsletter` | Links in any Brevo email send to the full Neural Feed list |
| `welcome-sequence` | Links in the 7-email welcome sequence |
| `audit-nurture` | Links in the 4-email audit nurture sequence |
| `blog` | Internal cross-links from one blog post to another |
| `linkedin` | Links in LinkedIn posts or LinkedIn articles |
| `bluesky` | Links in Bluesky posts |
| `assessment` | Links from the AI Adoption Assessment page |
| `audit` | Links from the AI Partnership Audit page |
| `purebrain` | Links from the purebrain.ai homepage (internal navigation) |
| `organic` | Direct traffic, bookmarks (not usually set manually) |
| `referral` | Partner or third-party links |

---

### Mediums (`utm_medium`) — HOW it arrived

| Value | Use When |
|-------|----------|
| `email` | All email sends (newsletter, sequences, transactional) |
| `social` | Social media platforms (LinkedIn, Bluesky) |
| `website` | Internal links from our own website properties |
| `cta` | Call-to-action buttons (use with `utm_source=blog` or `utm_source=assessment`) |
| `referral` | External site links to us |

---

### Campaigns (`utm_campaign`) — WHAT campaign sent it

| Value | Use When |
|-------|----------|
| `neural-feed-rss` | Automated RSS campaign emails |
| `neural-feed-weekly` | Manually sent weekly Neural Feed issues |
| `welcome-sequence` | 7-email new subscriber welcome |
| `audit-nurture` | 4-email audit completion follow-up |
| `re-engagement` | 3-email re-engagement series |
| `ai-partnership-audit` | AI Partnership Audit page and lead magnet |
| `ai-adoption-assessment` | AI Adoption Assessment page |
| `blog-[slug]` | Blog-post-specific campaigns — replace `[slug]` with the post slug (e.g., `blog-trust-gap`) |
| `linkedin-organic` | Organic LinkedIn content without paid spend |
| `bluesky-thread` | Bluesky thread posts |

---

### Content (`utm_content`) — WHICH element was clicked

| Value | Use When |
|-------|----------|
| `read-post` | Primary "Read the full post" CTA in RSS emails |
| `blog-footer` | Footer link to blog index |
| `footer-cta` | Footer CTA in email (secondary ask) |
| `header-nav` | Navigation bar links |
| `inline-link` | In-body text links within blog posts |
| `sidebar-cta` | Sidebar call-to-action widgets |
| `banner-cta` | Banner or hero CTA buttons |
| `ps-link` | P.S. section links in emails |
| `post-cta` | Primary CTA at the bottom of a social post |
| `post-link` | Link to a blog post within a social post |
| `thread-link` | Link within a Bluesky thread |
| `email-1` through `email-7` | Specific email in a sequence (for per-email link tracking) |

---

## Pre-Built UTM Link Templates

Copy, paste, and replace `[POST-SLUG]` or `[SOURCE-SLUG]` / `[TARGET-SLUG]` with the actual post slug.

---

### Email — Neural Feed Newsletter

**Blog post read CTA:**
```
https://purebrain.ai/blog/[POST-SLUG]/?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-weekly&utm_content=read-post
```

**Blog index footer link:**
```
https://purebrain.ai/blog/?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-weekly&utm_content=blog-footer
```

**Homepage awakening CTA:**
```
https://purebrain.ai/#awakening?utm_source=newsletter&utm_medium=email&utm_campaign=neural-feed-weekly&utm_content=footer-cta
```

---

### Email — Welcome Sequence (adjust `email-N` for each email)

**Email 1 primary CTA:**
```
https://purebrain.ai/#awakening?utm_source=welcome-sequence&utm_medium=email&utm_campaign=welcome-sequence&utm_content=email-1
```

**Email 4 CTA:**
```
https://purebrain.ai/#awakening?utm_source=welcome-sequence&utm_medium=email&utm_campaign=welcome-sequence&utm_content=email-4
```

---

### Email — Audit Nurture Sequence

**Audit nurture Email 1 CTA:**
```
https://purebrain.ai/#awakening?utm_source=audit-nurture&utm_medium=email&utm_campaign=audit-nurture&utm_content=email-1
```

**Audit nurture Email 4 (direct ask):**
```
https://purebrain.ai/#awakening?utm_source=audit-nurture&utm_medium=email&utm_campaign=audit-nurture&utm_content=email-4
```

---

### Social — LinkedIn Posts

**LinkedIn post CTA to homepage:**
```
https://purebrain.ai/#awakening?utm_source=linkedin&utm_medium=social&utm_campaign=linkedin-organic&utm_content=post-cta
```

**LinkedIn post to a specific blog post:**
```
https://purebrain.ai/blog/[POST-SLUG]/?utm_source=linkedin&utm_medium=social&utm_campaign=linkedin-organic&utm_content=post-link
```

---

### Social — Bluesky Threads

**Bluesky thread to a specific blog post:**
```
https://purebrain.ai/blog/[POST-SLUG]/?utm_source=bluesky&utm_medium=social&utm_campaign=bluesky-thread&utm_content=thread-link
```

**Bluesky thread to homepage:**
```
https://purebrain.ai/#awakening?utm_source=bluesky&utm_medium=social&utm_campaign=bluesky-thread&utm_content=cta
```

---

### Landing Pages — Assessment and Audit

**Assessment page inline CTA:**
```
https://purebrain.ai/#awakening?utm_source=assessment&utm_medium=cta&utm_campaign=ai-adoption-assessment&utm_content=banner-cta
```

**Audit page to homepage:**
```
https://purebrain.ai/#awakening?utm_source=audit&utm_medium=cta&utm_campaign=ai-partnership-audit&utm_content=banner-cta
```

---

### Blog — Internal Cross-Links

**Blog post linking to another blog post:**
```
https://purebrain.ai/blog/[TARGET-SLUG]/?utm_source=blog&utm_medium=website&utm_campaign=blog-[SOURCE-SLUG]&utm_content=inline-link
```

**Blog post CTA to homepage:**
```
https://purebrain.ai/#awakening?utm_source=blog&utm_medium=cta&utm_campaign=blog-[SOURCE-SLUG]&utm_content=footer-cta
```

---

## GA4 Setup: Custom Dimensions for UTM Reporting

For UTMs to surface in Google Analytics 4 reports:

1. Go to: GA4 → Admin → Data Streams → purebrain.ai → Configure tag settings
2. Enable "Allow manual tagging to override auto-tagging" if using Google Ads
3. Create custom dimensions (GA4 → Admin → Custom Definitions → Create):
   - `utm_campaign` → Event-scoped → parameter: `campaign`
   - `utm_content` → Event-scoped → parameter: `content`
   - `utm_source` → Event-scoped → parameter: `source`
   - `utm_medium` → Event-scoped → parameter: `medium`
4. Build an Exploration Report: Free Form, add dimensions Source / Medium / Campaign / Content, add metrics Sessions and Conversions

---

## Governance Rules

1. **All lowercase.** Write `newsletter`, not `Newsletter`. GA4 is case-sensitive — mixed case creates duplicate entries in reports.

2. **Hyphens, not underscores.** Write `audit-nurture`, not `audit_nurture`. Hyphens are URL-safe and human-readable.

3. **No spaces.** Spaces break URLs. Use hyphens everywhere.

4. **Tag every link in every email.** Not just the primary CTA. Footer links, P.S. links, image links — all of them.

5. **Update this document when new campaigns are created.** A stale reference produces stale data.

6. **Validate before publishing.** Paste any new UTM URL into Google's Campaign URL Builder at `ga-dev-tools.google.com/campaign-url-builder/` to confirm it is well-formed.

---

*Last updated: 2026-02-23. Source: brevo-automation-plan.md, ITEM 2.*
