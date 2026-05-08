#!/usr/bin/env python3
"""
Blog SEO Gap Fixes (GAPs A, B, D, E)
=====================================
Idempotent fixes for all blog posts in exports/cf-pages-deploy/blog/:

  GAP-A: Add <h1> with post title at top of article body (if missing)
  GAP-B: Inject inline subscribe form + CTA block before </article> close
  GAP-D: Inject "Related Posts" section (3 most recent others) before CTA
  GAP-E: Fix JSON-LD schema author → Organization "Pure Technology"

Each mutation is wrapped in HTML comment markers so re-runs are safe.

Usage:
    python3 tools/blog_seo_h1_schema_fix.py [--dry-run]
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path("/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog")
MANIFEST_PATH = Path("/home/jared/projects/AI-CIV/aether/tools/blog_posts_manifest.json")

# Idempotency markers
H1_MARK = "<!-- aether-seo-h1-v1 -->"
CTA_MARK_START = "<!-- aether-seo-cta-v1-start -->"
CTA_MARK_END = "<!-- aether-seo-cta-v1-end -->"
RELATED_MARK_START = "<!-- aether-related-posts-v1-start -->"
RELATED_MARK_END = "<!-- aether-related-posts-v1-end -->"
SCHEMA_MARK = "aether-seo-schema-v1"  # placed as JSON comment-ish via extra key


def is_redirect_stub(html: str) -> bool:
    return 'http-equiv="refresh"' in html and "<title>Redirecting" in html


def extract_title(html: str) -> str:
    m = re.search(r"<title>([^<]+)</title>", html)
    if not m:
        return ""
    t = m.group(1).strip()
    # Strip common " – PureBrain" suffix for H1
    t = re.sub(r"\s*[\u2013\u2014\-|]\s*PureBrain\s*$", "", t)
    return t


def extract_date(html: str) -> str:
    """Return ISO date YYYY-MM-DD."""
    m = re.search(r'article:published_time"\s*content="([^"]+)"', html)
    if m:
        return m.group(1)[:10]
    # Schema fallback
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)
    if m:
        return m.group(1)[:10]
    return "2026-01-01"


def extract_excerpt(html: str) -> str:
    m = re.search(r'<meta name="description" content="([^"]*)"', html)
    if m:
        return m.group(1)[:200]
    return ""


# ---------------------------------------------------------------------------
# GAP-A: H1 insertion
# ---------------------------------------------------------------------------
def inject_h1(html: str, title: str) -> tuple[str, bool]:
    if H1_MARK in html:
        return html, False
    # Skip if any real <h1> already in article
    article_match = re.search(r'(<article[^>]*class="pb-blog-post"[^>]*>)', html)
    if not article_match:
        return html, False
    # Check if h1 already anywhere in body
    if re.search(r"<h1[\s>]", html):
        # mark as seen but don't add
        html = html.replace(article_match.group(1), article_match.group(1) + "\n" + H1_MARK, 1)
        return html, True
    # Decode HTML entities lightly for H1 visible text
    visible = title.replace("&#8217;", "\u2019").replace("&#8211;", "\u2013").replace("&#8220;", "\u201c").replace("&#8221;", "\u201d").replace("&#038;", "&").replace("&amp;", "&")
    h1_block = (
        f'\n{H1_MARK}\n'
        f'<h1 class="pb-post-h1" style="font-family:\'Oswald\',sans-serif;'
        f'font-size:2.4rem;font-weight:700;color:#ffffff;line-height:1.15;'
        f'margin:24px 0 12px 0;letter-spacing:0.3px;">{visible}</h1>\n'
    )
    html = html.replace(article_match.group(1), article_match.group(1) + h1_block, 1)
    return html, True


# ---------------------------------------------------------------------------
# GAP-B: CTA + inline subscribe form
# ---------------------------------------------------------------------------
CTA_HTML = (CTA_MARK_START + """
<section class="aether-post-cta" style="margin:48px 0 32px;padding:36px 28px;background:linear-gradient(135deg,#080a12 0%,#0f1a2e 100%);border-radius:16px;border:1px solid rgba(42,147,193,0.3);box-shadow:0 18px 50px rgba(0,0,0,0.45);font-family:'Plus Jakarta Sans',sans-serif;color:#e8eef7;position:relative;overflow:hidden;">
  <div style="position:absolute;top:-60px;right:-60px;width:200px;height:200px;background:radial-gradient(circle,rgba(241,66,11,0.12) 0%,transparent 70%);pointer-events:none;"></div>
  <h2 style="font-family:'Oswald',sans-serif;font-size:1.8rem;font-weight:700;color:#ffffff;margin:0 0 10px;line-height:1.2;">Ready to build with <span style="color:#2a93c1;">AI</span>?</h2>
  <p style="margin:0 0 20px;color:#b9c5d6;font-size:1.02rem;line-height:1.55;">Stop renting tools. Start your AI partnership — a system that remembers, learns, and works beside you.</p>
  <div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:24px;">
    <a href="https://purebrain.ai/#awakening" style="display:inline-block;background:linear-gradient(135deg,#f1420b 0%,#ff6b3d 100%);color:#fff;padding:14px 26px;border-radius:10px;text-decoration:none;font-weight:700;font-size:0.98rem;letter-spacing:0.3px;box-shadow:0 8px 22px rgba(241,66,11,0.35);">Start Your AI Partnership &rarr;</a>
    <a href="https://purebrain.ai/brainiac-mastermind-training/?bypass=portal" style="display:inline-block;background:transparent;color:#2a93c1;padding:14px 26px;border-radius:10px;text-decoration:none;font-weight:700;font-size:0.98rem;letter-spacing:0.3px;border:1px solid rgba(42,147,193,0.5);">Get Free Brainiac Training</a>
  </div>
  <div style="border-top:1px solid rgba(42,147,193,0.18);padding-top:22px;">
    <div style="font-size:0.78rem;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;color:#2a93c1;margin-bottom:8px;">The Neural Feed</div>
    <p style="margin:0 0 14px;color:#b9c5d6;font-size:0.95rem;">One email. Once a week. No fluff.</p>
    <form class="aether-inline-subscribe" novalidate style="display:flex;flex-wrap:wrap;gap:8px;max-width:520px;">
      <input type="email" required placeholder="your@email.com" aria-label="Email address" style="flex:1 1 220px;min-width:0;padding:13px 16px;border-radius:10px;border:1px solid rgba(42,147,193,0.35);background:rgba(10,12,22,0.9);color:#fff;font-size:1rem;font-family:inherit;outline:none;" />
      <button type="submit" style="padding:13px 24px;border-radius:10px;border:none;background:linear-gradient(135deg,#2a93c1 0%,#4ab3e1 100%);color:#fff;font-weight:700;font-size:0.98rem;font-family:inherit;cursor:pointer;box-shadow:0 8px 22px rgba(42,147,193,0.35);">Subscribe Free</button>
      <div class="aether-inline-msg" role="alert" aria-live="polite" style="flex:1 1 100%;font-size:0.92rem;margin-top:6px;min-height:1em;"></div>
    </form>
    <p style="margin:12px 0 0;font-size:0.82rem;color:#7a8598;">No spam. Unsubscribe anytime. <a href="https://purebrain.ai/privacy-policy/" style="color:#2a93c1;text-decoration:none;">Privacy</a>.</p>
  </div>
</section>
<script>
(function(){
  var forms = document.querySelectorAll('form.aether-inline-subscribe');
  if(!forms.length) return;
  forms.forEach(function(form){
    if(form.dataset.bound) return; form.dataset.bound='1';
    var msg = form.querySelector('.aether-inline-msg');
    var input = form.querySelector('input[type=email]');
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var email = (input.value||'').trim();
      if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)){
        msg.style.color = '#f1420b'; msg.textContent = 'Please enter a valid email.';
        return;
      }
      msg.style.color = '#2a93c1'; msg.textContent = 'Subscribing...';
      fetch('/api/subscribe', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email:email})})
      .then(function(r){return r.json();})
      .then(function(d){
        if(d.ok){ form.style.display='none'; msg.style.color='#2a93c1'; msg.textContent = d.message==='already_subscribed' ? "You're already subscribed!" : "You're in! Look for your first issue this Friday."; }
        else { msg.style.color='#f1420b'; msg.textContent = d.message || 'Something went wrong. Please try again.'; }
      })
      .catch(function(){ msg.style.color='#f1420b'; msg.textContent = 'Connection error. Please try again.'; });
    });
  });
})();
</script>
""" + CTA_MARK_END)


def inject_cta(html: str) -> tuple[str, bool]:
    if CTA_MARK_START in html:
        return html, False
    # Inject before </article>
    if "</article>" not in html:
        return html, False
    html = html.replace("</article>", CTA_HTML + "\n</article>", 1)
    return html, True


# ---------------------------------------------------------------------------
# GAP-D: Related posts
# ---------------------------------------------------------------------------
def build_related_html(related: list) -> str:
    items = []
    for r in related:
        items.append(
            f'<a href="/blog/{r["slug"]}/" style="display:block;background:rgba(15,23,42,0.7);border:1px solid rgba(42,147,193,0.22);border-radius:12px;padding:18px;text-decoration:none;color:#e8eef7;transition:transform .15s,border-color .15s;">'
            f'<div style="font-family:\'Oswald\',sans-serif;font-size:1.02rem;font-weight:600;color:#ffffff;line-height:1.3;margin-bottom:8px;">{r["title"]}</div>'
            f'<div style="font-size:0.82rem;color:#7a8598;">{r["date"]} &middot; Read &rarr;</div>'
            f'</a>'
        )
    grid = "".join(items)
    return (
        f"\n{RELATED_MARK_START}\n"
        f'<section class="aether-related-posts" aria-label="Related posts" '
        f'style="margin:40px 0 0;padding:32px 24px;background:rgba(10,12,22,0.55);'
        f'border-radius:14px;border:1px solid rgba(42,147,193,0.18);'
        f'font-family:\'Plus Jakarta Sans\',sans-serif;">'
        f'<h2 style="font-family:\'Oswald\',sans-serif;font-size:1.5rem;font-weight:700;color:#ffffff;margin:0 0 20px;letter-spacing:0.3px;">More From The Neural Feed</h2>'
        f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;">{grid}</div>'
        f'</section>\n{RELATED_MARK_END}\n'
    )


def inject_related(html: str, current_slug: str, manifest: list) -> tuple[str, bool]:
    if RELATED_MARK_START in html:
        return html, False
    # Pick 3 most recent others
    others = [m for m in manifest if m["slug"] != current_slug]
    others.sort(key=lambda x: x["date"], reverse=True)
    picks = others[:3]
    if not picks:
        return html, False
    block = build_related_html(picks)
    # Inject before CTA if present, else before </article>
    if CTA_MARK_START in html:
        html = html.replace(CTA_MARK_START, block + CTA_MARK_START, 1)
    elif "</article>" in html:
        html = html.replace("</article>", block + "\n</article>", 1)
    else:
        return html, False
    return html, True


# ---------------------------------------------------------------------------
# GAP-E: Schema author fix
# ---------------------------------------------------------------------------
def fix_schema_author(html: str) -> tuple[str, bool]:
    """Replace author Person→Organization in all JSON-LD BlogPosting blocks."""
    changed = False

    def repl(match):
        nonlocal changed
        block = match.group(0)
        try:
            # extract inside of <script>...</script>
            inner = re.search(r'>\s*(\{.*?\})\s*<', block, re.DOTALL)
            if not inner:
                return block
            data = json.loads(inner.group(1))
        except Exception:
            return block

        def fix_node(node):
            nonlocal changed
            if isinstance(node, dict):
                if node.get("@type") in ("BlogPosting", "Article", "NewsArticle"):
                    if "author" in node:
                        current = node["author"]
                        target = {
                            "@type": "Organization",
                            "name": "Pure Technology",
                            "url": "https://purebrain.ai",
                        }
                        if current != target:
                            node["author"] = target
                            changed = True
                for v in node.values():
                    fix_node(v)
            elif isinstance(node, list):
                for v in node:
                    fix_node(v)

        fix_node(data)
        if not changed:
            return block
        new_json = json.dumps(data, indent=2)
        return re.sub(r'>\s*\{.*?\}\s*<', lambda m: ">\n" + new_json + "\n<", block, count=1, flags=re.DOTALL)

    new_html = re.sub(
        r'<script[^>]*type="application/ld\+json"[^>]*>.*?</script>',
        repl,
        html,
        flags=re.DOTALL,
    )
    return new_html, changed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    dry = "--dry-run" in sys.argv

    post_dirs = sorted([p for p in ROOT.iterdir() if p.is_dir()])
    manifest = []
    redirects_skipped = []

    # Pass 1: build manifest
    for d in post_dirs:
        idx = d / "index.html"
        if not idx.exists():
            continue
        html = idx.read_text(encoding="utf-8", errors="replace")
        if is_redirect_stub(html):
            redirects_skipped.append(d.name)
            continue
        title = extract_title(html)
        date = extract_date(html)
        excerpt = extract_excerpt(html)
        manifest.append({
            "slug": d.name,
            "title": title,
            "date": date,
            "excerpt": excerpt,
        })

    # Write manifest
    if not dry:
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest: {len(manifest)} posts ({len(redirects_skipped)} redirect stubs skipped)")

    # Pass 2: mutate each post
    stats = {"h1": 0, "cta": 0, "related": 0, "schema": 0, "skipped_redirect": len(redirects_skipped), "files_changed": 0}
    for entry in manifest:
        idx = ROOT / entry["slug"] / "index.html"
        html = idx.read_text(encoding="utf-8", errors="replace")
        original = html

        html, did_h1 = inject_h1(html, entry["title"])
        if did_h1: stats["h1"] += 1

        html, did_cta = inject_cta(html)
        if did_cta: stats["cta"] += 1

        html, did_rel = inject_related(html, entry["slug"], manifest)
        if did_rel: stats["related"] += 1

        html, did_schema = fix_schema_author(html)
        if did_schema: stats["schema"] += 1

        if html != original:
            stats["files_changed"] += 1
            if not dry:
                idx.write_text(html, encoding="utf-8")

    print(f"Results: {json.dumps(stats, indent=2)}")
    return stats


if __name__ == "__main__":
    main()
