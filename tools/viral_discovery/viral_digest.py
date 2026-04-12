#!/usr/bin/env python3
"""
Viral Content Digest Generator

Generates actionable daily digest from viral content discovery.
Outputs markdown report with:
- Top posts to engage with
- Trending topics for content creation
- Competitor activity
- Piggybacking opportunities

Can sync to Google Drive for easy access.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from viral_discovery.viral_discovery import ViralContentDiscovery, ViralContent

# Try to import GDrive manager
try:
    from gdrive_manager import GDriveManager
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False


def generate_daily_digest(
    discovery: Optional[ViralContentDiscovery] = None,
    run_discovery: bool = True,
    platforms: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
    sync_gdrive: bool = False,
    gdrive_path: str = "AI Productivity Reports/Viral Content"
) -> str:
    """
    Generate actionable daily digest of viral content.

    Args:
        discovery: Existing ViralContentDiscovery instance (or create new)
        run_discovery: Whether to run fresh discovery
        platforms: Platforms to include
        output_dir: Local output directory (default: docs/viral-digest)
        sync_gdrive: Upload to Google Drive
        gdrive_path: Google Drive folder path

    Returns:
        Path to generated digest file
    """
    if discovery is None:
        discovery = ViralContentDiscovery()

    if run_discovery:
        discovery.discover_all(platforms=platforms)

    # Generate markdown digest
    digest = _build_digest_markdown(discovery)

    # Output paths
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"Daily-Digest-{today}.md"

    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path(__file__).parent.parent.parent / "docs" / "viral-digest"

    output_path.mkdir(parents=True, exist_ok=True)
    filepath = output_path / filename

    with open(filepath, "w") as f:
        f.write(digest)

    print(f"\nDigest saved to: {filepath}")

    # Sync to Google Drive if requested
    if sync_gdrive and GDRIVE_AVAILABLE:
        try:
            gdrive = GDriveManager()
            file_id = gdrive.upload_to_path(
                str(filepath),
                gdrive_path,
                root_folder_name="CTO"
            )
            print(f"Uploaded to Google Drive: {file_id}")
        except Exception as e:
            print(f"GDrive sync failed: {e}")

    return str(filepath)


def _build_digest_markdown(discovery: ViralContentDiscovery) -> str:
    """Build the markdown digest content."""
    today = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M")

    lines = [
        f"# VIRAL CONTENT DIGEST - {today}",
        "",
        f"**Generated**: {today} at {time_str}",
        f"**Purpose**: Actionable content for engagement, reposting, and trend-riding",
        "",
        "---",
        "",
    ]

    # LinkedIn Section
    if "linkedin" in discovery.results and discovery.results["linkedin"]:
        lines.extend(_linkedin_section(discovery.results["linkedin"]))

    # Twitter Section
    if "twitter" in discovery.results and discovery.results["twitter"]:
        lines.extend(_twitter_section(discovery.results["twitter"]))

    # Reddit Section
    if "reddit" in discovery.results and discovery.results["reddit"]:
        lines.extend(_reddit_section(discovery.results["reddit"]))

    # TikTok Section
    if "tiktok" in discovery.results and discovery.results["tiktok"]:
        lines.extend(_tiktok_section(discovery.results["tiktok"]))

    # Instagram Section
    if "instagram" in discovery.results and discovery.results["instagram"]:
        lines.extend(_instagram_section(discovery.results["instagram"]))

    # Top Opportunities (cross-platform)
    lines.extend(_top_opportunities_section(discovery))

    # Quick Actions Summary
    lines.extend(_quick_actions_section(discovery))

    return "\n".join(lines)


def _linkedin_section(content: List[ViralContent]) -> List[str]:
    """Generate LinkedIn section of digest."""
    lines = [
        "## LinkedIn Hot Posts (engage/comment today)",
        "",
    ]

    # Top 5 by engagement
    top_posts = sorted(
        content,
        key=lambda x: x.engagement.get("reactions", 0),
        reverse=True
    )[:5]

    for i, post in enumerate(top_posts, 1):
        reactions = post.engagement.get("reactions", 0)
        comments = post.engagement.get("comments", 0)
        relevance = post.relevance_score

        lines.append(f"### {i}. {post.author}")
        lines.append(f"**Engagement**: {reactions:,} reactions, {comments} comments")
        lines.append(f"**Relevance Score**: {relevance:.0f}/100")
        lines.append(f"**Categories**: {', '.join(post.categories)}")
        lines.append("")
        lines.append(f"> {post.text[:300]}...")
        lines.append("")
        if post.url:
            lines.append(f"**Link**: [{post.url[:50]}...]({post.url})")
        lines.append("")

        # Action suggestion
        if relevance >= 70:
            lines.append("**ACTION**: High relevance - comment with our POV on this topic")
        elif relevance >= 40:
            lines.append("**ACTION**: Moderate relevance - like and consider sharing")
        else:
            lines.append("**ACTION**: Low relevance - monitor only")
        lines.append("")

    return lines


def _twitter_section(content: List[ViralContent]) -> List[str]:
    """Generate Twitter section of digest."""
    lines = [
        "## Twitter Trending (quote tweet opportunities)",
        "",
    ]

    top_tweets = sorted(
        content,
        key=lambda x: x.engagement.get("retweets", 0),
        reverse=True
    )[:5]

    for i, tweet in enumerate(top_tweets, 1):
        retweets = tweet.engagement.get("retweets", 0)
        likes = tweet.engagement.get("likes", 0)

        lines.append(f"### {i}. @{tweet.author}")
        lines.append(f"**Stats**: {retweets} RTs, {likes} likes")
        lines.append(f"**Keywords**: {', '.join(tweet.keywords_matched[:3])}")
        lines.append("")
        lines.append(f"> {tweet.text[:280]}")
        lines.append("")
        if tweet.url:
            lines.append(f"**Link**: {tweet.url}")
        lines.append("")

        if tweet.relevance_score >= 60:
            lines.append("**ACTION**: Quote tweet with our perspective")
        else:
            lines.append("**ACTION**: Engage (like/reply)")
        lines.append("")

    return lines


def _reddit_section(content: List[ViralContent]) -> List[str]:
    """Generate Reddit section of digest."""
    lines = [
        "## Reddit Discussions (add value/reference)",
        "",
    ]

    top_posts = sorted(
        content,
        key=lambda x: x.engagement.get("upvotes", 0),
        reverse=True
    )[:5]

    for i, post in enumerate(top_posts, 1):
        upvotes = post.engagement.get("upvotes", 0)
        comments = post.engagement.get("comments", 0)

        lines.append(f"### {i}. {post.title[:80]}...")
        lines.append(f"**Stats**: {upvotes:,} upvotes, {comments} comments")
        lines.append(f"**Relevance**: {post.relevance_score:.0f}/100")
        lines.append("")
        if post.text:
            lines.append(f"> {post.text[:200]}...")
            lines.append("")
        if post.url:
            lines.append(f"**Link**: {post.url}")
        lines.append("")

        if post.relevance_score >= 50:
            lines.append("**ACTION**: Comment with insights/case study")
        else:
            lines.append("**ACTION**: Reference for content ideas")
        lines.append("")

    return lines


def _tiktok_section(content: List[ViralContent]) -> List[str]:
    """Generate TikTok section of digest."""
    lines = [
        "## TikTok Trends (content ideas)",
        "",
    ]

    top_videos = sorted(
        content,
        key=lambda x: x.engagement.get("views", 0),
        reverse=True
    )[:5]

    for i, video in enumerate(top_videos, 1):
        views = video.engagement.get("views", 0)
        likes = video.engagement.get("likes", 0)

        lines.append(f"### {i}. @{video.author}")
        lines.append(f"**Stats**: {views:,} views, {likes:,} likes")
        lines.append(f"**Categories**: {', '.join(video.categories)}")
        lines.append("")
        lines.append(f"> {video.text[:200]}...")
        lines.append("")
        if video.url:
            lines.append(f"**Link**: {video.url}")
        lines.append("")
        lines.append("**CONTENT IDEA**: Create similar format for our niche")
        lines.append("")

    return lines


def _instagram_section(content: List[ViralContent]) -> List[str]:
    """Generate Instagram section of digest."""
    lines = [
        "## Instagram Activations (brand inspiration)",
        "",
    ]

    top_posts = sorted(
        content,
        key=lambda x: x.engagement.get("likes", 0),
        reverse=True
    )[:5]

    for i, post in enumerate(top_posts, 1):
        likes = post.engagement.get("likes", 0)
        comments = post.engagement.get("comments", 0)

        lines.append(f"### {i}. @{post.author}")
        lines.append(f"**Stats**: {likes:,} likes, {comments} comments")
        lines.append(f"**Categories**: {', '.join(post.categories)}")
        lines.append("")
        lines.append(f"> {post.text[:200]}...")
        lines.append("")
        if post.url:
            lines.append(f"**Link**: {post.url}")
        lines.append("")

    return lines


def _top_opportunities_section(discovery: ViralContentDiscovery) -> List[str]:
    """Generate top cross-platform opportunities."""
    lines = [
        "---",
        "",
        "## TOP OPPORTUNITIES (All Platforms)",
        "",
        "Highest relevance content to engage with today:",
        "",
    ]

    top_content = discovery.get_top_content(limit=10)

    for i, content in enumerate(top_content, 1):
        platform_emoji = {
            "linkedin": "L",
            "twitter": "T",
            "reddit": "R",
            "tiktok": "TT",
            "instagram": "IG"
        }.get(content.platform, "?")

        lines.append(f"{i}. **[{platform_emoji}]** {content.author} - {content.text[:60]}...")
        lines.append(f"   Relevance: {content.relevance_score:.0f}/100 | {content.url[:50] if content.url else 'no url'}...")
        lines.append("")

    return lines


def _quick_actions_section(discovery: ViralContentDiscovery) -> List[str]:
    """Generate quick actions summary."""
    lines = [
        "---",
        "",
        "## QUICK ACTIONS CHECKLIST",
        "",
    ]

    # Count high-relevance items per platform
    actions = []

    for platform, content in discovery.results.items():
        high_relevance = [c for c in content if c.relevance_score >= 60]
        if high_relevance:
            actions.append(f"- [ ] **{platform.title()}**: Engage with {len(high_relevance)} high-relevance posts")

    lines.extend(actions)

    lines.extend([
        "",
        "### Content Creation Ideas",
        "",
    ])

    # Collect trending categories across all content
    all_categories = []
    for content in discovery.results.values():
        for c in content:
            all_categories.extend(c.categories)

    # Count and sort categories
    from collections import Counter
    category_counts = Counter(all_categories)
    top_categories = category_counts.most_common(5)

    for category, count in top_categories:
        lines.append(f"- [ ] Create content about: **{category.replace('_', ' ').title()}** ({count} trending posts)")

    lines.extend([
        "",
        "---",
        "",
        f"*Generated by Viral Content Discovery System*",
        f"*{datetime.now().strftime('%Y-%m-%d %H:%M')}*",
    ])

    return lines


# ============================================================================
# CLI
# ============================================================================

def main():
    """Command-line interface for digest generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Viral Content Digest")
    parser.add_argument("--no-discovery", action="store_true",
                        help="Skip discovery (use cached results)")
    parser.add_argument("--platforms", type=str, nargs="+",
                        help="Platforms to include")
    parser.add_argument("--output", type=str,
                        help="Output directory")
    parser.add_argument("--sync-gdrive", action="store_true",
                        help="Upload to Google Drive")
    parser.add_argument("--gdrive-path", type=str,
                        default="AI Productivity Reports/Viral Content",
                        help="Google Drive folder path")

    args = parser.parse_args()

    filepath = generate_daily_digest(
        run_discovery=not args.no_discovery,
        platforms=args.platforms,
        output_dir=args.output,
        sync_gdrive=args.sync_gdrive,
        gdrive_path=args.gdrive_path
    )

    print(f"\nDigest complete: {filepath}")


if __name__ == "__main__":
    main()
