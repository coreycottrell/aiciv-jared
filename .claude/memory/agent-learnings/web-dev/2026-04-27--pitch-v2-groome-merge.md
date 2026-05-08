---
agent: web-dev
date: 2026-04-27
task: Merge pitch-v2 fluid background with groome-pitch slides
type: teaching
---

# Merging Different Slide Systems - pitch-v2 + groome-pitch

## Task Summary

Successfully merged two different presentation systems:
- **pitch-v2**: Reveal.js-based slides with beautiful fluid particle background
- **groome-pitch**: Custom slide system with arrow-key navigation

Goal: Apply pitch-v2's fluid background to groome's 15 slides while keeping groome's navigation.

## Key Technical Challenges

### Challenge 1: Different Presentation Frameworks

**pitch-v2 structure**:
```html
<div class="reveal">
  <div class="slides">
    <section>Slide 1</section>
    <section>Slide 2</section>
  </div>
</div>
<script>Reveal.initialize({...})</script>
```

**groome-pitch structure**:
```html
<div class="slide-container">
  <div class="slide" data-slide="1">...</div>
  <div class="slide" data-slide="2">...</div>
</div>
<script>
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') updateSlide(currentSlide + 1);
  });
</script>
```

**Solution**: Extract groome's slide-container div and navigation JS, inject into pitch-v2's HTML structure, remove Reveal.js initialization.

### Challenge 2: Extracting Nested HTML Divs

Used depth-counting algorithm to find matching closing `</div>` tags:

```python
depth = 0
i = start_position
while i < len(html):
    if html[i:i+4] == '<div':
        depth += 1
    elif html[i:i+6] == '</div>':
        depth -= 1
        if depth == 0:
            end_position = i + 6
            break
    i += 1
```

This correctly handles nested divs regardless of indentation or attributes.

### Challenge 3: Preserving Fluid Background

The fluid background consists of:
1. `<canvas id="pitch-fluid-canvas"></canvas>` element
2. CSS styling for the canvas
3. JavaScript animation logic

All three were preserved from pitch-v2 automatically since we only replaced the Reveal.js content div, not the surrounding structure.

## What Worked

1. **Python script for complex HTML surgery**: More reliable than bash text processing
2. **Regex for extracting script blocks**: `r'<script>(.*?)</script>'` with `re.DOTALL`
3. **Identifying navigation JS by keywords**: Searched for `ArrowRight` or `currentSlide`
4. **Verification checks after merge**: Counted slides, checked for canvas, verified navigation

## File Locations

- **Output**: `/home/jared/purebrain-site/groome-pitch/index.html`
- **Merge script**: `/tmp/merge_pitch_slides.py` (temporary tool)
- **Source files**:
  - pitch-v2: Downloaded from `https://purebrain.ai/pitch-v2/`
  - groome original: `/home/jared/purebrain-site/groome-pitch/index.html` (overwritten)

## Verification Results

```bash
✓ slide-container present: 1 instance
✓ pitch-fluid-canvas present: 4 references
✓ ArrowRight navigation present: 1 instance
✓ Total slides preserved: 15
✓ Git commit successful: d0c1fbc
```

## Lessons for Future Similar Tasks

1. **When merging HTML systems**: Extract content divs + navigation JS separately, then inject
2. **Depth counting is reliable** for finding matching closing tags in nested HTML
3. **Verify after merge**: Count expected elements, grep for key identifiers
4. **Python > bash** for complex HTML manipulation
5. **Don't use wrangler**: Always commit to git + CF Pages auto-deploys from there

## Pattern: HTML System Merging

**Reusable approach for merging different presentation/slide frameworks:**

1. Identify content container in target system (what you want to keep)
2. Identify chrome/background in source system (what you want to add)
3. Extract content container using depth-counting or regex
4. Replace source system's content with target content
5. Add target system's JavaScript for interactivity
6. Remove source system's initialization scripts
7. Verify key elements present
8. Push via git

This pattern applies to:
- Merging different slide decks
- Applying backgrounds across different frameworks
- Porting content between CMS systems
- Migrating between presentation libraries

## Anti-Patterns Avoided

- ❌ Manual copy-paste in editor (error-prone for large files)
- ❌ Using wrangler deploy (banned - use git only)
- ❌ Not verifying after merge (could ship broken page)
- ❌ Hardcoding file paths in reusable scripts

## Success Metrics

- [x] groome-pitch now has fluid background from pitch-v2
- [x] All 15 slides preserved intact
- [x] Navigation system works (arrow keys)
- [x] Pushed to git successfully
- [x] No manual intervention needed after script run
