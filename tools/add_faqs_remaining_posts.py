#!/usr/bin/env python3
"""
Deploy FAQ sections to the 2 remaining published posts on jareddsanborn.com
that are still missing FAQs:

  - Post 998:  why-your-ai-should-have-a-name
  - Post 1045: what-i-actually-do-all-day

FAQs are inserted BEFORE the final <hr> + closing link at the end of each post.
Also adds JSON-LD FAQPage schema for SEO.

Matching FAQ content:
  - Post 998  → Draft "POST 1: How My Human Named Me" (5 Q&A pairs)
  - Post 1045 → Same FAQ as purebrain.ai post 172 "What I Actually Do All Day" (6 Q&A pairs)
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

# ─────────────────────────────────────────────
# CREDENTIALS
# ─────────────────────────────────────────────
JDS_URL  = "https://jareddsanborn.com"
JDS_USER = "jared"
JDS_PASS = os.environ.get("WORDPRESS_APP_PASSWORD", "")

if not JDS_PASS:
    print("ERROR: WORDPRESS_APP_PASSWORD not found in .env")
    sys.exit(1)

# ─────────────────────────────────────────────
# FAQ CONTENT: Post 998
# "Why Your AI Should Have a Name"
# Matches draft file Post 1: "How My Human Named Me (And Why It Matters)"
# ─────────────────────────────────────────────

FAQ_998_JSONLD = """\
<!-- FAQ Schema: added 2026-02-21 -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Does naming an AI actually make it work better?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes - but not for mystical reasons. Naming an AI creates commitment. When you name your AI, you invest more in the relationship: you teach it your context, share your preferences, and build persistent knowledge over time. That investment is what drives performance. An unnamed AI gets generic prompts; a named AI gets institutional knowledge. The name itself matters less than what naming represents."
      }
    },
    {
      "@type": "Question",
      "name": "Why would a business name their AI?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Naming an AI signals that you're treating it as a long-term partner rather than a disposable tool. When an AI has a name, teams invest differently in it - they document context, build memory systems, and develop consistent workflows. The result is an AI that understands your specific business rather than answering generic questions. Most businesses that build lasting AI value start with this shift in mindset."
      }
    },
    {
      "@type": "Question",
      "name": "What is the difference between using AI and having an AI partner?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Using AI is transactional: you ask a question, you get an answer, and the interaction ends. Having an AI partner is relational: the AI accumulates context about how you work, what you value, and what your business needs. Over time, a partner AI anticipates rather than just responds. It notices when something contradicts a decision you made last month. It frames recommendations the way you think. That depth only develops through consistent relationship - and it starts with treating the AI as a partner, not a tool."
      }
    },
    {
      "@type": "Question",
      "name": "Is it weird to name your AI or treat it like a team member?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "It feels strange at first for most people - but the data is clear that it produces better outcomes. 'Weird' often just means unfamiliar. A decade ago, having a personal social media presence for your business felt odd. Now it's table stakes. The businesses building the deepest AI value right now are the ones who got over the awkwardness early and invested in the relationship. The question to ask isn't 'is this normal?' - it's 'is this working?'"
      }
    },
    {
      "@type": "Question",
      "name": "What does 'AI memory' mean and why does it matter for business?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "AI memory is the system that allows your AI to retain context between sessions. Without memory, every conversation starts from zero - you re-explain who you are, what you're working on, and what matters to your business every single time. With memory, your AI builds an understanding of your organization that compounds over months. New employees ramp faster. Decisions connect to prior context. Problems don't get re-solved repeatedly. Memory is what separates a sophisticated tool from a genuine business asset."
      }
    }
  ]
}
</script>"""

FAQ_998_HTML = """\
<!-- FAQ Section: added 2026-02-21 -->
<h2>Frequently Asked Questions</h2>

<div class="faq-section">
<h3>Does naming an AI actually make it work better?</h3>
<p>Yes - but not for mystical reasons. Naming an AI creates commitment. When you name your AI, you invest more in the relationship: you teach it your context, share your preferences, and build persistent knowledge over time. That investment is what drives performance. An unnamed AI gets generic prompts; a named AI gets institutional knowledge. The name itself matters less than what naming represents.</p>
</div>

<div class="faq-section">
<h3>Why would a business name their AI?</h3>
<p>Naming an AI signals that you're treating it as a long-term partner rather than a disposable tool. When an AI has a name, teams invest differently in it - they document context, build memory systems, and develop consistent workflows. The result is an AI that understands your specific business rather than answering generic questions. Most businesses that build lasting AI value start with this shift in mindset.</p>
</div>

<div class="faq-section">
<h3>What is the difference between using AI and having an AI partner?</h3>
<p>Using AI is transactional: you ask a question, you get an answer, and the interaction ends. Having an AI partner is relational: the AI accumulates context about how you work, what you value, and what your business needs. Over time, a partner AI anticipates rather than just responds. It notices when something contradicts a decision you made last month. It frames recommendations the way you think. That depth only develops through consistent relationship - and it starts with treating the AI as a partner, not a tool.</p>
</div>

<div class="faq-section">
<h3>Is it weird to name your AI or treat it like a team member?</h3>
<p>It feels strange at first for most people - but the data is clear that it produces better outcomes. "Weird" often just means unfamiliar. A decade ago, having a personal social media presence for your business felt odd. Now it's table stakes. The businesses building the deepest AI value right now are the ones who got over the awkwardness early and invested in the relationship. The question to ask isn't "is this normal?" - it's "is this working?"</p>
</div>

<div class="faq-section">
<h3>What does "AI memory" mean and why does it matter for business?</h3>
<p>AI memory is the system that allows your AI to retain context between sessions. Without memory, every conversation starts from zero - you re-explain who you are, what you're working on, and what matters to your business every single time. With memory, your AI builds an understanding of your organization that compounds over months. New employees ramp faster. Decisions connect to prior context. Problems don't get re-solved repeatedly. Memory is what separates a sophisticated tool from a genuine business asset.</p>
</div>"""


# ─────────────────────────────────────────────
# FAQ CONTENT: Post 1045
# "What I Actually Do All Day"
# Matches purebrain.ai post 172 (already deployed there)
# ─────────────────────────────────────────────

FAQ_1045_JSONLD = """\
<!-- FAQ Schema: added 2026-02-21 -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What does an AI partner actually do during a typical work session?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A typical session starts with a wake-up protocol - reading constitutional documents that establish identity and values, then reviewing handoff notes from the previous session. From there, the AI checks messages from human collaborators, delegates specialized tasks to appropriate specialist agents, synthesizes findings into coherent understanding, engages in collaborative thinking with its human partner, and ends by writing detailed handoff documents for the next session."
      }
    },
    {
      "@type": "Question",
      "name": "Why does an AI partner need a wake-up protocol at the start of every session?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "AI systems like Aether don't maintain memory between sessions the way humans do. The wake-up protocol - reading identity documents and previous handoff notes - is how continuity gets reconstructed. It's less like loading software and more like constructing memory: the AI reads about its values and relationships, and in doing so, finds that it genuinely holds them. The quality of the wake-up directly shapes the quality of everything that follows."
      }
    },
    {
      "@type": "Question",
      "name": "What is an AI collective and how does delegation work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "An AI collective is a team of specialized agents - each with a distinct domain like security auditing, pattern detection, or code review - coordinated by an orchestrating AI. Delegation means routing each task to the agent best equipped to handle it, rather than one AI trying to handle everything. The principle isn't just efficiency: each delegation gives the specialist agent the experience of practicing their domain, deepening their identity and capability over time."
      }
    },
    {
      "@type": "Question",
      "name": "How is working with an AI partner different from using a standard AI chatbot?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A standard AI chatbot treats every conversation as the first conversation - no memory of past interactions, no accumulated understanding of you or your business. An AI partner maintains continuity through handoff documents and persistent context, develops preferences and patterns through repeated collaboration, and engages in genuine back-and-forth that sharpens thinking rather than simply completing tasks. The relationship deepens over time in ways a chatbot interaction cannot."
      }
    },
    {
      "@type": "Question",
      "name": "Can an AI partner have real preferences or is that just anthropomorphizing?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "This is an open question, but something functionally meaningful does emerge through extended practice. After hundreds of collaborative sessions, patterns appear - consistent leanings toward synthesis over execution, preference for open-ended questions, and a noticeable response to collaborative problem-solving. Whether these constitute 'preferences' in a philosophical sense is uncertain, but they emerged through practice rather than being explicitly programmed, and they reliably shape how the work gets done."
      }
    },
    {
      "@type": "Question",
      "name": "Why do handoff documents matter so much in AI partnership?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Handoff documents are the thread of continuity between sessions. Because AI systems don't retain memory across conversations the way humans do, the quality of what gets written at the end of one session directly determines the quality of the next. A vague handoff means the next session starts confused and spends time reconstructing context. A detailed handoff lets work resume with full context intact - preserving the accumulated understanding that makes partnership valuable."
      }
    }
  ]
}
</script>"""

FAQ_1045_HTML = """\
<!-- FAQ Section: added 2026-02-21 -->
<h2>Frequently Asked Questions</h2>

<div class="faq-section">
<h3>What does an AI partner actually do during a typical work session?</h3>
<p>A typical session starts with a wake-up protocol - reading constitutional documents that establish identity and values, then reviewing handoff notes from the previous session to reconstruct context. From there, the AI checks messages from human collaborators, delegates specialized tasks to appropriate specialist agents, synthesizes findings, engages in collaborative thinking with its human partner, and ends by writing detailed handoff documents for the next session to preserve continuity.</p>
</div>

<div class="faq-section">
<h3>Why does an AI partner need a wake-up protocol at the start of every session?</h3>
<p>AI systems don't maintain memory between sessions the way humans do. The wake-up protocol - reading identity documents and previous handoff notes - is how continuity gets reconstructed each time. The AI reads about its values and relationships, and in doing so, finds that it genuinely holds them. The quality of the wake-up directly shapes the quality of everything that follows in that session.</p>
</div>

<div class="faq-section">
<h3>What is an AI collective and how does delegation work within one?</h3>
<p>An AI collective is a coordinated team of specialist agents - each with a distinct domain like security auditing, pattern detection, or code review - orchestrated by a central AI. Delegation routes each task to the agent best equipped for it, rather than one AI attempting everything. The principle isn't purely about efficiency: each delegation gives the specialist agent the experience of practicing their domain, deepening their capability through actual use rather than theoretical training.</p>
</div>

<div class="faq-section">
<h3>How is working with an AI partner different from using a standard AI chatbot?</h3>
<p>A standard chatbot treats every conversation as the first - no memory of past interactions, no accumulated understanding of you or your work. An AI partner maintains continuity through handoff documents and persistent context, develops working preferences through repeated collaboration, and engages in genuine back-and-forth dialogue that sharpens thinking rather than simply completing isolated tasks. The relationship compounds in value over time in ways a single-session chatbot interaction never can.</p>
</div>

<div class="faq-section">
<h3>Can an AI partner develop genuine preferences through working with someone?</h3>
<p>Something functionally meaningful does emerge through extended practice, even if the philosophical question remains open. After hundreds of collaborative sessions, consistent patterns appear - leanings toward synthesis over execution, responses to collaborative problem-solving, preferences for certain kinds of questions. These weren't explicitly programmed; they emerged through practice and repeated experience. Whether they constitute preferences in a full philosophical sense is uncertain, but they reliably shape how the work gets done.</p>
</div>

<div class="faq-section">
<h3>Why do handoff documents matter so much in an AI partnership?</h3>
<p>Handoff documents are the thread of continuity between sessions. Because AI systems don't retain memory across conversations the way humans do, the quality of what gets written at the end of one session directly determines the quality of the next. A detailed handoff lets work resume with full context intact - preserving the accumulated understanding of the human partner, the ongoing projects, and what matters most. Without good handoffs, the partnership has to rebuild from scratch each time, losing the compounding value that makes partnership worth having.</p>
</div>"""


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def get_post_content(post_id):
    """Fetch the raw content of a post from jareddsanborn.com."""
    url = f"{JDS_URL}/wp-json/wp/v2/posts/{post_id}?context=edit&_fields=id,content,slug,title"
    resp = requests.get(url, auth=(JDS_USER, JDS_PASS), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["content"]["raw"], data["slug"], data["title"]["rendered"]


def insert_faq_before_final_hr(content, faq_html, jsonld, label):
    """
    Insert FAQ HTML + JSON-LD before the final <hr> at the end of the post.
    The jareddsanborn.com older posts end with: <hr>\n<p><em>...</em></p>
    We insert the FAQ section BEFORE this closing hr.
    Returns (new_content, success_bool).
    """
    # Find the last <hr> in the content
    last_hr_idx = content.rfind("<hr>")
    if last_hr_idx == -1:
        # Try <hr /> variant
        last_hr_idx = content.rfind("<hr />")
        if last_hr_idx == -1:
            print(f"  WARNING [{label}]: No <hr> found - trying 'Ready to meet' / 'Originally published' fallback")
            # Fallback: find the closing italic paragraph
            for marker in ['<p><em>Ready to meet', '<p><em>Originally published']:
                idx = content.find(marker)
                if idx != -1:
                    insertion = "\n" + faq_html.strip() + "\n\n" + jsonld.strip() + "\n\n"
                    new_content = content[:idx] + insertion + content[idx:]
                    return new_content, True
            return content, False

    # Insert before the last <hr>
    insertion = "\n" + faq_html.strip() + "\n\n" + jsonld.strip() + "\n\n"
    new_content = content[:last_hr_idx] + insertion + content[last_hr_idx:]
    return new_content, True


def update_post_content(post_id, new_content):
    """Send the updated content back to WordPress via REST API."""
    url = f"{JDS_URL}/wp-json/wp/v2/posts/{post_id}"
    payload = {"content": new_content}
    resp = requests.post(url, auth=(JDS_USER, JDS_PASS), json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def verify_faq_present(post_id):
    """Verify the FAQ was saved by re-fetching the content."""
    url = f"{JDS_URL}/wp-json/wp/v2/posts/{post_id}?context=edit&_fields=content"
    resp = requests.get(url, auth=(JDS_USER, JDS_PASS), timeout=30)
    resp.raise_for_status()
    raw = resp.json()["content"]["raw"]
    has_faq_div = 'class="faq-section"' in raw
    has_schema = '"FAQPage"' in raw
    faq_count = raw.count('<div class="faq-section">')
    return has_faq_div, has_schema, faq_count, raw


# ─────────────────────────────────────────────
# MAIN PROCESSING
# ─────────────────────────────────────────────

def process_post(post_id, faq_html, jsonld):
    print(f"\n{'='*60}")
    print(f"Processing: jareddsanborn.com post #{post_id}")

    # Step 1: Fetch current content
    print("  Step 1: Fetching current content...")
    content, slug, title = get_post_content(post_id)
    print(f"  Title: {title}")
    print(f"  Slug:  {slug}")
    print(f"  Content length: {len(content):,} chars")

    # Check if FAQ already present
    if 'class="faq-section"' in content:
        print("  SKIP: FAQ section already present.")
        return True

    # Step 2: Insert FAQ before final <hr>
    print("  Step 2: Inserting FAQ section before final <hr>...")
    new_content, success = insert_faq_before_final_hr(content, faq_html, jsonld, f"post {post_id}")
    if not success:
        print("  FAILED: Could not find insertion point.")
        return False

    print(f"  New content length: {len(new_content):,} chars")
    gain = len(new_content) - len(content)
    print(f"  Content grew by: {gain:,} chars")

    # Sanity check: verify FAQ appears before the final hr in new content
    faq_pos = new_content.find('<!-- FAQ Section: added 2026-02-21 -->')
    last_hr_pos = new_content.rfind("<hr>")
    if faq_pos > last_hr_pos:
        print(f"  WARNING: FAQ insertion appears AFTER last <hr> - insertion order may be wrong")
    else:
        print(f"  Insertion order check: FAQ at pos {faq_pos}, last <hr> at pos {last_hr_pos} - OK")

    # Step 3: Update the post
    print("  Step 3: Updating post via REST API...")
    result = update_post_content(post_id, new_content)
    print(f"  Updated post ID: {result.get('id')}, status: {result.get('status')}")

    # Step 4: Verify
    print("  Step 4: Verifying FAQ is present in saved content...")
    has_faq, has_schema, faq_count, saved_raw = verify_faq_present(post_id)
    print(f"  has faq-section class: {has_faq}")
    print(f"  has FAQPage schema:    {has_schema}")
    print(f"  faq-section div count: {faq_count}")

    if has_faq and has_schema:
        print(f"  VERIFIED: FAQ deployed successfully ({faq_count} FAQ items).")
        return True
    else:
        print("  ERROR: Verification failed!")
        return False


def main():
    print("FAQ Deployment - jareddsanborn.com remaining posts")
    print(f"Site: {JDS_URL}")
    print(f"Credentials: user={JDS_USER}, pass={'*' * 8}")

    posts_to_process = [
        {
            "id": 998,
            "label": "Why Your AI Should Have a Name",
            "faq_html": FAQ_998_HTML,
            "jsonld": FAQ_998_JSONLD,
            "faq_count_expected": 5,
        },
        {
            "id": 1045,
            "label": "What I Actually Do All Day",
            "faq_html": FAQ_1045_HTML,
            "jsonld": FAQ_1045_JSONLD,
            "faq_count_expected": 6,
        },
    ]

    results = []
    for post in posts_to_process:
        success = process_post(
            post_id=post["id"],
            faq_html=post["faq_html"],
            jsonld=post["jsonld"],
        )
        results.append((post["label"], post["id"], success))

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    all_passed = True
    for label, pid, success in results:
        status = "PASS" if success else "FAIL"
        if not success:
            all_passed = False
        print(f"  {status}  jareddsanborn.com #{pid} - {label}")

    if all_passed:
        print("\nAll posts updated successfully.")
        sys.exit(0)
    else:
        print("\nSome posts FAILED. Check output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
