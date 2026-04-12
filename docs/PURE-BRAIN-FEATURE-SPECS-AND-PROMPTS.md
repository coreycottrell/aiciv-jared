# Pure Brain AI - Feature Specs & Claude Code Prompts

**Date**: 2026-02-05
**Purpose**: Compiled ChatGPT competitive analysis with implementation prompts

---

## Quick Navigation

1. [Settings](#1-settings)
2. [Projects](#2-projects)
3. [Canvas](#3-canvas)
4. [Search](#4-search-highlight-and-jump)
5. [BRAINS (Custom GPTs)](#5-brains-custom-gpts)

---

## 1. SETTINGS

### Feature Summary

ChatGPT has 12 settings categories. Most important for MVP:

| Category | Priority | Description |
|----------|----------|-------------|
| Theme | P0 | Light/Dark/System |
| Custom Instructions | P0 | What to know + How to respond |
| Memory | P1 | Remember facts across conversations |
| Data Controls | P0 | Training opt-out, export, delete |
| Model Selection | P0 | Choose default AI model |
| Keyboard Shortcuts | P1 | Ctrl+K search, etc. |
| Subscription/Billing | P0 | Plan management |

### Full Research Doc

`/home/jared/projects/AI-CIV/aether/docs/chatgpt-settings-breakdown.md`

### Claude Code Prompt

```
I need to implement a Settings system for our AI chat platform (Pure Brain AI).

Create a comprehensive settings architecture with these requirements:

1. ACCOUNT SETTINGS
   - Profile (name, email, avatar)
   - Authentication (password change, 2FA)
   - Account deletion with confirmation

2. PERSONALIZATION
   - Custom Instructions with two fields:
     a) "What should Pure Brain know about you?" (1500 char limit)
     b) "How should Pure Brain respond?" (1500 char limit)
   - Memory system: toggle on/off, view memories, delete individual memories
   - Default response format preferences

3. APPEARANCE
   - Theme: Light, Dark, System (follow OS)
   - Use CSS variables for theming
   - Persist preference to localStorage + user account

4. DATA CONTROLS
   - Toggle: "Use my conversations for training" (default OFF)
   - Export all data (JSON format)
   - Delete all conversations
   - Manage shared links

5. MODEL SELECTION
   - Default model picker (from available models)
   - Remember last used model per session

6. KEYBOARD SHORTCUTS
   - Display all shortcuts in a modal
   - Shortcuts: Ctrl+K (search), Enter (send), Shift+Enter (newline)

7. NOTIFICATIONS
   - Email notification preferences
   - Push notification preferences (if mobile)

Create the settings UI as a modal with sidebar navigation. Use React, TypeScript, and Tailwind CSS. Include the data models/interfaces and API endpoints needed.

Brand colors: #f1420b (orange), #ed6626, #2a93c1 (blue), #3a60ab
Fonts: Oswald (headings), Plus Jakarta Sans (body)
```

---

## 2. PROJECTS

### Feature Summary

Projects organize conversations, files, and custom instructions into containers.

| Feature | ChatGPT | Our Opportunity |
|---------|---------|-----------------|
| Creation | Simple folder + name | Same + templates |
| Files | Scoped to project | Same + cloud sync |
| Instructions | Per-project override | Same |
| Collaboration | NO (single user) | YES - Add sharing! |
| Platforms | Web + Windows only | All platforms |

### Key Competitive Gaps to Exploit

1. **No collaboration** - ChatGPT Projects are single-user only
2. **No cloud storage** - Can't connect Google Drive/Dropbox
3. **Model locked** - GPT-4o only, no switching
4. **No export/import** - Can't share project templates

### Full Research Doc

`/home/jared/projects/AI-CIV/aether/docs/competitive-analysis/CHATGPT-PROJECTS-FEATURE-BREAKDOWN.md`

### Claude Code Prompt

```
I need to implement a Projects feature for our AI chat platform (Pure Brain AI).

Projects are containers that organize related conversations, files, and custom instructions.

Requirements:

1. PROJECT CREATION
   - Create project with name and color
   - Color picker with 8-10 preset colors
   - Projects appear in left sidebar under "Projects" section
   - Collapsible project list

2. FILE MANAGEMENT
   - Upload files to specific projects (not global)
   - Supported formats: PDF, DOCX, TXT, MD, CSV, JSON, code files
   - File list view with name, size, upload date, delete button
   - Files automatically included in project conversation context
   - Drag-and-drop upload
   - Max 20 files per project, 50MB per file

3. CONVERSATION ORGANIZATION
   - "New chat in this project" button
   - Move existing chats to project (context menu)
   - Project-scoped conversation list
   - Search within project conversations

4. CUSTOM INSTRUCTIONS
   - Per-project instructions field (2000 char limit)
   - Project instructions OVERRIDE account-level instructions
   - Clear indicator that project instructions are active

5. SHARING & COLLABORATION (Our differentiator!)
   - Invite collaborators by email
   - Permission levels: Owner, Editor, Viewer
   - Activity log: who added what
   - Project templates: export/import configs

6. DATA MODEL (PostgreSQL)
   - projects: id, user_id, name, color, instructions, created_at
   - project_files: id, project_id, filename, file_path, size, mime_type
   - project_collaborators: project_id, user_id, role, invited_at
   - Modify chats table: add optional project_id foreign key

7. API ENDPOINTS
   - POST /projects (create)
   - GET /projects (list)
   - PATCH /projects/:id (update)
   - DELETE /projects/:id
   - POST /projects/:id/files (upload)
   - POST /chats/:id/move (move chat to project)

Create the UI components with React, TypeScript, and Tailwind CSS. Include proper error handling and loading states.

Brand colors: #f1420b (orange), #2a93c1 (blue)
```

---

## 3. CANVAS

### Feature Summary

Canvas is a split-screen collaborative editor for documents and code.

| Mode | AI Actions Available |
|------|---------------------|
| Document | Suggest edits, Adjust length, Reading level, Polish, Add emojis |
| Code | Review, Add comments, Fix bugs, Port language, Add tests, Optimize |

### Key Features

1. **Auto-triggering** - Opens when AI detects writing/coding task
2. **Split-screen** - Chat left, Canvas right (resizable)
3. **Version control** - Navigate through edit history
4. **Selection actions** - Select text, get contextual AI menu
5. **Export** - Download as .md, .txt, or code files

### Full Research Doc

`/home/jared/projects/AI-CIV/aether/docs/chatgpt-canvas-research/CHATGPT-CANVAS-FEATURE-BREAKDOWN.md`

### Claude Code Prompt

```
I need to implement a Canvas feature for our AI chat platform (Pure Brain AI).

Canvas is a collaborative editing interface where users and AI can work on documents/code together.

Requirements:

1. LAYOUT
   - Split-screen: chat panel (left) + Canvas panel (right)
   - Resizable divider between panels
   - Full-width Canvas mode (hide chat)
   - Close button to return to chat-only
   - Smooth slide-in animation when Canvas opens

2. ACTIVATION
   - Auto-trigger on writing tasks ("write a blog post", "draft an email")
   - Auto-trigger on coding tasks ("write a function", "create component")
   - Manual trigger: "Open in Canvas" button on code blocks/text responses
   - Heuristic: content > 500 chars + structured (headers/code)

3. DOCUMENT MODE
   - Rich text editor (use TipTap or Slate.js)
   - Markdown rendering and source toggle
   - Toolbar: Bold, Italic, Headers, Lists, Code blocks, Links
   - AI Actions menu:
     - Suggest edits (inline suggestions)
     - Adjust length (shorter/longer)
     - Reading level (simple/advanced)
     - Polish (grammar, tone)
     - Add emojis
   - Selection-based AI: select text -> floating menu appears

4. CODE MODE
   - Code editor with syntax highlighting (use Monaco or CodeMirror)
   - Language detection + manual language selector
   - Line numbers, bracket matching
   - AI Actions menu:
     - Review code (find bugs)
     - Add comments
     - Fix bugs
     - Port to language (dropdown)
     - Add tests
     - Optimize performance

5. COLLABORATIVE EDITING
   - AI suggestions shown inline with different color
   - Accept/Reject buttons per suggestion
   - Accept All / Reject All options
   - User edits preserved unless AI asked to change

6. VERSION CONTROL
   - Each AI edit creates new version
   - Version counter in footer: "Version 3/7"
   - Previous/Next navigation arrows
   - Click version number to jump to specific version
   - Store versions in database

7. EXPORT
   - Copy to clipboard button
   - Download as file:
     - Documents: .md, .txt
     - Code: appropriate extension (.py, .js, etc.)

8. KEYBOARD SHORTCUTS
   - Ctrl+S: Copy to clipboard
   - Ctrl+Z/Ctrl+Y: Undo/Redo
   - Escape: Close Canvas

Create with React, TypeScript, TipTap (documents), Monaco (code), and Tailwind CSS.

Brand colors: #f1420b (orange), #2a93c1 (blue), #0a0a0a (dark bg)
```

---

## 4. SEARCH (Highlight-and-Jump)

### Feature Summary

ChatGPT's search finds conversations but doesn't take you to the exact match. Our differentiator: **Highlight-and-Jump**.

| Feature | ChatGPT | Pure Brain (Our Version) |
|---------|---------|--------------------------|
| Find conversation | Yes | Yes |
| Jump to message | NO | YES |
| Highlight match | NO | YES |
| Prev/Next navigation | NO | YES |
| Date filters | NO | YES |
| Sender filters | NO | YES |

### Marketing Angle

**"Search that actually takes you there."**

### Full Research Doc

`/home/jared/projects/AI-CIV/aether/docs/chatgpt-search-research/CHATGPT-SEARCH-ANALYSIS.md`

### Claude Code Prompt

```
I need to implement an advanced Search feature for our AI chat platform (Pure Brain AI).

Our key differentiator: "Highlight-and-Jump" - when user clicks a search result, we scroll to the exact message and highlight the matched text.

Requirements:

1. SEARCH INTERFACE
   - Search input at top of sidebar
   - Keyboard shortcut: Ctrl+K to open search modal
   - Real-time results as user types (300ms debounce)
   - Filter toggles: [All] [My Messages] [AI Responses]
   - Date filter: [Any Time] [Today] [This Week] [This Month]

2. SEARCH RESULTS
   - List of matching conversations grouped by chat
   - Show: conversation title, match count, snippet with match highlighted
   - Format: "conversation title (3 matches)"
   - Show relative time: "2 days ago"
   - Click result -> open conversation AND jump to match

3. HIGHLIGHT-AND-JUMP (Key Feature!)
   - When result clicked:
     a) Open the conversation
     b) Scroll to the first matching message
     c) Highlight the matched text with yellow background
     d) Show match navigator: "< 2/3 >" with prev/next buttons
   - Highlight persists until user clicks "Clear Search"
   - F3 or Ctrl+G: Jump to next match
   - Shift+F3: Jump to previous match

4. SEARCH WITHIN CURRENT CHAT
   - Ctrl+F opens mini-search bar at top of chat
   - Highlights all matches in current conversation
   - Same prev/next navigation

5. SEARCH QUERY SYNTAX (Advanced)
   - Regular search: `python`
   - Exact phrase: `"machine learning"`
   - Sender filter: `from:me` or `from:ai`
   - Date: `date:today`, `date:week`, `date:2025-02-01`
   - AND/OR/NOT: `python AND django`, `NOT flask`

6. BACKEND REQUIREMENTS
   - PostgreSQL full-text search or Elasticsearch
   - Index: conversation_id, message_id, content, sender, timestamp
   - API endpoint returns message_id and character positions of matches

7. API RESPONSE FORMAT
   {
     "total_matches": 24,
     "results": [
       {
         "conversation_id": "uuid",
         "conversation_title": "string",
         "matches": [
           {
             "message_id": "uuid",
             "message_index": 5,
             "sender": "user",
             "snippet": "...text around [MATCH]...",
             "match_positions": [[45, 50]]
           }
         ]
       }
     ]
   }

8. FRONTEND COMPONENTS
   - SearchModal: overlay with input and results
   - SearchResults: list of matching conversations
   - MatchHighlighter: component to wrap and highlight matches
   - MatchNavigator: prev/next buttons with counter

Create with React, TypeScript, and Tailwind CSS. Include the API types and search state management.

Highlight color: #FEF08A (yellow-200)
Brand: #f1420b (orange), #2a93c1 (blue)
```

---

## 5. BRAINS (Custom GPTs)

### Feature Summary

ChatGPT calls them "GPTs" - we call them "BRAINS". Users can create custom AI assistants with specific instructions, knowledge, and capabilities.

### Key Competitive Gaps to Exploit

| GPT Limitation | BRAINS Solution |
|----------------|-----------------|
| Single owner only | Multi-collaborator editing |
| No version control | Full version history |
| Files only for knowledge | URLs, APIs, live data |
| Basic analytics | Detailed usage dashboard |
| No invite sharing | Granular access control |
| No forking | Public Brains can be forked |

### Full Research Doc

`/home/jared/projects/AI-CIV/aether/docs/research/GPT-FEATURE-ANALYSIS.md`

### Claude Code Prompt

```
I need to implement a BRAINS feature for our AI chat platform (Pure Brain AI).

BRAINS are customizable AI assistants that users can create, share, and discover. (Like ChatGPT's GPTs but better.)

Requirements:

1. BRAIN CREATION FLOW
   Two modes:
   a) Simple Mode: Conversational wizard that generates config
   b) Advanced Mode: Direct editing of all fields

   Configuration fields:
   - Name (50 chars max)
   - Description (300 chars)
   - Avatar (image upload or emoji picker)
   - Instructions (system prompt, 8000 chars)
   - Conversation Starters (4 suggested prompts)
   - Knowledge (uploaded files)
   - Capabilities (toggles: web browsing, image gen, code execution)
   - Actions (external API connections via OpenAPI spec)

2. KNOWLEDGE MANAGEMENT
   - File upload (PDF, DOCX, TXT, MD, CSV, JSON)
   - Up to 20 files, 512MB each
   - RAG integration: files chunked and embedded for retrieval
   - Live preview: test knowledge retrieval
   - Future: URL sources that auto-refresh

3. PUBLISHING & SHARING
   Visibility levels:
   - Private: Only creator
   - Link: Anyone with URL
   - Invite: Specific users by email (our differentiator!)
   - Team: Workspace members
   - Public: Listed in Brain Store

4. BRAIN STORE (Discovery)
   - Categories: Writing, Productivity, Programming, Research, etc.
   - Featured/Trending sections
   - Search with filters
   - Brain detail page with:
     - Name, description, creator
     - Conversation starters
     - User ratings and reviews
     - "Add to My Brains" button
     - "Try it" preview

5. COLLABORATION (Our Differentiator!)
   - Invite collaborators with roles: Owner, Editor, Viewer
   - Version history: see all changes, restore previous versions
   - Comments/feedback on Brain config
   - Transfer ownership
   - Fork public Brains to create derivatives

6. ANALYTICS DASHBOARD
   For Brain creators:
   - Total conversations
   - Unique users
   - Average session length
   - Top conversation starters used
   - User ratings breakdown
   - Geographic distribution (optional)

7. DATA MODEL (PostgreSQL)
   ```sql
   brains (
     id, owner_id, name, description, avatar,
     instructions, visibility, category,
     created_at, updated_at, published_at
   )

   brain_collaborators (
     brain_id, user_id, role, added_at
   )

   brain_versions (
     id, brain_id, version_number,
     config_snapshot, created_by, created_at
   )

   brain_knowledge (
     id, brain_id, type, filename,
     file_path, content_hash
   )

   brain_capabilities (
     brain_id, capability_name, enabled
   )

   brain_reviews (
     id, brain_id, user_id,
     rating, comment, created_at
   )

   store_categories (id, name, display_order)
   ```

8. API ENDPOINTS
   - POST /brains (create)
   - GET /brains (list user's brains)
   - GET /brains/:id (get brain details)
   - PATCH /brains/:id (update)
   - DELETE /brains/:id
   - POST /brains/:id/publish (publish to store)
   - POST /brains/:id/fork (fork a public brain)
   - GET /store/brains (browse store)
   - GET /store/brains/featured
   - GET /store/brains/trending

Create with React, TypeScript, and Tailwind CSS. Include the Brain creation wizard, store browse UI, and analytics dashboard.

Brand: #f1420b (orange), #2a93c1 (blue), #0a0a0a (dark)
```

---

## Implementation Priority

### Phase 1 (MVP)
1. Settings (basic: theme, custom instructions, data controls)
2. Search with Highlight-and-Jump

### Phase 2
3. Projects (without collaboration)
4. Canvas (document mode only)

### Phase 3
5. BRAINS (creation + private use)
6. Canvas (code mode)

### Phase 4
7. Brain Store
8. Project collaboration
9. Brain collaboration

---

## Research Files Reference

| Feature | Full Research Doc |
|---------|-------------------|
| Settings | `/docs/chatgpt-settings-breakdown.md` |
| Projects | `/docs/competitive-analysis/CHATGPT-PROJECTS-FEATURE-BREAKDOWN.md` |
| Canvas | `/docs/chatgpt-canvas-research/CHATGPT-CANVAS-FEATURE-BREAKDOWN.md` |
| Search | `/docs/chatgpt-search-research/CHATGPT-SEARCH-ANALYSIS.md` |
| BRAINS | `/docs/research/GPT-FEATURE-ANALYSIS.md` |

---

**Created by Aether for Pure Brain AI**
**2026-02-05**
