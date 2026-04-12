#!/usr/bin/env python3
"""
inject_faq_schema.py — Add FAQPage JSON-LD schema to blog posts that have FAQ content
but no structured data.

Task 2 assigned by CTO.
Author: full-stack-developer
Date: 2026-03-09

Posts to fix (purebrain.ai):
  1245 — The AI That Forgets You
  1189 — Age of AI Agents: Team of AIs
  1139 — Your AI Doesn't Work For You
  1084 — AI Doesn't Make Your Team Smarter
  966  — First 90 Days of AI Partnership
  950  — Your AI Has No Memory

Posts to fix (jareddsanborn.com):
  1222 — The AI That Forgets You (mirror of 1245)
  1220, 1216, 1212, 1210, 1207, 1195, + others from audit

IMPORTANT: This script reads each post first, parses the FAQ structure,
builds the JSON-LD, then injects it at the END of post_content (before the
closing </article> tag or at the very end). The plugin's auto-schema (v5.8.0)
will skip these posts once schema is present in post_content.
"""

import os
import re
import json
import base64
import time
import urllib.request
import urllib.parse
import urllib.error
from html.parser import HTMLParser
from pathlib import Path
from dotenv import load_dotenv

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
load_dotenv(AETHER_ROOT / ".env")

# ─── Credentials ─────────────────────────────────────────────────────────────

PB_BASE  = "https://purebrain.ai"
PB_USER  = os.environ.get("PUREBRAIN_WP_USER", "purebrain@puremarketing.ai")
PB_PASS  = os.environ.get("PUREBRAIN_WP_APP_PASSWORD", "")

JDS_BASE = "https://jareddsanborn.com"
JDS_USER = os.environ.get("WORDPRESS_USER", "jared")
JDS_PASS = os.environ.get("WORDPRESS_APP_PASSWORD", "")

# ─── Post lists ──────────────────────────────────────────────────────────────

PB_POSTS = [1245, 1189, 1139, 1084, 966, 950]

# JDS post IDs — from audit: has FAQ + accordion, no schema (4 posts)
# + has FAQ, no schema, no accordion (3 posts) + potential others
# Audit listed 10 JDS posts with FAQ but no schema — we'll detect all at runtime
JDS_POSTS = []  # Will be populated by scanning all JDS posts with FAQ


# ─── HTML FAQ parser ─────────────────────────────────────────────────────────

class FAQHTMLParser(HTMLParser):
    """
    Parse FAQ Q&A pairs from post HTML content.
    Handles multiple structures used across purebrain.ai posts.
    """

    def __init__(self):
        super().__init__()
        self.pairs = []
        self._in_faq_section = False
        self._in_pb_faq_item = False
        self._in_question_tag = False
        self._in_answer_tag = False
        self._current_question = ""
        self._current_answer = ""
        self._current_tag = None
        self._after_faq_h2 = False
        self._in_h3_after_faq = False
        self._pending_h3 = ""
        self._depth_faq_section = 0
        self._depth_pb_faq_item = 0

    def _add_pair(self, q, a):
        q = q.strip()
        a = a.strip()
        if q and a:
            # Avoid duplicates
            for existing_q, _ in self.pairs:
                if existing_q == q:
                    return
            self.pairs.append((q, a))

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = attrs_dict.get("class", "")

        # Structure A: .faq-section
        if "faq-section" in classes:
            self._in_faq_section = True
            self._current_question = ""
            self._current_answer = ""
            return

        # Structure B: .pb-faq-item
        if "pb-faq-item" in classes:
            self._in_pb_faq_item = True
            self._current_question = ""
            self._current_answer = ""
            return

        if self._in_faq_section or self._in_pb_faq_item:
            if tag in ("h3", "h4") and (
                "pb-faq-q" in classes or self._in_faq_section
            ):
                self._in_question_tag = True
                self._current_tag = tag
            elif "pb-faq-q" in classes:
                self._in_question_tag = True
                self._current_tag = tag
            elif "pb-faq-a" in classes:
                self._in_answer_tag = True
                self._current_tag = tag
            elif tag == "p" and self._in_faq_section and self._current_question:
                self._in_answer_tag = True
                self._current_tag = tag

        # Structure D: h2 containing FAQ text, followed by h3+p
        if tag == "h2":
            # Will check text in handle_data
            self._potential_faq_h2 = True
            self._h2_text = ""

        if self._after_faq_h2 and tag == "h3":
            self._in_h3_after_faq = True
            self._pending_h3 = ""

    def handle_endtag(self, tag):
        if self._in_question_tag and tag == self._current_tag:
            self._in_question_tag = False

        if self._in_answer_tag and tag == self._current_tag:
            self._in_answer_tag = False
            if self._in_faq_section and self._current_question and self._current_answer:
                self._add_pair(self._current_question, self._current_answer)
                self._current_question = ""
                self._current_answer = ""
            elif self._in_pb_faq_item and self._current_question and self._current_answer:
                self._add_pair(self._current_question, self._current_answer)

        if tag in ("div", "section"):
            if self._in_faq_section:
                self._in_faq_section = False
            if self._in_pb_faq_item:
                self._in_pb_faq_item = False
                self._current_question = ""
                self._current_answer = ""

        if self._in_h3_after_faq and tag == "h3":
            self._in_h3_after_faq = False

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return

        if self._in_question_tag:
            self._current_question += " " + data
        elif self._in_answer_tag:
            self._current_answer += " " + data

        # Track h2 text for Structure D detection
        if hasattr(self, "_potential_faq_h2") and self._potential_faq_h2:
            self._h2_text += data
            if "faq" in self._h2_text.lower() or "frequently asked" in self._h2_text.lower():
                self._after_faq_h2 = True
            self._potential_faq_h2 = False

        if self._in_h3_after_faq:
            self._pending_h3 += data


def parse_faq_from_html(html_content):
    """
    Parse FAQ Q&A pairs from post HTML.
    Returns list of (question, answer) tuples.
    """
    # Try HTMLParser approach
    parser = FAQHTMLParser()
    parser.feed(html_content)

    if parser.pairs:
        return parser.pairs

    # Fallback: regex-based extraction for .faq-section h3 + p
    pairs = []

    # Pattern A: <div class="faq-section"><h3>Q</h3><p>A</p></div>
    faq_section_pattern = re.compile(
        r'<div[^>]+class="[^"]*faq-section[^"]*"[^>]*>(.*?)</div>',
        re.DOTALL | re.IGNORECASE
    )
    h3_pattern = re.compile(r'<h[34][^>]*>(.*?)</h[34]>', re.DOTALL | re.IGNORECASE)
    p_pattern  = re.compile(r'<p[^>]*>(.*?)</p>', re.DOTALL | re.IGNORECASE)

    for section_match in faq_section_pattern.finditer(html_content):
        section_html = section_match.group(1)
        h_match = h3_pattern.search(section_html)
        p_match = p_pattern.search(section_html)
        if h_match and p_match:
            question = re.sub(r'<[^>]+>', '', h_match.group(1)).strip()
            answer   = re.sub(r'<[^>]+>', '', p_match.group(1)).strip()
            if question and answer:
                pairs.append((question, answer))

    if pairs:
        return pairs

    # Pattern B: .pb-faq-item
    pb_item_pattern = re.compile(
        r'<(?:div|p)[^>]+class="[^"]*pb-faq-item[^"]*"[^>]*>(.*?)</(?:div|p)>',
        re.DOTALL | re.IGNORECASE
    )
    pb_q_pattern = re.compile(r'class="[^"]*pb-faq-q[^"]*"[^>]*>(.*?)</', re.DOTALL | re.IGNORECASE)
    pb_a_pattern = re.compile(r'class="[^"]*pb-faq-a[^"]*"[^>]*>(.*?)</', re.DOTALL | re.IGNORECASE)

    for item_match in pb_item_pattern.finditer(html_content):
        item_html = item_match.group(1)
        q_match = pb_q_pattern.search(item_html)
        a_match = pb_a_pattern.search(item_html)
        if q_match and a_match:
            question = re.sub(r'<[^>]+>', '', q_match.group(1)).strip()
            answer   = re.sub(r'<[^>]+>', '', a_match.group(1)).strip()
            if question and answer:
                pairs.append((question, answer))

    if pairs:
        return pairs

    # Pattern D: bare h3+p after <h2>FAQ</h2>
    faq_h2_match = re.search(
        r'<h2[^>]*>[^<]*(?:FAQ|Frequently Asked)[^<]*</h2>(.*?)(?=<h[12]|$)',
        html_content, re.DOTALL | re.IGNORECASE
    )
    if faq_h2_match:
        faq_block = faq_h2_match.group(1)
        qa_pairs = re.findall(
            r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>',
            faq_block, re.DOTALL | re.IGNORECASE
        )
        for q_html, a_html in qa_pairs:
            q = re.sub(r'<[^>]+>', '', q_html).strip()
            a = re.sub(r'<[^>]+>', '', a_html).strip()
            if q and a:
                pairs.append((q, a))

    return pairs


def build_faq_schema(pairs, post_url=""):
    """Build FAQPage JSON-LD schema from Q&A pairs."""
    entities = []
    for question, answer in pairs:
        entities.append({
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": answer
            }
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities
    }

    return json.dumps(schema, ensure_ascii=False, indent=2)


def wp_auth_header(user, app_password):
    """Return Basic Auth header value."""
    token = base64.b64encode(f"{user}:{app_password}".encode()).decode()
    return f"Basic {token}"


def fetch_post(base_url, post_id, auth_header):
    """Fetch post content via WP REST API."""
    url = f"{base_url}/wp-json/wp/v2/posts/{post_id}?context=edit"
    req = urllib.request.Request(url, headers={
        "Authorization": auth_header,
        "User-Agent": "PureBrain-FAQSchema/1.0"
    })
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  ERROR fetching post {post_id}: HTTP {e.code}")
        return None
    except Exception as e:
        print(f"  ERROR fetching post {post_id}: {e}")
        return None


def update_post_content(base_url, post_id, new_content, auth_header):
    """Update post content via WP REST API."""
    url = f"{base_url}/wp-json/wp/v2/posts/{post_id}"
    payload = json.dumps({"content": new_content}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "User-Agent": "PureBrain-FAQSchema/1.0"
        }
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode("utf-8"))
        return result
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  ERROR updating post {post_id}: HTTP {e.code}")
        print(f"  Body: {body[:200]}")
        return None
    except Exception as e:
        print(f"  ERROR updating post {post_id}: {e}")
        return None


def verify_post_schema(base_url, post_id, auth_header):
    """Verify schema was injected into the post."""
    post_data = fetch_post(base_url, post_id, auth_header)
    if not post_data:
        return False
    content = post_data.get("content", {}).get("raw", "")
    return '"FAQPage"' in content or "'FAQPage'" in content


def process_post(base_url, post_id, auth_header, site_label):
    """Process a single post: read, parse FAQ, inject schema."""
    print(f"\n--- {site_label} Post {post_id} ---")

    # Step 1: Read post
    print(f"  Reading post {post_id}...")
    post_data = fetch_post(base_url, post_id, auth_header)
    if not post_data:
        print(f"  SKIP: Could not fetch post")
        return False

    title = post_data.get("title", {}).get("rendered", "Unknown")
    print(f"  Title: {title}")

    # Get raw content (the actual stored HTML)
    content_raw = post_data.get("content", {}).get("raw", "")
    if not content_raw:
        print(f"  SKIP: Empty post content")
        return False

    # Step 2: Check if schema already exists
    if '"FAQPage"' in content_raw or "'FAQPage'" in content_raw:
        print(f"  SKIP: FAQPage schema already present in post content")
        return True

    # Step 3: Parse FAQ pairs
    print(f"  Parsing FAQ from content ({len(content_raw)} chars)...")
    faq_pairs = parse_faq_from_html(content_raw)

    if not faq_pairs:
        print(f"  WARNING: No FAQ pairs found in post {post_id}. Logging structure for manual review.")
        # Log a sample of the content to help diagnose
        sample = content_raw[:500].replace('\n', ' ')
        print(f"  Content sample: {sample}")
        return False

    print(f"  Found {len(faq_pairs)} FAQ pairs:")
    for i, (q, a) in enumerate(faq_pairs, 1):
        print(f"    {i}. Q: {q[:60]}...")
        print(f"       A: {a[:80]}...")

    # Step 4: Build JSON-LD schema
    schema_json = build_faq_schema(faq_pairs)
    schema_block = f'\n\n<script type="application/ld+json">\n{schema_json}\n</script>'

    # Step 5: Inject schema at end of post content
    # We inject BEFORE the closing </article> tag if present, otherwise at end
    if '</article>' in content_raw:
        new_content = content_raw.replace('</article>', f'{schema_block}\n</article>', 1)
    elif '<!-- /wp:html -->' in content_raw:
        # wp:html wrapped content
        new_content = content_raw.replace('<!-- /wp:html -->', f'{schema_block}\n<!-- /wp:html -->', 1)
    else:
        new_content = content_raw + schema_block

    print(f"  Injecting schema ({len(schema_block)} chars) into post...")

    # Step 6: Update post
    result = update_post_content(base_url, post_id, new_content, auth_header)
    if not result:
        print(f"  FAILED: Post update returned no result")
        return False

    # Step 7: Verify
    print(f"  Verifying schema in post content...")
    time.sleep(2)
    verified = verify_post_schema(base_url, post_id, auth_header)
    if verified:
        print(f"  VERIFIED: Schema present in post {post_id}")
    else:
        print(f"  WARNING: Could not verify schema in post {post_id} — check manually")

    return verified


def get_jds_posts_needing_schema(auth_header):
    """
    Scan JDS posts to find those with FAQ content but no schema.
    Returns list of post IDs.
    """
    print("\n[JDS] Scanning for posts needing schema...")
    url = f"{JDS_BASE}/wp-json/wp/v2/posts?per_page=50&context=edit"
    req = urllib.request.Request(url, headers={
        "Authorization": auth_header,
        "User-Agent": "PureBrain-FAQSchema/1.0"
    })
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        posts = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ERROR fetching JDS post list: {e}")
        return []

    needs_schema = []
    for post in posts:
        post_id = post["id"]
        content_raw = post.get("content", {}).get("raw", "")
        if not content_raw:
            continue

        has_faq = any(pattern in content_raw.lower() for pattern in [
            'faq-section', 'pb-faq-item', 'frequently asked', '<h2>faq',
            'faq</h2>', 'faq</'
        ])
        has_schema = '"FAQPage"' in content_raw or "'FAQPage'" in content_raw

        if has_faq and not has_schema:
            title = post.get("title", {}).get("rendered", "Unknown")
            print(f"  Found JDS post needing schema: {post_id} — {title}")
            needs_schema.append(post_id)

    return needs_schema


def send_telegram(message):
    """Send status update to Telegram."""
    try:
        config = json.loads(
            (AETHER_ROOT / "config/telegram_config.json").read_text()
        )
        token = config["bot_token"]
        data = urllib.parse.urlencode({
            "chat_id": "548906264",
            "text": message,
        }).encode()
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            timeout=10
        )
    except Exception as e:
        print(f"  Telegram send failed: {e}")


def main():
    print("=" * 60)
    print("FAQ JSON-LD Schema Injection Tool")
    print("Task 2 — Full-Stack Developer")
    print("=" * 60)

    results = {"pb": {}, "jds": {}}

    pb_auth  = wp_auth_header(PB_USER, PB_PASS)
    jds_auth = wp_auth_header(JDS_USER, JDS_PASS)

    if not PB_PASS:
        print("ERROR: PUREBRAIN_WP_APP_PASSWORD not set")
        return
    if not JDS_PASS:
        print("ERROR: WORDPRESS_APP_PASSWORD not set")
        return

    send_telegram("[CTO] Task 2 starting: FAQ JSON-LD schema injection for 6 purebrain.ai + JDS posts...")

    # ─── purebrain.ai ────────────────────────────────────────────────────────
    print("\n" + "=" * 40)
    print("PUREBRAIN.AI")
    print("=" * 40)

    pb_success = 0
    pb_failed = []
    pb_skipped = []

    for post_id in PB_POSTS:
        success = process_post(PB_BASE, post_id, pb_auth, "purebrain.ai")
        if success:
            pb_success += 1
            results["pb"][post_id] = "DONE"
        else:
            post_data = fetch_post(PB_BASE, post_id, pb_auth)
            if post_data:
                content_raw = post_data.get("content", {}).get("raw", "")
                if '"FAQPage"' in content_raw:
                    pb_skipped.append(post_id)
                    results["pb"][post_id] = "SKIPPED (already has schema)"
                else:
                    pb_failed.append(post_id)
                    results["pb"][post_id] = "FAILED"
            else:
                pb_failed.append(post_id)
                results["pb"][post_id] = "FAILED"
        time.sleep(1)

    # ─── jareddsanborn.com ───────────────────────────────────────────────────
    print("\n" + "=" * 40)
    print("JAREDDSANBORN.COM")
    print("=" * 40)

    jds_post_ids = get_jds_posts_needing_schema(jds_auth)
    if not jds_post_ids:
        print("No JDS posts found needing schema (or scan failed).")

    jds_success = 0
    jds_failed = []

    for post_id in jds_post_ids:
        success = process_post(JDS_BASE, post_id, jds_auth, "jareddsanborn.com")
        if success:
            jds_success += 1
            results["jds"][post_id] = "DONE"
        else:
            results["jds"][post_id] = "FAILED"
            jds_failed.append(post_id)
        time.sleep(1)

    # ─── Summary ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("TASK 2 SUMMARY")
    print("=" * 60)
    print(f"\npurebrain.ai:")
    print(f"  Success: {pb_success}/{len(PB_POSTS)}")
    if pb_failed:
        print(f"  Failed (manual review needed): {pb_failed}")
    if pb_skipped:
        print(f"  Skipped (already had schema): {pb_skipped}")

    print(f"\njareddsanborn.com:")
    print(f"  Success: {jds_success}/{len(jds_post_ids)}")
    if jds_failed:
        print(f"  Failed (manual review needed): {jds_failed}")

    print(f"\nFull results: {json.dumps(results, indent=2)}")

    # Save results
    results_path = AETHER_ROOT / "exports/departments/systems-technology/reports/2026-03-09--faq-schema-injection-results.json"
    results_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to: {results_path}")

    msg = (
        f"[CTO] Task 2 COMPLETE: FAQ schema injection. "
        f"purebrain.ai: {pb_success}/{len(PB_POSTS)} posts done. "
        f"JDS: {jds_success}/{len(jds_post_ids)} posts done."
    )
    if pb_failed or jds_failed:
        msg += f" MANUAL REVIEW NEEDED: PB={pb_failed}, JDS={jds_failed}"
    send_telegram(msg)


if __name__ == "__main__":
    main()
