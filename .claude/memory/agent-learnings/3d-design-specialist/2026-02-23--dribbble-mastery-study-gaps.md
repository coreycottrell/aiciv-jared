# Memory: 35 Dribbble Reference Study + Mastery Gap Analysis
**Date**: 2026-02-23
**Agent**: 3d-design-specialist
**Type**: synthesis
**Topic**: Milkinside/Gleb Kuznetsov visual language + PureBrain application gaps

---

## Context

Studied 35 Dribbble references from Gleb Kuznetsov and Milkinside. Jared's directive: "this isn't just about 3D design for your avatar - this is learning fire User Experience Design for the future."

## Critical Discovery: Milkinside Uses Offline Rendering

**Milkinside tool stack**: Cinema 4D + Houdini FX + Octane Render + Redshift + 300+ plugins
**NOT Three.js / WebGL**. Their Dribbble shots are offline renders (sometimes 87 hours on 5 RTX cards).
**Our role**: Reverse-engineer their offline renders into real-time Three.js that achieves similar emotional impact.

## The Hex-Cube Insight (Samsung R3 Shot - Most Important)

A perfect cube viewed from its space diagonal (1,1,1 axis) appears as a perfect regular hexagon in isometric projection.

**Mathematical equivalence**: hexagonal grids and cubic grids describe the same space.
**Rotation to achieve hex view**: ISO_X = -35.264 degrees, ISO_Y = 45 degrees.

**PureBrain application**: The avatar should be a RoundedBox (chamfered cube) not a sphere. At isometric angle = reads as PureBrain hexagon logo. Rotating = reveals cube nature = 4 distinct visual readings from one geometry.

```jsx
<RoundedBox args={[1.2, 1.2, 1.2]} radius={0.05} smoothness={8}
  rotation={[-35.264 * Math.PI/180, 45 * Math.PI/180, 0]}>
  <MeshTransmissionMaterial color="#2a93c1" ... />
</RoundedBox>
```

## The Three-State AI Visual Framework

Gleb designs for 3 user states:
1. Making a request (input receiving) → LISTENING visual state
2. Waiting for results (processing) → THINKING visual state
3. Reading results (output delivery) → SPEAKING visual state

Each state has defined: color, motion intensity, material tint, external vs internal motion balance.

State transitions are as important as the states themselves:
- Idle → Listening: 0.3s ease-out, brightness surge
- Listening → Thinking: 0.5s ease-in-out, withdrawal inward
- Thinking → Speaking: 0.4s spring, bloom surge
- Speaking → Idle: 1.5s ease-in, gradual withdrawal

## Gap Analysis Summary

**Real-time Three.js technical**: 85% (gaps: vertex deformation, orbital rings, internal particles, iridescence)
**Design system depth**: 18% (gaps: design tokens, multi-scale library, product UI patterns)

**1-week plan to close real-time gap**:
- Day 1: RoundedBox hex-cube at isometric angle
- Day 2: Orbital ring system (3 rings, state-responsive speed)
- Day 3: Vertex displacement simplex noise shader
- Day 4: Internal particle universe
- Day 5: Multi-view gallery (3 angles simultaneously, Samsung R3 pattern)
- Day 6: Design token codification
- Day 7: Production build + documentation

**4-8 weeks to close design system gap**: tokens, multi-scale library, product UI patterns

## Key Technique Discoveries

1. **Chamfered cube > hexagonal prism**: More visual readings, correct geometric relationship
2. **Orbital rings at different inclinations**: 3 rings at 0°, 30°, 60° = orbital system complexity without chaos
3. **Vertex displacement with custom shader material**: `three-custom-shader-material` package
4. **Internal particles need additive blending**: `blending={THREE.AdditiveBlending}` + `depthWrite={false}`
5. **State color mapping**: idle=blue, listening=cyan, thinking=violet, speaking=warm-gold
6. **Warm-cool tension is non-negotiable**: Cool blue + warm gold = intelligent life. Pure cool = robotic.

## The Gleb UX Philosophy (Red Dot Interview)

"Great communication design is almost always subconscious."

The geometry IS the UX. The material communicates product quality. The state machine IS the brand personality.
For future PureBrain products: the hex-cube as navigation anchor, data as gem elements, loading as materialization.

## Deliverable Files

All analysis exported to:
- `/home/jared/projects/AI-CIV/aether/exports/overnight-content/dribbble-study/01-reference-analysis.md`
- `/home/jared/projects/AI-CIV/aether/exports/overnight-content/dribbble-study/02-samsung-r3-cube-deep-analysis.md`
- `/home/jared/projects/AI-CIV/aether/exports/overnight-content/dribbble-study/03-technique-taxonomy.md`
- `/home/jared/projects/AI-CIV/aether/exports/overnight-content/dribbble-study/04-mastery-gap-analysis.md`

## Tags

3d-design, milkinside, gleb-kuznetsov, hex-cube-duality, isometric-projection, ai-sphere, state-machine, design-system, vertex-displacement, orbital-rings, purebrain-brand
