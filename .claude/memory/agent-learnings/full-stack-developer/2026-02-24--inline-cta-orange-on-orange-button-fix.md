# Memory: Inline CTA Button Invisible Text Fix — v5.0.1

**Date**: 2026-02-24
**Type**: teaching
**Topic**: Blog post inline CTA button orange-on-orange invisible text — root cause + fix pattern

---

## Problem

Jared reported: "inline CTA button inside blog post content has invisible text — orange text on orange background."

The footer CTA button ("Start Your AI Partnership") looked fine. Only the mid-content inline CTA had invisible text.

---

## Root Cause

Post 879 ("Your Next Direct Report Won't Be Human"):
```html
<p><a href="https://purebrain.ai/#awakening">Take the free assessment →</a></p>
```

This bare `<a>` tag had NO class, NO inline style. The post's own style block contains:
```css
#pb-agent-manager-post a { color: #f1420b !important; }
#pb-agent-manager-post a:hover { color: #ffffff !important; background-color: #f1420b; }
```

This makes the link text orange. The plugin j3 hook ALSO adds an orange background on hover for `.entry-content a` — so hovering gives orange background + (without explicit white override) orange text = invisible.

The footer `.cta-btn` link was fine because it uses `class="cta-btn"` and the CSS block in the post has:
```css
#pb-agent-manager-post .blog-cta-block .cta-btn { color: #ffffff !important; }
```

**Lesson**: The footer CTA had white text because it was inside `.blog-cta-block .cta-btn`. The inline mid-content CTA was just a bare `<a>` inheriting the general orange color rule.

---

## Affected Posts

| Site | Post ID | Title | Bare Links Count |
|------|---------|-------|-----------------|
| purebrain.ai | 879 | Your Next Direct Report Won't Be Human | 1 |
| purebrain.ai | 606 | Why 95% of AI Pilots Fail | 1 (+ 1 inline text mention, intentionally kept) |
| jareddsanborn.com | 1195 | Your Next Direct Report Won't Be Human | 1 |
| jareddsanborn.com | 1092 | Why 95% of AI Pilots Fail | 1 |

**Posts 696, 631, 565, 480, 381, 316, 373, 172** — all fine (footer CTA already has inline-block style or .cta-btn class).

---

## Fix: Two-Layer Approach

### Layer 1: REST API Content Fix (immediate)

Converted bare `<p><a href="#awakening">TEXT</a></p>` to:
```html
<div class="pb-inline-cta" style="margin: 2rem 0; text-align: center;">
<a href="{url}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #f1420b 0%, #d13608 100%); color: #ffffff !important; font-weight: 700; font-size: 1.05rem; border-radius: 8px; text-decoration: none !important; letter-spacing: 0.5px; transition: background 0.3s ease;">{text}</a>
</div>
```

Script: `tools/security/fix_inline_cta_white_text_v501.py`

### Layer 2: Plugin CSS (permanent safety net)

New j5 hook at wp_head priority 99 — added to `purebrain-security-plugin.php v5.0.1`:
```css
html body.single-post .pb-inline-cta a,
html body.single-post .pb-inline-cta a:link,
html body.single-post .pb-inline-cta a:visited {
    color: #ffffff !important;
    text-decoration: none !important;
}
html body.single-post .pb-inline-cta a:hover { ... same + darker bg ... }
/* Also: .entry-content a[style*="background"][style*="gradient"] gets white text */
```

Deploy script: `tools/security/deploy_plugin_v501_purebrain.py`

---

## Verification Results

| Check | Post 879 | Post 606 |
|-------|---------|---------|
| page_loads_200 | OK | OK |
| pb-inline-cta_present | OK | OK |
| inline_white_text | OK | OK |
| j5_css_rule_present | OK | OK |
| no_bare_awakening_p_link | OK | OK |

All 5/5 checks passed on both posts. Plugin deployed and verified.

---

## Key Lessons

### 1. How to identify "invisible button" problems
- Jared says "orange text on orange background" → always check post's own CSS block for `a { color: #f1420b }` rule
- If bare `<a>` has no class + no inline style → it inherits the general orange color
- Plugin j3 adds orange bg on hover → invisible

### 2. Audit pattern
```python
# Find bare awakening links (problem)
all_awk = re.findall(r'<a[^>]*#awakening[^>]*>[^<]+</a>', raw)
problem = [a for a in all_awk if 'inline-block' not in a and 'cta-btn' not in a]
```

### 3. Fix pattern — styled button wrapper
Always wrap inline CTAs in `.pb-inline-cta` div with inline `color: #ffffff !important` on the `<a>`. This class is now covered by the permanent plugin CSS.

### 4. Not all bare `<a href="#awakening">` are bugs
Post 606 had an in-text inline mention `<a href="#awakening">purebrain.ai/#awakening</a>` inside `<em>` paragraph — this is intentionally a text link, NOT a button. Correctly left as-is (hover handled by j3 hook = orange bg + white text).

### 5. JDS REST API works (no form login needed)
JDS: user=`AetherPureBrain.ai`, password from `WORDPRESS_APP_PASSWORD` env var, curl with `-u` flag.

---

## Files Modified

1. `tools/security/purebrain-security/purebrain-security-plugin.php` — v5.0.0 → v5.0.1 (added j5 hook)
2. `tools/security/fix_inline_cta_white_text_v501.py` — new script (REST API post content fix)
3. `tools/security/deploy_plugin_v501_purebrain.py` — new deploy script
4. Posts 879, 606 (purebrain.ai) — content updated via REST API
5. Posts 1195, 1092 (jareddsanborn.com) — content updated via REST API
