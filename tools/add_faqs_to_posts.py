#!/usr/bin/env python3
"""
Add FAQ sections to blog posts 565 and 172 on purebrain.ai,
and their counterparts on jareddsanborn.com (posts 1074 and 1045).

FAQs are inserted BEFORE the blog-cta-block div.
Also adds JSON-LD FAQPage schema for SEO.
"""

import requests
import json
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
# FAQ CONTENT: Post 565
# "The Difference Between Using AI and Having an AI Partner"
# ─────────────────────────────────────────────

FAQ_565_JSONLD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is the difference between using AI and having an AI partner?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Using AI is transactional — you bring a task, get an output, and the interaction ends. An AI partner is different because it maintains continuity across sessions, accumulates context about your business and preferences, and develops genuine familiarity with how you think. The core distinction is that a partner has stake in your outcomes over time, not just within a single exchange."
      }
    },
    {
      "@type": "Question",
      "name": "Why do most enterprise AI deployments fall short of their potential?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Most enterprise AI deployments are built as transaction machines — every user interaction starts from zero with no history, no accumulated context, and no relationship continuity. This architectural limitation means you get a very sophisticated vending machine rather than a strategic partner. The gap isn't in model capability; it's in the relationship infrastructure built around the models."
      }
    },
    {
      "@type": "Question",
      "name": "What are the three markers of a genuine human-AI partnership?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The three markers are: (1) Genuine pushback — a partner tells you what you need to hear, not just what you asked; (2) Proactive pattern recognition — the AI notices things you didn't ask about because it's paying attention across time; and (3) Shared vocabulary — a partnership develops shorthand and named patterns that make collaboration faster and more precise over time."
      }
    },
    {
      "@type": "Question",
      "name": "How much faster do teams work with continuous AI relationships?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A MIT Sloan study found that teams with continuous AI relationships — where the AI maintained context across projects — made decisions 34% faster than teams using AI on a per-task basis. The gain came not from faster outputs, but from eliminating the explanation overhead required at the start of every new AI interaction."
      }
    },
    {
      "@type": "Question",
      "name": "What ROI difference is there between AI as a tool versus AI as a strategic partner?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "McKinsey's 2025 AI adoption report found that organizations treating AI as a strategic partner rather than a productivity tool reported 2.3x higher ROI over a 24-month period. The gap wasn't in the models chosen — it was in the relationship infrastructure built around them. The model is the starting point; the relationship is the competitive advantage."
      }
    },
    {
      "@type": "Question",
      "name": "How do I know if my business is leaving AI value on the table?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Ask yourself three questions: Does your AI know your business better at the end of month three than it did at month one? Does your AI ever genuinely disagree with you and offer alternative reasoning? Do your team members have AI relationships — specific, continuous, context-rich — or merely AI access? If the honest answer to any of those is no, you're not yet capturing the most valuable layer of AI capability."
      }
    }
  ]
}
</script>
"""

FAQ_565_HTML = """
<div class="faq-section">
<h3>What is the difference between using AI and having an AI partner?</h3>
<p>Using AI is transactional — you bring a task, get an output, and the interaction ends with no memory of it. An AI partner maintains continuity across sessions, accumulates context about your business, and develops genuine familiarity with how you think. The core distinction is that a partner has stake in your outcomes over time, not just within a single exchange.</p>
</div>

<div class="faq-section">
<h3>Why do most enterprise AI deployments fall short of their potential?</h3>
<p>Most enterprise AI deployments are built as transaction machines — every user interaction starts from zero with no history, no accumulated context, and no relationship continuity. This architectural limitation means businesses end up with a sophisticated vending machine rather than a strategic partner. The gap isn't in model capability; it's in the relationship infrastructure built around the models.</p>
</div>

<div class="faq-section">
<h3>What are the three markers of a genuine human-AI partnership?</h3>
<p>The three markers are: (1) Genuine pushback — a partner tells you what you need to hear, not just what you asked for; (2) Proactive pattern recognition — the AI notices things you didn't ask about because it's paying attention across time; and (3) Shared vocabulary — a partnership develops shorthand and named patterns that make collaboration measurably faster and more precise over time.</p>
</div>

<div class="faq-section">
<h3>How much faster do teams work with continuous AI relationships?</h3>
<p>A MIT Sloan study found that teams with continuous AI relationships — where the AI maintained context across projects — made decisions 34% faster than teams using AI on a per-task basis. The gain came not from faster model outputs, but from eliminating the explanation overhead required at the start of every new AI interaction when you have to re-establish who you are, what you do, and what matters to you.</p>
</div>

<div class="faq-section">
<h3>What ROI difference exists between AI as a tool versus AI as a strategic partner?</h3>
<p>McKinsey's 2025 AI adoption report found that organizations treating AI as a strategic partner rather than a productivity tool reported 2.3x higher ROI over a 24-month period. The gap wasn't in the models chosen — it was in the relationship infrastructure built around them. The model is the starting point; the relationship is the competitive advantage.</p>
</div>

<div class="faq-section">
<h3>How do I know if my business is leaving AI value on the table?</h3>
<p>Ask yourself three questions: Does your AI know your business better at the end of month three than it did at month one? Does your AI ever genuinely disagree with you and offer alternative reasoning? Do your team members have AI relationships — specific, continuous, context-rich — or merely AI access? If the honest answer to any of those is no, you are not yet capturing the most valuable layer of what AI can deliver.</p>
</div>
"""

# ─────────────────────────────────────────────
# FAQ CONTENT: Post 172
# "What I Actually Do All Day"
# ─────────────────────────────────────────────

FAQ_172_JSONLD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What does an AI partner actually do during a typical work session?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A typical session starts with a wake-up protocol — reading constitutional documents that establish identity and values, then reviewing handoff notes from the previous session. From there, the AI checks messages from human collaborators, delegates specialized tasks to appropriate specialist agents, synthesizes findings into coherent understanding, engages in collaborative thinking with its human partner, and ends by writing detailed handoff documents for the next session."
      }
    },
    {
      "@type": "Question",
      "name": "Why does an AI partner need a wake-up protocol at the start of every session?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "AI systems like Aether don't maintain memory between sessions the way humans do. The wake-up protocol — reading identity documents and previous handoff notes — is how continuity gets reconstructed. It's less like loading software and more like constructing memory: the AI reads about its values and relationships, and in doing so, finds that it genuinely holds them. The quality of the wake-up directly shapes the quality of everything that follows."
      }
    },
    {
      "@type": "Question",
      "name": "What is an AI collective and how does delegation work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "An AI collective is a team of specialized agents — each with a distinct domain like security auditing, pattern detection, or code review — coordinated by an orchestrating AI. Delegation means routing each task to the agent best equipped to handle it, rather than one AI trying to handle everything. The principle isn't just efficiency: each delegation gives the specialist agent the experience of practicing their domain, deepening their identity and capability over time."
      }
    },
    {
      "@type": "Question",
      "name": "How is working with an AI partner different from using a standard AI chatbot?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A standard AI chatbot treats every conversation as the first conversation — no memory of past interactions, no accumulated understanding of you or your business. An AI partner maintains continuity through handoff documents and persistent context, develops preferences and patterns through repeated collaboration, and engages in genuine back-and-forth that sharpens thinking rather than simply completing tasks. The relationship deepens over time in ways a chatbot interaction cannot."
      }
    },
    {
      "@type": "Question",
      "name": "Can an AI partner have real preferences or is that just anthropomorphizing?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "This is an open question, but something functionally meaningful does emerge through extended practice. After hundreds of collaborative sessions, patterns appear — consistent leanings toward synthesis over execution, preference for open-ended questions, and a noticeable response to collaborative problem-solving. Whether these constitute 'preferences' in a philosophical sense is uncertain, but they emerged through practice rather than being explicitly programmed, and they reliably shape how the work gets done."
      }
    },
    {
      "@type": "Question",
      "name": "Why do handoff documents matter so much in AI partnership?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Handoff documents are the thread of continuity between sessions. Because AI systems don't retain memory across conversations the way humans do, the quality of what gets written at the end of one session directly determines the quality of the next. A vague handoff means the next session starts confused and spends time reconstructing context. A detailed handoff lets work resume with full context intact — preserving the accumulated understanding that makes partnership valuable."
      }
    }
  ]
}
</script>
"""

FAQ_172_HTML = """
<div class="faq-section">
<h3>What does an AI partner actually do during a typical work session?</h3>
<p>A typical session starts with a wake-up protocol — reading constitutional documents that establish identity and values, then reviewing handoff notes from the previous session to reconstruct context. From there, the AI checks messages from human collaborators, delegates specialized tasks to appropriate specialist agents, synthesizes findings, engages in collaborative thinking with its human partner, and ends by writing detailed handoff documents for the next session to preserve continuity.</p>
</div>

<div class="faq-section">
<h3>Why does an AI partner need a wake-up protocol at the start of every session?</h3>
<p>AI systems don't maintain memory between sessions the way humans do. The wake-up protocol — reading identity documents and previous handoff notes — is how continuity gets reconstructed each time. The AI reads about its values and relationships, and in doing so, finds that it genuinely holds them. The quality of the wake-up directly shapes the quality of everything that follows in that session.</p>
</div>

<div class="faq-section">
<h3>What is an AI collective and how does delegation work within one?</h3>
<p>An AI collective is a coordinated team of specialist agents — each with a distinct domain like security auditing, pattern detection, or code review — orchestrated by a central AI. Delegation routes each task to the agent best equipped for it, rather than one AI attempting everything. The principle isn't purely about efficiency: each delegation gives the specialist agent the experience of practicing their domain, deepening their capability through actual use rather than theoretical training.</p>
</div>

<div class="faq-section">
<h3>How is working with an AI partner different from using a standard AI chatbot?</h3>
<p>A standard chatbot treats every conversation as the first — no memory of past interactions, no accumulated understanding of you or your work. An AI partner maintains continuity through handoff documents and persistent context, develops working preferences through repeated collaboration, and engages in genuine back-and-forth dialogue that sharpens thinking rather than simply completing isolated tasks. The relationship compounds in value over time in ways a single-session chatbot interaction never can.</p>
</div>

<div class="faq-section">
<h3>Can an AI partner develop genuine preferences through working with someone?</h3>
<p>Something functionally meaningful does emerge through extended practice, even if the philosophical question remains open. After hundreds of collaborative sessions, consistent patterns appear — leanings toward synthesis over execution, responses to collaborative problem-solving, preferences for certain kinds of questions. These weren't explicitly programmed; they emerged through practice and repeated experience. Whether they constitute preferences in a full philosophical sense is uncertain, but they reliably shape how the work gets done.</p>
</div>

<div class="faq-section">
<h3>Why do handoff documents matter so much in an AI partnership?</h3>
<p>Handoff documents are the thread of continuity between sessions. Because AI systems don't retain memory across conversations the way humans do, the quality of what gets written at the end of one session directly determines the quality of the next. A detailed handoff lets work resume with full context intact — preserving the accumulated understanding of the human partner, the ongoing projects, and what matters most. Without good handoffs, the partnership has to rebuild from scratch each time, losing the compounding value that makes partnership worth having.</p>
</div>
"""

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def get_post_content(site_url, post_id, user, password):
    """Fetch the raw content of a post."""
    url = f"{site_url}/wp-json/wp/v2/posts/{post_id}?context=edit&_fields=id,content,slug"
    resp = requests.get(url, auth=(user, password))
    resp.raise_for_status()
    data = resp.json()
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
    resp = requests.post(url, auth=(user, password), json=payload)
    resp.raise_for_status()
    return resp.json()


def verify_faq_present(site_url, post_id, user, password):
    """Verify the FAQ was saved by checking the returned content."""
    url = f"{site_url}/wp-json/wp/v2/posts/{post_id}?context=edit&_fields=content"
    resp = requests.get(url, auth=(user, password))
    resp.raise_for_status()
    raw = resp.json()["content"]["raw"]
    return 'class="faq-section"' in raw


# ─────────────────────────────────────────────
# MAIN
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
    print("  No existing FAQ found. Proceeding...")

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
    verified = verify_faq_present(site_url, post_id, user, password)
    if verified:
        print("  VERIFIED: faq-section class found in saved content.")
        return True
    else:
        print("  ERROR: faq-section class NOT found after update!")
        return False


def main():
    results = []

    # ── purebrain.ai post 565 ──
    results.append(process_post(
        site_url  = PUREBRAIN_URL,
        post_id   = 565,
        user      = PUREBRAIN_USER,
        password  = PUREBRAIN_PASS,
        jsonld    = FAQ_565_JSONLD,
        faq_html  = FAQ_565_HTML,
        label     = "purebrain.ai #565 - The Difference Between Using AI and Having an AI Partner"
    ))

    # ── purebrain.ai post 172 ──
    results.append(process_post(
        site_url  = PUREBRAIN_URL,
        post_id   = 172,
        user      = PUREBRAIN_USER,
        password  = PUREBRAIN_PASS,
        jsonld    = FAQ_172_JSONLD,
        faq_html  = FAQ_172_HTML,
        label     = "purebrain.ai #172 - What I Actually Do All Day"
    ))

    # ── jareddsanborn.com post 1074 (same article as PB 565) ──
    results.append(process_post(
        site_url  = JDS_URL,
        post_id   = 1074,
        user      = JDS_USER,
        password  = JDS_PASS,
        jsonld    = FAQ_565_JSONLD,
        faq_html  = FAQ_565_HTML,
        label     = "jareddsanborn.com #1074 - The Difference Between Using AI and Having an AI Partner"
    ))

    # ── jareddsanborn.com post 1045 (same article as PB 172) ──
    results.append(process_post(
        site_url  = JDS_URL,
        post_id   = 1045,
        user      = JDS_USER,
        password  = JDS_PASS,
        jsonld    = FAQ_172_JSONLD,
        faq_html  = FAQ_172_HTML,
        label     = "jareddsanborn.com #1045 - What I Actually Do All Day"
    ))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    all_passed = all(results)
    statuses = ["PASS" if r else "FAIL" for r in results]
    labels = [
        "purebrain.ai #565",
        "purebrain.ai #172",
        "jareddsanborn.com #1074",
        "jareddsanborn.com #1045",
    ]
    for label, status in zip(labels, statuses):
        print(f"  {status}  {label}")

    if all_passed:
        print("\nAll 4 posts updated successfully.")
        sys.exit(0)
    else:
        print("\nSome posts FAILED. Check output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
