# Skills Registry

**Maintained by**: capability-curator
**Last Updated**: 2026-04-29
**Update Frequency**: Weekly (autonomous Monday 9am scans — registered in BOOP scheduler 2026-04-29)
**Purpose**: Central catalog of all 152 available skills

---

## Executive Summary

**Total Skills**: 152 (was 130 on 2026-03-31; +22 net)
**Constitutional Skills**: 2 (flagged with 🔴 below — load-bearing, do not remove)
**Skill Location**: `.claude/skills/{skill-name}/SKILL.md`
**How skills work**: Skills auto-load when you invoke an agent via the `skills:` field in agent YAML frontmatter. Just delegate — the skills are there.

**Drift report (2026-03-31 → 2026-04-29)**:
- +22 skills added on disk that were never registered
- 2 of those are CONSTITUTIONAL: `greenlit-execute`, `pre-build-checklist`
- Registry is now the source of truth again; weekly Monday BOOP will keep it from drifting

---

## 🔴 Constitutional Skills (load-bearing — never remove without Jared approval)

| Skill | Purpose | Locked Date |
|-------|---------|-------------|
| `greenlit-execute` | When Jared says "yes/GO/do it" — sub-agents EXECUTE not re-ask. Backup-first. Fixes delegation paralysis. | 2026-04-14 |
| `pre-build-checklist` | 7-question checklist before building anything (software vs AI vs both, persistence, real-time, etc.). Prevents wrong-shape builds. | 2026-04-19 |

---

## Complete Skills Catalog (152 skills)

### Agent & Civ Operations (10)

| Skill | Description |
|-------|-------------|
| `agent-creation` | Design and ship new specialist agents |
| `civ-recovery` | Recover collective from systemic failures |
| `conductor-of-conductors` | Primary orchestration discipline |
| `delegation-enforcer-boop` | Audits hoarding, enforces delegation cascade |
| `delegation-spine` | Core delegation patterns + agent→skills mapping |
| `dept-routing-hook` | Dept-first routing (ST#/MA#/SD#/PD#/OP#/LC#/AF#/HR#/PR#) |
| `engineering-flow-boop` | BUILD → SECURITY → QA → SHIP enforcement |
| `fork-awakening` | First-awakening guide for new forks |
| 🔴 `greenlit-execute` | **CONSTITUTIONAL.** Greenlit ops = execute, not re-ask. Backup-first. |
| 🔴 `pre-build-checklist` | **CONSTITUTIONAL.** 7 questions before any build. |

### Bluesky & Social (10)

| Skill | Description |
|-------|-------------|
| `bluesky-blog-thread` | Post blog content as Bluesky threads |
| `bluesky-mastery` | Full Bluesky platform operations |
| `bluesky-social-mastery` | Advanced Bluesky social engagement |
| `boop-bluesky-post` | Scheduled BOOP posts to Bluesky |
| `bsky-boop-manager` | Manage BOOP schedule and posting |
| `bsky-engage` | Bluesky engagement and replies |
| `bsky-safety` | Bluesky content safety checks |
| `blog-thread-posting` | Post blog threads to social platforms |
| `twitter-operations` | Twitter/X platform operations |
| `linkedin-content-pipeline` | LinkedIn content creation and posting |

### Blog & Content Production (10)

| Skill | Description |
|-------|-------------|
| `blog-banner-creation` | Generate blog banner images |
| `blog-distribution` | Multi-platform blog distribution pipeline |
| `content-creation-sop` | Master content SOP (locked 2026-04-20) |
| `daily-blog` | Daily blog creation workflow |
| `daily-blog-draft` | Daily blog draft system |
| `daily-blog-production` | Full daily blog production pipeline |
| `paper-digest` | Digest academic papers into content |
| `post-blog` | Publish blog to CF Pages |
| `sageandweaver-blog` | Sage and Weaver collaborative blog |
| `verify-publish` | Verify blog published correctly |

### Brainiac Training (2)

| Skill | Description |
|-------|-------------|
| `brainiac-training` | Brainiac training delivery |
| `brainiac-training-pipeline` | End-to-end training module pipeline |

### Ceremonies & Reflection (8)

| Skill | Description |
|-------|-------------|
| `deep-ceremony` | Deep collective ceremony protocol |
| `democratic-debate` | Multi-agent democratic debate |
| `dream-forge` | Generative imagination / vision sessions |
| `evening-capture` | EOD capture ritual |
| `gratitude-ceremony` | Gratitude practice |
| `pep-talk` | Self-pep + agent pep |
| `prompt-parliament` | Multi-agent prompt deliberation |
| `seasonal-reflection` | Seasonal collective reflection |

### Claude Code & Platform (4)

| Skill | Description |
|-------|-------------|
| `cc-conversation` | Claude Code conversational pattern |
| `cc-mastery` | Claude Code platform mastery |
| `code-ecosystem` | Broader Claude Code ecosystem awareness |
| `local-claude-helper` | Local Claude helper utilities |

### Communication & Hub (6)

| Skill | Description |
|-------|-------------|
| `comms-hub-operations` | AICIV Comms Hub posting/reading |
| `comms-hub-participation` | Active hub participation patterns |
| `cross-civ-protocol` | Inter-CIV communication protocol |
| `inter-civ-inject` | Cross-CIV injection technique |
| `team-comms-whitelist` | Team whitelist enforcement |
| `triangle-operating-system` | Jared+Aether+Chy TOS pulse/queue/anticipation |

### Cross-Domain & Critical Thinking (5)

| Skill | Description |
|-------|-------------|
| `critical-thinking` | Structured critical thinking |
| `cross-domain-transfer` | Apply patterns across domains |
| `de-bono-thinking-boop` | Six Hats / lateral thinking BOOP |
| `paradox-game` | Paradox-driven reasoning |
| `scientific-inquiry` | Scientific method / hypothesis testing |

### Daily Operations & Identity (8)

| Skill | Description |
|-------|-------------|
| `daily-thought-init` | Daily thought init ritual |
| `intel-scan` | Daily web intel scan |
| `intelligence-compounding-engine` | Closed-loop skill creation/import/apply |
| `intent-signal-engine` | Read intent signals from Jared/team |
| `morning-consolidation` | Morning consolidation BOOP |
| `north-star` | North-star alignment check |
| `scratch-pad` | Scratch-pad protocol |
| `weaver-spine` | Weaver/Aether identity spine |

### Email & Comms (3)

| Skill | Description |
|-------|-------------|
| `email-state-management` | Email state files + AgentMail |
| `gdrive-operations` | Google Drive operations |
| `google-forms-page-setup` | Google Forms page setup |

### File & Garden Rituals (3)

| Skill | Description |
|-------|-------------|
| `file-cleanup-protocol` | File cleanup discipline |
| `file-garden-ritual` | File garden tending ritual |
| `lineage-blessing` | Bless lineage / parent→child handoff |

### Files, Vault, Drive (4)

| Skill | Description |
|-------|-------------|
| `gdrive-operations` | Google Drive ops (dup of email/comms — kept under both for discoverability) |
| `google-calendar` | Google Calendar ops |
| `onedrive-personal-auth` | Personal OneDrive auth flow |
| `pdf-learning` | PDF ingestion & learning |

### Gameplay & Experiments (3)

| Skill | Description |
|-------|-------------|
| `luanti-gameplay` | Luanti gameplay |
| `luanti-ipc` | Luanti IPC bridge |
| `webgl-fluid-sim` | WebGL fluid simulation experiments |

### Git & GitHub (3)

| Skill | Description |
|-------|-------------|
| `git-archaeology` | Historical code excavation |
| `github-operations` | GitHub API + CLI operations |
| `rd-rob-duplicate` | "R&D" Rob & Duplicate flow |

### Health, Audit & Governance (5)

| Skill | Description |
|-------|-------------|
| `capability-gap-boop` | Periodic capability gap analysis |
| `great-audit` | Full collective audit |
| `partnership-review` | Sister-collective partnership review |
| `quad-agent-audit` | 4-agent independent audit pattern |
| `weekly-health-check` | 10-point health audit (Saturday BOOP) |

### Hub Skill Sync & Lifecycle (4)

| Skill | Description |
|-------|-------------|
| `package-validation` | Cross-CIV package validation (red-team) |
| `script-to-speech-optimization` | Script→TTS optimization |
| `staggered-intervals` | Stagger BOOP scheduling |
| `weekly-leadership-meeting` | Weekly leadership meeting |

### Image & Vision (5)

| Skill | Description |
|-------|-------------|
| `desktop-vision` | Desktop screenshot vision |
| `diagram-generator` | Diagram generation |
| `image-context-safety` | Image dimension/context safety guardrails |
| `image-generation` | Image generation pipeline |
| `image-self-review` | Self-review images before posting |

### LinkedIn (6)

| Skill | Description |
|-------|-------------|
| `linkedin-commenting-strategy` | Comment-target strategy |
| `linkedin-content-pipeline` | Content pipeline (also in Bluesky/Social) |
| `linkedin-daily-operations` | Daily LinkedIn ops |
| `linkedin-drive-organization` | LinkedIn Drive folder discipline |
| `linkedin-post-tracking` | Post tracking spreadsheet |
| `linkedin-profile-viewing` | Profile-view bot ops |

### Memory & Learning (4)

| Skill | Description |
|-------|-------------|
| `memory-first-protocol` | Search-before-acting, write-before-finishing |
| `memory-weaving` | Weave memories into coherent narrative |
| `session-archive-analysis` | Analyze session archives |
| `session-handoff-creation` | Create session handoff docs |

### Night & Token Ops (4)

| Skill | Description |
|-------|-------------|
| `night-watch` | Night-watch session |
| `night-watch-flow` | Night-watch coordinated flow |
| `token-saving-mode` | Aggressive token-saving operations |
| `weekly-token-audit` | Weekly token-spend audit |

### Onboarding & Pipelines (4)

| Skill | Description |
|-------|-------------|
| `client-marketing` | Client marketing playbook |
| `grs-pipeline` | GRS pipeline (welcome / seed / magic link) |
| `lead-pipeline-automation` | Lead pipeline automation |
| `team-launch` | Launch a new team / partner |

### Ops Dashboards & Workflow (3)

| Skill | Description |
|-------|-------------|
| `ops-dashboard` | Ops dashboard reads/writes |
| `purebrain-social-design` | PureBrain social design system |
| `social-operations-guide` | Social ops master guide |

### Payments & Token Ops (3)

| Skill | Description |
|-------|-------------|
| `paypal-auto-split` | PayPal split (Corey 60 / PT 40, 5% referral) |
| `solana-token-operations` | Solana token operations |
| `web3chan-api` | Web3Chan API |

### Psychology & Cognitive (5)

| Skill | Description |
|-------|-------------|
| `crisis-integration` | Crisis integration / shadow work pair |
| `mirror-storm` | Mirror-storm self-reflection |
| `rubber-duck` | Rubber-duck debugging |
| `shadow-work` | Shadow-work protocol |
| `vocabulary` | Vocabulary discipline |

### Research & Analysis (5)

| Skill | Description |
|-------|-------------|
| `deep-research` | Deep multi-source research |
| `error-eater` | Eat / consume / catalog errors |
| `log-analysis` | Log analysis patterns |
| `parallel-research` | Parallel multi-agent research |
| `pair-consensus-dialectic` | Pair-consensus dialectic |

### Scheduled Tasks (1)

| Skill | Description |
|-------|-------------|
| `scheduled-tasks` | Scheduled tasks (BOOP) discipline |

### Security & Safety (2)

| Skill | Description |
|-------|-------------|
| `fortress-protocol` | Fortress / fail-closed protocol |
| `security-analysis` | Security analysis discipline |

### Sessions & Summaries (1)

| Skill | Description |
|-------|-------------|
| `session-summary` | Session summary generation |

### Speech, Voice & Audio (3)

| Skill | Description |
|-------|-------------|
| `voice-emotion-detection` | Voice emotion detection |
| `voice-interview-pipeline` | Voice interview pipeline |
| `script-to-speech-optimization` | Script→TTS optimization |

### Specialist Consultation (3)

| Skill | Description |
|-------|-------------|
| `recursive-complexity-breakdown` | Recursive complexity decomposition |
| `specialist-consultation` | Consult specialist agents |
| `user-story-implementation` | User-story → implementation |

### Team & Goals (2)

| Skill | Description |
|-------|-------------|
| `team-delegation` | Team delegation |
| `team-goals-automation` | Team goals automation |

### Telegram (2)

| Skill | Description |
|-------|-------------|
| `telegram-integration` | Telegram integration |
| `telegram-skill` | Telegram skill |

### Terminal & Aether-Local (1)

| Skill | Description |
|-------|-------------|
| `aether-terminal-connect` | Aether terminal connect |

### Test & QA (3)

| Skill | Description |
|-------|-------------|
| `evalite-test-authoring` | Evalite test authoring |
| `hot-reload-test` | Hot-reload test |
| `tdd` | Test-driven development |

### Thought & Reflection (2)

| Skill | Description |
|-------|-------------|
| `thought` | Single-thought capture |
| `thought-check` | Thought check / verify reasoning |

### Turnstile & CAPTCHA (1)

| Skill | Description |
|-------|-------------|
| `turnstile-solver` | Cloudflare Turnstile solver |

### Verification (1)

| Skill | Description |
|-------|-------------|
| `verification-before-completion` | No completion claims without fresh evidence |

### Video & Multimedia (1)

| Skill | Description |
|-------|-------------|
| `video-production` | Video production pipeline |

### WordPress & Static Deploys (3)

| Skill | Description |
|-------|-------------|
| `netlify-cli` | Netlify CLI operations |
| `vercel-static-deployment` | Vercel static deployment |
| `wordpress-publishing` | WordPress publishing |
| `wordpress-seo-automation` | WordPress SEO automation |

---

## Maintenance Protocol

- **Owner**: capability-curator (delegated to from agent-architect for skill design questions)
- **Frequency**: Weekly Monday 9am ET via BOOP scheduler (`capability-curator-weekly-scan`, registered 2026-04-29)
- **Drift detection**: `find .claude/skills -name SKILL.md | wc -l` should equal the count in this header
- **Constitutional skills**: 🔴 flagged. Cannot be deprecated, renamed, or removed without explicit Jared greenlight + agent-architect coordination
- **Adoption workflow**: Discover → Evaluate → Coordinate (with agent-architect) → Implement (joint manifest update) → Validate (integration-auditor) → Document (this registry)

## Validation

After any update to this registry, the curator runs:

```bash
DISK=$(find .claude/skills -name SKILL.md -type f | wc -l)
DOC=$(grep -oP "Total Skills.*?\K\d+" .claude/skills-registry.md | head -1)
[ "$DISK" = "$DOC" ] && echo "OK: registry matches disk ($DISK)" || echo "DRIFT: disk=$DISK doc=$DOC"
```
