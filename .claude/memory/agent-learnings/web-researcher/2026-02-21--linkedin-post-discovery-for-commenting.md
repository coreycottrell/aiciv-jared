# Research: LinkedIn Post Discovery for Thought Leader Commenting

**Date**: 2026-02-21
**Agent**: web-researcher
**Type**: technique + gotcha
**Topic**: Finding recent LinkedIn post URLs for AI thought leaders

---

## Context

Task: Find direct clickable LinkedIn post URLs from 4 AI thought leaders
(Pascal Bornet, Ethan Mollick, Bernard Marr, Allie K. Miller) for Jared to comment on.

---

## Key Techniques That Worked

1. **Search for their article/Substack first** - Thought leaders post their articles to
   LinkedIn. Find the article URL, then search for the LinkedIn post version.
   Pattern: "[Name] LinkedIn [article title] activity" often returns the post URL.

2. **Use activity feed as fallback**: `linkedin.com/today/author/[handle]` and
   `linkedin.com/in/[handle]/recent-activity/shares/` always work for finding recent posts
   even when specific post URLs aren't indexed.

3. **Search their X/Twitter for LinkedIn shares**: Thought leaders often share LinkedIn
   post links on X. Search: `"[name]" site:x.com linkedin.com/posts`

4. **Substack newsletters mirror LinkedIn content**: Pascal Bornet's Substack newsletter
   content = his LinkedIn posts. Same pattern likely works for other newsletter-active voices.

---

## Gotchas

1. **LinkedIn returns HTTP 999** for any programmatic scraping attempt (WebFetch tool).
   LinkedIn pages cannot be fetched directly. Must use search engine indexing.

2. **LinkedIn post URLs are rarely indexed by Google** unless the post got massive
   external sharing. High-activity-ID posts (74xx etc.) from Feb 2026 were almost never
   in search results.

3. **Activity ID numbers are sequential timestamps** - higher number = more recent.
   Activity IDs in the 7.4 billion range = roughly late 2025/early 2026.
   Activity IDs in the 7.2-7.3 billion range = roughly mid-2025.
   Activity IDs in the 6.x billion range = 2021-2022 era.

4. **Bernard Marr's website shows article dates as Feb 2026** but the corresponding
   LinkedIn post may have been Dec 2025 (articles get repurposed). Always cross-check.

5. **Allie Miller's most-indexed LinkedIn post** was from Dec 29, 2025 (2026 AI predictions).
   Her Feb 2026 posts were not yet indexed at time of research.

---

## Confirmed Post URLs (Feb 2026)

| Person | Post URL | Date |
|--------|----------|------|
| Ethan Mollick | https://www.linkedin.com/posts/emollick_a-guide-to-which-ai-to-use-in-the-agentic-activity-7429704014352527360-Gv4H | Feb 18, 2026 |
| Bernard Marr | https://www.linkedin.com/posts/bernardmarr_the-growing-ai-backlash-is-the-revolution-activity-7411657138298728448-poNs | Feb 17, 2026 |

---

## Sources
- Ethan Mollick Substack: https://www.oneusefulthing.org/
- Pascal Bornet Newsletter: https://pascalbornet.substack.com/
- Bernard Marr site: https://bernardmarr.com/
- Allie K Miller site: https://www.alliekmiller.com/

---

## When to Apply

Any future request to find recent LinkedIn post URLs from public thought leaders.
Use this technique sequence:
1. Find their most recent article/newsletter
2. Search "[name] LinkedIn [article title] activity"
3. Use activity feed as fallback
4. Check X/Twitter for shared LinkedIn links
