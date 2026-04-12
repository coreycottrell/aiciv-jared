# Memory: Portal Login Page — 7-Change Update from Jared's Annotated Screenshot

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Applying 7 annotated changes to purebrain-portal-login.html — branding, copy, footer glow

---

## File

`/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-login.html`
Lines: 1,164

Base: original file at same path. Jared sent annotated screenshot via Telegram.

---

## 7 Changes Applied

### 1. Heading
- Old: `Enter Your Portal`
- New: `Enter Your AI's Brain Stream`
- Note: Left a comment in HTML showing where `window.AI_NAME` variable can be injected for dynamic AI name

### 2. Subtext
- Old: `Your AI civilization is waiting. 30+ specialized agents ready to work.`
- New: `Your AI's Neural Network is waiting. 50+ specialized agents ready to work.`
- Note: 50+ not 30+. Neural Network framing.

### 3. Logo Brand Colors (CORRECTED)
- PURE: was `--dark-blue` (#3a60ab) → now `#2a93c1` (light-blue per spec)
- BRAIN: was `--orange` (#ed6626) → now `#f1420b` (bright-orange per spec)
- .ai: white (unchanged)
- Also applied same colors to footer powered-by brand spans

### 4. Orb Icon
- Already present: `.pb-logo-mark` (52px CSS glass orb at top)
- No change needed — confirmed present

### 5. Field Label + Placeholder
- Old: `AiCIV Name` (both label text and placeholder attr)
- New: `Your AI's Name` (both label and placeholder)
- PRESERVED: `id="loginAicivName"` unchanged (interface compatibility)

### 6. Footer — Added PURETECHNOLOGY.AI
- Old: `Powered by PureBrain.ai`
- New: `POWERED BY PUREBRAIN.AI & PURETECHNOLOGY.AI`
- Styling: PURE=blue, BRAIN=orange, .AI=white/60%, separator &=muted, PURETECHNOLOGY.AI=white/55%
- Used `pb-brand-*` CSS classes for each segment

### 7. Bottom Section — Make It Pop
- Added `.pb-footer-glow-bar` — 1px top border with orange-to-blue gradient
- Added animated radial glow in `.pb-footer-inner::before` (`footerGlowPulse` 4s)
- Gradient background on `.pb-footer-inner` (blue → orange → dark)
- "AI Partnership. Redefined." → now `pb-footer-tagline` with:
  - Orange-to-blue gradient text via `-webkit-background-clip: text`
  - `taglineGlow` animation (3s) with drop-shadow filter (orange + blue)
  - Oswald heading font, 17px, uppercase, letter-spacing
- Card padding restructure: moved to `.pb-card-content` wrapper (38px padding removed from card, added to content div)
- `.pb-footer` gets `overflow: hidden` + border-radius to clip the gradient

---

## Architecture Note: Card Padding Restructure

To allow the footer to extend edge-to-edge (no side padding), restructured card:
- `pb-login-card`: padding changed to `48px 40px 0` (removed bottom padding)
- New `.pb-card-content`: `padding-bottom: 36px` (wraps logo through escape hatch)
- `.pb-footer`: sits outside `.pb-card-content`, directly in card

This allows the glow background to span the full card width.

---

## Interface IDs Preserved (All Intact)

| ID | Preserved |
|----|-----------|
| `loginOverlay` | YES |
| `loginAicivName` | YES |
| `loginSecret` | YES |
| `loginError` | YES |
| `loginButton` | YES |
| `handleLogin()` | YES |
| `openSettingsModal()` escape hatch | YES |

---

## Key CSS Patterns

### Gradient Text (tagline)
```css
background: linear-gradient(100deg, #f1420b 0%, #ed6626 30%, #2a93c1 70%, #3a60ab 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
filter: drop-shadow(0 0 12px rgba(241,66,11,0.5)) drop-shadow(0 0 24px rgba(42,147,193,0.3));
```

### Glow Bar (1px top border of footer)
```css
background: linear-gradient(90deg, transparent 0%, rgba(241,66,11,0.8) 20%, rgba(42,147,193,0.9) 50%, transparent 100%);
```
