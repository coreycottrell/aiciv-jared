# cto: AI Migration Portal — Architecture Decision Document

**Agent**: cto
**Domain**: Technology Strategy & Vision
**Date**: 2026-02-23
**Version**: 2.0 (Full build-team edition — adds file ownership map and integration plan)

---

## Executive Summary

The AI Migration Portal directly reduces the #1 barrier to PureBrain adoption: switching cost anxiety. This document defines the complete technical architecture for the MVP, with enough precision that 7-10 agents can build simultaneously without file conflicts.

The core architecture recommendation: **extend the existing Node.js/Express backend at `tools/purebrain_hub/`** rather than building new infrastructure. The server already runs behind the Cloudflare Tunnel at `https://api.purebrain.ai`. The existing Cloudflare Worker at `https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages` handles AI conversation and is NOT touched by this build. The portal UI is a standalone self-contained HTML page deployed to WordPress via REST API (matching the existing chatbox and audit page patterns).

---

## Section A: Tech Stack Decisions

### Decision 1: Frontend — Self-Contained HTML Page (No Framework)

**Decision**: Vanilla JS + CSS in a single self-contained HTML file, deployed to WordPress via REST API with `elementor_canvas` template.

**Rationale**:
- This is the established PureBrain deployment pattern (chatbox, audit page, assessment page all use this pattern)
- No build toolchain, no npm on the deployment side
- Works with Elementor CSS scoping rules we already understand
- Agents can work on separate sections of the HTML file without conflicts if ownership is clearly defined

**File**: `exports/migration-portal.html` → deployed to WordPress page `/migration-portal/`

**CSS scoping rule** (mandatory): All CSS must be scoped under `#pb-migration-portal` to avoid WordPress theme overrides. Use `!important` on critical layout and color properties.

---

### Decision 2: ZIP Parsing — Client-Side JSZip via CDN

**Decision**: Parse the ChatGPT and Claude export ZIPs in the browser using JSZip, not on the server.

**Rationale**:
- ChatGPT exports can be 50-80MB. Uploading that file to the server adds latency, encryption overhead, and storage cost.
- JSZip is a mature, well-audited library (11M weekly npm downloads, MIT license). Load via CDN: `https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js`
- The user's conversation data never leaves their browser — it is processed client-side, and only the extracted context profile (a small JSON object) is sent to the server
- This is a meaningful privacy improvement over server-side parsing. "Your raw conversations stay on your device" is a compelling and true claim.
- The pattern extraction (frequency analysis) is simple enough to run in client-side JS — no LLM calls needed for MVP

**What JSZip does in this build**:
1. Accept the ZIP file from the `<input type="file">` element
2. Extract `conversations.json` from within the ZIP
3. Extract `user.json` from within the ZIP (ChatGPT custom instructions)
4. Pass both JSON objects to the local pattern extraction functions
5. The extraction functions run client-side, produce the context profile object
6. Only the context profile JSON is sent to the server via `POST /api/migration/profile`

**What this means for the server**: The server no longer needs to handle ZIP uploads. It only receives and stores the extracted JSON profile. This simplifies the backend considerably.

**Fallback for malformed exports**: If JSZip fails to parse the file (wrong format, corrupted), the UI shows an error: "We couldn't read this file. Make sure you downloaded the full export from ChatGPT Settings > Data Controls > Export Data." No server call is made on failure.

---

### Decision 3: Pattern Extraction — Client-Side JavaScript

**Decision**: Frequency analysis runs in client-side JavaScript. No server-side Python sidecar needed for MVP.

**Rationale**:
- The ChatGPT `conversations.json` is a flat array of conversations, each with a messages array. Counting message frequency by topic is a simple string frequency analysis — no NLP library required.
- For MVP, the extraction algorithm is: tokenize user message content, remove stop words (a standard 200-word list), count term frequencies, return top 5 terms.
- This runs in under 2 seconds for even the largest exports (100K messages).
- Client-side execution means Step 3 starts immediately — there is no server round-trip delay waiting for a job queue.

**MVP extraction algorithm (client-side)**:
```javascript
// Input: conversations array from conversations.json
// Output: { topTopics, conversationCount, dateRange, communicationStyle, customInstructions }

function extractProfile(conversations, userJson) {
  const termFreq = {};
  const STOP_WORDS = new Set([/* 200 common English stop words */]);
  let conversationCount = 0;
  let earliestDate = null;
  let latestDate = null;
  let bulletCount = 0;
  let proseCount = 0;

  for (const convo of conversations) {
    conversationCount++;
    const createTime = convo.create_time;
    if (createTime) {
      if (!earliestDate || createTime < earliestDate) earliestDate = createTime;
      if (!latestDate || createTime > latestDate) latestDate = createTime;
    }
    for (const [, node] of Object.entries(convo.mapping || {})) {
      const msg = node.message;
      if (!msg || msg.author.role !== 'user') continue;
      const content = (msg.content?.parts || []).join(' ').toLowerCase();
      const words = content.split(/\W+/).filter(w => w.length > 3 && !STOP_WORDS.has(w));
      for (const word of words) {
        termFreq[word] = (termFreq[word] || 0) + 1;
      }
      // Detect style preference
      if (content.includes('\n-') || content.includes('\n*') || content.includes('\n1.')) {
        bulletCount++;
      } else {
        proseCount++;
      }
    }
  }

  const topTopics = Object.entries(termFreq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([term]) => term);

  const customInstructions = userJson?.['custom_instructions'] || null;
  const communicationStyle = customInstructions
    ? customInstructions.slice(0, 300)
    : (bulletCount > proseCount ? 'Prefers bullet points and structured responses' : 'Prefers prose responses');

  return {
    topTopics,
    conversationCount,
    dateRange: { start: earliestDate, end: latestDate },
    communicationStyle,
    customInstructions
  };
}
```

---

### Decision 4: Data Storage — API Call to Existing Hub Server

**Decision**: Send the extracted context profile to the Node.js hub server via a single `POST /api/migration/profile` call. Store in sql.js SQLite.

**Rationale**:
- The hub server at `tools/purebrain_hub/server/index.js` is already running and accessible via the Cloudflare Tunnel
- sql.js is adequate for MVP user counts (low double-digits to low hundreds)
- No new infrastructure needed

**What is NOT used**: The Cloudflare Worker at `pure-brain-dashboard-api.purebrain.workers.dev/v1/messages` is the AI conversation endpoint. It is NOT used for migration data storage. This is a deliberate separation — migration context data goes to the persistent hub server, not to the stateless AI Worker.

---

### Decision 5: Cloudflare Worker — Used Only for AI Context Injection

**Decision**: The Cloudflare Worker endpoint (`https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages`) is NOT modified as part of this build. Migration context is injected by the portal UI by reading the stored profile and prepending it to the first chat message.

**How context injection works at MVP**:
1. When the user clicks "Start this task" on Step 4, the portal fetches their migration profile from `GET /api/migration/profile/{user_id}`
2. The portal builds a context prefix string from the profile:
   ```
   [Context from your previous AI tool: You frequently worked on {topTopics}.
   Your preferred style: {communicationStyle}.
   Custom instructions you had previously: {customInstructions}]
   ```
3. This prefix is prepended to the user's first message before sending to the Worker
4. The Worker processes it as a normal message — no Worker code changes required

**Phase 2 note**: In Phase 2, the Worker system prompt can be updated to permanently include the migration context. For MVP, client-side prepending is simpler and equally effective.

---

### Decision 6: Real-Time Progress (Step 3) — Simulated SSE with Timed Events

**Decision**: For MVP, Step 3 uses a client-side timer to animate insight cards with a realistic delay. No server-side SSE needed.

**Rationale**:
- Since extraction happens client-side (Decision 3), we already have all the insight cards generated before Step 3 starts
- "Real-time" from the user's perspective means cards appearing one at a time with pauses — not genuinely async
- A 600ms setTimeout between cards matches the emotional experience the spec describes without needing a streaming connection
- This eliminates the SSE endpoint entirely from the MVP backend

**Implementation**:
```javascript
async function runStep3Animation(insightCards, progressCallback) {
  const totalCards = insightCards.length;
  for (let i = 0; i < totalCards; i++) {
    await sleep(600 + Math.random() * 400); // 600-1000ms between cards
    progressCallback({
      progress: Math.round(((i + 1) / totalCards) * 100),
      card: insightCards[i]
    });
  }
}
```

**Backend SSE (for Phase 2)**: When OAuth integrations are added (Notion, HubSpot), the server must actually fetch external data. At that point, SSE via `text/event-stream` becomes necessary. Build it then, not now.

---

### Full Tech Stack Summary

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | Vanilla JS/CSS HTML page in WordPress | Matches existing chatbox pattern |
| ZIP parsing | JSZip 3.10.1 via CDN (client-side) | Raw data never leaves browser, faster UX |
| Pattern extraction | Client-side JavaScript | Fast enough for MVP, no server round-trip |
| Real-time Step 3 | Client-side timer simulation | All data available immediately after extraction |
| Profile storage | POST to Node.js hub server → sql.js | Existing infrastructure, no new services |
| AI context injection | Client-side prepend to first message | Worker not modified |
| AI conversations | Cloudflare Worker (existing, unchanged) | Stateless AI endpoint stays separate |
| Infrastructure | Existing Cloudflare Tunnel at api.purebrain.ai | No new configuration |

---

## Section B: MVP Scope Lock

**The MVP scope is locked. Do not expand it during this build.**

### In Scope for MVP

- Step 1: ChatGPT ZIP upload + Claude ZIP upload + Midjourney style text form + CSV fallback
- Step 2: Review what was found — data summary with remove toggles
- Step 3: Animated insight cards (client-side timed animation)
- Step 4: 3 personalized task cards with pre-loaded chat prompts
- Migration Complete badge stored in user profile and shown in dashboard
- Profile saved to hub server database
- AI context injection on first conversation (client-side prepend)

### Out of Scope for MVP (Hard Boundary)

- Notion OAuth
- HubSpot OAuth
- Canva OAuth
- Gemini/Google OAuth
- Server-side SSE streaming (not needed with client-side extraction)
- LLM-powered extraction (frequency analysis is sufficient to prove the concept)
- Migration Summary PDF
- Real-time processing status websocket

**Scope rationale**: ChatGPT file upload covers the majority of PureBrain's target switchers. OAuth adds 4-6 weeks of security review per provider. Client-side processing eliminates the backend complexity almost entirely. Prove the "Your history becomes PureBrain's foundation" moment with file upload first.

---

## Section C: File Structure and Agent Ownership

This section defines exactly what files each developer builds. Files are assigned to specific agents. No two agents own the same file. Interface contracts are defined at the boundary between files.

### File Map

```
exports/
  migration-portal.html              ← PORTAL UI (owned by: full-stack-developer)
  migration-portal-parser.js         ← ZIP PARSING + EXTRACTION (owned by: ai-ml-engineer)
  migration-portal-step3-animation.js ← STEP 3 ANIMATION (owned by: full-stack-developer)

tools/purebrain_hub/server/
  index.js                           ← EXISTING (do not touch existing routes)
  routes/migration.js                ← NEW MIGRATION ROUTES (owned by: full-stack-developer)
  db/migration-schema.sql            ← NEW DB SCHEMA (owned by: full-stack-developer)
  db/migrate.js                      ← DB MIGRATION RUNNER (owned by: full-stack-developer)

tools/purebrain_hub/public/
  [no new files — portal is served from WordPress, not from hub server]
```

### File Ownership Details

#### `exports/migration-portal-parser.js` — ai-ml-engineer owns this

This file contains ONLY:
- `extractChatGPTProfile(conversations, userJson)` → returns context profile object
- `extractClaudeProfile(conversations)` → returns context profile object
- `generateInsightCards(profile)` → returns array of insight card objects
- `generateSuggestedTasks(profile, exodusData)` → returns array of task card objects
- `STOP_WORDS` constant set
- JSZip loading helper: `loadZipFile(file)` → returns `{ conversations, userJson }`

**This file has zero DOM references.** It is pure logic. It exports its functions to `window.MigrationParser` namespace. It can be developed and unit tested independently.

**Interface contract (output of extractProfile)**:
```javascript
{
  topTopics: string[],           // max 5 strings
  conversationCount: number,
  dateRange: { start: number|null, end: number|null }, // Unix timestamps
  communicationStyle: string,    // freeform description
  customInstructions: string|null,
  preferredAnswerFormat: 'bullet' | 'prose' | 'mixed',
  source: 'chatgpt' | 'claude' | 'csv' | 'manual'
}
```

**Interface contract (output of generateInsightCards)**:
```javascript
[{
  cardType: 'topic' | 'style' | 'custom_instructions',
  title: string,   // e.g. "You asked about market analysis 23 times."
  body: string     // e.g. "We've flagged this as a core use pattern."
}]
```

**Interface contract (output of generateSuggestedTasks)**:
```javascript
[{
  icon: 'chart' | 'pen' | 'database' | 'memory' | 'code',
  title: string,
  description: string,
  preLoadedPrompt: string,
  sourceSignal: 'top_topic' | 'custom_instructions' | 'frustration' | 'use_case'
}]
```

---

#### `exports/migration-portal.html` — full-stack-developer owns this (except the parsing section)

This file contains:
- The complete HTML structure and inline CSS for all 4 steps
- The wizard navigation logic (step progression, back button)
- File upload event handlers (calls `window.MigrationParser.loadZipFile()`)
- Step 2 remove toggle logic
- Step 3 animation controller (calls `window.MigrationAnimator.run()`)
- Step 4 task card rendering and "Start this task" pre-loaded prompt injection
- The `POST /api/migration/profile` call to save the profile to the hub server
- Migration Complete badge rendering
- `<script src="migration-portal-parser.js">` tag to load the parser
- `<script src="migration-portal-step3-animation.js">` tag to load the animator

**CSS requirement**: All CSS scoped under `#pb-migration-portal`. Body background set via `body.page { background-color: #080a12 !important; }`.

**PureBrain brand variables**:
```css
#pb-migration-portal {
  --pb-bg: #080a12;
  --pb-blue: #2a93c1;
  --pb-orange: #f1420b;
  --pb-surface: rgba(15, 15, 20, 0.98);
  --pb-border: rgba(255, 255, 255, 0.08);
  --pb-text: rgba(255, 255, 255, 0.9);
  --pb-muted: rgba(255, 255, 255, 0.45);
}
```

---

#### `exports/migration-portal-step3-animation.js` — full-stack-developer owns this

This file contains ONLY the Step 3 animation controller:
- `window.MigrationAnimator.run(insightCards, domTargets, onComplete)`
- Timed card appearance logic
- Progress bar percentage updates
- Profile checklist tick animation
- Exports to `window.MigrationAnimator` namespace

**Zero DOM structure assumptions** — receives DOM target elements as parameters from the portal HTML. Decoupled from the HTML structure so the UI can change without touching this file.

---

#### `tools/purebrain_hub/server/routes/migration.js` — full-stack-developer owns this

This file contains the Express router for migration endpoints.
It is registered in `index.js` as: `app.use('/api/migration', require('./routes/migration'))`.
The `index.js` file itself is NOT modified beyond adding this one line.

Endpoints in this file:
```
POST   /api/migration/profile         ← Save extracted profile from client
GET    /api/migration/profile/:userId ← Retrieve profile (for portal reload, context injection)
DELETE /api/migration/profile/:userId ← GDPR erasure
GET    /api/migration/badge/:userId   ← Dashboard badge data
POST   /api/migration/complete        ← Mark migration complete, return badge data
```

**Auth pattern**: Follows the same `Authorization: Bearer {token}` pattern as existing hub routes. User ID in the request body must match the token's user ID — never trust a user_id parameter alone.

---

#### `tools/purebrain_hub/server/db/migration-schema.sql` — full-stack-developer owns this

Contains only the `CREATE TABLE IF NOT EXISTS` statements for migration tables. Does not modify existing tables. Run by `migrate.js` at server startup.

---

#### `tools/purebrain_hub/server/db/migrate.js` — full-stack-developer owns this

Reads `migration-schema.sql` and executes it against the sql.js database. Called from `index.js` at startup: `require('./db/migrate')(db)`. One addition to `index.js`.

---

### Files That Must NOT Be Modified

| File | Reason |
|---|---|
| `tools/purebrain_hub/server/index.js` | Two additions only: require migration router + require migrate.js at startup. No structural changes. |
| Any existing hub routes | Not touched. Migration is additive. |
| `exports/pay-test-script-chat-flow.js` | Not in scope for this build. Chatbox is a separate system. |
| Cloudflare Worker code | Not in scope. Worker unchanged. |
| Any WordPress plugin files | Not in scope. Portal is a new WordPress page, not a plugin change. |

---

## Section D: Database Schema

Tables added to `tools/purebrain_hub/hub.db` via `migration-schema.sql`.

### user_migration_profiles

```sql
CREATE TABLE IF NOT EXISTS user_migration_profiles (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL UNIQUE,
  migration_status TEXT NOT NULL DEFAULT 'not_started',
    -- 'not_started' | 'in_progress' | 'complete' | 'abandoned'
  competitor TEXT,
    -- 'chatgpt' | 'claude' | 'other'
  exodus_data TEXT DEFAULT '{}',
    -- JSON from Brevo passthrough (quiz answers)
  conversation_count INTEGER DEFAULT 0,
  date_range_start TEXT,
  date_range_end TEXT,
  top_topics TEXT DEFAULT '[]',
    -- JSON array, max 5 strings
  communication_style TEXT,
  preferred_answer_format TEXT DEFAULT 'mixed',
    -- 'bullet' | 'prose' | 'mixed'
  custom_instructions_raw TEXT,
  midjourney_style TEXT,
  migration_config TEXT DEFAULT '{}',
    -- JSON: which data categories user confirmed/removed
  started_at TEXT,
  completed_at TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
  updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_migration_user_id ON user_migration_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_migration_status ON user_migration_profiles(migration_status);
```

### migration_insight_cards

```sql
CREATE TABLE IF NOT EXISTS migration_insight_cards (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  card_type TEXT NOT NULL,
    -- 'topic' | 'style' | 'custom_instructions'
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  display_order INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_cards_user_id ON migration_insight_cards(user_id);
```

### migration_suggested_tasks

```sql
CREATE TABLE IF NOT EXISTS migration_suggested_tasks (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  icon TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  pre_loaded_prompt TEXT NOT NULL,
  source_signal TEXT,
  display_order INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON migration_suggested_tasks(user_id);
```

### Phase 2 Only: migration_oauth_tokens

```sql
-- DO NOT CREATE THIS TABLE IN MVP
-- Included here for planning only

CREATE TABLE IF NOT EXISTS migration_oauth_tokens (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  access_token_enc TEXT NOT NULL,   -- AES-256-GCM encrypted
  refresh_token_enc TEXT,
  token_iv TEXT NOT NULL,
  token_tag TEXT NOT NULL,
  scopes TEXT NOT NULL DEFAULT '[]',
  expires_at TEXT,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
  revoked_at TEXT,
  UNIQUE(user_id, provider)
);
```

---

## Section E: API Endpoints

### Endpoints in `routes/migration.js`

```
POST   /api/migration/profile
  Body: {
    userId: string,
    competitor: string,
    conversationCount: number,
    dateRangeStart: string|null,
    dateRangeEnd: string|null,
    topTopics: string[],
    communicationStyle: string,
    preferredAnswerFormat: string,
    customInstructionsRaw: string|null,
    midjourneyStyle: string|null,
    insightCards: [{cardType, title, body, displayOrder}],
    suggestedTasks: [{icon, title, description, preLoadedPrompt, sourceSignal, displayOrder}]
  }
  Response: { success: true, profileId: string }
  Notes: Creates or updates the user_migration_profiles row.
         Replaces insight cards and tasks for this user.
         Sets migration_status to 'in_progress'.

GET    /api/migration/profile/:userId
  Response: { migrationStatus, competitor, conversationCount, topTopics,
              communicationStyle, customInstructionsRaw, insightCards, suggestedTasks }
  Notes: Returns full profile for portal reload or context injection.

GET    /api/migration/badge/:userId
  Response: { status, conversationCount, topTopics, completedAt, competitor }
  Notes: Lightweight endpoint for dashboard badge rendering.

POST   /api/migration/complete
  Body: { userId: string }
  Response: { success: true, badge: { conversationCount, topTopics, completedAt, competitor } }
  Notes: Sets migration_status to 'complete', records completed_at.

DELETE /api/migration/profile/:userId
  Response: { success: true }
  Notes: Deletes all rows in user_migration_profiles, migration_insight_cards,
         migration_suggested_tasks for this user.
         Sets migration_status to 'not_started'.
         GDPR Right to Erasure compliance.
```

### API NOT Used for Migration

The Cloudflare Worker endpoint `https://pure-brain-dashboard-api.purebrain.workers.dev/v1/messages` is the AI conversation API. Migration data is NOT sent here. This endpoint is only called when the user sends a chat message. The migration context is injected by the portal UI as a prefix to the user's first message payload — the Worker sees it as a normal user message.

---

## Section F: Integration Plan

### How the Pieces Connect

```
BROWSER (user's machine)
  |
  | User uploads conversations.zip
  |
  ↓
migration-portal-parser.js (JSZip + client-side extraction)
  |
  | Produces: profile object + insight cards + suggested tasks
  |
  ↓
migration-portal.html (Step 3 animation → Step 4 display)
  |
  | POST /api/migration/profile
  |
  ↓
api.purebrain.ai (Cloudflare Tunnel → Node.js hub server)
  |
  | Writes to hub.db via routes/migration.js
  |
  ↓
hub.db (sql.js SQLite)
  user_migration_profiles
  migration_insight_cards
  migration_suggested_tasks

---

FIRST CONVERSATION
  |
  | User clicks "Start this task" on Step 4
  |
  ↓
migration-portal.html
  |
  | 1. Reads pre_loaded_prompt from stored task card
  | 2. Reads top_topics + communication_style + custom_instructions_raw from profile
  | 3. Builds context prefix string
  | 4. Calls Cloudflare Worker with:
  |    { message: "[Context prefix]\n\n[pre_loaded_prompt]", ... }
  |
  ↓
pure-brain-dashboard-api.purebrain.workers.dev/v1/messages
  |
  | (existing Worker, unchanged)
  |
  ↓
Claude API response to user
```

### Integration with Exodus Landing Page (Sprint 4)

The exodus page (existing `/switching-from-chatgpt/` etc.) collects quiz answers and stores them in Brevo as contact attributes. On first portal login:

1. Portal calls `GET /api/migration/profile/{userId}`
2. If `exodus_data` is empty, portal calls Brevo API: `GET /v3/contacts/{email}` using the user's email
3. Brevo returns contact record with attributes: `competitor`, `primary_use_cases`, `had_custom_config`, `main_frustration`
4. Portal stores these in `user_migration_profiles.exodus_data` via `POST /api/migration/profile` update
5. Task generator (`generateSuggestedTasks`) reads `exodus_data.primary_use_cases` and `exodus_data.main_frustration` to personalize Step 4 tasks

**Who builds this**: The exodus page quiz additions and Brevo attribute setup are separate from the core portal build. This is Sprint 4 work. The portal must function without exodus data — it degrades gracefully to topic-based tasks if exodus data is unavailable.

### Integration with Portal Dashboard (existing)

The portal dashboard (the page users land on after login) needs two changes:

1. **Migration banner** — shown on first login if `migration_status != 'complete'`. Reads from `GET /api/migration/badge/{userId}`. This is a new section in the existing dashboard HTML.

2. **Migration Complete badge** — shown permanently after completion. Reads same endpoint, shows different state when `migration_status == 'complete'`.

**Who builds this**: full-stack-developer, in the same portal HTML file. The badge is a conditional render in the dashboard section, not a separate file.

---

## Section G: Security Architecture

### Client-Side Processing Security Model

Since ZIP processing happens in the browser:
- Raw conversation data never travels over the network — only the extracted profile JSON does
- The profile JSON contains topic keywords and style descriptions — no personally identifiable conversation content
- This is a privacy improvement, not just a technical shortcut

### API Security

Every endpoint in `routes/migration.js` must:
1. Validate the `Authorization: Bearer {token}` header (same pattern as existing hub auth)
2. Confirm the `userId` in the request body/params matches the token's user ID
3. Never allow cross-user data access (user A cannot read user B's profile)

### File Handling (Client-Side JSZip)

JSZip runs entirely in the browser sandbox. Risks:
- **Malicious ZIP**: JSZip has well-known protections against zip bombs. The parser should set a max uncompressed size limit: reject if `conversations.json` exceeds 200MB uncompressed.
- **XSS via imported content**: Custom instructions are stored verbatim but always rendered via `textContent` or explicit escaping, never via `innerHTML` insertion.

### GDPR Compliance

**Consent gate**: Before Step 1, display and require acknowledgment of: "I consent to PureBrain processing my imported data to personalize my experience. This data is used only for your individual account. It is not used for AI training and is not shared with third parties."

**Right to Erasure**: `DELETE /api/migration/profile/{userId}` erases all migration data from the database.

**Data minimization**: Only extracted context (topic keywords, style preference, custom instructions) is stored. Raw conversation content is never stored — it stays in the user's browser memory only for the duration of the Step 1-3 session.

---

## Section H: Build Order

### Sprint 1: Parser (Days 1-3)

**Owner**: ai-ml-engineer

Deliverable: `exports/migration-portal-parser.js` — fully working, fully tested

Tasks:
1. `loadZipFile(file)` — JSZip wrapper, extracts `conversations.json` and `user.json`
2. `extractChatGPTProfile(conversations, userJson)` — returns profile object matching interface contract
3. `extractClaudeProfile(conversations)` — returns profile object (Claude export schema differs slightly)
4. `generateInsightCards(profile)` — returns array of insight card objects
5. `generateSuggestedTasks(profile, exodusData)` — returns array of task card objects (exodusData can be null)
6. Unit tests: run against a sample ChatGPT export to verify correctness

**Done when**: Can be loaded in a browser console, run against a real ChatGPT export ZIP, and return a valid profile object with correct topic counts and insight cards.

---

### Sprint 2: Backend (Days 2-4, runs parallel with Sprint 1)

**Owner**: full-stack-developer (backend focus)

Deliverable: Working migration API endpoints in hub server

Tasks:
1. `db/migration-schema.sql` — write all CREATE TABLE statements
2. `db/migrate.js` — schema migration runner
3. Add two lines to `index.js`: `require('./db/migrate')(db)` and `app.use('/api/migration', require('./routes/migration'))`
4. `routes/migration.js` — implement all 5 endpoints
5. Test with curl: POST a sample profile, GET it back, verify it round-trips correctly

**Done when**: `curl -X POST https://api.purebrain.ai/api/migration/profile` with a sample profile payload returns `{ success: true, profileId: "..." }` and the data can be retrieved by GET.

---

### Sprint 3: Portal UI Steps 1-3 (Days 4-8)

**Owner**: full-stack-developer (frontend focus) + full-stack-developer instance 2 (Step 3 animator)

Tasks (primary):
1. Portal HTML shell: dark theme, `#pb-migration-portal` scope, PureBrain design variables, 4-step wizard framework, progress dots
2. Step 1 UI: file upload card (ChatGPT, Claude, drag-and-drop), manual style text form, "Continue with what I have" button, calls `window.MigrationParser.loadZipFile()`
3. Step 2 UI: data summary display (conversation count, date range, custom instructions preview), remove toggles, GDPR consent note, "Start Import" CTA
4. Step 3 UI: animated orb (PureBrain orb, CSS animation, pulsing state), progress bar container, insight card container, profile checklist
5. Deploy to WordPress as password-protected page for testing

Tasks (Step 3 animator, can run in parallel):
1. `exports/migration-portal-step3-animation.js` — `window.MigrationAnimator.run()` with timed card appearance

**Done when**: Upload a ChatGPT ZIP, see the Step 2 data summary populated from the extracted data, click "Start Import", see insight cards animate in sequentially on Step 3.

---

### Sprint 4: Steps 4 and Context Integration (Days 9-12)

**Owner**: full-stack-developer

Tasks:
1. Step 4 UI: task cards with icons (use SVG icons inline, no image dependencies), specific numbers from import, pre-loaded prompt links into chat
2. "Start this task" → context injection → Cloudflare Worker call
3. Migration Complete badge in dashboard
4. `POST /api/migration/complete` call on "Go to my PureBrain" button click

**Done when**: End-to-end flow works. Upload ZIP → view insights → view tasks → click "Start this task" → chat opens with relevant pre-loaded context → first AI response references the user's history.

---

### Sprint 5: Exodus Page + Brevo (Days 13-16)

**Owner**: full-stack-developer

Tasks:
1. Add 4 questions to exodus page quiz flows (Questions A-D from spec Section 2)
2. Update Brevo contact attributes schema: add `competitor`, `primary_use_cases`, `had_custom_config`, `main_frustration`
3. Portal login flow: look up user email in Brevo, pull exodus attributes, populate `exodus_data` in migration profile
4. Update `generateSuggestedTasks()` in parser to use exodus data when available

---

### Sprint 6: Security Review and QA (Days 17-22)

**Owner**: security-engineer-tech (security) + qa-engineer (QA)

Security review tasks:
1. Verify cross-user data isolation on all API endpoints
2. Verify GDPR consent gate is present and required (not bypassable)
3. Verify Right to Erasure endpoint works completely
4. Review JSZip usage for zip bomb vulnerability
5. Verify custom instructions are always rendered escaped (no XSS via imported content)
6. Verify auth token validation on all migration endpoints

QA tasks:
1. Full end-to-end flow with real ChatGPT export ZIP
2. Full end-to-end flow with real Claude export ZIP
3. Step skip flows (skip each step, verify graceful degradation)
4. Large file handling (request a large export from a heavy ChatGPT user if available)
5. Mobile layout: 375px, 390px, 768px
6. GDPR consent gate: verify it cannot be bypassed to reach Step 1
7. Context injection: verify first chat message contains the profile context prefix

---

## Section I: Risk Assessment

### Risk 1: ChatGPT Export Schema Changes
**Probability**: Medium (OpenAI has changed this format before)
**Impact**: High — parser breaks silently
**Mitigation**: The parser validates expected fields before processing. If `conversations.json` does not contain the expected `mapping` structure, return a clear user-facing error. Store one known-good sample export in the test fixtures. When schema validation fails, fail loudly, not silently.

### Risk 2: JSZip Size Limits
**Probability**: Medium (heavy ChatGPT users have large exports)
**Impact**: Low — browser may slow during parsing of very large files
**Mitigation**: Add an uncompressed size check after JSZip reads the file. If `conversations.json` exceeds 200MB uncompressed, display: "Your export is very large. Processing may take a minute." Cap the extraction at 50,000 conversations to prevent browser freezing — the top topics extracted from 50K convos are as useful as from 200K.

### Risk 3: The Emotional Promise vs. Technical Reality
**Probability**: Medium
**Impact**: High — this is the core product risk
**Mitigation**: Frequency analysis of topic keywords is not the same as understanding a user. The insight cards will show real numbers ("23 conversations about market analysis") but the AI partner's first response quality depends entirely on how the context prefix is written. Sprint 4 item 2 (context injection) must be tested qualitatively, not just technically. Test with at least 3 real ChatGPT exports from actual users before launch. The risk is overselling. Underpromise slightly in copy and let the experience exceed expectations.

### Risk 4: Brevo Rate Limits on Exodus Data Lookup
**Probability**: Low
**Impact**: Low — exodus data is a nice-to-have enhancement, not required
**Mitigation**: The Brevo lookup happens on first portal login. If the API call fails or returns no data, the portal works without exodus data — tasks are generated from the ZIP extraction alone. Fail gracefully, never block the user on a Brevo API failure.

### Risk 5: sql.js Performance at Scale
**Probability**: Low at current user count
**Impact**: Medium if PureBrain scales to 50+ concurrent users
**Mitigation**: sql.js is fine for MVP. If concurrent users exceed 50, migrate to `better-sqlite3` (same SQL, native binding, 10x faster writes). Flag this as a scale trigger but do not build it now.

### Risk 6: XSS via Custom Instructions
**Probability**: Low
**Impact**: High — custom instructions are user-supplied text that could contain script injection attempts
**Mitigation**: All display of custom instructions must use `textContent` or explicit HTML escaping, never `innerHTML` with raw user data. ai-ml-engineer must follow this rule in `generateInsightCards()` when building card content from `customInstructions`. full-stack-developer must follow this rule in the portal HTML when rendering card content.

### Risk 7: GDPR Exposure via Exodus Data
**Probability**: Low
**Impact**: High for EU users
**Mitigation**: Ensure the exodus page and portal consent language explicitly covers Brevo storage of quiz answers. Legal review before the exodus page quiz additions go live (Sprint 5). This is a legal question, not a technical one — escalate to Jared before Sprint 5.

---

## Section J: Agent Delegation Map

For the conductor orchestrating this build:

| Agent | Files Owned | Sprint |
|---|---|---|
| ai-ml-engineer | `exports/migration-portal-parser.js` | Sprint 1 |
| full-stack-developer (backend) | `routes/migration.js`, `db/migration-schema.sql`, `db/migrate.js` | Sprint 2 |
| full-stack-developer (frontend-portal) | `exports/migration-portal.html` | Sprint 3 |
| full-stack-developer (animator) | `exports/migration-portal-step3-animation.js` | Sprint 3 (parallel) |
| full-stack-developer (integration) | Steps 4 + context injection + badge | Sprint 4 |
| full-stack-developer (exodus) | Exodus page questions + Brevo | Sprint 5 |
| security-engineer-tech | Security review | Sprint 6 |
| qa-engineer | End-to-end QA | Sprint 6 |

**Sprints 1 and 2 run fully in parallel** — parser development and backend API development have no shared files and only depend on the interface contracts defined in Section C.

**Sprint 3 runs partially in parallel** — the Step 3 animator (`migration-portal-step3-animation.js`) can be built independently while the main portal HTML is being built, as long as the `window.MigrationAnimator` interface contract is respected.

**Sprints 4, 5, 6 are sequential** — each depends on the prior sprint's output being stable.

---

## Verification

This document was written after reading:
- `docs/from-telegram/ai-migration-portal-spec.md` — complete feature spec (read in full)
- `exports/chatbox-revamp-architecture-spec.md` — prior CTO architecture (existing deployment patterns)
- `.claude/memory/agent-learnings/cto/2026-02-23--migration-portal-architecture.md` — prior architecture memory
- `.claude/memory/agent-learnings/cto/2026-02-21--engineering-pipeline-full-team-architecture.md` — engineering pipeline patterns

Prior architecture doc (version 1.0) existed and was superseded by this document. Key changes from v1.0:
- **ZIP parsing moved to client-side JSZip** (eliminates Python sidecar, eliminates server-side file handling, improves privacy posture)
- **SSE replaced by client-side timer simulation** (extraction is synchronous with client-side approach)
- **File structure section added** (agent ownership map, interface contracts)
- **Integration plan section added** (how pieces connect, how Cloudflare Worker is used)

## Memory Written

Path: `.claude/memory/agent-learnings/cto/2026-02-23--migration-portal-architecture-v2.md`
Type: synthesis
Topic: AI Migration Portal — v2 architecture with client-side JSZip, file ownership map, integration plan

Key decision changes from v1:
- ZIP parsing: Python sidecar → JSZip (client-side). Raw data never leaves browser.
- SSE: server-side streaming → client-side timed simulation. Simpler, equally effective for MVP.
- File structure: 3 JS files with clear ownership. No file conflicts possible.
- Integration: Cloudflare Worker untouched. Context injected client-side as message prefix.

---

**END OF DOCUMENT**

**Handoff to**:
- ai-ml-engineer → build `exports/migration-portal-parser.js` (Sprint 1)
- full-stack-developer → build backend routes (Sprint 2) in parallel
- security-engineer-tech → Sprint 6 security gate
- qa-engineer → Sprint 6 QA gate

**Pre-build required**: Jared confirmation on MVP scope boundaries before Sprint 1 begins.
