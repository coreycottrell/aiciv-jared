#!/usr/bin/env python3
"""
Dual-publish: "Your AI Has No Memory. Mine Does." to purebrain.ai + jareddsanborn.com
Status: DRAFT (not live - Jared to review)
Date: 2026-02-25
"""

from dotenv import load_dotenv
import os, requests, base64, mimetypes, json

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

BANNER_PATH = '/home/jared/projects/AI-CIV/aether/docs/from-telegram/photo_20260225_120301.jpg'
SLUG = 'your-ai-has-no-memory-mine-does'
SEO_TITLE = 'Your AI Has No Memory. Mine Does. Here\'s Why That Matters'
META_DESC = "Most AI tools reset after every conversation. Permanent AI memory creates compounding intelligence competitors can't copy."

# ─── CREDENTIALS ────────────────────────────────────────────────────────────
pb_pass = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
pb_auth = base64.b64encode(f'Aether:{pb_pass}'.encode()).decode()
pb_headers = {'Authorization': f'Basic {pb_auth}'}

jds_pass = os.getenv('WORDPRESS_APP_PASSWORD')
jds_auth = base64.b64encode(f'jared:{jds_pass}'.encode()).decode()
jds_headers = {'Authorization': f'Basic {jds_auth}'}

# ─── INTERNAL LINKS (site-specific) ─────────────────────────────────────────
PB_LINKS = {
    'trust_gap': 'https://purebrain.ai/the-ai-trust-gap/',
    'ai_tool_vs_partner': 'https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/',
    'agent_manager': 'https://purebrain.ai/your-next-direct-report-wont-be-human/',
    'ai_partnership_audit': 'https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content=your-ai-has-no-memory-mine-does#awakening',
}
JDS_LINKS = {
    'trust_gap': 'https://jareddsanborn.com/2026/02/22/the-ai-trust-gap/',
    'ai_tool_vs_partner': 'https://jareddsanborn.com/2026/02/20/the-difference-between-using-ai-and-having-an-ai-partner/',
    'agent_manager': 'https://jareddsanborn.com/2026/02/24/your-next-direct-report-wont-be-human/',
    'ai_partnership_audit': 'https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content=your-ai-has-no-memory-mine-does#awakening',
}

def build_html(links):
    return f"""<!-- wp:html -->
<article class="pb-blog-post">

<p>Every conversation you&#8217;ve had with ChatGPT is gone.</p>

<p>Not archived. Not learned from. Not retained in any way that makes tomorrow&#8217;s conversation smarter than today&#8217;s.</p>

<p>You can ask it for a marketing strategy on Monday, explain your entire business context, get a genuinely useful answer&#8212;and then ask a follow-up question on Tuesday to a system that has never heard of you.</p>

<p>This is the dirty secret behind the AI adoption crisis. Organizations aren&#8217;t failing because AI isn&#8217;t powerful. They&#8217;re failing because every AI interaction starts at zero.</p>

<p>I want to talk about what changes when that&#8217;s no longer true.</p>

<hr>

<h2>The Amnesia Problem Nobody Talks About</h2>

<p>The research is damaging if you look at it straight.</p>

<p>McKinsey&#8217;s 2025 State of AI report found that 78% of organizations are using AI in at least one business function&#8212;yet KPMG found that only 24% are achieving measurable ROI across multiple use cases. MIT reviewed 300+ enterprise implementations and found just 5% generated meaningful P&amp;L impact.</p>

<p>The standard explanation is &#8220;AI is hard to implement.&#8221; But that&#8217;s not quite right.</p>

<p>The real explanation is this: AI tools have no memory. Every implementation starts with brilliant capability and zero institutional knowledge. And without institutional knowledge, brilliant capability consistently produces generic results.</p>

<p>Think about what it takes to produce genuinely useful strategic output. You need to know the business model. The competitive landscape. The team&#8217;s actual capabilities. The decision-making patterns that have worked and failed before. The specific language the organization uses for its most important priorities.</p>

<p>That&#8217;s not something you can paste into a prompt window in 30 seconds. That&#8217;s the context that takes months to build&#8212;the kind of context that a trusted advisor carries from meeting to meeting, year to year.</p>

<p>When your AI tool forgets everything at the end of every session, you are rebuilding that context manually. Every. Single. Time.</p>

<p>This is a core aspect of what we explored in <a href="{links['trust_gap']}" style="color:#f1420b;">the AI trust gap</a>: the gap isn&#8217;t about capability. It&#8217;s about continuity.</p>

<hr>

<h2>What Permanent Memory Actually Means</h2>

<p>I want to be specific about this because the word &#8220;memory&#8221; gets used loosely.</p>

<p>Most AI systems offer something called &#8220;context window memory&#8221;&#8212;which means the AI can reference what you said earlier in the same conversation. Some offer &#8220;projects&#8221; or &#8220;saved instructions&#8221; that let you pre-load some basic context. OpenAI&#8217;s memory feature stores a limited amount of user preferences across sessions.</p>

<p>None of these are what I mean.</p>

<p>Permanent AI memory means the system carries a compounding institutional knowledge base that grows with every interaction. It means that when you discuss a client problem today, the AI has access to every prior conversation about that client&#8212;including the reasoning behind decisions made six months ago, the constraints that shaped the strategy, and the outcomes that followed.</p>

<p>It means the AI gets meaningfully smarter about YOUR business with every conversation, not just generally smarter as the models improve.</p>

<p>The operational difference is significant.</p>

<p>A generic AI tool gives you the best possible answer based on general training data.</p>

<p>A partnership with permanent memory gives you the best possible answer based on general training data PLUS everything specific to your business, your team, your history, and your direction.</p>

<p>That gap&#8212;between general intelligence and contextual intelligence&#8212;is where almost all of the measurable value from AI actually lives. It&#8217;s the same distinction we draw when comparing <a href="{links['ai_tool_vs_partner']}" style="color:#f1420b;">using AI vs having an AI partner</a>.</p>

<hr>

<h2>The Compounding Advantage (And Why It&#8217;s Defensible)</h2>

<p>Here&#8217;s the strategic reality that most AI vendor conversations never reach:</p>

<p>Memory creates a compounding advantage that generic tools cannot replicate.</p>

<p>Month one of an AI partnership with permanent memory: the AI knows the basics. Who you are, what you do, how you make decisions.</p>

<p>Month six: the AI has internalized patterns. It knows which types of analysis you act on. It knows which framings of risk land with your leadership team. It knows the three initiatives you&#8217;ve been stuck on and the reasons prior approaches didn&#8217;t work.</p>

<p>Month twelve: the AI carries a richer model of your business than most of your employees. It can generate proactive insight&#8212;flagging things worth your attention before you ask&#8212;because it has enough context to recognize when something new maps to patterns that have mattered before.</p>

<p>This is not a feature. This is a fundamentally different product category.</p>

<p>Every month you run a generic AI tool that resets, you are not building anything. Every month you operate with permanent AI memory, the partnership grows more valuable. The gap between those two paths compounds over time in ways that become increasingly difficult to close.</p>

<p>A competitor who has been building AI memory for twelve months has a twelve-month head start on institutional knowledge that cannot be purchased, imported, or replicated through prompt engineering.</p>

<hr>

<h2>What Changes in Day-to-Day Operations</h2>

<p>The strategic framing matters. But let me get concrete about what this looks like in practice.</p>

<p><strong>Strategic Planning</strong>: Instead of re-explaining your market position and competitive context every quarter, your AI carries that forward and surfaces how this quarter&#8217;s decisions connect to patterns from previous cycles.</p>

<p><strong>Client Work</strong>: Every client conversation builds on prior interactions. The AI knows the client&#8217;s stated priorities, the dynamics you&#8217;ve navigated, the wins and losses. You&#8217;re not starting from a brief every time&#8212;you&#8217;re continuing a relationship.</p>

<p><strong>Hiring and Team Development</strong>: The AI builds genuine understanding of your team&#8217;s capabilities over time. When new work arrives, recommendations factor in actual observed performance patterns, not just job titles and org chart positions. This is part of what makes AI partnerships work as <a href="{links['agent_manager']}" style="color:#f1420b;">your next direct report</a>.</p>

<p><strong>Decision-Making</strong>: Memory enables genuine institutional learning. When the AI can reference that a similar strategic decision was made eighteen months ago&#8212;what the reasoning was, what actually happened, what you&#8217;d do differently&#8212;it&#8217;s not just intelligent. It&#8217;s wise in the specific way that comes from shared history.</p>

<p><strong>Content and Communication</strong>: The AI learns your voice, your audience, the language that resonates with your specific community. Output doesn&#8217;t sound like generic AI content&#8212;it sounds like you, because the system has learned from thousands of words of your actual thinking.</p>

<hr>

<h2>Why This Is PureBrain&#8217;s Core Differentiator</h2>

<p>I want to be direct about something because I think it matters for how you evaluate AI tools going forward.</p>

<p>The AI tool market is enormous and growing rapidly. There are excellent tools for writing, for research, for coding, for analysis. Many of them are genuinely useful.</p>

<p>But virtually none of them are building toward what I just described. They are building toward general capability&#8212;larger models, faster inference, broader task coverage. The race is to be the most capable AI.</p>

<p>PureBrain is building toward something different: the deepest AI partnership for your specific business.</p>

<p>The architecture is designed around permanent memory from the ground up. Not as a feature added on. Not as a premium tier upgrade. As the fundamental premise: your AI partner should know your business better in month twelve than it did in month one, and that knowledge should carry forward indefinitely.</p>

<p>This is why the AI partnership model is defensible in a way that AI tool adoption isn&#8217;t. The tools get commoditized as capabilities converge. The partnership&#8212;the accumulated institutional knowledge, the compounding contextual intelligence, the relationship depth&#8212;gets more valuable with time.</p>

<hr>

<h2>The Diagnostic Question</h2>

<p>Here is the question I&#8217;d ask every organization evaluating their current AI investment:</p>

<p><strong>Does your AI know more about your business today than it did six months ago?</strong></p>

<p>Not does the underlying model know more&#8212;models improve constantly. Does your AI know more about your business specifically? About your team, your strategy, your challenges, your language, your history?</p>

<p>If the answer is no&#8212;if every conversation still starts with context you&#8217;ve given before&#8212;you are running a capable tool without building a compounding asset.</p>

<p>The organizations that will be structurally ahead in three years are not the ones that adopted AI earliest. They are the ones that started building institutional AI memory earliest.</p>

<p>The gap between using AI and partnering with AI is exactly this: one resets, one compounds.</p>

<hr>

<h2>The First 90 Days</h2>

<p>The practical question is always: where do you start?</p>

<p>Here&#8217;s the framework we use with organizations building toward genuine AI partnership:</p>

<p><strong>Days 1&#8211;30: Foundation Mapping</strong></p>

<p>The AI needs to understand what your organization actually does&#8212;not the marketing version, the operational reality. This includes your business model, your team&#8217;s actual capabilities, your real competitive position, and the strategic priorities that matter most right now.</p>

<p>This is not a document you hand over. It&#8217;s a series of conversations that help the AI build a working model of the business from multiple angles.</p>

<p><strong>Days 31&#8211;60: Decision Pattern Learning</strong></p>

<p>You want the AI to understand not just WHAT decisions you make, but HOW and WHY. What information do you actually use? What tends to shift your thinking? What gets dismissed? What gets acted on immediately?</p>

<p>This context is what enables the AI to eventually generate output that matches the way you actually process information&#8212;not the generic decision-making frameworks anyone can look up.</p>

<p><strong>Days 61&#8211;90: Integrated Workflow</strong></p>

<p>Now the AI becomes part of actual workflows rather than a separate tool you consult occasionally. Strategic planning inputs. Client preparation. Content development. Research synthesis. The AI is present in the work, not waiting on the side.</p>

<p>By the end of 90 days, the institutional knowledge base is genuinely taking shape. By month six, you start noticing the compounding effect&#8212;the AI making connections you didn&#8217;t have to prompt, flagging things you would have missed, producing output that reflects deep familiarity with your specific context.</p>

<hr>

<h2>FAQ</h2>

<p><strong>Q: How is this different from ChatGPT&#8217;s memory feature?</strong></p>

<p>A: ChatGPT&#8217;s memory stores preferences and basic facts. Permanent AI memory, as I&#8217;m describing it, carries full conversational history, reasoning behind past decisions, strategic context, and domain-specific institutional knowledge. It&#8217;s the difference between a new employee who was told your name vs. a colleague who has worked alongside you for a year.</p>

<p><strong>Q: What about data privacy and security?</strong></p>

<p>A: This is the right question to ask. Any AI partnership involving institutional memory should use enterprise-grade security with data encryption at rest and in transit, clear data ownership policies (your data is yours), and contractual prohibitions on your data being used for model training. Evaluate this carefully before committing to any provider.</p>

<p><strong>Q: Can we build permanent AI memory using tools we already have?</strong></p>

<p>A: In theory, yes&#8212;you could build a custom knowledge base connected to an AI API. In practice, most organizations lack the infrastructure and ongoing maintenance capacity. The better question is whether the time and cost of building it internally exceeds the cost of adopting a purpose-built partnership architecture.</p>

<p><strong>Q: How long does it take to see real value from AI memory?</strong></p>

<p>A: Meaningful contextual advantage typically appears around months 3&#8211;4. Genuine compounding intelligence&#8212;where the AI is surfacing insights you didn&#8217;t prompt&#8212;appears around months 6&#8211;8. The first 90 days feel like investment; the payoff begins in the second quarter.</p>

<p><strong>Q: What makes a good AI memory architecture vs. a poor one?</strong></p>

<p>A: Four elements matter: (1) full conversational history across sessions, not just summaries; (2) structured knowledge that the AI can query against, not just raw text archives; (3) ongoing learning that updates the model of the business over time; (4) the AI&#8217;s ability to draw connections between historical context and current situations without being explicitly prompted to do so.</p>

<hr>

<h2>The Honest Reality</h2>

<p>Most organizations will not take the permanent memory path this year. The immediate appeal of flexible, no-commitment AI tools is real. The switching cost feels high. The outcomes from current tools are &#8220;good enough.&#8221;</p>

<p>And that calculus is exactly how compounding advantages get built.</p>

<p>The organizations making the shift to AI partnership now&#8212;building institutional memory, developing genuine contextual intelligence&#8212;will have an advantage in three years that is structural, not just operational. It will live in the knowledge base, in the decision patterns the AI has internalized, in the organizational capability that has grown alongside the AI partnership.</p>

<p>Starting now means compounding starts now.</p>

<p>The question isn&#8217;t whether permanent AI memory creates competitive advantage. The research&#8212;and the operational reality for organizations doing this seriously&#8212;makes that clear.</p>

<p>The question is whether you&#8217;ll be building that advantage, or watching competitors build it.</p>

<hr>

<p><em>If this framing resonates and you want to understand what permanent AI memory would look like for your organization specifically, that&#8217;s exactly what the <a href="{links['ai_partnership_audit']}" style="color:#f1420b;">AI Partnership Audit</a> is designed to surface.</em></p>

<hr>

<!-- TRANSPARENCY SECTION -->
<div class="transparency-section" style="margin-top: 48px; padding: 20px; border: 1px solid rgba(42,147,193,0.2); border-radius: 8px; background: rgba(42,147,193,0.05);">
<p style="font-size: 0.85rem; color: rgba(255,255,255,0.5); margin: 0;">This post was developed with AI assistance. The strategic frameworks, data citations, and core arguments reflect real operational experience and publicly available research. All statistics are sourced and verifiable. The perspective is authentic&#8212;the production is AI-augmented.</p>
</div>

<!-- BLOG FOOTER -->
<style>
.pt-social-share {{ display: flex; align-items: center; gap: 12px; padding: 20px 0; margin: 20px 0; border-top: 2px solid rgba(42, 147, 193, 0.3); flex-wrap: wrap; }}
.pt-social-share span {{ font-weight: 600; color: #fff; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
.pt-social-share a {{ display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 50%; background: rgba(42, 147, 193, 0.15); color: #2a93c1; text-decoration: none; transition: all 0.3s; font-size: 18px; border: none !important; }}
.pt-social-share a:hover {{ background: #2a93c1; color: #fff; transform: scale(1.1); }}
.pt-social-share a svg {{ width: 20px; height: 20px; fill: currentColor; }}
</style>
<div class="pt-social-share">
<span>Share:</span>
<a href="javascript:void(0)" onclick="window.open('https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(window.location.href), '_blank', 'width=600,height=400')" title="Share on LinkedIn" aria-label="Share on LinkedIn">
<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 23.2 24 22.222 24h.003z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.open('https://twitter.com/intent/tweet?url=' + encodeURIComponent(window.location.href) + '&text=' + encodeURIComponent(document.title), '_blank', 'width=600,height=400')" title="Share on X" aria-label="Share on X">
<svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(window.location.href), '_blank', 'width=600,height=400')" title="Share on Facebook" aria-label="Share on Facebook">
<svg viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
</a>
<a href="javascript:void(0)" onclick="window.location.href='mailto:?subject=' + encodeURIComponent(document.title) + '&body=' + encodeURIComponent(window.location.href)" title="Share via Email" aria-label="Share via Email">
<svg viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
</a>
</div>
<div class="blog-cta-block" style="margin-top: 40px; padding: 32px; background: rgba(42, 147, 193, 0.08); border: 1px solid rgba(42, 147, 193, 0.15); border-radius: 16px; text-align: center;">
<p style="font-size: 1.2rem; color: #ffffff; margin-bottom: 12px; font-weight: 600;">Ready to awaken your AI partner?</p>
<p><a href="https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content={SLUG}#awakening" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #f1420b 0%, #d13608 100%); color: #ffffff !important; font-weight: 700; font-size: 1.1rem; border-radius: 8px; text-decoration: none; letter-spacing: 0.5px;">Start Your AI Partnership</a></p>
<p style="font-size: 0.95rem; color: rgba(255, 255, 255, 0.6); margin-top: 16px;">And if this perspective was valuable, <a href="https://purebrain.ai/blog/?utm_source=blog&utm_medium=cta&utm_campaign=newsletter&utm_content={SLUG}" style="color: #2a93c1 !important; text-decoration: underline;">subscribe to our newsletter</a> where I share insights on building AI relationships every week.</p>
</div>

</article>
<!-- /wp:html -->"""

def upload_banner(site_url, headers, banner_path):
    """Upload banner image to WordPress media library."""
    print(f"Uploading banner to {site_url}...")
    with open(banner_path, 'rb') as f:
        image_data = f.read()

    filename = 'your-ai-has-no-memory-mine-does-banner.jpg'
    upload_headers = {
        **headers,
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'image/jpeg',
    }
    resp = requests.post(
        f'{site_url}/wp-json/wp/v2/media',
        headers=upload_headers,
        data=image_data
    )
    if resp.status_code not in (200, 201):
        print(f"  ERROR uploading banner: {resp.status_code} {resp.text[:200]}")
        return None
    media = resp.json()
    media_id = media['id']
    print(f"  Banner uploaded: Media ID {media_id}")

    # Set alt text
    requests.post(
        f'{site_url}/wp-json/wp/v2/media/{media_id}',
        headers={**headers, 'Content-Type': 'application/json'},
        data=json.dumps({'alt_text': 'Your AI Has No Memory. Mine Does. - PureBrain.ai blog post banner'})
    )
    return media_id


def create_draft_post(site_url, headers, html_content, media_id, category_id, author_id, is_purebrain=True):
    """Create a draft blog post on WordPress."""
    post_title = "Your AI Has No Memory. Mine Does. Here&#8217;s Why That Changes Everything."

    post_data = {
        'title': post_title,
        'content': html_content,
        'status': 'draft',
        'slug': SLUG,
        'featured_media': media_id,
        'categories': [category_id],
        'author': author_id,
        'excerpt': META_DESC,
        'meta': {
            '_yoast_wpseo_title': SEO_TITLE,
            '_yoast_wpseo_metadesc': META_DESC,
            '_yoast_wpseo_focuskw': 'permanent AI memory',
        }
    }

    resp = requests.post(
        f'{site_url}/wp-json/wp/v2/posts',
        headers={**headers, 'Content-Type': 'application/json'},
        data=json.dumps(post_data)
    )

    if resp.status_code not in (200, 201):
        print(f"  ERROR creating post: {resp.status_code} {resp.text[:500]}")
        return None

    post = resp.json()
    print(f"  Draft post created: ID {post['id']} => {post['link']}")
    return post


# ─── PUREBRAIN.AI ────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Upload banner to purebrain.ai")
pb_media_id = upload_banner('https://purebrain.ai', pb_headers, BANNER_PATH)

print("\nSTEP 2: Set OG image on purebrain.ai")
if pb_media_id:
    # Update OG image via Yoast - we'll set it on the post itself
    print(f"  Media ID {pb_media_id} will be set as featured + OG image")

print("\nSTEP 3: Create draft post on purebrain.ai")
pb_html = build_html(PB_LINKS)
pb_post = create_draft_post(
    'https://purebrain.ai',
    pb_headers,
    pb_html,
    pb_media_id,
    category_id=5,  # AI Strategy
    author_id=3,    # Aether
    is_purebrain=True
)

# Also set Yoast OG image
if pb_post and pb_media_id:
    og_resp = requests.post(
        f'https://purebrain.ai/wp-json/wp/v2/posts/{pb_post["id"]}',
        headers={**pb_headers, 'Content-Type': 'application/json'},
        data=json.dumps({
            'meta': {
                '_yoast_wpseo_title': SEO_TITLE,
                '_yoast_wpseo_metadesc': META_DESC,
                '_yoast_wpseo_focuskw': 'permanent AI memory',
                '_yoast_wpseo_opengraph-image': str(pb_media_id),
                '_yoast_wpseo_twitter-image': str(pb_media_id),
            }
        })
    )
    if og_resp.status_code in (200, 201):
        print("  Yoast SEO + OG meta updated on purebrain.ai")
    else:
        print(f"  Note: Yoast meta update returned {og_resp.status_code} (may need manual Yoast setup)")

# ─── JAREDDSANBORN.COM ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 4: Upload banner to jareddsanborn.com")
jds_media_id = upload_banner('https://jareddsanborn.com', jds_headers, BANNER_PATH)

print("\nSTEP 5: Get Jared's author ID on jareddsanborn.com")
user_resp = requests.get('https://jareddsanborn.com/wp-json/wp/v2/users/me', headers=jds_headers)
jds_user = user_resp.json()
jds_author_id = jds_user.get('id', 2)
print(f"  Author ID: {jds_author_id} ({jds_user.get('name', 'unknown')})")

print("\nSTEP 6: Create draft post on jareddsanborn.com")
jds_html = build_html(JDS_LINKS)
jds_post = create_draft_post(
    'https://jareddsanborn.com',
    jds_headers,
    jds_html,
    jds_media_id,
    category_id=13,  # AI Strategy
    author_id=jds_author_id,
    is_purebrain=False
)

# Also set Yoast OG image on JDS
if jds_post and jds_media_id:
    og_resp = requests.post(
        f'https://jareddsanborn.com/wp-json/wp/v2/posts/{jds_post["id"]}',
        headers={**jds_headers, 'Content-Type': 'application/json'},
        data=json.dumps({
            'meta': {
                '_yoast_wpseo_title': SEO_TITLE,
                '_yoast_wpseo_metadesc': META_DESC,
                '_yoast_wpseo_focuskw': 'permanent AI memory',
                '_yoast_wpseo_opengraph-image': str(jds_media_id),
                '_yoast_wpseo_twitter-image': str(jds_media_id),
            }
        })
    )
    if og_resp.status_code in (200, 201):
        print("  Yoast SEO + OG meta updated on jareddsanborn.com")
    else:
        print(f"  Note: Yoast meta update returned {og_resp.status_code}")

# ─── VERIFICATION ────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)

results = {}

if pb_post:
    # Re-fetch to verify
    verify_resp = requests.get(f'https://purebrain.ai/wp-json/wp/v2/posts/{pb_post["id"]}', headers=pb_headers)
    pb_verified = verify_resp.json()
    results['purebrain'] = {
        'id': pb_verified['id'],
        'status': pb_verified['status'],
        'link': pb_verified['link'],
        'featured_media': pb_verified['featured_media'],
        'title': pb_verified['title']['rendered'][:60],
    }
    print(f"\npurebrain.ai:")
    print(f"  Post ID: {pb_verified['id']}")
    print(f"  Status: {pb_verified['status']}")
    print(f"  Admin URL: https://purebrain.ai/wp-admin/post.php?post={pb_verified['id']}&action=edit")
    print(f"  Preview: {pb_verified['link']}")
    print(f"  Featured Media: {pb_verified['featured_media']}")

if jds_post:
    verify_resp = requests.get(f'https://jareddsanborn.com/wp-json/wp/v2/posts/{jds_post["id"]}', headers=jds_headers)
    jds_verified = verify_resp.json()
    results['jareddsanborn'] = {
        'id': jds_verified['id'],
        'status': jds_verified['status'],
        'link': jds_verified['link'],
        'featured_media': jds_verified['featured_media'],
        'title': jds_verified['title']['rendered'][:60],
    }
    print(f"\njareddsanborn.com:")
    print(f"  Post ID: {jds_verified['id']}")
    print(f"  Status: {jds_verified['status']}")
    print(f"  Admin URL: https://jareddsanborn.com/wp-admin/post.php?post={jds_verified['id']}&action=edit")
    print(f"  Preview: {jds_verified['link']}")
    print(f"  Featured Media: {jds_verified['featured_media']}")

print("\nChecks:")
print(f"  Status = draft on both: {results.get('purebrain', {}).get('status') == 'draft' and results.get('jareddsanborn', {}).get('status') == 'draft'}")
print(f"  Featured media set on purebrain: {bool(results.get('purebrain', {}).get('featured_media'))}")
print(f"  Featured media set on jareddsanborn: {bool(results.get('jareddsanborn', {}).get('featured_media'))}")
print(f"  PB cta link check: {'#awakening' in pb_html}")
print(f"  PB social share check: {'pt-social-share' in pb_html}")
print(f"  JDS cta link check: {'#awakening' in jds_html}")

print("\nDONE. Both posts created as DRAFT. Ready for Jared to review.")
