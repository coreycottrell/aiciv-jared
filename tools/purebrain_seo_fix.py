#!/usr/bin/env python3
"""
PureBrain SEO Fix — All Key Public Pages
Applies Yoast SEO meta, OG/Twitter tags, excerpts, and featured images.
Date: 2026-02-27
Agent: full-stack-developer

Does NOT modify page content — only meta fields, featured_media, and excerpt.
"""

import os, sys, time, json
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

BASE = 'https://purebrain.ai/wp-json/wp/v2'
AUTH = HTTPBasicAuth('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD'))

MEDIA_URLS = {
    80:  'https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif',
    694: 'https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg',
    793: 'https://purebrain.ai/wp-content/uploads/2026/02/ai-tool-stack-calculator-og.png',
    997: 'https://purebrain.ai/wp-content/uploads/2026/02/amplify-founder-scaled.jpg',
}

# -----------------------------------------------------------------------
# PAGE DEFINITIONS
# Each entry: page_id -> dict of fields to set
#   excerpt        -> string (plain text)
#   featured_media -> int (media ID)
#   yoast_title    -> string (SEO title)
#   yoast_metadesc -> string
#   og_title       -> string
#   og_desc        -> string
#   og_image       -> string (URL)
#   og_image_id    -> int
#   twitter_title  -> string (mirrors og_title)
#   twitter_desc   -> string (mirrors og_desc)
#   twitter_image  -> string (URL, mirrors og_image)
#   twitter_image_id -> int
# -----------------------------------------------------------------------

PAGES = {

    # 1. Homepage — only needs excerpt
    11: {
        'excerpt': "PureBrain is your AI executive team — 23 department heads running marketing, sales, legal, finance, engineering, and operations 24/7. Not a chatbot. A full organizational structure with permanent memory that compounds intelligence over time.",
    },

    # 2. Blog Index
    319: {
        'featured_media': 694,
        'yoast_title':    "The Neural Feed — AI Partnership Blog | PureBrain.ai",
        'yoast_metadesc': "Insights on AI partnership, business automation, and the future of human-AI collaboration. Published daily by PureBrain's AI team and founder Jared Sanborn.",
        'og_title':       "The Neural Feed — Where AI Meets Business Reality",
        'og_desc':        "Daily insights on AI partnership, multi-agent AI systems, and building businesses with AI executive teams. From the PureBrain team.",
        'og_image':       MEDIA_URLS[694],
        'og_image_id':    694,
        'excerpt':        "The Neural Feed is PureBrain's daily blog covering AI partnership, business automation, multi-agent systems, and the future of human-AI collaboration.",
    },

    # 3. Calculator
    777: {
        'og_title': "Free AI Tool Stack Calculator — See What 195+ AI Tools Really Cost",
        'og_desc':  "Calculate the true cost of your AI tool stack across 35 categories. See how PureBrain replaces 195+ tools with one AI executive team. Free calculator.",
        'og_image': MEDIA_URLS[793],
        'og_image_id': 793,
        'excerpt':  "Calculate the true cost of your AI tool stack across 35 categories and 195+ tools. See the SaaSpocalypse data and discover how PureBrain replaces your entire tool stack.",
    },

    # 4-11. Comparison pages
    752: {
        'og_title': "PureBrain vs Every AI Tool — Comprehensive Comparison",
        'og_desc':  "See how PureBrain's 23-department AI team compares to ChatGPT, Claude, Copilot, Gemini, and more. Not a chatbot comparison — an organizational comparison.",
        'og_image': MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':  "Compare PureBrain's AI executive team against ChatGPT, Claude, Copilot, Gemini, Jasper, Perplexity, DeepSeek, and Custom GPTs.",
    },
    753: {
        'og_title': "PureBrain vs ChatGPT — Why a Chat Window Isn't an Executive Team",
        'og_desc':  "ChatGPT answers questions. PureBrain runs your business. Compare a chatbot to a 23-department AI organization with permanent memory.",
        'og_image': MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':  "PureBrain vs ChatGPT: Compare a single chat interface to a full AI organizational structure with 23 departments, permanent memory, and 24/7 operations.",
    },
    754: {
        'og_title': "PureBrain vs Claude — From Conversation to Complete Operations",
        'og_desc':  "Claude is brilliant at conversation. PureBrain orchestrates 23 departments. See why a great AI model isn't the same as an AI executive team.",
        'og_image': MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':  "PureBrain vs Claude: While Claude excels at conversation, PureBrain orchestrates 23 AI departments with permanent memory and continuous operations.",
    },
    755: {
        'og_title': "PureBrain vs Microsoft Copilot — Copilot Assists. PureBrain Operates.",
        'og_desc':  "Copilot helps with Office tasks. PureBrain runs marketing, sales, legal, finance, and engineering 24/7. See the difference between assistance and operations.",
        'og_image': MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':  "PureBrain vs Microsoft Copilot: Compare document assistance to full business operations across 23 departments.",
    },
    756: {
        'og_title': "PureBrain vs Custom GPTs — Single Bots vs an AI Organization",
        'og_desc':  "Custom GPTs do one thing. PureBrain coordinates 23 departments with shared memory. See why an org chart beats a menu of chatbots.",
        'og_image': MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':  "PureBrain vs Custom GPTs: Compare isolated single-purpose bots to a coordinated 23-department AI organization with shared memory.",
    },
    757: {
        'og_title': "PureBrain vs DeepSeek — Raw Intelligence vs Organizational Power",
        'og_desc':  "DeepSeek is a powerful model. PureBrain is a powered organization. See why model intelligence alone doesn't run a business.",
        'og_image': MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':  "PureBrain vs DeepSeek: Compare a powerful language model to a complete AI organizational structure with 23 departments.",
    },
    758: {
        'og_title': "PureBrain vs Gemini — Google's AI vs Your AI Executive Team",
        'og_desc':  "Gemini is Google's AI assistant. PureBrain is your AI executive team. Compare a search companion to 23-department business operations.",
        'og_image': MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':  "PureBrain vs Gemini: Compare Google's AI assistant to a full AI organizational structure running your business 24/7.",
    },
    759: {
        'og_title': "PureBrain vs Jasper — Marketing Content vs Complete Business Operations",
        'og_desc':  "Jasper writes marketing copy. PureBrain runs 23 departments including marketing. See why content generation isn't business operations.",
        'og_image': MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':  "PureBrain vs Jasper: Compare a marketing content tool to a complete AI executive team covering all 23 business functions.",
    },
    760: {
        'og_title': "PureBrain vs Perplexity — Search Answers vs Business Intelligence",
        'og_desc':  "Perplexity finds information. PureBrain acts on it across 23 departments. See the difference between research and operations.",
        'og_image': MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':  "PureBrain vs Perplexity: Compare an AI search engine to a full AI organizational structure with permanent memory and 24/7 operations.",
    },

    # 12-18. Other key pages
    284: {
        'yoast_title': "AI Partnership Readiness Assessment | PureBrain.ai",
        'og_title':    "Are You Ready for an AI Partnership? Take the Assessment",
        'og_desc':     "Free 2-minute assessment to discover your AI partnership readiness score. See where you stand and what PureBrain can do for your business.",
        'og_image':    MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':     "Take the free AI Partnership Readiness Assessment to discover your score and see how PureBrain's AI executive team can transform your business operations.",
    },
    577: {
        'og_title': "AI Partnership Qualification — Are You Ready for PureBrain?",
        'og_desc':  "Discover if your business is ready for an AI executive team. Our qualification process ensures PureBrain is the right fit for your operations.",
        'excerpt':  "Qualify for AI partnership with PureBrain. Our review process ensures you're ready to leverage a 23-department AI executive team.",
    },
    731: {
        'og_title': "Meet Aether — The AI Behind PureBrain",
        'og_desc':  "Aether is the AI intelligence powering PureBrain. Learn about the technology, philosophy, and team behind your AI executive partner.",
        'excerpt':  "Meet Aether, the AI intelligence at the heart of PureBrain. Learn about the multi-agent architecture and philosophy behind your AI executive team.",
    },
    794: {
        'yoast_title': "Why PureBrain | AI Partnership vs AI Platforms",
        'og_title':    "Why PureBrain? Because AI Tools Don't Run Your Business",
        'og_desc':     "The difference between AI tools and AI partnership. PureBrain doesn't help you work — it works for you. 23 departments, permanent memory, 24/7 operations.",
        'excerpt':     "Discover why PureBrain's AI partnership model outperforms every AI platform. Not a tool you use — a team that works for you.",
    },
    923: {
        'og_title': "Partner Program — Grow With PureBrain",
        'og_desc':  "Join PureBrain's partner program. Offer your clients AI executive teams and earn recurring revenue on every partnership you refer.",
        'excerpt':  "PureBrain's partner program lets agencies, consultants, and advisors offer AI executive teams to their clients.",
    },
    929: {
        'og_title': "Our Mission, Vision & Values — Pure Technology",
        'og_desc':  "Pure Technology exists to make AI partnership accessible to every business. Our mission, vision, and values guide everything we build.",
        'excerpt':  "Pure Technology's mission, vision, and values. We believe every business deserves an AI executive team — not just enterprises.",
    },
    405: {
        'yoast_title': "The Complete Guide to AI Partnership | PureBrain.ai",
        'og_title':    "The Complete Guide to AI Partnership — From First Session to Full Operations",
        'og_desc':     "Everything you need to know about AI partnership. How PureBrain works, what to expect, and how 23 AI departments transform your business.",
        'og_image':    MEDIA_URLS[694],
        'og_image_id': 694,
        'excerpt':     "The complete guide to AI partnership with PureBrain. Learn how 23 AI department heads transform every function of your business.",
    },
    620: {
        'featured_media': 694,
        'og_title':       "The AI Partnership Audit — See What PureBrain Can Do For You",
        'og_desc':        "Our free audit shows exactly which business functions PureBrain can automate and the projected impact on your operations.",
        'excerpt':        "Get a free AI partnership audit showing which of your 12 core business functions PureBrain can transform.",
    },
    700: {
        'og_title': "The Neural Feed Archives — Past Insights on AI Partnership",
        'og_desc':  "Browse the complete archive of PureBrain's AI partnership insights, business automation strategies, and human-AI collaboration stories.",
        'excerpt':  "The Neural Feed archives — browse all past insights on AI partnership, business automation, and human-AI collaboration.",
    },
    800: {
        'featured_media': 694,
        'og_title':       "Migration Portal — Bring Your AI History to PureBrain",
        'og_desc':        "Import your ChatGPT, Claude, or Gemini conversation history into PureBrain. Your AI partner starts with your full context.",
        'excerpt':        "Migrate your AI conversation history from ChatGPT, Claude, or Gemini into PureBrain's permanent memory system.",
    },
    816: {
        'featured_media': 694,
        'og_title':       "Free AI Website Analysis — See Your Site Through AI Eyes",
        'og_desc':        "Get a comprehensive AI-powered analysis of your website's performance, SEO, content, and conversion potential. Free from PureBrain.",
        'excerpt':        "Free AI website analysis from PureBrain. See your site's performance, SEO health, content quality, and conversion optimization opportunities.",
    },
    860: {
        'og_title': "AI Website Execution — Turn Analysis Into Results",
        'og_desc':  "PureBrain implements the improvements identified in your website analysis. Design, content, SEO, and conversion optimization executed by AI.",
        'excerpt':  "PureBrain's AI website execution service turns analysis into results — design, content, SEO, and conversion improvements implemented.",
    },
    970: {
        'featured_media': 694,
        'yoast_title':    "What We Built vs What It Would Have Cost | PureBrain.ai",
        'yoast_metadesc': "See the real cost comparison: what Pure Technology built with PureBrain vs what it would cost with traditional hiring. The numbers speak for themselves.",
        'og_title':       "The Real Cost of Building Without AI — A Pure Technology Case Study",
        'og_desc':        "Pure Technology built an entire business infrastructure with PureBrain that would have cost millions with traditional teams. See the numbers.",
        'excerpt':        "A real cost comparison showing what Pure Technology built with PureBrain versus what it would have cost with traditional hiring and agencies.",
    },
    987: {
        'featured_media': 997,
        'yoast_title':    "You've Been Invited — PureBrain.ai",
        'yoast_metadesc': "You've received an exclusive invitation to PureBrain. Join the founders already running their businesses with a 23-department AI executive team.",
        'og_title':       "You've Been Invited to PureBrain",
        'og_desc':        "Exclusive access to PureBrain's AI executive team. 23 departments running your business 24/7 with permanent memory. Your invitation is waiting.",
        'og_image':       MEDIA_URLS[997],
        'og_image_id':    997,
        'excerpt':        "Exclusive invitation to PureBrain — your AI executive team with 23 departments, permanent memory, and 24/7 operations.",
    },
}


def build_payload(cfg):
    """Convert config dict into a WP REST API payload."""
    payload = {}
    meta = {}

    if 'featured_media' in cfg:
        payload['featured_media'] = cfg['featured_media']

    if 'excerpt' in cfg:
        payload['excerpt'] = cfg['excerpt']

    if 'yoast_title' in cfg:
        meta['_yoast_wpseo_title'] = cfg['yoast_title']

    if 'yoast_metadesc' in cfg:
        meta['_yoast_wpseo_metadesc'] = cfg['yoast_metadesc']

    if 'og_title' in cfg:
        meta['_yoast_wpseo_opengraph-title'] = cfg['og_title']
        meta['_yoast_wpseo_twitter-title'] = cfg.get('twitter_title', cfg['og_title'])

    if 'og_desc' in cfg:
        meta['_yoast_wpseo_opengraph-description'] = cfg['og_desc']
        meta['_yoast_wpseo_twitter-description'] = cfg.get('twitter_desc', cfg['og_desc'])

    if 'og_image' in cfg:
        meta['_yoast_wpseo_opengraph-image'] = cfg['og_image']
        meta['_yoast_wpseo_twitter-image'] = cfg.get('twitter_image', cfg['og_image'])

    if 'og_image_id' in cfg:
        # Yoast stores image IDs as strings in the REST API
        meta['_yoast_wpseo_opengraph-image-id'] = str(cfg['og_image_id'])
        meta['_yoast_wpseo_twitter-image-id'] = str(cfg.get('twitter_image_id', cfg['og_image_id']))

    if meta:
        payload['meta'] = meta

    return payload


def update_page(page_id, cfg):
    """PUT update to a single page. Returns (success, status_code, message)."""
    payload = build_payload(cfg)
    if not payload:
        return True, 0, "nothing to update"

    url = f"{BASE}/pages/{page_id}"
    r = requests.put(url, auth=AUTH, json=payload, timeout=30)

    if r.status_code in (200, 201):
        return True, r.status_code, "OK"
    else:
        try:
            err = r.json().get('message', r.text[:200])
        except Exception:
            err = r.text[:200]
        return False, r.status_code, err


def describe_changes(cfg):
    """Human-readable summary of what will be changed."""
    lines = []
    if 'featured_media' in cfg:
        lines.append(f"featured_media={cfg['featured_media']}")
    if 'excerpt' in cfg:
        lines.append("excerpt")
    if 'yoast_title' in cfg:
        lines.append("yoast_title")
    if 'yoast_metadesc' in cfg:
        lines.append("yoast_metadesc")
    if 'og_title' in cfg:
        lines.append("og_title+twitter_title")
    if 'og_desc' in cfg:
        lines.append("og_desc+twitter_desc")
    if 'og_image' in cfg:
        lines.append("og_image+twitter_image")
    return ", ".join(lines)


def main():
    results = []
    total = len(PAGES)
    success_count = 0
    fail_count = 0

    print(f"\nPureBrain SEO Fix — {total} pages to process\n")
    print("=" * 70)

    for page_id, cfg in PAGES.items():
        changes = describe_changes(cfg)
        print(f"  Page {page_id:>4} | {changes}")
        ok, status, msg = update_page(page_id, cfg)

        if ok:
            success_count += 1
            result_str = "SUCCESS"
            print(f"           -> {result_str} (HTTP {status})")
        else:
            fail_count += 1
            result_str = f"FAILED (HTTP {status}): {msg}"
            print(f"           -> {result_str}")

        results.append({
            'page_id': page_id,
            'changes': changes,
            'success': ok,
            'status':  status,
            'message': msg,
        })

        # Polite rate-limiting
        time.sleep(0.8)

    print("=" * 70)
    print(f"\nDone: {success_count} succeeded, {fail_count} failed out of {total} pages.\n")

    # Write summary report
    report_path = '/home/jared/projects/AI-CIV/aether/exports/seo-audit-fixes.md'
    with open(report_path, 'w') as f:
        f.write("# PureBrain SEO Audit Fixes\n\n")
        f.write(f"**Date**: 2026-02-27  \n")
        f.write(f"**Agent**: full-stack-developer  \n")
        f.write(f"**Pages processed**: {total}  \n")
        f.write(f"**Succeeded**: {success_count}  \n")
        f.write(f"**Failed**: {fail_count}  \n\n")
        f.write("---\n\n")
        f.write("## Results by Page\n\n")
        f.write("| Page ID | Fields Changed | Status | Notes |\n")
        f.write("|---------|---------------|--------|-------|\n")
        for r in results:
            status_str = "SUCCESS" if r['success'] else f"FAILED ({r['status']})"
            notes = r['message'] if not r['success'] else ""
            f.write(f"| {r['page_id']} | {r['changes']} | {status_str} | {notes} |\n")
        f.write("\n---\n\n")
        f.write("## Fields Updated Per Category\n\n")
        f.write("- **Homepage (11)**: excerpt only (already has full SEO)\n")
        f.write("- **Blog Index (319)**: featured_media, SEO title, meta desc, OG title/desc/image, excerpt\n")
        f.write("- **Calculator (777)**: OG title/desc/image, excerpt\n")
        f.write("- **Comparison pages (752-760)**: OG title/desc/image, excerpt\n")
        f.write("- **Other key pages (284,577,731,794,923,929,405,620,700,800,816,860,970,987)**: varies per page\n\n")
        f.write("## Notes\n\n")
        f.write("- Page content NOT modified — only meta fields, featured_media, and excerpt\n")
        f.write("- Twitter tags mirror OG tags on every page\n")
        f.write("- All OG/Twitter images use the same URL as the specified featured image media ID\n")

    print(f"Report saved to: {report_path}")
    return fail_count == 0


if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)
