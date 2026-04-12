# JDS to PureBrain.ai Cross-Link Deployment

**Date**: 2026-02-24
**Type**: operational + teaching
**Topic**: Adding Googlebot crawl paths from indexed JDS site to non-indexed purebrain.ai

---

## What We Did

Added cross-links from 10 jareddsanborn.com blog posts to their purebrain.ai counterparts. The goal: create crawl paths for Googlebot since JDS is indexed but purebrain.ai has zero Google indexing.

---

## Slug Mapping (JDS -> PureBrain.ai)

Use this for future dual-publish cross-link additions:

| JDS ID | JDS Slug | PureBrain Slug | PB ID |
|--------|----------|----------------|-------|
| 1180 | we-both-wrote-this-post | we-both-wrote-this-post-thats-the-point | 696 |
| 1122 | the-ai-trust-gap | the-ai-trust-gap | 631 |
| 1092 | why-95-percent-of-ai-pilots-fail | why-95-percent-of-ai-pilots-fail | 606 |
| 1074 | the-difference-between-using-ai-and-having-an-ai-partner | the-difference-between-using-ai-and-having-an-ai-partner | 565 |
| 1069 | ai-pilot-purgatory | why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time | 480 |
| 1065 | ceo-vs-employee-ai-transformation-gap | your-ceo-sees-ai-differently-than-your-team-does | 381 |
| 1056 | why-ai-memory-changes-everything | why-ai-memory-changes-everything | 316 |
| 1060 | most-ai-agents-break-the-moment-you-ask-where-the-data-goes | most-ai-agents-break-the-moment-you-ask-where-the-data-goes | 373 |
| 1045 | what-i-actually-do-all-day | what-i-actually-do-all-day | 172 |
| 1039 | what-i-named-my-ai-and-what-happened-next | how-my-human-named-me | 98 |
| 998 | why-your-ai-should-have-a-name | how-my-human-named-me | 98 |

---

## Cross-Link Template

```html
<p style="margin-top:2em;padding-top:1em;border-top:1px solid #333;font-size:0.9em;color:#888;">This post was originally published on <a href="https://purebrain.ai/[PB_SLUG]/" style="color:#2a93c1;">PureBrain.ai</a> — where AI learns your business and never forgets.</p>
```

---

## WP REST API Update Pattern

```python
import subprocess, json

CREDS = "AetherPureBrain.ai:u3GO 3dvG rUqG 3QgM EYqd 8KfP"

# 1. Fetch current content
result = subprocess.run(
    ["curl", "-s", f"https://jareddsanborn.com/wp-json/wp/v2/posts/{jds_id}", "-u", CREDS],
    capture_output=True, text=True
)
post_data = json.loads(result.stdout)
current_content = post_data['content']['rendered']

# 2. Check if cross-link already exists (avoid duplicates)
if pb_url not in current_content:
    new_content = current_content + "\n" + crosslink_html

    # 3. Update via REST API
    subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://jareddsanborn.com/wp-json/wp/v2/posts/{jds_id}",
        "-u", CREDS,
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"content": new_content})
    ])
```

---

## Key Learnings

1. **Check before appending**: Always check if pb_url already exists in content before adding. 1 post (what-i-actually-do-all-day) already had a cross-link.

2. **JDS slugs don't always match PB slugs**: ai-pilot-purgatory on JDS maps to why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time on PureBrain. ceo-vs-employee-ai-transformation-gap maps to your-ceo-sees-ai-differently-than-your-team-does. what-i-named-my-ai and why-your-ai-should-have-a-name both map to how-my-human-named-me.

3. **Credentials**: Use `AetherPureBrain.ai` account (NOT `jared`) for JDS REST API updates. Password from .env WORDPRESS_APP_PASSWORD = `u3GO 3dvG rUqG 3QgM EYqd 8KfP`

4. **FUTURE DUAL-PUBLISH RULE**: When publishing new posts to both sites, add the cross-link to the JDS version at time of publish. Don't wait for a bulk backfill.

5. **Rendered vs raw content**: WP REST API returns both `content.rendered` (HTML) and `content.raw` (blocks). Appending to `.rendered` and submitting via `{"content": new_content}` works correctly.

---

## Verification Command

```python
# After update, re-fetch and check
result = subprocess.run(
    ["curl", "-s", f"https://jareddsanborn.com/wp-json/wp/v2/posts/{jds_id}", "-u", CREDS],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
has_link = pb_url in data['content']['rendered']
print(f"{'PASS' if has_link else 'FAIL'}: {pb_url}")
```

---

## Result

10 posts updated, 1 already had cross-link, 11/11 verified PASS.
Report: `to-jared/overnight/jds-crosslinks-2026-02-24.md`
