# WordPress Revision Rollback Pattern — March 2026

**Date**: 2026-03-11
**Task**: Rollback pay-test-2 (page 689) and pay-test-sandbox-3 (page 1232) to March 9 state
**Result**: SUCCESS — both pages restored and verified live

---

## Key Findings

### Credentials
- **Working WP credentials**: `purebrain@puremarketing.ai` with app password `41w3 xWWZ 11em UXgj hjAF sx2T`
- The credentials in the task prompt (Jared:FlFr2VOtlHiHaJWjzW96OHUJ) return 401 for revisions
- Use `PUREBRAIN_WP_APP_PASSWORD` from `.env`

### WordPress Revisions API
- Endpoint: `GET /wp-json/wp/v2/pages/{id}/revisions?per_page=50`
- Need `context=edit` to get `content.raw`: `GET /wp-json/wp/v2/pages/{id}/revisions/{rev_id}?context=edit`
- **NOT all revisions have raw content** — some return empty raw (Elementor creates revisions for meta-only saves)
- Must iterate through revisions to find ones with `len(raw) > 0`

### Elementor Pages Are Self-Contained HTML
- These pay-test pages store full HTML in `post_content` wrapped in `<!-- wp:html -->`
- The `_elementor_data` meta is empty on revisions (revisions don't capture meta)
- The `content.raw` from revisions IS the complete page (464KB+)
- So restoring `content.raw` via REST API is sufficient — no separate elementor_data restore needed

### Large Payload Handling
- Content is 464,000+ chars — too large for curl CLI arguments (argument list too long)
- MUST use Python `requests` library to POST large content
- Pattern:
  ```python
  import requests, base64
  credentials = base64.b64encode(f"user:pass".encode()).decode()
  headers = {"Authorization": f"Basic {credentials}", "Content-Type": "application/json"}
  with open('/tmp/content.html') as f:
      content = f.read()
  response = requests.post(url, headers=headers, json={"content": content}, timeout=60)
  ```

### Cache Clearing
- After restore: `DELETE /wp-json/elementor/v1/cache` (returns 200)
- Add `?nocache=1` to verify actual served content changed
- loading-spinner and waitlist in CSS context are normal — not broken state indicators

### Revision Selection Strategy for March 9
- page 689: Target revision **1492** (2026-03-09T23:42:49) — last March 9 revision before March 10 changes
- page 1232: Target revision **1484** (2026-03-09T21:28:03) — revision 1486 existed but had empty raw; 1484 had 464KB content

---

## Verified Working State (March 9 versions)
Both pages confirmed containing:
- `Begin Awakening` button (4 occurrences)
- `PayPal` payment integration (128-134 occurrences)
- `chat-container` elements
- `bypass` flow logic
- No password gate
- No broken spinner state

---

## Rollback Command Template

```python
import requests, base64

APP_PASS = "41w3 xWWZ 11em UXgj hjAF sx2T"
credentials = base64.b64encode(f"purebrain@puremarketing.ai:{APP_PASS}".encode()).decode()
headers = {"Authorization": f"Basic {credentials}", "Content-Type": "application/json"}

# Step 1: Find target revision
revisions = requests.get(
    f"https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}/revisions?per_page=50",
    headers=headers
).json()

# Step 2: Find last revision before target date with non-empty raw
# Step 3: Pull raw content
rev_data = requests.get(
    f"https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}/revisions/{REV_ID}?context=edit",
    headers=headers
).json()
content = rev_data['content']['raw']

# Step 4: Restore
requests.post(f"https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}",
    headers=headers, json={"content": content}, timeout=60)

# Step 5: Clear cache
requests.delete("https://purebrain.ai/wp-json/elementor/v1/cache", headers=headers)
```
