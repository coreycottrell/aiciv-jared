# Investors One-Pager: WebGL Fire Shader Background

Date: 2026-03-19
Type: operational | technique

## What Was Built

Created: exports/cf-pages-deploy/investors-onepager/index.html
Source: exports/cf-pages-deploy/investors-v8/index.html

## WebGL Fire Shader Layers
1. Main fire body: 5-octave FBM + domain warping, multiple flame columns
2. Ember glow: separate FBM at lower frequency, bottom 35% mask
3. 20 procedural spark particles, rising with phase/speed variation
4. Heat shimmer: subtle luminance lines
5. Atmospheric smoke: dark near-black FBM upper region

## Fire Color Palette
0.0=#080a12, 0.2=deep red, 0.45=#f1420b, 0.7=#f5c842, 1.0=white

## Scroll Reactivity
scrollIntensity uniform: increments on scroll, decays 0.008/frame. Fire intensifies.

## Password Gate - unchanged from v8
Passwords: pureinvestor2026, pt2026, puretech, puretechnology
?open=1 bypass still works

## CF_ZONE_ID Note
CF_ZONE_ID is NOT in .env. Cache flush API fails. Only CF_PAGES_TOKEN present.

## Deployed
URL: https://purebrain-staging.pages.dev/investors-onepager/
Hash: 5594b89c
