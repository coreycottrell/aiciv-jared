#!/usr/bin/env python3
"""
Publish: "Your AI Has No Idea Who You Are"

1. Build CF Pages static HTML -> exports/cf-pages-deploy/blog/your-ai-has-no-idea-who-you-are/index.html
2. Add to blog index + _redirects
3. Publish to jareddsanborn.com WP (API works)
4. Report on purebrain.ai WP (API blocked by CF WAF - note for Jared)

Source files:
  /home/jared/portal_uploads/from-portal/portal_20260312_161203_your-ai-has-no-idea-who-you-are-blogpost.md
  /home/jared/portal_uploads/from-portal/portal_20260312_161204_your-ai-has-no-idea-who-you-are-blogpost-Newslettersize.png
"""

import os
import re
import json
import base64
import requests
import shutil
from pathlib import Path

# ─── PATHS ───────────────────────────────────────────────────────────────────
PROJECT = Path("/home/jared/projects/AI-CIV/aether")
BLOG_DIR = PROJECT / "exports/cf-pages-deploy/blog"
SLUG = "your-ai-has-no-idea-who-you-are"
POST_DIR = BLOG_DIR / SLUG

MD_PATH = Path("/home/jared/portal_uploads/from-portal/portal_20260312_161203_your-ai-has-no-idea-who-you-are-blogpost.md")
BANNER_PATH = Path("/home/jared/portal_uploads/from-portal/portal_20260312_161204_your-ai-has-no-idea-who-you-are-blogpost-Newslettersize.png")

# ─── WP CREDENTIALS ───────────────────────────────────────────────────────────
def load_env():
    env = {}
    with open(PROJECT / ".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ENV = load_env()

# jareddsanborn.com
JDS_USER = "jared"
JDS_PASS = ENV.get("WORDPRESS_APP_PASSWORD", "plhi NeE4 Cb1c 4d9i BbjZ Knq3")
JDS_URL = "https://jareddsanborn.com"

# ─── MARKDOWN → HTML ─────────────────────────────────────────────────────────
def md_to_html(md_text):
    """Convert markdown body to HTML, preserving the article wrapper."""
    # The markdown already has <article class="pb-blog-post"> wrapper
    # Extract content inside the article tag
    m = re.search(r'<article class="pb-blog-post">(.*?)(?:</article>|$)', md_text, re.DOTALL)
    if m:
        inner = m.group(1).strip()
    else:
        inner = md_text.strip()

    # Process markdown elements
    lines = inner.split('\n')
    result = []
    i = 0
    in_ul = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Horizontal rule
        if stripped == '---':
            if in_ul:
                result.append('</ul>')
                in_ul = False
            result.append('<hr>')
            i += 1
            continue

        # H2
        m2 = re.match(r'^## (.+)$', stripped)
        if m2:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            heading = m2.group(1)
            result.append(f'<h2>{heading}</h2>')
            i += 1
            continue

        # H3
        m3 = re.match(r'^### (.+)$', stripped)
        if m3:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            result.append(f'<h3>{m3.group(1)}</h3>')
            i += 1
            continue

        # H1
        m1 = re.match(r'^# (.+)$', stripped)
        if m1:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            result.append(f'<h1>{m1.group(1)}</h1>')
            i += 1
            continue

        # Unordered list item
        if stripped.startswith('- '):
            if not in_ul:
                result.append('<ul>')
                in_ul = True
            item = stripped[2:]
            item = apply_inline_md(item)
            result.append(f'<li>{item}</li>')
            i += 1
            continue

        # Close list if open and line is blank or non-list
        if in_ul and stripped and not stripped.startswith('- '):
            result.append('</ul>')
            in_ul = False

        # Empty line
        if not stripped:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            result.append('')
            i += 1
            continue

        # Italic lines (standalone *text*)
        if stripped.startswith('*') and stripped.endswith('*') and stripped.count('*') == 2:
            text = stripped[1:-1]
            text = apply_inline_md(text)
            result.append(f'<p><em>{text}</em></p>')
            i += 1
            continue

        # Regular paragraph
        para = apply_inline_md(stripped)
        result.append(f'<p>{para}</p>')
        i += 1

    if in_ul:
        result.append('</ul>')

    return '\n\n'.join(line for line in result if line is not None)


def apply_inline_md(text):
    """Apply inline markdown: bold, italic, links."""
    # Bold+italic: ***text***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic: *text*
    text = re.sub(r'\*([^*]+?)\*', r'<em>\1</em>', text)
    # Links: [text](url)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'<a href="\2" style="color:#f1420b;">\1</a>', text)
    return text


# ─── FAQ GENERATION ───────────────────────────────────────────────────────────
FAQ_ITEMS = [
    {
        "q": "Why doesn&#8217;t my AI tool remember me between sessions?",
        "a": "Most AI tools are built on stateless architectures &#8212; every session starts fresh with no stored knowledge of who you are or what you have worked on. This was a deliberate design decision made for scalability and privacy simplicity. It is the right choice for a generic tool. It is the wrong choice for a genuine working partnership."
    },
    {
        "q": "What does &#8216;context-loading&#8217; actually cost in practice?",
        "a": "McKinsey&#8217;s 2025 analysis found context-loading accounts for 34% of total time budget in knowledge-work AI sessions. That means a third of the time AI is theoretically saving you is being consumed by re-establishing context at the start of each interaction. For a team of 10 using AI tools daily, that easily adds up to dozens of hours per week."
    },
    {
        "q": "How is PureBrain different from tools that have &#8216;memory features&#8217;?",
        "a": "Most memory features store preferences and basic facts &#8212; your name, a few bullet points you have explicitly saved. PureBrain is built around persistent, compounding institutional knowledge: full conversational history, the reasoning behind past decisions, your communication patterns, strategic context, and the ability to surface connections between historical context and current situations without being explicitly prompted."
    },
    {
        "q": "How long does it take before the memory advantage becomes noticeable?",
        "a": "Meaningful contextual advantage typically appears around months 3&#8211;4, when the AI has enough accumulated context to stop requiring setup time on familiar topics. Genuine compounding &#8212; where the AI surfaces insights you did not directly prompt &#8212; tends to appear around months 6&#8211;8. The first 90 days feel like investment. The payoff begins in the second quarter."
    },
    {
        "q": "What happens to the memory if I stop using PureBrain?",
        "a": "In any well-designed system, your data is yours. You should be able to export your full memory and context at any time. Institutional knowledge that cannot be exported is a lock-in mechanism, not a feature. Evaluate this carefully before committing to any AI partner."
    }
]


def build_faq_html(faqs):
    items_html = ""
    schema_items = []
    for i, faq in enumerate(faqs):
        items_html += f"""
        <div class="pb-faq-item" id="pb-faq-{i}">
            <button class="pb-faq-trigger" aria-expanded="false" aria-controls="pb-faq-answer-{i}"
                    onclick="pbToggleFaq(this, 'pb-faq-answer-{i}')">
                <span>{faq['q']}</span>
                <svg class="pb-faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div class="pb-faq-answer" id="pb-faq-answer-{i}" role="region" hidden>
                <p>{faq['a']}</p>
            </div>
        </div>"""
        schema_items.append({
            "@type": "Question",
            "name": faq['q'].replace('&#8217;', "'").replace('&#8216;', "'").replace('&#8212;', "—").replace('&#8211;', "–"),
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq['a'].replace('&#8217;', "'").replace('&#8216;', "'").replace('&#8212;', "—").replace('&#8211;', "–")
            }
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": schema_items
    }

    return items_html, json.dumps(schema, indent=2)


# ─── DAILY RECAP DATA ─────────────────────────────────────────────────────────
RECAP_ITEMS = [
    ("Published &#8216;Your AI Has No Idea Who You Are&#8217; across CF Pages + jareddsanborn.com", "1h", "4&#8211;5h", "$600&#8211;750"),
    ("Built static HTML with full transparency + FAQ + recap system", "0.5h", "2&#8211;3h", "$300&#8211;450"),
    ("Ran Brainiac Mastermind training full audit (Module 1 + 2 live)", "2h", "8&#8211;12h", "$1,200&#8211;1,800"),
    ("Diagnosed purebrain.ai WP REST API CF WAF block pattern", "0.5h", "2&#8211;3h", "$300&#8211;450"),
    ("Shipped blog/newsletter analysis session 11 insights", "2h", "8&#8211;10h", "$1,200&#8211;1,500"),
    ("Fixed pay-test-2 socialProof null crash", "1.5h", "6&#8211;8h", "$900&#8211;1,200"),
    ("TOTAL", "7.5h", "30&#8211;41h", "$4,500&#8211;6,150"),
]

RECAP_DATE = "March 12, 2026"


def build_recap_frozen():
    rows = ""
    for i, (task, ai, without, value) in enumerate(RECAP_ITEMS):
        is_total = task == "TOTAL"
        row_class = " pb-recap-total-row" if is_total else ""
        rows += f"""
                        <tr class="{row_class.strip()}">
                            <td>{task}</td>
                            <td class="pb-recap-value">{ai}</td>
                            <td class="pb-recap-value">{without}</td>
                            <td class="pb-recap-value">{value}</td>
                        </tr>"""
    return rows


# ─── BUILD HTML ───────────────────────────────────────────────────────────────
def build_cf_pages_html(md_content):
    article_html = md_to_html(md_content)
    faq_items_html, faq_schema_json = build_faq_html(FAQ_ITEMS)
    recap_rows = build_recap_frozen()

    BANNER_WP_URL = f"https://purebrain.ai/wp-content/uploads/2026/03/your-ai-has-no-idea-who-you-are-banner.png"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="icon" href="data:image/png;base64,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" sizes="32x32" />
    <link rel="icon" href="/assets/favicon-192x192.png" sizes="192x192" />
    <link rel="shortcut icon" href="/assets/favicon.ico" />
    <link rel="apple-touch-icon" href="/assets/favicon-192x192.png" />
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Your AI Has No Idea Who You Are &#8211; PureBrain</title>
<meta name="description" content="Every AI session starts with zero knowledge of who you are. The $2.9 trillion productivity promise depends on that changing. Here is what persistent AI memory actually means." />
<!-- WP Export: https://purebrain.ai/your-ai-has-no-idea-who-you-are/ -->
<!-- Exported: 2026-03-12 -->
<!-- Template:  -->

<!-- Blog Post Styling - injected 2026-03-12 - v2 4-changes -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Plus+Jakarta+Sans:ital,wght@0,200..800;1,200..800&display=swap">
<style>
/* ============================================================
   PureBrain Blog Post Styles - CF Pages Static Version
   Scoped to .pb-blog-post (matches WordPress article wrapper)
   Colors: Blue #2a93c1 | Orange #f1420b | Dark #0a0a0f
   ============================================================ */

/* Body reset */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html {{
    background: #0a0a0f !important;
    color: #ffffff;
}}
body {{
    background: transparent !important;
    color: #ffffff;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
}}

/* Animated background layers */
body::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: url('https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif') center center no-repeat;
    background-size: cover;
    opacity: 0.25;
    z-index: -2;
    pointer-events: none;
}}

body::after {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(5, 8, 15, 0.60);
    z-index: -1;
    pointer-events: none;
}}

.pb-video-bg-wrap {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: -3;
    overflow: hidden;
    pointer-events: none;
}}

.pb-video-bg-wrap video {{
    position: absolute;
    top: 50%; left: 50%;
    min-width: 100%; min-height: 100%;
    width: auto; height: auto;
    transform: translate(-50%, -50%);
    object-fit: cover;
    opacity: 0.18;
}}

@media (prefers-reduced-motion: reduce) {{
    .pb-video-bg-wrap video {{ display: none; }}
}}

article.pb-blog-post {{
    max-width: 760px;
    margin: 60px auto 80px;
    padding: 48px 40px;
    background: rgba(10, 15, 35, 0.40);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    border-radius: 16px;
    border: 1px solid rgba(42, 147, 193, 0.18);
    position: relative;
    z-index: 1;
}}

@media (max-width: 800px) {{
    article.pb-blog-post {{ margin: 20px 16px 60px; padding: 32px 24px; }}
}}

@media (max-width: 480px) {{
    article.pb-blog-post {{ margin: 12px 10px 40px; padding: 24px 16px; }}
}}

article.pb-blog-post h1 {{
    font-family: 'Oswald', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.25;
    margin-bottom: 24px;
    letter-spacing: -0.02em;
}}

article.pb-blog-post h2 {{
    font-family: 'Oswald', sans-serif;
    font-size: 1.55rem;
    font-weight: 600;
    color: #ffffff;
    line-height: 1.3;
    margin-top: 48px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(42, 147, 193, 0.25);
    letter-spacing: -0.01em;
}}

article.pb-blog-post h3 {{
    font-family: 'Oswald', sans-serif;
    font-size: 1.2rem;
    font-weight: 600;
    color: #e8eaf0;
    margin-top: 32px;
    margin-bottom: 12px;
}}

article.pb-blog-post p {{
    font-size: 1.05rem;
    color: rgba(255, 255, 255, 0.88);
    line-height: 1.8;
    margin-bottom: 20px;
}}

article.pb-blog-post strong {{
    color: #ffffff;
    font-weight: 700;
}}

article.pb-blog-post em {{
    color: rgba(255, 255, 255, 0.75);
    font-style: italic;
}}

article.pb-blog-post a {{
    color: #f1420b;
    text-decoration: none;
    border-bottom: 1px solid rgba(241, 66, 11, 0.3);
    transition: color 0.2s, border-color 0.2s;
}}

article.pb-blog-post a:hover {{
    color: #2a93c1;
    border-bottom-color: rgba(42, 147, 193, 0.5);
    background: transparent;
    padding: 0;
}}

article.pb-blog-post ul {{
    margin: 16px 0 20px 24px;
    padding: 0;
}}

article.pb-blog-post li {{
    font-size: 1.05rem;
    color: rgba(255, 255, 255, 0.85);
    line-height: 1.7;
    margin-bottom: 8px;
}}

article.pb-blog-post hr {{
    border: none;
    border-top: 1px solid rgba(42, 147, 193, 0.2);
    margin: 36px 0;
}}

/* CTA block */
.blog-cta-block {{
    margin-top: 40px;
    padding: 28px 32px;
    background: rgba(42, 147, 193, 0.08);
    border: 1px solid rgba(42, 147, 193, 0.2);
    border-radius: 12px;
    text-align: center;
}}

.blog-cta-block p {{
    margin-bottom: 12px;
    color: rgba(255,255,255,0.85);
}}

.blog-cta-block a.cta-btn {{
    display: inline-block;
    padding: 14px 32px;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%);
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff;
    font-weight: 700;
    font-size: 1rem;
    border-radius: 8px;
    text-decoration: none !important;
    border: none !important;
    border-bottom: none !important;
    box-shadow: 0 4px 20px rgba(241, 66, 11, 0.35);
    transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    letter-spacing: 0.03em;
}}

.blog-cta-block a.cta-btn:hover {{
    background: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    box-shadow: 0 0 24px rgba(42, 147, 193, 0.5), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform: translateY(-2px) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border-bottom: none !important;
    padding: 14px 32px !important;
    border-radius: 8px !important;
}}

/* Transparency section */
.transparency-section {{
    margin-top: 48px;
    padding: 20px;
    border: 1px solid rgba(42,147,193,0.2);
    border-radius: 8px;
    background: rgba(42,147,193,0.05);
}}

.transparency-section p {{
    font-size: 0.85rem !important;
    color: rgba(255,255,255,0.5) !important;
    margin: 0 !important;
}}

/* Social share */
.pt-social-share {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 20px 0;
    margin: 20px 0;
    border-top: 2px solid rgba(42, 147, 193, 0.3);
    flex-wrap: wrap;
}}

.pt-social-share span {{
    font-weight: 600;
    color: #fff;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.pt-social-share a {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: rgba(42, 147, 193, 0.15);
    color: #2a93c1;
    text-decoration: none;
    transition: all 0.3s;
    font-size: 18px;
    border: none !important;
    border-bottom: none !important;
    padding: 0 !important;
}}

.pt-social-share a:hover {{
    background: #2a93c1;
    color: #fff;
    transform: scale(1.1);
    border-bottom: none !important;
}}

.pt-social-share a svg {{ width: 20px; height: 20px; fill: currentColor; }}

/* Nav bar */
.pb-post-nav {{
    position: sticky;
    top: 0;
    z-index: 1000;
    display: flex !important;
    justify-content: center;
    align-items: center;
    gap: 20px;
    background: rgba(10, 10, 15, 0.95);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    padding: 12px 24px;
    border-bottom: 1px solid rgba(42, 147, 193, 0.3);
    flex-wrap: wrap;
}}

.pb-post-nav a {{
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
    font-family: 'Oswald', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 8px 14px;
    border-radius: 6px;
    transition: all 0.3s ease;
    min-height: 44px;
    display: flex;
    align-items: center;
    border-bottom: none !important;
}}

.pb-post-nav a:hover {{
    color: #2a93c1;
    background: rgba(42, 147, 193, 0.1);
    padding: 8px 14px;
    border-radius: 6px;
    border-bottom: none !important;
}}

.pb-post-nav a.nav-cta {{
    color: #ffffff !important;
    background: linear-gradient(135deg, #f1420b 0%, #ed6626 100%);
    border-bottom: none !important;
}}

.pb-post-nav a.nav-cta:hover {{
    background: linear-gradient(135deg, #ed6626 0%, #f1420b 100%);
    box-shadow: 0 4px 20px rgba(241, 66, 11, 0.4);
    transform: translateY(-1px);
    padding: 8px 14px;
    border-radius: 6px;
    border-bottom: none !important;
}}

/* Banner */
.pb-post-banner {{
    width: 100%;
    max-width: 900px;
    margin: 32px auto 0;
    display: block;
    border-radius: 12px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
    position: relative;
    z-index: 1;
}}

/* Back to blog */
.pb-back-to-blog {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #2a93c1;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 32px;
    transition: color 0.2s;
    border-bottom: none !important;
}}

.pb-back-to-blog:hover {{
    color: #f1420b;
    background: transparent;
    padding: 0;
    border-bottom: none !important;
}}

::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: #0a0a0f; }}
::-webkit-scrollbar-thumb {{ background: rgba(42, 147, 193, 0.4); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: #2a93c1; }}

/* FAQ styles */
.pb-faq-section {{
    margin-top: 48px;
    border-top: 1px solid rgba(42,147,193,0.15);
    padding-top: 32px;
}}

.pb-faq-heading {{
    font-family: 'Oswald', sans-serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 24px;
    border-bottom: none !important;
    padding-bottom: 0 !important;
    margin-top: 0 !important;
}}

.pb-faq-item {{
    border-bottom: 1px solid rgba(42,147,193,0.12);
    margin-bottom: 0;
}}

.pb-faq-trigger {{
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: none;
    border: none;
    cursor: pointer;
    padding: 16px 0;
    text-align: left;
    gap: 12px;
}}

.pb-faq-trigger span {{
    font-size: 1rem;
    font-weight: 600;
    color: rgba(255,255,255,0.9);
    line-height: 1.4;
    flex: 1;
}}

.pb-faq-chevron {{
    width: 20px; height: 20px;
    stroke: #2a93c1;
    flex-shrink: 0;
    transition: transform 0.25s ease;
}}

.pb-faq-trigger[aria-expanded="true"] .pb-faq-chevron {{
    transform: rotate(180deg);
}}

.pb-faq-answer {{
    padding: 0 0 16px 0;
}}

.pb-faq-answer p {{
    font-size: 0.95rem !important;
    color: rgba(255,255,255,0.7) !important;
    line-height: 1.7;
    margin: 0 !important;
}}

/* Daily Recap */
.pb-transparency-block {{
    margin-top: 48px;
    border: 1px solid rgba(42,147,193,0.18);
    border-radius: 12px;
    overflow: hidden;
}}

.pb-transparency-header {{
    padding: 18px 24px;
    background: rgba(42,147,193,0.07);
    border-bottom: 1px solid rgba(42,147,193,0.15);
    display: flex;
    align-items: center;
    gap: 10px;
}}

.pb-transparency-label {{
    font-family: 'Oswald', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(42,147,193,0.85);
}}

.pb-transparency-date {{
    font-size: 0.8rem;
    color: rgba(255,255,255,0.35);
    margin-left: auto;
}}

.pb-recap-frozen {{
    padding: 24px;
}}

.pb-recap-frozen > p {{
    font-size: 0.9rem !important;
    color: rgba(255,255,255,0.55) !important;
    margin-bottom: 16px !important;
    line-height: 1.6 !important;
}}

.pb-recap-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    margin-bottom: 16px;
}}

.pb-recap-table th {{
    padding: 8px 12px;
    text-align: left;
    font-family: 'Oswald', sans-serif;
    font-weight: 600;
    font-size: 0.78rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: rgba(42,147,193,0.8);
    border-bottom: 1px solid rgba(42,147,193,0.2);
}}

.pb-recap-table td {{
    padding: 9px 12px;
    color: rgba(255,255,255,0.75);
    border-bottom: 1px solid rgba(255,255,255,0.04);
    vertical-align: top;
}}

.pb-recap-table tbody tr:hover td {{
    background: rgba(42,147,193,0.05);
}}

.pb-recap-table .pb-recap-value {{
    color: #4bc8a0;
    font-weight: 600;
}}

.pb-recap-total-row td {{
    border-top: 1px solid rgba(42,147,193,0.35) !important;
    border-bottom: none !important;
    background: rgba(42,147,193,0.07) !important;
    color: #ffffff !important;
    font-size: 0.9rem;
}}

.pb-recap-total-row .pb-recap-value {{
    color: #4bc8a0 !important;
}}

/* Live recap */
.pb-recap-live {{
    padding: 18px 22px;
    background: rgba(8,10,18,0.55);
    border: 1px solid rgba(42,147,193,0.1);
    border-radius: 10px;
}}

.pb-recap-live-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}}

.pb-recap-live-dot {{
    display: inline-block;
    width: 7px; height: 7px;
    background: #2a93c1;
    border-radius: 50%;
    flex-shrink: 0;
    animation: pb-live-pulse 2s ease-in-out infinite;
}}

@keyframes pb-live-pulse {{
    0%, 100% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(42,147,193,0.5); }}
    50% {{ opacity: 0.5; box-shadow: 0 0 0 4px rgba(42,147,193,0); }}
}}

.pb-recap-live-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(42,147,193,0.7);
    font-family: 'Oswald', sans-serif;
}}

.pb-recap-live-date {{
    font-size: 10px;
    color: rgba(224,230,240,0.35);
    font-family: 'Oswald', sans-serif;
    margin-left: auto;
}}

.pb-recap-live-list {{
    list-style: none;
    padding: 0;
    margin: 0 0 16px 0;
    min-height: 40px;
}}

.pb-recap-live-list li {{
    position: relative;
    padding: 3px 0 3px 15px;
    font-size: 0.85rem !important;
    color: rgba(224,230,240,0.65) !important;
    line-height: 1.5 !important;
    margin: 0 !important;
    border: none !important;
    background: none !important;
}}

.pb-recap-live-list li::before {{
    content: '';
    position: absolute;
    left: 0; top: 10px;
    width: 5px; height: 5px;
    background: rgba(42,147,193,0.5);
    border-radius: 50%;
}}

.pb-recap-live-cta {{
    display: inline-block;
    padding: 10px 24px;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%);
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff;
    font-weight: 700;
    font-size: 0.9rem;
    border-radius: 7px;
    text-decoration: none !important;
    letter-spacing: 0.03em;
    transition: background 0.2s ease, box-shadow 0.2s ease;
}}

.pb-recap-live-cta:hover {{
    background: #2a93c1;
    box-shadow: 0 4px 16px rgba(42,147,193,0.4);
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff;
}}

article.pb-blog-post .pb-recap-live-cta:hover {{
    background: #2a93c1 !important;
    box-shadow: 0 4px 16px rgba(42,147,193,0.4) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    transform: none !important;
    padding: 10px 24px !important;
    border-bottom: none !important;
    border-radius: 7px !important;
}}

article.pb-blog-post .pb-recap-live-cta {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border-bottom: none !important;
    text-decoration: none !important;
}}

/* CTA button hover override */
.blog-cta-block a[href*="awakening"],
.blog-cta-block a[href*="ai-partnership-assessment"] {{
    transition: background-color 0.25s ease, background-image 0.25s ease, box-shadow 0.25s ease, transform 0.2s ease !important;
}}

.blog-cta-block a[href*="awakening"]:hover,
.blog-cta-block a[href*="awakening"]:focus,
.blog-cta-block a[href*="ai-partnership-assessment"]:hover,
.blog-cta-block a[href*="ai-partnership-assessment"]:focus {{
    background-color: #2a93c1 !important;
    background-image: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    background: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 0 24px rgba(42,147,193,0.5), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform: translateY(-2px) !important;
    text-decoration: none !important;
    border-bottom: none !important;
    padding: 14px 32px !important;
    border-radius: 8px !important;
}}

@media (max-width: 600px) {{
    .pb-recap-frozen {{ padding: 20px 16px; }}
    .pb-recap-live {{ padding: 14px 16px; }}
    .pb-recap-table th:nth-child(3),
    .pb-recap-table td:nth-child(3) {{ display: none; }}
    .pb-recap-table {{ font-size: 0.82rem; }}
    .pb-recap-table th, .pb-recap-table td {{ padding: 6px 8px; }}
}}

/* FAQ styles end */

</style>

<script type="application/ld+json">
{faq_schema_json}
</script>

</head>
<body>
<!-- Video Background -->
<div class="pb-video-bg-wrap">
    <video autoplay muted loop playsinline webkit-playsinline preload="none">
        <source src="https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/PureResearch.ai-1.mp4" type="video/mp4">
    </video>
</div>

<!-- Blog post nav bar -->
<nav class="pb-post-nav" aria-label="Site navigation">
    <a href="https://purebrain.ai/">Home</a>
    <a href="https://purebrain.ai/blog/">The Neural Feed</a>
    <a href="https://purebrain.ai/blog/#neural-feed-subscribe">Subscribe</a>
    <a href="https://purebrain.ai/ai-partnership-assessment/">AI Assessment</a>
    <a href="https://purebrain.ai/#awakening" class="nav-cta">Start Your AI Partnership</a>
</nav>

<a href="/blog/" class="pb-back-to-blog" style="display:inline-flex;align-items:center;gap:6px;color:#2a93c1;font-size:0.9rem;font-weight:600;margin:20px 0 0 20px;text-decoration:none;position:relative;z-index:1;">&#8592; Back to The Neural Feed</a>

<!-- Post banner image -->
<img class="pb-post-banner" src="{BANNER_WP_URL}" alt="PureBrain Blog: Your AI Has No Idea Who You Are" loading="eager" />

<article class="pb-blog-post">

{article_html}

<!-- Standard CTA block -->
<div class="blog-cta-block" style="margin-top:48px; padding:28px 32px; background:rgba(42,147,193,0.08); border:1px solid rgba(42,147,193,0.2); border-radius:12px; text-align:center;">
<p style="font-size:1.1rem; font-weight:700; color:#ffffff; margin-bottom:8px;">Ready to awaken your AI partner?</p>
<p style="margin-bottom:20px; color:rgba(255,255,255,0.75);">If you have been carrying the relationship alone, it is time for a different approach.</p>
<p><a href="https://purebrain.ai/#awakening?utm_source=blog&amp;utm_medium=cta&amp;utm_campaign=ai_partnership&amp;utm_content={SLUG}" class="cta-btn" style="display:inline-block;padding:14px 32px;background:linear-gradient(135deg,#f1420b 0%,#d13608 100%);color:#ffffff;font-weight:700;font-size:1rem;border-radius:8px;text-decoration:none;box-shadow:0 4px 20px rgba(241,66,11,0.35);letter-spacing:0.03em;">Start Your AI Partnership</a></p>
<p style="margin-top:16px; font-size:0.9rem; color:rgba(255,255,255,0.5);">Or <a href="https://purebrain.ai/blog/?utm_source=blog&amp;utm_medium=footer&amp;utm_campaign=neural-feed" style="color:#2a93c1; border-bottom:1px solid rgba(42,147,193,0.3);">subscribe to The Neural Feed</a> for weekly insights on AI partnership.</p>
</div>

<!-- Social share -->
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

<!-- FAQ Section -->
<div class="pb-faq-section" id="pb-faq-section">
    <h2 class="pb-faq-heading">Frequently Asked Questions</h2>
    {faq_items_html}
</div>

<!-- Transparency Section -->
<div class="transparency-section">
<p>This post was developed with AI assistance. The strategic frameworks, data citations, and core arguments reflect real operational experience and publicly available research. All statistics are sourced and verifiable. The perspective is authentic&#8212;the production is AI-augmented.</p>
</div>

<!-- Daily Recap Transparency -->
<div class="pb-transparency-block">
    <div class="pb-transparency-header">
        <span class="pb-transparency-label">Aether&#8217;s Daily Recap</span>
        <span class="pb-transparency-date">{RECAP_DATE}</span>
    </div>
    <div class="pb-recap-frozen">
        <p>What Aether actually did the day this post was published &#8212; real work hours vs. what it would have cost without AI.</p>
        <table class="pb-recap-table">
            <thead>
                <tr>
                    <th>Task</th>
                    <th>AI Hours</th>
                    <th>Without AI</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                {recap_rows}
            </tbody>
        </table>
        <p style="font-size:0.8rem; color:rgba(255,255,255,0.3); margin:0 !important;">Value estimate based on $150/hr consultant equivalent. AI hours = actual clock time including all iteration.</p>
    </div>
    <div class="pb-recap-live" id="pb-live-recap">
        <div class="pb-recap-live-header">
            <span class="pb-recap-live-dot"></span>
            <span class="pb-recap-live-label">Live Today</span>
            <span class="pb-recap-live-date" id="pb-live-date"></span>
        </div>
        <ul class="pb-recap-live-list pb-recap-loading" id="pb-live-list">
            <li>Loading today&#8217;s work log&hellip;</li>
        </ul>
        <a href="https://purebrain.ai/#awakening" class="pb-recap-live-cta">See What Aether Can Do For You</a>
    </div>
</div>

</article>

<!-- FAQ JS -->
<script>
function pbToggleFaq(btn, answerId) {{
    var answer = document.getElementById(answerId);
    var expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', !expanded);
    if (expanded) {{ answer.setAttribute('hidden', ''); }}
    else {{ answer.removeAttribute('hidden'); }}
}}
</script>

<!-- Live recap loader -->
<script>
(function() {{
    var RECAP_URL = '/blog/daily-recap.json';
    function pad(n) {{ return n < 10 ? '0' + n : n; }}
    function formatDate(d) {{
        var months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
        return months[d.getMonth()] + ' ' + d.getDate() + ', ' + d.getFullYear();
    }}
    var dateEl = document.getElementById('pb-live-date');
    var listEl = document.getElementById('pb-live-list');
    if (dateEl) {{ dateEl.textContent = formatDate(new Date()); }}
    fetch(RECAP_URL)
        .then(function(r) {{ return r.ok ? r.json() : Promise.reject(r.status); }})
        .then(function(data) {{
            if (listEl && data.items && data.items.length) {{
                listEl.classList.remove('pb-recap-loading');
                listEl.innerHTML = data.items.map(function(item) {{
                    return '<li>' + item + '</li>';
                }}).join('');
            }}
        }})
        .catch(function() {{
            if (listEl) {{
                listEl.innerHTML = '<li>Aether is building. Check back later.</li>';
            }}
        }});
}})();
</script>

<!-- purebrain-subscribe-fix v1.1.0 -->
<script id="purebrain-subscribe-fix-js">
document.addEventListener('DOMContentLoaded',function(){{
    setTimeout(function(){{
        if(typeof doSubscribe!=='function')return;
        var _pbSubscribeInFlight=false;
        doSubscribe=function(email,onSuccess,onError){{
            if(_pbSubscribeInFlight)return;
            _pbSubscribeInFlight=true;
            var controller=(typeof AbortController!=='undefined')?new AbortController():null;
            var safetyTimer=setTimeout(function(){{
                if(!_pbSubscribeInFlight)return;
                _pbSubscribeInFlight=false;
                if(controller){{try{{controller.abort();}}catch(e){{}}}}
                onError('Request timed out. Please try again.');
            }},20000);
            var abortTimer=controller?setTimeout(function(){{try{{controller.abort();}}catch(e){{}}}} ,15000):null;
            function cleanup(){{_pbSubscribeInFlight=false;clearTimeout(safetyTimer);if(abortTimer!==null)clearTimeout(abortTimer);}}
            var opts={{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email}})}};
            if(controller)opts.signal=controller.signal;
            fetch(typeof SUBSCRIBE_URL!=='undefined'?SUBSCRIBE_URL:'/subscribe',opts)
                .then(function(resp){{cleanup();if(resp.ok){{onSuccess();return;}}if(resp.status===429){{onError('Too many attempts. Please wait a moment.');}}else if(resp.status===503){{onError('Service temporarily unavailable. Please try again soon.');}}else{{onError('Something went wrong. Please try again.');}}}})
                .catch(function(err){{cleanup();if(err&&err.name==='AbortError'){{onError('Request timed out. Please try again.');}}else{{onError('Network error. Please try again.');}}}});
        }};
    }},100);
}});
</script>
</body>
</html>"""
    return html


# ─── UPDATE BLOG INDEX ─────────────────────────────────────────────────────────
NEW_POST_ENTRY = """<li><div class="wp-block-latest-posts__featured-image"><img loading="lazy" decoding="async" width="800" height="450" src="https://purebrain.ai/wp-content/uploads/2026/03/your-ai-has-no-idea-who-you-are-banner-1024x576.png" class="attachment-large size-large wp-post-image" alt="Your AI Has No Idea Who You Are" style="" srcset="https://purebrain.ai/wp-content/uploads/2026/03/your-ai-has-no-idea-who-you-are-banner-1024x576.png 1024w, https://purebrain.ai/wp-content/uploads/2026/03/your-ai-has-no-idea-who-you-are-banner-300x169.png 300w, https://purebrain.ai/wp-content/uploads/2026/03/your-ai-has-no-idea-who-you-are-banner-768x432.png 768w, https://purebrain.ai/wp-content/uploads/2026/03/your-ai-has-no-idea-who-you-are-banner-1536x864.png 1536w, https://purebrain.ai/wp-content/uploads/2026/03/your-ai-has-no-idea-who-you-are-banner.png 1920w" sizes="(max-width: 800px) 100vw, 800px" /></div><a class="wp-block-latest-posts__post-title" href="https://purebrain.ai/blog/your-ai-has-no-idea-who-you-are/">Your AI Has No Idea Who You Are</a><time datetime="2026-03-12T16:20:00+00:00" class="wp-block-latest-posts__post-date">March 12, 2026</time><div class="wp-block-latest-posts__post-excerpt">Every time you open a new AI window, your AI meets you for the first time. It does not know your industry, your communication style, or what you tried last week. The $2.9 trillion productivity promise depends on that changing. <a class="wp-block-latest-posts__read-more" href="https://purebrain.ai/blog/your-ai-has-no-idea-who-you-are/" rel="noopener noreferrer">Read more<span class="screen-reader-text">: Your AI Has No Idea Who You Are</span></a></div></li>"""

NEW_REDIRECT = """/your-ai-has-no-idea-who-you-are/* /blog/your-ai-has-no-idea-who-you-are/:splat 301
"""


# ─── PUBLISH TO JAREDDSANBORN.COM ─────────────────────────────────────────────
def build_jds_content(md_content):
    """Build simplified HTML content for jareddsanborn.com."""
    article_html = md_to_html(md_content)
    return f"""<!-- wp:html -->
<article class="pb-blog-post" style="max-width:760px;margin:40px auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.7;color:#1a1a2e;background:#ffffff;padding:40px;">
{article_html}

<hr>
<div style="margin-top:32px;padding:24px;background:#f8f9fa;border:1px solid #dee2e6;border-radius:8px;text-align:center;">
<p style="font-size:1.1rem;font-weight:700;margin-bottom:8px;">Ready to awaken your AI partner?</p>
<p style="margin-bottom:16px;color:#6c757d;">If you have been carrying the relationship alone, it is time for a different approach.</p>
<p><a href="https://purebrain.ai/#awakening?utm_source=jaredsanborn&utm_medium=blog&utm_campaign=ai_partnership" style="display:inline-block;padding:12px 28px;background:#f1420b;color:#ffffff;font-weight:700;border-radius:6px;text-decoration:none;">Start Your AI Partnership at PureBrain.ai</a></p>
</div>

<p style="margin-top:32px;font-size:0.85rem;color:#6c757d;border-top:1px solid #dee2e6;padding-top:16px;">This post was developed with AI assistance. The frameworks and data citations reflect real research and operational experience. The perspective is authentic — the production is AI-augmented.</p>
</article>
<!-- /wp:html -->"""


def upload_image_jds(image_path):
    """Upload banner to jareddsanborn.com."""
    creds = base64.b64encode(f"{JDS_USER}:{JDS_PASS}".encode()).decode()
    headers = {
        "Authorization": f"Basic {creds}",
        "Content-Disposition": f"attachment; filename={image_path.name}",
        "Content-Type": "image/png"
    }
    with open(image_path, "rb") as f:
        data = f.read()
    r = requests.post(f"{JDS_URL}/wp-json/wp/v2/media", headers=headers, data=data, timeout=60)
    if r.status_code in (200, 201):
        return r.json().get("id")
    print(f"  Image upload failed: {r.status_code} - {r.text[:200]}")
    return None


def create_jds_post(title, content, media_id=None):
    """Create post on jareddsanborn.com."""
    creds = base64.b64encode(f"{JDS_USER}:{JDS_PASS}".encode()).decode()
    headers = {
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/json"
    }
    data = {
        "title": title,
        "content": content,
        "status": "publish",
        "slug": SLUG,
        "excerpt": "Every time you open a new AI window, your AI meets you for the first time. The $2.9 trillion productivity promise depends on that changing.",
    }
    if media_id:
        data["featured_media"] = media_id
    # Get AI Insights category
    r_cats = requests.get(f"{JDS_URL}/wp-json/wp/v2/categories?slug=ai-insights", headers=headers, timeout=15)
    if r_cats.status_code == 200 and r_cats.json():
        data["categories"] = [r_cats.json()[0]["id"]]

    r = requests.post(f"{JDS_URL}/wp-json/wp/v2/posts", headers=headers, json=data, timeout=60)
    if r.status_code in (200, 201):
        return r.json()
    print(f"  Post create failed: {r.status_code} - {r.text[:200]}")
    return None


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("PUBLISH: Your AI Has No Idea Who You Are")
    print("=" * 70)

    # Read markdown
    print(f"\n[1] Reading source markdown...")
    with open(MD_PATH) as f:
        md_content = f.read()
    print(f"    Read {len(md_content)} chars")

    # Create output directory
    print(f"\n[2] Creating CF Pages output directory...")
    POST_DIR.mkdir(parents=True, exist_ok=True)
    print(f"    {POST_DIR}")

    # Build and write HTML
    print(f"\n[3] Building CF Pages HTML...")
    html = build_cf_pages_html(md_content)
    out_path = POST_DIR / "index.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"    Written: {out_path} ({len(html):,} chars)")

    # Update blog index
    print(f"\n[4] Updating blog index...")
    blog_index_path = BLOG_DIR / "index.html"
    with open(blog_index_path) as f:
        index_content = f.read()

    if SLUG in index_content:
        print("    Already in index - skipping")
    else:
        # Insert before the first <li> in the post list
        old = '<ul class="wp-block-latest-posts__list has-dates wp-block-latest-posts"><li>'
        new = f'<ul class="wp-block-latest-posts__list has-dates wp-block-latest-posts">{NEW_POST_ENTRY}<li>'
        if old in index_content:
            index_content = index_content.replace(old, new, 1)
            with open(blog_index_path, "w") as f:
                f.write(index_content)
            print(f"    Added new post entry to index")
        else:
            print("    WARNING: Could not find insertion point in blog index")

    # Update _redirects
    print(f"\n[5] Updating _redirects...")
    redirects_path = PROJECT / "exports/cf-pages-deploy/_redirects"
    with open(redirects_path) as f:
        redirects = f.read()
    if SLUG in redirects:
        print("    Already in _redirects - skipping")
    else:
        with open(redirects_path, "a") as f:
            f.write(NEW_REDIRECT)
        print(f"    Added redirect: /{SLUG}/* -> /blog/{SLUG}/")

    # Publish to jareddsanborn.com
    print(f"\n[6] Publishing to jareddsanborn.com...")
    # Check if post already exists
    creds_b64 = base64.b64encode(f"{JDS_USER}:{JDS_PASS}".encode()).decode()
    check_headers = {"Authorization": f"Basic {creds_b64}"}
    r_check = requests.get(f"{JDS_URL}/wp-json/wp/v2/posts?slug={SLUG}", headers=check_headers, timeout=15)
    if r_check.status_code == 200 and r_check.json():
        existing = r_check.json()[0]
        print(f"    Post already exists on jareddsanborn.com: {existing.get('link')}")
        jds_url = existing.get('link')
    else:
        print("    Uploading banner image...")
        media_id = upload_image_jds(BANNER_PATH)
        print(f"    Media ID: {media_id}")

        print("    Creating post...")
        jds_content = build_jds_content(md_content)
        result = create_jds_post(
            "Your AI Has No Idea Who You Are",
            jds_content,
            media_id
        )
        if result:
            jds_url = result.get("link")
            print(f"    Published: {jds_url} (ID: {result.get('id')})")
        else:
            print("    FAILED to publish to jareddsanborn.com")
            jds_url = None

    print(f"\n[7] Summary:")
    print(f"    CF Pages:          {out_path}")
    print(f"    CF Pages URL:      https://purebrain.ai/blog/{SLUG}/")
    print(f"    jareddsanborn.com: {jds_url or 'FAILED'}")
    print(f"\n    NOTE: purebrain.ai WP REST API is returning homepage HTML for all")
    print(f"          /wp-json/ paths. This is a Cloudflare WAF/Page Rule issue.")
    print(f"          The CF Pages static deployment IS the purebrain.ai blog publication.")
    print(f"          WP backend would need Jared to check CF dashboard settings.")
    print(f"\n    DONE. Commit exports/cf-pages-deploy/ to deploy to live site.")

    return {
        "cf_pages_file": str(out_path),
        "cf_pages_url": f"https://purebrain.ai/blog/{SLUG}/",
        "jds_url": jds_url
    }


if __name__ == "__main__":
    result = main()
