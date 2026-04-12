# Test 5: Headline Rewrite Variants

## Test Overview

| Field | Value |
|---|---|
| **Test name** | Headline Rewrite |
| **Element** | Hero section H1 headline (and page `<title>` tag) |
| **Test type** | A/B/C (3-way split) |
| **Split** | 33% / 34% / 33% |
| **Minimum run** | 3 weeks or 400 unique visitors per variant |
| **Primary metric** | Scroll depth (50%+ of page) |
| **Secondary metrics** | Time on page, CTA click-through rate, bounce rate |
| **Do NOT run simultaneously with** | Test 2 (CTA Copy) — headline and CTA copy interact; run separately to isolate signal |

---

## Hypothesis

The current headline ("The AI that matters most!") is generic and exclamation-mark heavy. It makes a claim without telling visitors *why* it matters or *how* it is different from GPT-4, Gemini, or any other AI tool. Testing emotionally specific alternatives that communicate PureBrain's core differentiators (memory, relationship, personalization) will reduce bounce rate and increase engagement.

**Expected lift**: 10-20% reduction in bounce rate; 15-25% increase in scroll depth to 50%.

---

## The Three Variants

### Variant A (Control) — Current live headline

```
The AI that matters most!
```

**Character count**: 24 (with punctuation)
**Analysis**:
- Superlative claim ("most") with no supporting evidence above the fold
- Exclamation mark signals enthusiasm, but can read as aggressive to skeptical visitors
- "Matters" is abstract — matters for what? Matters how?
- No differentiation from competitors — any AI could make this claim
- Strength: Short, confident, easy to read at large type sizes

**When it works**: When visitors arrive already knowing PureBrain (warm traffic, referrals, return visitors)

---

### Variant B — Ownership / Identity / Rules framing

```
Your AI. Your Rules. Your Partner.
```

**Character count**: 35
**Analysis**:
- Triple "Your" creates rhythmic ownership — the product is customized *for this person*
- "Rules" addresses the #1 AI anxiety: fear of losing control, privacy, data ownership
- "Partner" lands the brand's core differentiator in one word
- Period-separated fragments are punchy, scannable at large hero type sizes
- Works at any font size — can even be broken into three lines for visual impact
- Risk: slightly abstract — what rules? Consider supporting with a subheadline

**Recommended subheadline to pair**:
> "PureBrain learns your style, remembers your conversations, and never resets. The AI that grows with you."

**HTML implementation**:
```html
<h1 class="elementor-heading-title" data-ab-test="headline" data-ab-variant="b">
  Your AI. Your Rules. Your Partner.
</h1>
```

**Three-line visual treatment** (for large hero displays):
```
Your AI.
Your Rules.
Your Partner.
```

---

### Variant C — Memory / Relationship / Specificity framing

```
The AI that remembers you.
```

**Character count**: 28
**Analysis**:
- "Remembers you" is the single most powerful differentiator PureBrain has vs. every competitor
- Directly contrasts with the universal user frustration: "I have to re-explain myself every time"
- Emotionally evocative — "remembers you" implies being *known*, not just *used*
- Period (not exclamation) communicates confidence rather than desperation
- Simple enough for cold traffic to grasp instantly
- Risk: visitors may ask "remembers what?" — subheadline must answer this

**Recommended subheadline to pair**:
> "Your goals. Your voice. Your history. PureBrain builds a relationship with you — one conversation at a time."

**HTML implementation**:
```html
<h1 class="elementor-heading-title" data-ab-test="headline" data-ab-variant="c">
  The AI that remembers you.
</h1>
```

**Predicted performance**: Strongest with cold traffic and anyone who has experienced "AI amnesia" with ChatGPT or Claude (re-explaining context every new session). This speaks directly to a universal pain point.

---

## Supporting Copy Matrix

Match your subheadline and body copy to each headline variant for coherence:

| Element | Variant A (Control) | Variant B (Your AI.) | Variant C (Remembers You.) |
|---|---|---|---|
| **H1** | The AI that matters most! | Your AI. Your Rules. Your Partner. | The AI that remembers you. |
| **Subheadline** | (current live) | PureBrain learns your style, remembers your conversations, and never resets. | Your goals. Your voice. Your history. Built into every conversation. |
| **Body para 1** | (current live) | Unlike generic AI tools, PureBrain adapts to your work style and remembers what matters to you. | Most AI tools forget you the moment you close the tab. PureBrain doesn't. |
| **CTA button** | Awaken Your PURE BRAIN | Start My AI Partnership | Meet the AI that knows you |

---

## Implementation Instructions

### Option 1: Google Optimize (recommended)

1. Navigate to Google Optimize → Create Experience → A/B Test
2. Target URL: `https://purebrain.ai/` (exact match)
3. Element: `h1.elementor-heading-title` (first H1 on page)
4. Variant B: Change text to "Your AI. Your Rules. Your Partner."
5. Variant C: Change text to "The AI that remembers you."
6. Objectives: add `scroll_depth` event (50%), `session_start`, `cta_click`
7. Traffic allocation: 33 / 34 / 33

### Option 2: JavaScript split (via GTM Custom HTML tag)

```javascript
(function () {
  var TEST   = 'headline';
  var COOKIE = 'pb_headline_variant';

  function getOrSet() {
    var m = document.cookie.match(new RegExp(COOKIE + '=([^;]+)'));
    if (m) return m[1];
    var variants = ['a', 'b', 'c'];
    var v = variants[Math.floor(Math.random() * variants.length)];
    document.cookie = COOKIE + '=' + v + '; path=/; max-age=' + (86400 * 30);
    return v;
  }

  var variant = getOrSet();

  var headlines = {
    a: 'The AI that matters most!',
    b: 'Your AI. Your Rules. Your Partner.',
    c: 'The AI that remembers you.'
  };

  var subheadlines = {
    a: null, // keep current
    b: 'PureBrain learns your style, remembers your conversations, and never resets. The AI that grows with you.',
    c: 'Your goals. Your voice. Your history. PureBrain builds a relationship with you — one conversation at a time.'
  };

  // Wait for DOM
  document.addEventListener('DOMContentLoaded', function () {
    // Update headline
    var h1 = document.querySelector('h1.elementor-heading-title, h1.hero-headline, [data-pb-headline]');
    if (h1 && headlines[variant]) {
      h1.textContent = headlines[variant];
      h1.setAttribute('data-ab-test', TEST);
      h1.setAttribute('data-ab-variant', variant);
    }

    // Update subheadline (if variant has one)
    if (subheadlines[variant]) {
      var sub = document.querySelector('.hero-subheadline, .elementor-widget-text-editor p:first-of-type, [data-pb-subheadline]');
      if (sub) sub.textContent = subheadlines[variant];
    }

    // Fire analytics
    try {
      gtag('event', 'ab_variant_assigned', { test_name: TEST, variant: variant });
    } catch (e) {}
  });
})();
```

### Option 3: Elementor Dynamic Content (no code)

Use Elementor's built-in A/B split or a plugin like **Nelio A/B Testing for Elementor**:

1. Duplicate the hero section
2. Edit the H1 text in each duplicate
3. Set traffic split 33/33/33 via plugin
4. Configure conversion goal: button click or form submit

---

## Measurement Plan

### Primary metric: Bounce rate reduction

A "bounce" = visitor views only one page and leaves within 10 seconds without clicking anything. Headline is the first thing visitors read — it should pull them into the page.

Track bounce rate per variant using GA4 session segmentation:
```
Segment: users where ab_variant = [a|b|c] AND test_name = 'headline'
Metric: Bounce rate (sessions with 0 events beyond page_view)
```

### Secondary metric: Scroll depth

Track what percentage of visitors scroll to 50% of page height (below hero) per variant:
```
GA4 Event: scroll_depth
Properties: { percent: 50, test_name: 'headline', variant: 'a'|'b'|'c' }
```

### Statistical significance target

- Minimum 400 unique visitors per variant
- p < 0.05 (95% confidence)
- Run for minimum 21 days (captures weekly usage patterns)

---

## Expected Outcomes

| Variant | Predicted bounce rate | Predicted scroll 50% | Rationale |
|---|---|---|---|
| A (Control) | ~35% (baseline) | ~45% (baseline) | Current performance |
| B (Your AI.) | ~27% | ~54% | Ownership language resonates with autonomy-motivated buyers |
| C (Remembers you.) | ~24% | ~58% | Memory pain point is universal; most specific differentiator |

**Prediction**: Variant C wins on cold traffic. Variant B may win on warmer LinkedIn referral traffic.

---

## Post-Test Actions

If Variant B or C wins by >= 10% over control:

1. Update the H1 in Elementor directly
2. Update the page `<title>` tag: "PureBrain – [winning headline]"
3. Update the `og:title` meta tag (OpenGraph / social share)
4. Update the meta description to align with winning message
5. Consider updating LinkedIn post headlines to match winning frame
6. Run Test 2 (CTA Copy) next — now that headline is locked, test the button copy

---

## Related Tests

- Test 2 (CTA Copy) — Do NOT run simultaneously; run after headline test concludes
- Test 4 (Trust Signals) — Safe to run simultaneously (different page section)
- Test 1 (Form Simplification) — Safe to run simultaneously
