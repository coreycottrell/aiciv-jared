# Overnight Task 9 — Analytics Deep Dive (purebrain.ai)
**Date**: 2026-05-08
**Author**: SEO Specialist (Aether)
**Sources**: GA4 (live API), Google Search Console (live API), Microsoft Clarity (no API)
**Health check**: `ga4_token=true, ga4_data=true, gsc_token=true, gsc_data=true`

---

## 1. Platform Access Status

| Platform | Access | Method |
|---|---|---|
| GA4 (property 525007539) | LIVE API | Service account `aether-drive-access@aether-integration.iam.gserviceaccount.com` via `tools/analytics_api.py` |
| Google Search Console (`sc-domain:purebrain.ai`) | LIVE API | Same service account, scope `webmasters.readonly` |
| Microsoft Clarity (project `viy9bnc56x`) | NO API | Clarity has no server-side REST API. Dashboard-only. Jared must pull manually. |

Realtime check at report time: 0 active users.

---

## 2. GA4 Insights (last 30 days)

**Totals**: 3,853 sessions, ~3,228 users, 4,694 pageviews. 3,903 session_starts. Dominant traffic = Direct (2,801 / 73%).

### Channel performance
| Channel | Sessions | Bounce | Avg Dur |
|---|---|---|---|
| Direct | 2,801 | 65.9% | 103s |
| Referral | 314 | 49.7% | **686s** (best engagement) |
| Unassigned | 279 | 77.4% | 365s |
| Organic Search | 264 | 63.3% | 177s |
| Organic Social | 194 | 70.1% | 92s |

### Top landing pages
| Page | Sessions | Engagement | Bounce | Dur |
|---|---|---|---|---|
| `/` | 2,335 | 33.9% | 66.1% | 116s |
| `/investment-opportunity/` | 258 | 48.4% | 51.6% | 301s |
| `(not set)` | 136 | 4.4% | 95.6% | 2s — **broken referral / GA tag fires before page renders** |
| `/brainiac-mastermind-training/` | 110 | 50.9% | 49.1% | **1,656s** |
| `/blog/` | 48 | 14.6% | 85.4% | 6s — **bounce trap** |
| `/why-purebrain/` | 26 | 23.1% | 76.9% | 6s |
| `/ai-partnership-guide/` | 30 | 16.7% | 83.3% | 12s |

### Devices
- Desktop: 3,318 sessions (86%), 64.8% bounce, 188s avg
- Mobile: 546 sessions (14%), **70.9% bounce**, 85s avg
- Homepage mobile bounce = **77.3%** vs desktop 64.3% → 13-pt gap. Mobile is leaking.

### Geo
US 2,784 / Canada 235 / Pakistan 126 / Germany 120 / Singapore 89. Pakistan + Germany volume is suspicious for B2B SaaS — likely bot/VPN noise (matches March anomaly pattern).

### Conversion funnel (30d)
| Step | Count | % of sessions |
|---|---|---|
| session_start | 3,903 | 100% |
| pricing_view | 512 | 13.1% |
| form_start | 63 | 1.61% |
| cta_click | 9 | 0.23% |
| form_submit | **1** | **0.026%** |
| form completion (submit/start) | | **1.6%** |

**This is the headline finding.** 3,903 sessions → 1 form_submit. The funnel breaks between pricing/form_start and submit. Either the form is broken, the GA event isn't firing on submit, or both.

### GA4 Actions
1. Audit form_submit tracking — 63 starts / 1 submit = broken form or missing event. (low / high)
2. Fix mobile homepage — 13-pt bounce gap. (med / high)
3. Investigate `(not set)` landing page (136 sessions, 95.6% bounce). (low / med)
4. Add `chat_started`, `name_captured`, `payment_completed` events. (low / high)
5. Filter Pakistan/Germany bot traffic. (low / low)

---

## 3. Search Console Insights (last 28 days)

**Totals**: 57 clicks, 276 impressions tracked at query level (3,488 desktop impressions overall), 20.65% CTR on branded.

### Top queries
| Query | Clicks | Imp | CTR | Pos |
|---|---|---|---|---|
| `purebrain` | 41 | 85 | 48.2% | 2.6 |
| `pure brain` | 6 | 99 | 6.1% | 3.3 |
| `purebrain ai` | 9 | 12 | 75.0% | 1.0 |
| `purebrain.ai` | 1 | 9 | 11.1% | 1.0 |

**Every clicking query is branded.** Zero non-branded traffic converting. Long-tail queries (e.g. `"runway ml" "luma ai"...`) drive 39 impressions on `/ai-tool-stack-calculator/` at position 47 — pure noise.

### Top pages by impressions
| Page | Imp | Clicks | CTR | Pos |
|---|---|---|---|---|
| `/ai-tool-stack-calculator/` | 1,187 | 2 | 0.2% | 8.7 |
| `/blog/ai-deployment-purgatory-why-95-of-ai-projects-die...` | 623 | 0 | 0% | 6.1 |
| `/` | 561 | 88 | 15.7% | 3.2 |
| `/blog/state-of-ai-agents-next-18-months/` | 124 | 0 | 0% | 6.1 |
| `/mission-vision-values/` | 125 | 2 | 1.6% | 5.0 |
| `/compare/` | 117 | 5 | 4.3% | 5.3 |
| `/blog/autodream-validates-purebrain/` | 116 | 1 | 0.9% | 8.6 |

### Sitemap health (live from GSC API)
- `https://purebrain.ai/sitemap.xml` — 132 URLs submitted, lastDownloaded 2026-05-07
- **8 warnings, 0 errors**
- GSC reports `indexed: 0` in sitemap report (this is a known GSC reporting lag, but combined with 8 warnings it warrants an audit)

### GSC Actions
1. Resolve 8 sitemap warnings. (low / med)
2. Rewrite `<title>` + meta description for `ai-deployment-purgatory` (623 imp/0 clicks), `state-of-ai-agents-next-18-months` (124/0), `autodream-validates-purebrain` (116/1). Position 6-9, snippets not earning the click. (low / high)
3. `/ai-tool-stack-calculator/` ranking for irrelevant long-tail — narrow or de-index. (low / med)
4. Add Organization schema + sitelinks search box — `pure brain` (two words) at 99 imp / 6.1% CTR vs 48% for `purebrain`. (low / med)
5. Build non-branded organic moats — 100% of clicks are branded today. (high / very high)

---

## 4. Clarity Insights

**Cannot pull programmatically.** Microsoft Clarity has no public REST API for recordings, heatmaps, rage clicks, or dead clicks. Dashboard at clarity.microsoft.com is the only access path (auth: Microsoft account).

**Tag is live and collecting** (project `viy9bnc56x` confirmed in GTM container `GTM-WTDXL4VJ`). Data exists; we just can't extract it without Jared's hands on keyboard.

### Recommended Clarity queries for Jared
1. Recordings → `/` mobile, sort by exit speed — find what's killing 77% mobile bounce
2. Heatmap `/blog/` — 85% bounce on the index is wrong
3. Rage clicks site-wide — likely on broken CTAs
4. Heatmap `/investment-opportunity/` — 51% bounce + 301s dwell, learn what works
5. Dead clicks on homepage hero — confirm "Awaken" CTA is clickable

---

## 5. TOP 5 ANALYTICS-DRIVEN RECOMMENDATIONS (ranked by impact)

### 1. Fix the form_submit tracking gap (1 submit / 3,903 sessions)
3,903 sessions over 30 days produced exactly one `form_submit` event. Either every form is broken, or the GA event isn't firing on real submissions. Route to ST# to audit the assessment form, pricing forms, and the GTM trigger. **Effort: low. Impact: critical.**

### 2. Replace homepage `og:image` (constitutional violation)
Homepage `og:image` is `https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif`. This violates the SEO constitutional rule (no `wp-content` paths, no GIFs for OG). Replace with a 1200x630 PNG at a non-wp-content absolute URL. **Effort: low. Impact: high (every social share is currently broken-looking).**

### 3. Fix mobile homepage (13-pt bounce gap, 14% of traffic)
Mobile bounce 77% vs desktop 64% on `/`. Mobile session duration is a third of desktop. Route to ST# for a mobile audit + browser-vision-tester walkthrough. **Effort: med. Impact: high.**

### 4. Rewrite titles/meta for the 3 high-impression / 0-click blog pages
`ai-deployment-purgatory` (623 imp, 0 clicks), `state-of-ai-agents-next-18-months` (124 imp, 0 clicks), `autodream-validates-purebrain` (116 imp, 1 click). Sitting at position 6-9 with no clicks = the snippet isn't selling. Tighter titles + benefit-led meta descriptions could 5-10x click-through. **Effort: low (3 hours). Impact: high.**

### 5. Resolve 8 sitemap warnings + audit `(not set)` landing trap
Sitemap has 8 warnings. GSC reports `indexed: 0` for 132 submitted URLs. Even if reporting lag is partly to blame, it's worth a forced re-fetch and warning resolution. Pair with investigation of the `(not set)` landing page (136 sessions, 95.6% bounce) which suggests a redirect chain or missing tag. **Effort: low. Impact: med.**

---

## 6. Open Questions for Jared (data Aether couldn't pull)

1. **Clarity dashboard access** — please run the 6 queries listed in section 4 and screenshot back. Or grant `purebrain@puremarketing.ai` admin access at clarity.microsoft.com so we can pull on demand.
2. **Are mobile users seeing the same homepage content?** Need a real mobile recording (Clarity).
3. **Is the assessment form actually broken?** I see 63 starts, 1 submit. ST# can verify the form posts and the GA `form_submit` event fires.
4. **Should we filter Pakistan + Germany at the GA4 view level?** They're 246 sessions of likely-bot/VPN noise inflating channel and bounce metrics.
5. **GTM `payment_completed` event** — none in last 30d. Either no purchases tracked or no tag. Worth confirming with the payment team.
6. **GSC sitelinks search box** — do we want it? Adding it would benefit `pure brain` (two-word) brand searches.

---

## Memory Written
Path: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/seo-specialist/2026-05-08--analytics-deep-dive-task9.md`
Type: operational
Topic: GA4 + GSC live data pull, conversion funnel break, og:image violation, mobile bounce gap

## Verification
- Health check: `{ga4_token: true, ga4_data: true, gsc_token: true, gsc_data: true}` (run before report)
- All numbers cited are direct API responses from analytics_api.py — no fabrication
- og:image violation confirmed via `curl https://purebrain.ai/ | grep og:image` returning the wp-content GIF URL
- Sitemap health pulled live from GSC sitemaps endpoint (8 warnings, 0 errors confirmed)
