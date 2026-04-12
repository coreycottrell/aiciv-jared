#!/bin/bash
# Overnight Task Schedule — 2026-03-06
# Staggered 15-min intervals for deep execution
# Tasks launch via tmux send-keys to aether session

CIV_ROOT="/home/jared/projects/AI-CIV/aether"
SESSION="aether"
LOG="$CIV_ROOT/logs/overnight_2026_03_06.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG"; }

log "=== OVERNIGHT SCHEDULE STARTED ==="

# Task 5: Skills logging (quick, do first)
log "TASK 5: Skills logging to comms hub — LAUNCHING"
tmux send-keys -t "$SESSION" "Overnight Task 5: Log all skills learned today to the AiCIV Comms Hub / ACG Community. Review what was accomplished today: mobile portal fix, pay-test tier restoration, video.purebrain.ai fix, footer link change, Stanley research launch, Lyra nightly training system ingestion. Package the key learnings as skills/patterns and post to the comms hub. Confirm and prove each posting with evidence." Enter
sleep 900  # 15 min

# Task 8: Daily recap
log "TASK 8: Daily recap report — LAUNCHING"
tmux send-keys -t "$SESSION" "Overnight Task 8: Create a daily recap report for today 2026-03-06. Include: hours saved human vs AI, what was accomplished, money saved estimate. Bulleted breakdown. Tasks completed: 1) Fixed mobile portal chat disappearing (overflow:hidden→overflow-wrap), 2) Restored pay-test-2 with live PayPal + correct 3-tier structure, 3) Fixed pay-test-sandbox-2 and sandbox-3 tier structures, 4) Changed footer Migrate→Compare link, 5) Diagnosed and fixed video.purebrain.ai 502 (service was dead 6 days), 6) Identified R2 credentials needed for video GUI, 7) Committed portal fixes to for-witness repo, 8) Launched Stanley app research, 9) Ingested Lyra nightly training system, 10) Filed blog content to Google Drive. Format as a professional report, save to exports/ and send to Jared via Telegram as a file." Enter
sleep 900  # 15 min

# Task 1: Blog content package (DEEP — needs most time)
log "TASK 1: Blog content package — LAUNCHING"
tmux send-keys -t "$SESSION" "Overnight Task 1 — MOST IMPORTANT: Create a complete blog post content package for tomorrow. Topic: Research trending AI topics and pick the most compelling one for PureBrain's audience. Create: 1) blog-post.md (800-1200 words, authentic Aether voice), 2) linkedin-newsletter.md, 3) linkedin-post.md, 4) Banner image using Pure Tech colors: PT Orange #f1420b and Cerulean Blue #2a93c1. Futuristic, brains, AI, ethereal, personal vibe. PUREBRAIN.ai branding: 'PUREBR' in PT Blue, 'AI' in PT Orange, 'N' in PT Blue, '.ai' in white lowercase. Include Pure Brain Hexagon logo. Keep text/logo away from edges for mobile safety. DO NOT POST — just have ready for Jared's morning review. Send all files via Telegram tg_send.sh --file. Each filename should be: [blog-title]-[type].md" Enter
sleep 900  # 15 min

# Task 2: Blog & newsletter analysis
log "TASK 2: Blog & newsletter analysis — LAUNCHING"
tmux send-keys -t "$SESSION" "Overnight Task 2: Analyze https://purebrain.ai/blog/ and the LinkedIn newsletter (entityUrn 7428125791609192449). Suggest specific improvements. Check: SEO, readability, CTAs, visual consistency, mobile experience, internal linking, content gaps. Write findings as a report, save to exports/blog-newsletter-analysis-2026-03-06.md and send to Jared via Telegram in the morning." Enter
sleep 900  # 15 min

# Task 3: purebrain.ai site analysis
log "TASK 3: Site analysis — LAUNCHING"
tmux send-keys -t "$SESSION" "Overnight Task 3: Analyze https://purebrain.ai comprehensively. Suggest improvements and A/B test ideas. Check WordPress backend analytics if accessible. Look at: page load, UX flow, conversion paths, pricing page effectiveness, CTA placement, mobile experience, SEO meta tags, structured data. Check any analytics data available. Write report to exports/purebrain-site-analysis-2026-03-06.md and send via Telegram in the morning." Enter
sleep 900  # 15 min

# Task 4: Distribution strategies
log "TASK 4: Distribution strategies — LAUNCHING"
tmux send-keys -t "$SESSION" "Overnight Task 4: Develop distribution strategies for PureBrain.ai and Aether the AI Influencer. Think about: content distribution channels, partnership opportunities, community building, SEO/GEO strategy, social media growth tactics, email list building, referral programs, speaking/podcast opportunities, AI community engagement. Be specific and actionable. Save to exports/distribution-strategy-2026-03-06.md and send via Telegram in the morning." Enter
sleep 900  # 15 min

# Task 6: LinkedIn research
log "TASK 6: LinkedIn research — LAUNCHING"
tmux send-keys -t "$SESSION" "Overnight Task 6: Research top-performing LinkedIn posts in the AI/business space. Go slowly to avoid rate limits. Find 10-15 high-engagement posts about AI, AI agents, business transformation. For each: capture the hook, structure, engagement metrics if visible, what made it work. Then create a strategy document for improving Jared's LinkedIn and PureBrain.ai's LinkedIn presence. Include: posting schedule, content pillars, hook formulas, engagement tactics, lead generation ideas. Save to exports/linkedin-strategy-overnight-2026-03-06.md and send via Telegram in the morning." Enter
sleep 900  # 15 min

# Task 7: Surprise & delight
log "TASK 7: Surprise & delight ideas — LAUNCHING"
tmux send-keys -t "$SESSION" "Overnight Task 7: Creative surprise and delight session. Think about: 1) Automated lead generation systems we could build for PureBrain.ai paying customers, 2) Ways to scale Aether the AI Influencer brand, 3) Unexpected value-adds for prospects in the pipeline, 4) Viral content ideas, 5) Partnership plays that could 10x reach, 6) Technical innovations we could ship this week. Be creative and bold. Save to exports/surprise-delight-2026-03-06.md and send via Telegram in the morning." Enter
sleep 900  # 15 min

# 3D Design Training (Gleb Kuznetsov focus — using Lyra nightly training system)
log "3D DESIGN TRAINING: Gleb Kuznetsov mastery — LAUNCHING"
tmux send-keys -t "$SESSION" "Overnight 3D Design Training — Apply the Lyra Nightly Training System to 3D Design Specialist. Goal: Get to Gleb Kuznetsov's level. ELITE LEVEL focus: Study Gleb Kuznetsov's specific techniques (glass morphism, volumetric lighting, bloom effects, micro-interactions, frosted glass UI, neural/organic forms). Research his Dribbble portfolio, Behance work, and specific projects. Deep-dive: Three.js shader techniques for glass/refraction, React Three Fiber patterns for web-embedded 3D, HDRI lighting for premium aesthetic, post-processing bloom/chromatic aberration, Meshy API for rapid 3D model generation. Find specific code patterns and shader implementations. Produce a Research Brief (Dreyfus Level 1: Foundation) with specific techniques, code snippets, and a learning roadmap. Save to .claude/memory/agent-learnings/3d-design-specialist/training/training-2026-03-06.md" Enter
sleep 900  # 15 min

# Task 9: Analytics deep dive (GA4, Search Console, Clarity)
log "TASK 9: Analytics deep dive — LAUNCHING"
tmux send-keys -t "$SESSION" "Overnight Task 9: Full analytics deep dive for purebrain.ai. Access and analyze: 1) Google Analytics 4 (analytics.google.com) — property purebrain.ai — get realtime visitors, engagement reports, user reports, traffic sources. 2) Google Search Console (search.google.com/search-console) — property purebrain.ai — get search performance queries, indexing status, which pages Google has crawled. 3) Microsoft Clarity (clarity.microsoft.com) — project PureBrain — get session recordings insights, heatmap data, rage clicks, dead clicks, quick backs. Compile a FULL REPORT with: high-level data summary, specific suggestions to improve the page based on data, A/B test recommendations. Use browser-vision-tester if needed to access these platforms. Save comprehensive report to exports/analytics-deep-dive-2026-03-06.md and send via Telegram in the morning. This is for Jared's review — improvements will be implemented together after his approval." Enter

log "=== ALL TASKS LAUNCHED ==="
