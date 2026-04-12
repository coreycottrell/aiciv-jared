# Brainiac Module 1 & 2 HLS Live + Training Page Restored

**Date**: 2026-03-12
**Agent**: dept-systems-technology
**Tags**: brainiac, hls, r2, cloudflare-stream, training-page, video

## What Happened

Task requested uploading Module 1 MP4 (332MB) to Cloudflare Stream. Investigation revealed:

### Cloudflare Stream Status
- Cloudflare Stream is NOT enabled on either CF account
- Account 1 (d526a3e9498dd167509003004df03290): Images Basic, R2 Paid, Teams Free, SSL for SaaS
- Account 2 (19bb52a20bc7fc1b34036fea91f6860c): R2 Paid only
- Stream requires separate paid add-on at dash.cloudflare.com -> Stream
- Auth error code 10002 = "Authorization Failure" = feature not subscribed

### Videos Already Transcoded + Uploaded to R2
Both modules were ALREADY fully in R2 on account 2, purebrain-video bucket:

**Module 1** (`brainiac/recordings/module-1/`):
- HLS URL: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/brainiac/recordings/module-1/master.m3u8`
- Poster: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/brainiac/recordings/module-1/poster.jpg`
- Segments: 159 x ~10s (VOD playlist)
- Duration: 26m 30s
- Status: HTTP 200 OK

**Module 2** (`brainiac/recordings/module-2/`):
- HLS URL: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/brainiac/recordings/module-2/master.m3u8`
- Poster: NONE (404) - needs extraction or placeholder
- Segments: 107 (LIVE_ENDED playlist, target duration 19s)
- Duration: 17m 47s
- Status: HTTP 200 OK

### Training Page Fix
The `TRAINING_VIDEOS` array in `exports/cf-pages-deploy/brainiac-mastermind-training/index.html` had a comment:
`/* Module 1 & 2 video cards removed — will be re-added once R2 uploads complete */`

Added both video cards back with status: "live" and correct HLS URLs.
Deployed via: `CLOUDFLARE_API_TOKEN=[CF_PAGES_TOKEN] npx wrangler pages deploy exports/cf-pages-deploy/ --project-name purebrain-staging --branch main`

### Files
- Stream info JSON: `exports/brainiac-training/module-1-stream-info.json`
- Training page: `exports/cf-pages-deploy/brainiac-mastermind-training/index.html`
- Deployed preview: `https://3e4860ab.purebrain-staging.pages.dev`

## Key Learnings

1. **CF Global API Key auth pattern**: Use `X-Auth-Email` + `X-Auth-Key` headers (NOT Bearer). Key works for accounts list but NOT Stream (not subscribed).
2. **CF Stream needs subscription**: Error code 10002 from Stream API = feature not enabled. Need to subscribe first.
3. **CF Pages token**: `CF_PAGES_TOKEN` env var works for wrangler deploys via `CLOUDFLARE_API_TOKEN`.
4. **Two CF accounts**: Account 1 (In0v8/d526a3e...) and Account 2 (Jared/19bb52a...). Video R2 is on account 2.
5. **WP REST API blocked**: purebrain.ai WP REST API intercepted by CF Pages - returns homepage HTML not JSON.
6. **R2 public URL**: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/` is the public CDN for purebrain-video bucket on account 2.
7. **Module 2 poster missing**: No poster.jpg for module-2 in R2. Can be added by extracting first frame from MP4.

## Action Items Remaining
- Module 2 poster: Extract a frame from the 604MB MP4 at `exports/brainiac-training/downloads/2026-03-11/`
- If true Cloudflare Stream ABR is needed: subscribe at dash.cloudflare.com
