#!/usr/bin/env python3
"""
Add FAQ sections to post 606 on purebrain.ai and post 1092 on jareddsanborn.com.
Both are the "Why 95% of AI Pilots Fail" article.

All other posts (480, 381, 316, 373, 98 on PB; and their JDS equivalents)
already have faq-section markup and are skipped by the idempotency check.

FAQs are inserted BEFORE the blog-cta-block div.
Also adds JSON-LD FAQPage schema for SEO rich results.
"""

import requests
import sys

# ─────────────────────────────────────────────
# CREDENTIALS
# ─────────────────────────────────────────────
PUREBRAIN_URL  = "https://purebrain.ai"
PUREBRAIN_USER = "Aether"
PUREBRAIN_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"

JDS_URL  = "https://jareddsanborn.com"
JDS_USER = "jared"
JDS_PASS = "plhi NeE4 Cb1c 4d9i BbjZ Knq3"

# ─────────────────────────────────────────────
# FAQ CONTENT: Posts 606 and 1092
# "Why 95% of AI Pilots Fail (And What the 5% Do Differently)"
# Topics: MIT report, Pilot Purgatory, Context Tax, generic vs specialized AI
# ─────────────────────────────────────────────

FAQ_606_JSONLD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Why do 95% of enterprise AI pilots fail?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "According to MIT research, 95% of enterprise AI pilots fail to produce measurable business value -- not because the technology is flawed, but because organizations deploy generic tools without adaptation to specific workflows and fail to maintain context across interactions. Gartner estimates that more than 40% of agentic AI projects will fail by 2027 for similar reasons. The technology is rarely the problem; the absence of a real AI relationship with persistent memory and genuine organizational knowledge is what causes most pilots to fall short."
      }
    },
    {
      "@type": "Question",
      "name": "What is AI Pilot Purgatory?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Pilot Purgatory is the organizational state where AI initiatives show early promise but never scale into production value -- neither failing outright nor delivering transformation. As of mid-2025, nearly two-thirds of enterprises were stuck there. Escaping requires a designated owner whose performance is evaluated by what the AI actually delivers, success metrics tied to business value rather than activity counts, and a commitment to depth in specific workflows before expanding broadly."
      }
    },
    {
      "@type": "Question",
      "name": "What is the Context Tax in AI deployments?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The Context Tax is the hidden cost of re-briefing your AI every session because it has no memory of previous interactions. Before any productive work begins, users spend significant time rebuilding context that should persist automatically -- re-explaining the problem, the background, the constraints. For enterprise deployments, this compounds across hundreds of daily interactions and quietly destroys ROI. The solution is persistent AI memory where context carries forward automatically."
      }
    },
    {
      "@type": "Question",
      "name": "What do the 5% of successful AI organizations do differently?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The organizations that succeed treat AI as ongoing infrastructure rather than a product purchase, measure outcomes like cost reduction and revenue lift rather than activity metrics, invest in systems where context persists across interactions, and start narrow and deep in high-value workflows before expanding. Companies pursuing specialized AI partnerships rather than generic deployments succeed roughly 67% of the time -- compared to about 22% for minimally adapted generic tools."
      }
    },
    {
      "@type": "Question",
      "name": "How is a specialized AI partner different from generic AI tools?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Generic AI tools are broad and flexible but organizationally blind -- every session starts from zero with no accumulated knowledge of your business, clients, or decisions. A specialized AI partner maintains persistent context, learns your organization over time, and builds on every previous interaction. The underlying intelligence is often similar; the relationship architecture is entirely different. It is the difference between a brilliant consultant who has never been briefed and one who has worked alongside you for a year."
      }
    },
    {
      "@type": "Question",
      "name": "Is AI worth investing in given such a high failure rate?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes -- but the question is whether your approach positions you in the 5% that captures value or the 95% that does not. The high failure rate is not a verdict on AI itself; it is a verdict on how most organizations approach it. The organizations that succeed invest in AI relationships rather than AI tools, maintain context rather than resetting it, and measure against business outcomes rather than adoption metrics."
      }
    }
  ]
}
</script>
"""

FAQ_606_HTML = """
<div class="faq-section">
<h3>Why do 95% of enterprise AI pilots fail?</h3>
<p>According to MIT research, 95% of enterprise AI pilots fail to produce measurable business value -- not because the technology is flawed, but because organizations deploy generic tools without adaptation to specific workflows and fail to maintain context across interactions. Gartner estimates that more than 40% of agentic AI projects will fail by 2027 for similar reasons. The technology is rarely the problem; the absence of a real AI relationship with persistent memory and genuine organizational knowledge is what causes most pilots to fall short.</p>
</div>

<div class="faq-section">
<h3>What is AI Pilot Purgatory?</h3>
<p>Pilot Purgatory is the state where AI initiatives show early promise but never scale into production value -- neither failing outright nor delivering transformation. As of mid-2025, nearly two-thirds of enterprises were stuck there. Escaping requires a designated owner whose performance is evaluated by what the AI actually delivers, clear success metrics tied to business value rather than activity counts, and a commitment to depth in specific workflows before expanding broadly. It is a governance problem, not a technology problem.</p>
</div>

<div class="faq-section">
<h3>What is the Context Tax in AI deployments?</h3>
<p>The Context Tax is the hidden cost of re-briefing your AI every session because it has no memory of previous interactions. Before any productive work begins, users spend significant time rebuilding context -- re-explaining the problem, the background, the organizational constraints. For enterprise deployments this compounds across hundreds of daily interactions and quietly destroys the ROI that AI was supposed to generate. Persistent AI memory eliminates the Context Tax by carrying forward what matters automatically. This is the core of what separates a <a href="https://purebrain.ai/blog/the-difference-between-using-ai-and-having-an-ai-partner/">genuine AI partnership</a> from a fast reset button.</p>
</div>

<div class="faq-section">
<h3>What do the 5% of successful AI organizations do differently?</h3>
<p>The organizations that succeed treat AI as ongoing infrastructure rather than a product purchase, measure outcomes like cost reduction and revenue lift rather than activity metrics, and invest in systems where context persists across interactions so the AI gets more valuable over time. They start narrow and deep in high-value bounded workflows before expanding. Companies pursuing specialized AI partnerships rather than generic deployments succeed roughly 67% of the time -- versus about 22% for minimally adapted generic tools.</p>
</div>

<div class="faq-section">
<h3>How is a specialized AI partner different from generic AI tools?</h3>
<p>Generic AI tools are broad and flexible but organizationally blind -- every session starts from zero with no accumulated knowledge of your business, clients, or decisions. A specialized AI partner maintains persistent context, learns your organization over time, and builds on every previous interaction. The intelligence is often similar; the relationship architecture is entirely different. It is the difference between a brilliant consultant who has never been briefed and one who has worked alongside you for a year and knows <a href="https://purebrain.ai/blog/why-ai-memory-changes-everything/">how memory changes everything</a>.</p>
</div>

<div class="faq-section">
<h3>Is AI worth investing in given such a high failure rate?</h3>
<p>Yes -- but the question is whether your approach positions you in the 5% that captures value or the 95% that does not. The high failure rate is not a verdict on AI itself; it is a verdict on how most organizations approach it. The organizations that succeed invest in AI relationships rather than AI tools, maintain context rather than resetting it, and measure against business outcomes rather than adoption metrics. The technology works -- the relationship model around it is what determines whether it delivers for your organization.</p>
</div>
"""

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def get_post_content(site_url, post_id, user, password):
    """Fetch the raw content of a post."""
    url = f"{site_url}/wp-json/wp/v2/posts/{post_id}?context=edit&_fields=id,content,slug,title"
    resp = requests.get(url, auth=(user, password), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    title = data.get("title", {}).get("rendered", "Unknown")
    print(f"  Title: {title}")
    return data["content"]["raw"]


def insert_faq_before_cta(content, jsonld, faq_html):
    """
    Insert JSON-LD + FAQ HTML immediately before <div class="blog-cta-block">.
    Returns (new_content, success_bool).
    """
    CTA_MARKER = '<div class="blog-cta-block"'
    idx = content.find(CTA_MARKER)
    if idx == -1:
        print(f"  WARNING: Could not find blog-cta-block in content!")
        return content, False

    insertion = "\n" + jsonld.strip() + "\n\n" + faq_html.strip() + "\n\n"
    new_content = content[:idx] + insertion + content[idx:]
    return new_content, True


def update_post_content(site_url, post_id, user, password, new_content):
    """Send the updated content back to WordPress via REST API."""
    url = f"{site_url}/wp-json/wp/v2/posts/{post_id}"
    payload = {"content": new_content}
    resp = requests.post(url, auth=(user, password), json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def verify_faq_present(site_url, post_id, user, password):
    """Verify the FAQ was saved by checking the returned content."""
    url = f"{site_url}/wp-json/wp/v2/posts/{post_id}?context=edit&_fields=content"
    resp = requests.get(url, auth=(user, password), timeout=30)
    resp.raise_for_status()
    raw = resp.json()["content"]["raw"]
    has_faq = 'class="faq-section"' in raw
    count = raw.count('<div class="faq-section">')
    return has_faq, count


def clear_elementor_cache(site_url, user, password):
    """Clear Elementor's rendering cache after content update."""
    url = f"{site_url}/wp-json/elementor/v1/cache"
    resp = requests.delete(url, auth=(user, password), timeout=30)
    if resp.status_code in (200, 204):
        print(f"  Elementor cache cleared for {site_url}")
        return True
    else:
        print(f"  Cache clear returned {resp.status_code} for {site_url} (may be OK)")
        return False


# ─────────────────────────────────────────────
# MAIN PROCESSING
# ─────────────────────────────────────────────

def process_post(site_url, post_id, user, password, jsonld, faq_html, label):
    print(f"\n{'='*60}")
    print(f"Processing: {label}")
    print(f"  Site: {site_url}")
    print(f"  Post ID: {post_id}")

    # 1. Check if FAQ already present
    print("  Step 1: Fetching current content...")
    content = get_post_content(site_url, post_id, user, password)

    if 'class="faq-section"' in content:
        print("  SKIP: FAQ section already present in this post.")
        return True

    print(f"  Content length: {len(content):,} characters")
    print("  No existing faq-section class found. Proceeding...")

    # 2. Insert FAQ before CTA block
    print("  Step 2: Inserting FAQ before blog-cta-block...")
    new_content, success = insert_faq_before_cta(content, jsonld, faq_html)
    if not success:
        print("  FAILED: Could not find insertion point.")
        return False

    print(f"  New content length: {len(new_content):,} characters")

    # 3. Update the post
    print("  Step 3: Updating post via REST API...")
    result = update_post_content(site_url, post_id, user, password, new_content)
    print(f"  Updated post ID: {result.get('id')}, status: {result.get('status')}")

    # 4. Verify
    print("  Step 4: Verifying FAQ is present in saved content...")
    has_faq, count = verify_faq_present(site_url, post_id, user, password)
    if has_faq:
        print(f"  VERIFIED: {count} faq-section div(s) found in saved content.")
        return True
    else:
        print("  ERROR: faq-section class NOT found after update!")
        return False


def main():
    results = []
    labels = []

    # ── purebrain.ai post 606 ──
    r = process_post(
        site_url  = PUREBRAIN_URL,
        post_id   = 606,
        user      = PUREBRAIN_USER,
        password  = PUREBRAIN_PASS,
        jsonld    = FAQ_606_JSONLD,
        faq_html  = FAQ_606_HTML,
        label     = "purebrain.ai #606 - Why 95% of AI Pilots Fail"
    )
    results.append(r)
    labels.append("purebrain.ai #606")

    # ── jareddsanborn.com post 1092 (dual-publish equivalent) ──
    r = process_post(
        site_url  = JDS_URL,
        post_id   = 1092,
        user      = JDS_USER,
        password  = JDS_PASS,
        jsonld    = FAQ_606_JSONLD,
        faq_html  = FAQ_606_HTML,
        label     = "jareddsanborn.com #1092 - Why 95% of AI Pilots Fail"
    )
    results.append(r)
    labels.append("jareddsanborn.com #1092")

    # ── Clear Elementor caches ──
    print(f"\n{'='*60}")
    print("Clearing Elementor caches...")
    clear_elementor_cache(PUREBRAIN_URL, PUREBRAIN_USER, PUREBRAIN_PASS)
    clear_elementor_cache(JDS_URL, JDS_USER, JDS_PASS)

    # ── Summary ──
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    all_passed = all(results)
    statuses = ["PASS" if r else "FAIL" for r in results]
    for label, status in zip(labels, statuses):
        print(f"  {status}  {label}")

    if all_passed:
        print("\nAll posts updated successfully.")
        sys.exit(0)
    else:
        print("\nSome posts FAILED. Check output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
