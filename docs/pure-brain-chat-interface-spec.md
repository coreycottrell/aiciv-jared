# Pure Brain Chat Interface - Component Specification

**Agent**: feature-designer
**Domain**: UX Design, Component Specifications
**Date**: 2026-02-04

---

## Overview

This specification defines the visual design and interaction patterns for the Pure Brain chat interface. Components are designed to align with the established Pure Marketing brand while creating an immersive, intelligent AI conversation experience.

---

## Design Tokens

### Colors

```css
/* Primary Brand Colors */
--pb-orange: #f1420b;
--pb-orange-hover: #ff5722;
--pb-orange-muted: rgba(241, 66, 11, 0.15);

--pb-blue: #2a93c1;
--pb-blue-hover: #3ba5d3;
--pb-blue-muted: rgba(42, 147, 193, 0.15);

/* Backgrounds */
--pb-bg-primary: #0a0a0a;
--pb-bg-elevated: #111111;
--pb-bg-surface: #1a1a1a;
--pb-bg-overlay: rgba(10, 10, 10, 0.95);

/* Text */
--pb-text-primary: #ffffff;
--pb-text-secondary: #b0b0b0;
--pb-text-muted: #888888;
--pb-text-disabled: #555555;

/* Borders */
--pb-border-subtle: rgba(255, 255, 255, 0.08);
--pb-border-default: rgba(255, 255, 255, 0.12);
--pb-border-strong: rgba(255, 255, 255, 0.2);

/* Shadows */
--pb-shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
--pb-shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
--pb-shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
--pb-shadow-glow-orange: 0 0 20px rgba(241, 66, 11, 0.3);
--pb-shadow-glow-blue: 0 0 20px rgba(42, 147, 193, 0.3);
```

### Typography

```css
/* Font Family */
--pb-font-heading: 'Oswald', sans-serif;
--pb-font-body: 'Plus Jakarta Sans', sans-serif;
--pb-font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Font Sizes */
--pb-text-xs: 0.75rem;    /* 12px */
--pb-text-sm: 0.875rem;   /* 14px */
--pb-text-base: 1rem;     /* 16px */
--pb-text-lg: 1.125rem;   /* 18px */
--pb-text-xl: 1.25rem;    /* 20px */
--pb-text-2xl: 1.5rem;    /* 24px */
--pb-text-3xl: 2rem;      /* 32px */

/* Font Weights */
--pb-font-light: 300;
--pb-font-regular: 400;
--pb-font-medium: 500;
--pb-font-semibold: 600;
--pb-font-bold: 700;

/* Line Heights */
--pb-leading-tight: 1.25;
--pb-leading-normal: 1.5;
--pb-leading-relaxed: 1.75;
```

### Spacing

```css
/* Spacing Scale (4px base) */
--pb-space-1: 0.25rem;   /* 4px */
--pb-space-2: 0.5rem;    /* 8px */
--pb-space-3: 0.75rem;   /* 12px */
--pb-space-4: 1rem;      /* 16px */
--pb-space-5: 1.25rem;   /* 20px */
--pb-space-6: 1.5rem;    /* 24px */
--pb-space-8: 2rem;      /* 32px */
--pb-space-10: 2.5rem;   /* 40px */
--pb-space-12: 3rem;     /* 48px */
--pb-space-16: 4rem;     /* 64px */
```

### Border Radius

```css
--pb-radius-sm: 6px;
--pb-radius-md: 12px;
--pb-radius-lg: 16px;
--pb-radius-xl: 20px;
--pb-radius-2xl: 24px;
--pb-radius-full: 9999px;
```

### Transitions

```css
--pb-transition-fast: 150ms ease;
--pb-transition-base: 250ms ease;
--pb-transition-slow: 400ms ease;
--pb-transition-bounce: 400ms cubic-bezier(0.34, 1.56, 0.64, 1);
```

---

## Component 1: Message Bubble

### Overview
Message bubbles display individual messages in the conversation. User and AI messages have distinct visual treatments.

### Structure

```
+------------------------------------------+
|  [Avatar]  Message Content               |
|            Additional content...         |
|            12:34 PM                       |
+------------------------------------------+
```

### User Message Bubble

**Container**
- Background: `linear-gradient(135deg, #f1420b, #ff5722)`
- Border Radius: `20px 20px 4px 20px` (rounded except bottom-right)
- Padding: `16px 20px`
- Max Width: `75%` of chat container
- Alignment: Right-aligned
- Margin: `8px 0`
- Box Shadow: `var(--pb-shadow-md)`

**Typography**
- Font: `var(--pb-font-body)`
- Size: `var(--pb-text-base)` (16px)
- Weight: `var(--pb-font-regular)`
- Color: `#ffffff`
- Line Height: `var(--pb-leading-normal)`

**Timestamp**
- Font Size: `var(--pb-text-xs)` (12px)
- Color: `rgba(255, 255, 255, 0.7)`
- Alignment: Right
- Margin Top: `6px`

**States**
```css
/* Default */
.message-user {
  background: linear-gradient(135deg, #f1420b, #ff5722);
  box-shadow: 0 4px 16px rgba(241, 66, 11, 0.3);
}

/* Sending (animated) */
.message-user--sending {
  opacity: 0.7;
  animation: pulse 1.5s ease-in-out infinite;
}

/* Error */
.message-user--error {
  border: 2px solid #ff4444;
  position: relative;
}

.message-user--error::after {
  content: "!";
  position: absolute;
  right: -8px;
  top: -8px;
  width: 20px;
  height: 20px;
  background: #ff4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}
```

### AI Message Bubble

**Container**
- Background: `var(--pb-bg-surface)` (#1a1a1a)
- Border: `1px solid var(--pb-border-subtle)`
- Border Radius: `20px 20px 20px 4px` (rounded except bottom-left)
- Padding: `16px 20px`
- Max Width: `80%` of chat container
- Alignment: Left-aligned
- Margin: `8px 0`
- Box Shadow: `var(--pb-shadow-sm)`

**Avatar**
- Size: `36px x 36px`
- Shape: Circle
- Background: `linear-gradient(135deg, #2a93c1, #3a60ab)`
- Icon: Pure Brain logo or "PB" initials
- Position: Left of message, vertically aligned to top
- Gap from message: `12px`

**Typography**
- Font: `var(--pb-font-body)`
- Size: `var(--pb-text-base)` (16px)
- Weight: `var(--pb-font-regular)`
- Color: `var(--pb-text-primary)` (#ffffff)
- Line Height: `var(--pb-leading-relaxed)`

**Code Blocks (within AI messages)**
- Background: `#0d0d0d`
- Border: `1px solid var(--pb-border-subtle)`
- Border Radius: `var(--pb-radius-md)` (12px)
- Padding: `16px`
- Font: `var(--pb-font-mono)`
- Font Size: `var(--pb-text-sm)` (14px)
- Color: `#e0e0e0`
- Overflow: `auto` with custom scrollbar

**States**
```css
/* Typing indicator */
.message-ai--typing {
  display: flex;
  gap: 6px;
  padding: 16px 24px;
}

.message-ai--typing .dot {
  width: 8px;
  height: 8px;
  background: var(--pb-blue);
  border-radius: 50%;
  animation: typing-bounce 1.4s ease-in-out infinite;
}

.message-ai--typing .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.message-ai--typing .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-8px); opacity: 1; }
}

/* Streaming (text appearing) */
.message-ai--streaming {
  border-left: 2px solid var(--pb-blue);
}

.message-ai--streaming::after {
  content: "";
  display: inline-block;
  width: 2px;
  height: 1em;
  background: var(--pb-blue);
  margin-left: 2px;
  animation: cursor-blink 1s step-end infinite;
}

@keyframes cursor-blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
```

### Accessibility
- Messages use `role="listitem"` within a `role="list"` container
- Screen reader announces "You said:" for user messages, "Pure Brain said:" for AI
- Timestamps use `<time>` element with `datetime` attribute
- Focus indicator: `2px solid var(--pb-orange)` with `4px` offset

---

## Component 2: Input Bar

### Overview
The input bar allows users to type and send messages. It includes a text area, send button, and optional attachment controls.

### Structure

```
+------------------------------------------------------------+
|  [+]  | Type your message...                    | [Send ->] |
+------------------------------------------------------------+
```

### Container

**Dimensions**
- Height: `auto` (min 56px, max 200px based on content)
- Width: `100%`
- Position: Fixed to bottom of chat area
- Padding: `12px 16px`
- Background: `var(--pb-bg-elevated)` with backdrop blur
- Border Top: `1px solid var(--pb-border-subtle)`

```css
.input-bar {
  position: sticky;
  bottom: 0;
  width: 100%;
  min-height: 56px;
  max-height: 200px;
  padding: 12px 16px;
  background: rgba(17, 17, 17, 0.9);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: flex-end;
  gap: 12px;
}
```

### Text Input

**Container**
- Background: `var(--pb-bg-surface)`
- Border: `1px solid var(--pb-border-default)`
- Border Radius: `var(--pb-radius-xl)` (20px)
- Padding: `12px 20px`
- Flex: `1` (fills available space)

**Typography**
- Font: `var(--pb-font-body)`
- Size: `var(--pb-text-base)` (16px)
- Color: `var(--pb-text-primary)`
- Placeholder Color: `var(--pb-text-muted)`
- Line Height: `var(--pb-leading-normal)`

**States**
```css
/* Default */
.input-field {
  background: #1a1a1a;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 12px 20px;
  color: #ffffff;
  transition: border-color 250ms ease, box-shadow 250ms ease;
}

/* Focus */
.input-field:focus {
  outline: none;
  border-color: var(--pb-blue);
  box-shadow: 0 0 0 3px rgba(42, 147, 193, 0.2);
}

/* Hover */
.input-field:hover:not(:focus) {
  border-color: rgba(255, 255, 255, 0.2);
}

/* Disabled */
.input-field:disabled {
  background: #0d0d0d;
  color: var(--pb-text-disabled);
  cursor: not-allowed;
}

/* Error */
.input-field--error {
  border-color: #ff4444;
  box-shadow: 0 0 0 3px rgba(255, 68, 68, 0.2);
}
```

### Send Button

**Dimensions**
- Size: `48px x 48px`
- Border Radius: `var(--pb-radius-full)` (circle)

**Appearance**
- Background: `linear-gradient(135deg, #f1420b, #ff5722)`
- Icon: Arrow right (24px)
- Icon Color: `#ffffff`

**States**
```css
/* Default */
.send-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f1420b, #ff5722);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 150ms ease, box-shadow 250ms ease;
}

/* Hover */
.send-button:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(241, 66, 11, 0.4);
}

/* Active */
.send-button:active {
  transform: scale(0.95);
}

/* Disabled (no text in input) */
.send-button:disabled {
  background: #333333;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Loading */
.send-button--loading {
  pointer-events: none;
}

.send-button--loading .icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### Attachment Button (Optional)

**Dimensions**
- Size: `40px x 40px`
- Border Radius: `var(--pb-radius-full)` (circle)

**Appearance**
- Background: `transparent`
- Border: `1px solid var(--pb-border-default)`
- Icon: Plus (20px)
- Icon Color: `var(--pb-text-muted)`

**States**
```css
/* Default */
.attach-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: var(--pb-text-muted);
  transition: all 250ms ease;
}

/* Hover */
.attach-button:hover {
  border-color: var(--pb-blue);
  color: var(--pb-blue);
  background: rgba(42, 147, 193, 0.1);
}

/* Active (menu open) */
.attach-button--active {
  background: var(--pb-blue);
  border-color: var(--pb-blue);
  color: #ffffff;
}
```

### Accessibility
- Input has `aria-label="Type your message"`
- Send button has `aria-label="Send message"`
- Keyboard: Enter sends, Shift+Enter for new line
- Focus trap within input bar when active
- Screen reader announces character count near limit

---

## Component 3: Sidebar Navigation

### Overview
Collapsible sidebar for conversation history, settings, and navigation.

### Structure

```
+------------------------+
| [=] PURE BRAIN         |
+------------------------+
| + New Chat             |
+------------------------+
| Recent                 |
| > Today's project...   |
| > Marketing strategy...|
| > API integration...   |
+------------------------+
| History                |
| > Yesterday            |
| > Last 7 days          |
+------------------------+
|                        |
|                        |
+------------------------+
| [Settings] [Profile]   |
+------------------------+
```

### Container

**Dimensions**
- Width: `280px` (expanded), `72px` (collapsed)
- Height: `100vh`
- Position: Fixed left

**Appearance**
- Background: `var(--pb-bg-primary)` (#0a0a0a)
- Border Right: `1px solid var(--pb-border-subtle)`
- Box Shadow: `4px 0 16px rgba(0, 0, 0, 0.3)` (when overlapping content)

```css
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 280px;
  height: 100vh;
  background: #0a0a0a;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  transition: width 300ms ease, transform 300ms ease;
  z-index: 100;
}

/* Collapsed state */
.sidebar--collapsed {
  width: 72px;
}

/* Mobile (overlay) */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    box-shadow: 4px 0 16px rgba(0, 0, 0, 0.5);
  }

  .sidebar--open {
    transform: translateX(0);
  }
}
```

### Header

**Dimensions**
- Height: `64px`
- Padding: `16px 20px`

**Content**
- Logo: Pure Brain icon (32px)
- Title: "PURE BRAIN" (hidden when collapsed)
- Toggle Button: Hamburger/Close icon

```css
.sidebar-header {
  height: 64px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-header__logo {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.sidebar-header__title {
  font-family: var(--pb-font-heading);
  font-size: var(--pb-text-lg);
  font-weight: var(--pb-font-semibold);
  color: var(--pb-text-primary);
  white-space: nowrap;
  overflow: hidden;
  transition: opacity 200ms ease;
}

.sidebar--collapsed .sidebar-header__title {
  opacity: 0;
  width: 0;
}
```

### New Chat Button

**Dimensions**
- Height: `48px`
- Margin: `16px`
- Border Radius: `var(--pb-radius-lg)` (16px)

**Appearance**
- Background: `linear-gradient(135deg, #f1420b, #ff5722)`
- Full width

```css
.new-chat-button {
  margin: 16px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f1420b, #ff5722);
  border: none;
  color: #ffffff;
  font-family: var(--pb-font-body);
  font-size: var(--pb-text-sm);
  font-weight: var(--pb-font-semibold);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: transform 150ms ease, box-shadow 250ms ease;
}

.new-chat-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(241, 66, 11, 0.4);
}

.sidebar--collapsed .new-chat-button {
  width: 40px;
  height: 40px;
  margin: 16px auto;
  border-radius: 50%;
}

.sidebar--collapsed .new-chat-button span {
  display: none;
}
```

### Conversation List

**Section Header**
- Font: `var(--pb-font-body)`
- Size: `var(--pb-text-xs)` (12px)
- Weight: `var(--pb-font-semibold)`
- Color: `var(--pb-text-muted)`
- Text Transform: `uppercase`
- Letter Spacing: `0.05em`
- Padding: `16px 20px 8px`

**Conversation Item**
- Height: `44px`
- Padding: `0 20px`
- Border Radius: `var(--pb-radius-md)` (12px) with margin `0 8px`

```css
.conversation-section {
  padding: 8px 0;
}

.conversation-section__title {
  font-size: 12px;
  font-weight: 600;
  color: #888888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 16px 20px 8px;
}

.conversation-item {
  display: flex;
  align-items: center;
  height: 44px;
  padding: 0 12px;
  margin: 2px 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 150ms ease;
}

.conversation-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.conversation-item--active {
  background: rgba(42, 147, 193, 0.15);
  border-left: 3px solid var(--pb-blue);
}

.conversation-item__title {
  font-size: 14px;
  color: var(--pb-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.conversation-item--active .conversation-item__title {
  color: var(--pb-text-primary);
}

.conversation-item__icon {
  width: 20px;
  height: 20px;
  margin-right: 12px;
  color: var(--pb-text-muted);
  flex-shrink: 0;
}
```

### Footer

**Dimensions**
- Height: `64px`
- Padding: `12px 16px`
- Position: Sticky bottom

**Content**
- Settings icon button
- Profile avatar/button

```css
.sidebar-footer {
  margin-top: auto;
  height: 64px;
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar-footer__button {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--pb-text-muted);
  cursor: pointer;
  transition: all 200ms ease;
}

.sidebar-footer__button:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--pb-text-primary);
  border-color: rgba(255, 255, 255, 0.15);
}
```

### Accessibility
- Sidebar uses `role="navigation"` with `aria-label="Chat navigation"`
- Conversation list uses `role="listbox"` with `aria-activedescendant`
- Collapsed state announces via `aria-expanded="false"`
- Keyboard navigation: Tab through items, Enter to select
- Mobile: Overlay has focus trap, Escape closes

---

## Component 4: Header

### Overview
Top header with branding, status indicators, and quick actions.

### Structure

```
+------------------------------------------------------------+
| [=]  Pure Brain           [Status: Online]      [?] [User] |
+------------------------------------------------------------+
```

### Container

**Dimensions**
- Height: `64px`
- Width: `100%`
- Position: Fixed top

**Appearance**
- Background: `var(--pb-bg-elevated)` with backdrop blur
- Border Bottom: `1px solid var(--pb-border-subtle)`

```css
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(17, 17, 17, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  padding: 0 24px;
  z-index: 90;
}

/* When sidebar is open, offset header */
.header--sidebar-open {
  left: 280px;
}

@media (max-width: 768px) {
  .header--sidebar-open {
    left: 0;
  }
}
```

### Menu Toggle (Mobile/Collapsed)

**Dimensions**
- Size: `40px x 40px`
- Border Radius: `var(--pb-radius-md)` (12px)

```css
.header__menu-toggle {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: transparent;
  border: none;
  color: var(--pb-text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  transition: background 150ms ease;
}

.header__menu-toggle:hover {
  background: rgba(255, 255, 255, 0.05);
}

/* Hide when sidebar is expanded on desktop */
@media (min-width: 769px) {
  .sidebar:not(.sidebar--collapsed) + .header .header__menu-toggle {
    display: none;
  }
}
```

### Title Section

**Content**
- Page/conversation title
- Optional subtitle or breadcrumb

```css
.header__title-section {
  flex: 1;
  min-width: 0;
}

.header__title {
  font-family: var(--pb-font-heading);
  font-size: var(--pb-text-lg);
  font-weight: var(--pb-font-semibold);
  color: var(--pb-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header__subtitle {
  font-size: var(--pb-text-xs);
  color: var(--pb-text-muted);
  margin-top: 2px;
}
```

### Status Indicator

**Appearance**
- Pill shape with dot indicator
- Colors: Green (online), Yellow (thinking), Red (error), Gray (offline)

```css
.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.05);
  font-size: 12px;
  color: var(--pb-text-secondary);
}

.status-indicator__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

/* Online */
.status-indicator--online .status-indicator__dot {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

/* Thinking */
.status-indicator--thinking .status-indicator__dot {
  background: #f59e0b;
  animation: pulse-fast 0.8s ease-in-out infinite;
}

/* Error */
.status-indicator--error .status-indicator__dot {
  background: #ef4444;
}

/* Offline */
.status-indicator--offline .status-indicator__dot {
  background: #6b7280;
  animation: none;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes pulse-fast {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.2); }
}
```

### Action Buttons

**Dimensions**
- Size: `40px x 40px`
- Border Radius: `var(--pb-radius-md)` (12px)
- Gap between buttons: `8px`

```css
.header__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 16px;
}

.header__action-button {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--pb-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 200ms ease;
}

.header__action-button:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--pb-text-primary);
  border-color: rgba(255, 255, 255, 0.15);
}

/* Profile button with avatar */
.header__profile {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f1420b, #2a93c1);
  padding: 2px;
  cursor: pointer;
}

.header__profile-img {
  width: 100%;
  height: 100%;
  border-radius: 10px;
  object-fit: cover;
}
```

### Accessibility
- Header uses `role="banner"`
- Menu toggle has `aria-expanded` and `aria-controls`
- Status indicator has `role="status"` with `aria-live="polite"`
- Action buttons have descriptive `aria-label`

---

## Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 480px) {
  /* Smaller message bubbles */
  .message-user, .message-ai {
    max-width: 90%;
    padding: 12px 16px;
  }

  /* Full-width input */
  .input-bar {
    padding: 8px 12px;
  }

  /* Overlay sidebar */
  .sidebar {
    transform: translateX(-100%);
  }
}

/* Tablet */
@media (min-width: 481px) and (max-width: 768px) {
  .message-user, .message-ai {
    max-width: 85%;
  }

  .sidebar {
    transform: translateX(-100%);
  }
}

/* Desktop */
@media (min-width: 769px) {
  .main-content {
    margin-left: 280px;
  }

  .sidebar--collapsed + .main-content {
    margin-left: 72px;
  }
}

/* Large Desktop */
@media (min-width: 1200px) {
  .message-user {
    max-width: 60%;
  }

  .message-ai {
    max-width: 70%;
  }
}
```

---

## Animation Guidelines

### Entrance Animations

**Messages**
- New messages slide up and fade in
- Duration: 300ms
- Easing: `cubic-bezier(0.34, 1.56, 0.64, 1)` (bounce)

```css
@keyframes message-enter {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.message-enter {
  animation: message-enter 300ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
```

### Micro-interactions

**Button Press**
```css
.button:active {
  transform: scale(0.95);
  transition: transform 100ms ease;
}
```

**Focus Ring**
```css
:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(42, 147, 193, 0.4);
}
```

---

## Implementation Notes

### Performance Considerations
- Use `will-change` sparingly, only on actively animating elements
- Prefer `transform` and `opacity` for animations
- Use `backdrop-filter` with caution on mobile
- Virtualize long conversation lists

### Dark Mode
- This spec is dark-mode first
- Light mode would require separate color tokens
- Consider user preference via `prefers-color-scheme`

### Integration Points
- Input bar should integrate with typing debounce
- Message streaming requires special text rendering
- Sidebar state should persist in localStorage
- Header status should reflect actual API connection

---

## Memory Written

Path: /home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/feature-designer/2026-02-04--pure-brain-chat-interface-spec.md
Type: pattern
Topic: Chat interface component specification for Pure Brain

Key learnings captured:
- Brand color integration (orange #f1420b for user actions, blue #2a93c1 for AI/system)
- Message bubble asymmetric radius pattern (rounded on 3 corners, flat on origin side)
- Typing indicator with bounce animation and three dots
- Sidebar collapse pattern (280px -> 72px with icon-only mode)
- Status indicator states (online/thinking/error/offline with color-coded dots)
- Backdrop blur for floating UI elements (headers, input bars)
