# QA Audit: purebrain.ai/pay-test/ - 2026-02-18

**Type**: operational
**Topic**: Full QA audit of pay-test page WordPress page 439

## Page Structure Discovery

The pay-test page has an unusual triple-nested HTML structure:
- Outer WP page (DOCTYPE 1, elementor-439)
- Inside Elementor HTML widget: old homepage snapshot (DOCTYPE 2, dated 2026-02-17T22:02)
- Inside that snapshot's elementor-11 rendering: current homepage code (DOCTYPE 3)

All content, chatbox, PayPal, and post-payment flow live in the innermost layer.
Browsers handle nested DOCTYPEs by ignoring nested html/head/body tags but processing content inline.
The main purebrain.ai page has the SAME 3-DOCTYPE structure, so this is normal for this site.

## API Endpoints Tested and Working

- Primary: https://api.puremarketing.ai/v1/messages -> 200 OK, correct response
- Fallback: https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages -> 200 OK
- Both have correct CORS headers (access-control-allow-origin: https://purebrain.ai)
- Netlify logging proxy: https://sageandweaver-network.netlify.app/api/capture-proxy -> 200 OK (with valid payload)

## Confirmed Bugs

1. **PayPal Client ID**: `PAYPAL_CLIENT_ID = 'PAYPAL_CLIENT_ID'` - literal placeholder. SDK fails to load (HTTP 400), falls back to form POST approach automatically.
2. **Self-signed SSL on log server**: 89.167.19.20:8443 uses self-signed cert (CN=89.167.19.20). Browsers BLOCK this without exception - dual logging silently fails.
3. **ACGEE_API_KEY exposed**: `os3ctWW0CAQSVPnM-WeNZr75SKTlrvliGTTvkdanYbc` visible in page source.
4. **Behind-the-Curtain slide count**: 10 slides implemented, spec requires 11. The AI intro message says "There are 10 slides."
5. **startConversation() no try-catch**: Async errors are invisible to user. Should add error display.

## What Works

- Page loads: 200 OK, 485KB, 0.37s
- All 28 CSS/JS resources: 0 failures
- All 7 images: 200 OK
- Both Cloudinary videos: 206 OK (streaming)
- All 9 external links: OK (claude.ai/settings returns 403 but that's expected - login required)
- Chatbox DOM elements: all exist (chatMessages, userInput, submitBtn, etc.)
- startConversation function: globally accessible, properly scoped
- handleSubmit function: properly wired to form onsubmit
- FALLBACK_OPENING: implemented (works when API fails)
- PayPal modal: ESC, backdrop click, X button all wired
- Post-payment flow: all 5 phases implemented (questionnaire, curtain, telegram, claude max, completion)
- AI name carryover: integration glue correctly reads state.aiName
- Verify-payment endpoint: 89.167.19.20:8443/api/verify-payment -> 200 OK (with -k flag)
- Log-pay-test endpoint: 89.167.19.20:8443/api/log-pay-test -> 200 OK (with -k flag)

## Chatbox "Not Working" - Investigation Result

After comprehensive analysis, the chatbox JavaScript code is correct and should function.
The APIs work. CORS is configured. DOM elements exist. Scripts are in the correct global scope.
The chatbox script on pay-test is BYTE-FOR-BYTE IDENTICAL to the working main page script (55925 chars).

The "not working" report from Jared may be:
1. A browser-console JS error we can't see from static analysis
2. A CSS rendering issue making chatbox invisible in specific browsers
3. Referring to the post-payment flow specifically (PayPal SDK fails -> form fallback)
4. An intermittent API timeout that looks like chatbox failure

**Recommended next step**: Use Playwright/browser-vision-tester to actually click "Begin Awakening" and observe what happens in a real browser.

## Security Summary

- No Anthropic API keys exposed in source
- PayPal Client ID: literal placeholder (not a real key - OK for now)
- Raw IP (89.167.19.20) exposed in source - minor issue
- ACGEE_API_KEY in source - medium issue (third-party logging API key)
- Developer comments: none visible (previously fixed)
