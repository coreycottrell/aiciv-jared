# ChatGPT Settings - Comprehensive Breakdown

**Agent**: browser-vision-tester
**Domain**: Browser-based settings documentation
**Date**: 2026-02-05

---

## Research Methodology

Due to technical limitations (no desktop automation access in this environment, WebFetch blocked by OpenAI and many major tech sites with 403/404 errors), this documentation was compiled from multiple third-party sources including Zapier, IBM, Geeky Gadgets, 9to5Mac, 9to5Google, CIO, and TechRadar.

**Note**: For a COMPLETE and definitive settings audit, direct desktop automation access to ChatGPT.com with screenshots would be required. This document represents the most comprehensive compilation possible via web research.

---

## Settings Categories Overview

Based on research, ChatGPT settings are organized into these primary categories:

1. **Account & Profile**
2. **Personalization (Custom Instructions/Memory)**
3. **Data Controls & Privacy**
4. **Appearance & Interface**
5. **Voice & Audio**
6. **Subscription & Billing**
7. **Integrations & Connected Apps**
8. **Advanced Features**

---

## 1. Account & Profile Settings

### Setting: Email Address
- **Description**: Primary email for account login and notifications
- **Options/Values**: Email address input field
- **Implementation Notes**: Standard OAuth/email verification flow; support multiple auth methods (Google, Microsoft, Apple)

### Setting: Profile Name
- **Description**: Display name shown in the interface
- **Options/Values**: Free text input
- **Implementation Notes**: Used in personalization and shared conversation attribution

### Setting: Profile Picture
- **Description**: Avatar displayed in conversations
- **Options/Values**: Image upload or default avatar
- **Implementation Notes**: Standard image upload with crop/resize functionality

### Setting: Phone Number (Optional)
- **Description**: For account recovery and WhatsApp integration
- **Options/Values**: Phone number with country code
- **Implementation Notes**: SMS verification, enables 1-800-ChatGPT WhatsApp access

---

## 2. Personalization Settings

### Setting: Custom Instructions
- **Description**: Persistent instructions that apply to all conversations
- **Sub-settings**:
  - **"What would you like ChatGPT to know about you?"**
    - Description: Background context about the user
    - Options: Free text (character limit ~1500)
  - **"How would you like ChatGPT to respond?"**
    - Description: Desired response style/format
    - Options: Free text (character limit ~1500)
- **Implementation Notes**: System-level prompt injection; critical for personalization

### Setting: Memory
- **Description**: ChatGPT remembers information from past conversations
- **Options/Values**:
  - Toggle: On/Off
  - View saved memories
  - Delete individual memories
  - Clear all memories
- **Implementation Notes**:
  - NOT available in Europe and Korea (regulatory restrictions)
  - Stores user-approved facts for cross-conversation persistence
  - Users can explicitly tell ChatGPT to "remember" or "forget" things

### Setting: Response Format Preferences
- **Description**: Default output formatting preferences
- **Options/Values**:
  - Code formatting
  - Tables
  - Lists
  - Comma-separated values
  - Plain text
- **Implementation Notes**: Can be set via custom instructions or per-conversation

### Setting: Tone Preferences
- **Description**: Desired communication style
- **Options/Values**:
  - Formal/Professional
  - Casual/Friendly
  - Technical
  - Simple/Accessible
- **Implementation Notes**: Typically set via custom instructions

### Setting: Role Assignment
- **Description**: Default persona for ChatGPT
- **Options/Values**: Free text (e.g., "tutor", "technical expert", "writing assistant")
- **Implementation Notes**: System prompt customization

---

## 3. Data Controls & Privacy Settings

### Setting: Chat History & Training
- **Description**: Whether conversations are saved and used for model improvement
- **Options/Values**:
  - Toggle: Enable/Disable training on conversations
  - Note: Disabling may affect some features
- **Implementation Notes**: GDPR/privacy compliance critical; clear user consent flow

### Setting: Data Export
- **Description**: Download all personal data
- **Options/Values**: Export request button
- **Implementation Notes**: Standard data portability (GDPR Article 20); export format likely JSON/CSV

### Setting: Delete Account
- **Description**: Permanently delete account and all data
- **Options/Values**: Delete button with confirmation
- **Implementation Notes**: Multi-step confirmation; 30-day grace period typical

### Setting: Shared Links
- **Description**: Manage conversations shared via public links
- **Options/Values**:
  - View all shared links
  - Delete individual shared links
  - Disable sharing globally
- **Implementation Notes**: Shared conversations are view-only for recipients

### Setting: Third-Party Data Sharing
- **Description**: Control data shared with integrations
- **Options/Values**: Per-integration toggles
- **Implementation Notes**: Granular permission management for each connected service

---

## 4. Appearance & Interface Settings

### Setting: Theme
- **Description**: Visual appearance of the interface
- **Options/Values**:
  - Light mode
  - Dark mode
  - System (follows OS setting)
- **Implementation Notes**: CSS theme switching; respect prefers-color-scheme

### Setting: Sidebar Display
- **Description**: Show/hide conversation history sidebar
- **Options/Values**: Toggle visibility
- **Implementation Notes**: Responsive design consideration for mobile

### Setting: Chat Organization
- **Description**: Options for organizing past conversations
- **Options/Values**:
  - Rename conversations
  - Archive conversations
  - Delete conversations
  - Search conversation history (Cmd+K / Ctrl+K)
- **Implementation Notes**: Full-text search across conversation history

### Setting: Default Model
- **Description**: Preferred AI model for new conversations
- **Options/Values** (varies by subscription):
  - GPT-4o (general purpose)
  - GPT-4.5 (broader knowledge)
  - o1 (complex reasoning)
  - o3-mini (STEM/coding, faster)
  - o3-mini-high (coding, higher reasoning)
- **Implementation Notes**: Model selector in conversation; remember last used

---

## 5. Voice & Audio Settings

### Setting: Voice Mode
- **Description**: Enable voice-based conversations
- **Options/Values**: Toggle On/Off
- **Implementation Notes**:
  - Desktop voice feature being retired early 2026
  - Merged voice and chat modes (seamless switching)

### Setting: Voice Selection
- **Description**: Choose ChatGPT's speaking voice
- **Options/Values**: Multiple voice options (names vary)
- **Implementation Notes**: Voice synthesis selection; consider regional accents

### Setting: Voice Input Language
- **Description**: Language for speech recognition
- **Options/Values**: Supported languages dropdown
- **Implementation Notes**: Integration with speech-to-text services

### Setting: Auto-play Audio Responses
- **Description**: Automatically speak responses
- **Options/Values**: Toggle On/Off
- **Implementation Notes**: Accessibility consideration; mute controls

---

## 6. Subscription & Billing Settings

### Setting: Current Plan
- **Description**: View and manage subscription tier
- **Options/Values**:
  - Free (limited messages, GPT-4o mini access)
  - Plus ($20/month) - increased limits, voice mode, custom GPTs
  - Pro ($200/month) - unlimited reasoning, advanced features
  - Teams (per-seat pricing)
  - Enterprise (custom pricing)
- **Implementation Notes**: Stripe or similar payment processor integration

### Setting: Usage Limits
- **Description**: View current usage against plan limits
- **Options/Values**: Display current/max message counts
- **Implementation Notes**: Real-time usage tracking; warning notifications

### Setting: Payment Method
- **Description**: Credit card or payment details
- **Options/Values**: Card management interface
- **Implementation Notes**: PCI compliance required; support multiple cards

### Setting: Billing History
- **Description**: View past invoices
- **Options/Values**: Invoice list with download
- **Implementation Notes**: PDF invoice generation

---

## 7. Integrations & Connected Apps Settings

### Setting: Google Drive Integration
- **Description**: Access files from Google Drive (Plus+ only)
- **Options/Values**: Connect/Disconnect, permission scopes
- **Implementation Notes**: OAuth2 flow; file picker integration

### Setting: Apple Music Integration
- **Description**: Control music, create playlists
- **Options/Values**: Connect/Disconnect
- **Implementation Notes**: Apple Music API integration; playlist creation

### Setting: Apple Health Integration (ChatGPT Health)
- **Description**: Access health data for wellness guidance
- **Options/Values**: Connect/Disconnect, data category permissions
- **Implementation Notes**: HealthKit integration on iOS; MyFitnessPal supported

### Setting: Adobe Integration
- **Description**: Access Photoshop, Express, Acrobat tools
- **Options/Values**: Connect/Disconnect
- **Implementation Notes**: Free access to Adobe tools within ChatGPT

### Setting: Custom GPTs
- **Description**: Create and manage custom GPT configurations
- **Options/Values**:
  - Create new GPT
  - Edit existing GPTs
  - Publish to GPT Store
  - Delete GPTs
  - Upload knowledge files
- **Implementation Notes**: Full GPT builder interface; knowledge base upload

### Setting: Browser/Plugins
- **Description**: Enable web browsing and third-party plugins
- **Options/Values**: Toggle individual capabilities
- **Implementation Notes**: Web search integration; plugin ecosystem

---

## 8. Advanced Features Settings

### Setting: Code Interpreter
- **Description**: Enable Python code execution
- **Options/Values**: Toggle On/Off per conversation
- **Implementation Notes**: Sandboxed Python environment; file upload/download

### Setting: DALL-E Image Generation
- **Description**: Enable AI image creation
- **Options/Values**: Toggle On/Off
- **Implementation Notes**: Image generation quotas; content policy filters

### Setting: Web Browsing
- **Description**: Allow ChatGPT to search the internet
- **Options/Values**: Toggle On/Off
- **Implementation Notes**: Real-time web search since October 2024

### Setting: Canvas/Editor Mode
- **Description**: Edit responses in dedicated editor
- **Options/Values**: Enable canvas for writing/code
- **Implementation Notes**: Side-by-side editing interface

### Setting: Live Video Input
- **Description**: Use camera for visual context (mobile)
- **Options/Values**: Toggle permission
- **Implementation Notes**: Camera access; real-time image recognition

### Setting: Scheduling
- **Description**: Set reminders and scheduled tasks
- **Options/Values**: Task/reminder creation interface
- **Implementation Notes**: Push notification integration

---

## 9. Safety & Parental Controls

### Setting: Age Prediction
- **Description**: OpenAI determines content eligibility via usage patterns
- **Options/Values**: Automatic (not user-configurable)
- **Implementation Notes**: Behavioral analysis for content filtering

### Setting: Parental Controls
- **Description**: Content restrictions for younger users
- **Options/Values**: Enable/configure restrictions
- **Implementation Notes**: Implemented after high-profile incidents

### Setting: Mental Health Guardrails
- **Description**: Redirection to professional resources
- **Options/Values**: Automatic (not user-configurable)
- **Implementation Notes**: Trigger-based routing to crisis resources

---

## 10. Notification Settings

### Setting: Email Notifications
- **Description**: Receive updates via email
- **Options/Values**:
  - Product updates
  - Tips and suggestions
  - Research opportunities
  - Marketing emails
- **Implementation Notes**: Unsubscribe compliance (CAN-SPAM)

### Setting: Push Notifications (Mobile)
- **Description**: Mobile app notifications
- **Options/Values**: Toggle by notification type
- **Implementation Notes**: Firebase/APNs integration

---

## 11. Keyboard Shortcuts

### Setting: Enable Keyboard Shortcuts
- **Description**: Quick actions via keyboard
- **Known Shortcuts**:
  - `Cmd/Ctrl + K`: Search conversations
  - `Enter`: Send message
  - `Shift + Enter`: New line without sending
- **Implementation Notes**: Discoverable shortcuts help modal

---

## 12. Language & Localization

### Setting: Interface Language
- **Description**: UI language
- **Options/Values**: 80+ supported languages
- **Implementation Notes**: Full i18n support

### Setting: Response Language
- **Description**: Preferred language for AI responses
- **Options/Values**: Can be set via custom instructions
- **Implementation Notes**: Multilingual model capability

---

## Implementation Priority for Competing Platform

### Critical (Must Have Day 1)
1. Account/Authentication
2. Theme (Light/Dark/System)
3. Chat History Management
4. Data Controls (export, delete)
5. Model Selection
6. Basic Personalization (custom instructions equivalent)

### High Priority (Launch Soon)
7. Memory System
8. Voice Mode
9. Subscription Management
10. Keyboard Shortcuts
11. Search Functionality

### Medium Priority (Roadmap)
12. Integrations Framework
13. Custom GPTs/Agents
14. Code Interpreter
15. Image Generation
16. Web Browsing

### Lower Priority (Future)
17. Scheduling
18. Live Video
19. Third-party Plugins
20. Advanced Parental Controls

---

## Key Differentiators Observed

1. **Memory Feature**: Persistent cross-conversation memory with explicit user control
2. **Custom GPTs**: User-created specialized assistants
3. **Voice Mode Evolution**: Merged voice/chat with seamless switching
4. **Deep Integrations**: Apple Music, Health, Google Drive, Adobe
5. **Advertising Model**: Ads appearing for free tier users (new 2026)

---

## Gaps Requiring Direct Screenshot Verification

The following settings likely exist but could not be confirmed via web research:

1. Exact settings menu structure and navigation
2. Specific toggle locations and UI placement
3. Advanced developer settings (if any)
4. Enterprise-specific controls
5. Accessibility settings (screen reader support, font sizes)
6. Notification granularity
7. Session timeout settings
8. Multi-device session management

---

## Memory Written

**Path**: /home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/browser-vision-tester/2026-02-05--chatgpt-settings-research.md
**Type**: operational
**Topic**: ChatGPT settings research methodology and findings

---

**Document Status**: Research-based compilation
**Verification Needed**: Direct desktop automation access to ChatGPT.com for screenshot verification
**Next Steps**: If desktop-vision tools become available, revisit with screenshot documentation

---

*Generated by browser-vision-tester*
*Research sources: Zapier, IBM, Geeky Gadgets, 9to5Mac, 9to5Google, CIO, TechRadar*
