# CTO Report: Cloudflare Pricing + R2 Video Pipeline Status

**Agent**: cto
**Domain**: Technology Strategy & Vision
**Date**: 2026-03-12

---

## TASK 1: Cloudflare Pro Plan & Load Balancing Pricing

### Summary Verdict

**Do NOT upgrade to Cloudflare Pro for load balancing on a single VPS.** Load balancing is a paid add-on at every tier — Pro does not include it. For a single-origin setup, the product doesn't do what you'd expect.

---

### Cloudflare Pro Plan: $20/month

What you get beyond Free:
- Web Application Firewall (WAF) — 100+ managed rules
- Advanced DDoS mitigation
- Image optimization (Polish, Mirage)
- 50 Page Rules (vs 3 on Free)
- HTTP/2 & HTTP/3 prioritization
- Mobile redirect
- Priority support
- Faster analytics (24hr data retention → 7 days)

**Load balancing: NOT included in Pro.** It's a separate add-on at every plan tier.

---

### Cloudflare Load Balancing: Separate Add-On Pricing

| Feature | Base ($5/mo) | Notes |
|---------|-------------|-------|
| Origins | 2 origins | Basic pool |
| Health check frequency | 60 seconds | Slowest option |
| Health check regions | 1 region | Single-point checks |
| Geo-routing | Not included | Flat +$10/mo |
| DNS queries | First 500k free | $0.50/500k after |

Add-on costs on top of base $5:

| Upgrade | Cost |
|---------|------|
| +4 origins (6 total) | +$15/mo |
| +30s health check intervals | +$10/mo |
| +4 health check regions | +$10/mo |
| Geo-routing | +$10/mo |

**Realistic minimum for multi-origin use**: $5–$35/month depending on config.

---

### Our Use Case Analysis: Single VPS for purebrain.ai

**Situation**: One VPS. One origin. Cloudflare free plan already in use.

**Conclusion: Cloudflare Load Balancing is not the right tool.**

Load balancing solves one problem: routing traffic across multiple origins with health-check failover. If we have one VPS, there is nothing to balance traffic between. The product would cost $5–15/month for a health check that pings a single server and... does nothing.

**What Pro DOES give us that has real value for purebrain.ai:**
- WAF with managed rules (worth it if we're getting bot traffic or need PCI/compliance coverage)
- Page Rules (50 instead of 3 — we use these for redirects/rewrites)
- Image optimization (Polish compresses images automatically — real performance win)

**Recommendation**: Upgrade to Pro ($20/mo) only if we want WAF protection or more Page Rules. Not for load balancing.

---

### Alternatives to Load Balancing on a Single VPS

| Option | Cost | Notes |
|--------|------|-------|
| Cloudflare Health Checks (standalone) | Free on Pro | Monitors origin, alerts only — no traffic routing |
| CF Tunnel (Zero Trust) | Free tier available | Expose VPS without public IP — bonus: DDoS protection built in |
| Nginx upstream failover | $0 | Software-only, no cloud cost — if we ever add a second VPS |
| Hetzner or DO load balancer | $6–12/mo | Better value if we actually need multi-origin |

**Best move if VPS reliability is the concern**: Cloudflare Tunnel (Argo Tunnel) on Free/Pro hides our VPS IP and adds resiliency. Zero marginal cost.

---

## TASK 2: R2 Video Pipeline — Status Update

### What Was Asked

"Pull Module 1 & 2 from Zoom API, transcode → upload to R2 → update training page"

### Current State: BUILT BUT BLOCKED

The full pipeline was built TODAY (2026-03-12) by the systems technology team. Here is the exact status:

---

### What IS Done

**Pipeline file**: `tools/zoom_brainiac_pipeline.py`

Full 7-step automated pipeline:
1. Monitor Zoom for new Brainiac recordings
2. Download video + VTT transcript
3. Transcode to HLS via ffmpeg (using existing `tools/video-pipeline/transcode.sh`)
4. Upload HLS segments + poster to Cloudflare R2
5. Update the training page WordPress embed
6. Generate AI-optimized training summary from transcript
7. Create/update PureBrain fleet skill package

**Credentials in .env**: All R2 credentials present and confirmed.
- R2 bucket: `pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev`
- Zoom client ID + secret: present

**Training page**: Fully built at `purebrain.ai/brainiac-mastermind-training/`
- Password gate: working (`brainiac2026`)
- HLS.js 1.5.7 video modal: working
- Module 01 and Module 02 cards: LIVE NOW badges showing
- Video library: one live video (Portal Demo), all others "coming soon"
- Page wired to accept new R2 URLs — just flip `status: 'coming_soon'` → `status: 'live'` and add HLS/poster URLs

---

### What IS Blocked

**Single blocker: Zoom OAuth scope.**

The Zoom OAuth app does NOT have the recording read scope. The API returns HTTP 400 with a scope error when trying to list recordings.

**Missing scopes**:
- `cloud_recording:read:list_user_recordings`
- `cloud_recording:read:list_user_recordings:admin`

**This requires Jared to take one manual action in a browser:**

1. Go to: https://marketplace.zoom.us/develop/apps
2. Find the OAuth app (client ID: `I9qZ8e1yQvuKkZ5rHmaYVg`)
3. Go to Scopes tab
4. Add both recording scopes above
5. Re-authorize (new OAuth flow) — new tokens save automatically to `.credentials/zoom_tokens.json`

After that one step, run:
```bash
python3 tools/zoom_api.py list         # Verify scope works
python3 tools/zoom_brainiac_pipeline.py --manual   # Run full pipeline
```

---

### After the Scope Fix: What Happens

The pipeline will:
1. Find the two most recent Brainiac Mastermind recordings in Zoom Cloud
2. Download them to temp directory
3. Transcode to HLS (requires `ffmpeg` installed on VPS — confirm with: `ffmpeg -version`)
4. Upload to R2 at `brainiac/recordings/YYYY-MM-DD/`
5. Update the training page with live video URLs
6. Generate summary JSON + markdown for each module
7. Update the fleet skill package

---

### ffmpeg Check

One soft dependency to verify on the VPS:
```bash
ffmpeg -version   # must exist for transcoding step
```

If not installed: `sudo apt install ffmpeg` (Ubuntu/Debian).

---

### Scheduling (Not Yet Configured)

Pipeline is designed to auto-run every Wednesday at 2:30pm ET. To activate, add to `.claude/scheduled-tasks-state.json`:

```json
{
  "id": "brainiac-zoom-pipeline",
  "schedule": "Wednesday 14:30 ET",
  "command": "python3 /home/jared/projects/AI-CIV/aether/tools/zoom_brainiac_pipeline.py",
  "retry_times": ["15:00", "15:30", "16:00"]
}
```

---

## Summary: Action Items for Jared

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 1 | **CF Pro**: Decide if WAF/Page Rules worth $20/mo. Skip LB add-on. | Jared decides | 5 min |
| 2 | **Zoom scope fix**: Add recording scopes to OAuth app at marketplace.zoom.us | Jared (browser) | 5 min |
| 3 | **ffmpeg check**: Confirm `ffmpeg -version` works on VPS | Aether or Jared | 1 min |
| 4 | After scope fix: run `--manual` pipeline to pull Module 1 & 2 | Aether (auto) | ~20 min unattended |

---

**Files Referenced**:
- `tools/zoom_brainiac_pipeline.py` — 7-step pipeline
- `tools/zoom_api.py` — Zoom API helper
- `tools/video-pipeline/transcode.sh` — HLS transcoder
- `tools/video-pipeline/upload_r2.py` — R2 uploader
- `exports/cf-pages-deploy/brainiac-mastermind-training/index.html` — Live training page
- `.env` — R2 + Zoom credentials

Sources:
- [Cloudflare Pro Plan](https://www.cloudflare.com/plans/pro/)
- [Cloudflare Load Balancing Docs](https://developers.cloudflare.com/load-balancing/)
- [CF Load Balancing Billing Docs](https://developers.cloudflare.com/support/account-management-billing/billing-cloudflare-add-on-services/billing-for-cloudflare-load-balancing/)
- [CF Load Balancing Pricing Community](https://community.cloudflare.com/t/please-elaborate-on-load-balancer-pricing/469042)
