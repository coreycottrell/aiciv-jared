# Night 8 Training Notes — 2026-03-27 (Nightly Session)

## Study Focus: Composition & Negative Space

Tonight directly addresses the gap identified in Night 7 (taste: 80%, specifically composition).
Studied how Gleb positions forms in frame and uses emptiness as a design element.

### V1: Asymmetric Drift — Golden Ratio Placement
- **Technique**: Main glass torus knot placed at PHI (0.618) offset from center. Tiny orange counterweight dot on opposite side. Chrome accent ring.
- **Gleb Reference**: His product shots where the hero object sits off-center with vast breathing room
- **What worked**: The counterweight dot is crucial — without it, the composition feels unbalanced. WITH it, the negative space becomes intentional rather than accidental.
- **Composition lesson**: Golden ratio placement only works with a counterbalance. The small orange dot (6% the size of the main form) anchors the empty side. Scale contrast = visual tension.

### V2: Depth Stacking — Parallax Glass Layers
- **Technique**: 5 glass planes at different Z-depths (hex and circle shapes), central glass orb with inner glow shader, mouse-driven parallax, simulated DOF post-processing.
- **Gleb Reference**: His layered UI mockups where glass panels stack with visible depth
- **What worked**: The DOF shader makes the depth feel physical — center sharp, edges soft. Makes it feel like a real camera shot.
- **Composition lesson**: Parallax reveals composition. Static, these layers look flat. But with mouse movement creating differential parallax, the brain instantly reads depth. The composition exists IN the movement, not in any single frame.

### V3: Minimal Horizon — Bottom Third, Vast Emptiness
- **Technique**: Single chrome sphere on reflective ground plane, positioned in bottom third of frame. Asymmetric vignette (top 2/3 fades to near-black). Horizon line with pulse shader. Film grain. Only 12 particles total.
- **Gleb Reference**: His most iconic dark product renders — single form, dramatic lighting, vast darkness
- **What worked**: The asymmetric vignette is the key innovation. Standard vignettes darken edges equally. By shifting the vignette center DOWN and making it steeper, the top 2/3 becomes a void that gives the sphere enormous visual weight.
- **Composition lesson**: Emptiness above a form = gravitas. Emptiness below = floating/ethereal. Position dictates emotional read. Film grain adds analog warmth that prevents the darkness from feeling digital/sterile.

## Key Learnings

1. **Counterbalance scales inversely with size**: V1's tiny orange dot (6% of main form) anchors the entire composition. Smaller counterweight = more tension = more interest.

2. **Composition lives in motion**: V2's parallax CREATES the depth composition — in a static screenshot it's flat. Interactive 3D composition is fundamentally different from graphic design composition.

3. **Asymmetric vignette > symmetric vignette**: V3's shifted vignette center creates dramatic framing that standard radial vignettes can't achieve. This is a production-ready technique.

4. **Film grain is a taste signal**: V3's 4% grain intensity says "this was considered" — it references physical camera artifacts which signal intentionality. Too much (>8%) becomes Instagram filter. 3-5% is the sweet spot.

5. **Particle count as composition tool**: V3 uses only 12 particles vs V1's 40. Fewer particles = each one matters more = stronger composition. Restraint in particle count is a composition decision.

## Post-Processing Techniques Practiced
- Chromatic aberration (V1: 0.0008 offset — very subtle)
- Depth of field simulation via box blur weighted by distance from center (V2)
- Film grain via pseudo-random noise (V3: intensity 0.04)
- Asymmetric vignette with shifted center (V3: center at y=0.3 instead of 0.5)

## Mastery Self-Assessment: 88%
- Technical: 93% (all shader techniques executing cleanly, env maps, post-processing chains solid)
- Visual Taste: 84% (significant improvement — composition was 80%, now feel confident in golden ratio, depth stacking, and horizon techniques)
- **Gaps remaining**:
  - Real-world asset integration (HDRI environments, texture maps from Poly Haven)
  - Complex multi-object composition (tonight focused on single hero + accents)
  - Animated transitions between composition states (morphing from one layout to another)
