# Memory: Pay-Test Page Testing Patterns
**Date**: 2026-02-20
**Type**: operational + teaching
**Topic**: Testing WP password-protected heavy Elementor pages with Playwright

---

## Key Learnings

### 1. GoDaddy WAF Rate Limiting
**Problem**: Running multiple Playwright browsers in quick succession (3+ in <5 minutes) triggers GoDaddy WAF:
- Shows "Please verify you are human" CAPTCHA page
- Returns 429 on all subsequent requests including WP login
- Rate limit clears in ~3-4 minutes

**Solution**: Single browser instance. Reuse contexts. Add 15s delays between page tests. Use single context with page navigation rather than spawning new browsers.

**Pattern**:
```python
# WRONG: Multiple browsers
browser1 = pw.chromium.launch()  # test page A
browser2 = pw.chromium.launch()  # test page B - TRIGGERS WAF

# RIGHT: One browser, navigate pages
browser = pw.chromium.launch()
ctx = browser.new_context()
page = ctx.new_page()
page.goto(url_a)  # test A
time.sleep(15)  # wait
page.goto(url_b)  # test B - safe
```

### 2. WordPress Password-Protected Pages
- WP page protection uses: `input[id^="pwbox-"]` + `input[type="submit"]`
- Password is stored in WP post: `GET /wp-json/wp/v2/pages/{id}?context=edit`
- WP returns `display:none` Elementor content until password entered
- After submitting password, WP sets cookie `wp-postpass_[hash]` - reusable across pages in same session

### 3. Pay-Test Page Structure
- URL: `https://purebrain.ai/pay-test/#awakening`
- Page password: `PureBrain.ai253443$$$` (both pay-test and pay-test-sandbox)
- After unlock: scroll to 20% of page height to find "Begin Awakening" button
- Button selector: `.chat-initial__btn`
- Chat input: `#userInput` (hidden until Begin Awakening clicked)
- Bypass code: `pb-full-bypass` → triggers Keen identity + Discover button
- Pricing section: `.pricing-section` with `display:none` by default (JS shows after Discover flow)
- Pricing CTAs: `.pricing-card__cta` buttons

### 4. VISUAL_SELF Tag
- Exists in embedded JS string (system prompt for AI)
- Explicitly marked "STRIPPED before display - user never sees it"
- NOT in any visible DOM text nodes
- Detection: search `<script>` contents, not visible text nodes

### 5. Pricing + PayPal Flow
- Pricing section hidden by default (`display:none`)
- Shown after Discover button clicked and Keen talks about capabilities
- PayPal modal triggered by `.pricing-card__cta` click
- Modal shows: plan name, price, "Secured by PayPal" footer
- PayPal SDK confirmed: `paypal.com/sdk` loaded in HTML
- Plan subscription IDs: P-1AG936074F... (Awakened), P-2SA65600... (Bonded), etc.

### 6. Mobile Testing
- Container padding: 24px (`.container` class) on both sides at 375px
- No horizontal scroll (scrollWidth == viewportWidth)
- Awakening section: `padding: 120px 24px`
- Mobile shows Begin Awakening button below animated brain logo
- Sandbox mode adds orange banner at top: "SANDBOX MODE - No real charges"

### 7. Console Errors to Expect (Not Bugs)
- `elementorFrontendConfig is not defined` - Elementor issue on pw-protected pages, no user impact
- `SCC Library has already been loaded` - duplicate script load, minor
- `fetch failed: net::ERR_FAILED` to 89.167.19.20:8765 - backend SSL cert issue (self-signed)

---

## Timing Reference
- Page load after password: 8 seconds
- Chat response to "hello": ~15 seconds
- Bypass response: ~15 seconds
- Discover/Keen capabilities loading: 20 seconds
- PayPal modal after button click: ~10 seconds
- Wait between page loads: 15 seconds minimum

---

## File Paths
- Test scripts: `/home/jared/projects/AI-CIV/aether/tools/test_pay_pages_final.py`
- Audit report: `/home/jared/projects/AI-CIV/aether/exports/pay-test-audit-report-2026-02-20.md`
- Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/` (prefix: 20260220_)
