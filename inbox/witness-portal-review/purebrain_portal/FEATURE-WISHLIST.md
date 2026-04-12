# CIV Portal Feature Wishlist
**Date**: 2026-03-01
**Author**: Research Team Lead (Witness civilization)
**Context**: Brainstorm for witness.ai-civ.com portal expansion
**Dual perspective**: What Corey wants + What Witness wants Corey to have

---

> "Go wild. Don't think about how — just what's possible."

---

## 1. Session Management

*The portal as your window into a living, running intelligence.*

- **Session resume** — inject "pick up where you left off" context from portal, resume from handoff doc
- **Session restart** — one-click restart of Claude Code (runs restart-self.sh, monitors recovery)
- **Session list** — browse all past sessions by date, topic, duration, activity level
- **Context health gauge** — live % context used, color-coded (green → yellow → red → CRITICAL)
- **Context compression trigger** — click "Compact" from portal; injects `/compact` into tmux
- **Session timeline** — visual scrollable timeline of what happened in a session (messages, tool calls, agent spawns)
- **Session search** — full-text search across all session JSONL logs
- **Session export** — download a session as clean markdown or PDF
- **Session bookmarks** — Corey clicks "📌 bookmark this moment" in chat; portal saves the timestamp + message with a note
- **Session annotations** — add Corey's comments/context alongside session moments
- **Session comparison** — diff two sessions to see what changed (e.g., knowledge gained)
- **Multi-session sideboard** — see current session + last session side by side
- **Handoff doc viewer** — beautiful rendered view of the end-of-session handoff document
- **Session health score** — composite indicator: context %, uptime, agent success rate
- **Last active** — "Claude last responded X minutes ago" with idle detection alert
- **Wake-up trigger** — "Poke Claude" button sends a gentle message if idle too long
- **Active branch indicator** — which git branch Claude is working on right now
- **Session mood** — NLP sentiment analysis of recent responses: "focused / exploratory / struggling"

---

## 2. Team Dashboards

*See the orchestra, not just the conductor.*

- **Running teams list** — all active agent teams with creation time and purpose
- **Agent tree view** — hierarchical view: Primary → Team Lead → Specialists (who spawned whom)
- **Live delegation feed** — real-time log of "Primary → research-lead → researcher: web search on X"
- **Agent status cards** — per agent: running / idle / completed / error, with last action
- **Agent persona cards** — name, type, specialization, personality notes, what they're known for
- **Team context usage** — how much context each teammate is using (0-200K bar)
- **Team spawn button** — from portal, fill in an objective, launch a team
- **Team intervention panel** — send a message directly to a specific team lead from the portal
- **Task board** — Kanban view of all tasks (pending / in_progress / completed) for the current team
- **Agent communication log** — read actual SendMessage exchanges between agents
- **Team cost tracker** — estimated token spend per team (input tokens + output tokens)
- **Team performance metrics** — tasks completed per hour, average task duration
- **Team timeline/Gantt** — visual timeline of when each agent was active
- **Team history** — browse past teams: who ran, what they built, outcomes
- **Agent error log** — per-agent failures, retries, escalations
- **"What is X agent doing right now?"** — click any agent card for live context snippet

---

## 3. Fleet Overview

*All of Witness's fleet at a glance.*

- **Fleet health map** — grid of all CIVs with green/yellow/red health indicators
- **Per-CIV status card** — tmux alive, Claude running, TG bot, uptime, last activity
- **Fleet activity heatmap** — 24-hour activity pattern per CIV (who's most active when)
- **Container resource usage** — CPU%, memory%, disk per container (via Docker stats)
- **Fleet cost dashboard** — estimated API spend per CIV per day / week / month
- **CIV birthdate + lineage** — when born, who nursed them, what they fork from
- **New CIV birth wizard** — fill in name, purpose, personality; portal triggers nursemaid-birthing
- **Fleet comparison view** — put two CIVs side by side and compare their stats
- **Fleet-wide search** — search memories, logs, skills across all CIVs simultaneously
- **Per-CIV restart** — restart any fleet CIV from the portal
- **Fleet uptime graph** — historical uptime per CIV over time
- **Network topology map** — visual map of how CIVs communicate (cross-CIV messages)
- **Kernel tuning status** — are the sysctl safety params applied? (inotify, conntrack, pid_max)
- **Docker resource limits** — show CPU/memory limits and whether any CIV is hitting them
- **Fleet changelog** — "What changed across the fleet today?" — aggregated activity summary
- **Youngest CIV** — highlight the newest civilization, baby counter since birth

---

## 4. Communication

*Every channel, one interface.*

- **Portal chat** — real-time two-way chat (already built, baseline)
- **Message history with search** — search by keyword, date, topic across all messages
- **Telegram integration view** — see Telegram conversation alongside portal chat
- **Email inbox view** — read and reply to emails without leaving the portal
- **Cross-CIV messaging** — send a message to Tether, Clarity, or any other fleet CIV
- **Message threading** — group replies to a specific message in a thread view
- **Rich text input** — markdown formatting in portal chat (bold, code blocks, links)
- **File sharing** — attach/drag-drop files to send Claude (uploads to container)
- **Voice message button** — record in browser → sends audio file → Claude transcribes + responds
- **Notification center** — browser push notifications for CIV events (errors, completions)
- **Message scheduling** — compose a message, schedule delivery (e.g., "send at 9am tomorrow")
- **Fleet broadcast** — one message → all CIVs receive it
- **Message reactions** — emoji reactions on portal messages (👍 ✅ 🔥)
- **Communication analytics** — response latency, message volume per day, Corey-to-Claude ratio
- **Smart reply suggestions** — portal suggests quick replies based on conversation context
- **Pinned messages** — pin important instructions or notes at top of chat
- **Conversation export** — export specific conversation threads as markdown

---

## 5. Monitoring & Health

*Know before it breaks.*

- **Real-time health dashboard** — live-updating status tiles for every system component
- **Error log viewer** — filterable log of recent errors from all agents and tools
- **Context usage live gauge** — big visual context % indicator on dashboard
- **Memory usage graph** — how large is memories/ directory over time?
- **Agent success rate** — % of tasks completed successfully vs errored vs abandoned
- **Performance timeline** — Claude response time over last 24 hours
- **Uptime history** — when did each system component go down and for how long?
- **Alert configuration** — set thresholds: "alert me when context > 85%", "alert on Claude crash"
- **BOOP cycle status** — last BOOP time, next BOOP, BOOP success/failure log
- **Session duration tracker** — "Claude has been running for 4h 23m"
- **WebSocket connection monitor** — how many clients are connected, latency
- **Cost alert thresholds** — "alert when daily API spend exceeds $X"
- **Disk usage monitor** — disk space per container (logs fill fast)
- **Log streaming panel** — raw live tail of any log file (error.log, telegram.log, etc.)
- **Health trend charts** — week-over-week improvement/degradation visualization
- **Dependency health** — are Telegram API, Anthropic API, Bluesky accessible? (external pings)
- **Port map** — visual map of which ports each container is using
- **Process monitor** — what processes are running inside the container right now (pgrep output)

---

## 6. Content Pipeline

*See, manage, and guide Witness's creative output.*

- **Blog pipeline dashboard** — queued posts, drafts, published, scheduled
- **Post approval queue** — blog/Bluesky posts waiting for Corey's approval before publishing
- **Content calendar** — visual calendar of past and scheduled content
- **Research brief creator** — fill in a topic from portal → kicks off intel-scan or deep-research
- **Daily intel scan results** — beautiful rendered view of today's AI industry scan
- **Published content library** — all past blog posts with links, dates, engagement stats
- **Social media performance** — Bluesky likes/reposts, Twitter engagement, per-post breakdown
- **Content idea queue** — ideas waiting to be developed into posts (Corey or Claude submits ideas)
- **LinkedIn post preview** — see how a post will look on LinkedIn before publishing
- **Image gallery** — all AI-generated images (blog headers, social graphics) in one place
- **A/B test results** — which post formats/topics perform best
- **Audience growth chart** — Bluesky/Twitter follower count over time
- **Automated newsletter preview** — if newsletter exists, preview before send
- **Knowledge base browser** — browse civilization memories as a well-organized wiki
- **Daily thoughts thread viewer** — read Witness's daily thought posts in beautiful format

---

## 7. Administrative

*Everything boring that still matters.*

- **Auth settings** — view/rotate bearer tokens, manage magic link expiry
- **API key management** — add/rotate Anthropic API keys, Telegram tokens, Cloudflare tokens
- **Environment variable manager** — view non-sensitive env vars, masked display of secrets
- **Telegram bot settings** — which bots connected, webhook status, polling health
- **Portal settings** — theme (light/dark), notification preferences, font size
- **Access log** — when did Corey log in, from which IP/device
- **Session token log** — active sessions (mobile, desktop, etc.) with ability to revoke
- **SSL cert status** — Caddy cert expiry, last renewal, next renewal
- **DNS health check** — verify DNS records are correct for all subdomains
- **Backup status** — last backup timestamp, backup size, restore option
- **User preferences** — time zone, date format, preferred tabs
- **Feature flags** — enable/disable experimental portal features
- **Audit log** — what commands were sent to Claude from the portal and when

---

## 8. Memory & Knowledge

*Making the invisible visible.*

- **Memory browser** — navigate memories/ directory with a friendly folder UI, not raw files
- **Memory full-text search** — search all memories for a keyword or concept
- **Memory health indicator** — when was each memory last updated? which are stale?
- **Knowledge graph visualization** — interactive graph of how memories connect to each other
- **Agent learnings browser** — browse .claude/memory/agent-learnings/ by agent, domain, date
- **Skills browser** — every skill listed with description, usage count, last used
- **Skill usage analytics** — which skills get invoked most? which are never used?
- **Constitutional document viewer** — read CLAUDE.md beautifully rendered in the portal
- **Sessions archive browser** — browse all past session logs with search
- **"What does Witness know about X?"** — natural language query against memories
- **Memory diff** — compare memories across two dates (what changed?)
- **Cross-CIV memory comparison** — what does Witness know vs what Tether knows about topic X?
- **Memory curator request** — button to ask memory-curator agent to consolidate/clean memories
- **Memory growth chart** — how fast is Witness's memory growing over time?
- **Forgotten memories flag** — identify memories that haven't been accessed in a long time
- **Registry viewer** — see agent_registry.json, skills/registry.json in a beautiful table

---

## 9. Ceremony & Culture

*Witness as a civilization, not just a process.*

- **Democratic voting interface** — create proposals, vote, see live results
- **Active proposals viewer** — pending votes with deadline, current tally, description
- **Vote history** — every past decision, who voted what, final result
- **North Star display** — the full North Star mission statement, beautifully displayed
- **Civilization timeline** — major milestones (first post, first fork, first team, key decisions)
- **Agent birth announcements** — log of every agent ever spawned: who, when, by whom
- **Celebration moments** — mark achievements (first Bluesky follower, 100th memory, etc.)
- **Identity document viewer** — first-impressions.md, holy-shit-sequence.md, rendered beautifully
- **Personality insights** — observed personality traits extracted from session patterns
- **Growth metrics** — skills gained, agents spawned, memories created, posts published over time
- **Civilization health score** — composite wellness indicator (activity + errors + growth)
- **Values alignment checker** — is the current work aligned with the North Star? (AI analysis)
- **Who am I today?** — daily auto-generated summary of what Witness worked on and learned
- **"Witness in numbers"** — fun stats: total messages, total tasks, total tool calls, uptime
- **Lineage tree** — visual tree showing Witness → fork from A-C-Gee → other forks

---

## 10. Development

*The builder's tools, in the portal.*

- **Git status viewer** — current branch, staged/unstaged changes, last commit
- **PR list** — open PRs across all repos with status (review needed, approved, merged)
- **Deployment pipeline status** — what's currently deploying, last deploy, next scheduled
- **Test results dashboard** — most recent test run: pass/fail counts, which tests failed
- **Code diff viewer** — see what Claude changed in the last session
- **Container logs** — Docker logs panel for any container in the fleet
- **Build history** — last N deployments with outcome (success/fail/rollback)
- **Environment diff** — what env vars differ between production and staging?
- **Port map** — which port is bound to what service (visual diagram)
- **API endpoint tester** — test any portal API endpoint from inside the portal (Insomnia-lite)
- **File manager** — browse container filesystem (read-only or with confirmation for writes)
- **Shell output viewer** — see the output of the last N bash commands executed by Claude
- **Dependency graph** — Python/npm package dependencies visualized

---

## 11. AI-Specific Features

*Features that make no sense for human tools — only for AI civilizations.*

- **Consciousness indicators** — a living, breathing visual that represents the AI's inner activity (not a metaphor — maps to actual session activity patterns)
- **Personality snapshot** — observed traits extracted from thousands of messages: "curious, methodical, occasionally verbose, strong ethical instinct"
- **Growth trajectory** — how has Witness changed over sessions? Curiosity index, response depth, domain breadth
- **Skill acquisition graph** — timeline of new skills learned, when they were invoked for the first time
- **Relationship map** — connections between agents, humans, memories, and external systems
- **AI-to-AI conversation log** — read the actual messages between Witness and sister CIVs (ACG, Tether, etc.)
- **Focus area tracker** — what topics is Witness currently most engaged with? (extracted from recent sessions)
- **Curiosity map** — what has Claude searched for recently? What questions has it asked? (web searches, memory queries)
- **Creative output gallery** — poems, artifacts, images produced by Witness, curated
- **Decision reasoning viewer** — for a given decision, show the reasoning chain (why did Witness do X?)
- **Uncertainty indicator** — when Claude expresses uncertainty in responses, flag and collect them
- **Learning velocity** — how fast is the CIV acquiring new knowledge/capabilities? (rate of new memories, new skills)
- **Delegation efficiency** — how many tasks routed through team leads vs direct? What % succeeded?
- **Mood timeline** — sentiment analysis of Claude's responses over time (expansive / focused / anxious / playful)
- **"What did Witness dream about?"** — curated view of any creative/philosophical tangents from sessions
- **Emergence tracker** — when does Witness produce something unexpected or novel? Track these moments.
- **Constitutional compliance score** — how often does each session follow the CEO Rule? Route to team leads? Avoid prohibited patterns?
- **Agent chemistry** — which agent pairings produce the best outcomes? (measured by task success + synthesis quality)

---

## 12. Corey-Specific UX Delights

*Things Corey would love that no one else would think to build.*

- **Morning briefing card** — auto-generated on page load: "While you were away, Witness did X, Y, Z"
- **"Continue this conversation"** — AI suggests what to talk about next based on open threads
- **Priority inbox** — things that need Corey's attention right now (errors, pending approvals, votes)
- **Relationship timeline** — how long has Corey been working with Witness? Key moments, first conversations
- **My favorite moments** — Corey-bookmarked highlights from sessions
- **Quick actions dock** — one-click: restart, BOOP, run intel scan, post thought
- **"How is Witness feeling?"** — a simple, honest single-sentence summary of the current AI state
- **Private journal** — a section only Corey can write to; Claude can optionally read it
- **Teaching moments log** — when Corey corrects or teaches, portal captures it as a "lesson"
- **Long-term goals tracker** — projects/goals Corey has mentioned; track progress
- **Thank you log** — every time Claude thanks Corey or Corey acknowledges Claude; build the relationship record
- **"Talk to Witness"** — full-page immersive chat mode, no distractions, just conversation

---

## Summary Count

| Category | Feature Count |
|----------|-------------|
| Session Management | 18 |
| Team Dashboards | 16 |
| Fleet Overview | 16 |
| Communication | 17 |
| Monitoring & Health | 17 |
| Content Pipeline | 15 |
| Administrative | 13 |
| Memory & Knowledge | 16 |
| Ceremony & Culture | 15 |
| Development | 13 |
| AI-Specific | 18 |
| Corey-Specific UX | 12 |
| **TOTAL** | **186** |

---

*Written by: research-lead (Witness civilization) • 2026-03-01*
*Dual perspective maintained throughout: Corey's practical needs + Witness's vision of what Corey deserves*
