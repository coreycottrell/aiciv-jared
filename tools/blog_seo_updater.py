#!/usr/bin/env python3
"""
Blog Post SEO Updater for purebrain.ai

Fetches all published posts and generates SEO improvements:
  1. FAQ schema markup (JSON-LD) for posts with Q&A content
  2. Meta descriptions (under 155 characters, compelling)
  3. Internal links between topically related posts

Usage:
    # Dry-run (default - reads only, generates plan):
    python tools/blog_seo_updater.py

    # Apply updates to live site:
    python tools/blog_seo_updater.py --apply

    # Dry-run for a single post by ID:
    python tools/blog_seo_updater.py --post-id 42

    # Save dry-run report to custom path:
    python tools/blog_seo_updater.py --report /path/to/report.md

Requirements:
    pip install requests beautifulsoup4

Credentials:
    Hardcoded for purebrain.ai / Aether account.
    App password: FlFr2VOtlHiHaJWjzW96OHUJ
"""

import argparse
import html
import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 not installed. Run: pip install beautifulsoup4")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WP_BASE_URL = "https://purebrain.ai"
WP_API_BASE = f"{WP_BASE_URL}/wp-json/wp/v2"
WP_AUTH = ("Aether", "FlFr2VOtlHiHaJWjzW96OHUJ")

RATE_LIMIT_SECONDS = 3       # Minimum seconds between API writes
FETCH_DELAY_SECONDS = 0.5    # Delay between read requests

DEFAULT_REPORT_PATH = Path(__file__).parent.parent / "exports" / "seo-update-plan.md"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("blog_seo_updater")

# ---------------------------------------------------------------------------
# Keyword / Topic Map
# ---------------------------------------------------------------------------

# Keywords each post type should target, keyed by topic slug.
# Values are lists of keyword strings and related topic slugs that link here.
KEYWORD_MAP = {
    "memory": {
        "target_keywords": ["AI that remembers you", "AI memory for business"],
        "related_topics": ["partnership", "relationship"],
        "description": "posts about AI memory, continuity, remembering context"
    },
    "partnership": {
        "target_keywords": ["naming your AI assistant", "personal AI relationship"],
        "related_topics": ["memory", "awakening"],
        "description": "posts about human-AI partnership, naming, awakening"
    },
    "awakening": {
        "target_keywords": ["naming your AI assistant", "personal AI relationship"],
        "related_topics": ["partnership", "memory"],
        "description": "posts about first moments, awakening, the fork metaphor"
    },
    "enterprise": {
        "target_keywords": ["AI pilot purgatory", "why AI projects fail"],
        "related_topics": ["failure", "roi"],
        "description": "posts about enterprise AI adoption, scale, business"
    },
    "failure": {
        "target_keywords": ["AI pilot purgatory", "why AI projects fail"],
        "related_topics": ["enterprise", "roi"],
        "description": "posts about AI project failures, pilot purgatory"
    },
    "relationship": {
        "target_keywords": ["personal AI relationship", "AI that remembers you"],
        "related_topics": ["memory", "partnership"],
        "description": "posts about building ongoing AI relationships"
    },
    "roi": {
        "target_keywords": ["why AI projects fail", "AI memory for business"],
        "related_topics": ["enterprise", "failure"],
        "description": "posts about AI ROI, business value, measurement"
    }
}

# Question-signal words that trigger FAQ schema detection
FAQ_QUESTION_STARTERS = (
    "what", "how", "why", "when", "can", "is", "are", "does", "do",
    "will", "should", "which", "where", "who"
)

# ---------------------------------------------------------------------------
# WordPress API helpers
# ---------------------------------------------------------------------------

def fetch_all_published_posts() -> list[dict]:
    """
    Fetch every published post from purebrain.ai via WordPress REST API.
    Handles pagination automatically.
    Returns list of raw post dicts from the API.
    """
    posts = []
    page = 1
    per_page = 100

    log.info("Fetching all published posts from %s ...", WP_BASE_URL)

    while True:
        params = {
            "status": "publish",
            "per_page": per_page,
            "page": page,
            "_fields": (
                "id,slug,link,title,content,excerpt,meta,"
                "date,modified,categories,tags,yoast_head_json"
            )
        }
        try:
            resp = requests.get(
                f"{WP_API_BASE}/posts",
                auth=WP_AUTH,
                params=params,
                timeout=30
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            log.error("Failed to fetch posts (page %d): %s", page, exc)
            break

        batch = resp.json()
        if not batch:
            break

        posts.extend(batch)
        log.info("  Fetched page %d: %d posts (total so far: %d)", page, len(batch), len(posts))

        # Check if there are more pages via X-WP-TotalPages header
        total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break

        page += 1
        time.sleep(FETCH_DELAY_SECONDS)

    log.info("Total published posts fetched: %d", len(posts))
    return posts


def fetch_post_meta(post_id: int) -> dict:
    """
    Fetch meta fields for a post (including Yoast SEO meta description).
    Returns dict of meta key -> value.
    """
    try:
        resp = requests.get(
            f"{WP_API_BASE}/posts/{post_id}",
            auth=WP_AUTH,
            params={"context": "edit", "_fields": "meta"},
            timeout=20
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("meta", {})
    except requests.RequestException as exc:
        log.warning("Failed to fetch meta for post %d: %s", post_id, exc)
    return {}


def update_post(post_id: int, payload: dict) -> tuple[bool, str]:
    """
    POST an update to a single WordPress post.
    Returns (success: bool, message: str).
    """
    try:
        resp = requests.post(
            f"{WP_API_BASE}/posts/{post_id}",
            auth=WP_AUTH,
            json=payload,
            timeout=60
        )
        if resp.status_code in (200, 201):
            return True, f"HTTP {resp.status_code} OK"
        else:
            return False, f"HTTP {resp.status_code}: {resp.text[:300]}"
    except requests.RequestException as exc:
        return False, str(exc)

# ---------------------------------------------------------------------------
# Content parsing helpers
# ---------------------------------------------------------------------------

def strip_html(raw_html: str) -> str:
    """Return plain text from an HTML string."""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def get_post_title(post: dict) -> str:
    """Extract the rendered title string."""
    title_obj = post.get("title", {})
    if isinstance(title_obj, dict):
        return html.unescape(title_obj.get("rendered", ""))
    return str(title_obj)


def get_post_content_html(post: dict) -> str:
    """Extract the raw (unrendered) content HTML for editing."""
    content_obj = post.get("content", {})
    if isinstance(content_obj, dict):
        return content_obj.get("raw", content_obj.get("rendered", ""))
    return str(content_obj)


def get_post_content_rendered(post: dict) -> str:
    """Extract the rendered content HTML."""
    content_obj = post.get("content", {})
    if isinstance(content_obj, dict):
        return content_obj.get("rendered", "")
    return str(content_obj)


def get_post_excerpt(post: dict) -> str:
    """Extract the post excerpt (plain text)."""
    exc_obj = post.get("excerpt", {})
    if isinstance(exc_obj, dict):
        raw = exc_obj.get("rendered", "")
    else:
        raw = str(exc_obj)
    return strip_html(raw)

# ---------------------------------------------------------------------------
# FAQ Schema detection & generation
# ---------------------------------------------------------------------------

def extract_faq_pairs(content_html: str) -> list[dict]:
    """
    Parse the post HTML for question/answer pairs.

    Detection rules:
      1. H2 or H3 elements that end with "?" — treated as questions.
         The answer is the concatenated text of all following siblings
         until the next heading.
      2. Paragraphs that start with a FAQ_QUESTION_STARTERS word and end "?"
         are treated as questions; the immediately following <p> is the answer.

    Returns list of {"question": str, "answer": str} dicts.
    """
    soup = BeautifulSoup(content_html, "html.parser")
    pairs = []
    seen_questions = set()

    # --- Strategy 1: Heading-based Q&A ---
    headings = soup.find_all(["h2", "h3"])
    for heading in headings:
        q_text = heading.get_text(strip=True)
        if not q_text.endswith("?"):
            continue
        if q_text.lower() in seen_questions:
            continue

        # Collect answer text from following siblings until next heading
        answer_parts = []
        for sibling in heading.find_next_siblings():
            if sibling.name in ("h1", "h2", "h3", "h4"):
                break
            text = sibling.get_text(separator=" ", strip=True)
            if text:
                answer_parts.append(text)
            if len(" ".join(answer_parts)) > 600:
                break

        answer_text = " ".join(answer_parts).strip()
        if answer_text and len(answer_text) > 20:
            pairs.append({"question": q_text, "answer": answer_text[:500]})
            seen_questions.add(q_text.lower())

    # --- Strategy 2: Paragraph-based Q&A ---
    paragraphs = soup.find_all("p")
    for i, p in enumerate(paragraphs):
        p_text = p.get_text(strip=True)
        if not p_text:
            continue

        first_word = p_text.split()[0].lower().rstrip("?:,")
        is_question = (
            p_text.endswith("?")
            and first_word in FAQ_QUESTION_STARTERS
            and len(p_text) < 200
        )
        if not is_question:
            continue
        if p_text.lower() in seen_questions:
            continue

        # Next non-empty paragraph is the answer
        answer_text = ""
        for j in range(i + 1, min(i + 4, len(paragraphs))):
            candidate = paragraphs[j].get_text(strip=True)
            if candidate and not candidate.endswith("?"):
                answer_text = candidate[:500]
                break

        if answer_text and len(answer_text) > 20:
            pairs.append({"question": p_text, "answer": answer_text})
            seen_questions.add(p_text.lower())

    return pairs


def build_faq_schema(faq_pairs: list[dict]) -> str:
    """
    Build a JSON-LD FAQPage schema script tag from extracted Q&A pairs.
    Returns the raw <script> HTML string.
    """
    entities = []
    for pair in faq_pairs:
        entities.append({
            "@type": "Question",
            "name": pair["question"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": pair["answer"]
            }
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities
    }

    schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
    return (
        "\n\n<!-- FAQ Schema: auto-generated by blog_seo_updater.py -->\n"
        f'<script type="application/ld+json">\n{schema_json}\n</script>'
    )


def has_existing_faq_schema(content_html: str) -> bool:
    """
    Return True if content already contains a JSON-LD FAQPage schema.
    Idempotency check — do not add schema if it is already present.
    """
    return (
        '"@type": "FAQPage"' in content_html
        or '"@type":"FAQPage"' in content_html
    )

# ---------------------------------------------------------------------------
# Meta description generation
# ---------------------------------------------------------------------------

def classify_post_topic(title: str, content_text: str) -> str:
    """
    Classify a post into one of the topic slugs in KEYWORD_MAP.
    Uses simple keyword matching on title + first 500 chars of content.
    Returns topic slug string, or "general" if no match.
    """
    probe = (title + " " + content_text[:500]).lower()

    topic_signals = {
        "memory": ["memory", "remembers", "remember", "context", "continuity", "forget"],
        "partnership": ["partner", "naming", "name", "relationship", "colleague", "working with"],
        "awakening": ["awaken", "fork", "born", "first session", "first moment", "identity"],
        "enterprise": ["enterprise", "organization", "company", "ceo", "executive", "corporate", "scale"],
        "failure": ["fail", "purgatory", "stuck", "pilot", "abandoned", "doesn't work", "dead end"],
        "relationship": ["relationship", "personal ai", "trust", "ongoing", "bond"],
        "roi": ["roi", "return on investment", "value", "productivity", "efficiency", "cost"]
    }

    scores = {topic: 0 for topic in topic_signals}
    for topic, signals in topic_signals.items():
        for signal in signals:
            if signal in probe:
                scores[topic] += 1

    best_topic = max(scores, key=scores.get)
    if scores[best_topic] == 0:
        return "general"
    return best_topic


def generate_meta_description(title: str, content_text: str, topic: str) -> str:
    """
    Generate a compelling meta description under 155 characters.

    Strategy:
      - Use first non-trivial sentence from content as base.
      - Append a relevant hook/CTA based on topic.
      - Trim to 155 chars, never cutting mid-word.
    """
    topic_ctas = {
        "memory": "Discover AI that actually remembers you.",
        "partnership": "Meet the AI built for real partnership.",
        "awakening": "What if your AI had a name — and a mind?",
        "enterprise": "Why most enterprise AI projects fail — and how to fix it.",
        "failure": "Escape AI pilot purgatory with PureBrain.",
        "relationship": "Build an AI relationship that grows with you.",
        "roi": "Real ROI from AI starts with the right relationship.",
        "general": "PureBrain.ai — AI that knows you, not just your prompts."
    }

    # Extract first meaningful sentence from content
    sentences = re.split(r'(?<=[.!?])\s+', content_text.strip())
    base_sentence = ""
    for sent in sentences:
        clean = sent.strip()
        # Skip very short or heading-like sentences
        if len(clean) > 40 and not clean.isupper():
            base_sentence = clean
            break

    # Build description
    cta = topic_ctas.get(topic, topic_ctas["general"])
    candidate = f"{base_sentence} {cta}".strip() if base_sentence else cta

    # Truncate to 155 chars at a word boundary
    if len(candidate) > 155:
        truncated = candidate[:152]
        last_space = truncated.rfind(" ")
        if last_space > 100:
            truncated = truncated[:last_space]
        candidate = truncated.rstrip(".,;:") + "..."

    return candidate


def get_existing_yoast_meta_desc(post_meta: dict) -> str:
    """
    Return the existing Yoast meta description if already set.
    Returns empty string if not present.
    """
    return (
        post_meta.get("_yoast_wpseo_metadesc")
        or post_meta.get("yoast_wpseo_metadesc")
        or ""
    )

# ---------------------------------------------------------------------------
# Internal linking
# ---------------------------------------------------------------------------

def build_topic_index(posts: list[dict]) -> dict[int, dict]:
    """
    Build a {post_id: {topic, title, url, slug}} index for all posts.
    Used to generate internal link recommendations.
    """
    index = {}
    for post in posts:
        post_id = post["id"]
        title = get_post_title(post)
        content_text = strip_html(get_post_content_rendered(post))
        topic = classify_post_topic(title, content_text)
        index[post_id] = {
            "topic": topic,
            "title": title,
            "url": post.get("link", ""),
            "slug": post.get("slug", "")
        }
    return index


def find_related_posts(
    post_id: int,
    post_topic: str,
    topic_index: dict[int, dict],
    max_links: int = 3
) -> list[dict]:
    """
    Find up to `max_links` related posts to link to from this post.

    Strategy:
      1. First, find posts with the same topic (exclude self).
      2. Then, find posts with topics in KEYWORD_MAP[topic]["related_topics"].
    """
    related_topics = set()
    related_topics.add(post_topic)
    if post_topic in KEYWORD_MAP:
        for rt in KEYWORD_MAP[post_topic].get("related_topics", []):
            related_topics.add(rt)

    candidates = []
    for pid, info in topic_index.items():
        if pid == post_id:
            continue
        if info["topic"] in related_topics and info["url"]:
            candidates.append(info)

    # Limit to max_links; prefer same-topic first
    same_topic = [c for c in candidates if c["topic"] == post_topic]
    other_topic = [c for c in candidates if c["topic"] != post_topic]
    ordered = same_topic + other_topic
    return ordered[:max_links]


def build_related_reading_section(related_posts: list[dict]) -> str:
    """
    Build a "Related Reading" HTML section to append at the end of a post.
    Uses <hr> separator and an unordered list of links.
    """
    if not related_posts:
        return ""

    items = "\n".join(
        f'<li><a href="{p["url"]}">{html.escape(p["title"])}</a></li>'
        for p in related_posts
    )

    return (
        "\n\n<!-- Internal Links: auto-generated by blog_seo_updater.py -->\n"
        "<hr>\n"
        "<p><strong>Related Reading</strong></p>\n"
        f"<ul>\n{items}\n</ul>"
    )


def has_existing_related_section(content_html: str) -> bool:
    """
    Check whether content already has a blog_seo_updater-generated related section.
    Idempotency check.
    """
    return "Internal Links: auto-generated by blog_seo_updater.py" in content_html

# ---------------------------------------------------------------------------
# Core analysis engine
# ---------------------------------------------------------------------------

def analyse_post(
    post: dict,
    post_meta: dict,
    topic_index: dict[int, dict]
) -> dict:
    """
    Analyse a single post and compute all proposed SEO changes.

    Returns a dict with:
      - post_id, title, url, topic
      - faq_pairs: list of detected Q&A pairs
      - faq_schema_html: <script> tag string (or empty if not applicable)
      - meta_description: proposed meta description (or existing if already set)
      - related_posts: list of related post info dicts
      - related_section_html: HTML for related reading block
      - changes: list of human-readable change descriptions
      - content_updated: bool (True if content needs changing)
      - meta_updated: bool (True if meta description needs setting)
    """
    post_id = post["id"]
    title = get_post_title(post)
    url = post.get("link", "")
    content_html = get_post_content_rendered(post)
    content_text = strip_html(content_html)
    topic = topic_index.get(post_id, {}).get("topic", "general")

    result = {
        "post_id": post_id,
        "title": title,
        "url": url,
        "topic": topic,
        "faq_pairs": [],
        "faq_schema_html": "",
        "meta_description": "",
        "meta_description_source": "",
        "related_posts": [],
        "related_section_html": "",
        "changes": [],
        "content_updated": False,
        "meta_updated": False
    }

    # --- FAQ Schema ---
    if has_existing_faq_schema(content_html):
        result["changes"].append("FAQ schema: already present (skipped)")
    else:
        faq_pairs = extract_faq_pairs(content_html)
        if faq_pairs:
            result["faq_pairs"] = faq_pairs
            result["faq_schema_html"] = build_faq_schema(faq_pairs)
            result["content_updated"] = True
            result["changes"].append(
                f"FAQ schema: ADD ({len(faq_pairs)} Q&A pairs detected)"
            )
        else:
            result["changes"].append("FAQ schema: no Q&A patterns detected (skipped)")

    # --- Meta Description ---
    existing_meta = get_existing_yoast_meta_desc(post_meta)
    existing_excerpt = get_post_excerpt(post)

    if existing_meta and len(existing_meta) <= 155:
        result["meta_description"] = existing_meta
        result["meta_description_source"] = "existing_yoast"
        result["changes"].append(
            f"Meta description: already set via Yoast ({len(existing_meta)} chars, kept)"
        )
    elif existing_excerpt and len(existing_excerpt) <= 155:
        # Already has a decent excerpt - propose keeping it unless too long
        result["meta_description"] = existing_excerpt
        result["meta_description_source"] = "existing_excerpt"
        result["changes"].append(
            f"Meta description: existing excerpt is OK ({len(existing_excerpt)} chars, kept)"
        )
    else:
        # Generate a new one
        new_meta = generate_meta_description(title, content_text, topic)
        result["meta_description"] = new_meta
        result["meta_description_source"] = "generated"
        result["meta_updated"] = True
        result["changes"].append(
            f"Meta description: GENERATE '{new_meta[:80]}...' ({len(new_meta)} chars)"
        )

    # --- Internal Links ---
    if has_existing_related_section(content_html):
        result["changes"].append("Internal links: related section already present (skipped)")
    else:
        related = find_related_posts(post_id, topic, topic_index, max_links=3)
        if related:
            result["related_posts"] = related
            result["related_section_html"] = build_related_reading_section(related)
            result["content_updated"] = True
            link_titles = ", ".join(f'"{r["title"]}"' for r in related)
            result["changes"].append(
                f"Internal links: ADD {len(related)} links -> {link_titles}"
            )
        else:
            result["changes"].append("Internal links: no related posts found (skipped)")

    return result


def build_updated_content(post: dict, analysis: dict) -> str:
    """
    Assemble the updated content HTML by appending FAQ schema and
    related-reading section to the existing content.

    Uses the rendered HTML as base (which is what the API returns).
    Appends generated blocks at the end.
    NOTE: Does NOT re-inject existing content — only appends new blocks.
    """
    content_html = get_post_content_rendered(post)

    if analysis["faq_schema_html"]:
        content_html = content_html + analysis["faq_schema_html"]

    if analysis["related_section_html"]:
        content_html = content_html + analysis["related_section_html"]

    return content_html

# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_dry_run_report(
    analyses: list[dict],
    report_path: Path
) -> str:
    """
    Generate a markdown dry-run report and write it to `report_path`.
    Returns the report text.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(analyses)
    content_changes = sum(1 for a in analyses if a["content_updated"])
    meta_changes = sum(1 for a in analyses if a["meta_updated"])

    lines = [
        "# PureBrain.ai SEO Update Plan",
        "",
        f"**Generated**: {now}",
        f"**Site**: {WP_BASE_URL}",
        f"**Total posts analysed**: {total}",
        f"**Posts requiring content update**: {content_changes}",
        f"**Posts requiring meta description update**: {meta_changes}",
        "",
        "---",
        "",
        "## Summary of Changes",
        "",
        "| Post ID | Title | Topic | Changes |",
        "|---------|-------|-------|---------|",
    ]

    for a in analyses:
        title_short = a["title"][:50] + ("..." if len(a["title"]) > 50 else "")
        changes_short = "; ".join(a["changes"])[:80]
        lines.append(
            f"| {a['post_id']} | [{title_short}]({a['url']}) | {a['topic']} | {changes_short} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Detailed Post Analysis",
        ""
    ]

    for a in analyses:
        lines += [
            f"### Post {a['post_id']}: {a['title']}",
            "",
            f"- **URL**: {a['url']}",
            f"- **Topic**: {a['topic']}",
            f"- **Content update needed**: {'YES' if a['content_updated'] else 'No'}",
            f"- **Meta update needed**: {'YES' if a['meta_updated'] else 'No'}",
            "",
            "**Proposed changes:**",
            ""
        ]

        for change in a["changes"]:
            lines.append(f"- {change}")

        if a["faq_pairs"]:
            lines += [
                "",
                f"**FAQ pairs detected ({len(a['faq_pairs'])}):**",
                ""
            ]
            for pair in a["faq_pairs"]:
                q_short = pair["question"][:100]
                a_short = pair["answer"][:100] + ("..." if len(pair["answer"]) > 100 else "")
                lines.append(f"- Q: *{q_short}*")
                lines.append(f"  A: {a_short}")

        if a["meta_description"]:
            lines += [
                "",
                f"**Meta description** ({a['meta_description_source']}, "
                f"{len(a['meta_description'])} chars):",
                f"> {a['meta_description']}",
                ""
            ]

        if a["related_posts"]:
            lines += [
                "**Internal links to add:**",
                ""
            ]
            for rp in a["related_posts"]:
                lines.append(f"- [{rp['title']}]({rp['url']}) (topic: {rp['topic']})")

        lines += ["", "---", ""]

    # Keyword targeting section
    lines += [
        "## Keyword Targeting Map",
        "",
        "| Keyword | Target Topic | Posts in Topic |",
        "|---------|-------------|----------------|"
    ]
    topic_post_counts = {}
    for a in analyses:
        topic_post_counts[a["topic"]] = topic_post_counts.get(a["topic"], 0) + 1

    for topic, info in KEYWORD_MAP.items():
        count = topic_post_counts.get(topic, 0)
        for kw in info["target_keywords"]:
            lines.append(f'| "{kw}" | {topic} | {count} posts |')

    lines += [
        "",
        "---",
        "",
        "## Next Steps",
        "",
        "1. Review this plan and confirm accuracy of FAQ detection.",
        "2. Review proposed meta descriptions for brand voice.",
        "3. Review internal link suggestions for topical accuracy.",
        "4. Run with `--apply` flag to execute updates:",
        "   ```",
        "   python tools/blog_seo_updater.py --apply",
        "   ```",
        "5. Verify changes on purebrain.ai after apply.",
        "",
        "---",
        "",
        "_Report generated by `tools/blog_seo_updater.py`_"
    ]

    report_text = "\n".join(lines)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8")
    log.info("Dry-run report saved to: %s", report_path)
    return report_text

# ---------------------------------------------------------------------------
# Apply updates
# ---------------------------------------------------------------------------

def apply_updates(analyses: list[dict], posts_by_id: dict[int, dict]) -> None:
    """
    Apply SEO updates to live posts. Only called with --apply flag.
    Updates content (FAQ schema + internal links) and meta description.
    Rate-limited to RATE_LIMIT_SECONDS between writes.
    """
    log.info("=== APPLY MODE: Writing updates to %s ===", WP_BASE_URL)
    log.warning("This will modify live posts. Rate limit: %ds between writes.", RATE_LIMIT_SECONDS)

    updates_needed = [a for a in analyses if a["content_updated"] or a["meta_updated"]]
    log.info("Posts to update: %d of %d", len(updates_needed), len(analyses))

    for i, analysis in enumerate(updates_needed, start=1):
        post_id = analysis["post_id"]
        title = analysis["title"]
        log.info("[%d/%d] Updating post %d: %s", i, len(updates_needed), post_id, title)

        post = posts_by_id.get(post_id)
        if not post:
            log.error("  Post %d not found in cache — skipping.", post_id)
            continue

        payload = {}

        # Build updated content if needed
        if analysis["content_updated"]:
            updated_content = build_updated_content(post, analysis)
            payload["content"] = updated_content
            log.info("  Content updated: +%d chars", len(updated_content) - len(get_post_content_rendered(post)))

        # Set meta description
        if analysis["meta_updated"]:
            meta_desc = analysis["meta_description"]
            # Try Yoast first via meta field, then fall back to excerpt
            payload["meta"] = {"_yoast_wpseo_metadesc": meta_desc}
            payload["excerpt"] = meta_desc
            log.info("  Meta description set: %s", meta_desc[:80])

        if not payload:
            log.info("  No payload to send — skipping.")
            continue

        success, message = update_post(post_id, payload)
        if success:
            log.info("  SUCCESS: %s", message)
        else:
            log.error("  FAILED: %s", message)

        # Rate limit
        if i < len(updates_needed):
            log.info("  Waiting %ds before next update...", RATE_LIMIT_SECONDS)
            time.sleep(RATE_LIMIT_SECONDS)

    log.info("=== Apply complete ===")

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Blog Post SEO Updater for purebrain.ai\n"
            "Generates FAQ schema, meta descriptions, and internal links."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  Dry-run (default):\n"
            "    python tools/blog_seo_updater.py\n\n"
            "  Apply updates to live site:\n"
            "    python tools/blog_seo_updater.py --apply\n\n"
            "  Analyse a single post:\n"
            "    python tools/blog_seo_updater.py --post-id 42\n\n"
            "  Custom report path:\n"
            "    python tools/blog_seo_updater.py --report /tmp/seo-plan.md\n"
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Actually write updates to WordPress. Default: dry-run only."
    )
    parser.add_argument(
        "--post-id",
        type=int,
        default=None,
        help="Only process this specific post ID."
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Path for dry-run report. Default: {DEFAULT_REPORT_PATH}"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose debug logging."
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    mode = "APPLY" if args.apply else "DRY-RUN"
    log.info("=== Blog SEO Updater starting in %s mode ===", mode)

    # Step 1: Fetch all posts
    all_posts = fetch_all_published_posts()
    if not all_posts:
        log.error("No posts fetched. Check credentials and site connectivity.")
        return 1

    # Filter to single post if requested
    if args.post_id is not None:
        all_posts = [p for p in all_posts if p["id"] == args.post_id]
        if not all_posts:
            log.error("Post ID %d not found in published posts.", args.post_id)
            return 1
        log.info("Filtered to post ID %d.", args.post_id)

    # Build lookup dict
    posts_by_id = {p["id"]: p for p in all_posts}

    # Step 2: Build topic index (needs all posts for linking)
    log.info("Building topic index...")
    topic_index = build_topic_index(all_posts)

    # Print topic distribution
    topic_counts: dict[str, int] = {}
    for info in topic_index.values():
        topic_counts[info["topic"]] = topic_counts.get(info["topic"], 0) + 1
    log.info("Topic distribution: %s", json.dumps(topic_counts, indent=2))

    # Step 3: Analyse each post
    log.info("Analysing %d posts...", len(all_posts))
    analyses = []

    for i, post in enumerate(all_posts, start=1):
        post_id = post["id"]
        title = get_post_title(post)
        log.info("[%d/%d] Analysing post %d: %s", i, len(all_posts), post_id, title)

        # Fetch meta (separate API call for edit-context meta fields)
        post_meta = fetch_post_meta(post_id)
        time.sleep(FETCH_DELAY_SECONDS)

        analysis = analyse_post(post, post_meta, topic_index)
        analyses.append(analysis)

        for change in analysis["changes"]:
            log.info("  -> %s", change)

    # Step 4: Generate dry-run report (always)
    log.info("Generating dry-run report...")
    generate_dry_run_report(analyses, args.report)

    # Print summary
    content_changes = sum(1 for a in analyses if a["content_updated"])
    meta_changes = sum(1 for a in analyses if a["meta_updated"])
    faq_added = sum(1 for a in analyses if a["faq_schema_html"])
    links_added = sum(1 for a in analyses if a["related_posts"])

    print("\n" + "=" * 60)
    print("SEO ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Posts analysed:              {len(analyses)}")
    print(f"Would add FAQ schema:        {faq_added}")
    print(f"Would add internal links:    {links_added}")
    print(f"Would update meta desc:      {meta_changes}")
    print(f"Total posts with changes:    {content_changes + meta_changes}")
    print(f"\nDry-run report saved to:\n  {args.report}")
    print("=" * 60)

    if not args.apply:
        print(
            "\nDRY-RUN MODE: No changes made to the live site.\n"
            "Review the report, then run with --apply to execute updates."
        )
        return 0

    # Step 5: Apply updates (only if --apply)
    confirm = input(
        f"\nAbout to update {content_changes + meta_changes} posts on {WP_BASE_URL}.\n"
        "Type 'yes' to proceed, anything else to cancel: "
    ).strip().lower()

    if confirm != "yes":
        log.info("Update cancelled by user.")
        return 0

    apply_updates(analyses, posts_by_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
