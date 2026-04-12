#!/usr/bin/env python3
"""
Website Analysis Pipeline - Multi-Agent Diagnostic
Aether AI | Client Marketing Department

Usage:
    python3 tools/website_analysis_pipeline.py https://example.com
    python3 tools/website_analysis_pipeline.py https://example.com --output reports/
    python3 tools/website_analysis_pipeline.py https://example.com --html

Outputs a JSON report by default. With --html, also generates an HTML report
using report-template.html populated with real data.
"""

import sys
import json
import re
import time
import argparse
import urllib.parse
from datetime import datetime
from pathlib import Path

try:
    import requests
    from requests.exceptions import RequestException
except ImportError:
    print("ERROR: requests library required. Run: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("WARNING: beautifulsoup4 not installed. Some checks will be limited.", file=sys.stderr)
    print("Install: pip install beautifulsoup4", file=sys.stderr)


# ─────────────────────────────────────────────
# SCORING CONFIG
# ─────────────────────────────────────────────

WEIGHTS = {
    "technical":    0.20,
    "seo":          0.25,
    "ux":           0.20,
    "marketing":    0.20,
    "positioning":  0.15,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    return raw


def score_label(score: int) -> str:
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    if score >= 40: return "Needs Work"
    return "Critical"


def score_color(score: int) -> str:
    if score >= 80: return "#00d68f"
    if score >= 60: return "#2a93c1"
    if score >= 40: return "#f1420b"
    return "#ff2d2d"


def extract_domain(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc or url


def word_count(text: str) -> int:
    return len(re.split(r'\s+', text.strip())) if text.strip() else 0


def flesch_reading_ease(text: str) -> float:
    """Approximate Flesch Reading Ease score."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.split(r'\s+', text.strip())
    words = [w for w in words if w]
    syllable_count = sum(_count_syllables(w) for w in words)

    if not sentences or not words:
        return 0.0

    asl = len(words) / len(sentences)   # avg sentence length
    asw = syllable_count / len(words)   # avg syllables per word
    return max(0, min(100, 206.835 - 1.015 * asl - 84.6 * asw))


def _count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:")
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


# ─────────────────────────────────────────────
# FETCH
# ─────────────────────────────────────────────

def fetch_page(url: str, timeout: int = 30) -> dict:
    """Fetch the page and return raw response data."""
    result = {
        "url": url,
        "success": False,
        "status_code": None,
        "response_time_ms": None,
        "html": "",
        "headers": {},
        "error": None,
        "final_url": url,
    }

    try:
        start = time.time()
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        elapsed_ms = (time.time() - start) * 1000

        result["success"]         = True
        result["status_code"]     = resp.status_code
        result["response_time_ms"] = round(elapsed_ms, 1)
        result["html"]            = resp.text
        result["headers"]         = dict(resp.headers)
        result["final_url"]       = resp.url
        result["encoding"]        = resp.encoding or "utf-8"
        result["content_length"]  = len(resp.content)

    except requests.exceptions.SSLError as e:
        result["error"] = f"SSL error: {str(e)[:120]}"
    except requests.exceptions.ConnectionError as e:
        result["error"] = f"Connection failed: {str(e)[:120]}"
    except requests.exceptions.Timeout:
        result["error"] = "Request timed out after 30s"
    except RequestException as e:
        result["error"] = str(e)[:200]

    return result


# ─────────────────────────────────────────────
# ANALYSIS MODULES
# ─────────────────────────────────────────────

def analyze_technical(fetch_result: dict) -> dict:
    """Technical performance analysis."""
    issues   = []
    wins     = []
    warnings = []
    score    = 100

    url      = fetch_result["url"]
    headers  = fetch_result.get("headers", {})
    html     = fetch_result.get("html", "")
    rt       = fetch_result.get("response_time_ms", 9999)
    size_kb  = fetch_result.get("content_length", 0) / 1024

    # SSL
    has_ssl = url.startswith("https://")
    if has_ssl:
        wins.append("HTTPS enabled — connection is encrypted")
    else:
        issues.append("No HTTPS — site is served over insecure HTTP")
        score -= 20

    # Response time
    if rt and rt < 500:
        wins.append(f"Fast server response: {rt:.0f}ms")
    elif rt and rt < 1500:
        warnings.append(f"Moderate server response time: {rt:.0f}ms (target <500ms)")
        score -= 5
    elif rt:
        issues.append(f"Slow server response: {rt:.0f}ms (target <500ms)")
        score -= 15

    # Page size
    if size_kb < 200:
        wins.append(f"Lean page size: {size_kb:.0f}KB")
    elif size_kb < 600:
        warnings.append(f"Page size {size_kb:.0f}KB — acceptable but optimizable")
        score -= 5
    else:
        issues.append(f"Large page size: {size_kb:.0f}KB — may slow load times")
        score -= 10

    # Security headers
    security_headers = {
        "X-Frame-Options":          "Clickjacking protection",
        "X-Content-Type-Options":   "MIME sniffing protection",
        "Referrer-Policy":          "Referrer information control",
        "Content-Security-Policy":  "XSS/injection protection",
    }
    for h, desc in security_headers.items():
        if h.lower() in {k.lower() for k in headers}:
            wins.append(f"Security header present: {h}")
        else:
            warnings.append(f"Missing security header: {h} ({desc})")
            score -= 3

    # Caching
    cache_control = headers.get("Cache-Control", headers.get("cache-control", ""))
    if cache_control:
        wins.append(f"Cache-Control header set: {cache_control[:60]}")
    else:
        warnings.append("No Cache-Control header — browser caching not configured")
        score -= 5

    # Gzip
    content_enc = headers.get("Content-Encoding", headers.get("content-encoding", ""))
    if "gzip" in content_enc or "br" in content_enc:
        wins.append(f"Compression enabled: {content_enc}")
    else:
        warnings.append("No compression detected (gzip/brotli) — larger transfer size")
        score -= 5

    # Viewport meta tag (mobile)
    if html:
        has_viewport = "viewport" in html.lower() and "width=device-width" in html.lower()
        if has_viewport:
            wins.append("Viewport meta tag present — mobile-ready")
        else:
            issues.append("Missing viewport meta tag — site may not render correctly on mobile")
            score -= 10

    return {
        "score": max(0, min(100, score)),
        "wins": wins,
        "warnings": warnings,
        "issues": issues,
        "raw": {
            "ssl": has_ssl,
            "response_time_ms": rt,
            "page_size_kb": round(size_kb, 1),
            "status_code": fetch_result.get("status_code"),
        }
    }


def analyze_seo(fetch_result: dict, soup=None) -> dict:
    """SEO analysis."""
    issues   = []
    wins     = []
    warnings = []
    score    = 100
    html     = fetch_result.get("html", "")

    if not BS4_AVAILABLE or soup is None:
        # Fallback: regex-based checks
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        desc_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        description = desc_match.group(1).strip() if desc_match else ""
        h1_count = len(re.findall(r'<h1[^>]*>', html, re.IGNORECASE))
        images = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
        images_no_alt = [img for img in images if 'alt=' not in img.lower() or 'alt=""' in img.lower()]
        canonical = bool(re.search(r'<link[^>]+rel=["\']canonical["\']', html, re.IGNORECASE))
        og_title = bool(re.search(r'property=["\']og:title["\']', html, re.IGNORECASE))
        schema = bool(re.search(r'application/ld\+json', html, re.IGNORECASE))
    else:
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ""
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        description = desc_tag.get('content', '').strip() if desc_tag else ""
        h1_count = len(soup.find_all('h1'))
        images = soup.find_all('img')
        images_no_alt = [img for img in images if not img.get('alt') or img.get('alt', '').strip() == '']
        canonical = bool(soup.find('link', attrs={'rel': 'canonical'}))
        og_title = bool(soup.find('meta', attrs={'property': 'og:title'}))
        schema = bool(soup.find('script', attrs={'type': 'application/ld+json'}))

    # Title tag
    if not title:
        issues.append("Missing <title> tag — critical for search rankings")
        score -= 20
    elif len(title) < 30:
        warnings.append(f"Title tag too short: '{title}' ({len(title)} chars). Aim for 50-60.")
        score -= 8
    elif len(title) > 70:
        warnings.append(f"Title tag too long ({len(title)} chars) — may truncate in search results")
        score -= 5
    else:
        wins.append(f"Good title tag: '{title[:55]}{'...' if len(title)>55 else ''}'")

    # Meta description
    if not description:
        issues.append("Missing meta description — search engines show generic snippet instead")
        score -= 15
    elif len(description) < 80:
        warnings.append(f"Meta description too short ({len(description)} chars). Aim for 120-160.")
        score -= 5
    elif len(description) > 165:
        warnings.append(f"Meta description too long ({len(description)} chars) — will truncate")
        score -= 3
    else:
        wins.append(f"Good meta description ({len(description)} chars)")

    # H1
    if h1_count == 0:
        issues.append("No H1 heading found — primary keyword signal missing for search engines")
        score -= 15
    elif h1_count > 1:
        warnings.append(f"Multiple H1 tags ({h1_count}) — use only one H1 per page")
        score -= 8
    else:
        wins.append("Single H1 heading — correct structure")

    # Images without alt
    total_images = len(images_no_alt) + (len(images) - len(images_no_alt)) if BS4_AVAILABLE and soup else 0
    if images_no_alt:
        n = len(images_no_alt)
        issues.append(f"{n} image(s) missing alt text — hurts SEO and accessibility")
        score -= min(15, n * 3)
    elif total_images > 0:
        wins.append("All images have alt text")

    # Canonical URL
    if canonical:
        wins.append("Canonical URL tag present — prevents duplicate content penalties")
    else:
        warnings.append("No canonical tag — consider adding to prevent duplicate content issues")
        score -= 5

    # Open Graph
    if og_title:
        wins.append("Open Graph tags present — social sharing will display correctly")
    else:
        warnings.append("No Open Graph tags — social media shares may look incomplete")
        score -= 5

    # Schema markup
    if schema:
        wins.append("Structured data (schema.org) found — helps rich snippet eligibility")
    else:
        warnings.append("No structured data (JSON-LD) — missed rich snippet opportunity")
        score -= 5

    return {
        "score": max(0, min(100, score)),
        "wins": wins,
        "warnings": warnings,
        "issues": issues,
        "raw": {
            "title": title,
            "description": description,
            "h1_count": h1_count,
            "images_missing_alt": len(images_no_alt),
            "has_canonical": canonical,
            "has_og": og_title,
            "has_schema": schema,
        }
    }


def analyze_ux(fetch_result: dict, soup=None) -> dict:
    """UX / UI analysis."""
    issues   = []
    wins     = []
    warnings = []
    score    = 100
    html     = fetch_result.get("html", "")

    # Navigation
    has_nav = bool(re.search(r'<nav[\s>]', html, re.IGNORECASE)) or bool(re.search(r'role=["\']navigation["\']', html, re.IGNORECASE))
    if has_nav:
        wins.append("Navigation element present (<nav> or role='navigation')")
    else:
        warnings.append("No semantic <nav> element detected — navigation structure may be unclear")
        score -= 8

    # Viewport (mobile readiness)
    has_viewport = "viewport" in html.lower() and "width=device-width" in html.lower()
    if has_viewport:
        wins.append("Viewport configured for mobile devices")
    else:
        issues.append("No viewport meta tag — site likely broken on mobile")
        score -= 20

    # Forms
    form_count = len(re.findall(r'<form[\s>]', html, re.IGNORECASE))
    if form_count > 0:
        # Check for labels
        label_count = len(re.findall(r'<label[\s>]', html, re.IGNORECASE))
        input_count = len(re.findall(r'<input[\s>]', html, re.IGNORECASE))
        if label_count >= input_count // 2:
            wins.append(f"Forms have labels ({form_count} form(s), {label_count} label(s))")
        else:
            warnings.append("Form inputs may lack associated labels — hurts accessibility")
            score -= 8

    # CTA buttons
    cta_patterns = [
        r'<button[^>]*>.*?(get started|buy|order|sign up|subscribe|contact|learn more|try|book|schedule|start)[^<]*</button>',
        r'<a[^>]*(class|id)[^>]*>[^<]*(get started|buy|order|sign up|subscribe|contact|learn more|start)[^<]*</a>',
    ]
    has_cta = any(re.search(p, html, re.IGNORECASE | re.DOTALL) for p in cta_patterns)
    if has_cta:
        wins.append("Call-to-action button(s) detected")
    else:
        warnings.append("No obvious call-to-action buttons detected — visitors may not know what to do next")
        score -= 12

    # Contact information
    has_contact = (
        re.search(r'(?:mailto:|tel:|phone|contact|email)[^\s<]{3,50}', html, re.IGNORECASE) is not None
    )
    if has_contact:
        wins.append("Contact information or contact link found")
    else:
        warnings.append("No visible contact information — reduces trust")
        score -= 8

    # Footer presence
    has_footer = bool(re.search(r'<footer[\s>]', html, re.IGNORECASE))
    if has_footer:
        wins.append("Footer element present — good navigation and trust structure")
    else:
        warnings.append("No <footer> element — footer content may not be semantically structured")
        score -= 5

    # ARIA landmarks
    has_main = bool(re.search(r'<main[\s>]|role=["\']main["\']', html, re.IGNORECASE))
    if has_main:
        wins.append("Main landmark (<main>) present — good accessibility structure")
    else:
        warnings.append("No <main> landmark — accessibility and screen reader navigation impacted")
        score -= 5

    # Skip link (accessibility)
    has_skip = bool(re.search(r'skip[- ]?(to|navigation|content|main)', html, re.IGNORECASE))
    if has_skip:
        wins.append("Skip navigation link found — good keyboard accessibility")
    else:
        warnings.append("No skip navigation link — keyboard users must tab through entire nav on every page")
        score -= 3

    return {
        "score": max(0, min(100, score)),
        "wins": wins,
        "warnings": warnings,
        "issues": issues,
        "raw": {
            "has_nav": has_nav,
            "has_viewport": has_viewport,
            "form_count": form_count,
            "has_cta": has_cta,
            "has_contact": has_contact,
        }
    }


def analyze_marketing(fetch_result: dict, soup=None) -> dict:
    """Marketing and messaging analysis."""
    issues   = []
    wins     = []
    warnings = []
    score    = 100
    html     = fetch_result.get("html", "")

    # Extract readable text
    if BS4_AVAILABLE and soup:
        for tag in soup(["script", "style", "noscript", "nav", "footer"]):
            tag.decompose()
        visible_text = soup.get_text(separator=" ", strip=True)
    else:
        visible_text = re.sub(r'<[^>]+>', ' ', html)
        visible_text = re.sub(r'\s+', ' ', visible_text).strip()

    wc = word_count(visible_text)
    fre = flesch_reading_ease(visible_text[:3000]) if visible_text else 0

    # Content length
    if wc < 150:
        issues.append(f"Very thin content: only ~{wc} words — not enough to persuade or rank")
        score -= 20
    elif wc < 400:
        warnings.append(f"Content may be too thin: ~{wc} words — consider expanding key sections")
        score -= 10
    elif wc > 3000:
        warnings.append(f"Long page (~{wc} words) — ensure key messages appear above the fold")
        score -= 3
    else:
        wins.append(f"Good content volume: ~{wc} words")

    # Readability
    if fre >= 60:
        wins.append(f"Readable copy — Flesch score {fre:.0f}/100 (easy to understand)")
    elif fre >= 40:
        warnings.append(f"Moderately complex copy — Flesch score {fre:.0f}/100. Consider simplifying.")
        score -= 8
    elif fre > 0:
        issues.append(f"Copy may be too complex — Flesch score {fre:.0f}/100. Aim for 60+.")
        score -= 15

    # Trust signals
    trust_patterns = [
        (r'testimonial|review|client|customer says|said about', "Testimonials/reviews detected"),
        (r'years? (of )?experience|since \d{4}', "Years of experience mentioned"),
        (r'\bguarantee\b|\bmoney.back\b', "Guarantee language present"),
        (r'\bcertif(ied|ication)\b|\baward\b|\bfeatured in\b', "Credentials/awards mentioned"),
        (r'\bssl\b|\bsecure\b|\bprivacy\b', "Security/privacy language present"),
    ]
    for pattern, label in trust_patterns:
        if re.search(pattern, visible_text, re.IGNORECASE):
            wins.append(label)
        else:
            warnings.append(f"No {label.lower()} found — consider adding trust signals")
            score -= 4

    # Value proposition check
    vp_words = ["we help", "we make", "we provide", "we offer", "you'll get", "you can", "our solution", "our service"]
    has_vp = any(w in visible_text.lower() for w in vp_words)
    if has_vp:
        wins.append("Value proposition language detected")
    else:
        issues.append("No clear value proposition language — visitors may not understand what you do")
        score -= 12

    # Social proof numbers
    has_numbers = bool(re.search(r'\b\d+[\+,]?\s*(clients|customers|users|companies|businesses|reviews|projects)', visible_text, re.IGNORECASE))
    if has_numbers:
        wins.append("Quantified social proof (numbers of clients/customers) found")
    else:
        warnings.append("No quantified social proof — specific numbers build more trust than vague claims")
        score -= 5

    return {
        "score": max(0, min(100, score)),
        "wins": wins,
        "warnings": warnings,
        "issues": issues,
        "raw": {
            "word_count": wc,
            "flesch_score": round(fre, 1),
        }
    }


def analyze_positioning(fetch_result: dict, soup=None) -> dict:
    """Business positioning analysis."""
    issues   = []
    wins     = []
    warnings = []
    score    = 100
    html     = fetch_result.get("html", "")

    if BS4_AVAILABLE and soup:
        visible_text = soup.get_text(separator=" ", strip=True)
    else:
        visible_text = re.sub(r'<[^>]+>', ' ', html)
        visible_text = re.sub(r'\s+', ' ', visible_text).strip()

    # About / who you are
    has_about = bool(re.search(r'\babout\b|\bwho we are\b|\bour story\b|\bour team\b|\bfounded\b', visible_text, re.IGNORECASE))
    if has_about:
        wins.append("Company story / About content present — humanizes the brand")
    else:
        warnings.append("No 'About' or 'Who we are' content visible — adds trust when present")
        score -= 8

    # Differentiation language
    diff_patterns = [
        r'\bunique\b|\bonly\b|\bbest\b|\bleading\b|\bfirst\b|\boriginal\b|\bdifference\b|\badvantage\b',
        r'\bwhy us\b|\bwhy choose\b|\bwhat sets us apart\b'
    ]
    has_diff = any(re.search(p, visible_text, re.IGNORECASE) for p in diff_patterns)
    if has_diff:
        wins.append("Differentiation language present — explains why you vs competitors")
    else:
        warnings.append("No differentiation messaging found — visitors may not understand what makes you different")
        score -= 12

    # Pricing visibility
    has_pricing = bool(re.search(r'\$\s*\d+|\bpricing\b|\bplans?\b|\bpackages?\b|\brates?\b|\bfee[s]?\b', visible_text, re.IGNORECASE))
    if has_pricing:
        wins.append("Pricing information visible — reduces friction in decision-making")
    else:
        warnings.append("No visible pricing — many buyers want to self-qualify before contacting you")
        score -= 10

    # Target audience
    has_audience = bool(re.search(r'\bfor\s+(small|medium|large|enterprise|startup|b2b|b2c|ecommerce|local|growing|scaling)\b', visible_text, re.IGNORECASE))
    if has_audience:
        wins.append("Target audience language present — visitors can self-identify as the right fit")
    else:
        warnings.append("Target audience not clearly stated — 'who is this for?' question left unanswered")
        score -= 8

    # FAQ or objection handling
    has_faq = bool(re.search(r'\bfaq\b|\bfrequently asked\b|\bcommon questions?\b|\bwondering\b|\bworried\b', visible_text, re.IGNORECASE))
    if has_faq:
        wins.append("FAQ or objection-handling content present")
    else:
        warnings.append("No FAQ section — consider addressing common objections proactively")
        score -= 5

    # Process / how it works
    has_process = bool(re.search(r'\bhow it works\b|\bour process\b|\bsteps?\b|\bwhat to expect\b', visible_text, re.IGNORECASE))
    if has_process:
        wins.append("Process / 'How it works' content present — reduces buyer uncertainty")
    else:
        warnings.append("No 'How it works' section — buyers often want to know the process before committing")
        score -= 7

    return {
        "score": max(0, min(100, score)),
        "wins": wins,
        "warnings": warnings,
        "issues": issues,
        "raw": {
            "has_about": has_about,
            "has_pricing": has_pricing,
            "has_faq": has_faq,
            "has_process": has_process,
        }
    }


# ─────────────────────────────────────────────
# LINK CHECKER (QUICK)
# ─────────────────────────────────────────────

def quick_link_check(url: str, soup=None, html: str = "") -> dict:
    """Sample a few links to check for obvious broken ones."""
    broken = []
    checked = 0

    if not BS4_AVAILABLE or soup is None:
        return {"checked": 0, "broken": [], "note": "bs4 required for link checking"}

    parsed_base = urllib.parse.urlparse(url)
    base = f"{parsed_base.scheme}://{parsed_base.netloc}"

    links = [a.get('href', '') for a in soup.find_all('a', href=True)]
    # Filter: only same-domain, no anchors, no javascript
    internal = []
    for link in links:
        if not link or link.startswith('#') or link.startswith('javascript') or link.startswith('mailto') or link.startswith('tel'):
            continue
        if link.startswith('/'):
            internal.append(base + link)
        elif link.startswith(base):
            internal.append(link)

    # Sample max 5 internal links
    sample = list(dict.fromkeys(internal))[:5]
    for lnk in sample:
        try:
            r = requests.head(lnk, headers=HEADERS, timeout=8, allow_redirects=True)
            checked += 1
            if r.status_code >= 400:
                broken.append({"url": lnk, "status": r.status_code})
        except Exception:
            checked += 1
            broken.append({"url": lnk, "status": "timeout/error"})

    return {"checked": checked, "broken": broken, "total_links_found": len(links)}


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────

def analyze_website(url: str, check_links: bool = True) -> dict:
    """Run the full multi-module analysis. Returns complete report dict."""
    url = normalize_url(url)
    domain = extract_domain(url)

    print(f"[Aether AI] Analyzing: {url}", file=sys.stderr)

    report = {
        "meta": {
            "url": url,
            "domain": domain,
            "generated": datetime.now().isoformat(),
            "generated_readable": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "analyzer_version": "1.0.0",
            "powered_by": "Aether AI",
        },
        "sections": {}
    }

    # ── FETCH ──
    print("[Aether AI] Fetching page...", file=sys.stderr)
    fetch_result = fetch_page(url)

    if not fetch_result["success"]:
        report["meta"]["fetch_error"] = fetch_result["error"]
        report["meta"]["overall_score"] = 0
        report["meta"]["overall_label"] = "Could Not Fetch"
        report["error"] = fetch_result["error"]
        return report

    report["meta"]["final_url"] = fetch_result["final_url"]
    report["meta"]["status_code"] = fetch_result["status_code"]
    report["meta"]["response_time_ms"] = fetch_result["response_time_ms"]
    report["meta"]["page_size_kb"] = round(fetch_result.get("content_length", 0) / 1024, 1)

    # ── PARSE ──
    soup = None
    if BS4_AVAILABLE:
        soup = BeautifulSoup(fetch_result["html"], "html.parser")

    # ── MODULES ──
    print("[Aether AI] Running technical analysis...", file=sys.stderr)
    report["sections"]["technical"] = analyze_technical(fetch_result)

    print("[Aether AI] Running SEO analysis...", file=sys.stderr)
    report["sections"]["seo"] = analyze_seo(fetch_result, soup)

    print("[Aether AI] Running UX analysis...", file=sys.stderr)
    report["sections"]["ux"] = analyze_ux(fetch_result, soup)

    print("[Aether AI] Running marketing analysis...", file=sys.stderr)
    report["sections"]["marketing"] = analyze_marketing(fetch_result, soup)

    print("[Aether AI] Running positioning analysis...", file=sys.stderr)
    report["sections"]["positioning"] = analyze_positioning(fetch_result, soup)

    # ── LINK CHECK ──
    if check_links:
        print("[Aether AI] Checking sample links...", file=sys.stderr)
        report["sections"]["links"] = quick_link_check(url, soup, fetch_result["html"])

    # ── OVERALL SCORE ──
    section_scores = {k: v["score"] for k, v in report["sections"].items() if "score" in v}
    total_weight = 0
    weighted_sum = 0
    for section, weight in WEIGHTS.items():
        if section in section_scores:
            weighted_sum += section_scores[section] * weight
            total_weight += weight

    overall = int(weighted_sum / total_weight) if total_weight > 0 else 0

    report["meta"]["overall_score"] = overall
    report["meta"]["overall_label"] = score_label(overall)
    report["meta"]["section_scores"] = {
        k: {"score": v["score"], "label": score_label(v["score"])}
        for k, v in report["sections"].items()
        if "score" in v
    }

    # ── PRIORITY RECOMMENDATIONS ──
    all_issues = []
    all_warnings = []
    for section_name, section_data in report["sections"].items():
        if isinstance(section_data, dict):
            for issue in section_data.get("issues", []):
                all_issues.append({"section": section_name, "text": issue, "priority": "critical"})
            for warn in section_data.get("warnings", []):
                all_warnings.append({"section": section_name, "text": warn, "priority": "moderate"})

    report["recommendations"] = {
        "critical": all_issues[:5],
        "moderate": all_warnings[:8],
        "total_issues": len(all_issues),
        "total_warnings": len(all_warnings),
    }

    print(f"[Aether AI] Analysis complete. Overall score: {overall}/100 ({score_label(overall)})", file=sys.stderr)
    return report


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Aether AI Website Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/website_analysis_pipeline.py https://example.com
  python3 tools/website_analysis_pipeline.py example.com --html --output reports/
        """
    )
    parser.add_argument("url", help="Website URL to analyze")
    parser.add_argument("--html", action="store_true", help="Also generate HTML report")
    parser.add_argument("--output", default=None, help="Output directory for reports")
    parser.add_argument("--no-links", action="store_true", help="Skip link checking (faster)")
    args = parser.parse_args()

    report = analyze_website(args.url, check_links=not args.no_links)

    # ── JSON OUTPUT ──
    json_output = json.dumps(report, indent=2, default=str)
    print(json_output)

    # ── SAVE TO DIRECTORY ──
    if args.output:
        out_dir = Path(args.output)
        out_dir.mkdir(parents=True, exist_ok=True)
        domain_slug = re.sub(r'[^\w\-]', '-', extract_domain(args.url))
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        json_path = out_dir / f"{domain_slug}-{ts}.json"
        json_path.write_text(json_output, encoding="utf-8")
        print(f"\n[Aether AI] JSON report saved: {json_path}", file=sys.stderr)

        if args.html:
            from generate_html_report import generate_html_report
            html_path = out_dir / f"{domain_slug}-{ts}.html"
            html_path.write_text(generate_html_report(report), encoding="utf-8")
            print(f"[Aether AI] HTML report saved: {html_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
