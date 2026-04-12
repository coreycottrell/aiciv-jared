# ChatGPT Projects Feature Breakdown

**Date**: 2026-02-05
**Purpose**: Comprehensive feature analysis for competitive platform implementation
**Research Method**: Web research (direct UI testing not available in current environment)

---

## Executive Summary

ChatGPT Projects is OpenAI's organizational feature that allows users to group related conversations, files, and custom instructions into dedicated containers. Think of it as "smart folders" for AI workflows. Released December 2024, initially for paid subscribers with gradual free tier rollout.

---

## 1. Project Creation

### How It Works in ChatGPT

| Aspect | Details |
|--------|---------|
| **Creation Flow** | Click '+' button next to 'Project' in sidebar > Enter name > Create Project |
| **Naming** | Free-form text, user-defined project names |
| **Visual Customization** | Color-coded folder icons (select via folder icon click) |
| **Location** | Projects appear in left sidebar, separate from regular chat history |

### User Benefits

- Quick project setup (3-4 clicks)
- Visual differentiation between projects via colors
- Clear separation from general chat history
- Intuitive folder-based mental model

### Implementation Requirements

1. **Sidebar Component**: Dedicated "Projects" section with collapse/expand
2. **Project Entity**: Name, color, creation date, owner metadata
3. **Color Picker**: Predefined color palette for project icons
4. **Creation Modal**: Simple form with name input and color selection
5. **Database Schema**: `projects` table with user_id, name, color, created_at

---

## 2. File Management

### How It Works in ChatGPT

| Aspect | Details |
|--------|---------|
| **Upload Location** | "Project files" section within each project |
| **File Scope** | Files apply ONLY to that specific project (not global) |
| **Deletion** | Click 'x' icon next to file; deletion is permanent (no recovery) |
| **File Limits** | Subject to subscription tier limits (exact numbers not publicly documented) |
| **Cloud Integration** | No OneDrive or Google Drive integration currently |

### User Benefits

- Context-specific file access (no file pollution across projects)
- Simple upload/delete interface
- Files automatically included in project conversation context
- Prevents confusion about which files apply to which work

### Implementation Requirements

1. **File Upload Component**: Drag-and-drop + click-to-upload interface
2. **Project-Scoped Storage**: Files linked to project_id, not globally
3. **File Display**: List view with filename, size, upload date, delete action
4. **Storage Tracking**: Per-project and per-user file quotas
5. **Soft Delete**: Consider implementing trash/recovery (competitive advantage)
6. **Context Injection**: System to include uploaded files in conversation context

### File Type Support (Inferred from General ChatGPT)

- Documents: PDF, DOCX, TXT, MD
- Data: CSV, XLSX, JSON
- Code: PY, JS, TS, HTML, CSS, etc.
- Images: PNG, JPG, GIF, WEBP

---

## 3. Conversation Organization

### How It Works in ChatGPT

| Aspect | Details |
|--------|---------|
| **New Chats** | "New chat in this project" button within project view |
| **Moving Chats** | Three-dot menu on chat > "Add to project" > Select destination |
| **Chat Display** | All project chats listed within project container |
| **Search** | Search functionality works within project scope |
| **Model** | All project chats use GPT-4o exclusively |

### User Benefits

- Conversations stay organized by topic/purpose
- Easy migration of existing relevant chats
- Searchable project-specific history
- Context continuity across multiple chat sessions

### Implementation Requirements

1. **Chat-Project Association**: `chats` table with optional `project_id` foreign key
2. **Move Chat UI**: Context menu with project selection dropdown
3. **Project Chat List**: Filtered view showing only project-associated chats
4. **Project-Scoped Search**: Index chats with project_id for filtered search
5. **New Chat Routing**: "Start in project" option during chat creation

---

## 4. Custom Instructions

### How It Works in ChatGPT

| Aspect | Details |
|--------|---------|
| **Access** | "Instructions" button within project view |
| **Scope** | Project instructions SUPERSEDE account-level instructions |
| **Content** | Free-form text for formatting, tone, focus area specifications |
| **Inheritance** | Project instructions only apply within that project |

### User Benefits

- Tailored AI behavior per project context
- No need to repeat context/preferences in every chat
- Consistent output across all project conversations
- Professional/personal separation of AI personas

### Implementation Requirements

1. **Instructions Editor**: Text area with save/cancel buttons
2. **Instruction Storage**: Text field in `projects` table
3. **System Prompt Injection**: Prepend project instructions to system prompt
4. **Priority Logic**: Project instructions > Account instructions > Defaults
5. **Character Limit**: Define reasonable limit (suggest 2000-4000 chars)
6. **Preview/Test**: Optional feature to test instruction effects

---

## 5. Sharing & Collaboration

### How It Works in ChatGPT

| Aspect | Details |
|--------|---------|
| **Individual Sharing** | NOT AVAILABLE - Projects are single-user only |
| **Teams Plan** | Teams subscribers may have additional collaboration (limited info) |
| **Export** | No native project export functionality documented |

### Competitor Advantage: Claude Projects

Claude Projects DOES support team collaboration:
- Share project snapshots with team members
- Collaborative context building
- Team-based project access

### User Benefits (If Implemented)

- Team collaboration on shared AI workflows
- Knowledge sharing without duplicating setup
- Organizational memory/knowledge base

### Implementation Requirements (Competitive Differentiator)

1. **Project Sharing**: Invite collaborators by email
2. **Permission Levels**: Owner, Editor, Viewer
3. **Shared Context**: All collaborators see same files/instructions
4. **Activity Log**: Track who added what
5. **Project Templates**: Export/import project configurations

---

## 6. Platform Availability

### How It Works in ChatGPT

| Platform | Project Support |
|----------|-----------------|
| **Web (chatgpt.com)** | Full support |
| **Windows Desktop** | Full support |
| **macOS Desktop** | NOT supported |
| **iOS App** | NOT supported |
| **Android App** | NOT supported |

### Competitor Advantage: Claude Projects

Claude supports project creation/editing across ALL platforms (web, desktop, mobile).

### Implementation Requirements

- Cross-platform parity from launch (competitive advantage)
- API support for third-party client integration
- Offline mode consideration for desktop apps

---

## 7. Subscription Tiers

### How It Works in ChatGPT

| Tier | Access |
|------|--------|
| **Free** | Coming soon (not yet available) |
| **Plus ($20/mo)** | Full access |
| **Pro ($200/mo)** | Full access |
| **Teams** | Full access |
| **Enterprise** | Early 2025 rollout |
| **Edu** | Early 2025 rollout |

### Implementation Requirements

- Tiered feature gating system
- Project limits per tier (suggest: Free=3, Plus=10, Pro=unlimited)
- File storage limits per tier
- Upgrade prompts when limits reached

---

## 8. Technical Specifications

### Known Limits

| Specification | Value |
|---------------|-------|
| **Context Window** | ~128,000 tokens (vs Claude's 200,000) |
| **Model** | GPT-4o only (no model switching within projects) |
| **File Size** | Not publicly documented (infer from general ChatGPT limits) |
| **Max Projects** | Not publicly documented |
| **Max Files/Project** | Not publicly documented |

### Implementation Requirements

1. **Context Management**: Token counting and truncation strategy
2. **File Processing**: Extract text from various formats for context
3. **Embedding System**: Vector storage for file semantic search
4. **Model Selection**: Consider allowing model choice per project

---

## 9. Integrated Features

### How It Works in ChatGPT

| Feature | Integration |
|---------|-------------|
| **Search** | Search within project conversations |
| **DALL-E** | Image generation available in project chats |
| **Canvas** | Collaborative brainstorming/content workspace |
| **Advanced Data Analysis** | Code execution for data processing |
| **Web Search** | Real-time information retrieval |

### Implementation Requirements

- Feature toggles per project (enable/disable specific capabilities)
- Tool/capability inheritance from parent subscription tier
- Audit logging for feature usage

---

## 10. Known Limitations

### Current ChatGPT Projects Limitations

1. **No Collaboration**: Single-user only (major gap vs Claude)
2. **Limited Platform Support**: Web + Windows only
3. **No Cloud Storage Integration**: Can't connect OneDrive/Drive
4. **Model Lock-in**: GPT-4o only, no switching
5. **No Export/Import**: Projects can't be exported or shared as templates
6. **Conversation Reference Issues**: Limited ability to accurately reference past conversations within projects
7. **Visual Generation Limits**: Restricted compared to standalone DALL-E
8. **No Offline Mode**: Requires internet connection

### Competitive Opportunities

These limitations present opportunities for differentiation:
- **Add collaboration from day one**
- **Full cross-platform support**
- **Cloud storage integration (Google Drive, Dropbox, OneDrive)**
- **Model flexibility within projects**
- **Project templates and sharing**
- **Better conversation memory/reference**
- **Offline mode for desktop apps**

---

## 11. Privacy Considerations

### How It Works in ChatGPT

| Aspect | Details |
|--------|---------|
| **Training Data** | User must manually opt out (unless Teams plan) |
| **Data Retention** | Conversations retained per OpenAI privacy policy |
| **Encryption** | Standard OpenAI security measures |

### Competitor Advantage: Claude

Claude excludes user data from model training BY DEFAULT.

### Implementation Requirements

- Clear privacy policy for project data
- Data retention controls (auto-delete options)
- Export my data functionality
- Training opt-out (or opt-in) toggle
- End-to-end encryption option for sensitive projects

---

## 12. Use Cases

### Primary Use Cases (from Research)

1. **Event Planning**: Gather all event-related chats, vendor info, timelines
2. **Coding Projects**: Code files, documentation, debugging conversations
3. **Client Work**: Per-client projects with relevant context
4. **Content Creation**: Writing projects with style guides, drafts, revisions
5. **Research**: Academic or market research with source materials
6. **Household Management**: Recipes, shopping lists, home projects
7. **Learning**: Course materials, study notes, tutoring conversations

---

## 13. Implementation Priority Matrix

### Must Have (P0)

| Feature | Rationale |
|---------|-----------|
| Project creation/deletion | Core functionality |
| File uploads within projects | Context management |
| Project-scoped conversations | Organization |
| Custom instructions per project | Personalization |
| Color/visual customization | UX polish |

### Should Have (P1)

| Feature | Rationale |
|---------|-----------|
| Move existing chats to projects | Workflow integration |
| Project-scoped search | Discoverability |
| Cross-platform support | Accessibility |
| Storage quota management | Operational |

### Nice to Have (P2)

| Feature | Rationale |
|---------|-----------|
| Project sharing/collaboration | Differentiator |
| Project templates | Power users |
| Cloud storage integration | Convenience |
| Export/import projects | Portability |
| Offline mode | Resilience |

---

## 14. Database Schema Proposal

```sql
-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    color VARCHAR(7), -- Hex color code
    instructions TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP -- Soft delete
);

-- Project Files
CREATE TABLE project_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(127),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Chat-Project Association
ALTER TABLE chats ADD COLUMN project_id UUID REFERENCES projects(id);

-- Project Collaborators (for future sharing)
CREATE TABLE project_collaborators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(50) DEFAULT 'viewer', -- owner, editor, viewer
    invited_at TIMESTAMP DEFAULT NOW(),
    accepted_at TIMESTAMP,
    UNIQUE(project_id, user_id)
);
```

---

## 15. API Endpoints Proposal

```
POST   /api/v1/projects              # Create project
GET    /api/v1/projects              # List user's projects
GET    /api/v1/projects/:id          # Get project details
PATCH  /api/v1/projects/:id          # Update project (name, color, instructions)
DELETE /api/v1/projects/:id          # Delete project

POST   /api/v1/projects/:id/files    # Upload file to project
GET    /api/v1/projects/:id/files    # List project files
DELETE /api/v1/projects/:id/files/:fileId # Delete file

GET    /api/v1/projects/:id/chats    # List project conversations
POST   /api/v1/chats/:chatId/move    # Move chat to project

# Future: Collaboration
POST   /api/v1/projects/:id/collaborators  # Invite collaborator
DELETE /api/v1/projects/:id/collaborators/:userId # Remove collaborator
```

---

## Summary

ChatGPT Projects provides organizational infrastructure for AI workflows with:

**Strengths**:
- Clean, simple UX for project creation
- File scoping to specific projects
- Custom instructions that override account defaults
- Integration with ChatGPT's broader feature set

**Weaknesses** (Opportunities for Competitors):
- No collaboration/sharing
- Limited platform support
- No cloud storage integration
- Model locked to GPT-4o
- Privacy requires manual opt-out

**Key Implementation Insight**: The feature is relatively straightforward technically - the value is in execution quality and addressing the gaps (especially collaboration and cross-platform support).

---

## Research Methodology Note

This analysis was compiled from web research sources including:
- geeky-gadgets.com
- allthings.how
- clickup.com/blog

Direct UI testing was not possible in the current environment. For complete validation, recommend hands-on testing through the ChatGPT web interface.

---

*Document created by browser-vision-tester agent for competitive analysis purposes.*
