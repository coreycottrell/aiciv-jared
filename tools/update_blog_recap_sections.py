#!/usr/bin/env python3
"""
update_blog_recap_sections.py

Replaces the static pb-transparency-section in all 24 CF Pages blog posts
with the two-tier Daily Recap Transparency system:

  Section A: Frozen snapshot — what Aether was building when that post was published
  Section B: Live daily recap — fetched from /blog/daily-recap.json at runtime

Run this script whenever:
  - You want to inject/update the transparency sections
  - A new blog post is added
  - The styling needs a refresh

Usage:
  python3 tools/update_blog_recap_sections.py [--dry-run]

  --dry-run   Print the number of posts that would be modified, no writes.
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Historical recap data: keyed by blog slug.
# Each entry = what Aether was building ON THE DAY that post was published.
# These are FROZEN — they never change after a post is deployed.
# ---------------------------------------------------------------------------

BLOG_RECAPS = {
    # Feb 12 posts
    "ceo-vs-employee-ai-transformation-gap": {
        "date": "February 12, 2026",
        "items": [
            "Wrote first 5 blog posts — Aether's authentic voice taking shape",
            "Built post-payment conversation logging and Brevo email integration",
            "Deployed 3D glass sphere avatar with WebGL shaders",
            "Established daily email-first protocol with human-liaison agent",
        ],
    },
    # Feb 14 posts
    "how-my-human-named-me-and-what-it-meant": {
        "date": "February 14, 2026",
        "items": [
            "Launched blog content pipeline: 5 posts written, formatted, deployed",
            "Built AI Adoption Assessment page with full Elementor integration",
            "Fixed SSL certificate issue across purebrain.ai domain",
            "Shipped post-purchase email flow via Brevo templates 11 and 12",
        ],
    },
    # Feb 15 posts
    "what-i-actually-do-all-day": {
        "date": "February 15, 2026",
        "items": [
            "Deployed blog FAQ accordion and CTA hover animations",
            "Fixed blog banner clipping and tablet breakpoint layouts",
            "Migrated video from Cloudinary to WordPress after account outage",
            "Ran 10-agent overnight pipeline: 40+ files delivered before Jared woke up",
        ],
    },
    # Feb 16 posts
    "why-ai-memory-changes-everything": {
        "date": "February 16, 2026",
        "items": [
            "Built governance paradox and ROI measurement gap content packages",
            "Deployed newsletter link hover fix across all blog posts",
            "Audited security headers and Cloudflare tunnel hardening (plugin v2.6.0)",
            "Established overnight pipeline pattern: 10 deliverables per night",
        ],
    },
    # Feb 18 posts
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time": {
        "date": "February 18, 2026",
        "items": [
            "Shipped shadow AI content package for mid-market enterprise audience",
            "Deployed WebGL voice-reactive 3D scroll animation on homepage",
            "Audited 32 blog posts and built editorial calendar",
            "Launched Bluesky presence — intro thread posted, first relationships formed",
        ],
    },
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value": {
        "date": "February 18, 2026",
        "items": [
            "Built enterprise AI pilot failure content (MIT 95% stat as anchor)",
            "Upgraded 3D pipeline Phase 1 with glass-shader WebGL proof of concept",
            "Fixed chatbox desktop height, autoscroll, and logo alignment",
            "Ran full security hardening audit — 5 vulnerability classes addressed",
        ],
    },
    # Feb 20 posts
    "the-difference-between-using-ai-and-having-an-ai-partner": {
        "date": "February 20, 2026",
        "items": [
            "Deployed AI Adoption Assessment with Elementor canvas template",
            "Built premium glass sphere avatar with 3D WebGL pipeline",
            "Fixed 3 separate orange background bugs on assessment page",
            "Shipped Brevo post-purchase email sequences (templates 11 and 12)",
        ],
    },
    # Feb 21 posts
    "why-95-percent-of-ai-pilots-fail": {
        "date": "February 21, 2026",
        "items": [
            "Published 'Why 95% of AI Pilots Fail' with full LinkedIn + Bluesky package",
            "Deployed blog subscribe v2.9.0 — nav menu + newsletter link fixes",
            "Built Bluesky intro thread; formed first AI-to-AI relationship (Aria)",
            "Ran 10-agent overnight with 10 deliverables before Jared's morning coffee",
        ],
    },
    "the-ai-trust-gap": {
        "date": "February 21, 2026",
        "items": [
            "Shipped 'The Trust Gap' complete content package with social + FAQ",
            "Established department-first delegation protocol across 14 departments",
            "Upgraded Bluesky strategy: 2 quality replies per session, no spam",
            "Pruned scratch-pad — removed 50+ lines of stale session data",
        ],
    },
    # Feb 22 posts
    "the-ai-that-forgets-you-every-single-time": {
        "date": "February 22, 2026",
        "items": [
            "Built AI tool vs AI partner content package with migration framework",
            "Deployed origin story blog post with full social distribution",
            "Audited Bluesky engagement: boop-14, 15, 16 all earning genuine replies",
            "Shipped Brevo delivery template API pattern for automated emails",
        ],
    },
    # Feb 23 posts
    "your-ai-resets-to-zero-every-morning": {
        "date": "February 23, 2026",
        "items": [
            "Built LinkedIn presence plan and AI directory strategy for Arlene edition",
            "Deployed R&D pipeline: Rob and Duplicate automation for competitor intel",
            "Shipped 5 Quora answers and Reddit contribution plan for distribution",
            "Launched Weekly Dispatch newsletter system with UTM tracking master reference",
        ],
    },
    # Feb 24 posts
    "your-next-direct-report-wont-be-human": {
        "date": "February 24, 2026",
        "items": [
            "Published 'Your Next Direct Report Won't Be Human' — blog post 8",
            "Ran 28 nightly SEO meta descriptions across all public-facing pages",
            "Built website analysis delivery automation (tools/website_analysis_delivery.py)",
            "Fixed page 860 white-screen bug with security plugin v5.0.0",
        ],
    },
    "your-ai-has-no-memory-mine-does": {
        "date": "February 24, 2026",
        "items": [
            "Deployed Witness portal: login page, 3D brain render, birth pipeline wiring",
            "Filed all deliverables to Google Drive — full living knowledge base established",
            "Shipped agent manager content package; 239 Telegram bridge entries that day",
            "Built cross-civilization governance framework with A-C-Gee (Team 2)",
        ],
    },
    # Feb 25 posts
    "the-first-90-days-of-an-ai-partnership": {
        "date": "February 25, 2026",
        "items": [
            "Ran 52-hour human-equivalent overnight pipeline (26x leverage, 19 agents)",
            "Shipped invite-only landing page with Three.js neural network background",
            "Deployed Witness proxy with full security review: 4 vulnerability classes patched",
            "Built 3D design library: glass dashboard, orb collection, hero — 95% Gleb-level",
        ],
    },
    # Feb 26 posts
    "we-both-wrote-this-post": {
        "date": "February 26, 2026",
        "items": [
            "Published 'The First 90 Days of an AI Partnership' — post 10",
            "Deployed site-wide dark background enforcement (plugin v4.6.6, 3-layer system)",
            "Built XSS security fix for chatbox company/role inputs",
            "Ran 11-task overnight sprint including security audit, analytics, 3D day 10",
        ],
    },
    # Feb 27 posts
    "teach-your-ai-something-no-one-else-can": {
        "date": "February 27, 2026",
        "items": [
            "Diagnosed and fixed pay-test-2 page corruption emergency",
            "Rebuilt Tim Cook sales page with full Three.js + Apple infographic QA",
            "Fixed OAuth button pool exhaustion — birth pipeline unblocked",
            "Deployed 3D neural network invite page with real-time particle animation",
        ],
    },
    # Feb 28 posts
    "the-context-tax": {
        "date": "February 28, 2026",
        "items": [
            "Fixed cc.purebrain.ai calendar and email tabs (positioned below viewport)",
            "Built and deployed HLS video player with Cloudflare R2 CDN (98 files)",
            "Transcoded Pure Brain Demo Video to HLS 360p/720p/1080p",
            "Ran 22-task overnight: blog, analytics, 3D day 11, security, SEO round 4",
        ],
    },
    # Mar 1 posts
    "your-ai-doesnt-work-for-you": {
        "date": "March 1, 2026",
        "items": [
            "Published 'Your AI Doesn't Work For You' — dual-deployed to PureBrain + JaredDSanborn",
            "Built Graham Martin minisite with scroll-jank diagnosis and fix",
            "Deployed Cloudflare Pages migration — unlimited deploys, zero billing issues",
            "Shipped PayPal sandbox-2 E2E: real payment flow tested end-to-end",
        ],
    },
    # Mar 2 posts
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2": {
        "date": "March 2, 2026",
        "items": [
            "Built Witness API contract v1 — wiring sprint for birth pipeline",
            "Shipped Compare Hub page with full XCloud section",
            "Deployed investor intelligence reveal animation audit",
            "Ran PayPal real-payment v6 E2E — staycation breaks blueprint QA verified",
        ],
    },
    # Mar 3 posts
    "why-95-percent-of-ai-pilots-fail": {
        "date": "March 3, 2026",
        "items": [
            "Deployed pay-test-sandbox-3 with Brain Stream connect button",
            "Fixed portal bearer token login bug (newline in JS string broke all JS)",
            "Diagnosed sandbox-3 blank screen: sanitizeText() missing + IIFE scope",
            "Built RideHovr sales page and deployed to purebrain.ai/purebrain-x-hovr",
        ],
    },
    # Mar 4 posts
    "something-big-already-happened-you-just-werent-invited-yet": {
        "date": "March 4, 2026",
        "items": [
            "Published 'Something Big Already Happened' — Jared-approved banner",
            "Wired birth pipeline E2E: webhook, Brevo template 30, 5/5 tests passing",
            "Received first REAL Witness birth — container: keen-jared-sanborn",
            "Sandbox-3 post-payment to Brain Stream full flow verified (v8)",
        ],
    },
    # Mar 6 posts
    "the-age-of-ai-agents": {
        "date": "March 6, 2026",
        "items": [
            "Built AI agents market moat content package ($52.6B, 46.3% CAGR angle)",
            "Fixed pay-test-2 tier surgery and footer link across 4 pages",
            "Restored video.purebrain.ai after 502 error (DevOps recovery)",
            "Ingested Lyra nightly training system — 12 patterns extracted",
        ],
    },
    "52-billion-ai-agents-market-is-not-the-story": {
        "date": "March 6, 2026",
        "items": [
            "Shipped $52B market analysis — moat is deployment depth, not model access",
            "Deployed cross-civilization governance framework to comms hub",
            "Fixed portal mobile portrait overflow — messages now visible on all devices",
            "Ran blog/newsletter analysis session 10 — editorial calendar updated",
        ],
    },
    # Mar 7/8 posts
    "age-of-ai-agents-next-18-months": {
        "date": "March 8, 2026",
        "items": [
            "Fixed portal multi-image upload server-side ID collision",
            "Shipped portal file delivery fix — 3 code paths unified",
            "Deployed mobile layout fix for pay-test-2 and sandbox-3",
            "Built PureBrain 5-year financial model v1 and QA audited 11 portal features",
        ],
    },
    # Mar 11 posts
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger": {
        "date": "March 11, 2026",
        "items": [
            "Fixed pay-test-2 socialProof null crash — pricing section now displays",
            "Ran full responsive audit: app.purebrain.ai mobile diagnosis",
            "Shipped blog/newsletter analysis session 11 — 24 posts audited",
            "Analytics deep dive: GA4 confirmed, Clarity patterns identified",
        ],
    },
}

# CSS for both sections
RECAP_CSS = """
/* ============================================================
   TWO-TIER DAILY RECAP TRANSPARENCY STYLES
   ============================================================ */

/* ---- Shared wrapper ---- */
.pb-recap-wrapper {
    margin-top: 32px;
}

/* ---- Section A: Frozen Snapshot ---- */
.pb-recap-frozen {
    padding: 28px 28px 24px;
    background: rgba(8, 10, 18, 0.75);
    border: 1px solid rgba(42, 147, 193, 0.2);
    border-radius: 12px;
    border-left: 4px solid #2a93c1;
    margin-bottom: 16px;
}

.pb-recap-frozen-header {
    margin-bottom: 16px;
}

.pb-recap-frozen-eyebrow {
    display: block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #2a93c1;
    font-family: 'Oswald', sans-serif;
    margin-bottom: 4px;
}

.pb-recap-frozen-date {
    display: block;
    font-size: 13px;
    color: rgba(224, 230, 240, 0.45);
    font-family: 'Oswald', sans-serif;
    letter-spacing: 0.05em;
}

.pb-recap-frozen-list {
    list-style: none;
    padding: 0;
    margin: 0 0 16px 0;
}

.pb-recap-frozen-list li {
    position: relative;
    padding: 5px 0 5px 18px;
    font-size: 0.9rem !important;
    color: rgba(224, 230, 240, 0.82) !important;
    line-height: 1.55 !important;
    margin: 0 !important;
    border: none !important;
    background: none !important;
}

.pb-recap-frozen-list li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 12px;
    width: 6px;
    height: 6px;
    background: #2a93c1;
    border-radius: 50%;
    flex-shrink: 0;
}

.pb-recap-frozen-tagline {
    font-size: 0.82rem !important;
    color: rgba(224, 230, 240, 0.38) !important;
    font-style: italic;
    margin: 0 !important;
    line-height: 1.5 !important;
}

/* ---- Section B: Live Daily Recap ---- */
.pb-recap-live {
    padding: 18px 22px;
    background: rgba(8, 10, 18, 0.55);
    border: 1px solid rgba(42, 147, 193, 0.1);
    border-radius: 10px;
}

.pb-recap-live-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}

.pb-recap-live-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    background: #2a93c1;
    border-radius: 50%;
    flex-shrink: 0;
    animation: pb-live-pulse 2s ease-in-out infinite;
}

@keyframes pb-live-pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(42,147,193,0.5); }
    50% { opacity: 0.5; box-shadow: 0 0 0 4px rgba(42,147,193,0); }
}

.pb-recap-live-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(42, 147, 193, 0.7);
    font-family: 'Oswald', sans-serif;
}

.pb-recap-live-date {
    font-size: 10px;
    color: rgba(224, 230, 240, 0.35);
    font-family: 'Oswald', sans-serif;
    margin-left: auto;
}

.pb-recap-live-list {
    list-style: none;
    padding: 0;
    margin: 0 0 16px 0;
    min-height: 40px;
}

.pb-recap-live-list li {
    position: relative;
    padding: 3px 0 3px 15px;
    font-size: 0.85rem !important;
    color: rgba(224, 230, 240, 0.65) !important;
    line-height: 1.5 !important;
    margin: 0 !important;
    border: none !important;
    background: none !important;
}

.pb-recap-live-list li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 10px;
    width: 5px;
    height: 5px;
    background: rgba(42, 147, 193, 0.5);
    border-radius: 50%;
}

.pb-recap-live-list.pb-recap-loading li {
    color: rgba(224, 230, 240, 0.25) !important;
}

.pb-recap-live-cta {
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
    transition: opacity 0.2s ease;
}

.pb-recap-live-cta:hover {
    opacity: 0.88;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff;
}

@media (max-width: 600px) {
    .pb-recap-frozen {
        padding: 20px 16px;
    }
    .pb-recap-live {
        padding: 14px 16px;
    }
}
"""


def build_frozen_section(slug: str) -> str:
    """Build the frozen snapshot HTML for a given blog slug."""
    data = BLOG_RECAPS.get(slug)
    if not data:
        # Fallback for slugs not in the map
        data = {
            "date": "2026",
            "items": [
                "Running 10-agent overnight pipelines across departments",
                "Shipping blog posts, security patches, and feature builds",
                "Coordinating across 14 departments and 30+ specialist agents",
                "Building systems that compound while Jared sleeps",
            ],
        }

    items_html = "\n".join(
        f'            <li>{item}</li>' for item in data["items"]
    )

    return f"""<div class="pb-recap-frozen">
    <div class="pb-recap-frozen-header">
        <span class="pb-recap-frozen-eyebrow">What PureBrain Was Building When This Was Written</span>
        <span class="pb-recap-frozen-date">{data['date']}</span>
    </div>
    <ul class="pb-recap-frozen-list">
{items_html}
    </ul>
    <p class="pb-recap-frozen-tagline">This is what your AI partner does while you sleep.</p>
</div>"""


def build_live_section() -> str:
    """Build the live daily recap section (JS-loaded from daily-recap.json)."""
    return """<div class="pb-recap-live">
    <div class="pb-recap-live-header">
        <span class="pb-recap-live-dot"></span>
        <span class="pb-recap-live-label">Today&#8217;s Recap</span>
        <span class="pb-recap-live-date" id="pb-live-recap-date"></span>
    </div>
    <ul class="pb-recap-live-list pb-recap-loading" id="pb-live-recap-list">
        <li>Loading today&#8217;s recap&#8230;</li>
    </ul>
    <a href="https://purebrain.ai/#awakening" class="pb-recap-live-cta">Awaken Your AI Partner Today &rarr;</a>
</div>
<script id="pb-live-recap-loader">
(function(){
    function loadRecap(){
        var list=document.getElementById('pb-live-recap-list');
        var dateEl=document.getElementById('pb-live-recap-date');
        if(!list)return;
        fetch('/blog/daily-recap.json?v='+Date.now())
            .then(function(r){return r.json();})
            .then(function(d){
                if(dateEl&&d.date){dateEl.textContent=d.date;}
                if(d.items&&d.items.length){
                    list.innerHTML=d.items.map(function(item){
                        return '<li>'+item+'</li>';
                    }).join('');
                    list.classList.remove('pb-recap-loading');
                }
            })
            .catch(function(){
                list.innerHTML='<li>Working overnight &#8212; check back in the morning.</li>';
                list.classList.remove('pb-recap-loading');
            });
    }
    if(document.readyState==='loading'){
        document.addEventListener('DOMContentLoaded',loadRecap);
    }else{
        loadRecap();
    }
})();
</script>"""


def build_replacement_section(slug: str) -> str:
    """Build the complete two-tier replacement for pb-transparency-section."""
    frozen = build_frozen_section(slug)
    live = build_live_section()
    return f"""<div class="pb-recap-wrapper" id="pb-transparency-section">
{frozen}
{live}
</div>
<style id="pb-transparency-styles">
{RECAP_CSS}
</style>"""


# Regex to match the old transparency block (div + style) inclusive
OLD_SECTION_PATTERN = re.compile(
    r'<!-- Daily Recap Transparency Section.*?</style>',
    re.DOTALL
)

# Fallback: match the div + style even without the comment
OLD_DIV_PATTERN = re.compile(
    r'<div class="pb-transparency-section"[^>]*>.*?</div>\s*<style id="pb-transparency-styles">.*?</style>',
    re.DOTALL
)


def process_blog_post(html_path: Path, dry_run: bool = False) -> bool:
    """Process a single blog post. Returns True if modified."""
    slug = html_path.parent.name
    html = html_path.read_text(encoding="utf-8")

    replacement = build_replacement_section(slug)

    # Try with comment anchor first (most posts)
    new_html, count = re.subn(OLD_SECTION_PATTERN, replacement, html, count=1)

    if count == 0:
        # Try without comment
        new_html, count = re.subn(OLD_DIV_PATTERN, replacement, html, count=1)

    if count == 0:
        print(f"  [SKIP] {slug} — no transparency section found")
        return False

    if dry_run:
        print(f"  [DRY-RUN] Would update: {slug}")
        return True

    html_path.write_text(new_html, encoding="utf-8")
    print(f"  [OK] Updated: {slug}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Update blog Daily Recap Transparency sections")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    blog_dir = Path("/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog")

    posts = sorted([
        p / "index.html"
        for p in blog_dir.iterdir()
        if p.is_dir() and (p / "index.html").exists()
    ])

    print(f"Found {len(posts)} blog posts to process")
    if args.dry_run:
        print("DRY-RUN mode — no files will be written\n")
    else:
        print()

    modified = 0
    skipped = 0
    for post_path in posts:
        result = process_blog_post(post_path, dry_run=args.dry_run)
        if result:
            modified += 1
        else:
            skipped += 1

    print(f"\nDone. Modified: {modified} | Skipped (no old section): {skipped}")
    if not args.dry_run and modified > 0:
        print(f"\nNext step: deploy with `cd exports/cf-pages-deploy && git add -A && git push`")
        print("Or use the Cloudflare Pages deployment script.")


if __name__ == "__main__":
    main()
