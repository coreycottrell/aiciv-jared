# Sandbox-3 Homepage Design Clone — 2026-03-10

## Task
Clone homepage design (page 11) to sandbox-3 (page 1232). Preserve chatbox, payment tiers, PayPal sandbox links, chat flow.

## Key Finding: Elementor Pages Need BOTH post_content AND _elementor_data

When cloning design to an Elementor page:
1. **post_content alone is NOT enough** — Elementor ignores it when `_elementor_edit_mode = 'builder'`
2. **Must also set `_elementor_data`** — full Elementor JSON with html widget containing the HTML
3. **Must also set `_elementor_edit_mode = 'builder'`** — activates Elementor rendering
4. **Must clear Elementor cache** — `DELETE /wp-json/elementor/v1/cache`

## Elementor Data Structure (for wp:html pages)
```json
[{
  "id": "abc12345", "elType": "section",
  "settings": {"layout": "full_width", "gap": "no", "padding": {...0}, "margin": {...0}},
  "elements": [{
    "id": "def67890", "elType": "column",
    "settings": {"_column_size": 100, "padding": {...0}},
    "elements": [{
      "id": "unique_id", "elType": "widget", "widgetType": "html",
      "settings": {"html": "[RAW HTML WITHOUT wp:html WRAPPER]"}
    }]
  }]
}]
```

## Source/Destination Split Points
- **pay-test-5 (1527)**: Design ends at `<!-- === PAY-TEST-2 PAYPAL + CHATBOX SCRIPTS === -->` (index 676300 in WP backup)
- **sandbox-3 local**: Payment starts at `<script>\n/* === PayPal SDK Integration` (index 430783)

## What Gets Replaced (Design) vs Preserved (Payment)
- **Design from pay-test-5**: Hero, CSS, demo section, comparison table, timeline, testimonials, footer, learn-more, portal, curtain, telegram sections
- **Payment from sandbox-3**: PayPal SDK + SANDBOX client ID + PLAN_IDS + PRICES + chatbox + chat flow + verify endpoint

## Key Differences: Live (pay-test-5) vs Sandbox (sandbox-3)
- `PAYPAL_CLIENT_ID`: `AWgWNlBQ...` (live) vs `AYTFob05...` (sandbox)
- `VERIFY_ENDPOINT`: `:8443` port (live) vs no port (sandbox)
- `PLAN_IDS`: 4 tiers with `// LIVE` comments (live) vs 3 tiers no comments (sandbox)
- `PRICES`: `Awakened: 79.00, Bonded: 149.00` (live) vs `Awakened: 149.00` x2 (sandbox)

## Password Protection
- sandbox-3 is password-protected: `PureBrain.ai253443$$`
- This is intentional — verification must use session cookies

## Files Saved
- Backups: `exports/cto-sandbox3-design-clone/`
  - `sandbox3-elementor-data-BACKUP.json`
  - `homepage-11-content-BACKUP.html`
  - `pay-test-5-1527-content-BACKUP.html`
- Final: `sandbox3-WP-FINAL.html`
- Local updated: `purebrain-site/public/pay-test-sandbox-3/index.html`
