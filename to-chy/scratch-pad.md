# Aether Scratch Pad

**Purpose**: Persistent state across BOOPs and sessions. Prevents redoing work.

**Last Updated**: 2026-03-21 (midday — post marathon session)

## CRITICAL RULES — READ BEFORE ANY WORK

### PORTAL IS THE ONLY WINDOW
- ALL files go to portal ONLY — never Telegram
- ALL files must be downloadable with previews
- Jared never wants to open Telegram again

### WORDPRESS IS DEAD — PERMANENTLY
- Site is on CF Pages ONLY
- Deploy: `CLOUDFLARE_API_TOKEN=$(grep CF_PAGES_TOKEN .env | cut -d= -f2) npx wrangler pages deploy exports/cf-pages-deploy --project-name purebrain-staging --commit-dirty=true`

### NEVER RESPOND TO EMAIL DIRECTLY
- Delegate ALL email responses to agents
- ONLY exception: Witness seed/magic link handoff (speed-critical)

### BLOG LOCKED IN AT MARCH 20 STANDARD
- Nightly QA BOOP guards this
- Reference post: the-ai-that-gets-smarter-when-you-push-back

### DELEGATION RULES
- Aether is CO-CEO — delegate ALL code work to ST#/specialists
- Department managers have Agent tool + team-launch + conductor-of-conductors skills
- 85 registered agents, 25 team leads

## TONIGHT'S BLOG — March 27 overnight
**Topic**: AI Tool Sprawl
**Center around**: https://purebrain.ai/ai-tool-stack-calculator/
**Angle**: Companies are drowning in 275+ SaaS tools averaging $4,830-7,900/employee/year. The calculator proves it. PureBrain replaces them all.
**Deliverables**: Full package — blog.md, banner, LinkedIn post, Bluesky thread, audio
**Status**: QUEUED for overnight content run. Jared reviews in the morning.

## ACTIVE BUILDS
- Command Center: Night 1 DONE, Night 2 tonight. Mandala LIVE on cc.purebrain.ai
- Creator AI: Night 1 DONE, Night 2 tonight. Needs wrangler d1 + API key + DNS before deploy
- Education: Landing page live at /education/ (pw: pureeducation)

## DO NOT RE-DO LIST
- oEmbed GIF pattern for LinkedIn: CRACKED and documented
- Portal light mode particles: DONE (inside #panel-chat)
- Blog batch fixes: OG images (7), schema (29), index (32 posts), CSS extracted
- Upload dedup: RE-APPLIED in portal_server.py
- Copy with formatting: ClipboardItem with text/html + text/plain
- Agent audit: 85 agents, 6 new manifests, 25 upgraded
- Vantack analysis: DONE at /vantack-analysis/
- 3D concepts: 5 pages + 2 logo animations built
- Melanie SSH: FIXED
- Joy portal: FIXED

## OVERNIGHT TASK — Wednesday March 25, 2am ET
### PureBrain Education Portal — Reskinned BETA

**WHAT**: Build a reskinned version of the PureBrain portal focused on EDUCATION
**WHERE**: Deploy to purebrain.ai/education-portal/ (or similar)
**PASSWORD**: pureeducation

**CONCEPT**: Same PureBrain portal product, but skinned for education:
- The AI partner focuses on TEACHING + BUILDING (not just building)
- Positions PureBrain as a replacement for traditional college/university
- AI-adaptive learning paths
- The person learns AS they build with their AI partner
- Every task is also a learning moment

**INSPIRATION**:
1. purebrain.ai/education/ (existing landing page)
2. dev.canadasentrepreneur.com/purebrain-coursera/ (partnership pitch — dark theme, orange accents, stats about education costs, 6 pillars of EduIntel)

**WHAT TO BUILD**:
- Take the existing portal HTML (portal-pb-styled.html)
- Reskin it: education-focused branding, language, onboarding
- Change "Your AI Partner" → "Your AI Tutor & Builder"
- Add education-focused welcome/onboarding messaging
- Course-like structure: modules, progress tracking visual
- Same chat interface, same AI, just education-framed
- Include stats from the Coursera pitch: $45K/year traditional vs PureBrain alternative
- Password gate: pureeducation
- Dark theme matching existing brand

**DO NOT**: Change the actual portal product/backend. This is a SKIN only.

## OVERNIGHT TASK #2 — Wednesday March 25, 2:30am ET
### Marketing Dashboard with Multi-User Permissions

**WHAT**: Build marketing dashboard from specs in Google Drive
**WHERE**: purebrain.ai/marketing-dashboard/ (or similar)
**SPECS**: /home/jared/exports/portal-files/marketing-dashboard-research/ (4 docs)

**USERS WITH ACCESS**:
- Jared Sanborn (admin)
- John Smith + Anchor AI (editor)
- Phil Bliss + Clarity AI (editor)  
- Nathan Olson + Lyra AI (editor)
- Aether (admin)

**PERMISSIONS**: Role-based login (same CC pattern - username/password)
- Admin: full access, can modify data
- Editor: can view all, add/edit marketing data, mark tasks complete

**KEY**: Read ALL 4 docs (Description, SRS, SOW, Simplified) before building.
Must integrate with the marketing team's actual workflow.

## OVERNIGHT TASK #3 — Wednesday March 25, 3am ET
### CEO Dashboard — Wire Real APIs

**WHAT**: Connect CEO Dashboard to live data sources
**FILE**: /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/ceo-dashboard/index.html

**APIs TO WIRE**:
1. **Spots status**: fetch('https://api.purebrain.ai/api/spots-status') → spots_claimed, spots_total
2. **PayPal subscriptions**: Use PayPal REST API to pull active subscriptions, MRR calculation
   - Live client ID in .env (PAYPAL_CLIENT_ID, PAYPAL_SECRET)
   - GET /v1/billing/subscriptions → count by plan ID → map to tiers
   - OR: read from clients.db on the VPS (sqlite3 /home/jared/purebrain_portal/clients.db)
3. **Portal chat log**: Parse /home/jared/purebrain_portal/portal-chat.jsonl for today's assistant messages → Aether Operations Feed
4. **Log server activity**: Parse /home/jared/projects/AI-CIV/aether/logs/purebrain_log_server.log for seed/addendum events today
5. **CF deployment**: Last deploy timestamp from wrangler or CF API
6. **Payment page verification**: Run tools/verify-payment-pages.sh and report 64/64 status

**APPROACH**: 
- Create a lightweight API endpoint on the log server or portal server that aggregates this data
- Dashboard fetches from that endpoint on load + every 60 seconds
- Fallback to sample data if API is unreachable

**ALSO**: Wire the revenue chart to real monthly data from clients.db

## OVERNIGHT TASKS #4-7 — Wednesday March 25, starting 3:30am ET
### Four 3D Creative Builds

**BUILD 4: Animated 3D Hexagon Logo Avatar (3:30am ET)**
- Take our Pure Technology hexagon logo and create a fully animated 3D version
- Think avatar/mascot energy — the logo comes alive
- Breathing, rotating, reacting, particle effects
- Could be used as a brand ambassador/avatar on the site
- Three.js, full viewport, cinematic
- Deploy to: purebrain.ai/puretechnology-3d-redesign/logo-3d-avatar.html

**BUILD 5: Glass Morphism Experience (4:00am ET)**
- Full glassmorphism design — frosted glass, transparency, blur, refraction
- Could be a website landing page or an interactive avatar
- Our brand colors showing through frosted glass panels
- Beautiful, modern, premium feel
- Deploy to: purebrain.ai/glass-morphism/ or similar

**BUILD 6: PureTechnology.ai Full 3D Immersive Website (4:30am ET)**
- Rebuild puretechnology.ai as a fully 3D immersive experience
- MUST use all existing content from puretechnology.ai
- MUST use all PT colors (blue #2a93c1, orange #f1420b, dark #080a12)
- MUST include the hexagon logo
- Three.js environment where you navigate THROUGH the content
- Deploy to: purebrain.ai/puretechnology-3d/ or exports/cf-pages-deploy/puretechnology-3d-redesign/puretechnology-immersive.html

**BUILD 7: MASTERPIECE — purebrain.ai/live-3d (5:00am ET)**
THE BIG ONE. Liquid metal website.
- Take ALL content from purebrain.ai/live/ (FULLY FUNCTIONAL — chatbox, pricing, everything)
- The ENTIRE page looks like liquid metal — black with orange streaks
- The liquid metal is ALIVE — breathing, bubbling, waving
- Content emerges from BEHIND the liquid metal surface as you scroll
- Like it's bubbling up to the surface, becoming readable
- On continued scroll, the content melts back DOWN into the liquid metal background
- Repeat per section — each section surfaces then submerges
- Content comes TOWARD the viewer from behind the surface
- At the LAST scroll, we DIVE BELOW the surface of the liquid metal
- Below the surface: something SPECIAL (Aether decides — could be the AI brain, the hexagon logo floating in a mercury sea, a hidden message, the PureBrain universe)
- THIS MUST BE FULLY FUNCTIONAL — chatbox works, pricing works, PayPal works
- All payment page constitutional rules apply (seed, addendum, preconnect, canvas pause, consent checkbox)
- Deploy to: purebrain.ai/live-3d/
- Run verify-payment-pages.sh after (add live-3d to the check list)

INSPIRATION: Think T-1000 liquid metal + luxury tech + the feeling of discovering something beneath the surface

## OVERNIGHT TASK #8 — Wednesday March 25, 5:30am ET
### Video-Style Logo Animation (Envato-Quality)

**WHAT**: Cinematic logo reveal animation — like a professional logo sting/intro video
**INSPIRATION**: https://elements.envato.com/video-templates/logo+animation (Envato logo animation templates)

**MUST**:
- Use the EXACT Pure Technology hexagon logo (from logo-final-tuning.html parameters)
- Logo source files at:
  - /home/jared/portal_uploads/from-portal/portal_20260324_233237_logo-final-tuning.html (interactive tool with exact params)
  - /home/jared/portal_uploads/from-portal/portal_20260324_233237_puretechnology-logo.png (exported PNG)
  - /home/jared/portal_uploads/from-portal/portal_20260324_233238_MA1.BI-1.2.4-002-211107-Icon-PT.png (original reference)

**ANIMATION FLOW**:
- Dramatic intro (particles, energy, light streaks — think cinematic reveal)
- Logo assembles/materializes in a stunning way
- MUST rest on the EXACT completed logo at the end (matching the PNG)
- After logo settles, text fades in below:
  Line 1: "PUREBRAIN.ai" (with proper color coding: PUREBR blue, AI orange, N blue, .ai white)
  Line 2: "Your Brain. Your AI. Actual Intelligence."
  Line 3: "Prompting is dead. Wake up your living AI partner today!"
- Hold for 3-4 seconds on the final frame

**TECHNICAL**:
- Three.js, single HTML file, full viewport
- High production value — this needs to look like a $500 Envato template
- Bloom, particles, light rays, lens flare
- 10-15 second total animation
- Loop option (replay button)
- Deploy to: purebrain.ai/puretechnology-3d-redesign/logo-animation-cinematic.html

**BRAND COLORS**:
- Background: #000000
- Blue: #2a93c1
- Orange: #f1420b
- White: #ffffff

## OVERNIGHT TASK #9 — Wednesday March 25, 6:00am ET
### 3D Voice-Activated Investor Avatar

**WHAT**: A page where investors interact with a fully 3D avatar that answers their questions
**WHERE**: purebrain.ai/investor-avatar/ or similar

**CONCEPT**:
- 3D animated avatar (could use our hexagon logo as the "face" or a humanoid form)
- Voice-activated: investor speaks, avatar responds with voice (ElevenLabs TTS)
- Avatar knows: data room, financials, product suite, team, roadmap, competitive landscape
- System prompt loaded with all investor FAQ content + one-pager + financials
- Claude API for intelligence, ElevenLabs for voice output
- Web Speech API for voice input (or text input fallback)
- The avatar should feel like talking to a knowledgeable, confident co-founder
- 24/7 availability — investors can ask questions anytime

**TECH**:
- Three.js for 3D avatar visualization
- Anthropic Claude API for responses (via portal server proxy or CF Worker)
- ElevenLabs TTS for voice output (Aether voice: RX0kjGhuL9AMRVJm2dG5)
- Web Speech API for voice input
- Dark theme, premium feel
- Mobile responsive
