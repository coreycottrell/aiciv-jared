# Cloudflare Tunnel: Complete Setup - PureBrain API (COMPLETED)

**Date**: 2026-02-20
**Type**: operational
**Agent**: devops-engineer
**Task**: Full Cloudflare Tunnel setup for api.purebrain.ai

---

## Outcome

Cloudflare Tunnel fully operational. api.purebrain.ai serving with trusted TLS.
WordPress pages 439 and 468 updated. No more self-signed cert errors.

---

## Completed Steps (in order)

1. Browser auth completed by Jared -> cert.pem appeared at `/root/.cloudflared/cert.pem`
2. `sudo cloudflared tunnel create purebrain-api`
   - Tunnel ID: `fa55839c-e753-4a96-935c-cc58cf24b4b8`
   - Credentials: `/root/.cloudflared/fa55839c-e753-4a96-935c-cc58cf24b4b8.json`
3. Config written to `/etc/cloudflared/config.yml` (noTLSVerify: true, localhost:8443)
4. `sudo cloudflared tunnel route dns purebrain-api api.purebrain.ai` -> CNAME auto-created
5. `sudo cloudflared service install && sudo systemctl enable cloudflared && sudo systemctl restart cloudflared`
6. Health check: `https://api.purebrain.ai/api/health` -> `{"ssl":true,"status":"ok"}`
7. WordPress pages 439 and 468 updated via `tools/security/update-endpoint-urls.py --execute`

---

## WordPress Update Gotcha: context=edit Required

The script initially failed because the REST API did not return `_elementor_data` in
meta without the `context=edit` query parameter.

Fix applied to `tools/security/update-endpoint-urls.py`:
```python
# WRONG:
url = f"{WORDPRESS_URL}/wp-json/wp/v2/pages/{page_id}"

# RIGHT:
url = f"{WORDPRESS_URL}/wp-json/wp/v2/pages/{page_id}?context=edit"
```

Without `context=edit`, WordPress omits protected/internal meta fields from the response.
This applies to ANY meta field that is not explicitly registered for public REST access.

---

## Replacements Made Per Page

Each page (439 and 468) had 7 URL replacements:
- 1x `/api/log-conversation`
- 5x `/api/verify-payment`
- 1x `/api/log-pay-test`

All JSON validated with `json.loads()` before and after. Elementor cache cleared.

---

## Final State

| Item | Value |
|------|-------|
| Tunnel name | purebrain-api |
| Tunnel ID | fa55839c-e753-4a96-935c-cc58cf24b4b8 |
| Domain | api.purebrain.ai |
| DNS | CNAME -> fa55839c-e753-4a96-935c-cc58cf24b4b8.cfargotunnel.com |
| Backend | https://localhost:8443 (self-signed, noTLSVerify=true) |
| Systemd | cloudflared.service, enabled, active |
| PoPs connected | fra08, fra10, fra13, fra19 (4 connections via QUIC) |
| Pages updated | 439 (pay-test), 468 (pay-test-sandbox) |

---

## Verification Commands

```bash
# Check tunnel service
ssh jared@89.167.19.20 'sudo systemctl status cloudflared --no-pager'

# Check health endpoint
curl https://api.purebrain.ai/api/health

# Check no old IP refs remain in pages
python3 -c "
import requests, base64, json, os
from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
WP_USER = 'Aether'
WP_PASS = os.environ.get('PUREBRAIN_WP_APP_PASSWORD', '')
auth = base64.b64encode(f'{WP_USER}:{WP_PASS}'.encode()).decode()
headers = {'Authorization': f'Basic {auth}'}
for page_id in [439, 468]:
    r = requests.get(f'https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit', headers=headers, timeout=30)
    elem = r.json().get('meta', {}).get('_elementor_data', '')
    print(f'Page {page_id}: old_ip={elem.count(chr(56)+chr(57)+ \".\")}, new_domain={elem.count(\"api.purebrain.ai\")}')
"
```
