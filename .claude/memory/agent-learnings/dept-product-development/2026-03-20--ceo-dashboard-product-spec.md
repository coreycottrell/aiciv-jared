# CEO Dashboard — Product Spec Memory

**Date**: 2026-03-20
**Type**: operational
**Topic**: CEO Dashboard product scope — architecture decision, user stories, data model, 4-night sprint

## Key Architecture Decision

- SEPARATE app from 777 Command Center (not inside it)
- Linked via shared Cloudflare Access + Google OAuth
- Connected via CF KV namespace (business mandala % syncs to 777)
- Navigation links both ways: 777 has "Business" tab, CEO Dashboard has "Personal Goals" link
- Same CF Pages + Workers + D1 stack as 777 (consistent infra)

## North-Star KPI

Free Cash Flow (FCF) per share — every metric must connect to FCF

## Tier-1 Tiles (always visible)

FCF per share, Cash on hand, Net debt / FCF, Run-rate burn, 12-month FCF forecast

## 6 Pillars (Tier-2)

Growth & Revenue, Customer & Brand, Operational Excellence, People & Culture, Innovation & Ideation, Risk & Resilience

## Key Enhancements Added Beyond Source Docs

1. Aether Agent Feed — agent activity tile, POST /api/agent-activity endpoint
2. PureBrain Revenue Tile — live Stripe/PayPal, MRR by tier
3. Weekly CEO Brief — Monday 07:00 ET, Claude-generated, Telegram + email + Drive
4. Decision Log — institutional memory of decisions with 30/60/90 day reviews
5. Investor-Ready Export — one-click formatted investor packet
6. OKR Tracker with Mandala Mirror — business OKRs linked to 777 personal mandala
7. Competitive Intelligence Tile — Aether web-researcher weekly scan

## 4-Night Sprint

- Night 1: Foundation + FCF Landing Page (auth, D1 schema, Stripe/PayPal, Tier-1 tiles)
- Night 2: Pillar Drill-Downs + Alerting (6 drill-down pages, threshold alerts)
- Night 3: AI Layer + Scenario Sandbox + OKR + Decision Log + Agent Feed
- Night 4: Export + Board View + 777 Bridge + Polish + QA

## Data Model (8 entities)

kpi_snapshots, kpi_definitions, okr_records, decisions, alerts, agent_activity_log, users, scenarios, annotations

## Recommended Start

Data Readiness Audit today (check what Stripe/PayPal/Sheets data is actually accessible), then Night 1 build tonight or tomorrow overnight.

## File Location

exports/departments/product-development/specs/2026-03-20--ceo-dashboard-spec.md
