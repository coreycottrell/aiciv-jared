# Clone pay-test-2 (689) to pay-test-sandbox-2 (688) — PayPal Sandbox Swap

**Date**: 2026-03-01
**Agent**: dept-systems-technology → full-stack-developer
**Pages**: 689 (source, untouched), 688 (target, updated)
**Status**: DEPLOYED AND VERIFIED

## Task

Jared: "start pay-test-sandbox-2 from scratch by cloning pay-test-2 which is working perfectly and then just replace the paypal live payments with sandbox payments"

Clone _elementor_data from page 689 (pay-test-2) → page 688 (pay-test-sandbox-2), swapping only the PayPal client ID.

## What Was Found in Page 689

- _elementor_data length: 491054 chars (5 top-level sections)
- Production PayPal client ID: AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI (1 occurrence)
- Production SDK URL: www.paypal.com/sdk/js (1 occurrence — note: this was NOT swapped, the sandbox client ID causes PayPal SDK to auto-detect sandbox mode)
- Plan IDs found: P-3VH43554A66001716NGLTFKY, P-43A28944XN5237411NGLTFLA, P-1AG936074F0953120NGLTFKY, P-2SA65600MT088594TNGLTFKY
- Plan IDs NOT changed (sandbox uses createOrder, not subscription)
- PB-SANDBOX-PAGE script: already embedded in page 689 (from prior work)
- Bypass Blocker: already embedded in page 689 (from prior work)

## What Was Changed

ONLY the PayPal client ID:
- Production: AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI
- Sandbox:  AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_

Note: The SDK URL (www.paypal.com/sdk/js) was NOT changed. PayPal SDK auto-detects sandbox vs live based on the client ID.

## Deployment Steps

1. GET page 689 with context=edit → _elementor_data (491054 chars) + post_content (436329 chars)
2. str.replace() production client ID → sandbox client ID (1 replacement)
3. Validate modified _elementor_data is valid JSON (5 top-level items — passed)
4. PUT to page 688: meta._elementor_data (491054 chars written, confirmed)
5. PUT to page 688: content (post_content also updated)
6. DELETE /elementor/v1/cache (returned 200 empty body — success)

## Verification Results

### DB check (page 688):
- _elementor_data length: 491054 chars
- sandbox client ID present: YES
- production client ID present: NO
- Result: PASS

### Live page check (https://purebrain.ai/pay-test-sandbox-2/):
- HTML length: 144870 chars
- sandbox client ID: YES
- production client ID: NO
- pricing content: YES
- PureBrain chatbox: YES
- Result: PASS

### Page 689 untouched check:
- production client ID: YES (still there)
- sandbox client ID: NO (not introduced)
- Result: PASS

## Key Notes

1. **SDK URL not swapped**: www.paypal.com/sdk/js → left as-is. PayPal auto-detects env from client ID.
2. **Plan IDs not swapped**: P-xxx plan IDs are production subscription plan IDs. The sandbox page uses createOrder (from the PB-SANDBOX-PAGE embedded script). These plan IDs will be called but the sandbox override intercepts before subscription checkout.
3. **PB-SANDBOX-PAGE already in 689**: The prior work on 689 embedded a sandbox setup script. This got cloned to 688 as-is — on 688 it will now trigger with the sandbox client ID, making the double-safety-net even stronger.
4. **Python urllib required**: curl has arg length limits at ~100KB payload. 516KB payload requires Python urllib.
5. **Cache DELETE returns empty body**: Normal — don't try to JSON parse it.

## Script

/tmp/clone_689_to_688.py (session-only, not persisted)
/tmp/verify_688.py (session-only, not persisted)
