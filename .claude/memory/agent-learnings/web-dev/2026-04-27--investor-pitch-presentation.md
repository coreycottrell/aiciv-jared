---
🌐: "Web Development"
🎯: "Built full-screen investor pitch presentation for 20-investor live call"
⏰: "2026-04-27 15:30"
🔍: "HTML5/CSS3/JS, CF Pages deployment, full-screen slides, industry-specific messaging"
💡: "Created beautiful pitch deck as web page - no PowerPoint needed. Full keyboard nav, smooth transitions, industry-tailored slides."
📈: "Delivered production-ready presentation in <1 hour. Deployed to https://purebrain.ai/groome-pitch/"
rubric_score: 5
---

# Investor Pitch Presentation - Groome Network

## What I Built

**Context**: Jared had a live investor call scheduled for this afternoon with 20 investors from Richard Groome's network (Notre-Dame Capital). Audience: mining, direct-to-consumer, legal, accounting, computer sales professionals - NOT tech people.

**Theme**: "Focus on the next generation of AI, and how you can help scale most businesses faster and more efficiently"

**Deliverable**: Full-screen web-based pitch deck (15 slides) with:
- Professional slide navigation (arrow keys, slide counter, overview grid on ESC)
- PureBrain branding (#080a12 bg, #2a93c1 blue, #f1420b orange)
- Oswald + Inter fonts (brand typography)
- Smooth 600ms cubic-bezier transitions
- Interactive CTA buttons (open in new tabs for live demo)
- Industry-specific slides (Mining, Legal, Accounting, D2C, Computer Sales)
- SVG chart showing compound effect (value curve)
- Responsive design (works on all screen sizes)

**Tech Stack**:
- Pure HTML5/CSS3/Vanilla JS (no dependencies = instant load)
- Google Fonts (Oswald, Inter)
- SVG for charts/graphics
- CF Pages deployment

**File Size**: ~17KB (extremely fast)

## Slide Structure (15 slides)

1. **Title** - "The Next Generation of AI: From Tool to Partner"
2. **The Problem** - Every industry has same problem (too much work, not enough people)
3. **Old vs New AI** - Side-by-side comparison (forgets vs remembers)
4. **How PureBrain Works** - 3 steps (Awaken → Partner → Compound)
5. **Mining** - Industry-specific use cases
6. **Direct-to-Consumer** - Industry use cases
7. **Legal** - Industry use cases
8. **Accounting** - Industry use cases
9. **Computer Sales / Tech** - Industry use cases
10. **The Compound Effect** - Visual chart (Month 1 → Month 6, value triples)
11. **Our Numbers** - 25+ customers, $2.5M seed, $25M Series-A, 225:1 LTV:CAC
12. **Live Demo** - Interactive CTAs (Try PureBrain, AI Calculator)
13. **Investment Opportunity** - $55M pre, $3.36/share, 19 spots, 1.9x step-up
14. **Why Now** - $3.68T market, first-mover advantage
15. **Thank You / Q&A** - Contact info

## Design Decisions

### Non-Tech Audience Focus
- Avoided jargon - used industry-specific language (geological data, contract review, cash flow forecasting)
- Concrete examples per industry ("200 contracts reviewed in a weekend")
- Visual comparison (Old AI vs New AI) - simple side-by-side
- ROI focus (time saved, errors caught, value compound)

### Professional Pitch Deck Format
- Full-screen slides (100vw x 100vh)
- Keyboard navigation (arrow keys = clean presentation)
- Slide counter (bottom-right, subtle)
- Overview grid (ESC key = show all slides as thumbnails)
- No mouse required for navigation

### Brand Consistency
- PureBrain color palette (dark bg, blue/orange accents)
- Typography hierarchy (Oswald for headings, Inter for body)
- Logo treatment: PUREBR(blue) + AI(orange) + N(blue) + .ai(white)

### Interactive Elements
- All links open in new tabs (don't lose slide position)
- CTA buttons with hover states
- Live demo buttons on Slide 12
- Investor portal links on Slide 13

## Deployment

**Commands**:
```bash
# Deployed to production CF Pages
CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py groome-pitch/
```

**Live URL**: https://purebrain.ai/groome-pitch/

**Deployment stats**:
- 1 file deployed (index.html)
- Instant propagation to CF edge
- No cache issues (new path)

## What I Learned

### Web-Based Presentations > PowerPoint
- No software dependencies (just a browser)
- Perfect for screenshare (consistent rendering)
- Lightweight (17KB vs multi-MB PPTX)
- Interactive (clickable links work during presentation)
- Version control (git-tracked, not binary)
- Deployable (URL > file attachment)

### Industry Messaging Patterns
Each industry slide followed same pattern:
1. Industry name + domain (e.g., "Mining: AI for Exploration, Operations & Safety")
2. 4 concrete use cases (bullet points)
3. Memorable quote/example (italicized, highlighted)
4. Optional CTA button

This made slides scannable and relatable to diverse audience.

### SVG Charts in Pitch Decks
Used inline SVG for the "Compound Effect" chart:
- Curve path showing value growth (Month 1 → 6)
- Gradient fill
- Labeled data points
- Lightweight (<1KB)
- Scales perfectly at any resolution

Better than embedding image (no additional HTTP request).

### Keyboard-First Navigation
- Arrow keys (left/right) = next/prev slide
- ESC = overview grid
- No mouse needed = cleaner presentation
- Slide counter = orientation

Professional presenters appreciate this.

## For Next Time

### Enhancements for Future Pitch Decks
1. **Auto-advance timer** (optional, for demo mode)
2. **Speaker notes** (visible only to presenter, not screenshare)
3. **Slide transitions** (fade, slide, zoom - selectable)
4. **Progress bar** (top of screen, subtle)
5. **QR codes** (for investor portal, auto-generated)
6. **Print stylesheet** (PDF export for deck sharing)

### Content Improvements
1. **More visuals** - icons for each industry (mining pickaxe, legal gavel, etc.)
2. **Client logos** (if we get permission to display)
3. **Video embed** (product demo on Slide 12)
4. **Testimonials** (customer quotes with headshots)

### Technical Optimizations
1. **Preload next slide** (instant transitions)
2. **Service worker** (offline-first for flaky conference WiFi)
3. **Print mode** (single-page PDF export)
4. **Presenter mode** (dual-screen: slides + notes)

## Files Created

- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/groome-pitch/index.html` - Full presentation
- `/home/jared/exports/portal-files/groome-pitch-delivered.md` - Delivery doc for Jared

## Success Metrics

- **Build time**: <1 hour (request to deployment)
- **File size**: 17KB (instant load)
- **Slides**: 15 (comprehensive coverage)
- **Industries**: 5 (Mining, Legal, Accounting, D2C, Computer Sales)
- **Interactive elements**: 6+ clickable CTAs
- **Deployment**: Live at https://purebrain.ai/groome-pitch/

## Reusable Pattern

This establishes a pattern for **web-based pitch decks**:

1. **HTML structure**: Full-screen slides, keyboard nav, slide counter
2. **CSS design**: Brand colors, typography, smooth transitions
3. **JS interaction**: Arrow keys, ESC overview, slide tracking
4. **CF deployment**: Version-controlled, URL-shareable
5. **Industry targeting**: Tailored slides per audience segment

Can be templated for future investor presentations, sales decks, conference talks.

## Constitutional Compliance

✅ **Memory-first protocol**: Searched web-dev memories (no prior pitch deck work found)  
✅ **Verification**: Tested navigation, links, deployment before completion  
✅ **Documentation**: Created memory entry + portal delivery doc  
✅ **Portal delivery**: Filed to `/home/jared/exports/portal-files/` with [FILE: path]

---

**This is a reusable capability. Future pitch decks can follow this pattern.**
