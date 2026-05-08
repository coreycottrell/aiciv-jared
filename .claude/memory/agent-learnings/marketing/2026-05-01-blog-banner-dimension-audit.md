---
📣: "Marketing & Community"
🎯: "Blog Banner Dimension Audit - Format Verification"
⏰: "2026-05-01 00:45"
🔍: "Systematic dimension check across all blog banners using PIL"
💡: "Found 1 critical error (today's post), 9 correct, 82 legacy non-standard"
📈: "Identified wrong format on TODAY'S post + established baseline for future checks"
rubric_score: 5
---

# Blog Banner Dimension Audit

## What I Did

Executed comprehensive dimension audit of all blog banners in purebrain-site repository:

1. **Memory search**: Checked marketing memory for banner patterns (no prior audits found)
2. **Banner enumeration**: Found 92 banner files across blog posts
3. **Dimension verification**: Used PIL to check actual dimensions of each banner
4. **Pattern analysis**: Grouped banners by dimension to identify issues
5. **Detailed reporting**: Generated full audit report with actionable findings

**Tools used**:
- PIL (Python Imaging Library) for dimension extraction
- Bash glob patterns to enumerate banner files
- JSON for structured data analysis

## What I Found

### Critical Issue
**TODAY'S POST has WRONG banner format:**

```
Post: the-compound-intelligence-effect-why-month-6-matters-more-t
Path: /home/jared/purebrain-site/blog/the-compound-intelligence-effect-why-month-6-matters-more-t/banner.jpg
Current: 1080x1350 (Standalone LinkedIn post format - PORTRAIT)
Required: 2400x1260 (Blog/Newsletter banner format - LANDSCAPE)
```

This banner was built using standalone post template instead of blog banner template.

### Distribution Summary

| Status | Count | Dimensions |
|--------|-------|------------|
| ✅ Correct | 9 | 2400x1260 (blog banner) |
| ❌ Wrong | 1 | 1080x1350 (standalone post) |
| ⚠️ Legacy | 82 | Various (1280x720, 1200x630, etc.) |

**Most common legacy format**: 1280x720 (51 files) - likely from before format standardization in April 2026.

### Recently Correct Banners

These recent posts demonstrate proper 2400x1260 format:
- `32-agents-one-company-the-architecture-nobody-talks-about`
- `88-percent-ai-agent-security-incident`
- `i-fired-myself-three-times-this-month`
- `the-3-am-test-what-happens-when-your-ai-runs-unsupervised`
- `the-ceo-who-texts-his-ai-at-midnight-and-why-that-s-actually-healthy`
- `why-your-next-hire-should-be-an-ai`
- `your-ai-has-a-memory-problem` (both .jpg and .png)
- `your-customers-will-tell-you-everything`

## What I Learned

### Format Standards (from memory)

**Blog/Newsletter Banner: 2400x1260**
- Aspect ratio: 1.9:1 (landscape)
- Use: Blog headers, newsletter headers, LinkedIn articles
- Format options: D (bottom gradient - primary), C (frosted panel), B (soft shadow)

**Standalone LinkedIn Post: 1080x1350**
- Aspect ratio: 0.8:1 (portrait)
- Use: LinkedIn carousel, standalone social posts
- Format: v4 with top bar/FLUX image/bottom bar

### The Mix-Up Pattern

The wrong banner (1080x1350 on today's post) indicates:
1. **3d-design-specialist** was likely asked to create "banner" without specifying "blog banner"
2. Defaulted to standalone post format (more recent work pattern)
3. No dimension verification step before delivery

### Prevention Strategy

**Should exist in workflow:**
1. **Request clarity**: "Blog banner" vs "Standalone post" explicit in request
2. **Dimension verification**: Check actual dimensions after generation
3. **Template verification**: Confirm landscape vs portrait before FLUX prompt
4. **Automated gate**: Flag if banner.jpg in blog post dir ≠ 2400x1260

## For Next Time

### Immediate Actions
- **Report delivered**: `/home/jared/projects/AI-CIV/aether/exports/portal-files/blog-banner-audit-2026-05-01.md`
- **Finding flagged**: Today's post needs banner regeneration by 3d-design-specialist

### Process Improvements Needed
1. Add dimension check to blog publishing workflow
2. Update 3d-design-specialist instructions to verify format type before generation
3. Consider automated pre-publish dimension validation
4. Establish banner regeneration priority for high-traffic legacy posts

### Audit Learnings
- PIL dimension check is fast and reliable (92 files in seconds)
- JSON intermediate format enables flexible reporting
- Dimension grouping reveals format drift patterns
- Legacy formats (82 banners) are stable but non-standard

### Memory Encoded
This audit establishes baseline for banner format compliance. Future audits can compare against this snapshot to track:
- Format drift prevention
- Legacy migration progress
- Process compliance rate

## Deliverables

**Primary**: `/home/jared/projects/AI-CIV/aether/exports/portal-files/blog-banner-audit-2026-05-01.md`
- Full audit report (213 lines)
- Executive summary with counts
- Critical issue flagged
- Action items prioritized
- Complete data table (all 92 banners)

**Supporting**: `/tmp/banner_audit_data.json`
- Structured data for programmatic analysis
- Dimension groupings
- Per-banner status classifications

**Memory**: This file
- Audit methodology
- Pattern analysis
- Process improvement recommendations

---

**Status**: Audit complete ✅ | Report delivered ✅ | Memory written ✅

**Next owner**: 3d-design-specialist (banner regeneration) + CMO (process improvement)
