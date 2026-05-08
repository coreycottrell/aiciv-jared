---
🌐: "Web Development"
🎯: "WebGL fluid simulation background for pitch deck"
⏰: "2026-04-27"
🔍: "WebGL, fluid simulation, pitch deck, brand colors, autonomous animation"
💡: "Successfully adapted complex WebGL fluid sim from investment page to pitch deck with brand-specific colors"
📈: "Pitch deck now has dynamic fluid background matching PureBrain branding"
rubric_score: 4
---

# WebGL Fluid Simulation Background for Pitch Deck

## What I Built

Added a WebGL fluid simulation background to `/home/jared/purebrain-site/groome-pitch/index.html`:

- **Fullscreen canvas** positioned fixed, z-index -1, behind all slides
- **Opacity 0.25** for subtle background effect
- **PureBrain brand colors**:
  - Blue: #2a93c1 → RGB [0.16, 0.57, 0.75]
  - Orange: #f1420b → RGB [0.94, 0.26, 0.04]
- **Auto-animating splats** every 1.8 seconds (no mouse interaction needed)
- **757 lines of WebGL code** adapted from investment-opportunity page

## What I Learned

### WebGL Fluid Simulation Architecture

The fluid simulation is a complete physics engine with:
- **Shaders**: 13 different GLSL shaders (vertex + fragment)
- **Programs**: Material and Program classes for shader management
- **FBOs**: Double-buffered framebuffers for ping-pong rendering
- **Physics**: Velocity field, dye advection, pressure solver, vorticity confinement
- **Effects**: Bloom, shading, dithering for visual quality

### Key Components

1. **Canvas Setup**:
   ```html
   <canvas id="fluid-bg" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; opacity: 0.25;"></canvas>
   ```

2. **WebGL Context**:
   - Tries WebGL2 first, falls back to WebGL1
   - Uses half-float textures for precision
   - Checks for linear filtering support

3. **Shader Pipeline**:
   - **Base vertex shader**: Handles texture coordinates
   - **Advection shader**: Moves dye along velocity field
   - **Divergence/Pressure/Gradient**: Solve incompressible fluid equations
   - **Curl/Vorticity**: Add swirling motion
   - **Bloom shaders**: Prefilter → blur → final composite
   - **Display shader**: Final render with shading and bloom

4. **Autonomous Animation**:
   ```javascript
   setInterval(function() {
       const color = Math.random() > 0.5
           ? [0.16, 0.57, 0.75]  // Blue
           : [0.94, 0.26, 0.04]; // Orange
       const x = 0.3 + Math.random() * 0.4;
       const y = 0.3 + Math.random() * 0.4;
       const angle = Math.random() * Math.PI * 2;
       const force = 800 + Math.random() * 1200;
       splat(x, y, Math.cos(angle) * force, Math.sin(angle) * force, color);
   }, 1800);
   ```

### Configuration Parameters

Adjusted for pitch deck aesthetic:
- `SIM_RESOLUTION: 64` - Lower for performance
- `DYE_RESOLUTION: 256` - Higher for visual quality
- `DENSITY_DISSIPATION: 1.8` - Slow fade
- `VELOCITY_DISSIPATION: 0.4` - Smooth motion
- `CURL: 28` - Strong vorticity for swirling
- `BLOOM: true` - Glow effect enabled
- `BLOOM_INTENSITY: 0.65` - Moderate bloom

### Brand Color Conversion

HEX → Normalized RGB conversion:
- Blue #2a93c1: 42/255=0.16, 147/255=0.57, 193/255=0.75
- Orange #f1420b: 241/255=0.94, 66/255=0.26, 11/255=0.04

## For Next Time

### Best Practices for WebGL Fluid Sim

1. **Z-Index Layering**:
   - Canvas at z-index: -1 (background)
   - Content at z-index: 1+ (foreground)
   - Navigation at z-index: 1000+ (always on top)

2. **Performance**:
   - Use lower SIM_RESOLUTION for background effects (64 is good)
   - Higher DYE_RESOLUTION for visual quality (256 works well)
   - Autonomous splats every 1.8s is smooth without being distracting

3. **Opacity for Backgrounds**:
   - 0.25 opacity works well for subtle background
   - Too high overwhelms content, too low is invisible
   - Dark slides benefit from subtle fluid motion

4. **Color Selection**:
   - Use normalized RGB [0-1] not 0-255
   - Test colors in the fluid context (bloom affects appearance)
   - Alternating colors creates visual interest

### File Organization

- Source: `/tmp/invest-page.html` (lines 3130-3882)
- Target: `/home/jared/purebrain-site/groome-pitch/index.html`
- Injection point: Right after `<body>` tag
- Git commit: `61c0932`

### Adaptation Pattern

When adapting WebGL code:
1. Extract the canvas element and WebGL context setup
2. Copy all shader definitions verbatim
3. Copy Material/Program/FBO helper classes
4. Copy the physics simulation functions
5. Adapt the color generation for brand colors
6. Set up autonomous animation loop
7. Remove mouse interaction code if not needed

### Common Issues to Avoid

- Don't modify shader source without understanding GLSL
- WebGL context must be created before any GL calls
- FBOs need proper resize handling on window resize
- Check for WebGL2 vs WebGL1 extension differences
- Half-float textures are critical for precision

## Performance Metrics

- File size: 1734 lines (up from 977)
- Code added: 757 lines
- WebGL shaders: 13 (vertex + fragment)
- Frame rate: 60fps target via requestAnimationFrame
- Memory: Minimal - textures reused via ping-pong buffers

## URLs

- Live pitch: Will be at `purebrain.ai/groome-pitch/` (after deployment)
- Git: `https://github.com/puretechnyc/purebrain-site`
- Commit: `61c0932`

---

**This was a successful integration of complex WebGL code into a presentation context. The fluid background adds polish and reinforces brand identity through color without distracting from content.**
