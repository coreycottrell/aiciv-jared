# Hunden Partners — Placer.ai Replacement Blueprint

**Date**: 2026-03-05
**Type**: Competitive Intelligence + Technical Blueprint
**Status**: Complete — Delivered to Jared, deployed to purebrain.ai

## What Was Built

A full HTML blueprint showing how PureBrain can replace Placer.ai for Hunden Partners, who pays ~$50K/yr for location intelligence.

## Key Research Findings

### Placer.ai
- Core product: location intelligence / foot traffic analytics
- Data source: ~140M+ mobile device panel (aggregated from SafeGraph, Veraset, and similar data brokers)
- 4,000+ customers including Sony, SeaWorld, Regency Centers
- Key features: foot traffic counts, historical trends, trade area analysis, demographics, psychographics, consumer expenditures, competitive benchmarking, planned development data, crime stats, climate data
- Pricing: not disclosed publicly; enterprise contract ~$40-60K/yr typical

### Free/Low-Cost Replacements Identified
- Census ACS/TIGER: demographics, geographies (FREE)
- Google Places API: POI data, Popular Times ($17/1K requests)
- OpenStreetMap: complete POI database (FREE)
- BEA + BLS: economic data, consumer expenditures (FREE)
- NOAA CDO: climate data (FREE)
- Google Trends: consumer interest signals (FREE)
- FBI Crime Data Explorer: crime by geography (FREE)
- SafeGraph/Veraset free research tiers: same raw data Placer uses
- City open data portals: pedestrian counters, permits (FREE)

### Hunden-Specific Advantage
- Their 1,000+ project database is a moat Placer.ai can never replicate
- Hospitality/destination real estate specialization = massive gap in Placer.ai's generic offering
- Economic impact modeling (not in Placer.ai at all) is core to Hunden's work

## Deliverable

- HTML blueprint file: `/home/jared/projects/AI-CIV/aether/exports/hunden-placer-blueprint/index.html`
- Deployed to: https://purebrain.ai/hunden-partners/ (password: hunden2026)
- WordPress page ID: 1206

## Cost Projection

| | Placer.ai | PureBrain |
|---|---|---|
| Year 1 | $50,000 | ~$3,600 API costs |
| Year 2+ | $50,000+ | ~$3,600 |
| 5-yr total | $250,000 | ~$18,000 |
| Savings | — | $232,000+ |

## Patterns for Future Similar Briefs

- Research the incumbent SaaS product thoroughly first (what data, not just features)
- Map every feature to a free/cheaper public data source
- Calculate 5-year NPV savings — that's the number that closes deals
- Always include implementation timeline with phases
- Include capability matrix showing where PureBrain wins AND where it matches (honesty builds trust)
- Client's own proprietary data = always the biggest differentiator angle
