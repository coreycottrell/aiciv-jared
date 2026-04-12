# Investor One-Pager: Three.js Plasma Fire Build

Date: 2026-03-19
Type: operational | technique

## What Was Built

Path: exports/cf-pages-deploy/investor-one-pager/index.html
Lines: 1711

## Three.js Fire Architecture

Used Three.js ES module (importmap cdn 0.162.0):
- OrthographicCamera(-1,1,1,-1) + PlaneGeometry(2,2) fullscreen quad
- ACESFilmicToneMapping + exposure 1.2 for cinematic look
- ShaderMaterial with uTime, uIntensity, uResolution uniforms
- PixelRatio capped at 2x for performance

## Fragment Shader (3-pass domain warp)

- Pass q: standard FBM double-domain
- Pass r: fbm(p + 4*q) — deep warp
- Pass s: fbm(p + 5.5*r) — triple warp for maximum organic chaos
- 5 fire columns (3 main + 2 tendrils)
- firePalette: #080a12 → crimson → #f1420b → amber → hot white
- 24 procedural ember sparks with lifecycle, drift, chromatic fringe
- Smoke layer upper 40% (blue-black fbm tint)
- Tone map: col/(col+0.9) + gamma 0.86
- Scroll + mousemove reactivity via intensity uniform

## Password Gate

Passwords: pureinvestor2026, pt2026, puretech, puretechnology
Bypass: ?open=1 OR sessionStorage('pt_investor_auth_v2')

## Deployment

URL: https://purebrain-staging.pages.dev/investor-one-pager/
HTTP: 200 verified
Deploy hash: 0b81e8f9

## Key Lesson

3-pass domain warp (q→r→s) produces significantly more organic fire than 2-pass.
OrthographicCamera(-1,1,1,-1) is correct for fullscreen shader quads with Three.js.
