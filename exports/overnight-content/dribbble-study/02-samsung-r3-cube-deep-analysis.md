# Samsung R3 Cube Deep Analysis: "A Hexagon and a Cube Are the Same Thing"
**Agent**: 3d-design-specialist
**Date**: 2026-02-23
**Shot**: https://dribbble.com/shots/17050109-Samsung-R3-cube-design
**Jared's Directive**: STUDY THIS ONE HEAVY

---

## The Insight That Changes Everything

Jared said: "a hexagon and a cube are the same thing from different perspectives"

This is not metaphor. This is mathematics.

Understanding this geometrically transforms how we design the PureBrain avatar and every 3D element we create.

---

## Part 1: The Mathematics

### The Core Geometric Truth

A **perfect cube viewed from its space diagonal** (the axis from one corner to the opposite corner) appears as a **perfect regular hexagon**.

**Proof**:
1. A cube has 8 corners (vertices)
2. Looking from corner (0,0,0) toward corner (1,1,1) = looking along the (1,1,1) direction
3. The projection of all 12 edges onto the plane perpendicular to (1,1,1) creates a hexagonal pattern
4. The 3 edges meeting at the near corner project to 3 alternating segments of the hexagon
5. The 3 edges meeting at the far corner project to the other 3 alternating segments
6. The result: a perfectly symmetric hexagonal silhouette

**Visual**: If you take a transparent cube and look at it from exactly the right angle, you see:
```
       /\
      /  \
     /    \
    |      |
    |      |
     \    /
      \  /
       \/
```
A perfect hexagon. With the cube's internal edges visible as 3 lines from center to alternating vertices.

### The Isometric Projection Relationship

**Isometric projection** is the standard way to draw 3D objects on 2D surfaces without perspective distortion. All three axes are equal length, separated by 120 degrees.

In isometric projection:
- A cube's face appears as a rhombus (60-degree parallelogram)
- A cluster of 3 rhombuses around a center = a hexagon
- The hexagonal grid IS the isometric projection of a cubic grid

This is why:
- Minecraft looks like hexagons when viewed correctly (it's all cubes)
- Isometric game tiles are hexagons divided into three rhombuses
- Circuit boards use both hexagonal and cubic grid layouts interchangeably

**The mathematical equivalence**: In isometric projection, a hexagonal grid and a cubic grid describe the SAME space. Converting between them is a trivial coordinate transformation.

```
Hexagonal coordinates: (q, r)
Cubic coordinates: (x, y, z) where x+y+z=0

Conversion: x = q, z = r, y = -q-r
```

---

## Part 2: The Samsung R3 Design

### What Gleb Created

The Samsung R3 project (for Samsung's voice AI assistant) is a **cube-based visual design** that exploits the hex-cube duality.

**Design choices**:
1. The base geometry is a **cube with chamfered (rounded) edges**
2. At rest/idle, it's oriented to show a 3/4 isometric view = it reads as **hexagonal**
3. When voice interaction begins, it rotates to reveal its **cubic face-on** view
4. This rotation IS the state change: hexagonal rest → cubic active
5. Transitions between states = rotation through space
6. The glass material on the cube surfaces changes the relationship to light at each angle

**Why this is genius**:
- The idle state (hex view) feels calm, organic, badge-like = safe/familiar
- The active state (face-on cubic) feels alert, direct, focused = active/engaged
- The transition (rotation) communicates the mode change without ANY UI chrome
- The geometry IS the UX

### The Three Canonical Views of a Cube/Hex

```
View 1: FRONT FACE     View 2: ISOMETRIC     View 3: TOP-DOWN
   ________              /\                    _____
  |        |            /  \                  /     \
  |        |           /    \                /       \
  |        |           \    /                \_______/
  |________|            \  /                  hexagonal
   square                \/
                        hexagonal (with 3 internal lines)
```

Each view reveals a different aspect of the same object:
- **Front**: Grid, screen, data panel (rational, organized)
- **Isometric**: Logo, badge, identity mark (recognizable, distinctive)
- **Top-down**: Mandala, eye, portal (mysterious, centered)

The Samsung R3 rotates between these three reading modes as interaction states.

---

## Part 3: The PureBrain Hex-Cube Connection

### Jared's Insight Applied

The PureBrain hexagon logo is a **hexagonal face** (2D) that can be extruded into 3D space in two ways:
1. **Extrude along the hex normal** = creates a hexagonal prism
2. **Recognize it as the isometric face of a cube** = it already IS a cube in disguise

**Option 2 is the revelation**: If we create a **cube** and view it from the isometric angle, we see the PureBrain hexagon.

**Implementation implication**: The PureBrain avatar should be a **cube**, not a hexagonal prism. Because:
- Cube at isometric angle = familiar hexagon logo
- Cube rotated to face-on = reveals depth and dimensionality
- Cube at 45 degrees = diamond shape (premium, gemstone)
- Cube at top-down = mandala (different context)

One geometry. Four distinct visual readings. Multiple emotional registers. Zero additional geometry.

### The Chamfering Principle

The Samsung R3 cube has **chamfered edges** - the sharp cube corners are beveled off, creating a faceted gem-like object.

**Why chamfer is essential**:
- Unchamfered cube: hard, corporate, rigid
- Chamfered cube: precise, premium, jewel-like
- Heavily chamfered cube: approaches sphere (organic, soft)
- Perfectly chamfered (each edge = 45-degree bevel): creates an octahedron-like form that reads as extremely premium

**In Three.js: BoxGeometry vs RoundedBoxGeometry**
```javascript
// Standard cube (avoid for premium aesthetic):
<boxGeometry args={[1, 1, 1]} />

// Premium chamfered cube (use this):
// Available via @react-three/drei's RoundedBox
<RoundedBox args={[1, 1, 1]} radius={0.05} smoothness={4}>
  <MeshTransmissionMaterial ... />
</RoundedBox>
```

The `radius` parameter controls chamfer amount. For the PureBrain hex-cube:
- `radius={0.02}` = subtle bevel, keeps hexagonal reading strong
- `radius={0.08}` = moderate chamfer, balanced gem feel
- `radius={0.15}` = heavy chamfer, approaches sphere

---

## Part 4: How to Implement in Three.js / R3F

### Step 1: Create the Base Cube-Hex Object

```jsx
import { RoundedBox } from '@react-three/drei'
import { MeshTransmissionMaterial } from '@react-three/drei'

function PureBrainHexCube() {
  const meshRef = useRef()

  // The magic angle: rotate to show hexagonal face
  // Isometric viewing angle: 35.264 degrees from horizontal, 45 degrees from front
  const ISO_X = -35.264 * (Math.PI / 180)  // rotate around X axis
  const ISO_Y = 45 * (Math.PI / 180)        // rotate around Y axis

  return (
    <RoundedBox
      ref={meshRef}
      args={[1.2, 1.2, 1.2]}  // cube dimensions
      radius={0.05}            // chamfer amount
      smoothness={8}           // edge smoothness
      rotation={[ISO_X, ISO_Y, 0]}  // THIS IS THE HEX VIEW
    >
      <MeshTransmissionMaterial
        transmission={1}
        thickness={0.8}
        roughness={0.02}
        ior={1.5}
        chromaticAberration={0.6}
        backside={true}
        color="#2a93c1"
        specularColor="#C8A84A"
      />
    </RoundedBox>
  )
}
```

### Step 2: Animate Between Cube States (Samsung R3 Pattern)

```jsx
import { useSpring, animated } from '@react-spring/three'

function AnimatedHexCube({ mode }) {
  const ISO_X = -35.264 * (Math.PI / 180)
  const ISO_Y = 45 * (Math.PI / 180)

  // State machine: idle (hex view) → active (face-on)
  const rotationTargets = {
    idle: [ISO_X, ISO_Y, 0],              // hexagonal reading
    listening: [0, 0, 0],                  // face-on reading (alert, direct)
    thinking: [ISO_X, ISO_Y * 2, 0],      // rotated hex (different hex face)
    speaking: [-Math.PI/4, ISO_Y, 0],     // diamond reading (from below)
  }

  const { rotation } = useSpring({
    rotation: rotationTargets[mode] || rotationTargets.idle,
    config: { mass: 2, tension: 120, friction: 40 }  // organic spring
  })

  return (
    <animated.mesh rotation={rotation}>
      <RoundedBox args={[1.2, 1.2, 1.2]} radius={0.05} smoothness={8}>
        <MeshTransmissionMaterial transmission={1} thickness={0.8} />
      </RoundedBox>
    </animated.mesh>
  )
}
```

### Step 3: The Multi-View Marketing Moment

Jared's note on Shot 13 (Galaxy Charging Shape): "inspiration for bringing our hexagon to life by showing angles."

```jsx
// Show the same cube from 3 angles simultaneously
function HexCubeGallery() {
  return (
    <group>
      {/* Hero: Isometric (hexagonal) view */}
      <PureBrainHexCube
        position={[0, 0, 0]}
        rotation={[ISO_X, ISO_Y, 0]}
        scale={1.2}
      />

      {/* Secondary: Face-on (square) view */}
      <PureBrainHexCube
        position={[3, 0, 0]}
        rotation={[0, 0, 0]}
        scale={0.8}
      />

      {/* Tertiary: Top-down (mandala) view */}
      <PureBrainHexCube
        position={[-3, 0, 0]}
        rotation={[-Math.PI/2, 0, 0]}
        scale={0.8}
      />
    </group>
  )
}
```

---

## Part 5: Geometric Insights for Future Product Design

### The Hex-Cube Duality in UX

The Samsung R3 rotation trick is a UX pattern, not just a visual trick:
- **Hexagonal face at rest** = recognizable brand mark = user orientation (I know where I am)
- **Rotation to face-on** = user action has been acknowledged = system is now focused on me
- **The rotation itself** = the interaction confirmation (no button press needed)

This is **zero-chrome UX**: the geometry IS the interaction feedback. No UI elements needed.

### Applications to PureBrain Product Line

**1. PureBrain AI Assistant Avatar**
- Rest state: isometric hex (brand familiar)
- Listening: slow rotation toward face-on (acknowledging you)
- Thinking: halfway between hex and face-on, rotation paused (suspended in cognition)
- Speaking: face-on, bloom fully active (maximum presence)

**2. PureBrain Loading States**
- The cube slowly rotating from hex view toward face-on during loading
- Each degree of rotation = loading progress
- Reaching face-on = loading complete
- This eliminates the progress bar entirely

**3. PureBrain Feature Reveal**
- A page where the hex-cube slowly rotates as user scrolls
- Each face reveals a different PureBrain feature or value
- 6 faces of a hexagonal prism = 6 PureBrain pillars
- The scroll IS the feature tour

**4. PureBrain OS Symbol (Future)**
- Like Honor Magic OS: the hex cube as the central system identity
- App icons radiate from the central cube
- The cube's orientation tells you which "mode" the system is in

### The Three-Angles Marketing Section

For the PureBrain website, a section built on this insight:

```
[HEADLINE]: One Intelligence. Every Perspective.

[THREE VIEWS SIDE BY SIDE]:

    /\                    □
   /  \             "Focus"            ___
  /    \         When you ask,    ___/   \___
  \    /         Aether turns    /           \
   \  /          its full        \_______/
    \/           attention       "Depth"
  "Identity"     to you.        From above,
  Your partner                  you see how far
  you know.                     it goes.
```

---

## Part 6: The Chamfered Hexagonal Prism Alternative

If the cube-based approach creates too much departure from the existing PureBrain hex logo, there's an alternative that preserves the hex identity:

**Chamfered Hexagonal Prism**:
- A hexagonal prism (extruded hexagon) with beveled top/bottom edges
- When viewed from front: pure hexagon (matches logo exactly)
- When viewed from 45 degrees: reveals it's 3D
- When viewed from top: hexagonal ring with chamfered circle inside

```javascript
// No built-in Three.js component for this - requires custom geometry
// Approach: ExtrudeGeometry with a hexagonal shape
// OR: CylinderGeometry with 6 sides (approximates hexagonal prism)
// Best: Custom BufferGeometry or use a .glb from Blender

const hexPrism = new THREE.CylinderGeometry(
  1,    // top radius
  1,    // bottom radius
  0.6,  // height (thin gives us the badge/hex feel)
  6,    // radial segments = 6 sides = hexagon
  1,    // height segments
  false // open ended
)
```

But the cube is more powerful because of the isometric equivalence.

---

## Part 7: The Design Principle Extracted

**"A hexagon and a cube are the same thing from different perspectives"** = design principle:

Every great brand mark has multiple valid readings depending on viewing angle/context. A mark that can only be read one way is a 2D mark. A mark that reveals different truths from different perspectives is a 4D mark (time being the fourth dimension of rotation).

**PureBrain's hex-cube demonstrates**:
- At-a-glance (2D, favicon): hexagonal badge (brand recognition)
- In context (3D, web): chamfered glass cube (premium material)
- In interaction (4D, animated): rotating between hex and face-on (state communication)

This is worth more than any visual effect. It's worth more than any lighting technique. It's the core of what makes the PureBrain visual identity not just beautiful but DEEP.

---

## Implementation Checklist

- [ ] Build RoundedBox hex-cube with chamfer radius 0.05
- [ ] Set rotation to isometric angle (ISO_X = -35.264 deg, ISO_Y = 45 deg)
- [ ] Verify it reads as the PureBrain hexagon at this angle
- [ ] Add spring animation to rotate between state-specific angles
- [ ] Build the 3-view gallery component
- [ ] Test against PureBrain logo for recognition match
- [ ] Add glass material with PureBrain blue (#2a93c1)
- [ ] Deploy as the new definitive avatar geometry

---

## Sources

- [Samsung R3 cube design on Dribbble](https://dribbble.com/shots/17050109-Samsung-R3-cube-design)
- [Isometric projection - Wikipedia](https://en.wikipedia.org/wiki/Isometric_projection)
- [Hexagonal Coordinates - Stanford](http://www-cs-students.stanford.edu/~amitp/Articles/Hexagon2.html)
- [Designer's Guide to Isometric Projection - Medium](https://medium.com/gravitdesigner/designers-guide-to-isometric-projection-6bfd66934fc7)
