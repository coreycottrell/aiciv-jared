# Claude Max Prompt: Pure Brain Portal Feature Upgrade

## INSTRUCTIONS FOR CLAUDE MAX

**Important**: Use this in the SAME Claude Max conversation where you built the Pure Brain Portal. Claude already has the code in context from when it built it.

Copy each part below into Claude Max one at a time. Start with Part 1.

---

## PART 1: CONTEXT & SETUP

```
I want to continue upgrading the Pure Brain Portal that you built for me. We need to add professional features to match ChatGPT, Gemini, and Claude.ai quality.

You already have the code in this conversation from when you built it. The portal is live at: https://puremarketing.ai/pure-brain-2-2/

Quick reminder of our brand standards:

BRAND COLORS:
- Bright Orange: #f1420b
- Orange: #ed6626
- Light Blue: #2a93c1
- Dark Blue: #3a60ab
- Black: #0a0a0a
- Card BG: rgba(20, 20, 20, 0.95)

FONTS:
- Headings: 'Oswald', sans-serif
- Body: 'Plus Jakarta Sans', sans-serif
- Code: 'JetBrains Mono', monospace

I'm going to request several feature upgrades one at a time. Each feature should integrate cleanly with the existing code you built.

Please confirm you remember the Pure Brain Portal code and are ready to add features.
```

---

## PART 2: FEATURE AUDIT

```
Before we add new features, please review what you already built for the Pure Brain Portal and tell me:

1. Current chat functionality - what's implemented?
2. Message rendering system - how are messages displayed?
3. Sidebar structure - what's there?
4. Artifact panel - is there one? How does it work?
5. API integration - how does it connect to Claude?

Based on this, identify which of these features are ALREADY implemented vs MISSING:
- Markdown rendering in messages
- Code blocks with syntax highlighting
- Copy button on code blocks
- Message actions (copy, edit, regenerate)
- Typing/thinking indicator
- Keyboard shortcuts
- Conversation history in sidebar
- Dark/Light mode toggle

List what we need to add.
```

---

## PART 3: ADD MARKDOWN RENDERING

```
FEATURE REQUEST: Add full Markdown rendering to AI messages.

Requirements:
1. Parse markdown in AI responses using a lightweight parser
2. Support: **bold**, *italic*, `inline code`, headers (#, ##, ###), bullet lists, numbered lists, blockquotes, horizontal rules, and links
3. Code blocks with ```language``` should trigger syntax highlighting
4. Links should open in new tabs with rel="noopener noreferrer"
5. Preserve the existing message bubble styling
6. Handle edge cases (empty content, malformed markdown)

Implementation approach:
- Add a parseMarkdown() function that converts markdown to HTML
- Call this function when rendering AI messages
- Style the rendered elements to match the dark theme

Please provide the complete updated JavaScript code for the message rendering section, plus any CSS additions needed.
```

---

## PART 4: ADD CODE BLOCKS WITH SYNTAX HIGHLIGHTING

```
FEATURE REQUEST: Professional code blocks with syntax highlighting and copy button.

Requirements:
1. Detect code blocks in messages (```language ... ```)
2. Apply syntax highlighting using highlight.js (CDN: https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js)
3. Show language label in top-left corner of code block
4. Add "Copy" button in top-right that:
   - Shows "Copy" by default
   - Shows "Copied!" for 2 seconds after click
   - Uses navigator.clipboard API
5. Dark theme for code (GitHub Dark or similar)
6. Horizontal scroll for long lines (no word wrap)
7. Rounded corners, subtle border matching card style

Styling requirements:
- Background: rgba(0, 0, 0, 0.4)
- Border: 1px solid rgba(255, 255, 255, 0.1)
- Border radius: 12px
- Font: 'JetBrains Mono', monospace
- Font size: 14px

Please provide:
1. The CDN links to add to <head>
2. Updated parseMarkdown function with code block handling
3. CSS for code blocks
4. Copy button functionality
```

---

## PART 5: ADD MESSAGE ACTIONS (COPY, EDIT, REGENERATE)

```
FEATURE REQUEST: Message action buttons for better UX.

Requirements for AI messages:
1. Copy button - copies entire message text (strips HTML)
2. Regenerate button - icon to regenerate response
3. Thumbs up/down feedback buttons
4. Actions appear on hover (always visible on mobile)
5. Position below the message bubble

Requirements for User messages:
1. Edit button - allows editing the message
2. When edit clicked: transform message into textarea with original text
3. Show "Save" and "Cancel" buttons
4. On save: update message and trigger new AI response
5. Show small "edited" label on edited messages

Styling:
- Action buttons: small, subtle, icon-based
- Use SVG icons (provide inline SVGs)
- Hover state: slight highlight
- Active/clicked state: brief animation

Please provide the complete HTML structure for message actions, CSS, and JavaScript event handlers.
```

---

## PART 6: ADD TYPING INDICATOR WITH ELAPSED TIME

```
FEATURE REQUEST: Enhanced typing/thinking indicator.

Requirements:
1. Three bouncing dots animation (like iMessage)
2. Text: "[AI Name] is thinking..."
3. After 10 seconds, show elapsed time: "Still thinking... (15s)"
4. Update every second after 10s threshold
5. Smooth fade-in when appearing
6. Match AI message bubble styling
7. Show AI avatar next to indicator

Animation specs:
- Dots: 6px circles, staggered bounce animation
- Bounce height: 4px
- Animation duration: 1.4s
- Stagger delay: 0.2s between dots

Please provide:
1. HTML structure for typing indicator
2. CSS animations
3. JavaScript to show/hide and track elapsed time
4. Integration with sendMessage function
```

---

## PART 7: ADD KEYBOARD SHORTCUTS

```
FEATURE REQUEST: Keyboard shortcuts for power users.

Shortcuts to implement:
1. Enter - Send message (when input focused)
2. Shift+Enter - New line in message
3. Cmd/Ctrl+N - New conversation
4. Cmd/Ctrl+K - Focus search (future feature, just show toast for now)
5. Escape - Close any open modal/panel
6. Cmd/Ctrl+/ - Toggle keyboard shortcuts help modal

Requirements:
1. Create a keyboard shortcut handler
2. Show shortcuts in a help modal (triggered by ? or Cmd+/)
3. Display shortcut hints in UI where relevant (e.g., "Enter to send")
4. Handle both Mac (Cmd) and Windows (Ctrl) modifiers
5. Don't trigger shortcuts when typing in input fields (except Enter/Shift+Enter)

Please provide:
1. JavaScript keyboard event listener
2. Shortcuts help modal HTML and CSS
3. Any UI updates needed to show shortcut hints
```

---

## PART 8: ADD COLLAPSIBLE SIDEBAR WITH CONVERSATION HISTORY

```
FEATURE REQUEST: Functional collapsible sidebar with real conversation history.

Requirements:
1. Sidebar collapses to icon-only mode (56px width)
2. Smooth animation on collapse/expand (300ms ease)
3. Persist collapse state to localStorage
4. Save conversations to localStorage with:
   - ID, title (first user message truncated), messages array, timestamp
5. Group conversations by: Today, Yesterday, Previous 7 Days, Older
6. Each conversation shows:
   - Title (truncated to 30 chars)
   - Relative timestamp
   - Delete button on hover (with confirmation)
7. Click conversation to load it
8. Active conversation highlighted
9. "New Chat" button always visible
10. Maximum 50 conversations stored (delete oldest when exceeded)

Data structure:
```javascript
{
  id: "conv_" + timestamp,
  title: "First message truncated...",
  messages: [{role, content, timestamp}],
  createdAt: ISO timestamp,
  updatedAt: ISO timestamp
}
```

Please provide complete sidebar HTML, CSS, and JavaScript for conversation management.
```

---

## PART 9: ADD ARTIFACTS PANEL IMPROVEMENTS

```
FEATURE REQUEST: Enhanced artifacts panel with better preview and editing.

Requirements:
1. Live HTML/CSS/JS preview in iframe
2. Syntax-highlighted code view with line numbers
3. Tabs: Preview | Code | (future: React, Mermaid)
4. Download button - saves artifact as .html file
5. Fullscreen button - opens in new window
6. Copy code button
7. Panel remembers open/closed state
8. Smooth slide-in animation when artifact created
9. Auto-detect artifact in AI response using pattern:
   <artifact type="html" title="Title">...code...</artifact>

Panel styling:
- Width: 50% of main area when open
- Subtle border-left separator
- Tabs with underline indicator
- Code view with dark background

Please provide updated artifact panel code with all features.
```

---

## PART 10: ADD DARK/LIGHT MODE TOGGLE

```
FEATURE REQUEST: Theme toggle with system preference detection.

Requirements:
1. Toggle button in sidebar footer or header
2. Sun icon for light mode, moon icon for dark mode
3. Detect system preference on first load (prefers-color-scheme)
4. Save preference to localStorage
5. Smooth transition when switching (300ms on background-color)
6. CSS variables for all theme colors

Light mode colors:
- Background: #fafaf9
- Card BG: #ffffff
- Text: #1a1a1a
- Muted text: #666666
- Borders: rgba(0, 0, 0, 0.1)
- Keep brand colors (orange, blue) the same

Dark mode colors (current):
- Background: #0a0a0a
- Card BG: rgba(20, 20, 20, 0.95)
- Text: rgba(255, 255, 255, 0.95)
- Muted: rgba(255, 255, 255, 0.5)
- Borders: rgba(255, 255, 255, 0.1)

Please provide:
1. CSS variables setup
2. Light mode class overrides
3. Toggle button component
4. JavaScript for theme management
```

---

## PART 11: FINAL INTEGRATION & TESTING

```
Now please provide a COMPLETE, FINAL HTML file that integrates ALL the features we've added:

1. Markdown rendering in messages
2. Code blocks with syntax highlighting and copy
3. Message actions (copy, edit, regenerate, feedback)
4. Enhanced typing indicator with elapsed time
5. Keyboard shortcuts with help modal
6. Collapsible sidebar with conversation history
7. Enhanced artifacts panel
8. Dark/Light mode toggle

The final file should:
- Be a single, self-contained HTML file
- Include all CSS inline in <style> tags
- Include all JavaScript inline in <script> tags
- Use CDN links for external libraries (highlight.js, fonts)
- Work standalone when opened in browser
- Connect to the existing Cloudflare Worker API for Claude
- Be production-ready

Please output the complete HTML file.
```

---

## USAGE INSTRUCTIONS

1. **Use the SAME Claude Max conversation** where you built the Pure Brain Portal (Claude already has the code)
2. Copy Part 1 and send it - Claude will confirm it remembers the code
3. Send Part 2 - Claude will audit existing features and identify gaps
4. Send Parts 3-10 one at a time for each feature upgrade
5. Claude will provide code that integrates with what it already built
6. Part 11 asks for the complete integrated file
7. Save the final output as a new HTML file and test

## NOTES

- **Must use same conversation** - Claude needs the code context from when it built the portal
- If Claude's response gets cut off, say "please continue"
- If a feature conflicts with existing code, ask Claude to resolve it
- Test each feature individually before moving to the next
- The final integrated file in Part 11 is the production version
