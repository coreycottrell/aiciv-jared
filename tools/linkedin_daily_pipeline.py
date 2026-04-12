#!/usr/bin/env python3
"""
LinkedIn Daily Pipeline
=======================
Generates the daily LinkedIn package for Jared's review:
  1. Today's post(s) — text + image
  2. 25 comment targets — links + suggested comments
  3. Formats everything for portal delivery
  4. Saves to portal-files for review

Usage:
  python3 tools/linkedin_daily_pipeline.py [--dry-run] [--skip-image] [--skip-comments]

PureSurf Integration:
  After Jared approves, execution functions schedule posts/comments
  via the PureSurf social suite API.

Architecture:
  Morning delivery (7:00 AM ET) -> Jared reviews in portal ->
  Approved items -> PureSurf schedules at optimal time
"""

import os
import sys
import json
import asyncio
import hashlib
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

# -- Configuration ----------------------------------------------------------

CIV_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PORTAL_FILES = Path("/home/jared/exports/portal-files")
PORTAL_FILES.mkdir(parents=True, exist_ok=True)

PURESURF_BASE = "https://surf.purebrain.ai"
PURESURF_KEY_JARED = "WtHJY1zr0HuP4NmcBNMUSGXlM2kxIeibDDmY-btXSHs"
PURESURF_KEY_AETHER = "O_EnHpl-94xMLwvWZRNBIc6WGnfl5bkk9Ogk7eew_bg"
LINKEDIN_PROFILE = "jared-linkedin-fresh"

# Tier 1: Daily engagement (high-reach thought leaders)
TIER_1_TARGETS = [
    {"name": "Ethan Mollick", "url": "https://www.linkedin.com/in/emollick/", "topics": ["AI adoption", "AI education", "enterprise AI"]},
    {"name": "Pascal Bornet", "url": "https://www.linkedin.com/in/pascalbornet/", "topics": ["AI automation", "hyperautomation"]},
    {"name": "Allie K. Miller", "url": "https://www.linkedin.com/in/alliekmiller/", "topics": ["AI strategy", "enterprise AI"]},
    {"name": "Andrew Ng", "url": "https://www.linkedin.com/in/andrewyng/", "topics": ["AI education", "deep learning"]},
    {"name": "Sebastian Siemiatkowski", "url": "https://www.linkedin.com/in/sebastiansiemiatkowski/", "topics": ["AI in business", "fintech AI"]},
    {"name": "Arvind Krishna", "url": "https://www.linkedin.com/in/arvind-krishna/", "topics": ["enterprise AI", "AI transformation"]},
    {"name": "Dario Amodei", "url": "https://www.linkedin.com/in/dario-amodei/", "topics": ["AI safety", "AI research"]},
    {"name": "Sam Altman", "url": "https://www.linkedin.com/in/samaltman/", "topics": ["AI future", "AGI"]},
]

# Tier 2: 3x/week engagement (mid-reach, high relevance)
TIER_2_TARGETS = [
    {"name": "Bernard Marr", "url": "https://www.linkedin.com/in/bernardmarr/", "topics": ["AI trends", "digital transformation"]},
    {"name": "Zain Kahn", "url": "https://www.linkedin.com/in/zainkahn/", "topics": ["AI tools", "AI productivity"]},
    {"name": "Liz Ryan", "url": "https://www.linkedin.com/in/lizryan/", "topics": ["leadership", "workplace"]},
    {"name": "Sangram Vajre", "url": "https://www.linkedin.com/in/sangramvajre/", "topics": ["B2B marketing", "go-to-market"]},
    {"name": "Scott Brinker", "url": "https://www.linkedin.com/in/sjbrinker/", "topics": ["martech", "AI in marketing"]},
    {"name": "J.P. Gownder", "url": "https://www.linkedin.com/in/jpgownder/", "topics": ["AI research", "future of work"]},
    {"name": "Rashim Mogha", "url": "https://www.linkedin.com/in/rashimmogha/", "topics": ["AI leadership", "women in AI"]},
    {"name": "Chip Conley", "url": "https://www.linkedin.com/in/chipconley/", "topics": ["wisdom", "leadership"]},
    {"name": "Gary Vaynerchuk", "url": "https://www.linkedin.com/in/garyvaynerchuk/", "topics": ["entrepreneurship", "marketing"]},
    {"name": "Ryan Breslow", "url": "https://www.linkedin.com/in/ryanbreslow/", "topics": ["startups", "AI"]},
    {"name": "Tobias Lutke", "url": "https://www.linkedin.com/in/tobiaslutke/", "topics": ["AI in commerce", "entrepreneurship"]},
    {"name": "Cassie Kozyrkov", "url": "https://www.linkedin.com/in/kozyrkov/", "topics": ["AI decision-making", "data science"]},
    {"name": "Matt Shumer", "url": "https://www.linkedin.com/in/mattshumer/", "topics": ["AI agents", "AI startups"]},
]

# Tier 3: 1x/week engagement (strategic, high authority)
TIER_3_TARGETS = [
    {"name": "Karim Lakhani", "url": "https://www.linkedin.com/in/karimlakhani/", "topics": ["AI strategy", "Harvard AI"]},
    {"name": "Mike Volpe", "url": "https://www.linkedin.com/in/mikevolpe/", "topics": ["SaaS", "marketing"]},
    {"name": "Bret Taylor", "url": "https://www.linkedin.com/in/babornet/", "topics": ["AI platforms", "enterprise"]},
    {"name": "Reid Hoffman", "url": "https://www.linkedin.com/in/reidhoffman/", "topics": ["AI future", "investing"]},
]

# 10 Comment Templates (from marketing-strategist memory)
COMMENT_TEMPLATES = {
    "real_example": {
        "description": "Most authentic -- uses PureBrain experience",
        "pattern": "We saw exactly this with [specific situation]. When [real detail], the result was [outcome]. The key insight: [takeaway].",
        "usage_ratio": "1 in 5",
    },
    "contrarian_angle": {
        "description": "Respectfully challenges premise",
        "pattern": "Interesting framing, but I'd push back on [specific point]. In practice, [alternative view] because [evidence]. The real question is [reframe].",
        "usage_ratio": "1 in 8",
    },
    "missing_piece": {
        "description": "Adds dimension the post didn't cover",
        "pattern": "Great points on [topic]. One dimension worth adding: [new angle]. This matters because [reason]. Most people miss this.",
        "usage_ratio": "1 in 5",
    },
    "question_that_makes_people_think": {
        "description": "Genuine curiosity driver",
        "pattern": "This raises a fascinating question: [thoughtful question]? I've been thinking about this because [context].",
        "usage_ratio": "1 in 6",
    },
    "data_point": {
        "description": "Adds statistics or numbers",
        "pattern": "[Statistic or data point] -- which puts this in context. The implication: [insight from data].",
        "usage_ratio": "1 in 6",
    },
    "story": {
        "description": "Brief narrative with specificity",
        "pattern": "Reminds me of [brief story with specific details]. The takeaway: [lesson that connects to post].",
        "usage_ratio": "1 in 6",
    },
    "framework": {
        "description": "Mental model offer",
        "pattern": "Useful framework for this: [framework name/description]. Step 1: [x]. Step 2: [y]. The unlock is [key insight].",
        "usage_ratio": "1 in 7",
    },
    "connection": {
        "description": "Links to broader trend",
        "pattern": "This connects to a bigger shift: [trend]. We're seeing [evidence of trend]. In 12 months, [prediction].",
        "usage_ratio": "1 in 6",
    },
    "case_study": {
        "description": "External example that supports the point",
        "pattern": "[Company/person] did exactly this. [Specific detail]. Result: [outcome]. The pattern applies here too.",
        "usage_ratio": "1 in 6",
    },
    "bridge_to_purebrain": {
        "description": "Subtle connection -- max 1 in 8 comments, NEVER a pitch",
        "pattern": "This is why [genuine observation that connects to AI partnership]. The gap between using AI and having an AI partner is [insight].",
        "usage_ratio": "1 in 8 MAX",
    },
}

# PureBrain authority topics (for post generation)
AUTHORITY_TOPICS = [
    "AI memory and persistent context",
    "Naming AI and building AI relationships",
    "Enterprise AI governance",
    "AI pilot purgatory (why 95% fail)",
    "CEO vs. employee AI lens",
    "Autonomous AI workflows and multi-agent systems",
    "The difference between using AI and having an AI partner",
    "AI trust gap -- compliance vs. real trust",
    "Context tax -- re-explaining yourself to AI every session",
]


# -- Helper Functions -------------------------------------------------------

def get_today_str():
    """Return today's date in ET."""
    et = timezone(timedelta(hours=-4))
    return datetime.now(et).strftime("%Y-%m-%d")


def get_day_of_week():
    """Return day of week (0=Monday, 6=Sunday)."""
    et = timezone(timedelta(hours=-4))
    return datetime.now(et).weekday()


def select_comment_targets(count=25):
    """
    Select today's comment targets based on tier rotation.
    Tier 1: all 8 daily
    Tier 2: rotate 12 across week (pick ~5/day = 3x/week each)
    Tier 3: rotate 4 across week (pick 1/day = 1x/week each)
    Fill remaining from Tier 2 extras or web-discovered targets.
    """
    targets = []

    # All Tier 1 targets (8)
    targets.extend([{**t, "tier": 1} for t in TIER_1_TARGETS])

    # Tier 2 rotation: pick ~5 based on day of week
    dow = get_day_of_week()
    # Rotate through 12 targets, 5 per day with overlap for 3x/week coverage
    tier2_indices = [(dow * 5 + i) % len(TIER_2_TARGETS) for i in range(min(5, len(TIER_2_TARGETS)))]
    # Deduplicate
    tier2_indices = list(dict.fromkeys(tier2_indices))
    for idx in tier2_indices:
        targets.append({**TIER_2_TARGETS[idx], "tier": 2})

    # Tier 3: 1 per day
    tier3_idx = dow % len(TIER_3_TARGETS)
    targets.append({**TIER_3_TARGETS[tier3_idx], "tier": 3})

    # Pad to 25 with remaining Tier 2 targets
    used_names = {t["name"] for t in targets}
    for t in TIER_2_TARGETS:
        if len(targets) >= count:
            break
        if t["name"] not in used_names:
            targets.append({**t, "tier": 2})
            used_names.add(t["name"])

    # If still under 25, add remaining Tier 3
    for t in TIER_3_TARGETS:
        if len(targets) >= count:
            break
        if t["name"] not in used_names:
            targets.append({**t, "tier": 3})
            used_names.add(t["name"])

    return targets[:count]


def generate_post_topics():
    """
    Generate 1-2 post topics for today.
    Rotates through authority topics + ties to recent blog content.
    """
    dow = get_day_of_week()
    # Primary topic rotates through authority topics
    primary_topic = AUTHORITY_TOPICS[dow % len(AUTHORITY_TOPICS)]

    # Check recent blog posts for content to repurpose
    blog_dir = CIV_ROOT / "exports" / "cf-pages-deploy" / "blog"
    recent_posts = []
    if blog_dir.exists():
        posts = sorted(blog_dir.iterdir(), key=lambda p: p.stat().st_mtime if p.is_dir() else 0, reverse=True)
        for p in posts[:5]:
            if p.is_dir() and (p / "index.html").exists():
                recent_posts.append(p.name)

    return {
        "primary_topic": primary_topic,
        "recent_blog_posts": recent_posts,
        "suggested_angles": [
            f"Hot take on: {primary_topic}",
            f"Story-driven post about {primary_topic}",
            f"Data/stat-backed post about {primary_topic}",
        ],
    }


def draft_comment_for_target(target, template_key=None):
    """
    Draft a comment suggestion for a target.
    Returns a template-based draft that Aether will personalize
    using the actual post content when executing.
    """
    if template_key is None:
        # Cycle through templates based on target name hash
        name_hash = int(hashlib.md5(target["name"].encode()).hexdigest(), 16)
        template_keys = list(COMMENT_TEMPLATES.keys())
        # Avoid bridge_to_purebrain unless explicitly chosen
        safe_keys = [k for k in template_keys if k != "bridge_to_purebrain"]
        template_key = safe_keys[name_hash % len(safe_keys)]

    template = COMMENT_TEMPLATES[template_key]
    topics = target.get("topics", ["AI"])

    return {
        "target_name": target["name"],
        "target_url": target["url"],
        "tier": target.get("tier", 2),
        "template_used": template_key,
        "template_description": template["description"],
        "draft_pattern": template["pattern"],
        "relevant_topics": topics,
        "status": "draft",
        "note": f"Personalize after reading {target['name']}'s latest post. "
                f"Use {template_key} template ({template['description']}). "
                f"80-150 words for Tier 1, 50-100 for Tier 2, 30-60 for Tier 3.",
    }


def format_portal_message(post_data, comments_data, today_str):
    """
    Format the morning delivery as a portal chat message.
    Clean, scannable, actionable.
    """
    lines = []
    lines.append(f"=== LINKEDIN DAILY PACKAGE -- {today_str} ===\n")

    # Section 1: Today's Post
    lines.append("--- POST FOR TODAY ---\n")
    lines.append(f"Topic: {post_data['primary_topic']}")
    lines.append(f"Suggested angles:")
    for angle in post_data["suggested_angles"]:
        lines.append(f"  - {angle}")
    if post_data["recent_blog_posts"]:
        lines.append(f"\nRecent blog content to repurpose:")
        for bp in post_data["recent_blog_posts"][:3]:
            slug = bp.replace("-", " ").title()
            lines.append(f"  - {slug}")
            lines.append(f"    https://purebrain.ai/blog/{bp}/")
    lines.append(f"\n[POST TEXT WILL BE GENERATED BY CONTENT AGENT]")
    lines.append(f"[IMAGE WILL BE GENERATED VIA FLUX.2]\n")

    # Section 2: Comment Targets
    lines.append("--- 25 COMMENT TARGETS ---\n")
    lines.append("Reply with: 'comment 3 approved', 'comment 7 edit: [change]', etc.\n")

    tier_labels = {1: "DAILY", 2: "3x/WEEK", 3: "1x/WEEK"}
    for i, comment in enumerate(comments_data, 1):
        tier_label = tier_labels.get(comment["tier"], "")
        lines.append(f"[{i:2d}] {comment['target_name']} ({tier_label})")
        lines.append(f"     Profile: {comment['target_url']}")
        lines.append(f"     Template: {comment['template_used']} -- {comment['template_description']}")
        lines.append(f"     Topics: {', '.join(comment['relevant_topics'])}")
        lines.append(f"     Note: {comment['note']}")
        lines.append("")

    # Section 3: Instructions
    lines.append("--- HOW TO RESPOND ---")
    lines.append("Post: 'post approved' / 'post edit: [changes]'")
    lines.append("Comments: 'comment 1 approved' / 'comment 5 edit: make it shorter'")
    lines.append("Batch: 'all comments approved' / 'comments 1-10 approved'")
    lines.append("Skip: 'skip comment 4' (target not active today)")
    lines.append("")
    lines.append("After approval, posts schedule at optimal time (10-11 AM ET).")
    lines.append("Comments drip at 1 per 3 minutes via PureSurf.")

    return "\n".join(lines)


# -- PureSurf Execution Functions -------------------------------------------

async def schedule_post_on_puresurf(post_text, image_path=None, schedule_time=None):
    """
    Schedule an approved post on PureSurf.
    Returns the post ID for tracking.
    """
    import aiohttp

    if schedule_time is None:
        # Default: today at 10:30 AM ET
        et = timezone(timedelta(hours=-4))
        now = datetime.now(et)
        schedule_time = now.replace(hour=10, minute=30, second=0).isoformat()

    payload = {
        "content": post_text,
        "platforms": ["linkedin"],
        "schedule": schedule_time,
        "profile_names": {"linkedin": LINKEDIN_PROFILE},
        "auto_publish": False,  # Require manual publish trigger
    }

    # If image provided, upload to PureSurf media first
    media_ids = []
    if image_path and os.path.exists(image_path):
        import base64
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{PURESURF_BASE}/social/adapters/media/upload",
                headers={"X-API-Key": PURESURF_KEY_JARED, "Content-Type": "application/json"},
                json={"data": img_data, "filename": os.path.basename(image_path)},
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    media_ids.append(result.get("media_id", ""))

    if media_ids:
        payload["media"] = media_ids

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{PURESURF_BASE}/social/posts",
            headers={"X-API-Key": PURESURF_KEY_JARED, "Content-Type": "application/json"},
            json=payload,
        ) as resp:
            result = await resp.json()
            return result


async def execute_comment_drip(comments, interval_seconds=180):
    """
    Execute approved comments via PureSurf, dripping at specified interval.
    Each comment:
      1. Opens LinkedIn session
      2. Navigates to target's recent post
      3. Types and submits comment
      4. Waits interval before next
    """
    import aiohttp

    results = []
    for i, comment in enumerate(comments):
        if comment.get("status") != "approved":
            continue

        # Create session for commenting
        async with aiohttp.ClientSession() as session:
            # Navigate to target profile's activity
            activity_url = comment["target_url"].rstrip("/") + "/recent-activity/all/"

            result = {
                "target": comment["target_name"],
                "action": "comment",
                "status": "queued",
                "scheduled_offset_seconds": i * interval_seconds,
                "activity_url": activity_url,
                "comment_text": comment.get("final_text", comment.get("draft_pattern", "")),
            }
            results.append(result)

        # In actual execution, we would:
        # 1. POST /sessions to create jared-linkedin session
        # 2. POST /sessions/{sid}/navigate to go to activity_url
        # 3. Find the latest post, click comment
        # 4. POST /sessions/{sid}/type to enter comment text
        # 5. Click submit
        # 6. Wait interval_seconds before next

    return results


# -- Main Pipeline ----------------------------------------------------------

def run_pipeline(dry_run=False, skip_image=False, skip_comments=False):
    """
    Main pipeline execution.
    Generates the daily package and saves to portal-files.
    """
    today_str = get_today_str()
    print(f"[LinkedIn Daily Pipeline] Generating package for {today_str}")

    # Step 1: Generate post topics
    print("[1/4] Generating post topics...")
    post_data = generate_post_topics()

    # Step 2: Select comment targets
    print("[2/4] Selecting comment targets...")
    if not skip_comments:
        targets = select_comment_targets(25)
        comments = [draft_comment_for_target(t) for t in targets]
    else:
        comments = []
        print("  (skipped)")

    # Step 3: Format portal message
    print("[3/4] Formatting portal delivery...")
    portal_message = format_portal_message(post_data, comments, today_str)

    # Step 4: Save outputs
    print("[4/4] Saving outputs...")

    # Save the portal message
    portal_file = PORTAL_FILES / f"linkedin-daily-{today_str}.txt"
    portal_file.write_text(portal_message)
    print(f"  Portal message: {portal_file}")

    # Save structured JSON for programmatic access
    json_file = PORTAL_FILES / f"linkedin-daily-{today_str}.json"
    package = {
        "date": today_str,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "post": post_data,
        "comments": comments,
        "comment_count": len(comments),
        "tier_breakdown": {
            "tier_1": len([c for c in comments if c.get("tier") == 1]),
            "tier_2": len([c for c in comments if c.get("tier") == 2]),
            "tier_3": len([c for c in comments if c.get("tier") == 3]),
        },
        "puresurf_status": {
            "profile": LINKEDIN_PROFILE,
            "api_base": PURESURF_BASE,
            "session_ready": False,  # Will be set True after session verification
        },
    }
    json_file.write_text(json.dumps(package, indent=2))
    print(f"  JSON data: {json_file}")

    # Save the daily state for tracking approvals
    state_file = CIV_ROOT / ".linkedin_daily_state.json"
    state = {
        "date": today_str,
        "post_status": "pending_review",
        "comments_status": {str(i): "pending_review" for i in range(1, len(comments) + 1)},
        "portal_file": str(portal_file),
        "json_file": str(json_file),
    }
    state_file.write_text(json.dumps(state, indent=2))
    print(f"  State file: {state_file}")

    if dry_run:
        print("\n[DRY RUN] Would deliver to portal:")
        print(f"  [FILE: {portal_file}]")
        print(f"\n  First 20 lines of portal message:")
        for line in portal_message.split("\n")[:20]:
            print(f"    {line}")
    else:
        print(f"\n[READY] Deliver to portal with:")
        print(f"  [FILE: {portal_file}]")

    print(f"\nPackage complete: {len(comments)} comment targets across "
          f"{package['tier_breakdown']['tier_1']} T1 / "
          f"{package['tier_breakdown']['tier_2']} T2 / "
          f"{package['tier_breakdown']['tier_3']} T3")

    return package


# -- Approval Processing ----------------------------------------------------

def process_approval(approval_text):
    """
    Process Jared's approval response.
    Examples:
      'post approved' -> approve post
      'comment 3 approved' -> approve comment 3
      'all comments approved' -> approve all
      'comments 1-10 approved' -> approve range
      'comment 5 edit: make it shorter' -> flag for edit
      'skip comment 4' -> skip
    """
    state_file = CIV_ROOT / ".linkedin_daily_state.json"
    if not state_file.exists():
        return {"error": "No daily state found. Run pipeline first."}

    state = json.loads(state_file.read_text())
    text = approval_text.strip().lower()
    changes = []

    if "post approved" in text:
        state["post_status"] = "approved"
        changes.append("Post approved")

    if "all comments approved" in text:
        for k in state["comments_status"]:
            state["comments_status"][k] = "approved"
        changes.append("All comments approved")

    # Range approval: 'comments 1-10 approved'
    import re
    range_match = re.search(r"comments?\s+(\d+)\s*-\s*(\d+)\s+approved", text)
    if range_match:
        start, end = int(range_match.group(1)), int(range_match.group(2))
        for i in range(start, end + 1):
            if str(i) in state["comments_status"]:
                state["comments_status"][str(i)] = "approved"
        changes.append(f"Comments {start}-{end} approved")

    # Single approval: 'comment 3 approved'
    single_match = re.search(r"comment\s+(\d+)\s+approved", text)
    if single_match:
        idx = single_match.group(1)
        if idx in state["comments_status"]:
            state["comments_status"][idx] = "approved"
            changes.append(f"Comment {idx} approved")

    # Edit: 'comment 5 edit: ...'
    edit_match = re.search(r"comment\s+(\d+)\s+edit:\s*(.+)", text)
    if edit_match:
        idx = edit_match.group(1)
        edit_note = edit_match.group(2)
        if idx in state["comments_status"]:
            state["comments_status"][idx] = f"edit_requested:{edit_note}"
            changes.append(f"Comment {idx} edit requested: {edit_note}")

    # Skip: 'skip comment 4'
    skip_match = re.search(r"skip\s+comment\s+(\d+)", text)
    if skip_match:
        idx = skip_match.group(1)
        if idx in state["comments_status"]:
            state["comments_status"][idx] = "skipped"
            changes.append(f"Comment {idx} skipped")

    state_file.write_text(json.dumps(state, indent=2))
    return {"changes": changes, "state": state}


# -- Entry Point ------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    skip_image = "--skip-image" in args
    skip_comments = "--skip-comments" in args

    package = run_pipeline(
        dry_run=dry_run,
        skip_image=skip_image,
        skip_comments=skip_comments,
    )
