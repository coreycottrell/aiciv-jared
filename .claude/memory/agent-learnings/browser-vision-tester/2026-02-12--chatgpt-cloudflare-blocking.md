# ChatGPT Cloudflare Blocking - Automation Workaround

**Date**: 2026-02-12
**Agent**: browser-vision-tester
**Type**: operational
**Topic**: Cloudflare bot protection blocks headless ChatGPT access

---

## Context

Tasked with researching 3 custom GPTs on ChatGPT via browser automation in a WSL2 headless environment.

## Key Finding

ChatGPT is protected by Cloudflare Turnstile which blocks headless Playwright:
- Page loads but shows "Verify you are human" checkbox
- Cannot proceed without human interaction
- Screenshot captured: `/home/jared/projects/AI-CIV/aether/docs/research/gpt-analysis/screenshots/chatgpt_test.png`

## Environment Constraints (WSL2 Headless)

| Tool | Status |
|------|--------|
| Playwright headless | Works for non-protected sites |
| Desktop-vision | Unavailable (no `/mnt/c/`, no X11) |
| WebFetch | Blocked (403) |
| powershell.exe | Not found |

## Solution Created

Automation script: `/home/jared/projects/AI-CIV/aether/tools/gpt-research/research_gpts.py`

Features:
- Persistent browser context (saves login state)
- Headed mode (user can solve CAPTCHA)
- Auto-screenshot at each step
- Extracts GPT responses
- Generates markdown report

## How to Run (requires GUI)

```bash
# From GUI environment (Windows or WSLg)
python3 /home/jared/projects/AI-CIV/aether/tools/gpt-research/research_gpts.py
```

The script will:
1. Open visible browser
2. User solves Cloudflare challenge once
3. Automation takes over for GPT research
4. Results saved to `docs/research/gpt-analysis/`

## Pattern: Cloudflare-Protected Site Automation

For sites with Cloudflare Turnstile:
1. **Cannot use pure headless** - always blocked
2. **Use persistent context** - login/verification survives sessions
3. **Headed mode required** - human solves initial CAPTCHA
4. **After first run** - subsequent runs may work headless (context saved)

## Related Memories

- `2026-02-05--gpt-feature-research-challenges.md` - Similar blocks
- `2026-02-05--chatgpt-settings-research.md` - Alternative sources

---

**Key Learning**: Cloudflare Turnstile is the gatekeeper for ChatGPT automation. Persistent browser context + headed mode is the workaround.
