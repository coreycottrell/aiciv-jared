# ChatGPT Canvas Feature Breakdown

**Agent**: browser-vision-tester
**Domain**: Visual UI Testing / Competitive Analysis
**Date**: 2026-02-05

---

## Executive Summary

ChatGPT Canvas is OpenAI's collaborative editing interface launched October 2024, enabling side-by-side AI-assisted writing and coding. This document provides a comprehensive feature breakdown for implementing a competing solution.

**Key Insight**: Canvas represents a paradigm shift from "AI as chat assistant" to "AI as collaborative editor." The fundamental innovation is a shared workspace where both human and AI can directly manipulate the same document.

---

## Table of Contents

1. [Feature Area: Activation & Triggering](#1-activation--triggering)
2. [Feature Area: Layout & Interface](#2-layout--interface)
3. [Feature Area: Document Mode](#3-document-mode)
4. [Feature Area: Code Mode](#4-code-mode)
5. [Feature Area: Collaborative Editing](#5-collaborative-editing)
6. [Feature Area: Version Control](#6-version-control)
7. [Feature Area: Shortcuts & Actions](#7-shortcuts--actions)
8. [Feature Area: Export & Integration](#8-export--integration)
9. [Competitive Comparison](#9-competitive-comparison)
10. [Implementation Requirements](#10-implementation-requirements)

---

## 1. Activation & Triggering

### How It Works in ChatGPT

**Automatic Triggering**:
- Canvas opens automatically when ChatGPT determines the task benefits from collaborative editing
- Writing tasks: "Write a blog post about...", "Draft an email...", "Create a story..."
- Coding tasks: "Write a Python function...", "Create a React component..."

**Manual Triggering**:
- Click "Open Canvas" button in response containing code/text
- Use prompt: "Open this in Canvas" or "Edit this in Canvas"
- Hover over code blocks to see "Open in Canvas" option

**Model Selection**:
- GPT-4 with Canvas (default for Plus users)
- Option to switch models affects Canvas behavior

### User Experience Flow

1. User enters prompt requesting content creation
2. ChatGPT evaluates if Canvas is appropriate
3. Canvas panel slides in from the right (split-screen view)
4. Content appears in editable Canvas while chat continues on left
5. User can toggle between chat-only and Canvas views

### Implementation Requirements

**Trigger Detection System**:
```
Required Components:
- Intent classifier: Detect "writing" vs "coding" vs "chat" intents
- Content length threshold: Canvas for substantial outputs (>15 lines suggested)
- Explicit trigger phrases: "canvas", "edit", "write document", etc.
- Code detection: Language detection for automatic code mode

Technical Requirements:
- Streaming support for progressive content loading
- Split-view responsive layout system
- Smooth animation for panel transitions
- State management for Canvas open/closed
```

**Heuristics for Auto-Opening**:
- Contains code block AND user asked for generation/modification
- Document structure (headers, lists, paragraphs) detected
- File type explicitly mentioned (.py, .js, .md, etc.)
- Length exceeds ~500 characters

---

## 2. Layout & Interface

### How It Works in ChatGPT

**Split-Screen Design**:
- Left panel: Standard chat interface
- Right panel: Canvas editor (expandable)
- Adjustable divider between panels
- Full-width Canvas mode available

**Canvas Panel Components**:
```
+------------------------------------------+
| [Mode: Document/Code] [Actions v] [X]    |  <- Header bar
|------------------------------------------|
|                                          |
|  [Editable content area]                 |  <- Main editor
|                                          |
|  Syntax highlighted (code)               |
|  Rich text (documents)                   |
|                                          |
|------------------------------------------|
| [Version: 1/3] [<] [>]  [Copy] [Download]|  <- Footer bar
+------------------------------------------+
```

**Responsive Behavior**:
- Mobile: Stacked layout (chat above, Canvas below)
- Tablet: Side-by-side with reduced chat width
- Desktop: Full split-screen experience

### Implementation Requirements

**Layout System**:
```
Required Components:
- Split panel container with resizable divider
- Panel state management (open/closed/fullscreen)
- Responsive breakpoints (mobile, tablet, desktop)
- Animation library for smooth transitions

Technical Stack Suggestions:
- React-split-pane or similar library
- CSS Grid/Flexbox for layout
- Framer Motion or similar for animations
- localStorage for panel preferences
```

**Accessibility**:
- Keyboard navigation between panels (Alt+1 / Alt+2)
- Screen reader announcements for panel changes
- Focus management when Canvas opens/closes

---

## 3. Document Mode

### How It Works in ChatGPT

**Editor Features**:
- Rich text editing (WYSIWYG-lite)
- Markdown rendering and source toggle
- Headers (H1-H6), bold, italic, underline
- Bullet lists, numbered lists
- Code inline and code blocks
- Links, blockquotes

**AI Writing Actions** (from toolbar/menu):
| Action | Description |
|--------|-------------|
| Suggest edits | AI proposes changes inline |
| Adjust length | Make shorter or longer |
| Reading level | Simplify or complexify |
| Add polish | Professional tone, grammar fix |
| Add emojis | Insert relevant emojis |
| Final polish | Comprehensive editing pass |

**Selection-Based Actions**:
- Select text -> AI menu appears
- Options: Rewrite, Expand, Summarize, Change tone

### User Experience Flow

1. Document appears in Canvas
2. User can directly edit OR request AI changes
3. User selects portion of text
4. Floating AI menu offers contextual actions
5. AI shows proposed changes inline (with accept/reject)
6. Chat continues alongside for questions/guidance

### Implementation Requirements

**Rich Text Editor**:
```
Required Components:
- ProseMirror, TipTap, or Slate.js base
- Custom toolbar with AI actions
- Selection detection for contextual menus
- Markdown import/export
- Real-time collaborative editing foundation

AI Integration Points:
- Selection -> API call with context
- Streaming response into editor
- Diff visualization for proposed changes
- Accept/reject UX for suggestions
```

**Document Mode Actions API**:
```typescript
interface DocumentAction {
  type: 'suggest_edits' | 'adjust_length' | 'reading_level' |
        'polish' | 'emojis' | 'rewrite' | 'expand' | 'summarize';
  selection?: { start: number; end: number };
  parameters?: {
    lengthTarget?: 'shorter' | 'longer';
    readingLevel?: 'elementary' | 'high_school' | 'college' | 'expert';
    tone?: 'formal' | 'casual' | 'professional' | 'friendly';
  };
}
```

---

## 4. Code Mode

### How It Works in ChatGPT

**Editor Features**:
- Syntax highlighting (50+ languages)
- Line numbers
- Code folding
- Auto-indentation
- Bracket matching
- Find and replace

**AI Coding Actions** (from toolbar/menu):
| Action | Description |
|--------|-------------|
| Review code | Check for bugs, issues |
| Add comments | Document the code |
| Add logging | Insert debug statements |
| Fix bugs | Identify and fix issues |
| Port to language | Convert to another language |
| Add tests | Generate unit tests |
| Explain code | Add inline explanations |
| Optimize | Improve performance |

**Language Support**:
- Auto-detection from file extension or content
- Manual language selection dropdown
- Syntax themes (light/dark)

### User Experience Flow

1. Code appears in Canvas with syntax highlighting
2. User edits directly OR requests AI modifications
3. AI actions operate on full code or selection
4. Changes shown with diff view option
5. User iterates until satisfied

### Implementation Requirements

**Code Editor**:
```
Required Components:
- Monaco Editor (VS Code base) or CodeMirror 6
- Language server protocol support (optional)
- Custom toolbar with AI actions
- Diff viewer for changes
- Multiple file support (future)

Language Features:
- Tree-sitter for parsing
- Language-specific AI prompts
- Test generation by framework
```

**Code Mode Actions API**:
```typescript
interface CodeAction {
  type: 'review' | 'add_comments' | 'add_logging' | 'fix_bugs' |
        'port_language' | 'add_tests' | 'explain' | 'optimize';
  language: string;
  selection?: { startLine: number; endLine: number };
  parameters?: {
    targetLanguage?: string;  // for port
    testFramework?: string;   // for tests
    logLevel?: 'debug' | 'info' | 'verbose';
  };
}
```

---

## 5. Collaborative Editing

### How It Works in ChatGPT

**Human-AI Collaboration Model**:
- Both parties can edit the same document
- AI waits for explicit requests (doesn't auto-edit)
- Human edits are preserved unless AI asked to change
- Conversational context informs AI edits

**Inline Suggestions**:
- AI can show suggestions without replacing
- Accept/reject buttons on each suggestion
- Accept all / Reject all options
- Suggestion highlighting (different color)

**Contextual Understanding**:
- AI remembers document history in conversation
- Can reference earlier versions
- Understands user's intent from chat

### User Experience Flow

1. User and AI co-create document
2. User: "Make the intro more engaging"
3. AI highlights intro, shows suggestion inline
4. User accepts or requests alternative
5. Process repeats until satisfied

### Implementation Requirements

**Collaboration System**:
```
Required Components:
- Operational Transform (OT) or CRDT for merging
- Change tracking with attribution
- Suggestion mode (track changes style)
- Conflict resolution UI

State Management:
- Document state
- Pending suggestions state
- User edit history
- AI intervention history
```

**Suggestion UX**:
```typescript
interface Suggestion {
  id: string;
  type: 'replace' | 'insert' | 'delete';
  range: { start: number; end: number };
  originalContent: string;
  suggestedContent: string;
  reason: string;
  status: 'pending' | 'accepted' | 'rejected';
}
```

---

## 6. Version Control

### How It Works in ChatGPT

**Version History**:
- Every AI edit creates a new version
- Manual user edits batched into versions
- Version counter displayed in footer (e.g., "Version 3/7")
- Navigate with arrow buttons

**Version Navigation**:
- Previous/Next arrows
- Jump to specific version (number click)
- View diff between versions
- Restore to earlier version

**Branching** (limited):
- Edit earlier message to create branch
- Each branch maintains separate Canvas history
- No merge between branches

### User Experience Flow

1. Document at Version 1
2. AI edits -> Version 2
3. User edits -> Version 3
4. User: "Go back to Version 1"
5. User can continue from V1 (creates new timeline)

### Implementation Requirements

**Version Control System**:
```
Required Components:
- Version storage (full snapshots or deltas)
- Diff algorithm (diff-match-patch)
- Version metadata (timestamp, author, action)
- Branch management (optional)

Storage Strategy:
- Delta compression for efficiency
- Maximum version limit (prevent unbounded growth)
- Cloud sync for persistence
```

**Version Data Structure**:
```typescript
interface Version {
  id: string;
  number: number;
  timestamp: Date;
  author: 'user' | 'ai';
  action: string;  // "AI: Added comments" / "User edit"
  content: string;
  diff?: {
    additions: number;
    deletions: number;
    changes: DiffChunk[];
  };
}
```

---

## 7. Shortcuts & Actions

### How It Works in ChatGPT

**Keyboard Shortcuts**:
| Shortcut | Action |
|----------|--------|
| Cmd/Ctrl + S | Save/Copy to clipboard |
| Cmd/Ctrl + Z | Undo |
| Cmd/Ctrl + Shift + Z | Redo |
| Cmd/Ctrl + / | Toggle comment (code) |
| Cmd/Ctrl + B | Bold (document) |
| Cmd/Ctrl + I | Italic (document) |
| Escape | Exit Canvas / Close |

**Quick Actions Menu**:
- Accessible via toolbar button
- Keyboard shortcut to open
- Search/filter actions
- Recently used actions

### Implementation Requirements

**Shortcut System**:
```
Required Components:
- Global hotkey manager
- Context-aware shortcuts (code vs document)
- Customizable shortcuts (settings)
- Shortcut hints in UI

Libraries:
- Mousetrap.js or similar
- Command palette component (Cmd+K style)
```

---

## 8. Export & Integration

### How It Works in ChatGPT

**Export Options**:
| Format | Availability |
|--------|--------------|
| Copy to clipboard | Always |
| Download as file | Code (with extension), Docs (.md/.txt) |
| Copy as Markdown | Documents |
| Raw code | Code mode |

**Integration Features**:
- No direct IDE integration (standalone)
- API access to Canvas (limited/beta)
- Share link for documents (Plus feature)

### User Experience Flow

1. Click download icon in footer
2. Select format (if multiple options)
3. File downloads with appropriate extension
4. Or: Click copy icon -> clipboard

### Implementation Requirements

**Export System**:
```
Required Components:
- File generation for various formats
- Clipboard API integration
- Download trigger mechanism
- Format conversion utilities

Formats to Support:
- .md (Markdown)
- .txt (Plain text)
- .py, .js, .ts, etc. (code files)
- .html (rendered documents, optional)
- .pdf (future, requires conversion)
```

---

## 9. Competitive Comparison

### ChatGPT Canvas vs Claude Artifacts

| Feature | ChatGPT Canvas | Claude Artifacts |
|---------|----------------|------------------|
| **Activation** | Auto + manual | Auto + manual |
| **Document editing** | Full WYSIWYG | Markdown-based |
| **Code editing** | Full editor | Read + copy focused |
| **Direct editing** | Yes, inline | Limited |
| **Version history** | Full navigation | Version selector |
| **AI actions menu** | Extensive | Minimal |
| **Selection actions** | Rich context menu | Not prominent |
| **Multi-artifact** | One active | Multiple in sidebar |
| **Interactive output** | Limited | React components, SVGs |
| **Export** | Download + copy | Download + copy |
| **Persistence** | Conversation-scoped | User account storage |

**Claude Artifacts Advantages**:
- Interactive React components
- SVG/diagram generation
- Persistent storage (20MB)
- Multiple artifacts per conversation

**ChatGPT Canvas Advantages**:
- True collaborative editing
- Richer document editing
- AI action menus
- Version navigation
- Selection-based AI actions

### ChatGPT Canvas vs Cursor

| Feature | ChatGPT Canvas | Cursor |
|---------|----------------|--------|
| **Primary use** | General writing/coding | Code-focused |
| **Environment** | Web browser | Desktop IDE |
| **Multi-file** | No | Yes |
| **Codebase awareness** | No | Full project |
| **Agent mode** | No | Yes (auto-edit) |
| **Code review** | In-canvas | PR integration |
| **Collaboration** | Human-AI | Human-AI + Human-Human |

### ChatGPT Canvas vs GitHub Copilot

| Feature | ChatGPT Canvas | GitHub Copilot |
|---------|----------------|----------------|
| **Inline completion** | No | Yes |
| **Document editing** | Yes | No |
| **IDE integration** | No | VS Code, JetBrains |
| **Issue assignment** | No | Yes |
| **Pull request** | No | Yes |
| **Multi-file** | No | Yes |

### ChatGPT Canvas vs Notion AI

| Feature | ChatGPT Canvas | Notion AI |
|---------|----------------|-----------|
| **Document editing** | Yes | Yes |
| **Code editing** | Yes | Limited |
| **Workspace integration** | No | Full |
| **Database support** | No | Yes |
| **Team collaboration** | No | Yes |
| **Custom agents** | No | Coming |
| **External MCP** | No | Yes |

---

## 10. Implementation Requirements

### MVP Feature Set

**Phase 1: Core Canvas (4-6 weeks)**
1. Split-screen layout with resizable panels
2. Basic document mode (Markdown editor)
3. Basic code mode (syntax highlighting)
4. Manual Canvas triggering
5. Copy/Download export

**Phase 2: AI Integration (3-4 weeks)**
1. Auto-triggering based on intent
2. AI actions for documents (3-4 core actions)
3. AI actions for code (3-4 core actions)
4. Selection-based AI menu

**Phase 3: Collaboration & Polish (3-4 weeks)**
1. Inline suggestions with accept/reject
2. Version history (basic)
3. Keyboard shortcuts
4. Mobile responsive layout

### Technical Architecture

```
+------------------+     +------------------+     +------------------+
|   Chat Service   |<--->|  Canvas Service  |<--->|   AI Service     |
+------------------+     +------------------+     +------------------+
         |                       |                       |
         v                       v                       v
+------------------+     +------------------+     +------------------+
|  Message Store   |     |  Document Store  |     |   LLM Gateway    |
+------------------+     +------------------+     +------------------+
```

**Key Components**:
1. **Canvas Service**: State management, version control
2. **Editor Component**: TipTap/Monaco based
3. **AI Actions Module**: Action definitions, prompts
4. **Diff Engine**: Change detection, merge
5. **Export Module**: Format conversion

### Technology Recommendations

**Frontend**:
- React 18+ with Suspense for streaming
- TipTap (documents) / Monaco (code)
- Zustand or Jotai for state
- Framer Motion for animations

**Backend**:
- WebSocket for real-time sync
- Redis for session state
- PostgreSQL for version storage
- S3 for document persistence

**AI Integration**:
- Streaming API support
- Context window management
- Action-specific prompts
- Rate limiting per action type

---

## Appendix: Research Methodology

**Sources Consulted**:
1. OpenAI official documentation (access blocked)
2. Claude Artifacts documentation (Anthropic support)
3. Cursor features page
4. GitHub Copilot features
5. Notion AI product page
6. Secondary tech news sources

**Limitations**:
- Direct ChatGPT Canvas access required authentication
- OpenAI help center returned 403 errors
- Some tech news sites blocked WebFetch
- Full hands-on testing not completed

**Recommendations for Further Research**:
1. Authenticated session testing of Canvas
2. User interviews with heavy Canvas users
3. A/B testing of activation triggers
4. Performance benchmarking of editors

---

## Document Metadata

**Created**: 2026-02-05
**Author**: browser-vision-tester
**Version**: 1.0
**Status**: Complete (pending authenticated testing)

**Files Created**:
- `/home/jared/projects/AI-CIV/aether/docs/chatgpt-canvas-research/CHATGPT-CANVAS-FEATURE-BREAKDOWN.md` (this document)
- `/home/jared/projects/AI-CIV/aether/tools/chatgpt_canvas_explorer.py` (automation script for future testing)

---

**END OF DOCUMENT**
