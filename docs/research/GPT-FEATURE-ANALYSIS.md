# ChatGPT GPTs Feature Analysis

**Agent**: browser-vision-tester
**Date**: 2026-02-05
**Purpose**: Document OpenAI's GPTs feature for BRAINS implementation

---

## Research Methodology Note

Direct web research was significantly limited due to site access restrictions (403/404 errors from most sources). This document combines:
1. Fragmentary information from accessible sources (OpenAI Community, Zapier, OpenAI Cookbook)
2. Established knowledge about the GPT feature from training data
3. Implementation recommendations for BRAINS

---

## Part 1: What Are GPTs?

### Definition

GPTs (custom GPTs) are customized versions of ChatGPT that users can create for specific purposes without coding. Launched by OpenAI in November 2023, they allow users to:

- Configure ChatGPT with custom instructions
- Upload knowledge files (documents, data)
- Connect to external services via Actions
- Share or publish their creations

### Key Insight from Research

From OpenAI Community forums: Users actively discuss maintenance costs, troubleshooting, and the lack of monetization - indicating GPTs are a mature feature with an active builder community.

---

## Part 2: GPT Creation Flow

### Access Points

1. **ChatGPT Interface**: Click "Explore GPTs" in sidebar
2. **Direct URL**: chat.openai.com/gpts/editor
3. **API Alternative**: Assistants API for programmatic creation

### Two Creation Modes

#### 1. Create Mode (Conversational)

- Chat-based setup wizard
- GPT Builder asks questions to configure the GPT
- Generates name, description, instructions automatically
- Good for beginners or simple GPTs

#### 2. Configure Mode (Direct)

Manual configuration of all settings:

| Field | Description | Character Limit |
|-------|-------------|-----------------|
| **Name** | Display name for the GPT | ~50 chars recommended |
| **Description** | Brief explanation shown in store | ~300 chars |
| **Instructions** | System prompt defining behavior | ~8000 chars |
| **Conversation Starters** | Pre-filled prompts users can click | 4 starters typical |
| **Knowledge** | Uploaded files the GPT can reference | Up to 20 files, 512MB each |
| **Capabilities** | Web browsing, DALL-E, Code Interpreter | Toggle on/off |
| **Actions** | External API connections | OpenAPI spec required |

### Creation Steps

1. **Start**: Click "Create a GPT"
2. **Choose Mode**: Create (conversational) or Configure (direct)
3. **Define Identity**: Name, description, profile image
4. **Write Instructions**: System prompt (the most important part)
5. **Add Knowledge**: Upload reference documents
6. **Enable Capabilities**: Toggle built-in tools
7. **Configure Actions**: Connect external APIs (optional)
8. **Test**: Preview pane shows live behavior
9. **Save**: Draft or publish

---

## Part 3: Configuration Options (Deep Dive)

### Instructions (System Prompt)

The core of GPT customization. Best practices:

```
You are [role/persona].

Your purpose is to [primary function].

When interacting:
- [Behavior guideline 1]
- [Behavior guideline 2]
- [Constraint or boundary]

You have access to [knowledge files/capabilities].

Always [key requirement].
Never [prohibited behavior].
```

### Knowledge Files

**Supported formats**:
- Documents: PDF, DOCX, TXT, MD
- Data: CSV, JSON, XLSX
- Code: PY, JS, HTML, CSS
- Images: PNG, JPG, GIF (for reference)

**How it works**:
- Files are chunked and embedded
- GPT retrieves relevant chunks via RAG
- Can cite sources from uploaded files

**Limitations**:
- 20 files maximum
- 512MB per file
- Files are accessible to all users of the GPT
- Cannot protect proprietary information in shared GPTs

### Capabilities (Built-in Tools)

| Capability | What It Does | Use Case |
|------------|--------------|----------|
| **Web Browsing** | Search and retrieve web content | Research, current events |
| **DALL-E Image Generation** | Create images from prompts | Visual content creation |
| **Code Interpreter** | Execute Python, analyze data | Data analysis, calculations |

### Actions (External APIs)

**What Actions Enable**:
- Connect to any API with OpenAPI spec
- Authenticate users (OAuth, API keys)
- Send/receive data from external services
- Trigger workflows in other tools

**Configuration Requirements**:
1. OpenAPI 3.0+ specification (JSON or YAML)
2. Authentication method (None, API Key, OAuth)
3. Privacy policy URL
4. Server URLs and endpoints

**From OpenAI Cookbook Research**:
Pre-built action integrations exist for: Salesforce, Jira, Google Calendar, GitHub, Gmail, Notion, and others.

---

## Part 4: Publishing and Sharing Options

### Visibility Levels

| Level | Access | URL | Store Listing |
|-------|--------|-----|---------------|
| **Only Me** | Private, creator only | No shareable link | Not listed |
| **Anyone with the link** | Semi-public | Shareable URL | Not listed |
| **Everyone (Public)** | Published to GPT Store | Store URL | Listed and searchable |

### Publishing Requirements (GPT Store)

To publish publicly:
1. GPT must comply with usage policies
2. Creator must verify identity (phone/payment)
3. Must have a unique, clear name
4. Must include privacy policy for Actions
5. Cannot impersonate real people/brands
6. Review process (automated + manual)

### The GPT Store

**Discovery Features**:
- Categories: Writing, Productivity, Research, Programming, Education, Lifestyle
- Featured/Trending sections
- Search by name or description
- Usage/popularity metrics (hidden from public)
- User reviews (limited functionality)

**Store URL**: chat.openai.com/gpts

---

## Part 5: Collaboration and Teams

### ChatGPT Team/Enterprise Features

- **Workspace GPTs**: Shared within organization
- **Admin controls**: Who can create/publish GPTs
- **Private sharing**: Share with specific team members
- **Analytics**: Usage data for workspace GPTs

### Collaboration Limitations (as of knowledge cutoff)

- No real-time collaborative editing
- No version control built-in
- No transfer of ownership
- Creator retains sole edit access

---

## Part 6: Analytics and Monetization

### Usage Analytics (Limited)

What creators can see:
- Conversation count (approximate)
- Growth trends (basic)
- Geographic distribution (limited)

What's NOT available:
- Detailed user demographics
- Conversation logs
- Revenue metrics
- Conversion tracking

### Monetization

**Current State** (from OpenAI Community research):
- Revenue sharing program announced but limited
- Top creators receive payments based on usage
- No self-serve monetization
- Many builders report "maintenance costs starting to hurt" without revenue

**Builder Program**:
- Invite-only initially
- Based on GPT popularity/quality
- Payouts based on engagement metrics

---

## Part 7: Technical Considerations

### Rate Limits

- GPT conversations count against user's ChatGPT Plus/Team limits
- Actions may have separate rate limits from external APIs
- Knowledge retrieval has latency considerations

### Security Considerations

**From Research**:
- Instructions can be extracted through prompt injection
- Knowledge files can potentially be accessed
- Actions expose API credentials (use OAuth when possible)
- No built-in analytics on attempted exploits

### Performance

- Cold start on first message (knowledge loading)
- Actions add latency per external call
- Large knowledge bases increase response time

---

## Part 8: BRAINS Implementation Recommendations

Based on GPT feature analysis, here are implementation recommendations for your BRAINS feature:

### Core Features to Implement

#### 1. Brain Creation Flow

**Two modes like GPTs**:
- **Simple Mode**: Conversational wizard that generates config
- **Advanced Mode**: Direct editing of all fields

**Essential Configuration Fields**:
```typescript
interface BrainConfig {
  // Identity
  name: string;              // Display name
  description: string;       // Short description
  avatar: string;            // Profile image URL

  // Behavior
  instructions: string;      // System prompt
  conversationStarters: string[]; // Suggested prompts

  // Knowledge
  knowledgeFiles: File[];    // Uploaded documents

  // Capabilities
  capabilities: {
    webBrowsing: boolean;
    imageGeneration: boolean;
    codeExecution: boolean;
    // Your custom capabilities
  };

  // Integrations
  actions: ActionConfig[];   // External API connections

  // Publishing
  visibility: 'private' | 'link' | 'public';
  category?: string;         // For public discovery
}
```

#### 2. Knowledge Management

**Improvements over GPTs**:
- Real-time knowledge updates (GPTs require re-upload)
- Structured knowledge bases (not just file dumps)
- Citation tracking and source management
- Knowledge versioning

**Implementation**:
```typescript
interface KnowledgeBase {
  files: {
    id: string;
    name: string;
    type: string;
    size: number;
    uploadedAt: Date;
    lastModified: Date;
    chunks: ChunkReference[];
  }[];
  urls: {
    id: string;
    url: string;
    lastCrawled: Date;
    refreshInterval?: number;
  }[];
  customData: {
    id: string;
    type: 'faq' | 'glossary' | 'structured';
    data: any;
  }[];
}
```

#### 3. Publishing Workflow

**Visibility Levels**:
| Level | Description |
|-------|-------------|
| `private` | Only creator can access |
| `link` | Anyone with URL can use |
| `invite` | Specific users/emails (improvement over GPTs) |
| `team` | Workspace members |
| `public` | Listed in Brain Store |

**Publishing Flow**:
1. Creator sets visibility
2. If public: automated policy check
3. If public: category selection required
4. Preview in store context
5. Submit for review (if required)
6. Publish or feedback loop

#### 4. Collaboration Features (Differentiate from GPTs)

**What GPTs lack that BRAINS should have**:

```typescript
interface BrainCollaboration {
  // Multiple editors
  collaborators: {
    userId: string;
    role: 'owner' | 'editor' | 'viewer';
    addedAt: Date;
  }[];

  // Version control
  versions: {
    id: string;
    createdAt: Date;
    createdBy: string;
    changes: string;
    config: BrainConfig;
  }[];

  // Comments/feedback
  feedback: {
    id: string;
    userId: string;
    comment: string;
    resolved: boolean;
  }[];

  // Transfer ownership
  transferOwnership(newOwnerId: string): Promise<void>;
}
```

#### 5. Analytics Dashboard

**What to track**:
```typescript
interface BrainAnalytics {
  // Usage
  totalConversations: number;
  uniqueUsers: number;
  averageSessionLength: number;
  messagesPerConversation: number;

  // Performance
  averageResponseTime: number;
  knowledgeRetrievalRate: number;
  actionSuccessRate: number;

  // Engagement
  conversationStarters: {
    prompt: string;
    useCount: number;
  }[];
  topQueries: string[];

  // Feedback
  ratings: number[];
  reviews: Review[];
}
```

#### 6. Brain Store (Discovery)

**Store Features**:
- Categories (user-defined + curated)
- Featured/Trending sections
- Search with filters
- User reviews and ratings
- Usage indicators
- Preview/try before adding

**Store API**:
```typescript
interface BrainStore {
  // Discovery
  getCategories(): Category[];
  getFeatured(): Brain[];
  getTrending(period: 'day' | 'week' | 'month'): Brain[];
  search(query: string, filters: SearchFilters): Brain[];

  // Details
  getBrain(id: string): BrainDetails;
  getReviews(brainId: string): Review[];

  // Actions
  addToMyBrains(brainId: string): Promise<void>;
  submitReview(brainId: string, review: Review): Promise<void>;
}
```

### Differentiation Opportunities

**Where to exceed GPTs**:

| GPT Limitation | BRAINS Solution |
|----------------|-----------------|
| Single owner only | Multi-collaborator editing |
| No version control | Full version history |
| Files only for knowledge | URLs, APIs, databases |
| Basic analytics | Detailed usage dashboard |
| No invite-specific sharing | Granular access control |
| No in-store monetization | Revenue sharing or tipping |
| Limited customization | Custom UI themes |
| No branching/forking | Public Brains can be forked |

### Technical Architecture

```
User Interface
    |
    v
Brain Editor <----> Brain Store
    |                    |
    v                    v
Configuration -------> Brain Registry
    |
    v
+---+---+---+
|   |   |   |
v   v   v   v
Knowledge  Actions  Capabilities  Analytics
Base       (APIs)   (Tools)       Engine
```

### Data Model

```sql
-- Core tables
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
  id, brain_id, type, source,
  content_hash, metadata, created_at
)

brain_actions (
  id, brain_id, name, openapi_spec,
  auth_type, auth_config
)

brain_capabilities (
  brain_id, capability_name, enabled
)

brain_analytics (
  brain_id, date, conversations,
  unique_users, avg_response_time
)

brain_reviews (
  id, brain_id, user_id,
  rating, comment, created_at
)

store_categories (
  id, name, description, display_order
)

brain_categories (
  brain_id, category_id
)
```

---

## Part 9: Implementation Roadmap

### Phase 1: Core Brain Creation
- [ ] Brain configuration schema
- [ ] Simple creation wizard
- [ ] Advanced configuration editor
- [ ] Instruction editor with preview
- [ ] Save/load brain configs

### Phase 2: Knowledge Management
- [ ] File upload system
- [ ] RAG integration for retrieval
- [ ] Knowledge preview/testing
- [ ] File management UI

### Phase 3: Capabilities & Actions
- [ ] Enable/disable built-in tools
- [ ] Action configuration UI
- [ ] OpenAPI spec editor/importer
- [ ] Authentication setup

### Phase 4: Publishing & Sharing
- [ ] Visibility controls
- [ ] Shareable links
- [ ] Invite-specific access
- [ ] Publishing workflow

### Phase 5: Brain Store
- [ ] Store listing page
- [ ] Category management
- [ ] Search and filters
- [ ] Brain details page

### Phase 6: Collaboration
- [ ] Multi-user editing
- [ ] Version history
- [ ] Comments/feedback
- [ ] Ownership transfer

### Phase 7: Analytics
- [ ] Usage tracking
- [ ] Analytics dashboard
- [ ] Performance metrics
- [ ] Review system

---

## Part 10: Open Questions for Design

1. **Monetization Model**: Will BRAINS support revenue sharing, tipping, or paid Brains?

2. **Forking/Remixing**: Can users fork public Brains to create derivatives?

3. **API Access**: Will there be programmatic Brain creation/management?

4. **Enterprise Features**: Special controls for team/enterprise workspaces?

5. **Capability Extensions**: Custom capabilities beyond standard tools?

6. **Knowledge Sync**: Real-time sync with external sources (Google Drive, Notion)?

7. **Conversation Handoff**: Can Brains hand off to human agents?

8. **Multi-Brain Workflows**: Can Brains invoke other Brains?

---

## Appendix A: GPT Store Categories (Reference)

As observed in research:
- Writing
- Productivity
- Research & Analysis
- Programming
- Education
- Lifestyle
- (Custom/Other)

---

## Appendix B: Sample Brain Configuration

```json
{
  "name": "Code Review Assistant",
  "description": "Expert code reviewer focused on clean code principles",
  "avatar": "https://example.com/code-review-avatar.png",
  "instructions": "You are an expert code reviewer. Your role is to analyze code submissions and provide constructive feedback focused on:\n\n1. Code clarity and readability\n2. Best practices and design patterns\n3. Potential bugs or edge cases\n4. Performance considerations\n5. Security vulnerabilities\n\nAlways be encouraging while being thorough. Start with positive observations before suggesting improvements. Use specific line references when possible.",
  "conversationStarters": [
    "Review this Python function for me",
    "What's wrong with this code?",
    "Help me refactor this class",
    "Check this for security issues"
  ],
  "knowledge": {
    "files": [
      {"name": "clean-code-principles.pdf", "type": "pdf"},
      {"name": "owasp-top-10.md", "type": "markdown"}
    ]
  },
  "capabilities": {
    "webBrowsing": false,
    "imageGeneration": false,
    "codeExecution": true
  },
  "actions": [],
  "visibility": "public",
  "category": "Programming"
}
```

---

## Research Sources

1. **OpenAI Community Forums** - Active builder discussions, troubleshooting threads, monetization concerns
2. **OpenAI Cookbook** - GPT Actions library, integration examples
3. **Zapier Blog** - Overview of custom GPT use cases
4. **Training Data Knowledge** - Feature details from November 2023 launch and subsequent updates

---

**Document Created**: 2026-02-05
**Agent**: browser-vision-tester
**Verification**: Research limited by web access restrictions; document synthesizes available information with implementation recommendations
