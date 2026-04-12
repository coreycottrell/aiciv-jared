# Cloudflare Worker Deployment Guide
## PureBrain Claude API Proxy - Secured Version

**File to deploy**: `tools/security/cloudflare-worker-secured.js`
**Target workers**:
- `pure-brain-dashboard-api` (workers.dev subdomain)
- Custom domain: `api.puremarketing.ai`

---

## Step 0: Generate Your PB_AUTH_TOKEN

Run this command locally to generate a strong secret token:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

Example output: `9sqpzbBEayQSEM0Et6oiVwCxeBhrUezS`

**Copy this value. You will need it in two places:**
1. Cloudflare dashboard (as `PB_AUTH_TOKEN` environment variable)
2. Your purebrain.ai JavaScript (as the value sent in `X-PB-Token` header)

**Keep this token secret.** It should never appear in public Git commits.

---

## Step 1: Create KV Namespace for Rate Limiting

KV (Key-Value) storage is used to track per-IP request counts.

1. Go to https://dash.cloudflare.com
2. In the left sidebar, click **Workers & Pages**
3. Click **KV** in the top navigation (or find it under Storage)
4. Click **Create namespace**
5. Name it: `PUREBRAIN_RATE_LIMIT`
6. Click **Add**
7. Note the **Namespace ID** shown in the list - you will need it in Step 3

---

## Step 2: Deploy the Worker Code

1. Go to https://dash.cloudflare.com
2. Click **Workers & Pages** in the left sidebar
3. Find your existing worker named `pure-brain-dashboard-api`
4. Click on the worker name
5. Click **Edit code** (or the `</>` icon)
6. Select **ALL** existing code in the editor (Ctrl+A / Cmd+A)
7. **Delete** it
8. Open `tools/security/cloudflare-worker-secured.js` from this repo
9. Copy the entire file contents
10. Paste into the Cloudflare editor
11. Click **Save and deploy**

Repeat for any other workers that point to the same proxy.

---

## Step 3: Bind the KV Namespace

After deploying the code, the worker needs to be connected to the KV namespace.

1. From your worker's page, click **Settings** tab
2. Click **Variables and Secrets** (or **Variables** in older UI)
3. Scroll down to **KV Namespace Bindings**
4. Click **Add binding**
5. Set:
   - **Variable name**: `RATE_LIMIT_KV`  (must match exactly - case sensitive)
   - **KV namespace**: Select `PUREBRAIN_RATE_LIMIT` from the dropdown
6. Click **Save**

---

## Step 4: Set Encrypted Environment Variables

Still in **Settings > Variables and Secrets**:

### ANTHROPIC_API_KEY (already set - just verify it's there)
- Variable name: `ANTHROPIC_API_KEY`
- Value: `sk-ant-...` (your existing key)
- **Encrypt**: Yes (click the lock icon or "Encrypt" checkbox)

### PB_AUTH_TOKEN (new - must add this)
1. Click **Add variable**
2. Variable name: `PB_AUTH_TOKEN`
3. Value: the token you generated in Step 0
4. Click **Encrypt** (critical - this hides the value from the dashboard UI)
5. Click **Save**

**After saving, click Deploy again** to pick up the new env vars.

---

## Step 5: Update purebrain.ai JavaScript

Every page that calls the Cloudflare worker proxy needs to send the `X-PB-Token` header.

### Affected pages
- Homepage chatbox (`purebrain.ai`)
- pay-test page (`purebrain.ai/pay-test/`)
- pay-test-sandbox page (`purebrain.ai/pay-test-sandbox/`)

### Change needed in the JavaScript fetch call

Find the existing code that calls the worker endpoint. It likely looks like:

```javascript
const response = await fetch('https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(payload)
});
```

Update it to add the token header:

```javascript
const response = await fetch('https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-PB-Token': 'YOUR_PB_AUTH_TOKEN_HERE',   // <-- add this line
  },
  body: JSON.stringify(payload)
});
```

Replace `YOUR_PB_AUTH_TOKEN_HERE` with the actual token value from Step 0.

### Important notes on token placement in JS

The token is embedded in client-side JavaScript, which means a determined person
COULD find it by inspecting the page source. This is acceptable because:

1. Origin checking is the first defense - requests without `purebrain.ai` as
   the Origin header are rejected before the token is even checked.
2. The token prevents automated scanners and tooling (e.g., curl, Postman, bots)
   from abusing the endpoint without first knowing the token AND spoofing the
   origin header simultaneously.
3. This is the same security model used by most public-facing API proxies.

For additional hardening, consider obfuscating the token assignment in your
JavaScript bundle (not security by obscurity alone, but raises the bar).

---

## Step 6: Verify the Deployment

### Test that legitimate requests work

From your browser console on purebrain.ai:

```javascript
fetch('https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-PB-Token': 'YOUR_TOKEN_HERE'
  },
  body: JSON.stringify({
    model: 'claude-3-5-haiku-20241022',
    max_tokens: 10,
    messages: [{ role: 'user', content: 'Hello' }]
  })
}).then(r => r.json()).then(console.log);
```

Expected: `200 OK` with a Claude response.

### Test that unauthorized requests are blocked

From any terminal (no Origin header = no purebrain.ai origin):

```bash
curl -X POST https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-5-haiku-20241022","max_tokens":10,"messages":[{"role":"user","content":"hack"}]}'
```

Expected: `403 Forbidden`

### Test rate limiting (optional)

```bash
for i in $(seq 1 35); do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST \
    https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages \
    -H "Content-Type: application/json" \
    -H "Origin: https://purebrain.ai" \
    -H "X-PB-Token: YOUR_TOKEN_HERE" \
    -d '{"model":"claude-3-5-haiku-20241022","max_tokens":1,"messages":[{"role":"user","content":"x"}]}'
done
```

Expected: first 30 return `200`, next 5 return `429`.

---

## Step 7: Monitor Rejection Logs

All rejected requests are logged to Cloudflare's log stream.

1. Go to your worker in the Cloudflare dashboard
2. Click the **Logs** tab (or **Real-time Logs**)
3. Click **Begin log stream**
4. Rejections appear as JSON with `"event":"rejected"` and include:
   - `reason` - why it was rejected (origin/token/rate limit)
   - `ip` - client IP
   - `origin` - the Origin header value
   - `ts` - timestamp

---

## Security Architecture Summary

```
Request from browser
       |
       v
[ Origin check ]  --> NOT in whitelist --> 403 + log
       |
       v
[ Token check  ]  --> X-PB-Token missing/wrong --> 403 + log
       |
       v
[ Rate limit   ]  --> >30 req/min from this IP --> 429 + log
       |
       v
[ Proxy to Anthropic API ]
       |
       v
Response to browser
```

Both origin AND token must pass. Failing either returns 403 with no
information about which check failed (avoids enumeration).

---

## Rotating the Token

When you need to rotate `PB_AUTH_TOKEN`:

1. Generate a new token (Step 0)
2. Update `PB_AUTH_TOKEN` in Cloudflare dashboard (Settings > Variables)
3. Deploy the updated token to all purebrain.ai pages' JavaScript
4. There is a brief window between steps 2 and 3 where the chatbox will
   return 403 - do this during low-traffic hours (overnight)

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Chatbox returns 403 | JS not sending X-PB-Token header | Add header to fetch call |
| Chatbox returns 403 | PB_AUTH_TOKEN mismatch | Verify token matches in both places |
| Chatbox returns 503 | ANTHROPIC_API_KEY not set | Add env var in Cloudflare dashboard |
| Chatbox returns 502 | Anthropic API down | Check status.anthropic.com |
| Rate limit hitting legitimate users | 30/min too low | Increase RATE_LIMIT_MAX_REQUESTS in worker code |
| KV binding missing | Worker logs warn about rate limiting disabled | Complete Step 3 |

---

## wrangler CLI Alternative (Advanced)

If you prefer CLI deployment over the dashboard:

```bash
# Ensure wrangler is available
npx wrangler --version

# Login to Cloudflare
npx wrangler login

# Deploy the worker
npx wrangler deploy tools/security/cloudflare-worker-secured.js \
  --name pure-brain-dashboard-api \
  --compatibility-date 2024-01-01

# Set secrets (prompts for value, never stored in plaintext)
npx wrangler secret put ANTHROPIC_API_KEY --name pure-brain-dashboard-api
npx wrangler secret put PB_AUTH_TOKEN --name pure-brain-dashboard-api

# Create KV namespace
npx wrangler kv:namespace create "PUREBRAIN_RATE_LIMIT"

# Bind KV namespace (add to wrangler.toml or use dashboard)
# Note: wrangler.toml binding still requires dashboard confirmation for encrypted vars
```

**Note**: For the KV binding, you'll still need to confirm it in the dashboard
or add a `wrangler.toml` with the namespace ID from the `kv:namespace create` output.

---

*Generated by security-engineer-tech agent - 2026-02-20*
