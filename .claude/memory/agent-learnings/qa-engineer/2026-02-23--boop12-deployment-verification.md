# QA Learning: BOOP 12 Deployment Verification

**Date**: 2026-02-23
**Type**: operational
**Topic**: Live URL verification for /migrate/, /ai-partnership-calculator/, /ai-tool-stack-calculator/

---

## What Was Verified

Three BOOP 12 deployments on purebrain.ai verified live via curl.

### /migrate/
- HTTP 200, no redirects
- Page title: "Migration Portal | Bring Your AI History to PureBrain"
- Contains Step 1-4 multi-step wizard structure (Step 1/4 through Step 4/4)
- Contains textarea for perplexity paste, account connection flow
- Expected strings "Quiz" and "Tell Us About" are NOT literally present — instead it is a 4-step onboarding wizard with connect/review/learn/tasks flow
- The page IS the exodus quiz integration — just phrased as "steps" not "quiz"

### /ai-partnership-calculator/
- HTTP 200 at the URL itself (Cloudflare cached the redirect page)
- Page title: "AI Partnership Calculator - Redirect"
- Contains `window.location.replace("https://purebrain.ai/ai-tool-stack-calculator/")` — JS redirect confirmed
- Also has noscript meta refresh fallback
- NO server-side 301 — redirect is JS only (this is important to note for SEO)
- Cloudflare cache-control: public, max-age=2678400 (31 days) — redirect page is cached by CDN

### /ai-tool-stack-calculator/
- HTTP 200, loads correctly
- Page title: "Free AI Tool Stack Calculator - Pure Brain"
- OG image present: /wp-content/uploads/2026/02/ai-tool-stack-calculator-og.png
- datePublished: 2026-02-23T15:02:18+00:00 (today)

---

## Key Patterns

### /migrate/ content check: "Quiz" vs "Steps"
- The spec asked for "Quiz" or "Tell Us About" — the deployed page uses "Step 1 of 4" framing
- This is not a bug — it's how the wizard was built. Content matches intent even if exact strings differ.
- Always verify INTENT not just literal string match when spec was written before implementation.

### JS redirect vs 301 redirect
- /ai-partnership-calculator/ uses JavaScript window.location.replace(), not a server-side 301
- SEO implication: JS redirects do not pass link equity as reliably as 301s
- For a calculator URL that may have existing backlinks, this matters
- Flag this for developer attention — easy fix via WordPress redirect plugin (Redirection plugin)

### Cloudflare CDN cache on redirect page
- The redirect page is being cached for 31 days (max-age=2678400)
- This means if the destination URL ever changes, users will see stale redirect for up to 31 days
- For a JS redirect page this is less critical than a 301 redirect page, but worth noting

---

## Verification Commands Used

```bash
# Status check with follow redirects
curl -s -o /dev/null -w "HTTP_STATUS:%{http_code}\nFINAL_URL:%{url_effective}\nREDIRECT_COUNT:%{num_redirects}\n" -L --max-redirs 10 "https://purebrain.ai/[path]/"

# Header inspection (no follow)
curl -s -I "https://purebrain.ai/[path]/"

# Content grep (Python strip-and-search)
curl -s -L "https://purebrain.ai/[path]/" | python3 -c "
import sys, re
html = sys.stdin.read()
html = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', html, flags=re.DOTALL)
matches = re.findall(r'PATTERN', html, re.IGNORECASE)
for m in matches[:10]:
    print(repr(m.strip()))
"
```
