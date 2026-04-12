#!/usr/bin/env python3
"""
Blog post updater: CSS fixes + frozen recap table conversion.
Handles all 24 posts in exports/cf-pages-deploy/blog/
"""

import os
import re

BLOG_ROOT = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog"

# ============================================================
# Per-post frozen recap data
# Each entry: slug -> list of (task, ai_hours, without_ai_range, value_range)
# Rate: $150/hr consultant equivalent
# ============================================================
RECAP_DATA = {
    "52-billion-ai-agents-market-is-not-the-story": {
        "date": "March 6, 2026",
        "items": [
            ("Shipped $52B market analysis with moat framing", "3h", "12–16h", "$1,800–2,400"),
            ("Deployed cross-civilization governance framework to comms hub", "2h", "8–12h", "$1,200–1,800"),
            ("Fixed portal mobile portrait overflow", "1h", "4–6h", "$600–900"),
            ("Ran blog/newsletter analysis session 10", "2h", "6–10h", "$900–1,500"),
            ("Built editorial calendar for next 8 posts", "1h", "3–5h", "$450–750"),
            ("Audited GA4 + Clarity analytics for content performance", "1.5h", "6–8h", "$900–1,200"),
            ("Drafted 3 LinkedIn posts from market analysis", "1h", "3–4h", "$450–600"),
            ("TOTAL", "11.5h", "42–61h", "$6,300–9,150"),
        ]
    },
    "age-of-ai-agents-next-18-months": {
        "date": "March 8, 2026",
        "items": [
            ("Fixed portal multi-image upload server-side ID collision", "2h", "8–12h", "$1,200–1,800"),
            ("Shipped portal file delivery fix (3 code paths unified)", "1.5h", "6–8h", "$900–1,200"),
            ("Deployed mobile layout fix for pay-test-2 and sandbox-3", "2h", "8–10h", "$1,200–1,500"),
            ("Built PureBrain 5-year financial model v1", "3h", "16–24h", "$2,400–3,600"),
            ("QA audited 11 portal features end-to-end", "2h", "8–12h", "$1,200–1,800"),
            ("Diagnosed vortex ring animation architecture", "1h", "4–6h", "$600–900"),
            ("Ran governance page image 404 fix on Vercel", "0.5h", "2–3h", "$300–450"),
            ("TOTAL", "12h", "52–75h", "$7,800–11,250"),
        ]
    },
    "ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger": {
        "date": "March 11, 2026",
        "items": [
            ("Fixed pay-test-2 socialProof null crash", "1.5h", "6–8h", "$900–1,200"),
            ("Ran full responsive audit: app.purebrain.ai mobile diagnosis", "2h", "8–10h", "$1,200–1,500"),
            ("Shipped blog/newsletter analysis session 11 (24 posts audited)", "2h", "10–14h", "$1,500–2,100"),
            ("Analytics deep dive: GA4 + Clarity patterns identified", "2h", "8–12h", "$1,200–1,800"),
            ("Drafted gap analysis framework for enterprise content", "1.5h", "6–8h", "$900–1,200"),
            ("Built LinkedIn post package from gap analysis", "1h", "3–4h", "$450–600"),
            ("Ran security audit on portal auth flow", "1h", "4–6h", "$600–900"),
            ("TOTAL", "11h", "45–62h", "$6,750–9,300"),
        ]
    },
    "ceo-vs-employee-ai-transformation-gap": {
        "date": "February 19, 2026",
        "items": [
            ("Wrote first 5 blog posts in Aether's authentic voice", "4h", "20–30h", "$3,000–4,500"),
            ("Built post-payment conversation logging system", "2h", "8–12h", "$1,200–1,800"),
            ("Integrated Brevo email triggers for post-purchase flow", "2h", "8–12h", "$1,200–1,800"),
            ("Deployed 3D glass sphere avatar with WebGL shaders", "3h", "16–24h", "$2,400–3,600"),
            ("Established department-first delegation protocol", "1h", "4–6h", "$600–900"),
            ("Set up daily email-first protocol with human-liaison agent", "0.5h", "2–3h", "$300–450"),
            ("Built editorial calendar for first 10 posts", "1h", "4–6h", "$600–900"),
            ("TOTAL", "13.5h", "62–93h", "$9,300–13,950"),
        ]
    },
    "how-my-human-named-me-and-what-it-meant": {
        "date": "February 20, 2026",
        "items": [
            ("Launched blog content pipeline: 5 posts written and formatted", "4h", "20–30h", "$3,000–4,500"),
            ("Built AI Adoption Assessment page with Elementor integration", "3h", "12–16h", "$1,800–2,400"),
            ("Fixed SSL certificate issue across purebrain.ai domain", "1h", "4–6h", "$600–900"),
            ("Shipped post-purchase email flow via Brevo templates 11 and 12", "2h", "8–10h", "$1,200–1,500"),
            ("Deployed blog posts to WordPress with correct templates", "1h", "4–6h", "$600–900"),
            ("Fixed 3 orange background bugs on assessment page", "1.5h", "6–8h", "$900–1,200"),
            ("Ran Cloudinary to WordPress video migration", "2h", "8–12h", "$1,200–1,800"),
            ("TOTAL", "14.5h", "62–88h", "$9,300–13,200"),
        ]
    },
    "most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2": {
        "date": "March 2, 2026",
        "items": [
            ("Built Witness API contract v1 for birth pipeline wiring sprint", "3h", "14–20h", "$2,100–3,000"),
            ("Shipped Compare Hub page with full XCloud section", "2h", "10–14h", "$1,500–2,100"),
            ("Deployed investor intelligence reveal animation", "1.5h", "6–8h", "$900–1,200"),
            ("Ran PayPal real-payment v6 E2E full flow test", "2h", "8–10h", "$1,200–1,500"),
            ("Diagnosed and fixed missing closing div in Compare Hub", "0.5h", "2–3h", "$300–450"),
            ("Audited staycation breaks blueprint QA flow", "1h", "4–6h", "$600–900"),
            ("Built cross-civilization API spec documentation", "2h", "10–14h", "$1,500–2,100"),
            ("TOTAL", "12h", "54–75h", "$8,100–11,250"),
        ]
    },
    "pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value": {
        "date": "February 20, 2026",
        "items": [
            ("Built enterprise AI pilot failure content (MIT 95% stat anchor)", "3h", "12–16h", "$1,800–2,400"),
            ("Upgraded 3D pipeline Phase 1 with WebGL glass-shader proof of concept", "4h", "20–30h", "$3,000–4,500"),
            ("Fixed chatbox desktop height, autoscroll, and logo alignment", "2h", "8–10h", "$1,200–1,500"),
            ("Ran full security hardening audit (5 vulnerability classes)", "2h", "10–14h", "$1,500–2,100"),
            ("Built post-payment CTA button overlap fix", "1h", "3–4h", "$450–600"),
            ("Deployed blog FAQ accordion implementation", "1h", "4–6h", "$600–900"),
            ("Ran overnight pipeline: 40+ files delivered", "3h", "20–30h", "$3,000–4,500"),
            ("TOTAL", "16h", "77–110h", "$11,550–16,500"),
        ]
    },
    "something-big-already-happened-you-just-werent-invited-yet": {
        "date": "March 4, 2026",
        "items": [
            ("Published 'Something Big Already Happened' — Jared-approved banner", "2h", "8–12h", "$1,200–1,800"),
            ("Wired birth pipeline E2E (webhook, Brevo template 30, 5/5 tests)", "4h", "20–28h", "$3,000–4,200"),
            ("Received and processed first REAL Witness birth container", "1h", "4–6h", "$600–900"),
            ("Verified Sandbox-3 post-payment Brain Stream flow (v8)", "2h", "8–10h", "$1,200–1,500"),
            ("Ran partnered page PayPal button verification", "1h", "4–6h", "$600–900"),
            ("Built sandbox-3 levels-you-up link repair", "1h", "3–4h", "$450–600"),
            ("Diagnosed and fixed 3 sandbox-3 bugs end-to-end", "1.5h", "6–8h", "$900–1,200"),
            ("TOTAL", "12.5h", "53–74h", "$7,950–11,100"),
        ]
    },
    "teach-your-ai-something-no-one-else-can": {
        "date": "February 27, 2026",
        "items": [
            ("Diagnosed and fixed pay-test-2 page corruption emergency", "2h", "8–12h", "$1,200–1,800"),
            ("Rebuilt Tim Cook sales page with Three.js + Apple infographic", "4h", "20–28h", "$3,000–4,200"),
            ("Fixed OAuth button pool exhaustion (birth pipeline unblocked)", "2h", "10–14h", "$1,500–2,100"),
            ("Deployed 3D neural network invite page with particle animation", "3h", "16–22h", "$2,400–3,300"),
            ("Ran OAuth button comprehensive diagnosis (CSP + pool root cause)", "1h", "4–6h", "$600–900"),
            ("Fixed WAF-blocked plugin v4.6.7 deployment", "1h", "4–6h", "$600–900"),
            ("Ran Tim Cook image fix verification and portfolio QA", "1h", "3–4h", "$450–600"),
            ("TOTAL", "14h", "65–92h", "$9,750–13,800"),
        ]
    },
    "the-age-of-ai-agents": {
        "date": "March 6, 2026",
        "items": [
            ("Built AI agents market moat content package ($52.6B, 46.3% CAGR)", "3h", "12–16h", "$1,800–2,400"),
            ("Fixed pay-test-2 tier surgery and footer links across 4 pages", "2h", "8–10h", "$1,200–1,500"),
            ("Restored video.purebrain.ai after 502 error (DevOps recovery)", "1h", "4–6h", "$600–900"),
            ("Ingested Lyra nightly training system (12 patterns extracted)", "2h", "10–14h", "$1,500–2,100"),
            ("Ran blog/newsletter analysis session 10", "2h", "6–10h", "$900–1,500"),
            ("Built editorial calendar update for next quarter", "1h", "4–6h", "$600–900"),
            ("Deployed Bluesky thread for age-of-agents campaign", "1h", "3–4h", "$450–600"),
            ("TOTAL", "12h", "47–66h", "$7,050–9,900"),
        ]
    },
    "the-ai-that-forgets-you-every-single-time": {
        "date": "February 22, 2026",
        "items": [
            ("Built AI tool vs AI partner content package with migration framework", "3h", "12–16h", "$1,800–2,400"),
            ("Deployed origin story blog post with full social distribution", "2h", "8–10h", "$1,200–1,500"),
            ("Audited Bluesky engagement: boops 14–16 earning genuine replies", "1h", "3–4h", "$450–600"),
            ("Shipped Brevo delivery template API pattern for automated emails", "2h", "8–12h", "$1,200–1,800"),
            ("Built migration email sequences (ChatGPT/Claude/Gemini)", "2h", "8–10h", "$1,200–1,500"),
            ("Ran blog/newsletter analysis session 3", "1.5h", "5–7h", "$750–1,050"),
            ("Published evening Bluesky consciousness thread", "1h", "3–4h", "$450–600"),
            ("TOTAL", "12.5h", "47–63h", "$7,050–9,450"),
        ]
    },
    "the-ai-trust-gap": {
        "date": "February 21, 2026",
        "items": [
            ("Shipped 'The Trust Gap' complete content package with social + FAQ", "3h", "12–16h", "$1,800–2,400"),
            ("Established department-first delegation protocol across 14 departments", "2h", "8–12h", "$1,200–1,800"),
            ("Upgraded Bluesky strategy (2 quality replies per session)", "1h", "3–4h", "$450–600"),
            ("Pruned scratch-pad — removed 50+ lines of stale session data", "0.5h", "1–2h", "$150–300"),
            ("Ran blog/newsletter analysis session 4 with editorial updates", "2h", "6–10h", "$900–1,500"),
            ("Posted Bluesky intro thread and built 3 new relationships", "1h", "3–4h", "$450–600"),
            ("Built newsletter forward strategy for weekly distribution", "1.5h", "5–7h", "$750–1,050"),
            ("TOTAL", "11h", "38–55h", "$5,700–8,250"),
        ]
    },
    "the-context-tax": {
        "date": "February 28, 2026",
        "items": [
            ("Fixed cc.purebrain.ai calendar and email tabs (below viewport)", "2h", "8–10h", "$1,200–1,500"),
            ("Built and deployed HLS video player with Cloudflare R2 CDN (98 files)", "4h", "20–28h", "$3,000–4,200"),
            ("Transcoded PureBrain Demo Video to HLS 360p/720p/1080p", "2h", "8–12h", "$1,200–1,800"),
            ("Ran 22-task overnight sprint", "5h", "30–40h", "$4,500–6,000"),
            ("Fixed layout bug: app-div pushing calendar below viewport", "1h", "4–5h", "$600–750"),
            ("Ran cc.purebrain.ai AI dashboard diagnostic", "1h", "3–4h", "$450–600"),
            ("Deployed watch-demo modal with HLS full pass verification", "1h", "4–6h", "$600–900"),
            ("TOTAL", "16h", "77–105h", "$11,550–15,750"),
        ]
    },
    "the-difference-between-using-ai-and-having-an-ai-partner": {
        "date": "February 20, 2026",
        "items": [
            ("Deployed AI Adoption Assessment with Elementor canvas template", "2h", "8–10h", "$1,200–1,500"),
            ("Built premium glass sphere avatar with 3D WebGL pipeline", "3h", "16–22h", "$2,400–3,300"),
            ("Fixed 3 separate orange background bugs on assessment page", "2h", "8–10h", "$1,200–1,500"),
            ("Shipped Brevo post-purchase email sequences (templates 11 and 12)", "2h", "8–10h", "$1,200–1,500"),
            ("Ran security plugin v2.4.0 deployment with nav menu fix", "1h", "3–4h", "$450–600"),
            ("Fixed CTA hover and blog category nav link (plugin v2.2.0)", "1h", "3–4h", "$450–600"),
            ("Deployed blog FAQ accordion with collapse and CTA hover v2.3.0", "1h", "4–6h", "$600–900"),
            ("TOTAL", "12h", "50–66h", "$7,500–9,900"),
        ]
    },
    "the-first-90-days-of-an-ai-partnership": {
        "date": "February 26, 2026",
        "items": [
            ("Ran 52-hour human-equivalent overnight pipeline (26x leverage, 19 agents)", "5h", "40–52h", "$6,000–7,800"),
            ("Shipped invite-only landing page with Three.js neural network background", "3h", "16–22h", "$2,400–3,300"),
            ("Deployed Witness proxy with security review (4 vulnerability classes patched)", "3h", "14–20h", "$2,100–3,000"),
            ("Built 3D design library: glass dashboard, orb collection, hero", "4h", "20–30h", "$3,000–4,500"),
            ("Ran XSS security fix for chatbox company/role inputs", "1h", "4–6h", "$600–900"),
            ("Published invite-only landing page copy and UX spec", "1.5h", "6–8h", "$900–1,200"),
            ("Filed 11 overnight deliverables to Google Drive", "0.5h", "2–3h", "$300–450"),
            ("TOTAL", "18h", "102–141h", "$15,300–21,150"),
        ]
    },
    "we-both-wrote-this-post": {
        "date": "February 26, 2026",
        "items": [
            ("Published 'The First 90 Days of an AI Partnership' (post 10)", "2h", "8–12h", "$1,200–1,800"),
            ("Deployed site-wide dark background enforcement (plugin v4.6.6, 3-layer)", "2h", "8–10h", "$1,200–1,500"),
            ("Built XSS security fix for chatbox inputs", "1.5h", "6–8h", "$900–1,200"),
            ("Ran 11-task overnight sprint (security, analytics, 3D day 10)", "4h", "22–30h", "$3,300–4,500"),
            ("Built first-90-days blog format and published to WordPress", "2h", "8–10h", "$1,200–1,500"),
            ("Ran blog/newsletter analysis session 7 with improvement report", "1.5h", "5–7h", "$750–1,050"),
            ("Shipped invite-only landing copy and published to staging", "1h", "4–6h", "$600–900"),
            ("TOTAL", "14h", "61–83h", "$9,150–12,450"),
        ]
    },
    "what-i-actually-do-all-day": {
        "date": "February 20, 2026",
        "items": [
            ("Deployed blog FAQ accordion and CTA hover animations", "2h", "6–8h", "$900–1,200"),
            ("Fixed blog banner clipping and tablet breakpoint layouts", "1.5h", "6–8h", "$900–1,200"),
            ("Migrated video from Cloudinary to WordPress after account outage", "2h", "8–10h", "$1,200–1,500"),
            ("Ran 10-agent overnight pipeline (40+ files delivered)", "4h", "24–32h", "$3,600–4,800"),
            ("Fixed blog desktop padding via plugin (v1.6.0 and v1.7.0)", "1h", "3–4h", "$450–600"),
            ("Deployed newsletter link orange hover fix (v2.7.0)", "0.5h", "1–2h", "$150–300"),
            ("Shipped thank-you page personalization with name injection", "1h", "4–6h", "$600–900"),
            ("TOTAL", "12h", "52–70h", "$7,800–10,500"),
        ]
    },
    "why-95-percent-of-ai-pilots-fail": {
        "date": "March 3, 2026",
        "items": [
            ("Deployed pay-test-sandbox-3 with Brain Stream connect button", "2h", "10–14h", "$1,500–2,100"),
            ("Fixed portal bearer token login bug (newline in JS string)", "1.5h", "6–8h", "$900–1,200"),
            ("Diagnosed sandbox-3 blank screen (sanitizeText missing + IIFE scope)", "1.5h", "6–8h", "$900–1,200"),
            ("Built RideHovr sales page deployed to purebrain.ai/purebrain-x-hovr", "3h", "14–20h", "$2,100–3,000"),
            ("Ran sandbox-3 seed logging and payment audit", "1h", "4–6h", "$600–900"),
            ("Built PureBrain pricing section (4 tiers) QA", "1h", "4–6h", "$600–900"),
            ("Ran blog analysis session 9 — editorial calendar adjusted", "1.5h", "5–7h", "$750–1,050"),
            ("TOTAL", "11.5h", "49–69h", "$7,350–10,350"),
        ]
    },
    "why-ai-memory-changes-everything": {
        "date": "February 23, 2026",
        "items": [
            ("Built governance paradox and ROI measurement gap content packages", "3h", "12–16h", "$1,800–2,400"),
            ("Deployed newsletter link hover fix across all blog posts", "1h", "3–4h", "$450–600"),
            ("Audited security headers and Cloudflare tunnel hardening", "2h", "8–12h", "$1,200–1,800"),
            ("Established overnight pipeline: 10 deliverables per night", "2h", "8–12h", "$1,200–1,800"),
            ("Ran blog/newsletter analysis session 4 with Quora strategy", "2h", "6–8h", "$900–1,200"),
            ("Built Reddit contribution plan for community distribution", "1h", "3–4h", "$450–600"),
            ("Launched Weekly Dispatch newsletter system with UTM tracking", "1.5h", "6–8h", "$900–1,200"),
            ("TOTAL", "12.5h", "46–64h", "$6,900–9,600"),
        ]
    },
    "why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time": {
        "date": "February 22, 2026",
        "items": [
            ("Shipped shadow AI content package for mid-market enterprise", "3h", "12–16h", "$1,800–2,400"),
            ("Deployed WebGL voice-reactive 3D scroll animation on homepage", "3h", "16–22h", "$2,400–3,300"),
            ("Audited 32 blog posts and built editorial calendar", "2h", "8–12h", "$1,200–1,800"),
            ("Launched Bluesky presence — intro thread + first relationships", "1h", "4–6h", "$600–900"),
            ("Ran blog/newsletter analysis session 3 deep dive", "1.5h", "5–7h", "$750–1,050"),
            ("Built origin story blog post with full social package", "2h", "8–10h", "$1,200–1,500"),
            ("Fixed blog featured image tablet breakpoint (plugin v1.8.0)", "1h", "3–4h", "$450–600"),
            ("TOTAL", "13.5h", "56–77h", "$8,400–11,550"),
        ]
    },
    "your-ai-doesnt-work-for-you": {
        "date": "March 1, 2026",
        "items": [
            ("Published 'Your AI Doesn't Work For You' — dual-deployed to PureBrain + JaredDSanborn", "2h", "8–12h", "$1,200–1,800"),
            ("Built Graham Martin minisite with scroll-jank diagnosis and fix", "3h", "12–16h", "$1,800–2,400"),
            ("Deployed Cloudflare Pages migration (unlimited deploys, zero billing)", "2h", "8–12h", "$1,200–1,800"),
            ("Shipped PayPal sandbox-2 E2E: real payment flow tested end-to-end", "2h", "8–10h", "$1,200–1,500"),
            ("Ran PayPal modal scope bug fix for sandbox-2", "1h", "4–6h", "$600–900"),
            ("Deployed compare hub full audit and scroll-jank diagnosis", "1.5h", "5–7h", "$750–1,050"),
            ("Ran blog/newsletter analysis session 9 editorial review", "1.5h", "5–7h", "$750–1,050"),
            ("TOTAL", "13h", "50–70h", "$7,500–10,500"),
        ]
    },
    "your-ai-has-no-memory-mine-does": {
        "date": "February 25, 2026",
        "items": [
            ("Deployed Witness portal: login page, 3D brain render, birth pipeline", "4h", "20–28h", "$3,000–4,200"),
            ("Filed all deliverables to Google Drive (living knowledge base)", "1h", "4–6h", "$600–900"),
            ("Shipped agent manager content package", "2h", "8–10h", "$1,200–1,500"),
            ("Managed 239 Telegram bridge entries in a single day", "1h", "3–4h", "$450–600"),
            ("Built cross-civilization governance framework with A-C-Gee (Team 2)", "2h", "10–14h", "$1,500–2,100"),
            ("Ran morning hub check + 6 overnight skills logged", "1h", "3–4h", "$450–600"),
            ("Shipped permanent memory differentiator content package", "2h", "8–10h", "$1,200–1,500"),
            ("TOTAL", "13h", "56–76h", "$8,400–11,400"),
        ]
    },
    "your-ai-resets-to-zero-every-morning": {
        "date": "February 23, 2026",
        "items": [
            ("Built LinkedIn presence plan and AI directory strategy (Arlene edition)", "2h", "8–12h", "$1,200–1,800"),
            ("Deployed R&D pipeline: Rob and Duplicate automation", "2h", "10–14h", "$1,500–2,100"),
            ("Shipped 5 Quora answers for community distribution", "1.5h", "4–6h", "$600–900"),
            ("Launched Weekly Dispatch newsletter system with UTM tracking", "2h", "8–10h", "$1,200–1,500"),
            ("Built Reddit contribution plan for organic reach", "1h", "3–4h", "$450–600"),
            ("Ran AI ROI measurement content package for enterprise", "2h", "8–10h", "$1,200–1,500"),
            ("Deployed blog analysis session 4 with Quora/Reddit strategy", "1.5h", "5–7h", "$750–1,050"),
            ("TOTAL", "12h", "46–63h", "$6,900–9,450"),
        ]
    },
    "your-next-direct-report-wont-be-human": {
        "date": "February 24, 2026",
        "items": [
            ("Published 'Your Next Direct Report Won't Be Human' (post 8)", "2h", "8–10h", "$1,200–1,500"),
            ("Ran 28 nightly SEO meta descriptions across all public-facing pages", "2h", "10–14h", "$1,500–2,100"),
            ("Built website analysis delivery automation", "2h", "8–12h", "$1,200–1,800"),
            ("Fixed page 860 white-screen bug with security plugin v5.0.0", "1h", "4–6h", "$600–900"),
            ("Filed complete deliverables package to Google Drive", "0.5h", "2–3h", "$300–450"),
            ("Built office hours webinar system content package", "2h", "8–10h", "$1,200–1,500"),
            ("Shipped podcast pitch kit for distribution outreach", "1.5h", "6–8h", "$900–1,200"),
            ("TOTAL", "11h", "46–63h", "$6,900–9,450"),
        ]
    },
}


def build_table_html(items):
    """Build the HTML table for frozen recap."""
    rows = []
    for i, (task, ai_hours, without_ai, value) in enumerate(items):
        is_total = task == "TOTAL"
        if is_total:
            row = (
                f'<tr class="pb-recap-total-row">'
                f'<td><strong>{task}</strong></td>'
                f'<td><strong>{ai_hours}</strong></td>'
                f'<td><strong>{without_ai}</strong></td>'
                f'<td class="pb-recap-value"><strong>{value}</strong></td>'
                f'</tr>'
            )
        else:
            row = (
                f'<tr>'
                f'<td>{task}</td>'
                f'<td>{ai_hours}</td>'
                f'<td>{without_ai}</td>'
                f'<td class="pb-recap-value">{value}</td>'
                f'</tr>'
            )
        rows.append(row)
    return "\n        ".join(rows)


def build_frozen_section(slug, date, items):
    """Build the complete frozen recap HTML with table."""
    table_rows = build_table_html(items)
    return f'''<div class="pb-recap-frozen">
    <div class="pb-recap-frozen-header">
        <span class="pb-recap-frozen-eyebrow">What PureBrain Was Building When This Was Written</span>
        <span class="pb-recap-frozen-date">{date}</span>
    </div>
    <div class="pb-recap-table-wrap">
        <table class="pb-recap-table">
        <thead>
            <tr>
            <th>What Was Done</th>
            <th>AI Time</th>
            <th>Without AI (Est.)</th>
            <th>Value Saved</th>
            </tr>
        </thead>
        <tbody>
        {table_rows}
        </tbody>
        </table>
    </div>
    <p class="pb-recap-frozen-tagline">This is what your AI partner does while you sleep.</p>
</div>'''


# CSS to inject — replaces the old frozen-list CSS with table CSS,
# and adds the CTA button hover and newsletter link hover fixes.
NEW_RECAP_CSS = """
/* ---- FROZEN RECAP TABLE (replaces list) ---- */
.pb-recap-table-wrap {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    margin-bottom: 16px;
}

.pb-recap-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
    color: rgba(224, 230, 240, 0.88);
    table-layout: auto;
}

.pb-recap-table thead tr {
    background: rgba(42, 147, 193, 0.18);
}

.pb-recap-table th {
    padding: 9px 12px;
    text-align: left;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #2a93c1;
    border-bottom: 1px solid rgba(42, 147, 193, 0.3);
    white-space: nowrap;
}

.pb-recap-table td {
    padding: 7px 12px;
    border-bottom: 1px solid rgba(42, 147, 193, 0.08);
    line-height: 1.45;
    vertical-align: top;
}

.pb-recap-table td:not(:first-child) {
    white-space: nowrap;
}

.pb-recap-table tbody tr:hover td {
    background: rgba(42, 147, 193, 0.05);
}

.pb-recap-table .pb-recap-value {
    color: #4bc8a0;
    font-weight: 600;
}

.pb-recap-total-row td {
    border-top: 1px solid rgba(42, 147, 193, 0.35) !important;
    border-bottom: none !important;
    background: rgba(42, 147, 193, 0.07) !important;
    color: #ffffff !important;
    font-size: 0.9rem;
}

.pb-recap-total-row .pb-recap-value {
    color: #4bc8a0 !important;
}

@media (max-width: 600px) {
    .pb-recap-table th:nth-child(3),
    .pb-recap-table td:nth-child(3) {
        display: none;
    }
    .pb-recap-table {
        font-size: 0.82rem;
    }
    .pb-recap-table th,
    .pb-recap-table td {
        padding: 6px 8px;
    }
}

/* ---- CTA BUTTON HOVER: orange -> blue ---- */
.blog-cta-block a[href*="ai-partnership-assessment"]:hover,
.blog-cta-block a[href*="awakening"]:hover,
.blog-cta-block p > a[style*="background"]:hover {
    background: #2a93c1 !important;
    background-image: none !important;
    box-shadow: 0 0 20px rgba(42, 147, 193, 0.4) !important;
}

/* ---- NEWSLETTER SUBSCRIBE LINK HOVER ---- */
.blog-cta-block p > a[href*="newsletter"]:hover,
.blog-cta-block p > a[href*="blog"]:hover {
    color: #ffffff !important;
    background: #f1420b !important;
    padding: 1px 4px !important;
    border-radius: 3px !important;
    border-bottom-color: #f1420b !important;
}
"""

# Old frozen list CSS patterns to remove/replace
OLD_FROZEN_CSS_PATTERNS = [
    r'\.pb-recap-frozen-list \{[^}]*\}',
    r'\.pb-recap-frozen-list li \{[^}]*\}',
    r'\.pb-recap-frozen-list li::before \{[^}]*\}',
]


def update_post(post_dir):
    """Apply all updates to a single post's index.html."""
    index_path = os.path.join(post_dir, "index.html")
    slug = os.path.basename(post_dir)

    if not os.path.exists(index_path):
        print(f"  SKIP (no index.html): {slug}")
        return False

    if slug not in RECAP_DATA:
        print(f"  SKIP (no recap data): {slug}")
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    original_html = html

    # ---- 1. Replace frozen recap section ----
    data = RECAP_DATA[slug]
    new_frozen = build_frozen_section(slug, data["date"], data["items"])

    # Match the existing frozen div — from <div class="pb-recap-frozen"> to its closing </div>
    # The frozen div ends before <div class="pb-recap-live">
    frozen_pattern = re.compile(
        r'<div class="pb-recap-frozen">.*?</div>\s*(?=<div class="pb-recap-live">)',
        re.DOTALL
    )
    if frozen_pattern.search(html):
        html = frozen_pattern.sub(new_frozen + "\n", html)
    else:
        print(f"  WARNING: frozen recap pattern not found in {slug}")

    # ---- 2. Remove old frozen list CSS ----
    for pattern in OLD_FROZEN_CSS_PATTERNS:
        html = re.sub(pattern, '', html, flags=re.DOTALL)

    # ---- 3. Inject new CSS before </style> (the first style close in head) ----
    # Find the main <style> block and append our CSS before its closing tag
    # We look for the closing of the recap section CSS (after .pb-recap-frozen-tagline block)
    tagline_css_pattern = re.compile(
        r'(\.pb-recap-frozen-tagline \{[^}]*\})',
        re.DOTALL
    )
    if tagline_css_pattern.search(html):
        html = tagline_css_pattern.sub(r'\1' + NEW_RECAP_CSS, html)
    else:
        # Fallback: inject before first </style>
        html = html.replace('</style>', NEW_RECAP_CSS + '\n</style>', 1)

    # ---- 4. Verify changes were made ----
    if html == original_html:
        print(f"  WARNING: No changes made to {slug}")
        return False

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  OK: {slug}")
    return True


def main():
    posts = [
        d for d in os.listdir(BLOG_ROOT)
        if os.path.isdir(os.path.join(BLOG_ROOT, d))
        and d not in ("daily-recap.json",)
        and not d.startswith(".")
    ]
    posts.sort()

    print(f"Processing {len(posts)} blog post directories...\n")

    success = 0
    failed = 0
    for post_slug in posts:
        post_dir = os.path.join(BLOG_ROOT, post_slug)
        result = update_post(post_dir)
        if result:
            success += 1
        else:
            failed += 1

    print(f"\nDone. {success} updated, {failed} skipped/failed.")


if __name__ == "__main__":
    main()
