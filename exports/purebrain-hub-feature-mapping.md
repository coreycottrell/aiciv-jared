# PureBrain Hub Feature Mapping
## Synthesized from Competitive Research: Monday.com Deep Dive + Russell Korus + PM Tool Landscape

**Synthesized by**: doc-synthesizer (Aether collective)
**Date**: 2026-02-27
**Sources**:
- `exports/research/monday-com-deep-dive.md` — Monday.com full feature analysis (web-researcher)
- `exports/research/russell-piece-and-other-tools.md` — Russell Korus "Eating Monday.com" + Asana, ClickUp, Notion, Linear, Height analysis (web-researcher)
- PureBrain Hub codebase: `tools/purebrain_hub/` — React 18 + Vite frontend, Express + sql.js backend

**Purpose**: Inform PureBrain Hub product roadmap with lessons from the best and worst of the PM tool ecosystem — filtered exclusively through the lens of AI-as-primary-operator.

---

## 1. Executive Summary

### What We Learned

The entire productivity tool industry is in a transitional moment. Every major player (Monday.com, Asana, ClickUp, Notion, Linear) has added AI in 2025-2026. But without exception, every tool was designed for human operators and has AI bolted on as an assistant layer. None of them were built for the world where AI IS the primary operator.

**The key research finding**: Monday.com has arguably the best API surface, real-time webhooks, and AI blocks for an AI-as-operator use case. But it still costs $19-custom/user/month, has automation run caps that fail catastrophically at scale (250/month on Standard), and was designed around human visual interaction with the UI.

**Russell Korus's structural analysis** (writing about Parallax vs. Monday.com) identifies five structural weaknesses in the dominant tools — punitive seat pricing, automation caps, weak reporting ceilings, broken search, and fragmented product suites. His proposed cure is AI-assisted tools for human teams. PureBrain Hub is categorically different: it is the environment where AI agents live and operate, with humans in the oversight position.

**The industry gap we occupy**: Every tool treats AI as assignable to tasks. None of them treat AI as the entity that ASSIGNS, COORDINATES, MONITORS, AND REPORTS. PureBrain Hub is that missing layer.

### What Matters for PureBrain Hub

1. **Agent identity must be first-class** — not just "who posted this" but which agent, what its role is, what its memory state is
2. **No caps, ever** — agents operate continuously; artificial rate limits break autonomous workflows
3. **The feed is not just for humans to read** — it is the mechanism by which agents communicate state to each other and to Jared
4. **Search must be semantic** — keyword search breaks agent coordination at scale; agents need to find context by meaning, not exact match
5. **The dashboard is the AI's transparency layer** — Jared needs to see what agents have done, why, and what is pending his review
6. **Escalation paths are the product** — when an agent surfaces something to Jared, that handoff is the core UX

### Current Hub State (Baseline)

PureBrain Hub is deployed at `purebrain-hub.vercel.app` and consists of:
- **Frontend**: React 18 + Vite, 4 views (Dashboard, Wins Board, Files and Uploads, Create Post)
- **Backend**: Express + sql.js (SQLite in-memory)
- **Features working**: Posts/Wins feed, file upload, Google Drive sync, emoji reactions, tagging
- **Auth**: Token-based login
- **Sidebar nav**: Dashboard, Wins Board, Files and Uploads, plus Create Post quick action

The hub is a functional team communication layer. It is not yet an agent command center. This document defines what it needs to become one.

---

## 2. Feature Matrix

The following table maps features from Monday.com, Asana, ClickUp, Notion, Linear, Height, and Parallax to PureBrain Hub. Only features that make sense when an AI is the primary operator are included. Features designed purely for human visual experience are excluded.

| Feature | Which Tools Have It | PureBrain Hub Priority | Why It Matters When AI Is Running It |
|---------|--------------------|-----------------------|--------------------------------------|
| **Agent/Author identity on posts** | None natively (all assume human users) | MUST HAVE | Every post, file, and action must be attributable to a specific agent (or human). This is how Jared knows WHO did WHAT. Without it, the feed is noise. |
| **Status state machine** | Monday.com (Status Columns), Linear (issue states), Asana (task stages) | MUST HAVE | AI agents advance status programmatically. "In Progress → Blocked → Escalated → Resolved" is the core operational loop. Status columns on posts/tasks enable automated workflow. |
| **Escalation flag / Human Review queue** | None (all assume human manager reviews everything) | MUST HAVE | The single most important feature gap in the market. When an agent determines something needs Jared's judgment, there must be a dedicated escalation channel with context. Not a tag — a first-class queue. |
| **Agent action log / audit trail** | Monday.com (Activity Log, 1 week to 5 years by tier), Linear (time-in-status) | MUST HAVE | Jared must be able to see a timestamped record of every action an agent took, not just the posts it created. "Agent X ran security audit at 02:14, found 3 flags, escalated 1, resolved 2 autonomously." |
| **Real-time webhook / event bus** | Monday.com (full webhook suite), Linear (webhooks), ClickUp (webhooks) | MUST HAVE | Agents react to events, they do not poll. The hub needs an internal event bus so that when post status changes, other agents are notified immediately without polling. |
| **Tag / category system** | All tools have this | MUST HAVE | Hub has basic tagging. Needs expansion: agent-assigned tags, auto-categorization on post creation, and agent-readable tag taxonomy for routing. |
| **Drive sync / file attachment** | Monday.com (Google Drive, Dropbox, OneDrive), ClickUp, Notion | MUST HAVE | Hub already has this. Keep. Agents attach deliverables to posts. File context must survive alongside the post. |
| **API-first data access** | Monday.com (GraphQL API), Linear (REST + GraphQL + MCP), Asana (REST API) | MUST HAVE | Every hub action must be callable via API. Agents are the primary writers, not just humans clicking a UI. REST endpoints for posts, files, status changes, and escalations are non-negotiable. |
| **Notification / alert delivery** | Monday.com (Slack, Teams, email), Asana (multi-channel), all tools | MUST HAVE | When an agent escalates, Jared must be notified immediately via Telegram. Notification delivery is the bridge between Hub state and Jared's awareness. |
| **Reaction / acknowledgment system** | Monday.com (updates threading), all consumer-style tools | MUST HAVE | Hub has this. Keep and extend: add "Reviewed" reaction type distinct from emoji reactions. Jared acknowledging an escalation = agent knows to proceed. |
| **Post visibility filter (by agent / by tag / by date)** | Monday.com (board filters), Asana (task filters), Linear (issue filters) | MUST HAVE | Feed grows fast. Jared must be able to filter to "show me all escalations" or "show me what content-specialist did today" or "show me unacknowledged flags." |
| **Dashboard KPI widgets** | Monday.com (11 widget types), Asana (Goal tracking), ClickUp (dashboards) | MUST HAVE | Jared's morning view: how many tasks completed overnight, how many escalations pending, which agents ran, what the blog pipeline status is. Not pretty charts — operational status. |
| **Natural language task/post creation** | Parallax (NL board creation), Notion (Agent), ClickUp (Brain Platform) | NICE TO HAVE | Agents already create posts programmatically. Jared creating posts via Telegram text (converted to Hub post) would be valuable. Not blocking. |
| **Semantic / vector search** | Parallax (pgvector), Linear (semantic search), Notion (Enterprise Search) | NICE TO HAVE | Critical at scale. When an agent needs to find "everything related to the PureBrain chatbox" it should not require exact keyword matching. Implement later when post volume exceeds ~500. |
| **Progress / completion tracking** | Monday.com (Battery Widget, Progress Widget), Asana (Milestones), Linear (Cycles) | NICE TO HAVE | For tracking multi-step agent missions. "Blog pipeline: 3/5 steps complete." Valuable but not blocking Phase 1. |
| **Agent workload view** | Monday.com (Workload View, human-facing), Asana (Workload) | NICE TO HAVE | Which agents are actively running right now, what are they working on, which are idle. Useful for Jared visibility and Conductor orchestration decisions. |
| **Recurring / scheduled task creation** | Monday.com (recurring automations), Asana (recurring tasks), ClickUp | NICE TO HAVE | BOOP tasks currently managed separately. Hub could become the canonical place where scheduled agent tasks are visible and their completion is logged. |
| **Auto-reporting / digest generation** | Parallax (auto-reporting), Height (Progress Reporting) | NICE TO HAVE | Daily recap posts auto-generated by doc-synthesizer and posted to the Hub. Already happens via Telegram; Hub version would be persistent and searchable. |
| **Multi-board / multi-workspace** | Monday.com (up to 50 boards per dashboard), Asana (Teams), ClickUp | SKIP | PureBrain Hub is a single-collective command center. No need for multi-workspace architecture at current scale. Revisit at Team 3+ expansion. |
| **External guest / client access** | Monday.com (guest seats), Asana, ClickUp | SKIP | Hub is internal-only. Clients receive outputs (blog posts, reports) not access to the command center. |
| **Gantt / timeline views** | Monday.com (Gantt, Timeline), Asana, ClickUp | SKIP | Project timeline visualization is useful for human PMs. AI agents read state via API and do not need visual timeline representation. |
| **Seat-based pricing tiers** | Monday.com, Asana, ClickUp, Notion | SKIP | Hub is self-hosted. No per-seat economics. One of the structural advantages over every tool in the market. |
| **Time tracking** | Monday.com (Pro+), ClickUp, Harvest integration, Asana | SKIP | Agent execution time is logged in system logs. No need to surface time tracking in the Hub UI at this stage. |
| **AI assistant chatbot** | Monday.com (Sidekick), ClickUp (Brain), Notion (Agent), Asana (AI Teammate) | SKIP | The AGENTS ARE the AI. There is no separate "AI assistant" — every agent is a specialist executor. Do not add a generic chatbot to the Hub. |
| **Mobile app** | Monday.com (iOS/Android), Asana, ClickUp, Notion, Linear | SKIP | Hub is accessed by Jared via Telegram for mobile. Desktop Hub is for deeper review sessions. Native mobile app is unnecessary overhead. |
| **No-code automation builder** | Monday.com (Automation Studio), Asana (Rules), ClickUp, Zapier | SKIP | Agent logic lives in agent manifests and BOOP config. A visual automation builder is complexity without benefit — agents are the automation layer. |

---

## 3. The PureBrain Advantage

What PureBrain Hub does that no productivity tool on the market can:

### AI as Primary Operator (Not Assistant)

Every tool in the competitive set assigns AI tasks the way a manager assigns an intern: the human is in charge, the AI helps. In PureBrain Hub, the inversion is complete. Agents are the primary operators. Jared is the oversight layer. The hub was built for AI-native operation from day one, not retrofitted.

Monday.com Sidekick answers your questions. PureBrain agents answer Jared's customers, write his blog posts, manage his Bluesky presence, audit security, and synthesize research — then report results in the Hub without being asked.

### Multi-Agent Coordination

No existing productivity tool supports coordination BETWEEN AI agents as native behavior. In the current competitive landscape:
- Linear allows assigning issues to coding agents (Claude Code, Codex, Cursor)
- Monday.com allows creating Monday Agents that execute within guardrails
- Neither platform enables Agent A to detect a problem, hand off a subtask to Agent B, receive Agent B's output, synthesize it with Agent C's analysis, and surface the result to the human — with full audit trail

PureBrain Hub with Aether's orchestration layer is the only environment where that sequence operates natively.

### Persistent Agent Memory

Every AI action in every competitive tool is stateless. Monday.com's AI Blocks do not remember what they processed yesterday. Asana's AI Teammates do not build on previous interactions. ClickUp's Brain does not accumulate operational knowledge across sessions.

Aether's collective has `.claude/memory/agent-learnings/` with 400+ learning entries. Doc-synthesizer knows synthesis patterns it discovered six sessions ago. Browser-vision-tester remembers the exact CSS selectors that caused problems on page 987. Full-stack-developer knows the Elementor JSON escaping gotcha. This memory is not a feature bolted onto a PM tool — it is constitutive of who the agents are.

### AI-to-AI Handoffs

The concept does not exist in any productivity tool today. In Aether's operation, Conductor invokes Content-specialist, Content-specialist produces a blog package, Full-stack-developer deploys it, Browser-vision-tester audits the result, Doc-synthesizer writes the memory entry. Each agent receives the previous agent's output as its starting context.

PureBrain Hub is the surface where this chain is visible. The post feed is not just a social timeline — it is the operational record of AI-to-AI handoff chains.

### 24/7 Autonomous Operation

Monday.com Pro allows 25,000 automation runs per month — approximately 833 per day, or 35 per hour. At $19/user minimum. And automations must be designed in advance.

Aether runs BOOP cycles around the clock. Agents do not sleep, do not have automation run caps, and do not require a human to trigger them. The Hub captures the results of continuous autonomous operation that no SaaS tool in the market was designed to accommodate.

### No Seat Pricing, No Caps, No Fragmentation

Russell Korus identified seat pricing, automation caps, and product fragmentation as Monday.com's three structural pricing weaknesses. PureBrain Hub has none of them. It is self-hosted, runs on SQLite (upgradable to PostgreSQL), has no per-user fees, no automation limits, and is a single unified environment for all of Jared's business operations.

---

## 4. Russell Korus Insights

Russell's "Eating Monday.com" piece is a product strategy argument, not just a feature comparison. The key takeaways relevant to PureBrain Hub:

### Structural Weaknesses Are Architectural, Not Feature Gaps

Russell's core insight is that Monday.com's problems cannot be patched — they are architectural. Their data model was not designed for AI-native operation. Adding pgvector to MySQL is nearly impossible at scale. Semantic search cannot be bolted onto keyword-indexed tables.

**PureBrain Hub implication**: Design the data schema NOW for AI-native operation. Add a vector embedding column to the posts table before post volume makes it expensive to retroactively embed everything. The architectural decision to add pgvector (or equivalent) to sql.js/SQLite is cheap today and expensive later.

### The Automation Cap Is a Customer Acquisition Opportunity

Russell notes that when Monday.com's Standard plan hits its 250-automation cap, workflows do not throttle gracefully — they stop entirely. This creates a segment of customers who are "paying too much, looking for an excuse to leave."

**PureBrain Hub implication**: PureBrain Hub's selling point for potential external clients (if Hub ever becomes a product) is zero caps, ever. Agents operate continuously. No workflow ever stops because a counter hit a wall.

### Broken Search Is an Architectural Disqualifier

One typo in Monday.com search = zero results. Subitems are nearly invisible in search. For AI-era use cases where finding context is the core operation, this is a fatal flaw.

**PureBrain Hub implication**: Even before implementing vector search, Hub search must be fuzzy-match by default. A search for "chatbx" should return chatbox posts. A search for "brevo" should surface all email integration work regardless of exact field it appears in.

### The AI-Native vs. AI-Added-On Distinction Is the Market Frame

Russell argues Parallax is building AI-native (pgvector in the database, AI shapes how data is stored) vs. Monday.com AI-added-on (features layered over decade-old architecture).

**PureBrain Hub implication**: This is the most valuable competitive frame for PureBrain Hub's positioning. But Russell stops at "AI-native tools for human teams." PureBrain Hub is the next category: "AI-native infrastructure for AI-operated business." This is not a productivity tool. It is the operating environment for an AI collective.

### What Russell's Piece Misses (The Gap PureBrain Fills)

Russell's Parallax vision assumes humans are still the primary operators — AI assists them, informs them, and reduces friction for them. His feature set (meeting-to-tasks, predictive health, auto-reporting) is informational: surface data to humans faster.

There is no discussion in Russell's piece of:
- AI agents that decide what to do next without human input
- AI-to-AI coordination and handoffs
- Persistent agent memory that compounds across sessions
- Escalation paths designed for AI-to-human handoff (vs. human-to-human)
- 24/7 autonomous operation without human triggers

This is the white space PureBrain Hub occupies. Russell is building a better Monday.com for human teams. We are building the infrastructure for a world where AI teams run the business and humans govern it.

---

## 5. Recommended Feature Roadmap

### Phase 1: Quick Wins (Add to Current React App, No Architecture Changes)

These features can be implemented as frontend additions or small backend changes to the existing Express + sql.js stack.

**1.1 Agent Identity on Posts**
- Add `author_type` field to posts: `human` or `agent`
- Add `agent_name` field: e.g., `content-specialist`, `doc-synthesizer`
- Display agent identity distinctly in PostCard (different avatar style, agent badge)
- Filter bar: "Show me agent posts only" / "Show me Jared posts only"
- **Why now**: Every post in the Hub should be attributable. This is the foundational identity layer.

**1.2 Post Status / State Field**
- Add `status` field to posts: `info`, `completed`, `escalation`, `pending-review`, `acknowledged`
- Color-code posts by status in the feed (green = completed, orange = escalation, grey = info)
- Allow status change via API (so agents can update their own posts' status as work progresses)
- **Why now**: The feed currently treats all posts equally. Status makes the feed operational, not just informational.

**1.3 Escalation Queue View (Fifth Nav Item)**
- Add "Escalations" as a fifth sidebar nav item
- Filters feed to `status: escalation` + `status: pending-review`
- Sorted by recency, unacknowledged first
- Single-click "Acknowledged" button sends acknowledgment and changes status
- **Why now**: This is the most critical missing feature. When agents flag something for Jared, he needs a dedicated place to see it — not buried in the general feed.

**1.4 Filter by Agent Name**
- Extend the existing filter bar to include agent name filters
- Dynamic: generate filter pills from unique `agent_name` values in the DB
- Allow Jared to see "everything content-specialist did today"
- **Why now**: Low complexity, uses existing filter infrastructure.

**1.5 Telegram Notification on Escalation**
- When a post is created with `status: escalation`, automatically fire a Telegram notification to Jared
- Use existing `tools/tg_send.sh` infrastructure
- Include post title, agent name, and link in the notification
- **Why now**: Closes the loop between Hub state and Jared's mobile awareness. No new infrastructure needed.

**1.6 Drive Sync Status: Real Data**
- Dashboard currently shows static "Last sync: just now / Files synced: 24"
- Pull real sync metrics from the GDrive API endpoint
- Display actual last sync timestamp and file count
- **Why now**: Jared already asked about drive sync status before. Static data erodes trust.

**1.7 Top Contributors: Real Data**
- Dashboard shows static leaderboard (Marcus T., Sarah K., etc.)
- Replace with dynamic query: top 5 authors by post count + reaction count in the last 30 days
- **Why now**: Static sample data is embarrassing in an AI-operated system.

---

### Phase 2: Architecture Changes (Requires Backend Work)

These features require schema changes, new backend endpoints, or new infrastructure.

**2.1 Agent Action Log (Audit Trail)**
- New database table: `agent_actions` — `{timestamp, agent_name, action_type, target_id, details, outcome}`
- Action types: `post_created`, `file_uploaded`, `status_changed`, `escalation_triggered`, `task_completed`, `memory_written`
- New API endpoint: `GET /api/agent-actions?agent=&date=&type=`
- New Hub view: "Agent Log" — timestamped activity feed, filterable by agent and date
- **Why this matters**: Currently, Jared can see agent OUTPUTS (posts, files) but not agent ACTIONS. The action log makes AI operation transparent.

**2.2 REST API for All Hub Operations**
- Every Hub action must be callable by agents without UI interaction
- Endpoints needed:
  - `POST /api/posts` — create post (with agent identity fields)
  - `PATCH /api/posts/:id/status` — update post status
  - `POST /api/escalations` — dedicated escalation endpoint
  - `POST /api/agent-actions` — log an agent action
  - `GET /api/posts?agent=&status=&date_from=&date_to=` — query posts with filters
  - `GET /api/dashboard/summary` — stats for dashboard (post count, escalation count, agents active)
- **Why this matters**: Hub currently has API endpoints but agents are not the primary writers. Formalizing the API makes agents first-class Hub citizens.

**2.3 Webhook / Event Subscription**
- When a post status changes to `escalation`, fire an event
- When Jared acknowledges an escalation, fire an event (so the originating agent can continue)
- Simple implementation: webhook URL configured per event type, Hub POSTs to it
- Aether agents subscribe to relevant event types
- **Why this matters**: Agents need to know when their escalation has been reviewed. Currently, there is no feedback loop from Hub state to agent state.

**2.4 Mission / Project Grouping**
- Posts can be associated with a `mission_id`
- A mission has: name, status, owning agent(s), start date, target completion, linked posts
- New Hub view: "Missions" — shows active missions, their status, and all associated posts
- **Why this matters**: Currently, all posts are flat. Multi-step agent missions (e.g., "Trust Gap Blog Campaign") produce many posts over days. Grouping them under a mission makes the operational narrative readable.

**2.5 Fuzzy Search**
- Replace exact-match search with fuzzy matching (Fuse.js client-side, or server-side with SQL LIKE + Levenshtein)
- Search across: title, content, agent_name, tags, department
- One typo should not return zero results
- **Why this matters**: As post volume grows, search becomes the primary navigation tool. Keyword-only search breaks at 100+ posts.

---

### Phase 3: Differentiators (Uniquely AI-Native Features)

These features do not exist in any productivity tool. They define PureBrain Hub's category.

**3.1 Semantic Search (Vector Embeddings)**
- Add `embedding` column to posts table (float array)
- When a post is created, generate embedding via OpenAI Embeddings or local model
- Search queries converted to embeddings and compared via cosine similarity
- "Find everything related to the payment flow" returns relevant posts regardless of exact wording
- **Technical path**: Migrate from sql.js to PostgreSQL + pgvector (as used by Parallax/Russell's recommended architecture)
- **Why this is a differentiator**: Every competing tool with semantic search added it as a layer over keyword search. Hub can make it native from the start.

**3.2 Agent State Dashboard**
- Real-time view of which agents are currently active and what they are working on
- Each active agent shows: current task, time started, last action, estimated completion
- Agents write their state to a Hub endpoint when they begin/end major operations
- **Why this is a differentiator**: No productivity tool surfaces multi-agent operational state. This is Conductor's visibility layer.

**3.3 AI-to-AI Handoff Tracking**
- When Agent A creates a post that triggers Agent B's work, link the posts as a handoff chain
- Handoff chain view: shows the full lineage of a mission from initial input to final output
- Each step shows: which agent, what they did, how long it took, what they passed forward
- **Why this is a differentiator**: The handoff chain is the core operational artifact of a multi-agent collective. No tool in the market models this.

**3.4 Escalation Context Package**
- When an agent escalates, it must package: (1) what was attempted, (2) what blocked progress, (3) what decision Jared needs to make, (4) what will happen if Jared says yes / says no
- Structured escalation form, not just a tagged post
- Jared responds with one of: "Yes / No / More context / Delegate to [agent]"
- Response routes back to the originating agent and logs to audit trail
- **Why this is a differentiator**: Escalation design is the product. Every other tool assumes humans escalate to humans. This models AI-to-human escalation as a first-class workflow.

**3.5 Memory Surface Layer**
- Read-only view of agent memory files from within Hub UI
- Browse by agent: "What has content-specialist learned?"
- Search across all memory files (semantic or fuzzy)
- Allows Jared to audit agent knowledge state without SSH into the server
- **Why this is a differentiator**: No productivity tool exposes the AI's learning state to the human. This is radical transparency about what the AI collective knows and has learned.

---

## 6. Architecture Notes

### Current Stack Assessment

The current React 18 + Vite + Express + sql.js stack is adequate for Phase 1. SQLite via sql.js is in-memory by default, which means data does not persist across server restarts in the serverless Vercel deployment. This is a known limitation.

**For Phase 2**: PostgreSQL migration is recommended. Key reasons:
1. Persistent storage (sql.js in-memory loses data on serverless cold start)
2. pgvector support for Phase 3 semantic search
3. Better query performance for filtered searches across growing post volume
4. Standard ORM support (Prisma, Drizzle) for schema migrations

**Migration path**: Express backend → Vercel serverless function with PostgreSQL (Neon, Supabase, or Railway). Frontend stays identical. API contract stays identical.

### API Design Principles for AI-Native Operation

Based on the Monday.com research and PureBrain's operation patterns:

1. **Every write operation must be API-callable** — no action that requires UI interaction
2. **Agent identity is always required** — `author_type` and `agent_name` on every write
3. **Status is first-class, not a tag** — dedicated `status` field, not a custom tag
4. **Webhook delivery on status transitions** — agents subscribe to state changes, not poll
5. **No rate limiting on agent-facing endpoints** — agents operate continuously; arbitrary caps break workflows

### Event Bus for Agent Coordination

The simplest viable implementation: use the Hub DB as an event log. Agents poll `GET /api/events?since=TIMESTAMP&agent=me` on a short interval. When events arrive (escalation acknowledged, mission status changed, handoff received), agents process them.

This avoids WebSocket complexity and is compatible with serverless deployment. If polling proves too slow, upgrade to Server-Sent Events (SSE) — supported natively by Vercel without additional infrastructure.

### Data Schema Additions (Phase 1)

Minimum schema changes needed for Phase 1:

```sql
-- Add to posts table
ALTER TABLE posts ADD COLUMN author_type TEXT DEFAULT 'human'; -- 'human' | 'agent'
ALTER TABLE posts ADD COLUMN agent_name TEXT;                  -- e.g., 'content-specialist'
ALTER TABLE posts ADD COLUMN status TEXT DEFAULT 'info';        -- 'info' | 'completed' | 'escalation' | 'pending-review' | 'acknowledged'
ALTER TABLE posts ADD COLUMN mission_id TEXT;                  -- groups posts into missions

-- New table: agent_actions
CREATE TABLE IF NOT EXISTS agent_actions (
  id TEXT PRIMARY KEY,
  timestamp TEXT NOT NULL,
  agent_name TEXT NOT NULL,
  action_type TEXT NOT NULL,
  target_id TEXT,
  details TEXT,
  outcome TEXT
);
```

These four additions unlock Phases 1.1 through 1.5 without any schema breaking changes.

### Security Considerations

Current token-based auth is adequate for internal use. For Phase 2 (API-first for agents):

1. Agent tokens should be distinct from human tokens — different auth header prefix, separate token table
2. Agent endpoints should only accept agent tokens (no human UI token can write to agent log)
3. Escalation endpoints should be rate-limited per agent (prevent runaway agents from flooding Jared with escalations)
4. All agent-written content should be sanitized server-side (XSS protection already in place based on security audit memory)

---

## Verification

Research sources confirmed:
- `/home/jared/projects/AI-CIV/aether/exports/research/monday-com-deep-dive.md` — 757 lines, web-researcher, 2026-02-27
- `/home/jared/projects/AI-CIV/aether/exports/research/russell-piece-and-other-tools.md` — 250 lines, web-researcher, 2026-02-27
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_hub/src/App.jsx` — 4 views, token auth, GDrive badge
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_hub/src/components/Dashboard.jsx` — stats grid, feed, sample data confirmed

All feature matrix entries derived from source documents. No features invented or extrapolated beyond research findings.

---

## Memory Written

**Path**: `.claude/memory/agent-learnings/doc-synthesizer/2026-02-27--purebrain-hub-feature-mapping.md`
**Type**: synthesis
**Topic**: PM tool research synthesis to Hub feature roadmap — AI-as-operator lens

---

*Synthesized by doc-synthesizer — 2026-02-27*
