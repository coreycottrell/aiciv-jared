# Telegram Onboarding Text Update - Pay Test Pages

**Date**: 2026-02-28
**Type**: technique + gotcha
**Pages updated**: 688, 689, 468, 439

---

## What Was Changed

In the post-payment chatbox flow, the BotFather deep link section had:

**OLD:**
```
First, make sure you're logged into Telegram. If you're not sure, visit
<a href=\"https://web.telegram.org/\" target=\"_blank\" rel=\"noopener\"
style=\"color:var(--light-blue);\">web.telegram.org</a> to confirm you're signed in.
```

**NEW:**
```
If you're on a desktop, visit <a href=\"https://web.telegram.org\" target=\"_blank\">
web.telegram.org</a> to confirm you're signed in. If you're on your phone,
<a href=\"https://telegram.org/dl\" target=\"_blank\">tap here</a> to download the
Telegram app or open it.
```

---

## Key Technical Patterns

### 1. Cloudflare blocks Python urllib but allows curl
- `urllib.request` with standard headers returns HTTP 403 (Cloudflare error code 1010)
- `curl` with `User-Agent: Mozilla/5.0 (compatible; WP REST API client)` works fine
- Always use `subprocess.run(["curl", ...])` for purebrain.ai WP REST calls

### 2. The "Argument list too long" curl problem for large pages
- Pages 688/689/468/439 are ~400KB+ of content
- Passing content as `-d "..."` CLI arg causes `OSError: [Errno 7] Argument list too long`
- Solution: write payload to `tempfile.NamedTemporaryFile` and use `-d @/path/to/file`

### 3. Text escaping in WordPress raw post_content
- Apostrophes in the JS template literal: literal `'` (ord 39) - NOT backslash-escaped
- HTML attribute quotes inside JS template literal: literal `\"` (backslash + doublequote)
- Python repr() shows `\'` for apostrophes and `\\"` for backslash-doublequote
- To match these in Python string literals: use `'` directly, and `\\"` for the backslash-quote pairs

### 4. post_content and _elementor_data have identical text
- The Telegram text appears identically in both `post_content` and `_elementor_data`
- The same `str.replace()` works on both fields without any extra escaping
- _elementor_data newlines ARE double-escaped (`\\n`) but the target text has no newlines

### 5. Pages 468 and 439 have TWO Telegram sections
- `// --- Telegram Login Confirmation ---` section: "Before we set up your bot..." (NOT changed)
- `// --- BotFather deep link ---` section: this was the one changed
- The dry-run confirmed exactly 1 occurrence of OLD_TEXT on each page

### 6. Page 11 has no chatbox Telegram text
- Only mention of Telegram on page 11 is in a value-card description ("Telegram integration")
- No changes needed to page 11

---

## Verification Approach (BUILD -> VERIFY -> SHIP)

1. `find_telegram_text.py` - found text on all pages via search
2. `verify_exact.py` - character-by-character byte analysis to build exact match string
3. `dryrun_verify.py` - confirmed `OLD_TEXT.count()` == 1 on all 4 pages before any changes
4. `update_telegram_text.py` - applied replacement + cleared Elementor cache
5. `post_deploy_verify.py` - re-fetched all pages, confirmed old gone, new present

All 4 pages: PASS

---

## Files Created
- `/home/jared/projects/AI-CIV/aether/tools/update_telegram_text.py` - main update script
- `/home/jared/projects/AI-CIV/aether/tools/dryrun_verify.py` - pre-deploy dry run
- `/home/jared/projects/AI-CIV/aether/tools/post_deploy_verify.py` - post-deploy verification
