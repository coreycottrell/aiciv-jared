# PureBrain Metrics Dashboard — 2026-04-28 20:38 UTC

## Funnel (last 7 days)
| Stage | Count | Notes |
|---|---|---|
| Web sessions (consented) | **771** | unique session IDs accepting ToS |
| Conversation events | 994 | full event stream |
| Seeds sent | **6** | real birth pipeline |
| Payments verified | **6** | **$1,099.50** |

Conversion: 771 → 6 = **0.78%** sessions-to-paid. Clean 1:1 seeds-to-payments (no leak in the pipeline).

## Payments
- **Total ever**: 66
- **Last 24h**: 1 ($74.50, Awakened, Matthew Keough)
- **Last 7d**: 6 ($1,099.50)
- **Last 30d**: 28 ($3,124.50), all verified
- **Tier mix (30d)**: Awakened 21 · Partnered 6 · Unified 1

## Web Engagement (24h)
- 198 events across 139 unique sessions
- 139 consent acceptances · 45 message exchanges · 6 conversation starts · 4 conversation completions · 4 capabilities reveals

## Onboarding (Seed Pipeline)
- **30d**: 21 seeds sent → 12 real / 9 sandbox tests
- Recent real names: Nova, Nexus, Vira, Spark
- 24h: 1 seed (Nexus, sandbox)

## Birth Completions
- 10 lifetime · 0 in last 7d (gap to investigate — payments arriving but birth completion event not firing)

## Health Signals
- 🟢 Payment pipeline: clean (6/6 verified, seeds match payments 1:1)
- 🟢 Consent capture: 139/24h, healthy top-of-funnel
- 🟡 Conversation completion rate: 4/6 starts complete in 24h (66% — watch)
- 🔴 **Birth completion gap**: 12 real seeds in 30d but 0 completion events in 7d → birth_completions.jsonl writer may have stopped
