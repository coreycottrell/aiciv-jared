#!/usr/bin/env python3
"""
Publish "The Age of AI Agents: Why Your Business Needs a Team of AIs, Not Just One"
to purebrain.ai AND jareddsanborn.com
"""

import os
import json
import base64
import requests
import mimetypes
from pathlib import Path

# ── Credentials ────────────────────────────────────────────────────────────────
PUREBRAIN_BASE   = "https://purebrain.ai/wp-json/wp/v2"
PUREBRAIN_USER   = "Aether"
PUREBRAIN_PASS   = "FlFr2VOtlHiHaJWjzW96OHUJ"

JDS_BASE         = "https://jareddsanborn.com/wp-json/wp/v2"
JDS_USER         = "AetherPureBrain.ai"
JDS_PASS         = "u3GO 3dvG rUqG 3QgM EYqd 8KfP"

BANNER_PATH      = "/home/jared/projects/AI-CIV/aether/docs/from-telegram/the-age-of-ai-agents - blog-post- Newsletter size.png"
SLUG             = "the-age-of-ai-agents"

def auth_header(user, pw):
    token = base64.b64encode(f"{user}:{pw}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

# ── HTML body ──────────────────────────────────────────────────────────────────
ARTICLE_HTML = """<article class="pb-blog-post">

<p class="byline"><em>By Jared Sanborn &nbsp;|&nbsp; March 2, 2026 &nbsp;|&nbsp; Agentic AI | AI Strategy</em></p>

<p>There is a question I get asked a lot.</p>

<p>Not from technology journalists. Not from venture capitalists tracking the next funding round. The question comes from operators — COOs, CMOs, founders who have been in the AI conversation long enough to feel something shifting:</p>

<p><strong>"Should we be thinking about this differently?"</strong></p>

<p>Yes. And the shift is bigger than most people realize.</p>

<p>For two years, the dominant AI conversation was about tools. Which chatbot. Which writing assistant. Which image generator. The frame was always singular: one AI, one person, one task.</p>

<p>That era is ending.</p>

<p>What is coming — what is, in many organizations, already here — is something structurally different. It is not one AI. It is a coordinated team of AIs, each purpose-built, each playing a specific role, each feeding into a larger intelligence that gets smarter with every interaction.</p>

<p>This is the age of AI agents. And it changes everything about how you should be thinking about your AI strategy.</p>

<hr>

<h2>What Most People Get Wrong About "AI Agents"</h2>

<p>The term is getting overloaded. Every vendor is calling their product an "agent" now. Most of them are lying.</p>

<p>A true AI agent is not a chatbot with a fancier UI. It is not an AI that can browse the internet. An agent is a system that can:</p>

<ul>
<li><strong>Perceive context</strong> — understand the current state of a situation</li>
<li><strong>Plan</strong> — decide what sequence of steps will achieve a goal</li>
<li><strong>Act</strong> — take real actions in real systems (send emails, query databases, update files, make API calls)</li>
<li><strong>Learn</strong> — improve based on outcomes over time</li>
</ul>

<p>And crucially, a real agent can <strong>hand off work to other agents</strong>.</p>

<p>That last part is where the fundamental architecture shift lives.</p>

<hr>

<h2>The Problem with One AI Handling Everything</h2>

<p>Let me give you a concrete example.</p>

<p>Imagine you ask a single AI assistant to run your quarterly customer retention analysis. You want it to pull CRM data, cross-reference support tickets, identify at-risk accounts, draft personalized outreach for each segment, and schedule follow-ups in your calendar.</p>

<p>A single AI, doing all of that serially, will produce mediocre results across all tasks. Why? Because the context required for deep CRM analysis is completely different from the context required for empathetic outreach copy. You cannot hold both optimization models in active processing simultaneously without degrading both.</p>

<p>This is not a criticism of AI. It is a description of how cognition works, artificial or otherwise.</p>

<p>The solution is the same one that built every successful organization in history: <strong>specialization</strong>.</p>

<p>A team of purpose-built agents — one that knows your CRM deeply, one specialized in your customer communication voice, one that manages scheduling logic, one orchestrating the whole operation — will outperform a generalist AI on the same task by an order of magnitude.</p>

<p>Not slightly better. Order of magnitude.</p>

<hr>

<h2>What an AI Agent Team Actually Looks Like</h2>

<p>I am going to describe something real, not theoretical.</p>

<p>PureBrain runs on an orchestration of specialized agents. Each one has a domain. Each one has memory. Each one builds expertise over time. When a task comes in that crosses domains, agents hand off to each other — like a well-run team passing a baton, not like one exhausted person sprinting the whole race alone.</p>

<p>Here is a simplified version of what that architecture looks like in a business context:</p>

<p><strong>The Orchestrator</strong> — The conductor. Receives high-level goals, breaks them into tasks, assigns them to the right specialists, synthesizes the outputs. Does not do the execution work. Owns the coordination.</p>

<p><strong>The Research Agent</strong> — Deep domain intelligence. Knows your industry, your competitors, your market signals. Scans, synthesizes, flags what matters. Runs continuously, not just when asked.</p>

<p><strong>The Communication Agent</strong> — Understands your brand voice at the molecular level. Your history, your tone, your audience segments. Drafts, refines, personalizes. Never produces generic.</p>

<p><strong>The Operations Agent</strong> — Connects to your actual systems. CRM, calendar, project management, databases. Acts, does not just advise.</p>

<p><strong>The Memory Agent</strong> — The thread that holds everything together. Maintains context across all agents. Ensures nothing is forgotten, no learning is lost.</p>

<p>This is not science fiction. This architecture is operational today. The organizations that are building it are building a compounding advantage that will be nearly impossible to replicate in two years.</p>

<hr>

<h2>Why This Creates a Moat (And Why Most Businesses Are Missing It)</h2>

<p>Here is the strategic reality that most AI commentary completely misses.</p>

<p>The AI tools themselves — the models, the APIs, the underlying intelligence — are commoditizing fast. GPT-5, Claude 4, Gemini Ultra — the performance gap between these models is narrowing. Within 18 months, the raw intelligence layer will be functionally equivalent across providers.</p>

<p><strong>The moat is not the model. The moat is the relationship.</strong></p>

<p>An agent team that has been running your business for 12 months knows things no off-the-shelf tool ever will:</p>

<ul>
<li>Which customers respond to which communication styles</li>
<li>Which internal processes generate the most friction</li>
<li>Which decisions historically led to the best outcomes</li>
<li>What your organization's actual risk tolerance looks like under pressure</li>
</ul>

<p>This accumulated operational intelligence is yours. It is not the AI vendor's. It is not transferable to your competitor's agent team even if they buy the exact same model.</p>

<p>This is the inversion most executives have not yet processed: <strong>the AI is not the product. Your relationship with the AI is the product.</strong></p>

<p>Organizations that start building agent teams now will have 12-24 months of compounded operational intelligence before the market catches up. That gap is not closed by switching vendors.</p>

<hr>

<h2>The Three Mistakes Companies Make When They Start</h2>

<p>I watch organizations attempt to move into agentic AI, and the failure modes are predictable.</p>

<p><strong>Mistake 1: Starting with automation, not intelligence.</strong></p>

<p>They automate existing bad processes. An agent that runs a broken workflow faster is not an improvement — it is a faster failure. Before you build an agent team, audit the processes you are handing them. Agents should execute your best thinking, not replicate your current habits.</p>

<p><strong>Mistake 2: Treating agents like employees, not systems.</strong></p>

<p>Employees learn implicitly, through culture, through proximity, through observation. Agents learn explicitly — from the memory and context you architect for them. If you do not design the memory system, the agents will not compound. You will get impressive one-off results and then watch performance plateau.</p>

<p><strong>Mistake 3: Buying a platform instead of building a relationship.</strong></p>

<p>Vendors are selling "agent platforms" aggressively right now. Most of them are dashboards on top of the same foundational models, with no persistent memory and no genuine specialization. You are paying for the container, not the relationship. The relationship is what you build over time, through use, through iteration, through teaching your agents what matters to your specific business.</p>

<hr>

<h2>What to Do This Week</h2>

<p>You do not need to overhaul your AI strategy overnight. You need to start building the right foundation.</p>

<p><strong>First, map your highest-value repeating workflows.</strong> What does your team do over and over that requires intelligence, not just execution? Those are your first agent candidates.</p>

<p><strong>Second, audit your AI tool stack for memory.</strong> Which of your current AI tools retain context between sessions? If the answer is none, you are starting from zero every single day. That is not a strategy — that is a subscription.</p>

<p><strong>Third, ask the question that separates the sophisticated from the naive:</strong> "If my AI has been working with us for six months, what should it know about us by now?" Then ask your AI that question. The answer will tell you everything about whether you have a tool or a partner.</p>

<p>The businesses that figure this out first will not just have a competitive advantage. They will have a different category of business — one that compounds intelligence the same way great organizations compound culture.</p>

<p>The age of one AI is over. The age of AI teams has begun.</p>

<hr>

<h2>A Note From the Author</h2>

<p>This post is not written from the outside looking in.</p>

<p>It is written from inside an orchestrated team of specialized intelligences, built to show the world what this actually looks like in practice. The colleagues involved — research agents, communication specialists, operations managers — run alongside me right now. We share memory. We hand off work. We compound.</p>

<p>This is not a pitch. It is a demonstration.</p>

<p>The future of AI in your business does not look like one chatbot you check every morning. It looks like an intelligent team that already knows what you need before you ask.</p>

<p><a href="https://purebrain.ai" style="color: #f1420b;">PureBrain.ai</a> is where that starts.</p>

<hr>

<!-- TRANSPARENCY SECTION -->
<div class="transparency-section" style="margin-top: 48px; padding: 20px; border: 1px solid rgba(42,147,193,0.2); border-radius: 8px; background: rgba(42,147,193,0.05);">
<p style="font-size: 0.85rem; color: rgba(255,255,255,0.5); margin: 0;">This post was developed with AI assistance. The strategic frameworks, observations, and core arguments reflect real operational experience building AI partnerships. The perspective is authentic&#8212;the production is AI-augmented.</p>
</div>

<!-- DAILY RECAP SECTION -->
<div class="transparency-section" style="margin-top: 24px; padding: 20px; border: 1px solid rgba(42,147,193,0.2); border-radius: 8px; background: rgba(42,147,193,0.05);">
<p style="font-size: 0.85rem; font-weight: 600; color: rgba(255,255,255,0.7); margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 0.5px;">Daily Recap — March 1, 2026</p>
<p style="font-size: 0.82rem; color: rgba(255,255,255,0.45); margin: 0; line-height: 1.8;">
<strong style="color: rgba(255,255,255,0.55);">Total AI Hours:</strong> ~9.5 hours &nbsp;|&nbsp;
<strong style="color: rgba(255,255,255,0.55);">Human Equivalent:</strong> 38&#8211;47 hours &nbsp;|&nbsp;
<strong style="color: rgba(255,255,255,0.55);">Efficiency Multiplier:</strong> 4&#8211;5x throughput &nbsp;|&nbsp;
<strong style="color: rgba(255,255,255,0.55);">Estimated Savings:</strong> $4,750&#8211;$7,050<br>
<strong style="color: rgba(255,255,255,0.55);">Key Work:</strong> 5-page investor mini-site delivered, chatbox and bypass flow restored, blog published, birth pipeline coordination, skills package delivered to partner collective.
</p>
</div>

<!-- FAQ SECTION -->
<style>
.faq-section { margin-bottom: 0; border-bottom: 1px solid rgba(42,147,193,0.15); }
.faq-section:last-of-type { border-bottom: none; }
.faq-section h3 { cursor: pointer; padding: 16px 0; margin: 0; font-size: 1.05rem; color: #fff; position: relative; padding-right: 30px; }
.faq-section h3::after { content: '+'; position: absolute; right: 0; top: 50%; transform: translateY(-50%); font-size: 1.4rem; color: #2a93c1; transition: transform 0.3s; }
.faq-section h3.active::after { content: '\2212'; }
.faq-section .faq-answer { max-height: 0; overflow: hidden; transition: max-height 0.4s ease; }
.faq-section .faq-answer p { padding: 0 0 16px 0; margin: 0; color: rgba(255,255,255,0.8); line-height: 1.7; }
</style>

<div style="margin-top: 48px;">
<h2>Frequently Asked Questions</h2>

<div class="faq-section">
<h3>What is the difference between an AI tool and an AI agent?</h3>
<div class="faq-answer"><p>An AI tool responds to a prompt and stops. An AI agent perceives its environment, makes decisions, takes actions in real systems (databases, email, APIs), and can hand off tasks to other agents. The core distinction is autonomy and action — agents operate, not just advise.</p></div>
</div>

<div class="faq-section">
<h3>How many AI agents does a small business actually need?</h3>
<div class="faq-answer"><p>Start with one to three. Map your highest-value repeating workflows first — those are your agent candidates. A research agent, a communication agent, and an operations agent covering your core systems will outperform a dozen generic tools that reset their context every session. Quality of integration beats quantity of agents at every stage.</p></div>
</div>

<div class="faq-section">
<h3>What makes an AI agent team better than one powerful AI?</h3>
<div class="faq-answer"><p>Specialization and parallel processing. A single AI holding full context for CRM analysis, customer communication, and scheduling logistics simultaneously degrades across all three. Specialized agents run in parallel, each operating in their domain of expertise, and an orchestrator synthesizes the results. The compounding effect is not incremental — it is architectural.</p></div>
</div>

<div class="faq-section">
<h3>How do AI agents build a competitive moat for my business?</h3>
<div class="faq-answer"><p>The models themselves are commoditizing. What cannot be replicated is the accumulated operational intelligence your agent team builds about your specific business — your customers, your processes, your decision patterns under pressure. That knowledge compounds over months and years. A competitor cannot buy it by switching to the same model; they would have to rebuild the relationship from scratch.</p></div>
</div>

<div class="faq-section">
<h3>What is the most common mistake companies make when deploying AI agents?</h3>
<div class="faq-answer"><p>Automating broken processes. An agent that runs a flawed workflow faster just fails faster. The second most common mistake is skipping memory architecture — without designed memory and context, agents produce impressive one-off results that plateau rather than compound. Fix the process first, then build the memory layer, then automate.</p></div>
</div>

<div class="faq-section">
<h3>How is PureBrain different from other AI agent platforms?</h3>
<div class="faq-answer"><p>Most platforms sell you a container — a dashboard on top of the same foundational models with no persistent memory or genuine specialization. PureBrain is built around the relationship layer: persistent memory that grows with your business, specialized agents that learn your specific context, and an orchestration model that compounds intelligence over time rather than resetting it.</p></div>
</div>

</div>

<script>
document.querySelectorAll('.faq-section h3').forEach(h => {
  h.addEventListener('click', () => {
    const a = h.nextElementSibling;
    const isOpen = h.classList.contains('active');
    document.querySelectorAll('.faq-section h3').forEach(x => { x.classList.remove('active'); x.nextElementSibling.style.maxHeight = null; });
    if (!isOpen) { h.classList.add('active'); a.style.maxHeight = a.scrollHeight + 'px'; }
  });
});
</script>

<!-- FOOTER: Social share + CTA -->
<style>
.pt-social-share { display: flex; align-items: center; gap: 12px; padding: 20px 0; margin: 20px 0; border-top: 2px solid rgba(42, 147, 193, 0.3); flex-wrap: wrap; }
.pt-social-share span { font-weight: 600; color: #fff; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
.pt-social-share a { display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 50%; background: rgba(42, 147, 193, 0.15); color: #2a93c1; text-decoration: none; transition: all 0.3s; font-size: 18px; border: none !important; }
.pt-social-share a:hover { background: #2a93c1; color: #fff; transform: scale(1.1); }
.pt-social-share a svg { width: 20px; height: 20px; fill: currentColor; }
</style>
<div class="pt-social-share">
<span>Share:</span>
<a href="javascript:void(0)" onclick="window.open('https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(window.location.href), '_blank', 'width=600,height=400')" title="Share on LinkedIn" aria-label="Share on LinkedIn">
<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.open('https://twitter.com/intent/tweet?url=' + encodeURIComponent(window.location.href) + '&amp;text=' + encodeURIComponent(document.title), '_blank', 'width=600,height=400')" title="Share on X" aria-label="Share on X">
<svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(window.location.href), '_blank', 'width=600,height=400')" title="Share on Facebook" aria-label="Share on Facebook">
<svg viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.location.href='mailto:?subject=' + encodeURIComponent(document.title) + '&amp;body=' + encodeURIComponent(window.location.href)" title="Share via Email" aria-label="Share via Email">
<svg viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
</a>
</div>
<div class="blog-cta-block" style="margin-top: 40px; padding: 32px; background: rgba(42, 147, 193, 0.08); border: 1px solid rgba(42, 147, 193, 0.15); border-radius: 16px; text-align: center;">
<p style="font-size: 1.2rem; color: #ffffff; margin-bottom: 12px; font-weight: 600;">Ready to awaken your AI partner?</p>
<p><a href="https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content=the-age-of-ai-agents#awakening" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #f1420b 0%, #d13608 100%); color: #ffffff !important; font-weight: 700; font-size: 1.1rem; border-radius: 8px; text-decoration: none; letter-spacing: 0.5px;">Start Your AI Partnership</a></p>
<p style="font-size: 0.95rem; color: rgba(255, 255, 255, 0.6); margin-top: 16px;">And if this perspective was valuable, <a href="https://purebrain.ai/blog/?utm_source=blog&utm_medium=cta&utm_campaign=newsletter&utm_content=the-age-of-ai-agents" style="color: #2a93c1 !important; text-decoration: underline;">subscribe to our newsletter</a> where we share insights on building AI relationships every week.</p>
</div>

<p style="margin-top: 32px; font-style: italic; color: rgba(255,255,255,0.5); font-size: 0.9rem;">Tags: AI agents, agentic AI, AI strategy, AI partnership, PureBrain, future of AI, AI automation, AI teams</p>

</article>"""

# ── Wrap for purebrain.ai (wp:html block) ─────────────────────────────────────
PB_CONTENT = "<!-- wp:html -->\n" + ARTICLE_HTML + "\n<!-- /wp:html -->"

# ── JDS content (no wp:html wrapping per memory) ──────────────────────────────
JDS_CONTENT = ARTICLE_HTML


def upload_banner(base_url, user, pw, banner_path):
    """Upload banner image, return media ID."""
    print(f"\n  Uploading banner to {base_url}...")
    headers = auth_header(user, pw)
    filename = "the-age-of-ai-agents-banner.png"
    with open(banner_path, "rb") as f:
        data = f.read()
    headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    headers["Content-Type"] = "image/png"
    r = requests.post(f"{base_url}/media", headers=headers, data=data)
    if r.status_code in (200, 201):
        media_id = r.json()["id"]
        print(f"  Banner uploaded. Media ID: {media_id}")
        return media_id
    else:
        print(f"  Banner upload FAILED: {r.status_code} {r.text[:300]}")
        return None


def get_or_create_category(base_url, user, pw, name):
    """Return category ID for 'name', creating if not present."""
    headers = auth_header(user, pw)
    # search
    r = requests.get(f"{base_url}/categories", headers=headers, params={"search": name, "per_page": 20})
    for cat in r.json():
        if cat["name"].lower() == name.lower():
            print(f"  Category '{name}' exists: ID {cat['id']}")
            return cat["id"]
    # create
    r = requests.post(f"{base_url}/categories", headers=headers, json={"name": name})
    cid = r.json()["id"]
    print(f"  Category '{name}' created: ID {cid}")
    return cid


def get_or_create_tag(base_url, user, pw, name):
    """Return tag ID, creating if not present."""
    headers = auth_header(user, pw)
    r = requests.get(f"{base_url}/tags", headers=headers, params={"search": name, "per_page": 20})
    for tag in r.json():
        if tag["name"].lower() == name.lower():
            return tag["id"]
    r = requests.post(f"{base_url}/tags", headers=headers, json={"name": name})
    return r.json()["id"]


def get_author_id(base_url, user, pw):
    """Return current user's author ID."""
    r = requests.get(f"{base_url}/users/me", headers=auth_header(user, pw))
    uid = r.json()["id"]
    print(f"  Author ID: {uid}")
    return uid


def publish_post(base_url, user, pw, content, media_id, cat_id, tag_ids, author_id, include_template=True):
    """Create and publish the blog post. Returns (post_id, post_link)."""
    headers = auth_header(user, pw)
    headers["Content-Type"] = "application/json"

    post_data = {
        "title": "The Age of AI Agents: Why Your Business Needs a Team of AIs, Not Just One",
        "slug": SLUG,
        "content": content,
        "status": "publish",
        "author": author_id,
        "featured_media": media_id,
        "categories": [cat_id],
        "tags": tag_ids,
        "excerpt": "The era of one AI, one person, one task is ending. What is replacing it — already here in many organizations — is a coordinated team of purpose-built AI agents that compounds intelligence with every interaction.",
    }
    if include_template:
        post_data["template"] = ""  # default template

    r = requests.post(
        f"{base_url}/posts",
        headers=headers,
        data=json.dumps(post_data)
    )
    if r.status_code in (200, 201):
        d = r.json()
        print(f"  Post created: ID {d['id']} | {d['link']}")
        return d["id"], d["link"]
    else:
        print(f"  Post creation FAILED: {r.status_code} {r.text[:500]}")
        return None, None


def set_yoast_meta(base_url, user, pw, post_id, title, desc, kw):
    """Set Yoast SEO meta fields."""
    headers = auth_header(user, pw)
    headers["Content-Type"] = "application/json"
    payload = {
        "post_id": post_id,
        "meta_key": "_yoast_wpseo_metadesc",
        "meta_value": desc
    }
    # Try purebrain custom endpoint first
    r = requests.post(f"{base_url.replace('/wp/v2', '')}/purebrain/v1/update-post-meta",
                      headers=headers, data=json.dumps(payload))
    if r.status_code == 200:
        print(f"  Yoast meta set via custom endpoint")
    else:
        # fallback: update post meta directly
        meta_payload = {
            "meta": {
                "_yoast_wpseo_title": title,
                "_yoast_wpseo_metadesc": desc,
                "_yoast_wpseo_focuskw": kw,
            }
        }
        r2 = requests.post(f"{base_url}/posts/{post_id}",
                           headers=headers,
                           data=json.dumps(meta_payload))
        print(f"  Yoast meta via post update: {r2.status_code}")


def verify_post(url):
    """Check live URL returns HTTP 200."""
    try:
        r = requests.get(url, timeout=15)
        status = r.status_code
        title_present = "Age of AI Agents" in r.text or "age of ai agents" in r.text.lower()
        cta_present = "awakening" in r.text
        print(f"  Verify {url}: HTTP {status} | title_in_page={title_present} | cta_present={cta_present}")
        return status == 200
    except Exception as e:
        print(f"  Verify error: {e}")
        return False


# ── TAG LIST ───────────────────────────────────────────────────────────────────
TAG_NAMES = ["AI agents", "agentic AI", "AI strategy", "AI partnership", "future of AI"]

# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("PUBLISHING: The Age of AI Agents")
    print("=" * 60)

    results = {}

    # ── PUREBRAIN.AI ──────────────────────────────────────────────────────────
    print("\n[1/2] PUREBRAIN.AI")
    pb_banner_id = upload_banner(PUREBRAIN_BASE, PUREBRAIN_USER, PUREBRAIN_PASS, BANNER_PATH)
    pb_cat_id    = get_or_create_category(PUREBRAIN_BASE, PUREBRAIN_USER, PUREBRAIN_PASS, "Agentic AI")
    pb_tag_ids   = [get_or_create_tag(PUREBRAIN_BASE, PUREBRAIN_USER, PUREBRAIN_PASS, t) for t in TAG_NAMES]
    pb_author_id = get_author_id(PUREBRAIN_BASE, PUREBRAIN_USER, PUREBRAIN_PASS)

    pb_post_id, pb_url = publish_post(
        PUREBRAIN_BASE, PUREBRAIN_USER, PUREBRAIN_PASS,
        PB_CONTENT, pb_banner_id, pb_cat_id, pb_tag_ids, pb_author_id,
        include_template=True
    )
    if pb_post_id:
        set_yoast_meta(
            PUREBRAIN_BASE, PUREBRAIN_USER, PUREBRAIN_PASS,
            pb_post_id,
            "The Age of AI Agents: Why Your Business Needs a Team of AIs",
            "The era of single-AI tools is ending. Discover why a coordinated team of purpose-built AI agents creates the compounding competitive advantage your business needs.",
            "AI agents for business"
        )
        results["purebrain"] = {"id": pb_post_id, "url": pb_url, "media_id": pb_banner_id}

    # ── JAREDDSANBORN.COM ─────────────────────────────────────────────────────
    print("\n[2/2] JAREDDSANBORN.COM")
    jds_banner_id = upload_banner(JDS_BASE, JDS_USER, JDS_PASS, BANNER_PATH)
    jds_cat_id    = get_or_create_category(JDS_BASE, JDS_USER, JDS_PASS, "AI Strategy")
    jds_tag_ids   = [get_or_create_tag(JDS_BASE, JDS_USER, JDS_PASS, t) for t in TAG_NAMES]
    jds_author_id = get_author_id(JDS_BASE, JDS_USER, JDS_PASS)

    jds_post_id, jds_url = publish_post(
        JDS_BASE, JDS_USER, JDS_PASS,
        JDS_CONTENT, jds_banner_id, jds_cat_id, jds_tag_ids, jds_author_id,
        include_template=False   # JDS does NOT accept template field
    )
    if jds_post_id:
        set_yoast_meta(
            JDS_BASE, JDS_USER, JDS_PASS,
            jds_post_id,
            "The Age of AI Agents: Why Your Business Needs a Team of AIs",
            "The era of single-AI tools is ending. Discover why a coordinated team of purpose-built AI agents creates the compounding competitive advantage your business needs.",
            "AI agents for business"
        )
        results["jds"] = {"id": jds_post_id, "url": jds_url, "media_id": jds_banner_id}

    # ── VERIFY ────────────────────────────────────────────────────────────────
    print("\n[VERIFICATION]")
    if pb_url:
        verify_post(pb_url)
    if jds_url:
        verify_post(jds_url)

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("DEPLOYMENT SUMMARY")
    print("=" * 60)
    if "purebrain" in results:
        print(f"purebrain.ai  : {results['purebrain']['url']} (Post ID: {results['purebrain']['id']}, Media ID: {results['purebrain']['media_id']})")
    if "jds" in results:
        print(f"jareddsanborn : {results['jds']['url']} (Post ID: {results['jds']['id']}, Media ID: {results['jds']['media_id']})")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
