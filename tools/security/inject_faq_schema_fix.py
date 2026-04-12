#!/usr/bin/env python3
"""
inject_faq_schema_fix.py — Fix FAQ schema injection for posts that failed
due to non-standard FAQ structures not caught by original parser.

Posts:
  purebrain.ai:
    1245 — faq-item with <button class="faq-question"> + <div class="faq-answer">
    966  — bare <p><strong>Q:...</strong></p><p>answer</p> after <h2>Frequently Asked Questions</h2>
    950  — bare <p><strong>Q:...</strong></p><p>A: answer</p> after <h2>FAQ</h2>

  jareddsanborn.com:
    1222 — same as 1245 (faq-item + button.faq-question structure)
    1216 — bare <p><strong>question</strong></p><p>answer</p> after <h2>Frequently Asked Questions</h2>
    1212 — faq-item with <p class="faq-question"> + <p>answer</p>
    1210 — same as 966
    1207 — same as 950
"""

import os, json, re, time, requests
from pathlib import Path
from dotenv import load_dotenv

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
load_dotenv(AETHER_ROOT / ".env")

PB_BASE   = "https://purebrain.ai"
PB_USER   = os.getenv("PUREBRAIN_WP_USER")
PB_PASS   = os.getenv("PUREBRAIN_WP_APP_PASSWORD")

JDS_BASE  = "https://jareddsanborn.com"
JDS_USER  = os.getenv("WORDPRESS_USER")
JDS_PASS  = os.getenv("WORDPRESS_APP_PASSWORD")

REPORT_DIR = AETHER_ROOT / "exports/departments/systems-technology/reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ─── Parsers for the three new structures ────────────────────────────────────

def parse_faq_button_style(content):
    """
    Structure: .faq-item > <button class="faq-question">Q text</button>
                          > <div class="faq-answer">A text</div>
    Used in: PB 1245, JDS 1222
    """
    pairs = []
    item_pattern = re.compile(
        r'<div[^>]+class="[^"]*faq-item[^"]*"[^>]*>(.*?)</div>\s*</div>',
        re.DOTALL | re.IGNORECASE
    )
    btn_pattern = re.compile(
        r'<button[^>]+class="[^"]*faq-question[^"]*"[^>]*>(.*?)</button>',
        re.DOTALL | re.IGNORECASE
    )
    ans_pattern = re.compile(
        r'<div[^>]+class="[^"]*faq-answer[^"]*"[^>]*>(.*?)</div>',
        re.DOTALL | re.IGNORECASE
    )
    for item in item_pattern.finditer(content):
        item_html = item.group(1)
        bm = btn_pattern.search(item_html)
        am = ans_pattern.search(item_html)
        if bm and am:
            q = re.sub(r'<[^>]+>', '', bm.group(1)).strip()
            a = re.sub(r'<[^>]+>', '', am.group(1)).strip()
            q = re.sub(r'\s+', ' ', q)
            a = re.sub(r'\s+', ' ', a)
            if q and a:
                pairs.append((q, a))
    return pairs


def parse_faq_p_question_class(content):
    """
    Structure: .faq-item > <p class="faq-question">Q text</p>
                         > <p>A text</p>
    Used in: JDS 1212
    """
    pairs = []
    # Find all faq-item divs (non-greedy)
    item_pattern = re.compile(
        r'<div[^>]+class="[^"]*faq-item[^"]*"[^>]*>(.*?)</div>',
        re.DOTALL | re.IGNORECASE
    )
    pq_pattern = re.compile(
        r'<p[^>]+class="[^"]*faq-question[^"]*"[^>]*>(.*?)</p>',
        re.DOTALL | re.IGNORECASE
    )
    pa_pattern = re.compile(r'<p(?![^>]*class="faq)[^>]*>(.*?)</p>', re.DOTALL | re.IGNORECASE)
    for item in item_pattern.finditer(content):
        item_html = item.group(1)
        qm = pq_pattern.search(item_html)
        # Answer is the first <p> without faq-question class
        am = pa_pattern.search(item_html)
        if qm and am:
            q = re.sub(r'<[^>]+>', '', qm.group(1)).strip()
            a = re.sub(r'<[^>]+>', '', am.group(1)).strip()
            q = re.sub(r'\s+', ' ', q)
            a = re.sub(r'\s+', ' ', a)
            if q and a:
                pairs.append((q, a))
    return pairs


def parse_faq_strong_qa_format(content):
    """
    Structure after <h2>FAQ</h2> or <h2>Frequently Asked Questions</h2>:
      <p><strong>Q: question text</strong></p>
      <p>A: answer text</p>
      OR
      <p>answer text (no A: prefix)</p>

    Also handles no Q:/A: prefix — just strong question + plain answer.
    Used in: PB 966, PB 950, JDS 1210, JDS 1207, JDS 1216
    """
    pairs = []
    # Find the FAQ h2 section
    faq_h2 = re.search(
        r'<h2[^>]*>[^<]*(?:FAQ|Frequently Asked(?:\s+Questions)?)[^<]*</h2>',
        content, re.IGNORECASE
    )
    if not faq_h2:
        return pairs

    # Extract everything after the FAQ h2 until next h2 or end
    after = content[faq_h2.end():]
    next_section = re.search(r'<h2[^>]*>', after, re.IGNORECASE)
    if next_section:
        after = after[:next_section.start()]

    # Strategy 1: <p><strong>Q: question</strong></p> then <p>A: answer or plain answer</p>
    # Strategy 2: <p><strong>question (no Q: prefix)</strong></p> then <p>answer</p>
    p_tags = re.findall(r'<p[^>]*>(.*?)</p>', after, re.DOTALL | re.IGNORECASE)

    i = 0
    while i < len(p_tags):
        p_content = p_tags[i]
        p_text = re.sub(r'<[^>]+>', '', p_content).strip()
        p_text = re.sub(r'\s+', ' ', p_text)

        # Check if this <p> contains a <strong> (question)
        has_strong = bool(re.search(r'<strong[^>]*>', p_content, re.IGNORECASE))

        if has_strong and i + 1 < len(p_tags):
            question = p_text
            # Strip leading Q: prefix
            question = re.sub(r'^Q:\s*', '', question, flags=re.IGNORECASE).strip()

            answer_raw = p_tags[i + 1]
            answer = re.sub(r'<[^>]+>', '', answer_raw).strip()
            answer = re.sub(r'\s+', ' ', answer)
            # Strip leading A: prefix
            answer = re.sub(r'^A:\s*', '', answer, flags=re.IGNORECASE).strip()

            if question and answer and len(answer) > 20:
                pairs.append((question, answer))
                i += 2
                continue
        i += 1

    return pairs


def parse_all_structures(content):
    """Try all parsers, return the best result."""
    # Try button style first (most specific)
    pairs = parse_faq_button_style(content)
    if pairs:
        return pairs, "button-faq-item"

    # Try p.faq-question class
    pairs = parse_faq_p_question_class(content)
    if pairs:
        return pairs, "p-faq-question-class"

    # Try strong Q/A format after h2
    pairs = parse_faq_strong_qa_format(content)
    if pairs:
        return pairs, "strong-qa-after-h2"

    return [], "none"


def build_schema(pairs):
    entities = []
    for q, a in pairs:
        entities.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}
        })
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities},
                      ensure_ascii=False, indent=2)


def has_schema(content):
    return '"FAQPage"' in content or "'FAQPage'" in content


def fetch_post(base_url, post_id, auth):
    r = requests.get(f"{base_url}/wp-json/wp/v2/posts/{post_id}?context=edit",
                     auth=auth, timeout=30)
    if r.status_code != 200:
        print(f"  ERROR: HTTP {r.status_code}")
        return None
    return r.json()


def update_post(base_url, post_id, new_content, auth):
    r = requests.post(f"{base_url}/wp-json/wp/v2/posts/{post_id}",
                      auth=auth,
                      json={"content": new_content},
                      timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ERROR: HTTP {r.status_code} — {r.text[:200]}")
        return None
    return r.json()


def send_telegram(message):
    try:
        config = json.loads((AETHER_ROOT / "config/telegram_config.json").read_text())
        requests.post(
            f"https://api.telegram.org/bot{config['bot_token']}/sendMessage",
            json={"chat_id": "548906264", "text": message},
            timeout=10
        )
    except Exception as e:
        print(f"  Telegram failed: {e}")


def process_post(base_url, post_id, auth, label):
    print(f"\n--- {label} Post {post_id} ---")

    data = fetch_post(base_url, post_id, auth)
    if not data:
        return False, "fetch_failed"

    title = data.get("title", {}).get("rendered", "")
    print(f"  Title: {title}")

    content = data.get("content", {}).get("raw", "")
    if not content:
        return False, "empty_content"

    if has_schema(content):
        print(f"  SKIP: Schema already present")
        return True, "already_done"

    pairs, structure_used = parse_all_structures(content)
    print(f"  Structure detected: {structure_used}")

    if not pairs:
        print(f"  FAIL: Could not parse FAQ pairs")
        return False, "no_pairs_found"

    print(f"  Parsed {len(pairs)} FAQ pairs:")
    for i, (q, a) in enumerate(pairs, 1):
        print(f"    {i}. Q: {q[:70]}")
        print(f"       A: {a[:90]}")

    schema_json = build_schema(pairs)
    schema_block = f'\n\n<script type="application/ld+json">\n{schema_json}\n</script>'

    # Inject: prefer before </article>, else before <!-- /wp:html -->, else at end
    if '</article>' in content:
        new_content = content.replace('</article>', f'{schema_block}\n</article>', 1)
    elif '<!-- /wp:html -->' in content:
        new_content = content.replace('<!-- /wp:html -->', f'{schema_block}\n<!-- /wp:html -->', 1)
    else:
        new_content = content + schema_block

    print(f"  Updating post...")
    result = update_post(base_url, post_id, new_content, auth)
    if not result:
        return False, "update_failed"

    time.sleep(2)

    # Verify
    verify_data = fetch_post(base_url, post_id, auth)
    if not verify_data:
        return False, "verify_fetch_failed"

    verified_content = verify_data.get("content", {}).get("raw", "")
    if has_schema(verified_content):
        print(f"  VERIFIED: Schema present in post content")
        return True, "done"
    else:
        print(f"  WARNING: Schema not found after update — check manually")
        return False, "verify_failed"


def main():
    print("=" * 60)
    print("FAQ Schema Injection — Fix Run")
    print("Processing posts that failed the initial parse")
    print("=" * 60)

    pb_auth  = (PB_USER, PB_PASS)
    jds_auth = (JDS_USER, JDS_PASS)

    send_telegram("[CTO] Task 2 fix-run: Injecting FAQ schema on 8 posts with non-standard FAQ structure...")

    results = {}

    # PB posts that failed
    pb_targets = [1245, 966, 950]
    for pid in pb_targets:
        ok, reason = process_post(PB_BASE, pid, pb_auth, "purebrain.ai")
        results[f"pb_{pid}"] = {"status": "DONE" if ok else "FAILED", "reason": reason}
        time.sleep(1)

    # JDS posts that failed
    jds_targets = [1222, 1216, 1212, 1210, 1207]
    for pid in jds_targets:
        ok, reason = process_post(JDS_BASE, pid, jds_auth, "jareddsanborn.com")
        results[f"jds_{pid}"] = {"status": "DONE" if ok else "FAILED", "reason": reason}
        time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    done = [k for k, v in results.items() if v["status"] == "DONE"]
    failed = [k for k, v in results.items() if v["status"] == "FAILED"]
    print(f"Done: {len(done)}")
    print(f"Failed: {len(failed)}")
    if failed:
        print(f"Still needs manual review: {failed}")

    for k, v in results.items():
        print(f"  {k}: {v}")

    # Save
    out = REPORT_DIR / "2026-03-09--faq-schema-fix-run-results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out}")

    msg = (
        f"[CTO] Task 2 fix-run COMPLETE. "
        f"Done: {len(done)}/{len(results)}. "
    )
    if failed:
        msg += f"Still failing: {failed}"
    else:
        msg += "All posts now have FAQ schema."
    send_telegram(msg)


if __name__ == "__main__":
    main()
