# Pure Brain Chat Interface Specification

**Date**: 2026-02-04
**Agent**: feature-designer
**Type**: pattern
**Topic**: Chat interface component specification for Pure Brain

---

## Context

Created comprehensive component specification for Pure Brain chat interface including:
- Message bubbles (user vs AI)
- Input bar with send/attachment buttons
- Sidebar navigation
- Header component

## Key Design Decisions

### Color Strategy
- **Orange (#f1420b)**: User actions, CTAs, user messages - creates warmth and energy
- **Blue (#2a93c1)**: AI/system elements, AI messages, focus states - creates trust and intelligence
- **Background (#0a0a0a)**: Near-black for depth, allows glow effects to pop

### Message Bubble Pattern
- Asymmetric border radius: rounded on 3 corners, flat on the corner pointing to sender
- User messages: bottom-right flat (pointing to their input)
- AI messages: bottom-left flat (pointing to AI avatar)
- This creates visual flow indicating message origin

### Typing Indicator
- Three dots with staggered bounce animation
- Blue color to indicate AI is working
- 1.4s animation cycle with 0.2s delays between dots

### Sidebar Collapse Pattern
- Full width: 280px
- Collapsed: 72px (icon-only mode)
- Mobile: Full overlay with transform slide
- Active conversation: left border accent + background highlight

### Floating UI Elements
- Use backdrop-filter: blur(20px) for glass effect
- Semi-transparent backgrounds (rgba with 0.9 alpha)
- Creates depth without hard edges

### Status Indicator States
1. **Online**: Green dot with glow, slow pulse
2. **Thinking**: Yellow/amber dot, fast pulse with scale
3. **Error**: Red dot, no animation
4. **Offline**: Gray dot, no animation

## Files Created

- `/home/jared/projects/AI-CIV/aether/docs/pure-brain-chat-interface-spec.md` - Full specification

## Reusable Patterns

### Design Token Structure
Organized tokens into logical groups:
- Colors (brand, backgrounds, text, borders)
- Typography (families, sizes, weights, line-heights)
- Spacing (4px base scale)
- Border radius (6px to full/pill)
- Transitions (150ms/250ms/400ms with easing)
- Shadows (sm/md/lg plus glow variants)

### State Definitions
For each component, defined:
- Default
- Hover
- Focus
- Active
- Disabled
- Loading (where applicable)
- Error (where applicable)

### Accessibility Patterns
- ARIA roles for semantic meaning
- Focus indicators (3px ring with brand color)
- Screen reader announcements
- Keyboard navigation support

## Future Considerations

- Light mode variant (would need inverse color tokens)
- Message reactions/actions menu
- File attachment preview states
- Message editing states
- Multi-select for bulk operations
- Voice input button state

---

**Confidence**: high
**Tags**: ux, component-spec, chat-interface, pure-brain, design-tokens
