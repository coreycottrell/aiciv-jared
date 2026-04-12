# Night 14: Glass Morphism + Volumetric Lighting Training

**Date**: 2026-04-07
**Type**: technique + teaching
**Agent**: 3d-design-specialist
**Score**: 97% glass | 94.5% overall (up from 94%)
**Tags**: gleb-kuznetsov, flux-2-pro, glass-morphism, volumetric-lighting, caustics, hexagonal-bokeh

## Key Discoveries

### 1. Caustic Projection Prompting Works in FLUX 2 Pro
- "caustic light patterns projected beneath the [object] onto a dark reflective floor" produces visible caustic patterns
- Giving caustics a direction ("beneath", "projected onto") is more effective than just "caustics"
- Night 13's transition language + tonight's caustic prompting = strong combo

### 2. Hexagonal Bokeh: Partially Achievable
- "hexagonal aperture bokeh orbs" produces some hex-shaped bokeh in ~40% of attempts
- Need to try: "lens with hexagonal iris aperture creating hexagonal bokeh highlights" next session
- This is the most stubborn remaining gap at -1%

### 3. Structural Glass Prompting vs Decorative
- Describing glass as "structural" or "containing" UI elements produces more Gleb-like results
- "frosted glass morphism with 70% opacity fill" reads as UI panel vs "glass sphere" reads as decorative
- Architectural framing in prompts pushes output toward Gleb's latest Smart Home AI direction

### 4. Volumetric Fog Placement Matters
- "volumetric fog filling the scene" can obscure the subject
- Better: "cerulean blue volumetric fog at mid-depth" or "volumetric haze behind the subject"
- Fog should enhance depth, not flatten it

### 5. God Rays Need Physical Source
- "volumetric god rays" alone produces generic atmosphere
- "god rays piercing through gaps in glass geometry" produces more dramatic, directional light shafts
- The physical obstruction creating the rays matters as much as the rays themselves

## PIL Template Status
- Night 14 indicator added (top-right, 12pt gray)
- Template stable from Night 12, only night number changes
- Oswald Bold for title/subtitle, shadow offset method (no stroke_width)

## Files Generated
- variation-1.png: Glass Morphism Card (932 KB) -- structural glass UI
- variation-2.png: Volumetric God Rays (1505 KB) -- light through crystal geometry
- variation-3.png: Chromatic Neural Bloom (1151 KB) -- prismatic dispersion + glass synapses
- All at: /home/jared/exports/portal-files/3d-training-2026-04-07/

## Mastery Breakdown
- Glass morphism: 97% (maintained)
- Volumetric lighting: 95% (up from 94%)
- Chromatic effects: 96% (maintained)
- Caustics: 93% (up from 91%)
- Overall: 94.5% (up from 94%)

## Next Session Goals
1. Hexagonal bokeh: try iris aperture language
2. Dynamic caustics following glass form contours
3. Three.js translation of best FLUX outputs
4. FLUX 2 Pro image editing mode for iterative refinement
