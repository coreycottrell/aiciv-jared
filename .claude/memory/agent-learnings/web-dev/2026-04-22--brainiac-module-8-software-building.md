---
agent: web-dev
task: Publish new Brainiac Mastermind Training module to purebrain.ai
date: 2026-04-22
topic: Brainiac module publishing, article-style HTML, CF Pages auto-deploy
type: teaching
---

# Publishing Brainiac Module 8: Software Building

## What I Built

Published a new training module to purebrain.ai/brainiac-mastermind-training/ titled "Why Your AI Should Build, Not Subscribe — Replacing Middleware with Bespoke Code"

**Components:**
1. Created `/brainiac-mastermind-training/brainiac-module-8-software-building/index.html`
2. Updated main index.html to add module card + AI training snippet
3. Updated module count badge from "6 modules" to "8 modules"
4. Followed dark theme (#080a12 bg, blue #2a93c1, orange #f1420b)

**Content format:**
- Article-style (not slide presentation like modules 2-3)
- Sections: Opening Truth, Problem, What AI Can Build, Pre-Build Checklist (7 questions), Decision Matrix, Real Scenario, How to Ask AI, Mindset Shift, Action Items, Bottom Line
- 18 min read, published April 21, 2026
- NEW badge added

## What I Learned

### Brainiac Training Structure

The Brainiac page has:
- Main index at `/brainiac-mastermind-training/index.html` (single large file)
- Individual module subdirectories: `/brainiac-module-{N}-{slug}/index.html`
- Two module formats exist:
  - Interactive slide presentation (modules 2-3) - uses slideshow.js
  - Article-style readable format (module 8) - simpler, better for text-heavy content
- Each module card includes:
  - Module number badge
  - Icon SVG
  - Tag (Foundations, Workflows, Software Building, etc.)
  - Title + description
  - Meta info (duration, date, badge)
  - Launch button
  - AI Training Snippet (collapsible, contains core concepts, techniques, implementation checklist, quotes)

### Git Workflow for purebrain-site

- Repository: https://github.com/puretechnyc/purebrain-site.git
- Production branch: `main`
- CF Pages auto-deploys on push to main (no manual wrangler needed)
- Current work branch was `admin-rebuild` - merged to main before pushing
- When branches diverge: use `git pull origin main --rebase` to cleanly integrate
- NEVER use wrangler for direct deploys (constitutional rule per MEMORY.md)

### Brand Consistency

CSS variables defined:
```css
--blue: #2a93c1;
--orange: #f1420b;
--dark: #080a12;
--dark2: #0d1020;
--dark3: #111526;
--white: #ffffff;
--light: #c8d6e5;
--muted: #6b7fa3;
```

Typography:
- `Plus Jakarta Sans` for body text
- `Oswald` for headings
- Line height: 1.7 for body, 1.15 for h1

## For Next Time

### When Publishing New Brainiac Modules

1. **Choose format**: Slide presentation vs article-style (article is easier for text-heavy content)
2. **Create directory**: `/brainiac-mastermind-training/brainiac-module-{N}-{slug}/`
3. **Create index.html** with standard structure:
   - Google Tag Manager + Clarity scripts
   - Favicon links
   - Title: "Brainiac — Module {N}: {Title}"
   - Dark theme CSS variables
   - Header with logo + back link
   - Content area (max-width: 900px for readability)
4. **Update main index.html**:
   - Update module count badge
   - Add module card with correct number, icon, tag, description
   - Add AI training snippet with core concepts, techniques, checklist, quotes
   - Insert before `</div><!-- /modules-grid -->` closing tag
5. **Commit and push to main**:
   - Stage: `git add brainiac-mastermind-training/`
   - Commit with descriptive message + Co-Authored-By
   - Merge to main if on different branch
   - Pull with rebase if divergent: `git pull origin main --rebase`
   - Push: `git push origin main`
6. **CF Pages auto-deploys** - no manual intervention needed

### Icon SVG Patterns

Each module has a custom icon. Pattern:
```html
<svg width="36" height="36" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="10" fill="rgba(42,147,193,0.12)"/>
  <!-- Custom paths for icon concept -->
  <path d="..." stroke="#2a93c1" stroke-width="2" stroke-linecap="round"/>
  <path d="..." stroke="#f1420b" stroke-width="2" stroke-linecap="round"/>
</svg>
```

Colors: blue (#2a93c1) for main elements, orange (#f1420b) for accents

### Article-Style Module Template

Works well for:
- Text-heavy content with sections
- How-to guides with checklists
- Concept explanations without visual slides

Structure:
- Tag badge at top
- h1 title + subtitle
- Divider lines between major sections
- h2 for major sections (blue)
- h3 for subsections (orange)
- Lists (ul/ol) with good spacing
- Checklist box (highlighted background, blue left border)
- Quotes/blockquotes (orange left border, italic)
- Footer with module attribution

## Performance Metrics

- Module HTML: 22KB (reasonable size)
- Total time: ~15 minutes (reading content, creating HTML, updating index, git workflow)
- Zero errors during deployment
- Clean git history maintained

## Files Modified

- `/home/jared/purebrain-site/brainiac-mastermind-training/index.html` (updated)
- `/home/jared/purebrain-site/brainiac-mastermind-training/brainiac-module-8-software-building/index.html` (created)

## Git Commit

Commit: 4afa740 (after rebase)
Branch: main
Pushed to: origin/main

CF Pages will auto-deploy to purebrain.ai within a few minutes.
