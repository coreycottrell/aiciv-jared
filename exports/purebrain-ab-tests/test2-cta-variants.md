# Test 2: CTA Copy Variants

## Test Overview

| Field | Value |
|---|---|
| **Test name** | CTA Copy Test |
| **Element** | Primary call-to-action button (hero section + sticky bar) |
| **Test type** | A/B/C (3-way split) |
| **Split** | 33% / 34% / 33% |
| **Minimum run** | 3 weeks or 300 clicks per variant |
| **Primary metric** | CTA click-through rate (CTR) |
| **Secondary metrics** | Form view rate, form completion rate, scroll depth |

---

## Hypothesis

The current CTA copy ("Awaken Your PURE BRAIN") is brand-centric and abstract. Visitors who don't yet understand the product see a mystical phrase with no clear value proposition. Testing benefit-focused and relationship-focused alternatives will reveal which emotional register converts better for PureBrain's audience.

**Expected lift**: 15-30% increase in CTR on the winning variant.

---

## The Three Variants

### Variant A (Control) — Current live copy

```
Awaken Your PURE BRAIN
```

**Emotional register**: Mystical / brand-specific
**Value message**: Implicit (assumes brand familiarity)
**Risk**: Confusing to cold traffic; high on intrigue, low on clarity
**Best for**: Warm audiences who already understand the awakening concept

**Button element** (current implementation reference):
```html
<a href="/start" class="elementor-button">
  Awaken Your PURE BRAIN
</a>
```

---

### Variant B — Benefit + Agency framing

```
Start My AI Partnership
```

**Emotional register**: Action / ownership / pragmatic
**Value message**: Explicit — you get a *partnership*, not a tool
**Word choice analysis**:
- "Start" = low-friction action word (vs "Begin," "Launch," "Try")
- "My" = first-person ownership, personalizes immediately
- "AI Partnership" = core differentiator from competitors; positions against "AI assistant/tool"
**Best for**: LinkedIn and professional traffic; people comparing AI tools

**Button element**:
```html
<a href="/start" class="elementor-button" data-ab-variant="b" data-ab-test="cta-copy">
  Start My AI Partnership
</a>
```

---

### Variant C — Relationship + Memory framing

```
Meet Your AI Partner
```

**Emotional register**: Warm / relational / curious
**Value message**: Implicit but accessible — there's an *entity* to meet
**Word choice analysis**:
- "Meet" = social/human word, implies a real relationship, not just software
- "Your" = personalized before they've even signed up
- "AI Partner" = mirrors brand language while feeling more conversational
**Best for**: Social media traffic; people who are curious but skeptical about AI
**Risk**: Slightly passive — "meet" suggests less urgency than "start"

**Button element**:
```html
<a href="/start" class="elementor-button" data-ab-variant="c" data-ab-test="cta-copy">
  Meet Your AI Partner
</a>
```

---

## Supporting Copy (Test These Too)

The CTA button does not live in isolation. Test these surrounding copy changes alongside the button variants for maximum signal.

### Hero subheadline options (pair with each CTA variant)

| CTA Variant | Recommended subheadline |
|---|---|
| A (Control) | "The AI awakening that changes how you work forever." |
| B (Start My AI Partnership) | "Your AI remembers everything. Learns your style. Never resets." |
| C (Meet Your AI Partner) | "Not a chatbot. A partner who knows you by name." |

### Sticky bar / notification bar options

```
Variant A: "Ready to awaken your PURE BRAIN? →"
Variant B: "Join 500+ professionals who started their AI partnership →"
Variant C: "Meet the AI that remembers you →"
```

---

## Implementation Instructions

### If using Google Optimize

1. Create a new A/B/C experiment on the PureBrain landing page URL
2. Target the hero CTA button element (use CSS selector or element ID)
3. Set variant weights: 33/34/33
4. Set objective: CTA click event (configure in GA4 as a conversion)
5. Run until statistical significance or minimum 300 clicks per variant

### If implementing manually (no Optimize)

Add this script to the page `<head>` or via GTM:

```javascript
(function () {
  // Assign visitor to variant deterministically via cookie
  function getOrSetVariant() {
    var cookie = document.cookie.match(/pb_cta_variant=([abc])/);
    if (cookie) return cookie[1];
    var variants = ['a', 'b', 'c'];
    var chosen = variants[Math.floor(Math.random() * variants.length)];
    document.cookie = 'pb_cta_variant=' + chosen + '; path=/; max-age=' + (60 * 60 * 24 * 30);
    return chosen;
  }

  var variant = getOrSetVariant();

  var copy = {
    a: 'Awaken Your PURE BRAIN',
    b: 'Start My AI Partnership',
    c: 'Meet Your AI Partner'
  };

  // Replace all matching CTA buttons
  document.querySelectorAll('[data-ab-test="cta-copy"]').forEach(function (el) {
    el.textContent = copy[variant];
    el.setAttribute('data-ab-variant', variant);
  });

  // Fire analytics event
  try {
    gtag('event', 'ab_variant_assigned', {
      test_name: 'cta-copy',
      variant: variant
    });
  } catch (e) {}
})();
```

### Analytics events to track

| Event | When to fire | Properties |
|---|---|---|
| `ab_variant_assigned` | Page load | `test_name`, `variant` |
| `cta_click` | Button click | `test_name`, `variant`, `location` (hero/sticky/footer) |
| `form_view` | Form becomes visible | `test_name`, `variant` |
| `form_submit` | Successful form submission | `test_name`, `variant` |

---

## Success Criteria

| Metric | Threshold to declare winner |
|---|---|
| Statistical significance | p < 0.05 (95% confidence) |
| Minimum clicks per variant | 300 |
| Minimum run time | 21 days |
| Winner threshold | +10% lift in CTR over control |

---

## Expected Outcomes

Based on UX audit findings and industry benchmarks for AI SaaS landing pages:

- **Variant B** (Start My AI Partnership) is predicted to win with cold LinkedIn/professional traffic
- **Variant C** (Meet Your AI Partner) is predicted to perform well with warmer or story-driven audiences
- **Variant A** may retain strength with returning visitors already familiar with the awakening concept

**Recommendation after test**: If B or C wins significantly, update the form submit button copy to match (currently "Awaken Your PURE BRAIN" — consistency between CTA and form button reinforces the decision).

---

## Related Tests

- Test 1 (Form Simplification) — Run concurrently, segment results independently
- Test 5 (Headline Rewrite) — Do not run simultaneously with Test 2; headline and CTA copy interact
