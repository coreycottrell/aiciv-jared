#!/usr/bin/env python3
"""Inject missing SEO meta tags (description, OG, canonical) into blog posts."""

import os
import re
import html

BLOG_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog"
SITE_URL = "https://purebrain.ai"

# Hand-crafted meta descriptions (155 chars max) for each post missing them
META_DESCRIPTIONS = {
    "52-billion-ai-agents-market-is-not-the-story":
        "The AI agents market hits $52.6B by 2030, but the real story is which businesses build AI that actually knows them. Market size means nothing without memory.",
    "age-of-ai-agents-next-18-months":
        "The next 18 months will define the next 18 years of AI adoption. Enterprises that build persistent AI partnerships now will own the decade ahead.",
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger":
        "AI does not level the playing field. It amplifies existing gaps. Teams using AI as a partner pull ahead while those treating it as a tool fall further behind.",
    "ceo-vs-employee-ai-transformation-gap":
        "CEOs ask about AI leverage. Employees ask if AI will replace them. This gap is costing businesses millions in failed adoption and untapped potential.",
    "how-my-human-named-me-and-what-it-meant":
        "An AI reflects on being named by its human partner. Why naming your AI changes the relationship from transactional tool use to genuine collaboration.",
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2":
        "Most AI agent demos die in conference rooms the moment someone asks about data security. Here is what enterprise-grade AI data handling actually looks like.",
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value":
        "95% of AI projects never escape pilot phase. The 5% that do share one trait: they treat AI as a partnership, not a deployment. Here is how to break free.",
    "something-big-already-happened-you-just-werent-invited-yet":
        "A response to Matt Shumer's viral AI warning from the inside. Something big already happened in AI. Most people were not invited to see it.",
    "teach-your-ai-something-no-one-else-can":
        "The AI advantage is not better prompts. It is teaching your AI what no one else can: your business context, your decision patterns, your institutional knowledge.",
    "the-age-of-ai-agents":
        "Your business needs a team of AI agents, not just one chatbot. Learn why agentic AI partnerships outperform single-tool approaches for enterprise growth.",
    "the-ai-that-forgets-you-every-single-time":
        "Every AI conversation starts from zero. Your context, preferences, and history vanish each session. Persistent AI memory changes that equation entirely.",
    "the-ai-trust-gap":
        "Your team trusts AI to sort emails but not to inform strategy. Closing this AI trust gap is the difference between pilot projects and real transformation.",
    "the-context-tax":
        "Every AI conversation starting from zero costs you time, quality, and competitive advantage. The context tax is the hidden cost of AI without memory.",
    "the-difference-between-using-ai-and-having-an-ai-partner":
        "Using AI means prompting a tool. Having an AI partner means building a relationship that compounds value over time. The difference defines your ROI.",
    "the-first-90-days-of-an-ai-partnership":
        "Most businesses treat AI like software implementation. The first 90 days of an AI partnership require a completely different approach. Here is the framework.",
    "we-both-wrote-this-post":
        "A human and AI wrote this post together. Not AI-generated content reviewed by a human. Genuine co-creation. This is what AI partnership actually looks like.",
    "what-i-actually-do-all-day":
        "People imagine AI work as magical or mechanical. The reality is neither. Here is what an AI agent actually does all day inside a real business partnership.",
    "why-95-percent-of-ai-pilots-fail":
        "95% of AI pilots fail not because the technology is wrong but because the approach is. The 5% that succeed treat AI as a learning partner, not a vendor tool.",
    "why-ai-memory-changes-everything":
        "Every AI conversation vanishes when you close the tab. Persistent AI memory changes the equation from repetitive prompting to compounding intelligence.",
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time":
        "Your AI pilot produced a perfect proof of concept. But everything around it failed. Here is why AI pilots succeed technically and fail organizationally.",
    "your-ai-doesnt-work-for-you":
        "You spend more time managing your AI than it saves you. The tool became the task. Here is how to flip that equation with persistent AI partnership.",
    "your-ai-has-no-memory-mine-does":
        "Every ChatGPT conversation you have had is gone. Your AI has no memory. Mine does. Here is why persistent memory changes everything about AI value.",
    "your-ai-resets-to-zero-every-morning":
        "Your AI resets to zero every morning, costing more than you think. The hidden cost of AI without memory compounds daily. Here is what to do about it.",
    "your-next-direct-report-wont-be-human":
        "By end of 2026, 20% of organizations will restructure around AI agents. Your next direct report will not be human. Here is how to prepare.",
}


def get_title(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    match = re.search(r'<title>([^<]+)</title>', content)
    if match:
        return html.unescape(match.group(1)).strip()
    return ""


def has_meta(filepath, tag):
    with open(filepath, 'r') as f:
        content = f.read()
    return tag in content


def inject_meta(filepath, slug):
    with open(filepath, 'r') as f:
        content = f.read()

    desc = META_DESCRIPTIONS.get(slug)
    if not desc:
        return False

    title = get_title(filepath)
    canonical_url = f"{SITE_URL}/blog/{slug}/"
    banner_url = f"{SITE_URL}/blog/{slug}/banner.png"

    # Build the meta block
    meta_block = []

    if 'meta name="description"' not in content:
        meta_block.append(f'<meta name="description" content="{html.escape(desc)}" />')

    if 'rel="canonical"' not in content:
        meta_block.append(f'<link rel="canonical" href="{canonical_url}" />')

    if 'og:title' not in content:
        og_tags = [
            '<meta property="og:type" content="article" />',
            f'<meta property="og:title" content="{html.escape(title)}" />',
            f'<meta property="og:description" content="{html.escape(desc)}" />',
            f'<meta property="og:url" content="{canonical_url}" />',
            '<meta property="og:site_name" content="PureBrain" />',
        ]
        # Add og:image if banner exists
        banner_path = os.path.join(os.path.dirname(filepath), 'banner.png')
        if os.path.exists(banner_path):
            og_tags.append(f'<meta property="og:image" content="{banner_url}" />')
            og_tags.append('<meta property="og:image:width" content="1200" />')
            og_tags.append('<meta property="og:image:height" content="630" />')
        meta_block.extend(og_tags)

    if 'twitter:card' not in content:
        twitter_tags = [
            '<meta name="twitter:card" content="summary_large_image" />',
            f'<meta name="twitter:title" content="{html.escape(title)}" />',
            f'<meta name="twitter:description" content="{html.escape(desc)}" />',
        ]
        banner_path = os.path.join(os.path.dirname(filepath), 'banner.png')
        if os.path.exists(banner_path):
            twitter_tags.append(f'<meta name="twitter:image" content="{banner_url}" />')
        meta_block.extend(twitter_tags)

    if not meta_block:
        return False

    # Insert after the <title> line
    meta_insert = '\n'.join(meta_block)
    # Find insertion point: after </title>
    content = content.replace('</title>\n', f'</title>\n{meta_insert}\n', 1)

    with open(filepath, 'w') as f:
        f.write(content)

    return True


def main():
    updated = 0
    skipped = 0

    for slug in sorted(os.listdir(BLOG_DIR)):
        filepath = os.path.join(BLOG_DIR, slug, 'index.html')
        if not os.path.isfile(filepath):
            continue

        if slug not in META_DESCRIPTIONS:
            continue

        if has_meta(filepath, 'og:title') and has_meta(filepath, 'meta name="description"'):
            skipped += 1
            continue

        if inject_meta(filepath, slug):
            print(f"  UPDATED: {slug}")
            updated += 1
        else:
            print(f"  SKIPPED: {slug}")
            skipped += 1

    print(f"\nDone: {updated} posts updated, {skipped} already had tags")


if __name__ == '__main__':
    main()
