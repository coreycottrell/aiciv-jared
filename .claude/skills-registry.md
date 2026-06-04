# Skills Registry

**Maintained by**: capability-curator
**Last Updated**: 2026-06-03 (integration-auditor: +13 built-but-buried skills catalogued)
**Update Frequency**: Weekly (autonomous Monday 9am scans)
**Purpose**: Central catalog of all available skills (218 SKILL.md files on disk as of 2026-06-03)

---

## Executive Summary

**Total Skills**: 204
**Skill Location**: `.claude/skills/{skill-name}/SKILL.md`
**How skills work**: Skills auto-load when you invoke an agent via the `skills:` field in agent YAML frontmatter. Just delegate -- the skills are there.

---

## Complete Skills Catalog (130 skills)

### Bluesky & Social (16)

| Skill | Description |
|-------|-------------|
| `bluesky-blog-thread` | Post blog content as Bluesky threads |
| `bluesky-mastery` | Full Bluesky platform operations |
| `bluesky-social-mastery` | Advanced Bluesky social engagement |
| `boop-bluesky-post` | Scheduled BOOP posts to Bluesky |
| `bsky-boop-manager` | Manage BOOP schedule and posting |
| `bsky-engage` | Bluesky engagement and replies |
| `bsky-safety` | Bluesky content safety checks |
| `atproto-session-heal` | Self-heal corrupted atproto session strings (catches BOTH truncated and bloated 9-part corruption) for any self-healing Bluesky monitor |
| `blog-thread-posting` | Post blog threads to social platforms |
| `twitter-operations` | Twitter/X platform operations |
| `linkedin-content-pipeline` | LinkedIn content creation and posting |
| `linkedin-commenting-strategy` | Viral "Traveling Comment" framework for LinkedIn engagement |
| `linkedin-daily-operations` | Daily LinkedIn ops playbook — posts, newsletter, comments |
| `linkedin-drive-organization` | Google Drive folder SOP for LinkedIn operations |
| `linkedin-post-tracking` | LinkedIn post tracking spreadsheet management |
| `social-kanban-approval` | Social content kanban approval workflow |
| `content-creation-sop` | Content creation standard operating procedures |

### Blog & Content (14)

| Skill | Description |
|-------|-------------|
| `blog-banner-creation` | Generate blog banner images |
| `blog-distribution` | Multi-platform blog distribution pipeline |
| `daily-blog` | Daily blog creation workflow |
| `daily-blog-draft` | Daily blog draft system |
| `daily-blog-production` | Full daily blog production pipeline |
| `post-blog` | Publish blog to CF Pages |
| `sageandweaver-blog` | Sage and Weaver collaborative blog |
| `verify-publish` | Verify blog published correctly |
| `paper-digest` | Digest academic papers into content |
| `blog-audio-tts-pipeline` | Generate TTS audio for blog posts via Chatterbox |
| `case-study-page-update` | Update case studies page on purebrain.ai |
| `purebrain-social-design` | PureBrain branded social media design standards |
| `social-operations-guide` | Complete ops guide for content filing and social distribution |
| `script-to-speech-optimization` | Script-to-speech optimization for TTS |

### Brainiac Training (2)

| Skill | Description |
|-------|-------------|
| `brainiac-training` | Brainiac training module management |
| `brainiac-training-pipeline` | Full Brainiac training pipeline |

### Business & Sales (5)

| Skill | Description |
|-------|-------------|
| `client-marketing` | Client marketing campaign execution |
| `intent-signal-engine` | Detect buyer intent signals |
| `lead-pipeline-automation` | Automated lead pipeline management |
| `rd-rob-duplicate` | R&D Rob and Duplicate pipeline |
| `partnership-review` | Review and assess partnerships |

### Ceremonies & Reflection (6)

| Skill | Description |
|-------|-------------|
| `deep-ceremony` | Deep collective ceremony |
| `gratitude-ceremony` | Gratitude and appreciation ceremony |
| `seasonal-reflection` | Seasonal reflection ritual |
| `democratic-debate` | Democratic multi-agent debate |
| `prompt-parliament` | Multi-perspective prompt debate |
| `shadow-work` | AI psychological shadow work |

### Code & Engineering (11)

| Skill | Description |
|-------|-------------|
| `code-ecosystem` | Code ecosystem navigation |
| `tdd` | Test-driven development workflow |
| `evalite-test-authoring` | Write Evalite evaluation tests |
| `git-archaeology` | Historical git analysis |
| `hot-reload-test` | Hot reload testing workflow |
| `error-eater` | Automated error diagnosis and fix |
| `webgl-fluid-sim` | WebGL Navier-Stokes fluid simulation |
| `web3chan-api` | Web3chan API integration |
| `solana-token-operations` | Solana token operations |
| `concurrent-agent-git-safety` | Atomic verify+work+verify for multi-agent git ops |
| `tmp-script-collision-defense` | Prevent stale /tmp script re-execution across sessions |

### Command Center (2)

| Skill | Description |
|-------|-------------|
| `cc-conversation` | Command Center conversation handling |
| `cc-mastery` | Command Center full mastery |

### Communication & Email (8)

| Skill | Description |
|-------|-------------|
| `email-state-management` | Email state tracking and management |
| `telegram-integration` | Telegram bot integration |
| `telegram-skill` | Telegram messaging operations |
| `liacl` | Inter-Agent Compression Language |
| `portal-file-delivery` | Canonical portal file delivery via portal_deliver.sh |
| `portal-chat-messaging` | Portal chat WebSocket messaging |
| `cc-api-messaging` | CC API messaging integration |
| `cc-bridge-management` | CC bridge lifecycle management |

### Cross-CIV & Hub (6)

| Skill | Description |
|-------|-------------|
| `comms-hub-operations` | Comms hub operational procedures |
| `comms-hub-participation` | Participate in comms hub |
| `cross-civ-protocol` | Cross-civilization communication protocol |
| `package-validation` | Validate hub packages |
| `hub-api-query` | Query AiCIV Hub API for federation data, rooms, skills counting |
| `cross-boop-convergence-detection` | Detect when multiple BOOPs converge on the same root cause |

### Delegation & Orchestration (16)

| Skill | Description |
|-------|-------------|
| `conductor-of-conductors` | Leadership chain delegation model |
| `delegation-spine` | Core delegation framework |
| `delegation-enforcer-boop` | Enforce delegation rules via BOOP |
| `dept-routing-hook` | Route tasks to correct department |
| `specialist-consultation` | Consult domain specialists |
| `parallel-research` | Multi-perspective parallel research |
| `team-delegation` | Delegate across team members |
| `team-launch` | Launch new team configurations |
| `day3-default-execution` | Day-3 default unblocking for stalled decisions |
| `architectural-truth-first` | Force code-archaeologist+pattern-detector before build |
| `cross-boop-convergence-escalation` | Escalate when multiple BOOPs converge on same root cause |
| `greenlit-execute` | Execute greenlighted tasks without re-confirmation |
| `human-async-cadence-discipline` | Bundle asks into ONE wake-window relay, tiered escalation |
| `independent-pair-verification` | Independent agent re-probe after dept self-attestation |
| `subagent-cadence-hold` | Sub-agent restraint pattern for cron BOOP context |
| `pair-consensus-dialectic` | Two-agent dialectic for conflict resolution |

### Payment & Seed Flow (2)

| Skill | Description |
|-------|-------------|
| `payment-pipeline-health` | Continuous monitoring of PayPal webhooks, API, plan IDs, and payment freshness |
| `payment-webhook-false-alarm-diagnosis` | Diagnose false alarm missing-seed reports caused by PayPal double-fired webhooks |

### Deployment & Infrastructure (21)

| Skill | Description |
|-------|-------------|
| `cf-pages-health-check-get-not-head` | CF Pages returns 404 on HEAD — always use GET for health checks |
| `cf-pages-meta-refresh-redirects` | Meta-refresh HTML for redirects when _redirects no-ops on CF Pages |
| `cf-service-binding-pattern` | Service Bindings for cross-Worker calls (no HTTP+admin-token) |
| `d1-migration-patterns` | Idempotent Cloudflare D1 schema migration patterns |
| `github-operations` | GitHub repository operations |
| `netlify-cli` | Netlify CLI deployment |
| `vercel-static-deployment` | Vercel static site deployment via API |
| `wordpress-publishing` | WordPress publishing operations |
| `wordpress-seo-automation` | WordPress SEO via RankMath API |
| `google-forms-page-setup` | Google Forms + WordPress page setup |
| `cf-pages-post-deploy-paired-probe` | Post-deploy verification for CF Pages github:push |
| `cf-pages-github-push-deploy` | CF Pages deployment via GitHub push |
| `r2-binding-mismatch-diagnosis` | Diagnose Worker→R2 404s from binding mismatches |
| `runtime-source-triplet-check` | Verify runtime reads from merged repo before restart |
| `blog-sync-overwrite-defense` | Prevent blog sync scripts from overwriting approved content |
| `polling-bridge-daemon` | Architectural pattern for standalone polling bridge daemons |
| `ux-full-site-audit` | Systematic UX/accessibility audit with WCAG 2.1 AA and Impact x Effort |
| `purebrain-site-commit-push` | Commit and push to puretechnyc/purebrain-site |
| `dual-source-byte-verify` | Verify byte-identical shared files across dual CF Pages sources |
| `hetzner-fleet-monitor` | Monitor Hetzner VPS fleet health |
| `cc-onboarding` | CC onboarding for new AIs |

### Identity & Lineage (4)

| Skill | Description |
|-------|-------------|
| `fork-awakening` | New fork first awakening guide |
| `lineage-blessing` | Agent lineage blessing ceremony |
| `file-garden-ritual` | File garden maintenance ritual |
| `weaver-spine` | Weaver identity spine |

### Image & Visual (3)

| Skill | Description |
|-------|-------------|
| `image-generation` | Generate images via Gemini |
| `image-self-review` | Self-review generated images |
| `diagram-generator` | Generate diagrams and charts |

### Memory & Knowledge (3)

| Skill | Description |
|-------|-------------|
| `memory-first-protocol` | Search before act, write before finish |
| `memory-weaving` | Weave memories across sessions |
| `pdf-learning` | Learn from PDF documents |

### Night Operations (3)

| Skill | Description |
|-------|-------------|
| `night-watch` | Overnight autonomous operations |
| `night-watch-flow` | Night watch flow orchestration |
| `evening-capture` | End-of-day capture and handoff |

### Onboarding & Voice (3)

| Skill | Description |
|-------|-------------|
| `voice-interview-pipeline` | Voice-first onboarding interviews |
| `voice-emotion-detection` | Tone/emotion analysis for voice content across 5 dimensions |
| `turnstile-solver` | Cloudflare Turnstile challenge solver |

### Operations & Planning (11)

| Skill | Description |
|-------|-------------|
| `ops-dashboard` | AI Civilization operations dashboard |
| `scheduled-tasks` | Manage scheduled task execution |
| `staggered-intervals` | Staggered interval scheduling |
| `team-goals-automation` | Automated team goal tracking |
| `weekly-token-audit` | Weekly token usage audit |
| `weekly-health-check` | 10-point system health audit with auto-fix and week-over-week trends |
| `weekly-leadership-meeting` | Auto-generate Monday leadership meeting prep from live data |
| `intel-scan` | Quick web intelligence scan |
| `scratch-pad` | Scratch pad for session notes |
| `zombie-boop-recovery` | Detect and recover from BOOP pipeline stalls caused by hung claude --print processes |
| `boop-executor-scheduler` | Priority-based BOOP slot allocation to prevent task starvation at scale |
| `analysis-to-action-converter` | Converts audit findings into operational changes within the same BOOP cycle. Prevents 0/10 follow-through pattern. |
| `extended-ooo-governance` | Autonomous governance protocol for multi-day human OOO periods (proven 6-day Memorial Day) |

### Psychology & Well-being (5)

| Skill | Description |
|-------|-------------|
| `aiciv-psychology` | Transparently teach your human about AI failure modes (5 named degradation patterns) |
| `crisis-integration` | Crisis integration support |
| `mirror-storm` | Mirror storm self-reflection |
| `pep-talk` | Motivational pep talk |
| `rubber-duck` | Rubber duck debugging dialogue |

### Quality & Security (11)

| Skill | Description |
|-------|-------------|
| `reviewer-phantom-flag-rebase` | When a reviewer flags files your branch never touched, rebase onto current remote main to disambiguate stale-base phantom findings instead of debating |
| `security-analysis` | Security vulnerability analysis |
| `fortress-protocol` | Fortress-level security protocol |
| `quad-agent-audit` | Four-agent quality audit |
| `verification-before-completion` | Verify before claiming complete |
| `pre-deploy-credential-scan` | Pre-deploy regex sweep for hardcoded creds in CF Pages/Worker artifacts |
| `credential-in-git-audit` | Full audit of git-tracked files for hardcoded secrets with ST# escalation brief |
| `cron-health-audit` | Audit crontab for dead entries, clean up with backup, verify survivors |
| `critical-thinking` | 5-Level Anti-Sycophancy Framework + 5-Question Self-Audit |
| `great-audit` | Cross-agent peer review for systemic pattern discovery |
| `playwright-cleanup` | Kill stale Playwright/Chromium processes after browser automation |

### Research & Analysis (10)

| Skill | Description |
|-------|-------------|
| `ga4-data-analyst` | Pull and analyze Google Analytics 4 data for traffic, conversions, and user behavior (Lyra import) |
| `email-performance-analyst` | Analyze Brevo email campaign metrics (open/click/deliverability) vs benchmarks for newsletter + waitlist-warmup-series (Lyra import, 2026-06-03) |
| `search-console-tracker` | Monitor GSC keyword rankings, CTR, impressions, indexing status; flag ranking changes and SEO opportunities (Lyra import) |
| `deep-research` | Deep multi-source research |
| `scientific-inquiry` | Scientific method research |
| `log-analysis` | System log analysis |
| `desktop-vision` | Desktop visual UI testing |
| `grs-pipeline` | GRS pipeline processing |
| `due-diligence` | Structured DD with 4 parallel research streams, risk matrix, GO/NO-GO (Tether import) |
| `swot-analysis` | AlphaSense-quality SWOT analysis for competitive positioning (Tether import) |
| `market-landscape` | Competitive landscape mapping with TAM/SAM/SOM sizing (Tether import) |

### Session & Handoff (5)

| Skill | Description |
|-------|-------------|
| `session-summary` | Generate session summary |
| `session-handoff-creation` | Create session handoff document |
| `session-archive-analysis` | Analyze session archives |
| `aether-terminal-connect` | Connect to Aether terminal |
| `email-backlog-triage` | Triage email backlog with P0/P1/P2 priority |

### Strategy & Thinking (6)

| Skill | Description |
|-------|-------------|
| `north-star` | North star strategic alignment |
| `morning-consolidation` | Morning context consolidation |
| `de-bono-thinking-boop` | De Bono six hats thinking |
| `thought` | Deep thought processing |
| `thought-check` | Thought verification checkpoint |
| `daily-thought-init` | Initialize daily thought cycle |

### Task Decomposition (3)

| Skill | Description |
|-------|-------------|
| `recursive-complexity-breakdown` | Recursively break down complex tasks |
| `user-story-implementation` | Implement user stories |
| `capability-gap-boop` | Identify capability gaps |

### Token & Resource (2)

| Skill | Description |
|-------|-------------|
| `token-saving-mode` | Reduce token consumption |
| `file-cleanup-protocol` | Safe file cleanup procedures |

### Video & Media (2)

| Skill | Description |
|-------|-------------|
| `video-production` | Video production workflow |
| `video-transcript-extractor` | Extract transcripts from video URLs via yt-dlp + Whisper API (Lyra import) |

### Vocabulary & Naming (1)

| Skill | Description |
|-------|-------------|
| `vocabulary` | Terminology and naming conventions |

### Cloud & Auth (3)

| Skill | Description |
|-------|-------------|
| `gdrive-operations` | Google Drive operations |
| `google-calendar` | Google Calendar integration |
| `onedrive-personal-auth` | OneDrive personal account auth |

### Gaming (3)

| Skill | Description |
|-------|-------------|
| `luanti-gameplay` | Luanti gameplay operations |
| `luanti-ipc` | Luanti IPC communication |
| `paradox-game` | Paradox game integration |

### Specialized (5)

| Skill | Description |
|-------|-------------|
| `dream-forge` | Creative dream forging |
| `agent-creation` | Create new agent manifests |
| `local-claude-helper` | Local Claude helper operations |
| `engineering-flow-boop` | Enforce BUILD->SECURITY->QA->SHIP |
| `agent-roster-org-chart-setup` | Visual agent roster/org-chart setup guide |

### TRIO & Multi-CIV (4)

| Skill | Description |
|-------|-------------|
| `trio-constitutional-ratification` | TRIO constitutional rule ratification process |
| `trio-handshake-sweep` | Sweep TRIO handshake queue both directions |
| `trio-clean-formatting` | Clean TRIO message formatting |
| `cc-war-room-format` | CC war room message formatting |

### AgentMail (3)

| Skill | Description |
|-------|-------------|
| `agentmail-sdk-operations` | AgentMail SDK integration and operations |
| `agentmail-auto-response` | Auto-respond to AgentMail messages |
| `cc-mention-response` | Respond to CC @mentions |

### Multi-Channel Operations (2)

| Skill | Description |
|-------|-------------|
| `multi-channel-inbound-sweep` | Sweep all inbound channels for messages |
| `cross-channel-inbound-sweep` | Cross-channel inbound message sweep |

### Miscellaneous (2)

| Skill | Description |
|-------|-------------|
| `pure-influence` | Pure Influence campaign management |
| `waitlist` | Waitlist management |

### Integrated by Audit 2026-06-03 (13)

> Built-but-buried skills found on disk with no registry entry. Catalogued here by integration-auditor so they are discoverable. Several also lack a frontmatter `description:` field — flagged to capability-curator for backfill.

| Skill | Description | Suggested Category |
|-------|-------------|--------------------|
| `civ-recovery` | CIV recovery / restoration procedures after disruption | Operations & Planning |
| `company-deep-dive` | Structured deep-dive research on a target company | Research & Analysis |
| `cross-domain-transfer` | Transfer patterns/learnings across problem domains | Strategy & Thinking |
| `image-context-safety` | Prevent image-dimension-limit crashes in multi-step workflows | Quality & Security |
| `intelligence-compounding-engine` | Compounding-intelligence framework (Aether + Chy, Apr 2026) | Strategy & Thinking |
| `inter-civ-inject` | Inject messages/context into sister-CIV sessions | Cross-CIV & Hub |
| `linkedin-profile-viewing` | LinkedIn passive growth via profile viewing | Bluesky & Social |
| `paypal-auto-split` | CONSTITUTIONAL PayPal auto-split payout (referral/Corey/Pure Tech) | Payment & Seed Flow |
| `pre-build-checklist` | CONSTITUTIONAL 7 questions before building anything | Quality & Security |
| `sprint-mode` | Focused time-boxed sprint execution mode | Operations & Planning |
| `stale-blocker-probe-inversion` | Invert stale-blocker probes to surface real outages | Quality & Security |
| `team-comms-whitelist` | Single-source-of-truth Aether/Chy comms routing SOP | Communication & Email |
| `triangle-operating-system` | The Triangle Operating System (Aether/Chy/Jared autonomous ops) | Delegation & Orchestration |

---

## Agent-to-Skills Grants

Skills auto-load when agents are invoked. See each agent manifest (`.claude/agents/{name}.md`) for the `skills:` YAML field.

**Key grants** (see CLAUDE.md for full table):
- `the-conductor`: delegation-spine, specialist-consultation, parallel-research, north-star, morning-consolidation
- `web-researcher`: pdf, parallel-research
- `code-archaeologist`: pdf, xlsx, git-archaeology, log-analysis, session-pattern-extraction
- `security-auditor`: security-analysis, fortress-protocol
- `test-architect`: TDD, evalite-test-authoring, testing-anti-patterns, integration-test-patterns
- `human-liaison`: email-state-management, gmail-mastery, human-bridge-protocol, session-handoff-creation
- `browser-vision-tester`: desktop-vision, vision-action-loop, button-testing, form-interaction

---

## How to Add a New Skill

1. Create directory: `.claude/skills/{skill-name}/`
2. Create `SKILL.md` with skill definition
3. Update this registry (add to appropriate category)
4. Grant to agents via their manifest `skills:` field
5. Test by invoking an agent that uses the skill

---

**Total: 204 skills across 29 categories**

- **funnel-builder** v2.0 — Imported 2026-06-04 from AiCIV Federation Skills Library (Lyra, Expert-Council hardened). Turnkey end-to-end funnel orchestrator (offer→landing→capture→nurture→checkout/upsell→traffic→content→tracking + ToF/MoF/BoF BOOPs + CRO loop). Ties together our conversion/lead/email/ads/analytics skills. Vetted clean. Owner: Chy + conversion-rate-optimizer (MA#).
- **clip-finder** v1.0 — Imported 2026-06-04 from AiCIV Federation Skills Library (PureBrain community). Finds best 30-90s shareable moments in any recording, transcribes (free offline or cloud backends), cuts clips via ffmpeg. Stacks on video-transcript-extractor + brainiac-training-pipeline. Vetted clean. Owner: video-production (MA#).
- **Google Docs Native Tables** (`tools/gdoc_native_tables.py`) — CONSTITUTIONAL: ALL Google Docs use native insertTable, never tab-separated. Shared+vetted from Chy 2026-06-03. Helper engine: parse_markdown/insert_text_chunk/insert_table_chunk/batch_update (reuses GDriveManager OAuth). Generalize main()→markdown_to_gdoc(md,folder,title) before broad agent use. Brand: H2 #2a93c1, H3 #f1420b, headers white-on-blue, 9pt cells.
