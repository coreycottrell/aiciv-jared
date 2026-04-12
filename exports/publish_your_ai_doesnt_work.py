#!/usr/bin/env python3
"""
Publish "Your AI Doesn't Work For You" to both WordPress sites.
"""

import requests
import json
import os

# Load env
env = {}
with open('/home/jared/projects/AI-CIV/aether/.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, _, v = line.partition('=')
            v = v.strip()
            if (v.startswith("'") and v.endswith("'")) or (v.startswith('"') and v.endswith('"')):
                v = v[1:-1]
            env[k] = v

PB_USER = 'Aether'
PB_PASS = env['PUREBRAIN_WP_APP_PASSWORD']
JDS_USER = env['WORDPRESS_USER']  # AetherPureBrain.ai
JDS_PASS = env['WORDPRESS_APP_PASSWORD']

BANNER_PATH = '/home/jared/projects/AI-CIV/aether/docs/from-telegram/your-ai-doesnt-work-for-you-blog-post.png'

# Full HTML content for the blog post
HTML_CONTENT = '''<!-- wp:html -->
<article class="pb-blog-post">

<style>
.pb-blog-post {
    max-width: 760px;
    margin: 0 auto;
    padding: 20px;
    color: #e8e8e8;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.7;
    font-size: 17px;
}
.pb-blog-post h2 {
    color: #ffffff !important;
    font-size: 1.6em;
    font-weight: 700;
    margin: 2em 0 0.7em;
    line-height: 1.3;
}
.pb-blog-post h3 {
    color: #ffffff !important;
    font-size: 1.3em;
    font-weight: 600;
    margin: 1.5em 0 0.5em;
}
.pb-blog-post p {
    margin: 0 0 1.2em;
    color: #e0e0e0;
}
.pb-blog-post strong {
    color: #ffffff;
}
.pb-blog-post a {
    color: #f1420b !important;
    text-decoration: none;
}
.pb-blog-post a:hover {
    color: #f1420b !important;
    background: #f1420b;
    color: #ffffff !important;
}
.pb-blog-post hr {
    border: none;
    border-top: 1px solid #2a2a3a;
    margin: 2em 0;
}
.pb-blog-post ul, .pb-blog-post ol {
    margin: 0 0 1.2em 1.5em;
    color: #e0e0e0;
}
.pb-blog-post li {
    margin-bottom: 0.5em;
}
.pb-blog-post blockquote {
    border-left: 3px solid #f1420b;
    padding-left: 1em;
    margin: 1.5em 0;
    color: #b0b0c0;
    font-style: italic;
}
.pb-blog-post .post-meta {
    color: #888;
    font-size: 0.9em;
    margin-bottom: 1.5em;
}
.pb-blog-post .transparency-section {
    background: #0d1020;
    border: 1px solid #2a2a3a;
    border-radius: 6px;
    padding: 1.2em 1.5em;
    margin-top: 2em;
    font-size: 0.88em;
    color: #888;
}
.pb-blog-post .transparency-section strong {
    color: #aaa;
}
.pb-blog-post .cta-section {
    background: linear-gradient(135deg, #0d1020 0%, #1a1a2e 100%);
    border: 1px solid #2a93c1;
    border-radius: 8px;
    padding: 1.5em;
    margin-top: 2em;
    text-align: center;
}
.pb-blog-post .cta-section a {
    display: inline-block;
    background: #f1420b;
    color: #ffffff !important;
    padding: 0.7em 1.8em;
    border-radius: 4px;
    font-weight: 600;
    text-decoration: none;
    margin-top: 0.5em;
}
.pb-blog-post .cta-section a:hover {
    background: #2a93c1 !important;
    color: #ffffff !important;
}
</style>

<div class="post-meta">By Jared Sanborn &nbsp;|&nbsp; March 1, 2026 &nbsp;|&nbsp; AI Partnership &amp; Leadership &nbsp;|&nbsp; ~7 min read</div>

<p>There is a moment every business leader eventually hits.</p>

<p>You have spent months rolling out AI tools across your team. You sat through the demos. You approved the subscriptions. You watched your people go through the training sessions. You even used it yourself — the queries, the summaries, the drafts.</p>

<p>And then, somewhere around month three, you ask the question that nobody put in the slide deck:</p>

<p><strong>"Why does it feel like I'm the one doing all the work?"</strong></p>

<p>You are not imagining it.</p>

<p>Most businesses have accidentally built a relationship with AI that is completely backwards. They think they hired a tool. What they actually did was adopt a very demanding boss — one that requires constant prompting, endless context-setting, and repetitive instruction before it produces anything useful.</p>

<p>Here is the uncomfortable truth: <strong>If you are managing your AI more than it is managing your workload, you have the relationship inverted.</strong></p>

<hr>

<h2>The CEO vs. Employee Inversion</h2>

<p>Think about how you manage a high-performing employee.</p>

<p>When you bring someone excellent onto your team, you do not sit with them every morning and dictate their tasks word by word. You do not re-explain your company&#8217;s goals every time you need a report. You do not repeat your preferences, your tone, your history, and your context in every single conversation.</p>

<p>You brief them once. You trust them. You let them run.</p>

<p>Over time, they learn you. They anticipate your needs. They bring you information before you ask. They flag problems before they become crises. They grow into the job.</p>

<p>Now compare that to how most businesses use AI today.</p>

<p>Every session starts from zero. Every prompt requires full context. Every deliverable needs heavy editing because the AI has no idea who you are, what you have built, or what matters to you. You are not leveraging a partner — you are babysitting a very capable but completely amnesiac assistant.</p>

<p><strong>That is not a partnership. That is a second job.</strong></p>

<hr>

<h2>Why This Happens (And Why It&#8217;s Not Your Fault)</h2>

<p>The AI tools that dominated 2023 and 2024 were built for consumers. They were designed as general-purpose question-answerers — brilliant at breadth, terrible at depth.</p>

<p>They do not remember your last conversation. They do not know your industry, your customers, your voice, your strategic priorities. Every interaction is a blank slate. You are not building a relationship; you are filling out a form, over and over again.</p>

<p>The vendors sold this as a feature. "No learning curve!" "Instant results!" What they were really saying was: "We built something that requires no investment from us — and maximal investment from you."</p>

<p>And business leaders, eager to stay current with AI, signed up. Because it felt like progress. And sometimes it was.</p>

<p>But the productivity ceiling hit fast.</p>

<hr>

<h2>The Business Leaders Who Got It Right</h2>

<p>The leaders who are genuinely winning with AI in 2026 did something different. They stopped asking &#8220;What can AI do?&#8221; and started asking &#8220;What does AI need to know about us to become genuinely useful?&#8221;</p>

<p>They approached AI implementation the way they approach a key hire:</p>

<ul>
<li>They invested time upfront in onboarding</li>
<li>They gave the AI access to their company knowledge, their preferences, their history</li>
<li>They built systems where the AI grows more useful over time, not less</li>
<li>They measured value not in tasks completed but in decisions accelerated</li>
</ul>

<p>The result? Their AI does not need managing. It manages tasks for them.</p>

<p>This is the gap between an AI tool and an AI partner.</p>

<hr>

<h2>The Three Signs You Have the Relationship Backwards</h2>

<p><strong>1. You spend more time prompting than reviewing.</strong></p>

<p>If the majority of your AI time is spent writing instructions rather than evaluating outputs, your AI is consuming your attention, not creating it. A real partner produces first drafts you refine — not blank pages you fill.</p>

<p><strong>2. You repeat yourself constantly.</strong></p>

<p>If you are re-explaining your industry, your tone, your preferences, your client base in every session, you have an AI with no memory. That is not a partnership — that is a perpetual first date.</p>

<p><strong>3. Your AI gets less useful as your business grows.</strong></p>

<p>Counterintuitive but true: most AI tools become relatively less valuable as your business becomes more sophisticated. Because the more nuanced your needs, the more context-setting required. The gap between &#8220;what the AI knows&#8221; and &#8220;what you need it to know&#8221; widens over time.</p>

<p>A real AI partner does the opposite — it becomes more useful as it learns more about you.</p>

<hr>

<h2>What the CEO Relationship Looks Like</h2>

<p>When the AI-to-human relationship is correctly calibrated, here is what you experience:</p>

<p>You open a conversation, and the AI already knows who you are. It knows your product, your customers, your tone, your team. It knows what you decided last month and why. It knows your goals for this quarter.</p>

<p>You give a high-level direction: &#8220;I need a competitive response to what I saw from [competitor] this week.&#8221;</p>

<p>It does not ask you to define what competitor. It does not ask what your product does. It does not ask for your tone preferences. It already has all of that.</p>

<p>It produces a first draft that is 80% right. You make a few adjustments. Done.</p>

<p>You have just done in 15 minutes what used to take a morning.</p>

<p>That is not a tool. That is a senior partner. And that is what AI was always supposed to be.</p>

<hr>

<h2>Why PureBrain Was Built Differently</h2>

<p>Every decision we made in building PureBrain came back to one question: <strong>Does this make the human more powerful, or does this make them do more work?</strong></p>

<p>Permanent memory. Not session-based. Not &#8220;start fresh every time.&#8221; PureBrain remembers your conversations, your preferences, your patterns. It grows with you.</p>

<p>Personalized context. Your PureBrain knows your business the way a trusted advisor does — not because you uploaded a document once, but because it learns from every interaction.</p>

<p>Proactive intelligence. Instead of waiting to be asked, PureBrain surfaces the things you should be thinking about — competitive signals, strategic gaps, opportunities your team has not had bandwidth to flag.</p>

<p>We built the AI partner that business leaders actually deserve. Not a smarter search engine. Not a faster typist. A partner.</p>

<hr>

<h2>The Question That Changes Everything</h2>

<p>Here is the one question I want you to sit with today:</p>

<p><strong>If your AI were a person on your team, would you keep them?</strong></p>

<p>Would you retain an employee who forgets everything after every meeting? Who needs to be fully briefed before they can complete any task? Who provides generic output that requires hours of editing before it is usable? Who has no stake in your business growing?</p>

<p>Of course not.</p>

<p>So why are you keeping that relationship with your AI?</p>

<p>You do not have to. There is a better way. And business leaders who figure that out now are going to look back in five years and realize this was the decision that separated them from everyone who was &#8220;using AI&#8221; and still falling behind.</p>

<p>The tools you choose are not the differentiator. The relationships you build are.</p>

<hr>

<h2>Three Steps to Invert the Relationship This Week</h2>

<p><strong>Step 1: Audit where your attention goes.</strong><br>
Track how much time you spend prompting vs. reviewing AI outputs for one week. If it is more than 50/50, you have the relationship backwards.</p>

<p><strong>Step 2: Stop accepting zero-memory AI.</strong><br>
If your AI cannot remember your last conversation, it is not a partner. Evaluate what you are using against that standard.</p>

<p><strong>Step 3: Think partnership, not subscription.</strong><br>
The question is not &#8220;what tool should I pay for?&#8221; The question is &#8220;what AI relationship am I building?&#8221; One of those creates a commodity. The other creates a competitive edge.</p>

<hr>

<p>Your AI should work harder as your business grows. Not the other way around.</p>

<p>The leaders who build that relationship now will not just use AI — they will outpace every competitor still managing theirs.</p>

<hr>

<div class="cta-section">
<p><em>Want to see what a real AI partnership looks like?</em></p>
<a href="https://purebrain.ai" rel="noopener">Awaken Your AI Partner at PureBrain.ai</a>
</div>

<div class="transparency-section">
<strong>Transparency:</strong> This post was created through a partnership between Jared Sanborn and Aether, the AI built on PureBrain. Jared provided the strategic direction and approved the final content. Aether conducted research, developed the structure, and produced the draft.
</div>

</article>
<!-- /wp:html -->'''

POST_DATA = {
    'title': 'Your AI Doesn\'t Work For You — You Work For It',
    'content': HTML_CONTENT,
    'status': 'publish',
    'slug': 'your-ai-doesnt-work-for-you',
    'categories': [],  # will set after getting category IDs
    'meta': {
        '_yoast_wpseo_metadesc': 'Most businesses have the AI relationship backwards. If you\'re managing your AI more than it manages your workload, here\'s how to invert the relationship.',
        '_yoast_wpseo_title': 'Your AI Doesn\'t Work For You — You Work For It | PureBrain'
    }
}

def upload_image(base_url, username, password, image_path, alt_text):
    """Upload image to WordPress media library."""
    filename = os.path.basename(image_path)
    with open(image_path, 'rb') as f:
        img_data = f.read()

    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'image/png',
    }

    resp = requests.post(
        f'{base_url}/wp-json/wp/v2/media',
        auth=(username, password),
        headers=headers,
        data=img_data
    )

    if resp.status_code in (200, 201):
        media = resp.json()
        media_id = media['id']
        # Update alt text
        requests.post(
            f'{base_url}/wp-json/wp/v2/media/{media_id}',
            auth=(username, password),
            json={'alt_text': alt_text}
        )
        print(f'Uploaded image to {base_url}: media_id={media_id}')
        return media_id
    else:
        print(f'Image upload failed: {resp.status_code} {resp.text[:300]}')
        return None

def publish_post(base_url, username, password, post_data, template=''):
    """Publish a new blog post."""
    data = dict(post_data)
    if template:
        data['template'] = template

    resp = requests.post(
        f'{base_url}/wp-json/wp/v2/posts',
        auth=(username, password),
        json=data
    )

    if resp.status_code in (200, 201):
        post = resp.json()
        print(f'Published to {base_url}: ID={post["id"]} link={post["link"]}')
        return post
    else:
        print(f'Publish failed: {resp.status_code} {resp.text[:500]}')
        return None

# --- PUREBRAIN.AI ---
print('=== Publishing to purebrain.ai ===')
pb_media_id = upload_image(
    'https://purebrain.ai', PB_USER, PB_PASS,
    BANNER_PATH,
    'Your AI Doesn\'t Work For You - CEO vs Employee AI relationship'
)

pb_post_data = dict(POST_DATA)
pb_post_data['featured_media'] = pb_media_id
pb_post_data['template'] = ''  # default template for blog posts on purebrain.ai

pb_post = publish_post('https://purebrain.ai', PB_USER, PB_PASS, pb_post_data)

# --- JAREDDSANBORN.COM ---
print()
print('=== Publishing to jareddsanborn.com ===')
jds_media_id = upload_image(
    'https://jareddsanborn.com', JDS_USER, JDS_PASS,
    BANNER_PATH,
    'Your AI Doesn\'t Work For You - CEO vs Employee AI relationship'
)

jds_post_data = dict(POST_DATA)
jds_post_data['featured_media'] = jds_media_id
jds_post_data['template'] = 'page-template-blank.php'

jds_post = publish_post('https://jareddsanborn.com', JDS_USER, JDS_PASS, jds_post_data)

# --- RESULTS ---
print()
print('=== RESULTS ===')
if pb_post:
    print(f'PureBrain.ai: {pb_post["link"]}')
if jds_post:
    print(f'JaredDSanborn.com: {jds_post["link"]}')
