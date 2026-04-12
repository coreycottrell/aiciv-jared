#!/usr/bin/env python3
"""
Deploy FAQ sections to the Trust Gap blog post on both purebrain.ai and jareddsanborn.com.

Posts:
  - purebrain.ai ID=631   slug=the-ai-trust-gap
  - jareddsanborn.com ID=1122  slug=the-ai-trust-gap

Method:
  1. Fetch raw content with context=edit
  2. Idempotency check: skip if 'faq-section' already present
  3. Build FAQ HTML with JSON-LD FAQPage schema
  4. Insert BEFORE <div class="blog-cta-block" on PB, BEFORE final <hr> on JDS
  5. POST updated content back via REST API
  6. Re-fetch and verify FAQ present

Author: full-stack-developer agent
Date: 2026-02-22
"""

import requests
import base64
import json
import re
import sys

# ─── Credentials ──────────────────────────────────────────────────────────────

PB_CREDS  = base64.b64encode(b'Aether:FlFr2VOtlHiHaJWjzW96OHUJ').decode()
JDS_CREDS = base64.b64encode('AetherPureBrain.ai:u3GO 3dvG rUqG 3QgM EYqd 8KfP'.encode()).decode()

PB_HEADERS  = {'Authorization': f'Basic {PB_CREDS}',  'Content-Type': 'application/json'}
JDS_HEADERS = {'Authorization': f'Basic {JDS_CREDS}', 'Content-Type': 'application/json'}

PB_BASE  = 'https://purebrain.ai/wp-json/wp/v2'
JDS_BASE = 'https://jareddsanborn.com/wp-json/wp/v2'

# ─── FAQ Content ──────────────────────────────────────────────────────────────

FAQ_ITEMS = [
    {
        "q": "What is the AI trust gap?",
        "a": "The AI trust gap is the significant difference between how much organizations trust AI for routine tasks versus strategic decisions. A 2025 Alteryx survey found that 50% of business leaders trust AI for repetitive work, but only 28% trust it for decision-making. That 22-point drop isn't a technology problem—it's a relationship problem. Organizations haven't given AI the opportunity to build a track record that earns higher-stakes trust."
    },
    {
        "q": "Why don't organizations trust AI for strategic decisions?",
        "a": "Most AI deployments keep AI in 'first-week employee' status permanently. You give it a task, it produces an output, and the interaction ends. There's no accumulation of context, no deepening relationship, no demonstrated judgment across many interactions. Trust at the strategic level requires time, consistency, and the AI knowing your priorities, history, and what went wrong last quarter. Capability pilots test what AI can do—they don't build the relationship needed to trust it with consequential decisions."
    },
    {
        "q": "What is AI pilot purgatory and how does it relate to trust?",
        "a": "AI pilot purgatory describes the situation where 75% of enterprise AI pilots stall before reaching production. Organizations prove AI could help, but somehow nothing advances. In almost every case, the root issue is trust—not in AI's raw capability, but in whether this specific AI knows enough about the organization to be trusted with real responsibility. The pilot proved capability; it didn't build the relationship."
    },
    {
        "q": "How do you build trust with an AI system over time?",
        "a": "Trust builds the same way it does with any new team member: through repeated interactions, demonstrated judgment, and accumulated context. An AI that remembers your priorities, has seen how you handle uncertainty, and has built up a track record of smaller decisions earns the right to weigh in on bigger ones. This requires moving from one-off task delegation to a genuine ongoing partnership—where the AI carries forward context session after session rather than starting fresh each time."
    },
    {
        "q": "Is the AI trust gap really a bigger barrier than technology limitations?",
        "a": "Yes, according to current data. Only 8.6% of companies have AI agents in production despite broad awareness of AI capabilities. The bottleneck isn't technology—organizations have already seen what AI can do in pilots. The barrier is trust: leaders aren't confident that their AI understands their organization well enough to be trusted with consequential work. Solving the trust gap requires a different approach to AI deployment, not better AI models."
    },
    {
        "q": "What's the difference between testing AI capability and building AI trust?",
        "a": "Capability testing answers: 'Can this AI do the thing?' It's a one-time demonstration—can it summarize documents, draft communications, analyze data? Trust building answers: 'Has this AI earned the right to handle real responsibility?' That requires watching how it operates in context over time, seeing how it handles unexpected situations, observing whether its judgment aligns with yours on smaller decisions before handing it bigger ones. Most organizations only do the first. The ones with production AI do both."
    }
]

def build_faq_html():
    """Build complete FAQ section: JSON-LD schema + accordion HTML."""

    # Build JSON-LD entities
    entities = []
    for item in FAQ_ITEMS:
        entities.append({
            "@type": "Question",
            "name": item["q"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": item["a"]
            }
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities
    }

    # Build accordion items
    accordion_items = ""
    for item in FAQ_ITEMS:
        accordion_items += f"""<details style="margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px;">
<summary style="cursor: pointer; font-weight: 600; color: #ffffff; padding: 8px 0; font-size: 16px; list-style: none; display: flex; justify-content: space-between; align-items: center;">{item['q']}</summary>
<p style="color: rgba(255,255,255,0.75); padding: 8px 0 4px 0; line-height: 1.6;">{item['a']}</p>
</details>
"""

    faq_html = f"""<div class="faq-section pb-faq-section" style="margin: 40px 0; padding: 30px; background: rgba(10,15,30,0.6); border: 1px solid rgba(42,147,193,0.2); border-radius: 12px;">
<h2 style="color: #2a93c1; font-size: 22px; margin-bottom: 20px;">Frequently Asked Questions</h2>
<script type="application/ld+json">
{json.dumps(schema, indent=2)}
</script>
{accordion_items}</div>
"""
    return faq_html


def deploy_faq(site_name, base_url, headers, post_id):
    """Fetch post, check idempotency, inject FAQ, update, verify."""

    print(f"\n{'='*60}")
    print(f"Deploying FAQ to {site_name} post ID={post_id}")
    print(f"{'='*60}")

    # Step 1: Fetch raw content
    r = requests.get(f'{base_url}/posts/{post_id}?context=edit', headers=headers, timeout=30)
    if r.status_code != 200:
        print(f"  ERROR: GET returned {r.status_code}: {r.text[:200]}")
        return False

    data = r.json()
    raw = data['content']['raw']
    title = data['title']['rendered']
    print(f"  Title: {title}")
    print(f"  Content length: {len(raw)} chars")

    # Step 2: Idempotency check
    if 'faq-section' in raw or 'pb-faq-section' in raw or 'FAQPage' in raw:
        print(f"  SKIP: FAQ already present on this post.")
        return True

    # Step 3: Build FAQ HTML
    faq_html = build_faq_html()
    print(f"  FAQ HTML built: {len(faq_html)} chars, {len(FAQ_ITEMS)} items")

    # Step 4: Find insertion point and inject
    # Priority 1: insert before <div class="blog-cta-block"
    # Priority 2: insert before final <hr>
    # Priority 3: append at end of content
    cta_match = re.search(r'<div[^>]*class="blog-cta-block[^"]*"[^>]*>', raw)
    if cta_match:
        insertion_idx = cta_match.start()
        print(f"  Insertion point: before blog-cta-block at index {insertion_idx}")
        new_content = raw[:insertion_idx] + faq_html + "\n" + raw[insertion_idx:]
    else:
        hr_idx = raw.rfind('<hr')
        if hr_idx != -1:
            print(f"  Insertion point: before final <hr> at index {hr_idx}")
            new_content = raw[:hr_idx] + faq_html + "\n" + raw[hr_idx:]
        else:
            # Fallback: append at end
            print(f"  Insertion point: appending at end of content (no cta-block or hr found)")
            new_content = raw.rstrip() + "\n\n" + faq_html

    # Step 5: Update via REST API
    payload = json.dumps({"content": new_content})
    r2 = requests.post(f'{base_url}/posts/{post_id}', headers=headers, data=payload, timeout=30)
    if r2.status_code not in (200, 201):
        print(f"  ERROR: POST returned {r2.status_code}: {r2.text[:300]}")
        return False
    print(f"  POST update: {r2.status_code} OK")

    # Step 6: Verify
    r3 = requests.get(f'{base_url}/posts/{post_id}?context=edit', headers=headers, timeout=30)
    updated_raw = r3.json()['content']['raw']
    faq_count = updated_raw.count('class="faq-section')
    schema_count = updated_raw.count('FAQPage')
    print(f"  Verification: faq-section divs={faq_count}, FAQPage schemas={schema_count}")

    if faq_count > 0 and schema_count > 0:
        print(f"  SUCCESS: FAQ deployed and verified.")
        return True
    else:
        print(f"  ERROR: FAQ not found after update!")
        return False


def clear_elementor_cache():
    """Clear Elementor cache on purebrain.ai."""
    r = requests.delete(
        'https://purebrain.ai/wp-json/elementor/v1/cache',
        headers=PB_HEADERS,
        timeout=20
    )
    print(f"\n  Elementor cache clear: {r.status_code}")


def main():
    print("Trust Gap FAQ Deployment")
    print("Posts: PB ID=631, JDS ID=1122")
    print()

    # Verify credentials work
    r_test = requests.get(f'{PB_BASE}/posts/631?context=edit', headers=PB_HEADERS, timeout=20)
    if r_test.status_code != 200:
        print(f"ERROR: Cannot reach purebrain.ai API ({r_test.status_code})")
        sys.exit(1)

    results = {}

    # Deploy to purebrain.ai
    results['purebrain.ai'] = deploy_faq('purebrain.ai', PB_BASE, PB_HEADERS, 631)

    # Deploy to jareddsanborn.com
    results['jareddsanborn.com'] = deploy_faq('jareddsanborn.com', JDS_BASE, JDS_HEADERS, 1122)

    # Clear Elementor cache on PB
    print("\nClearing Elementor cache on purebrain.ai...")
    clear_elementor_cache()

    # Summary
    print("\n" + "="*60)
    print("DEPLOYMENT SUMMARY")
    print("="*60)
    all_ok = True
    for site, ok in results.items():
        status = "SUCCESS" if ok else "FAILED"
        print(f"  {site}: {status}")
        if not ok:
            all_ok = False

    if all_ok:
        print("\nAll deployments successful.")
        sys.exit(0)
    else:
        print("\nOne or more deployments FAILED.")
        sys.exit(1)


if __name__ == '__main__':
    main()
