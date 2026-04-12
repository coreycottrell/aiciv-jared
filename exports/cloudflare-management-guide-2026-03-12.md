# purebrain.ai Cloudflare Pages Management Guide

**Date**: 2026-03-12
**Prepared by**: dept-it-support
**Environment**: Hybrid — WordPress (purebrain.ai origin) + Cloudflare Pages (purebrain-staging.pages.dev) + Cloudflare Tunnel (api, portal, cc subdomains)

---

## Architecture Summary (Read This First)

purebrain.ai currently runs on a **hybrid stack**:

| Layer | What It Is | Who Manages It |
|-------|-----------|----------------|
| **WordPress** | Origin content (purebrain.ai/wp-admin) | Aether via WP REST API |
| **Cloudflare CDN/DNS** | All DNS, SSL, caching proxy | Jared's CF account |
| **Cloudflare Tunnel** | `api.`, `portal.`, `cc.`, `*.purebrain.ai` subdomains → local server | aether-telegram.service on server |
| **Cloudflare Pages** | Static export staging site (`purebrain-staging.pages.dev`) | Aether via wrangler CLI |
| **CF Pages Custom Domain** | Not yet live — DNS flip still pending for full CF Pages production | IT action required |

**CF Account credentials** (already in `.env`):
- Account email: `jared@puretechnology.nyc`
- Account ID: `d526a3e9498dd167509003004df03290`
- CF Pages API Token: stored as `CF_PAGES_TOKEN` in `.env`
- CF Global API Key: stored as `CF_GLOBAL_API_KEY` in `.env`

**CF Pages project**: `purebrain-staging` (project ID: `7c467c82-7f69-46a4-a337-53c57a6e30cc`)
**Staging URL**: `https://purebrain-staging.pages.dev`

---

## TOPIC 1: Inviting Team Members and AIs to Manage the Site

### How Cloudflare Account Membership Works

Cloudflare has two access models:
1. **Account Members** — Human collaborators added to your Cloudflare account (for Jared adding a person)
2. **API Tokens** — Scoped programmatic credentials (for Aether or Lyra or any AI deploying automatically)

### Adding a Human Collaborator (e.g., a developer or team member)

**Step-by-step:**

1. Log in at `https://dash.cloudflare.com` with `jared@puretechnology.nyc`
2. Click your account name (top-left) → **Manage Account** → **Members**
3. Click **Invite Member**
4. Enter their email address
5. Assign a **Role** (see role table below)
6. Click **Send Invite** — they receive an email to accept

**Cloudflare Account Roles:**

| Role | What They Can Do | Use For |
|------|-----------------|---------|
| **Administrator** | Full account access, billing, all zones | Trusted full-access collaborator |
| **Administrator (Read Only)** | View everything, change nothing | Auditors, consultants reviewing setup |
| **Cloudflare Pages** | Deploy and manage Pages projects only | A developer who only touches static deploys |
| **DNS** | Edit DNS records only | Someone managing domain records |
| **Firewall** | Edit WAF/firewall rules only | Security-focused team member |
| **Workers** | Deploy and manage Workers/Functions | Developer working on edge functions |

**Recommendation for a second AI or trusted developer**: Assign the **Cloudflare Pages** role. This gives deploy rights without access to DNS, billing, or other zones.

### Creating an API Token for Programmatic Access (Aether/Lyra Deploying)

This is how AIs deploy to CF Pages without username/password.

**Current token**: `CF_PAGES_TOKEN` in `.env` — already working for wrangler deploys.

**To create a new token for another AI (e.g., Lyra):**

1. Log in at `https://dash.cloudflare.com`
2. Click your account icon (top-right) → **My Profile** → **API Tokens**
3. Click **Create Token**
4. Choose **Create Custom Token**
5. Configure:
   - **Token name**: `lyra-pages-deploy` (or whatever AI/agent name)
   - **Permissions**:
     - Account > Cloudflare Pages > Edit
     - (Optional) Zone > Zone > Read (if they need to check DNS)
   - **Account Resources**: Include — your specific account
   - **Zone Resources**: Not needed for Pages-only access
6. Click **Continue to Summary** → **Create Token**
7. Copy the token immediately — it is shown only once
8. Store in the relevant `.env` or pass it to that AI's environment

**How that AI then deploys:**

```bash
CLOUDFLARE_API_TOKEN=<their-token> CLOUDFLARE_ACCOUNT_ID=d526a3e9498dd167509003004df03290 \
npx wrangler pages deploy /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/ \
  --project-name=purebrain-staging \
  --branch=main \
  --commit-dirty=true
```

### Checking Who Currently Has Access

1. Dashboard → **Manage Account** → **Members** → see list of members
2. Dashboard → Profile → **API Tokens** → see all active tokens

**Action item**: Review both lists. Revoke any tokens that are no longer in use. Name each token by who/what uses it so you can revoke selectively.

---

## TOPIC 2: SEO Management — What Changed and What to Do

### The Situation

WordPress + RankMath/Yoast handled:
- Meta title and description injection per page
- Open Graph tags (for social sharing)
- Schema.org markup (structured data)
- XML sitemap generation
- robots.txt management

On CF Pages, all of that is **baked into the exported HTML at deploy time**. The good news: because the CF Pages export is generated FROM WordPress, the RankMath/Yoast tags are already embedded in each page's `index.html` at export time.

**Verification**: The `exports/cf-pages-deploy/index.html` already contains a full Yoast `<script type="application/ld+json">` schema block and meta tags. This confirms SEO metadata transfers correctly in the export.

### What Works Automatically (No Action Needed)

- Per-page `<meta name="description">` — exported from WordPress
- Open Graph tags (`og:title`, `og:image`, `og:description`) — exported
- Twitter card tags — exported
- Schema.org JSON-LD markup — exported (Yoast schema graph)
- Canonical URLs — exported

### What Needs Manual Management on CF Pages

**1. Sitemaps**

WordPress auto-generates `/sitemap_index.xml`. CF Pages does not.

**Option A (Recommended): Keep WordPress as sitemap source**
- WordPress already serves `https://purebrain.ai/sitemap_index.xml`
- Submit THIS URL to Google Search Console (not a CF Pages URL)
- As long as WordPress stays live, this works with zero effort

**Option B: Generate a static sitemap**
- Create `/sitemap.xml` manually in `exports/cf-pages-deploy/sitemap.xml`
- List all blog post and page URLs
- Add to `_redirects` if needed
- Must be manually updated with each new post

**Recommendation**: Use Option A. Point GSC at the WordPress sitemap.

**2. robots.txt**

WordPress serves `/robots.txt` automatically. For CF Pages:

```bash
# Create robots.txt in the CF Pages deploy root
cat > /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/robots.txt << 'EOF'
User-agent: *
Allow: /

Sitemap: https://purebrain.ai/sitemap_index.xml
EOF
```

Then redeploy. This ensures crawlers on the staging/production CF Pages URL also have guidance.

**3. New Page SEO — The Workflow**

When a new page is created:
1. Create/edit the page in WordPress (WP admin or REST API)
2. Set RankMath/Yoast meta in WordPress
3. Re-export the page HTML via the export script
4. Add it to `exports/cf-pages-deploy/{slug}/index.html`
5. Redeploy to CF Pages

The SEO metadata lives in WordPress, gets baked into HTML on export, and deploys to CF Pages.

**4. Google Search Console Integration**

GSC was connected to WordPress. You need to verify ownership on whichever domain GSC currently tracks.

**Current DNS**: `purebrain.ai` resolves to `188.114.96.3` / `188.114.97.3` — these are Cloudflare's proxy IPs. WordPress is behind Cloudflare CDN.

**To check and reconnect GSC:**
1. Go to `https://search.google.com/search-console`
2. Log in with `jared@puretechnology.nyc`
3. Select the `purebrain.ai` property
4. Check if it shows as verified
5. If not verified, use **DNS TXT record** method:
   - GSC gives you a TXT value like `google-site-verification=xxxxx`
   - In Cloudflare dashboard → DNS → Add record: Type TXT, Name `@`, Value `google-site-verification=xxxxx`
   - Click **Verify** in GSC

**The DNS TXT method is most reliable** because it survives hosting changes and does not depend on a specific file being reachable at a specific URL.

**5. SEO Tools Available Without WordPress Admin**

| Tool | Purpose | Access |
|------|---------|--------|
| **SEMRush** | Keyword research, rank tracking, site audit | Existing account |
| **Google Search Console** | Real indexing data, crawl errors, rankings | `jared@puretechnology.nyc` |
| **Cloudflare Analytics** | Traffic data (privacy-first, no cookies) | CF dashboard |
| **Independent Analytics** (WP plugin) | Per-page analytics inside WordPress | WP admin |

---

## TOPIC 3: Reconnecting Analytics and Services

### Google Analytics 4 (GA4)

**Current state**: The exported HTML pages reference WordPress plugins and WP-served scripts. GA4 tracking needs to be verified.

**To check what's currently tracking:**
```bash
grep -r "gtag\|G-[A-Z0-9]" /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/index.html 2>/dev/null | head -5
```

GA4 on WordPress is typically added via:
- A plugin (Site Kit by Google, MonsterInsights)
- WordPress theme `functions.php`
- Or manually in plugin footer injection

Because CF Pages serves static HTML exported from WordPress, **GA4 tracking only works if the `gtag` script was embedded in the HTML at export time**.

**To add GA4 to CF Pages pages reliably:**

Option A — Add to WordPress plugin footer (already injected into all exports):
The existing security plugin injects into `wp_head`. Add the GA4 snippet there so it bakes into all future exports.

```javascript
// Add to the purebrain-security plugin's wp_head output:
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

Replace `G-XXXXXXXXXX` with the actual GA4 measurement ID from the GA4 property settings.

Option B — Add directly to CF Pages `_headers` or a shared layout file if you move to a build framework.

**Action: Confirm the GA4 measurement ID** by checking the GA4 dashboard at `https://analytics.google.com` and looking at the data stream for `purebrain.ai`. The measurement ID starts with `G-`.

### Google Search Console (Re-verify After DNS Change)

See Topic 2, section 4 above. Use the DNS TXT method.

After verifying:
1. Submit `https://purebrain.ai/sitemap_index.xml` as the sitemap
2. Request indexing for any new pages using the URL Inspection tool
3. Monitor the Coverage report for crawl errors

### Brevo (Email Marketing)

Brevo uses:
- **API key** for programmatic email sending (confirmed in `.env`: `BREVO_API_KEY`)
- **Contact lists** (List 3 = Neural Feed, List 4 = Enterprise Leads)
- **SMTP** for WordPress transactional email

**What to check:**
1. Log into Brevo at `https://app.brevo.com`
2. Go to **Senders & IP** — verify `purebrain.ai` domain is still authenticated
3. Check **Domain Authentication** (DKIM/SPF records in Cloudflare DNS)
   - Brevo requires SPF and DKIM TXT records in Cloudflare DNS
   - If not present, deliverability breaks silently
4. In Cloudflare DNS, look for:
   - TXT record: `v=spf1 include:spf.sendinblue.com mx ~all`
   - DKIM CNAME records pointing to Brevo

**If records are missing:**
- Go to Brevo → Senders & IP → Domains → find `purebrain.ai` → copy the TXT values → add to Cloudflare DNS

### PayPal

**Credentials in `.env`:**
- Live client ID: `PAYPAL_CLIENT_ID`
- Sandbox client ID: `PAYPAL_SANDBOX_CLIENT_ID`

PayPal's JavaScript SDK runs client-side in the HTML pages and does not use IPN/webhook URLs in the traditional sense. The current setup uses PayPal JS Buttons that create orders and capture them via the PureBrain API.

**What to verify:**
1. The PayPal app (at `https://developer.paypal.com/dashboard/applications`) must have `purebrain.ai` in its allowed return URL list
2. The live app must not be in sandbox mode for production pages
3. API webhook endpoint if used: `https://api.purebrain.ai/...` — verify the Cloudflare Tunnel is routing correctly to `localhost:8443`

**Cloudflare Tunnel status check:**
```bash
# On the server (89.167.19.20):
sudo systemctl status cloudflared
# Or check tunnel health:
curl -s https://api.purebrain.ai/health
```

---

## TOPIC 4: Full Integration Checklist — What Else Needs Reconnecting

### DNS/SSL (Check First)

| Check | Status | Action If Broken |
|-------|--------|-----------------|
| `purebrain.ai` resolves to CF proxy IPs | Active (188.114.96/97.3) | None needed |
| SSL certificate | Managed by Cloudflare | Check CF dash → SSL/TLS → verify "Full (Strict)" mode |
| WordPress accessible behind CF | Should work | If broken, verify WP origin IP in CF DNS |
| Subdomain `api.purebrain.ai` | Via CF Tunnel | `systemctl status cloudflared` on server |
| Subdomain `portal.purebrain.ai` | Via CF Tunnel | Same |
| Wildcard `*.purebrain.ai` | Via CF Tunnel | Same |

**SSL recommendation**: Set Cloudflare SSL/TLS to **Full (Strict)** mode. This encrypts both the browser-to-Cloudflare connection and the Cloudflare-to-origin connection. If WordPress already has a valid SSL cert (likely from Let's Encrypt or CF Origin cert), this is safe.

### Cloudflare Tunnel

**Tunnel ID**: `fa55839c-e753-4a96-935c-cc58cf24b4b8`

The tunnel runs as a service on server `89.167.19.20`. It must be running for all subdomains to work:
- `api.purebrain.ai` → localhost:8443 (PureBrain API / log server)
- `portal.purebrain.ai` → localhost:8099 (admin portal)
- `cc.purebrain.ai` → localhost:8870 (command center)
- `video.purebrain.ai` → localhost:8765
- `*.purebrain.ai` → localhost:8099 (customer portals)

**To check tunnel health:**
```bash
# On the server:
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -n 50

# Or check DNS resolves and tunnel responds:
curl -I https://api.purebrain.ai
```

**If tunnel is down:**
```bash
sudo systemctl restart cloudflared
```

### Cloudflare WAF / Firewall Rules

The security plugin previously managed some WAF behavior via WP. Review current CF WAF rules in the dashboard:
- CF Dashboard → Security → WAF
- Ensure no rules are blocking the WP admin at `/wp-admin/` from your IP
- Ensure no rules are blocking the REST API at `/wp-json/`

### WordPress REST API (Critical for Aether)

Aether deploys everything via WP REST API. Verify it is accessible:
```bash
curl -s https://purebrain.ai/wp-json/wp/v2/ | python3 -m json.tool | head -5
```
Should return JSON. If it returns 403 or an empty response, the WAF or security plugin is blocking it.

### Email — WordPress Transactional (WP-Mail)

WordPress sends transactional emails (password reset, new user, WooCommerce if present) via its built-in mail function. These likely use SMTP via Brevo.

**Check**: Is the WP SMTP plugin (e.g., WP Mail SMTP or FluentSMTP) configured with Brevo credentials?
- WP Admin → Plugins → confirm SMTP plugin is active
- WP Admin → SMTP plugin settings → confirm Brevo host/API key is set

### Google Workspace / Gmail

- Email `jared@puretechnology.nyc` works via Google Workspace
- Aether's email `purebrain@puremarketing.ai` works via Gmail/Google Workspace
- Verify MX records in Cloudflare DNS still point to Google:
  - CF Dashboard → DNS → filter by MX records
  - Should show `aspmx.l.google.com` and similar Google MX entries

### Independent Analytics (WP Plugin)

The exported HTML references `iawp-click-endpoint.php` which is a WordPress plugin endpoint. This only works when WordPress is the actual server. On the CF Pages staging site this will 404, but that is acceptable for staging.

For production: ensure the WP plugin remains active and accessible at `https://purebrain.ai/wp-content/plugins/independent-analytics/`.

### Netlify (Secondary Static Deployments)

Some exports use Netlify (`.netlify/netlify.toml` exists). Check which projects still deploy there vs which have moved to CF Pages.

### Cloudflare R2 (Video Storage)

Videos are served from `video.purebrain.ai` which routes through the CF Tunnel to a local video server on port 8765. Large MP4 files (86MB, 71MB) are stored in R2.

**Check**: `curl -I https://video.purebrain.ai` — should get a 200 or redirect, not a 522.

---

## Deployment Reference — How Aether Deploys to CF Pages

For IT records, here is the exact command currently used:

```bash
# Standard deploy command (run from aether project root)
CLOUDFLARE_ACCOUNT_ID=d526a3e9498dd167509003004df03290 \
CLOUDFLARE_API_TOKEN=$CF_PAGES_TOKEN \
npx wrangler pages deploy /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/ \
  --project-name=purebrain-staging \
  --branch=main \
  --commit-dirty=true
```

**To add a new team member's API token for deploying:**
1. Create token per Topic 1 instructions
2. Replace `$CF_PAGES_TOKEN` with their token
3. Scope their token to `Cloudflare Pages > Edit` only

---

## Outstanding Action Items (Priority Order)

1. **Verify GA4 measurement ID** — confirm which `G-XXXXXXXXXX` is the live ID and ensure it is embedded in WordPress plugin head injection so all future page exports include it
2. **Verify GSC ownership** — log into Search Console, confirm `purebrain.ai` is verified. If not, add DNS TXT record in Cloudflare
3. **Submit sitemap to GSC** — submit `https://purebrain.ai/sitemap_index.xml`
4. **Audit API tokens** — in CF dashboard, review all tokens. Name each one. Revoke unused ones.
5. **Create `robots.txt`** in `exports/cf-pages-deploy/` and redeploy
6. **Verify Brevo DKIM/SPF** — in Cloudflare DNS, confirm Brevo authentication records exist
7. **Confirm Cloudflare Tunnel is running** — `systemctl status cloudflared` on server 89.167.19.20
8. **SSL/TLS mode check** — set to Full (Strict) if not already
9. **DNS flip decision** — decide if/when `purebrain.ai` custom domain gets added to the CF Pages project for full Pages production routing

---

## Memory Written

Path: `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/dept-it-support/2026-03-12--cloudflare-management-guide.md`
Type: synthesis
Topic: purebrain.ai Cloudflare Pages architecture, team access, SEO, analytics, reconnection checklist
