# WebGL Fluid Simulation Investor Page

**Date**: 2026-03-17
**Type**: technique
**Topic**: Embedding Pavel Dobryakov WebGL fluid sim into a self-contained HTML page with scroll animations

## Key Patterns

### Fluid Sim Integration
- Remove all dat.GUI references (startGUI function + all gui.add calls)
- Remove all ga() analytics calls
- Replace external PNG dithering texture with procedural: create 64x64 random noise Uint8Array, upload as gl.RGB texture
- Replace createTextureAsync(url) with inline gl.texImage2D call
- Rename update() to fluidLoop() to avoid name conflicts with page JS
- Rename render() to renderFluid() to avoid conflicts
- Change canvas reference from `document.getElementsByTagName('canvas')[0]` to getElementById

### Orange-Only Color Override
Replace generateColor() entirely:
```js
function generateColor() {
  const hue = 15 + Math.random() * 25; // orange-red to amber
  const saturation = 0.85 + Math.random() * 0.15;
  const value = 0.6 + Math.random() * 0.4;
  let c = HSVtoRGB(hue / 360, saturation, value);
  c.r *= 0.18; c.g *= 0.04; c.b *= 0.01;
  return c;
}
```
Set BACK_COLOR: { r: 8, g: 10, b: 18 }, DENSITY_DISSIPATION: 2.2

### GSAP ScrollTrigger Z-Depth Emergence
- sections use perspective:1400px on parent
- cards start: z:-800, scale:0.4, opacity:0, filter:blur(20px)
- cards emerge to: z:0, scale:1, opacity:1, filter:blur(0px)
- cards sink on leave: z:-600, scale:0.6, opacity:0, filter:blur(16px)
- Use onEnter/onLeave/onLeaveBack/onEnterBack callbacks (not scrub) for snappy transitions
- scroller must be set to the scrollable div, not window (body/html overflow:hidden)

### Auto-Splat
`setInterval(() => { splatStack.push(parseInt(Math.random()*4)+2); }, 3500);`
Keeps fluid alive without mouse interaction.

### Chat-Triggered Splat
`splatStack.push(3);` on every chat message — fluid responds to investor interactions.

## File Location
`exports/cf-pages-deploy/investors/index.html`
~1817 lines, ~100KB, fully self-contained

## Gotchas
- html/body must have overflow:hidden — scroll container is the fixed div
- GSAP ScrollTrigger needs scroller option pointing to the scrollable element
- Mobile: reduce SIM_RESOLUTION to 64, DYE_RESOLUTION to 512
- Passwords: pureinvestor2026, pt2026, puretech, puretechnology
