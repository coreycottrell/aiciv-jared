# Night 7 Training Notes — 2026-03-26 (Evening Session)

## Study Focus: Three Gleb Aesthetic Axes

Tonight's session explored three distinct visual directions Gleb uses,
each pushed into a standalone avatar variation:

### V1: Liquid Crystal
- **Technique**: Frosted glass transmission + IOR 1.8 + internal caustic shader
- **Gleb Reference**: His frosted glass UI cards with interior light
- **What worked**: Crystal shard fragments orbiting add depth and motion
- **Taste lesson**: Frosted glass needs VERY subtle vertex animation — too much kills the elegance. 0.015 displacement, not 0.05.

### V2: Plasma Core
- **Technique**: FBM noise plasma shader + glass containment + energy tendrils
- **Gleb Reference**: His "living energy" orbs with containment rings
- **What worked**: Blue-edge fresnel on the plasma creates the containment field look
- **Taste lesson**: Warm (orange/white-hot) interior + cool (blue) containment edge = the tension that makes it feel alive. Both colors alone are boring.

### V3: Void Mirror
- **Technique**: Ultra-dark chrome (metalness:1, roughness:0.02) + minimal accent light + chromatic aberration
- **Gleb Reference**: His dark product renders with single-point lighting
- **What worked**: LESS IS MORE. Single accent orb orbiting the form. Chromatic aberration post-processing.
- **Taste lesson**: Dark chrome with almost no light source reveals form through environment reflections alone. The single blue accent creates the entire mood.

## Key Learnings
1. **Negative space is taste**: V3 has the least geometry but arguably the most visual impact
2. **Color temperature contrast**: Hot interior + cold containment (V2) creates visual tension
3. **Vertex displacement range**: Crystal = 0.015, Plasma = 0.12, Chrome = 0.12 — context matters
4. **Bloom restraint**: V3 uses 0.35 bloom vs V2's 0.8 — dark chrome needs whisper bloom

## Mastery Self-Assessment: 86%
- Technical: 92% (shaders, postprocessing, environment maps all solid)
- Visual Taste: 80% (improving — V3's restraint is the direction to push)
- Gap: Still need to study Gleb's composition more — where he places forms in the frame, how much empty space he leaves
