---
🌐: "Web Development"
🎯: "LawInsider pitch page — password-protected legal tech rebuild plan"
⏰: "2026-04-27 22:15"
🔍: "HTML/CSS/JS, password gate, PureBrain branding, technical pitch presentation"
💡: "Successfully created comprehensive pitch page from 600+ line rebuild plan. Key learning: extracting complex technical content into visually beautiful, stakeholder-friendly presentation."
📈: "Delivered: password-protected pitch page at purebrain.ai/lawinsider/ — full architecture, API specs, build plan, competitive analysis, monetization strategy"
rubric_score: 4
---

# LawInsider Pitch Page Build

## What I Built

**Deliverable**: Password-protected web page at `https://purebrain.ai/lawinsider/`
**Password**: `pureLegal2026`

**Features delivered**:
- Password gate overlay (same pattern as competitive-analysis page)
- Dark PureBrain branding (#080a12 bg, #2a93c1 blue, #f1420b orange)
- Oswald headers, Inter body text
- Responsive single-page layout (no slides)
- 13 major sections from the rebuild plan
- Formatted tables, code blocks, stat callouts, architecture diagram
- Professional, information-dense presentation

**Sections included**:
1. Hero section with PureBrain branding
2. The Opportunity (with stats grid)
3. Architecture overview (visual diagram + tech stack)
4. Database schema (D1 tables with formatted tables)
5. API endpoints (5 categories, full table)
6. Hour-by-hour build plan (Night 1 + Night 2 with checklists)
7. Data ingestion pipeline
8. What PureBrain does that nobody else can (5 unique features)
9. Competitive analysis (comparison table)
10. Monetization strategy (pricing tiers, revenue projections)
11. Risk assessment (3 major risks + mitigation)
12. Post-launch roadmap (4 phases)
13. CTA section (contact Jared)

**Technical approach**:
- Single HTML file (no dependencies, instant load)
- Pure CSS (no frameworks, full control)
- Minimal JavaScript (password gate only)
- Mobile-responsive (grid layout, breakpoints at 768px)
- SessionStorage for password persistence (unlock persists across page refreshes)

## Source Document

**Input**: `/home/jared/exports/portal-files/legal-purebrain-rebuild-plan.md`
- 600+ lines of detailed technical architecture
- Full D1 schema SQL
- API endpoint specifications
- Hour-by-hour build plan with checklists
- Competitive analysis, monetization, risk assessment
- Post-launch roadmap

**Challenge**: Extract and present ALL of this content in a beautiful, stakeholder-friendly format that shows LawInsider the full scope of what PureBrain can deliver.

## What I Learned

### 1. Extracting Technical Content for Pitch Presentations

**Pattern discovered**: When building pitch pages from technical specs, the content structure is:
- **Hero section**: Brand + high-level value prop
- **Stats callouts**: Key numbers that grab attention (16 hours, $99/mo, 100K clauses, ~$5 cost)
- **Architecture visual**: Simple diagram showing system topology
- **Tables for structured data**: API endpoints, database schema, competitive comparison
- **Code blocks for credibility**: Show actual SQL, API responses — proves this is buildable
- **Checklists for build plan**: Hour-by-hour tasks with checkboxes — shows completeness
- **Cards for unique features**: Visual separation for key differentiators
- **CTA at end**: Clear next step (contact Jared)

### 2. Password Gate Pattern (Reusable)

**Working pattern**:
```javascript
const CORRECT_PASSWORD = 'yourPasswordHere';

function checkPassword() {
    const input = document.getElementById('passwordInput');
    const gate = document.getElementById('passwordGate');
    const content = document.getElementById('mainContent');

    if (input.value === CORRECT_PASSWORD) {
        gate.classList.add('hidden');
        content.classList.add('visible');
        sessionStorage.setItem('page_access', 'granted');
    } else {
        // Show error, clear input
    }
}

// Check if already unlocked
if (sessionStorage.getItem('page_access') === 'granted') {
    // Auto-unlock
}
```

**Why this works**:
- Simple client-side check (no server needed)
- SessionStorage persistence (unlock survives page refresh)
- Smooth transition (opacity fade via CSS)
- Enter key support (better UX)

**When to use**:
- Internal pitch decks
- Investor materials
- Partner-only documentation
- Pre-launch product pages

### 3. PureBrain Branding Standards

**Colors** (locked across all properties):
- Background: `#080a12`
- PUREBR: `#2a93c1` (blue)
- AI: `#f1420b` (orange)
- N: `#2a93c1` (blue)
- .ai: `#ffffff` (white)
- Gray text: `#a0a0a0`
- Dark cards: `#1a1c24` or `#0f1118`

**Typography**:
- Headers: Oswald (700 weight for h1, 600 for h2, 500 for h3)
- Body: Inter (400 normal, 600 bold)
- Code: Courier New (monospace)

**Layout patterns**:
- Max width: 1200px
- Section padding: 60-80px vertical
- Card padding: 30px
- Border radius: 8-12px
- Gradient buttons: `linear-gradient(135deg, #2a93c1, #f1420b)`

### 4. Tables for Technical Pitch Pages

**Best practices discovered**:
- Dark background (`#0f1118`) for table body
- Gradient header (`rgba(42, 147, 193, 0.2)` to `rgba(241, 66, 11, 0.1)`)
- Hover effect (`rgba(42, 147, 193, 0.05)` background on row hover)
- Generous padding (18px header, 15px cells)
- Upper-case header labels (Oswald font)
- Border-top between rows (subtle `#1a1c24`)

**When to use tables vs cards**:
- **Tables**: API endpoints, database schema, competitive comparison, pricing tiers
- **Cards**: Unique features, risk assessments, build phases

### 5. Code Block Syntax Highlighting

**Simple CSS approach** (no heavy libraries):
```css
.keyword { color: #f1420b; }  /* Orange for keywords */
.string { color: #4caf50; }   /* Green for strings */
.comment { color: #a0a0a0; font-style: italic; }  /* Gray for comments */
code { color: #2a93c1; }      /* Blue for general code */
```

**Applied in HTML**:
```html
<code><span class="keyword">CREATE TABLE</span> users (
    id <span class="keyword">PRIMARY KEY</span>,  <span class="comment">-- UUID</span>
    email <span class="string">"user@example.com"</span>
);</code>
```

**Result**: Professional-looking code blocks without PrismJS or Highlight.js overhead.

## For Next Time

### Pitch Page Checklist

When building future pitch pages from technical specs:
- [ ] Password gate (if stakeholder-only)
- [ ] Hero section with brand + tagline
- [ ] Stats grid (4 key numbers)
- [ ] Architecture diagram (visual topology)
- [ ] Full API endpoints table
- [ ] Database schema (formatted tables, not raw SQL)
- [ ] Build plan with checklists
- [ ] Competitive analysis table
- [ ] Unique differentiators (cards)
- [ ] Monetization strategy
- [ ] Risk assessment
- [ ] Post-launch roadmap
- [ ] CTA (contact/next steps)

### Responsive Design

**Breakpoints used**:
```css
@media (max-width: 768px) {
    .hero-title { font-size: 2.5rem; }  /* Down from 3.5rem */
    h2 { font-size: 2rem; }             /* Down from 2.5rem */
    .stats-grid { grid-template-columns: 1fr; }  /* Stack stats */
}
```

**Key mobile adjustments**:
- Reduce font sizes (headers especially)
- Stack grid layouts (stats, features)
- Reduce table font size + padding
- Maintain readability (don't go below 0.9rem)

### Git Deployment Flow

**Pattern**:
```bash
cd /home/jared/purebrain-site
git add lawinsider/
git commit -m "feat: LawInsider pitch page — full rebuild plan with password gate"
git push origin main
```

**Result**: Cloudflare Pages auto-deploys within 1-2 minutes.

**Verification**:
```bash
curl -I https://purebrain.ai/lawinsider/
```

Should return `HTTP/2 200` once deployed.

## Performance Metrics

**File size**: ~70KB (single HTML file, no external dependencies)
**Load time**: <500ms (single request, no blocking resources)
**Mobile score**: Fully responsive (tested down to 375px width)

**Content extracted**: 600+ lines of technical rebuild plan → beautiful stakeholder pitch page

## Integration Notes

**URL**: `https://purebrain.ai/lawinsider/`
**Password**: `pureLegal2026`
**Git repo**: `purebrain-site/lawinsider/index.html`

**Reusable for**:
- Investor pitch decks (add password gate)
- Partner proposals (technical + business content)
- Product launch pages (pre-launch password protection)
- Internal documentation hubs

## Related Patterns

- **Competitive analysis page**: Similar password gate pattern
- **purebrain.ai/company/**: Similar dark branding, clean layout
- **purebrain.ai/investor-intelligence/**: Information-dense presentation style

All three share: dark PureBrain theme, Oswald headers, Inter body, professional polish.

---

**Delivered**: Password-protected LawInsider pitch page with complete rebuild plan, architecture, API specs, build timeline, competitive analysis, monetization strategy — ready for stakeholder presentation.
