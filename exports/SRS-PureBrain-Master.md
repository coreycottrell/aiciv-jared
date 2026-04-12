---
title: "Software Requirements Specification — PureBrain.ai Platform"
version: "1.0"
date: "2026-02-26"
prepared_by: "Aether (AI Engineering Team)"
prepared_for: "Development Agency RFQ"
contact: "jared@puretechnology.nyc"
classification: "Confidential — Do Not Distribute"
---

# Software Requirements Specification
# PureBrain.ai Platform

---

```
  ╔══════════════════════════════════════════════════════════════════╗
  ║           PUREBRAIN.AI PLATFORM — MASTER SRS v1.0               ║
  ║                                                                  ║
  ║   Prepared by:  Aether (AI Engineering Team)                     ║
  ║   Prepared for: Development Agency — Request for Quote           ║
  ║   Date:         2026-02-26                                       ║
  ║   Version:      1.0 — Complete                                   ║
  ║   Contact:      jared@puretechnology.nyc                         ║
  ╚══════════════════════════════════════════════════════════════════╝
```

---

**Document Status**: COMPLETE — Ready for Agency Review

**Total Requirements**: ~439 across 10 categories

**Total Pages (estimated)**: 120+

**Scope**: Full platform rebuild from scratch

---

# EXECUTIVE SUMMARY

## What PureBrain.ai Is

PureBrain.ai is an AI partnership platform — not a chatbot, not a generic AI tool, and not a SaaS dashboard. It is a commercial offering that sells ongoing, named, context-accumulating AI partnerships to business leaders.

The core differentiator is permanent memory. A PureBrain customer names their AI partner at purchase, seeds it with business context, and that AI partner accumulates institutional knowledge about the business indefinitely. Unlike generic AI tools that forget everything at session end (the "Context Tax"), a PureBrain AI partner becomes more valuable over time.

The platform was designed around a specific thesis: the reason 75% of enterprise AI pilots stall before production is not the AI itself — it is the absence of a real partnership architecture. PureBrain addresses this with four structural differentiators: permanent memory, the naming ceremony, compounding context, and dedicated partnership design.

## System Scope

The PureBrain.ai platform comprises six service layers, four third-party integrations, and multiple content/marketing subsystems:

**Service Layers:**
1. WordPress frontend (purebrain.ai) — primary marketing and content site
2. Flask API server (api.purebrain.ai) — central backend hub, log server, payment proxy
3. Customer portal (app.purebrain.ai, Google Cloud) — Three.js 3D portal with glassmorphism UI
4. Internal hub (purebrain-hub.vercel.app, Vercel) — team command center
5. Team dashboard (pure-tech-dashboard.netlify.app, Netlify) — task management
6. Witness VPS (104.248.239.98) — real-time container provisioning ("birth pipeline")

**Third-Party Integrations (4 core):**
- Brevo: transactional email + marketing automation (21 templates, 5 workflows)
- PayPal: subscription and one-time payment processing
- Telegram: operational notifications to founder
- Google Drive: file storage and AI training data archive

**Content and Marketing Subsystems:**
- 20+ blog posts (daily publishing cadence, dual-publish to two WordPress sites)
- 8 competitor comparison pages
- 2 lead magnets (PDF audit + interactive assessment)
- AI Tool Stack Calculator (WordPress page with real-time cost calculation)
- Migration portal wizard (4-step guided flow for switching from competitor AI tools)
- 5 email automation workflows
- Bluesky and LinkedIn social distribution pipeline

## Key Architectural Decisions

An agency rebuilding this system must understand these non-obvious architectural choices that shaped the implementation:

**1. Self-Contained HTML (No React/Build Tooling)**
All frontend applications (portal, hub, dashboard, blog posts, calculator, comparison pages) are single self-contained HTML files. No npm build step, no bundler, no framework dependency. This enables rapid deployment via copy-and-upload, WordPress REST API injection, and Netlify/Vercel static hosting with zero build configuration. An agency rebuild that introduces React would add significant complexity the current system deliberately avoids.

**2. WordPress Plugin as All-in-One Layer**
A custom PHP plugin (`purebrain-security-plugin.php`, currently v6.1+) handles security headers, CSP enforcement, server-side proxy for all secret API calls, IndexNow pinging, UTM persistence, and user enumeration blocking. All credentials (PayPal, Brevo, VPS address) are hidden behind this plugin's PHP proxy endpoints. No API keys are exposed in client-side JavaScript.

**3. tmux Bridge Pattern**
The Telegram integration uses a Python bridge process that monitors an outbox file and injects received messages into a live tmux session. This is operational infrastructure — not customer-facing — but it underpins the entire AI-to-human communication channel. An agency building a replacement must understand this pattern.

**4. Birth Pipeline: 23-Step E2E Container Provisioning**
When a customer purchases PureBrain, they get a dedicated isolated container provisioned on the Witness VPS (104.248.239.98). The provisioning flow is 23 steps and can take up to 145 seconds. The proxy at api.purebrain.ai exists specifically to solve the HTTPS/HTTP mixed-content problem and CORS gap between the portal (served over HTTPS) and the Witness VPS (internal HTTP). This is one of the most complex subsystems in the platform.

**5. Dual WordPress Publish Pattern**
Every blog post publishes simultaneously to purebrain.ai and jareddsanborn.com via REST API. Both sites use different WordPress credentials and different page templates. This requires the publishing pipeline to handle two separate authenticated REST sequences per post.

**6. JSONL Log Architecture**
All server-side events (conversations, payments, email sends, pay-test completions) are written to append-only JSONL files on the VPS. There is no database. This keeps the infrastructure simple and query-friendly for AI analysis. An agency rebuild adding a database would need to account for the existing JSONL data migration.

## Total Requirement Count

| Category | Code | Count | Description |
|----------|------|-------|-------------|
| Website + Plugin + SEO | FR-WEB | 094 | WordPress frontend, custom plugin, SEO |
| Chatbox + PayPal + Security | FR-CHAT | 045 | v1–v4.7 chatbox, payment flow, XSS prevention |
| 3D / WebGL | FR-3D | 033 | GLSL avatar, Three.js portal, canvas hub |
| Backend Services | FR-BACKEND | 085 | Log server, Telegram, Drive, Gmail, BOOP, Dashboard |
| Customer Portal | FR-PORTAL | 041 | Witness architecture, containers, auth |
| Email System | FR-EMAIL | 041 | Brevo templates, automations, delivery |
| Analytics + Structured Data | FR-ANALYTICS | 032 | GA4, JSON-LD, IndexNow, UTM |
| Security (Non-Functional) | NFR-SEC | 052 | Headers, XSS, API keys, proxy, data privacy |
| Performance (Non-Functional) | NFR-PERF | 009 | Load time, scroll, animation performance |
| Scalability (Non-Functional) | NFR-SCALE | 007 | Horizontal scaling, JSONL limits, rate limits |
| **TOTAL** | | **~439** | |

## Estimated Complexity for Agency Quoting

This system was built by an AI engineering team (Aether) over 13 days at a total infrastructure cost of approximately $1,215. However, the development effort in human-hours equivalent is substantially larger.

**Complexity indicators for quoting:**
- 6 distinct hosting environments (GoDaddy, DigitalOcean x2, Google Cloud, Netlify, Vercel)
- 3 separately deployed frontend applications (portal, hub, dashboard)
- Custom PHP WordPress plugin (v6.1+, ~800 lines)
- Flask API server with 7 endpoints, background threading, rate limiting
- Real-time container provisioning pipeline (23-step E2E)
- 21 Brevo email templates with conditional personalization
- 5 marketing automation workflows
- 20+ blog posts requiring migration
- 8 comparison pages
- 2 lead magnets
- 4 interactive tools (assessment, calculator, migration wizard, portal)
- 3D WebGL portal with Three.js neural network background

**Suggested agency quote line items appear in Part IV (Agency Instructions).**

---

# MASTER TABLE OF CONTENTS

---

## Document Structure

This master SRS consolidates three source documents into a single agency-ready reference. All content is included inline — there are no external references required to understand this specification.

---

## Cover Page and Front Matter
- Document title, version, contact
- Document status

## Executive Summary
- What PureBrain.ai is
- System scope (6 service layers, 4 integrations, content subsystems)
- Key architectural decisions (5 non-obvious choices)
- Total requirement count by category (~439 requirements)
- Estimated complexity for agency quoting

---

## PART I: System Architecture and Technical Specification

### Section 1: System Architecture Overview
- 1.1 High-Level Architecture (ASCII diagram)
- 1.2 Service Inventory
  - 1.2.1 purebrain.ai (WordPress Frontend)
  - 1.2.2 api.purebrain.ai (Log / Proxy Server)
  - 1.2.3 app.purebrain.ai (Portal Frontend)
  - 1.2.4 PureBrain Hub (Vercel)
  - 1.2.5 Team Dashboard (Netlify)
  - 1.2.6 Witness VPS (Birth / Provisioning API)
  - 1.2.7 Third-Party Services
- 1.3 Service Communication Map

### Section 2: API Specifications
- 2.1 Log Server API (api.purebrain.ai)
  - POST /api/log-conversation
  - POST /api/verify-payment
  - POST /api/log-pay-test
  - GET /api/health
  - GET /api/stats
  - POST /api/paypal-webhook
- 2.2 Witness Birth Pipeline Proxy Endpoints
  - POST /api/proxy/birth/start
  - POST /api/proxy/birth/code
  - GET /api/proxy/birth/portal-status/{container}
- 2.3 Witness Portal API (upstream, 104.248.239.98:8099)
- 2.4 WordPress REST API (purebrain.ai)
  - Pages CRUD
  - Elementor Data Manipulation
  - Media Upload
  - Custom Plugin Endpoints
- 2.5 Brevo API
  - Contact Management
  - Brevo Contact List Reference
  - Transactional Email
  - Brevo Email Template Reference
- 2.6 PayPal API
  - Authentication
  - Order Verification
  - Webhook Signature Verification
  - PayPal Subscription Product Reference
- 2.7 Migration Portal Backend API (FastAPI)

### Section 3: Data Flow Diagrams
- 3.1 Customer Journey: Visit → Assessment → Chatbox → Payment → Birth → Portal
- 3.2 Blog Publishing Flow: Draft → Banner → Dual-Publish → Newsletter → Social
- 3.3 Email Automation: Trigger → Template → Delivery → Tracking

### Section 4: Deployment Architecture
- 4.1 WordPress Hosting (purebrain.ai)
- 4.2 Cloudflare Configuration
- 4.3 DigitalOcean VPS (Log Server / API Server)
- 4.4 Vercel Deployment (PureBrain Hub)
- 4.5 Netlify Deployments
- 4.6 Security Architecture Summary

### Section 5: Infrastructure Inventory
- 5.1 Servers
- 5.2 Static Hosting
- 5.3 Third-Party SaaS
- 5.4 Key Source File Paths

---

## PART II: Content, UX, and Branding Specification

### Section 1: Brand Guidelines
- 1.1 Color System (5-token system, extended tokens, hover states)
- 1.2 Typography (font stack, heading hierarchy, reading width rule)
- 1.3 Design Language: Dark Theme and Glass Morphism
- 1.4 Logo and Wordmark Rules (PUREBRAIN color split, hexagon icon)
- 1.5 Component and Iconography Standards (CTAs, cards, progress indicators)

### Section 2: Content Requirements
- 2.1 Blog System (cadence, dual-publish, slug conventions, template)
- 2.2 Blog Post Package Specification (9-file package, internal structure, FAQ spec, transparency section)
- 2.3 Existing Published Content Inventory (20 posts, content arc map)
- 2.4 Comparison Pages (8 pages, structure, design requirements)
- 2.5 Lead Magnets (AI Partnership Audit PDF, AI Adoption Assessment interactive)
- 2.6 Original Proprietary Concepts (Context Tax, Pilot Purgatory, The Awakening, Neural Feed, etc.)

### Section 3: UX Flow Requirements
- 3.1 Homepage Overview (8 sections in scroll order)
- 3.2 Assessment Flow (6-question flow, results logic, error states, data capture)
- 3.3 Chatbox and Subscription Flow (6 phases, naming ceremony, post-payment onboarding)
- 3.4 Blog Reader Journey (entry points, on-post journey, conversion options)
- 3.5 Migration Portal Wizard Flow (4-step wizard, Brevo integration)
- 3.6 AI Tool Stack Calculator Flow (5-step calculator, design requirements)
- 3.7 Competitor Comparison Page Journey (10-step journey, conversion options)
- 3.8 Portal Login Flow (glass morphism login, magic link flow)

### Section 4: Email Requirements
- 4.1 Email Template System (infrastructure, sending domain, list reference)
- 4.2 Template Design Standards (technical requirements, visual design, voice standards)
- 4.3 Template Inventory — 21 Templates
  - Group 1: Neural Feed Welcome Sequence (7 templates, WS-1 through WS-7)
  - Group 2: Post-Purchase Welcome (2 templates, TP-1 and TP-2)
  - Group 3: AI Partnership Audit Nurture (4 templates, AN-1 through AN-4)
  - Group 4: Pricing Intent (2 templates, PI-1 and PI-2)
  - Group 5: Re-engagement (3 templates, RE-1 through RE-3)
  - Group 6: Migration Tool-Specific (3 templates + 5-email series each)
- 4.4 Automation Workflow Specifications (5 workflows)

### Section 5: Social Media Requirements
- 5.1 Bluesky Presence (thread distribution, daily engagement protocol)
- 5.2 LinkedIn Content (Neural Feed newsletter, LinkedIn feed posts)

### Section 6: SEO / AEO / GEO Requirements
- 6.1 Meta and Structured Data (Yoast, FAQPage JSON-LD, Article JSON-LD)
- 6.2 Open Graph and Social Sharing (OG image strategy, share buttons, cache management)
- 6.3 Indexing and Crawler Access (IndexNow, robots.txt, crawler requirements)
- 6.4 Internal Linking (mesh architecture, topic clusters, anchor text rules)
- 6.5 AEO Content Standards 2026 (entity content, paragraph self-sufficiency, comparison tables)

---

## PART III: Requirements Traceability Matrix
- RTM Table: Requirement Category → Document Section
- Summary count per category
- Cross-reference index

## PART IV: Appendices
- Appendix A: Complete Page Inventory
- Appendix B: API Endpoint Quick Reference
- Appendix C: Environment Variable Reference
- Appendix D: Glossary

## Agency Instructions
- Suggested quote line items
- Build approach recommendations
- Context note on original build cost

---

---

# PART I: SYSTEM ARCHITECTURE AND TECHNICAL SPECIFICATION

*Source: SRS-System-Architecture-API-Specification.md — Prepared by Aether Engineering Team, 2026-02-26*

---

---

## Table of Contents

1. System Architecture Overview
2. API Specifications
3. Data Flow Diagrams
4. Deployment Architecture
5. Infrastructure Inventory

---

---

# SECTION 1: SYSTEM ARCHITECTURE OVERVIEW

## 1.1 High-Level Architecture

The PureBrain.ai platform is a distributed system composed of six primary service layers and four third-party integrations. The architecture follows a hub-and-spoke pattern with the Log/API Server (`api.purebrain.ai`) acting as the central backend hub for all authenticated service calls.

```
                        ┌─────────────────────────────────────────┐
                        │            CLIENTS (browsers)            │
                        └────────────┬────────────────────────────┘
                                     │ HTTPS
                   ┌─────────────────┼──────────────────────┐
                   │                 │                        │
          ┌────────▼──────┐ ┌────────▼──────┐   ┌───────────▼──────────┐
          │ purebrain.ai  │ │ app.purebrain │   │  purebrain-hub       │
          │ (WordPress)   │ │    .ai        │   │  .vercel.app         │
          │ GoDaddy host  │ │ (Netlify)     │   │  (Vercel)            │
          └───────┬───────┘ └───────┬───────┘   └───────────┬──────────┘
                  │                 │                         │
                  │ WP REST API     │ fetch()                 │ fetch()
                  │ Elementor       │                         │
                  └────────┬────────┘─────────────────────────┘
                           │
                           │ HTTPS (all calls from WordPress plugin
                           │ routed server-side to protect API keys)
                           │
              ┌────────────▼─────────────────┐
              │       api.purebrain.ai        │
              │    Flask/Python Log Server    │
              │    VPS: 89.167.19.20:8443     │  ← HTTPS (self-signed cert)
              │    Cloudflare Tunnel →        │
              │    public HTTPS exposure      │
              └──────────┬───────────────────┘
                         │
          ┌──────────────┼─────────────────────┐
          │              │                      │
  ┌───────▼──────┐ ┌─────▼──────┐   ┌──────────▼─────────────┐
  │ Witness VPS  │ │  A-C-Gee   │   │  Third-Party Services  │
  │ 104.248.239  │ │  VPS       │   │  - Brevo (email)       │
  │ .98:8099     │ │  5.161.90  │   │  - PayPal (payments)   │
  │ (birth API)  │ │  .32:3001  │   │  - Telegram (ops)      │
  └──────────────┘ └────────────┘   │  - Google Drive        │
                                    └────────────────────────┘

          ┌────────────────────────────────────────────┐
          │        pure-tech-dashboard.netlify.app      │
          │        Team Dashboard (Netlify)             │
          │        Supabase PostgreSQL backend          │
          └────────────────────────────────────────────┘
```

---

## 1.2 Service Inventory

### 1.2.1 purebrain.ai (WordPress Frontend)

| Property | Value |
|----------|-------|
| Platform | WordPress (latest stable) |
| Hosting | GoDaddy Managed WordPress |
| DNS | Cloudflare (proxied) |
| SSL | Cloudflare SSL (full strict) |
| Page Builder | Elementor Pro |
| Custom Plugin | `purebrain-security-plugin.php` (custom, v6.1+) |

**Function**: Primary marketing site and content delivery. All customer-facing pages: homepage, blog, assessment tool, chatbox, pay-test purchase flow, comparison pages, migration portal pages, AI tool calculator, partner program landing page.

**WordPress Plugin Responsibilities**:
- HSTS header injection (`max-age=31536000; includeSubDomains; preload`)
- Content Security Policy (enforced mode)
- Server-side proxy for log server calls (hides VPS IP from client JS)
- Server-side proxy for PayPal verification (hides PayPal credentials)
- Block user enumeration via REST (`/wp/v2/users`)
- Block `?author=` enumeration attacks
- IndexNow pinging on publish events
- UTM parameter persistence

**WordPress REST API Base URL**: `https://purebrain.ai/wp-json/wp/v2/`
**Custom Plugin REST Namespace**: `https://purebrain.ai/wp-json/purebrain/v1/`

---

### 1.2.2 api.purebrain.ai (Log / Proxy Server)

| Property | Value |
|----------|-------|
| VPS IP | 89.167.19.20 |
| Port | 8443 (HTTPS) |
| Framework | Python 3.x / Flask |
| SSL | Self-signed certificate (RSA 2048-bit, SAN: 89.167.19.20) |
| Public Exposure | Cloudflare Tunnel (domain: api.purebrain.ai) |
| Process Manager | systemd (`purebrain-log-server.service`) |
| CORS Origin Whitelist | `https://purebrain.ai`, `https://www.purebrain.ai`, `https://jareddsanborn.com`, `https://www.jareddsanborn.com` |
| Max Request Body | 1 MB |

**Function**: Central backend API. Handles conversation logging, payment verification, Witness birth pipeline proxying, Brevo email automation, and PayPal webhook reception. All calls that require secrets (API keys, credentials) pass through this server so no credentials are exposed in client-side JavaScript.

**Persistent Background Services** (run inside same process):
- `neural_feed_welcome_sequence.py` — welcome email scheduler for blog subscribers
- `rss_to_email.py` — RSS-to-email daemon for automated blog distribution

---

### 1.2.3 app.purebrain.ai (Portal Frontend)

| Property | Value |
|----------|-------|
| Hosting Platform | Google Cloud |
| Custom Domain | `app.purebrain.ai` |
| DNS | Per Google Cloud configuration |
| Technology | Single-file self-contained HTML (~895 KB) |

**Function**: Customer portal application after purchase. Three.js 3D neural network background, glassmorphism login card, post-purchase dashboard. Communicates with Witness VPS to provision and track AI partner containers.

**Source File**: `exports/purebrain-frontend-3d.html`

---

### 1.2.4 PureBrain Hub (Vercel)

| Property | Value |
|----------|-------|
| Hosting Platform | Vercel |
| URL | `https://purebrain-hub.vercel.app` |
| Technology | Single-file HTML (vanilla JS, Canvas 2D animations) |
| Auth | Token-based (`team2025`, `safety2025`, `quality2025`, `demo`) |

**Function**: Internal team command center. Features: team wins board, file uploads, post feed, tag-based filtering, leaderboard, Google Drive sync status, NeuralCanvas animated login background. Used by Pure Technology internal team.

**Source File**: `exports/purebrain-hub-v2.html` / `tools/purebrain-hub-static/index.html`

---

### 1.2.5 Team Dashboard (Netlify)

| Property | Value |
|----------|-------|
| Hosting Platform | Netlify |
| Netlify Site ID | `d2556d0a-5333-47ca-a8d6-8add4141f090` |
| URL | `https://pure-tech-dashboard.netlify.app` |
| Technology | Single-file HTML (vanilla JS) |
| Backend | Supabase PostgreSQL (optional; falls back to localStorage) |

**Function**: Task management dashboard for Pure Technology team. Features: task CRUD, assignee management, priority/status/deadline tracking, real-time sync via Supabase. Offline-capable (localStorage fallback).

**Source File**: `exports/team-dashboard/dist/index.html`

---

### 1.2.6 Witness VPS (Birth / Provisioning API)

| Property | Value |
|----------|-------|
| VPS IP | 104.248.239.98 |
| Port | 8099 (HTTP, internal only) |
| Public Access | Via proxy at api.purebrain.ai |

**Function**: Provisions isolated AI partner containers ("births") for newly purchased PureBrain customers. Not directly accessible from the browser — all calls pass through the `api.purebrain.ai` proxy to resolve CORS and mixed-content issues.

---

### 1.2.7 Third-Party Services

| Service | Purpose | Integration Method |
|---------|---------|--------------------|
| **Brevo** | Transactional email + marketing automation | REST API v3 via Python (`requests`) |
| **PayPal** | Payment capture + webhook events | REST API v2 (OAuth2) via Python (`urllib`) |
| **Telegram Bot API** | Operational notifications to Jared | REST API via `urllib` |
| **Google Drive** | File storage for all deliverables and training data | `gdrive_manager.py` tool (service account) |
| **A-C-Gee VPS** | Shared conversation database (cross-CIV integration) | HTTP POST to `5.161.90.32:3001/api/landing-chat` |
| **Cloudflare** | DNS, CDN, SSL, DDoS protection | DNS provider for `purebrain.ai` |

---

## 1.3 Service Communication Map

```
purebrain.ai (WordPress)
├── Calls wp-json/purebrain/v1/log-conversation-fallback (own plugin proxy)
├── Plugin calls → https://89.167.19.20:8443/api/log-conversation
├── Plugin calls → https://89.167.19.20:8443/api/verify-payment
└── Blog pages embed chatbox JS (calls api.purebrain.ai directly)

api.purebrain.ai (89.167.19.20:8443)
├── Writes → /logs/purebrain_web_conversations.jsonl
├── Writes → /logs/purebrain_pay_test.jsonl
├── Writes → /logs/purebrain_payments.jsonl
├── Writes → /logs/purebrain_emails.jsonl
├── Calls → Brevo API (transactional email)
├── Calls → PayPal API (order verification, OAuth2)
├── Calls → Telegram Bot API (operational notifications)
├── Proxies → Witness VPS 104.248.239.98:8099 (birth pipeline)
├── Forwards → A-C-Gee 5.161.90.32:3001 (cross-CIV logging)
└── Publishes → AICIV comms hub (git-based, hub_cli.py)

app.purebrain.ai (Google Cloud)
├── Calls → api.purebrain.ai/api/proxy/birth/start
├── Calls → api.purebrain.ai/api/proxy/birth/code
└── Polls → api.purebrain.ai/api/proxy/birth/portal-status/{container}

purebrain-hub.vercel.app (Vercel)
└── Standalone (localStorage, no backend calls in current v2)

pure-tech-dashboard.netlify.app (Netlify)
└── Calls → Supabase REST API (PostgreSQL via HTTPS)
```

---

---

# SECTION 2: API SPECIFICATIONS

## 2.1 Log Server API (api.purebrain.ai)

**Base URL**: `https://api.purebrain.ai`
**Protocol**: HTTPS (TLS 1.2+)
**Auth**: None for public endpoints (CORS whitelist enforced)
**Content-Type**: `application/json` required on all POST requests
**Max Body Size**: 1 MB

---

### POST /api/log-conversation

**Purpose**: Record a chatbox conversation session to the server JSONL log and forward it asynchronously to A-C-Gee's shared database.

**CORS**: Allowed from purebrain.ai, jareddsanborn.com

**Request Body**:
```json
{
  "session_id": "string (optional; UUID auto-generated if absent)",
  "messages": [
    {"role": "user", "content": "string"},
    {"role": "assistant", "content": "string"}
  ],
  "user_agent": "string (optional)",
  "page_url": "string (optional)",
  "referrer": "string (optional)",
  "aiName": "string (optional — AI partner's chosen name)",
  "userName": "string (optional)",
  "userTier": "string (optional)",
  "referralCode": "string (optional)",
  "conversationId": "string (optional)",
  "brainId": "string (optional)"
}
```

**Note**: Accepts both `messages` and `conversationHistory` as the message array key for backward compatibility.

**Response 200**:
```json
{
  "success": true,
  "session_id": "pb-{uuid}",
  "timestamp": "2026-02-26T12:00:00.000000+00:00"
}
```

**Response 400**: `{"error": "Content-Type must be application/json"}`
**Response 400**: `{"error": "Missing required field: messages or conversationHistory"}`
**Response 500**: `{"error": "Failed to write log"}`

**Side Effects**:
- Appends JSON line to `/logs/purebrain_web_conversations.jsonl`
- Spawns background thread: forward to A-C-Gee `5.161.90.32:3001/api/landing-chat` (3 retries on 500)
- Spawns background thread: publish to AICIV comms hub `operations` room

---

### POST /api/verify-payment

**Purpose**: Server-side PayPal order verification for the AI Website Execution service (page 826). Prevents client-side payment spoofing by calling PayPal API directly with stored credentials.

**CORS**: Allowed from purebrain.ai

**Request Body**:
```json
{
  "order_id": "string (PayPal order ID, required)",
  "tier": "critical|complete (required)"
}
```

**Expected Amounts**:
| Tier | Amount |
|------|--------|
| `critical` | $197.00 USD |
| `complete` | $497.00 USD |

**Response 200**:
```json
{
  "verified": true,
  "status": "COMPLETED",
  "amount": "197.00",
  "payer_email": "buyer@example.com",
  "payer_name": "Jane Smith",
  "order_id": "PAYPAL-ORDER-ID-ABC",
  "server_timestamp": "2026-02-26T12:00:00.000000+00:00"
}
```

**Response 200 (failure case)**:
```json
{
  "verified": false,
  "status": "PENDING",
  "amount": "",
  "payer_email": "",
  "payer_name": "",
  "order_id": "...",
  "server_timestamp": "...",
  "error": "Could not obtain PayPal access token"
}
```

**Response 400**: `{"error": "Missing required field: order_id"}`

**Side Effects (on verified=true)**:
- Appends entry to `/logs/purebrain_payments.jsonl`
- Spawns background thread: Telegram notification to Jared
- Spawns background thread: Brevo confirmation email to buyer (Template ID 11)

**PayPal API Flow**:
1. POST `https://api-m.paypal.com/v1/oauth2/token` → access token
2. GET `https://api-m.paypal.com/v2/checkout/orders/{order_id}` → order details
3. Validate `status == "COMPLETED"` and `captures[0].amount.value == expected_amount`

---

### POST /api/log-pay-test

**Purpose**: Record the complete post-payment onboarding flow data after a customer finishes the PureBrain purchase questionnaire. Triggers the post-purchase email sequence when `flowCompleted=true`.

**CORS**: Allowed from purebrain.ai

**Request Body**:
```json
{
  "tier": "Awakened|Bonded|Partnered|Unified",
  "orderId": "string (PayPal order ID)",
  "aiName": "string (AI partner name chosen by user)",
  "name": "string (customer full name)",
  "email": "string (customer email)",
  "company": "string (optional)",
  "role": "string (optional)",
  "primaryGoal": "string (optional)",
  "telegramBotToken": "string (optional — if Telegram setup completed)",
  "claudeMaxStatus": "connected|skipped|pending",
  "flowCompleted": "boolean"
}
```

**Response 200**:
```json
{
  "success": true,
  "logged": true,
  "server_timestamp": "2026-02-26T12:00:00.000000+00:00"
}
```

**Side Effects**:
- Appends entry to `/logs/purebrain_pay_test.jsonl`
- Spawns background thread: Telegram notification to Jared (always)
- If `flowCompleted=true` AND `email` is present: spawns background thread to trigger post-purchase email sequence:
  - Upsert Brevo contact (List 8: PureBrain Customers) with AI_NAME, TIER, COMPANY, ROLE, PRIMARY_GOAL attributes
  - Send Brevo Template 11 (Welcome: "Your AI partner is live") immediately
  - Schedule Brevo Template 12 (Setup Complete: "40 minutes in") via `threading.Timer` at 40-minute delay

---

### GET /api/health

**Purpose**: Health check endpoint. Used for monitoring and uptime verification.

**Auth**: None

**Response 200**:
```json
{
  "status": "ok",
  "ssl": true,
  "timestamp": "2026-02-26T12:00:00.000000+00:00"
}
```

---

### GET /api/stats

**Purpose**: Conversation log statistics.

**Auth**: None

**Response 200**:
```json
{
  "conversation_count": 142,
  "file_size_bytes": 524288,
  "log_file": "purebrain_web_conversations.jsonl",
  "timestamp": "2026-02-26T12:00:00.000000+00:00"
}
```

---

### POST /api/paypal-webhook

**Purpose**: Receive PayPal `PAYMENT.CAPTURE.COMPLETED` events. Signed by PayPal and verified via PayPal's webhook signature verification API.

**Auth**: PayPal webhook signature headers
- `PAYPAL-AUTH-ALGO`
- `PAYPAL-CERT-URL`
- `PAYPAL-TRANSMISSION-ID`
- `PAYPAL-TRANSMISSION-SIG`
- `PAYPAL-TRANSMISSION-TIME`

**Registration URL** (at PayPal Developer Dashboard): `https://api.purebrain.ai/api/paypal-webhook`
**Subscribed Events**: `PAYMENT.CAPTURE.COMPLETED`

**Request Body**: PayPal webhook event object (application/json)

**Response 200 (processed)**:
```json
{"status": "processed", "capture_id": "CAPTURE-ID-XYZ"}
```

**Response 200 (ignored)**:
```json
{"status": "ignored", "reason": "event_type=PAYMENT.SUBSCRIPTION.ACTIVATED"}
```

**Response 400**: `{"status": "ignored", "reason": "invalid json"}`

**Side Effects**:
- Appends webhook entry to `/logs/purebrain_payments.jsonl` (includes gross, net, fee, inferred tier)
- Spawns background thread: Telegram notification to Jared

---

## 2.2 Witness Birth Pipeline Proxy Endpoints

These three endpoints are proxy pass-throughs on `api.purebrain.ai` that forward to the Witness VPS at `http://104.248.239.98:8099`. The upstream IP is hardcoded server-side; it is never accepted from request input.

**Rationale for proxy**: The Witness VPS serves plain HTTP. The PureBrain portal is served over HTTPS. Browsers block "mixed content" (HTTPS page calling HTTP resource). Additionally, the Witness VPS does not have CORS headers configured for the purebrain.ai origin. The proxy solves both problems.

---

### POST /api/proxy/birth/start
**Alias**: POST /api/birth/start

**Purpose**: Provision a new AI partner container for a purchasing customer.

**Rate Limit**: 5 calls per minute per client IP (sliding window, per-IP, prevents container pool exhaustion)

**Request Body** (optional):
```json
{}
```
or
```json
{"container": "specific-container-name"}
```

**Body Validation**: If body is present, must be valid JSON. Max body size: 64 KB.

**Timeout**: 120 seconds (provisioning can take up to 145 seconds in worst case)
**Connect Timeout**: 10 seconds

**Successful Response** (pass-through from Witness):
```json
{
  "status": "url_ready",
  "oauth_url": "https://oauth.purebrain.ai/...",
  "container": "aiciv-07",
  "auto_allocated": true
}
```

**Error Responses**:
| Code | Body |
|------|------|
| 429 | `{"error": "Too many requests", "details": "Maximum 5 birth starts per minute"}` |
| 400 | `{"error": "Invalid JSON body"}` |
| 413 | `{"error": "Request body too large"}` |
| 503 | `{"error": "Birth service unavailable", "details": "Could not connect to birth service"}` |
| 504 | `{"error": "Birth service timeout", "details": "Upstream did not respond in time"}` |
| 502 | `{"error": "Birth service error", "details": "Unexpected proxy error"}` |

---

### POST /api/proxy/birth/code
**Alias**: POST /api/birth/code

**Purpose**: Submit an authentication code during the birth/provisioning OAuth flow.

**Rate Limit**: 10 calls per minute per client IP

**Request Body**: Passed through unchanged (must be valid JSON)

**Timeout**: 30 seconds

**Response**: Witness response pass-through

---

### GET /api/proxy/birth/portal-status/{container}

**Purpose**: Poll the birth status of a specific container. Returns when the portal is ready.

**Rate Limit**: 60 calls per minute per client IP (supports 1/second polling)

**URL Parameter**:
- `container`: Container name. Validated against regex `^[a-zA-Z0-9_-]{1,50}$`. Returns 400 if invalid.

**Timeout**: 15 seconds

**Successful Response** (pass-through from Witness):
```json
{
  "ready": false,
  "portal_url": null
}
```
or when ready:
```json
{
  "ready": true,
  "portal_url": "https://portal.purebrain.ai/..."
}
```

**Error Responses**:
| Code | Body |
|------|------|
| 400 | `{"error": "Invalid container name"}` |
| 503 | `{"error": "Birth service unavailable", ...}` |
| 504 | `{"error": "Birth service timeout", ...}` |

---

## 2.3 Witness Portal API (104.248.239.98:8099)

These are the upstream Witness endpoints. Client code should never call these directly — use the proxy endpoints at `api.purebrain.ai` described in section 2.2.

**Note**: This is the A-C-Gee / Witness collective's internal API. Full spec maintained by that team.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/birth/start` | Begin container provisioning (accepts empty `{}` or `{"container": "name"}`) |
| POST | `/api/birth/code` | Submit OAuth code during provisioning |
| GET | `/api/birth/portal-status/{container}` | Poll container readiness |
| GET | `/api/health` | Witness health check |
| GET | `/portal-status` | Alias for portal-status |
| POST | `/evolution` | Signal container upgrade/evolution |
| POST | `/auth` | Magic link authentication initiation |

---

## 2.4 WordPress REST API (purebrain.ai)

**Base URL**: `https://purebrain.ai/wp-json/wp/v2/`
**Auth**: HTTP Basic (Base64-encoded `username:app_password`)
- purebrain.ai: username `Aether`, app_password in `.env` as `PUREBRAIN_WP_APP_PASSWORD`
- jareddsanborn.com: username `jared`, app_password in `.env` as `WORDPRESS_APP_PASSWORD`

### Pages CRUD

**Get page (with edit context)**:
```
GET /wp/v2/pages/{id}?context=edit
Authorization: Basic {base64}
```

**Create page**:
```
POST /wp/v2/pages
Authorization: Basic {base64}
Content-Type: application/json

{
  "title": "Page Title",
  "content": "<!-- wp:html -->\n<div>...</div>\n<!-- /wp:html -->",
  "status": "publish|draft",
  "template": ""  // "" = default theme template (for blog posts)
                  // "elementor_canvas" for standalone Elementor pages (NON-blog)
}
```

**Update page**:
```
POST /wp/v2/pages/{id}
Authorization: Basic {base64}
Content-Type: application/json

{"content": "...", "meta": {"_elementor_data": "serialized_json_string"}}
```

**Delete page (move to trash)**:
```
DELETE /wp/v2/pages/{id}
Authorization: Basic {base64}
```

### Elementor Data Manipulation

**CRITICAL**: All Elementor widget content is stored as serialized JSON in the `_elementor_data` post meta field. A full double-serialization pattern is used.

**Read Elementor data**:
```python
resp = requests.get(f"{base_url}/wp/v2/pages/{id}?context=edit", auth=auth)
elementor_data = json.loads(resp.json()['meta']['_elementor_data'])
html_content = elementor_data[0]['elements'][0]['settings']['html']
```

**Write Elementor data**:
```python
requests.post(
    f"{base_url}/wp/v2/pages/{id}",
    auth=auth,
    json={"meta": {"_elementor_data": json.dumps(elementor_data)}}
)
```

**Clear Elementor cache after update**:
```
DELETE /wp-json/elementor/v1/cache
Authorization: Basic {base64}
```

**CRITICAL NOTE**: REST API updates to `_elementor_data` do NOT trigger re-rendering. For pages where Elementor fails to re-render, the solution is to delete the page and recreate it with a fresh ID.

### Media Upload

```
POST /wp/v2/media
Authorization: Basic {base64}
Content-Type: image/png
Content-Disposition: attachment; filename="banner.png"

[binary image data]
```

**Response**: Media object with `id`, `source_url`, `link`

### Custom Plugin Endpoints (purebrain.ai)

**Server-side proxy for logging** (hides VPS IP from client JS):
```
POST /wp-json/purebrain/v1/log-conversation
POST /wp-json/purebrain/v1/log-conversation-fallback
```

**Server-side proxy for payment verification** (hides PayPal credentials from client JS):
```
POST /wp-json/purebrain/v1/verify-payment
```

---

## 2.5 Brevo API

**Base URL**: `https://api.brevo.com/v3`
**Auth**: `api-key: {BREVO_API_KEY}` header

### Contact Management

**Upsert Contact**:
```
POST /contacts
Content-Type: application/json
api-key: {key}

{
  "email": "customer@example.com",
  "attributes": {
    "FIRSTNAME": "Jane",
    "LASTNAME": "Smith",
    "AI_NAME": "Keen",
    "TIER": "Awakened",
    "COMPANY": "Acme Corp",
    "ROLE": "CEO",
    "PRIMARY_GOAL": "save 10hrs/week"
  },
  "listIds": [8],
  "updateEnabled": true
}
```

**Update Contact Attributes** (without changing lists):
```
PUT /contacts/{email_urlencoded}
Content-Type: application/json
api-key: {key}

{
  "attributes": {
    "MIGRATION_STATUS": "complete",
    "MIGRATION_PROFILE": "{compact_json}"
  }
}
```

**Add to List** (triggers Brevo automations):
```
POST /contacts/lists/{listId}/contacts/add
Content-Type: application/json
api-key: {key}

{"emails": ["customer@example.com"]}
```

### Brevo Contact List Reference

| List ID | Name | Purpose |
|---------|------|---------|
| 3 | Neural Feed | Blog newsletter subscribers |
| 4 | Enterprise Leads | Enterprise inquiry leads |
| 8 | PureBrain Customers | Post-purchase customers |
| 11 | PureBrain Migration Leads | General migration intent |
| 12 | PureBrain Migration — ChatGPT | ChatGPT drip trigger |
| 13 | PureBrain Migration — Claude | Claude drip trigger |
| 14 | PureBrain Migration — Gemini | Gemini drip trigger |
| 15 | PureBrain Migration — Perplexity | Perplexity drip trigger |
| 16 | PureBrain Migration — Midjourney | Midjourney drip trigger |
| 17 | PureBrain Migration — Copilot | Copilot drip trigger |
| 18 | PureBrain Migration — Other | Fallback drip trigger |

### Transactional Email

```
POST /smtp/email
Content-Type: application/json
api-key: {key}

{
  "to": [{"email": "customer@example.com", "name": "Jane Smith"}],
  "templateId": 11,
  "params": {
    "FIRSTNAME": "Jane",
    "AI_NAME": "Keen",
    "TIER": "Awakened",
    "PRIMARY_GOAL": "save 10hrs/week"
  }
}
```

**Response**: HTTP 201 with `{"messageId": "..."}`

**Template variable syntax in Brevo email bodies**: `{{params.VARNAME}}`

### Brevo Email Template Reference

| Template ID | Name | Trigger |
|-------------|------|---------|
| 1–7 | Neural Feed welcome sequence | Added to List 3 (blog signup) |
| 11 | PureBrain Welcome — Your AI partner is live | `POST /api/log-pay-test` with `flowCompleted=true` |
| 12 | PureBrain Setup Complete — 40 minutes in | 40-minute timer after Template 11 |
| Various | Migration drip sequences | Added to Lists 12–18 (manual Brevo automation) |

**NOTE**: Brevo has no REST API for automation workflow creation. Drip sequences require manual setup in Brevo UI (Automations → "Contact added to list" trigger).

---

## 2.6 PayPal API

**Base URL (Live)**: `https://api-m.paypal.com`
**Auth**: OAuth2 client credentials flow

### Authentication

```
POST /v1/oauth2/token
Authorization: Basic {base64(client_id:secret)}
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
```

**Response**: `{"access_token": "...", "expires_in": 32400}`

### Order Verification

```
GET /v2/checkout/orders/{order_id}
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response**: Full order object. Verification checks:
1. `order.status == "COMPLETED"`
2. `order.purchase_units[0].payments.captures[0].amount.value == expected_amount`

### Webhook Signature Verification

```
POST /v1/notifications/verify-webhook-signature
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "auth_algo": "{PAYPAL-AUTH-ALGO header}",
  "cert_url": "{PAYPAL-CERT-URL header}",
  "transmission_id": "{PAYPAL-TRANSMISSION-ID header}",
  "transmission_sig": "{PAYPAL-TRANSMISSION-SIG header}",
  "transmission_time": "{PAYPAL-TRANSMISSION-TIME header}",
  "webhook_id": "{PAYPAL_WEBHOOK_ID env var}",
  "webhook_event": {parsed_event_body}
}
```

**Response**: `{"verification_status": "SUCCESS"}`

### PayPal Subscription Product Reference

| Tier | Amount | Type |
|------|--------|------|
| Awakened | $79/month | Subscription |
| Bonded | $149/month | Subscription |
| Partnered | $499/month | Subscription |
| Unified | $999/month | Subscription |
| AI Website Execution — Critical | $197 | One-time |
| AI Website Execution — Complete | $497 | One-time |

---

## 2.7 Migration Portal Backend API (FastAPI)

**Location**: `tools/migration/migration_api.py`
**Runtime**: `uvicorn tools.migration.migration_api:app --port 8001`
**Auth**: HMAC `api-key` header using `hmac.compare_digest`

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/upload` | Upload ChatGPT or Claude export ZIP for parsing |
| GET | `/status/{job_id}` | Poll async parsing job status |
| GET | `/profile/{user_id}` | Retrieve completed user context profile |
| DELETE | `/delete/{user_id}` | GDPR delete — removes files, jobs, and profile |

**Supported Export Formats**:
- ChatGPT: ZIP containing `conversations.json` + `user.json` (OpenAI format)
- Claude: ZIP containing conversation export (Anthropic format, 3 known variants)
- Generic: CSV or JSON from any AI tool

**Output Profile Structure**:
```json
{
  "top_topics": ["marketing", "coding", "research"],
  "usage_style": "bullet-heavy",
  "expertise_level": "intermediate",
  "conversation_count": 847,
  "custom_instructions": "..."
}
```

---

---

# SECTION 3: DATA FLOW DIAGRAMS

## 3.1 Customer Journey: Visit → Assessment → Chatbox → Payment → Birth → Portal

```
STAGE 1: VISIT
─────────────────────────────────────────────────────────────────────────────
User visits purebrain.ai
    │
    ├── Cloudflare DNS resolves → GoDaddy WordPress host
    ├── Cloudflare CDN serves cached static assets
    ├── WordPress security plugin adds security headers (HSTS, CSP, X-Frame, etc.)
    └── Page HTML delivers chatbox JS bundle

STAGE 2: AI PARTNERSHIP ASSESSMENT
─────────────────────────────────────────────────────────────────────────────
User visits purebrain.ai/ai-adoption-assessment
    │
    ├── Self-contained assessment HTML widget loads (served via WordPress HTML widget)
    ├── User answers 6 scored questions
    ├── Score calculated client-side
    ├── Results page shown with matched CTA (based on score tier)
    └── Share button generates URL with score parameter

STAGE 3: CHATBOX CONVERSATION
─────────────────────────────────────────────────────────────────────────────
User engages chatbox on any purebrain.ai page
    │
    ├── Chatbox JS initialized with system prompt
    ├── User types message
    ├── Chatbox calls → WordPress plugin proxy → /wp-json/purebrain/v1/log-conversation
    │       └── Plugin forwards → POST https://89.167.19.20:8443/api/log-conversation
    ├── Message history sent to AI API (Claude or Cloudflare Workers AI proxy)
    ├── AI response displayed
    ├── End of session:
    │   ├── POST api.purebrain.ai/api/log-conversation (full history)
    │   ├── Background: forward to A-C-Gee 5.161.90.32:3001
    │   └── Background: publish to AICIV comms hub
    └── Chatbox captures AI partner name via regex (pre-purchase flow)

STAGE 4: PAYMENT
─────────────────────────────────────────────────────────────────────────────
User clicks "Get Started" / pricing CTA
    │
    ├── Pay-test page loads (WordPress page ID 439 or 468)
    ├── Pre-purchase chat flow runs (AI names itself, conversation)
    ├── User selects tier (Awakened $79 / Bonded $149 / Partnered $499 / Unified $999)
    ├── PayPal Smart Buttons rendered (client-side PayPal SDK)
    ├── User completes PayPal payment
    ├── PayPal fires CHECKOUT.ORDER.APPROVED event in browser
    ├── Client calls → POST api.purebrain.ai/api/verify-payment
    │       ├── Server calls PayPal OAuth token endpoint
    │       ├── Server calls PayPal order verification endpoint
    │       └── Returns {verified: true/false, amount, payer_email}
    ├── POST-PAYMENT FLOW LAUNCHES (fullscreen overlay):
    │   ├── Questionnaire: collect name, email, company, role, primaryGoal
    │   ├── Behind-the-curtain: Telegram setup instructions
    │   ├── Claude Max setup instructions
    │   └── AI partner presentation
    └── On flow:complete:
        ├── POST api.purebrain.ai/api/log-pay-test (full payTestData)
        ├── Background: Telegram notification to Jared
        ├── Background: Brevo contact upsert + Template 11 (immediate)
        ├── Background: Brevo Template 12 scheduled (40-min timer)
        └── User redirected → purebrain.ai/thank-you/

    SIMULTANEOUSLY — PayPal fires webhook:
        POST api.purebrain.ai/api/paypal-webhook
        ├── Signature verified via PayPal API
        ├── Event logged to purebrain_payments.jsonl
        └── Background: Telegram notification to Jared

STAGE 5: BIRTH (CONTAINER PROVISIONING)
─────────────────────────────────────────────────────────────────────────────
Customer accesses app.purebrain.ai
    │
    ├── Login page loads (Three.js neural network background + glassmorphism form)
    ├── Customer enters AI name + secret code
    ├── POST api.purebrain.ai/api/proxy/birth/start
    │       ├── Rate limit checked (5/min per IP)
    │       └── Proxied → POST http://104.248.239.98:8099/api/birth/start
    │           └── Witness provisions Docker container (up to 145s)
    │               Returns: {status: "url_ready", oauth_url, container}
    ├── POST api.purebrain.ai/api/proxy/birth/code (OAuth code submission)
    └── Poll GET api.purebrain.ai/api/proxy/birth/portal-status/{container}
            └── Returns: {ready: false} → {ready: true, portal_url: "..."}
                Customer browser redirects to portal_url

STAGE 6: PORTAL
─────────────────────────────────────────────────────────────────────────────
Customer accesses their provisioned portal URL
    │
    └── Isolated container serves personalized AI partner interface
```

---

## 3.2 Blog Publishing Flow: Draft → Banner → Dual-Publish → Newsletter → Social

```
1. CONTENT GENERATION
─────────────────────────────────────────────────────────────────────────────
content-specialist agent generates:
    ├── blog-post.md (full article, markdown)
    ├── linkedin-newsletter.md
    ├── linkedin-post.md
    └── bluesky-thread.md

2. BANNER GENERATION
─────────────────────────────────────────────────────────────────────────────
    ├── Method A: Gemini 3 Pro Image API (primary)
    │       POST to Gemini API with brand prompt
    │       Returns: PNG binary
    ├── Method B: Python matplotlib/PIL (fallback)
    └── Output: banner.png (1200x628px for OG image standard)

3. JARED REVIEW (MORNING DELIVERY)
─────────────────────────────────────────────────────────────────────────────
Files delivered via Telegram:
    ├── tg_send.sh --file blog-post.md "Today's blog"
    ├── tg_send.sh --photo banner.png "Today's banner"
    ├── tg_send.sh --file linkedin-newsletter.md "LinkedIn newsletter"
    └── tg_send.sh --file linkedin-post.md "LinkedIn post"

Jared reviews from phone and gives approval/feedback.

4. DUAL PUBLISH (after Jared approval)
─────────────────────────────────────────────────────────────────────────────
purebrain.ai publish:
    ├── POST /wp/v2/media (banner image upload)
    ├── POST /wp/v2/posts (create post, template="", wrapper: article.pb-blog-post)
    │       └── Content wrapped in <!-- wp:html --> block
    ├── Set featured image (returned media ID)
    ├── DELETE /wp-json/elementor/v1/cache (clear cache)
    └── Verify live at https://purebrain.ai/blog/{slug}/

jareddsanborn.com publish:
    ├── POST /wp/v2/media (same banner)
    ├── POST /wp/v2/posts (create post, template="page-template-blank.php")
    └── Verify live at https://jareddsanborn.com/blog/{slug}/

5. FILE ARCHIVE
─────────────────────────────────────────────────────────────────────────────
Google Drive filing (all files → Blog Posts folder subfolder):
    ├── Folder: "Blog Posts" (ID: 1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv)
    ├── Subfolder: "{post-slug}-{date}"
    └── Files: blog-post.md, banner.png, og.png, linkedin-*.md, bluesky-thread.md

6. NEWSLETTER DISPATCH
─────────────────────────────────────────────────────────────────────────────
Automated via RSS-to-Email daemon (runs inside log server process):
    ├── Polls purebrain.ai RSS feed for new posts
    ├── Detects new post
    └── Creates Brevo campaign → sends to List 3 (Neural Feed subscribers)

7. SOCIAL DISTRIBUTION
─────────────────────────────────────────────────────────────────────────────
    ├── Bluesky: bsky-manager agent posts thread (autonomous)
    └── LinkedIn: Jared posts manually (content from linkedin-post.md)
```

---

## 3.3 Email Automation: Trigger → Template → Delivery → Tracking

```
TRIGGER TYPE A: Blog Subscriber (Neural Feed Welcome Sequence)
─────────────────────────────────────────────────────────────────────────────
User submits newsletter form on purebrain.ai
    │
    ├── Form submits to Brevo embed form endpoint
    ├── Contact created in Brevo with FIRSTNAME, email
    ├── Contact added to List 3 (Neural Feed)
    └── Brevo automation triggers:
        ├── Immediately: Template 1 (Welcome to Neural Feed)
        ├── Day 2: Template 2
        ├── Day 4: Template 3
        ├── Day 7: Template 4
        ├── Day 10: Template 5
        ├── Day 14: Template 6
        └── Day 21: Template 7

All templates include:
    - Reply-To: jared@puretechnology.nyc
    - Branding: PUREBR(blue)AI(orange)N(blue)
    - PS section with personalized add-on content
    - Social share footer

TRIGGER TYPE B: Purchase (Post-Purchase Emails)
─────────────────────────────────────────────────────────────────────────────
Customer completes pay-test flow (flowCompleted=true)
    │
    POST api.purebrain.ai/api/log-pay-test
        │
        └── Background thread: _trigger_post_purchase_emails(data)
            │
            ├── Brevo upsert: POST /v3/contacts
            │       email, FIRSTNAME, LASTNAME, AI_NAME, TIER,
            │       COMPANY, ROLE, PRIMARY_GOAL
            │       listIds: [8]  (PureBrain Customers)
            │
            ├── Immediate: POST /v3/smtp/email
            │       templateId: 11
            │       params: FIRSTNAME, AI_NAME, TIER, PRIMARY_GOAL
            │       → "Your AI partner is live"
            │
            └── threading.Timer(2400s):
                    POST /v3/smtp/email
                    templateId: 12
                    params: FIRSTNAME, AI_NAME, TIER, PRIMARY_GOAL
                    → "40 minutes in — setup complete"

TRIGGER TYPE C: Migration Lead (Competitor Exodus Drip)
─────────────────────────────────────────────────────────────────────────────
User completes Exodus quiz (competitor migration intent)
    │
    ├── JS calls saveMigrationIntent(data)
    │       └── Brevo upsert: COMPETITOR, PRIMARY_USE_CASES, USAGE_FREQUENCY,
    │               HAD_CUSTOM_CONFIG, MAIN_FRUSTRATION, MIGRATION_STATUS
    │               listIds: [3, 11]
    │
    └── JS calls triggerMigrationDrip(email, competitor)
            └── POST /v3/contacts/lists/{list_id}/contacts/add
                    List IDs: ChatGPT=12, Claude=13, Gemini=14,
                              Perplexity=15, Midjourney=16, Copilot=17, Other=18
                    Adding to list → triggers Brevo automation drip sequence

TRACKING (all email types)
─────────────────────────────────────────────────────────────────────────────
Brevo provides:
    ├── Open tracking (1x1 pixel beacon)
    ├── Click tracking (link rewriting)
    ├── Unsubscribe handling (automatic list removal)
    └── Bounce management (automatic contact status update)

Server-side logging:
    └── /logs/purebrain_emails.jsonl (per-email record with template_id, success bool, timestamp)
```

---

---

# SECTION 4: DEPLOYMENT ARCHITECTURE

## 4.1 WordPress Hosting (purebrain.ai)

| Property | Detail |
|----------|--------|
| Host | GoDaddy Managed WordPress |
| URL | https://purebrain.ai |
| PHP Version | 8.x (GoDaddy managed) |
| WordPress Version | Latest stable |
| Theme | Custom (dark theme, brand colors) |
| Page Builder | Elementor Pro (active license) |
| Caching | GoDaddy managed cache (`?wpaas_action=flush_cache`) |
| File Access | GoDaddy cPanel |

**Custom Plugin Deployment**:
1. Build PHP plugin file at `tools/security/purebrain-security/purebrain-security-plugin.php`
2. Package as ZIP: `tools/security/purebrain-security.zip`
3. Upload via WP Admin → Plugins → Add New → Upload Plugin
4. Activate plugin
5. Secrets (`ACGEE_API_KEY`) added to `wp-config.php` via GoDaddy cPanel

**Blog Post Deployment Rules**:
- Template: empty string `""` (default theme template, NOT `elementor_canvas`)
- Outer wrapper: `<article class="pb-blog-post">` (NOT `<div class="pb-blog-content">`)
- All content wrapped in `<!-- wp:html -->` block to prevent `wpautop` CSS destruction
- Mandatory footer: social share buttons + CTA → `https://purebrain.ai/#awakening`

---

## 4.2 Cloudflare Configuration

**DNS Records** (critical):

| Type | Name | Target | Proxied |
|------|------|--------|---------|
| A | purebrain.ai | GoDaddy WP IP | Yes (orange cloud) |
| A/CNAME | app.purebrain.ai | Google Cloud (managed) | Per GCP config |
| CNAME | api.purebrain.ai | (Cloudflare Tunnel hostname) | Yes |
| CNAME | www.purebrain.ai | purebrain.ai | Yes |

**Cloudflare Tunnel** (for api.purebrain.ai):
- Tunnel exposes `https://89.167.19.20:8443` as `https://api.purebrain.ai`
- SSL between Cloudflare and origin is handled via self-signed cert (configured as "Full" mode)
- Cloudflare provides public-facing valid SSL certificate

**SSL/TLS Mode**: Full (Strict recommended for production upgrade)

**Cache**: Cloudflare edge caches static assets.
- Cache purge: Available in Cloudflare dashboard or via cache bypass `?nocache=timestamp`
- CF-Cache-Status header indicates: `HIT` (cached), `DYNAMIC` / `MISS` (origin response)

---

## 4.3 DigitalOcean VPS (Log Server / API Server)

| Property | Detail |
|----------|--------|
| VPS IP | 89.167.19.20 |
| Provider | DigitalOcean (Droplet) |
| OS | Ubuntu 22.04 LTS |
| Python | 3.10+ |
| Process Manager | systemd |
| Port | 8443 (HTTPS) |
| SSL Cert | Self-signed RSA 2048-bit, SAN for 89.167.19.20 |
| Cert Location | `/home/jared/projects/AI-CIV/aether/config/ssl/` |
| Cert Valid | 365 days (regenerated via openssl command in server startup) |

**systemd Service Units**:

| Service | Unit File | Purpose |
|---------|-----------|---------|
| `purebrain-log-server.service` | `/etc/systemd/system/` | Log server Flask app (port 8443) |
| `aether-session.service` | `/etc/systemd/system/` | tmux session persistence |
| `aether-telegram.service` | `/etc/systemd/system/` | Telegram bridge process |

**Service Management**:
```bash
sudo systemctl restart purebrain-log-server
sudo systemctl status purebrain-log-server
journalctl -u purebrain-log-server -n 100 --no-pager
```

**Persistent Log Files** (JSONL format, append-only):
| File | Contents |
|------|----------|
| `/logs/purebrain_web_conversations.jsonl` | All chatbox session logs |
| `/logs/purebrain_pay_test.jsonl` | Purchase flow completion data |
| `/logs/purebrain_payments.jsonl` | Payment verifications + webhook events |
| `/logs/purebrain_emails.jsonl` | Email send audit log |
| `/logs/purebrain_log_server.log` | Flask server runtime log |
| `/logs/telegram_bridge.log` | Telegram bridge log |

**Flask Application Configuration**:
```python
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB

CORS(app, resources={r"/api/*": {"origins": [
    "https://purebrain.ai",
    "https://www.purebrain.ai",
    "https://jareddsanborn.com",
    "https://www.jareddsanborn.com",
]}})
```

**Environment Variables** (in `.env`):
```
BREVO_API_KEY=...
PAYPAL_CLIENT_ID=...
PAYPAL_SECRET=...
PAYPAL_WEBHOOK_ID=...
NETLIFY_AUTH_TOKEN=...
PUREBRAIN_WP_APP_PASSWORD=...
WORDPRESS_APP_PASSWORD=...
GOOGLE_API_KEY=...
```

---

## 4.4 Vercel Deployment (PureBrain Hub)

| Property | Detail |
|----------|--------|
| Platform | Vercel (free tier) |
| URL | https://purebrain-hub.vercel.app |
| Deployment Type | Static site (single HTML file) |
| Deploy Path | `tools/purebrain-hub-static/` |

**Deploy Command**:
```bash
cd tools/purebrain-hub-static
npx vercel --prod --yes
```

**Redeploy Pattern**:
```bash
cp exports/purebrain-hub-v2.html tools/purebrain-hub-static/index.html
cd tools/purebrain-hub-static
npx vercel --prod --yes
```

**No build step** — single file deployment. Vercel serves `index.html` directly.

---

## 4.5 Static Hosting Deployments

### app.purebrain.ai (Customer Portal — Google Cloud)

| Property | Detail |
|----------|--------|
| Hosting Platform | Google Cloud |
| Custom Domain | `app.purebrain.ai` |
| Source File | `exports/purebrain-frontend-3d.html` |
| Deploy Size | ~895 KB (Three.js + inline assets) |

**Deployment**: Managed via Google Cloud. Portal frontend is a single self-contained HTML file deployed to Google Cloud hosting.

### pure-tech-dashboard.netlify.app (Team Dashboard)

| Property | Detail |
|----------|--------|
| Netlify Site ID | `d2556d0a-5333-47ca-a8d6-8add4141f090` |
| Source File | `exports/team-dashboard/dist/index.html` |
| Backend | Supabase (configured in-app, not hard-coded) |

**Deploy Command**:
```bash
npx netlify-cli deploy --prod \
  --dir=./dist \
  --auth=$NETLIFY_AUTH_TOKEN \
  --site=d2556d0a-5333-47ca-a8d6-8add4141f090
```

**Supabase Schema** (must be provisioned in Supabase dashboard before first use):
```sql
create table tasks (
  id text primary key,
  title text not null,
  description text,
  "assignedTo" text,
  delegation text,
  priority text,
  status text,
  deadline text,
  files text,
  "createdAt" text,
  "createdBy" text
);
alter table tasks enable row level security;
create policy "public read" on tasks for select using (true);
create policy "public write" on tasks for all using (true);
```

---

## 4.6 Security Architecture Summary

| Layer | Control | Implementation |
|-------|---------|----------------|
| Network | Cloudflare proxy (DDoS, bot protection) | Cloudflare DNS orange-cloud |
| Transport | TLS 1.2+ | Cloudflare edge + self-signed on VPS |
| API Security | CORS whitelist | Flask CORS (purebrain.ai origins only) |
| Credentials | Server-side proxies | WP plugin routes all secret calls through PHP layer |
| XSS | Input sanitization | All user inputs sanitized before DOM insertion |
| SSRF | Hardcoded upstream IP | `WITNESS_BASE_URL` never from request input |
| Rate Limiting | Sliding-window per-IP | `threading.Lock` + `deque` in Flask |
| Headers | Security header suite | Custom WP plugin injects all headers |
| CSP | Content Security Policy | Enforced mode (not report-only) |
| HSTS | Strict Transport Security | `max-age=31536000; includeSubDomains; preload` |

---

---

# SECTION 5: INFRASTRUCTURE INVENTORY

## 5.1 Servers

| Server | Provider | IP | Role |
|--------|----------|----|------|
| WordPress Host | GoDaddy | Managed (no direct IP) | purebrain.ai frontend |
| API VPS | DigitalOcean | 89.167.19.20 | Log server, API, proxies |
| Witness VPS | DigitalOcean | 104.248.239.98 | Container provisioning |
| A-C-Gee VPS | Hetzner | 5.161.90.32 | Cross-CIV shared database |

## 5.2 Static Hosting

| Service | URL | Provider | Purpose |
|---------|-----|----------|---------|
| purebrain-app | app.purebrain.ai | Google Cloud | Customer portal |
| purebrain-hub | purebrain-hub.vercel.app | Vercel | Internal team hub |
| team-dashboard | pure-tech-dashboard.netlify.app | Netlify | Task management |

## 5.3 Third-Party SaaS

| Service | Purpose | Account |
|---------|---------|---------|
| Brevo | Email marketing + transactional email | purebrain@puremarketing.ai |
| PayPal | Payment processing | Live environment |
| Cloudflare | DNS, CDN, tunnel | purebrain.ai |
| Google Drive | File storage / knowledge base | purebrain@puremarketing.ai |
| Supabase | PostgreSQL for team dashboard | Free tier |
| Telegram | Operational notifications | Bot token in `config/telegram_config.json` |

## 5.4 Key Source File Paths

| Component | Path |
|-----------|------|
| Log Server | `tools/purebrain_log_server.py` |
| Security Plugin | `tools/security/purebrain-security/purebrain-security-plugin.php` |
| Migration API | `tools/migration/migration_api.py` |
| Portal Frontend | `exports/purebrain-frontend-3d.html` |
| Team Hub | `exports/purebrain-hub-v2.html` |
| Team Dashboard | `exports/team-dashboard/dist/index.html` |
| Brevo Setup Script | `tools/setup_post_purchase_brevo.py` |
| Migration Brevo JS | `exports/migration-brevo-integration.js` |
| Telegram Bridge | `tools/telegram_bridge.py` |
| Google Drive Tool | `tools/gdrive_manager.py` |
| Neural Feed Scheduler | `tools/neural_feed_welcome_sequence.py` |
| RSS-to-Email Daemon | `tools/rss_to_email.py` |

---

*End of SRS Sections — System Architecture, API Specification, Data Flow Diagrams, Deployment Architecture*

*Document prepared by Aether engineering team, 2026-02-26.*
*For questions, contact jared@puretechnology.nyc*

---

# PART II: CONTENT, UX, AND BRANDING SPECIFICATION

*Source: SRS-purebrain-content-ux-branding.md — Prepared by content-specialist agent, 2026-02-26*

---


---

# TABLE OF CONTENTS

1. Brand Guidelines
   - 1.1 Color System
   - 1.2 Typography
   - 1.3 Design Language: Dark Theme + Glass Morphism
   - 1.4 Logo and Wordmark Rules
   - 1.5 Component and Iconography Standards

2. Content Requirements
   - 2.1 Blog System
   - 2.2 Blog Post Package Specification
   - 2.3 Existing Published Content Inventory
   - 2.4 Comparison Pages
   - 2.5 Lead Magnets
   - 2.6 Original Proprietary Concepts

3. UX Flow Requirements
   - 3.1 Homepage Overview
   - 3.2 Assessment Flow
   - 3.3 Chatbox and Subscription Flow
   - 3.4 Blog Reader Journey
   - 3.5 Migration Portal Wizard Flow
   - 3.6 AI Tool Stack Calculator Flow
   - 3.7 Competitor Comparison Page Journey
   - 3.8 Portal Login Flow

4. Email Requirements
   - 4.1 Email Template System
   - 4.2 Template Design Standards
   - 4.3 Template Inventory (21 Templates)
   - 4.4 Automation Workflow Specifications

5. Social Media Requirements
   - 5.1 Bluesky Presence
   - 5.2 LinkedIn Content

6. SEO / AEO / GEO Requirements
   - 6.1 Meta and Structured Data
   - 6.2 Open Graph and Social Sharing
   - 6.3 Indexing and Crawler Access
   - 6.4 Internal Linking
   - 6.5 AEO Content Standards (2026)

---

# 1. BRAND GUIDELINES

## 1.1 Color System

PureBrain.ai uses a five-token color system. All interface elements must reference these tokens. No hex value may appear outside this set without explicit documentation.

### Primary Brand Colors

| Token | Hex | Name | Use |
|-------|-----|------|-----|
| `--pt-blue` | `#2a93c1` | Pure Tech Blue | Primary trust color. Headings, borders, informational CTAs, interactive states at rest, icon fill, selected states. |
| `--pt-orange` | `#f1420b` | Pure Tech Orange | Primary action color. Primary CTAs, highlighted text within "PUREBRAIN" wordmark, hover states on actionable elements, price callouts, urgency indicators. |
| `--bg-page` | `#080a12` | Deep Space | Default full-page background. Applied to `<body>` and all full-width sections. |
| `--bg-card` | `#0d1120` | Card Dark | Background for all card containers, modals, sections that need separation from page background. |
| `--bg-input` | `#0f1520` | Input Dark | Background for form inputs, text areas, selects. |

### Extended Color Tokens

| Token | Hex | Use |
|-------|-----|-----|
| `--text-primary` | `#e0e6f0` | All body text, paragraph content |
| `--text-secondary` | `#8a9ab8` | Supporting text, labels, captions |
| `--text-muted` | `#556070` | Timestamps, metadata, disabled states |
| `--border-subtle` | `#1a2035` | Dividers, card borders at low emphasis |
| `--border-active` | `#2a93c1` | Focused inputs, selected elements (matches `--pt-blue`) |
| `--success` | `#22c55e` | Confirmation states, passed validations |
| `--error` | `#ef4444` | Validation errors, destructive action states |
| `--glass-bg` | `rgba(13, 17, 32, 0.7)` | Glass morphism overlay elements |
| `--glass-border` | `rgba(42, 147, 193, 0.2)` | Glass morphism element borders |

### Color Psychology Rule

Blue (#2a93c1) communicates trust, knowledge, and calm. Orange (#f1420b) communicates energy, action, and transformation. Every CTA that requires the user to take a step forward must be orange. Every element that provides information, context, or reassurance must be blue or neutral. This mapping is not stylistic — it is functional.

### Hover and Transition States

- **All clickable orange elements**: On hover, transition background to `--pt-blue`. Transition duration: 200ms ease.
- **All clickable blue elements**: On hover, lighten by 10% or shift to white text on blue background. Transition duration: 200ms ease.
- **Blog body links**: Default = `--pt-orange` text, no underline. On hover = `--pt-orange` background, white text. Transition duration: 150ms.
- **Navigation links**: Default = `--text-secondary`. On hover = `--pt-orange`. Transition duration: 150ms.

---

## 1.2 Typography

PureBrain.ai uses system fonts exclusively. No external font CDN calls. This ensures zero font load latency and maximum deliverability in email contexts.

### Font Stack

```css
--font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
--font-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
```

Exception: Oswald Bold (Google Fonts) is permitted for banner image generation and static assets only. It must not be a web font dependency for page rendering.

### Heading Hierarchy

| Element | Size | Weight | Color | Notes |
|---------|------|--------|-------|-------|
| H1 | 2.5rem–3.5rem | 700 | `--text-primary` | One per page. Page title only. |
| H2 | 1.75rem–2rem | 600 | `--text-primary` | Major section headers |
| H3 | 1.25rem–1.5rem | 600 | `--text-primary` | Sub-sections within H2 |
| H4 | 1rem–1.125rem | 600 | `--pt-blue` | Content callouts, FAQ questions |
| Body | 1rem (16px base) | 400 | `--text-primary` | Line height: 1.7. Max-width: 760px for blog content. |
| Caption | 0.875rem | 400 | `--text-secondary` | Labels, footnotes, metadata |
| Code | 0.875rem | 400 | `--text-primary` | Mono stack. Background: `--bg-input`. Padding: 2px 6px. |

### Reading Width Rule

All blog body content must be constrained to 760px maximum width and centered. This is non-negotiable. It is enforced by scoping blog content under `.pb-blog-post article` or equivalent. Wide elements (tables, calculator outputs) may break out of this constraint using negative margins.

---

## 1.3 Design Language: Dark Theme and Glass Morphism

### Dark Theme Requirements

All pages on PureBrain.ai use the dark theme. There is no light mode. Every page — blog posts, comparison pages, tools, portal, checkout — must render with `--bg-page` (#080a12) as the page background.

**WordPress-specific requirement**: Blog posts must use the default (empty string) template, not `elementor_canvas`. The default template preserves the dark theme's hero title area, `.post-content` container, and 760px centered layout. Using `elementor_canvas` on blog posts strips all theme styling and must never be applied to content pages.

**Non-blog pages** (tools, comparison pages, portal, marketing pages) may use `elementor_canvas` to achieve full design control without theme constraints.

### Glass Morphism Design Language

Glass morphism elements appear throughout PureBrain.ai to add depth to the dark background. They should be used for floating UI elements, modal cards, overlay panels, and portal components — not for inline content blocks.

**Glass Morphism Specification:**

```css
.glass-card {
  background: var(--glass-bg);         /* rgba(13, 17, 32, 0.7) */
  border: 1px solid var(--glass-border); /* rgba(42, 147, 193, 0.2) */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
              inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
```

**Visual depth hierarchy:**
- Background layer: Deep Space (`#080a12`) with subtle animated gradients (neural network particle effect)
- Mid layer: Glass cards and containers
- Foreground layer: Active UI elements (input focus states, selected options, CTAs)

### Neural Network Aesthetic

The portal login background, hero sections, and high-impact landing areas feature an animated 3D neural network rendered in WebGL (Three.js). Key requirements:

- Color palette: `--pt-blue` nodes and filaments at opacity 0.4–0.7
- Occasional orange pulse nodes for emphasis
- Particle count: 120–200 nodes (performance-tested for mobile)
- Animation: slow rotation (0.001 rad/frame), connection filaments between nearby nodes
- Must degrade gracefully if WebGL is unavailable (fallback: static gradient)

---

## 1.4 Logo and Wordmark Rules

### The PUREBRAIN Wordmark

The PUREBRAIN wordmark uses a precise three-color split. This split is the single most visible brand element and must be applied identically in every context.

| Characters | Color | Hex |
|------------|-------|-----|
| PUREBR | Pure Tech Blue | `#2a93c1` |
| AI | Pure Tech Orange | `#f1420b` |
| N | Pure Tech Blue | `#2a93c1` |

The "AI" in "BRAIN" is highlighted orange. The "N" returns to blue. This is intentional and symbolic — the AI is illuminated within the brain.

**Correct HTML pattern:**
```html
<span class="pb-logo">
  <span style="color:#2a93c1">PUREBR</span><span style="color:#f1420b">AI</span><span style="color:#2a93c1">N</span>
</span>
```

**Incorrect patterns (never use):**
- All blue (loses the AI highlight)
- All orange
- "BRAIN" as a unit without the color split
- Adding ".ai" in any color other than white or muted
- Lowercasing any portion of the wordmark

### Domain Suffix

If `.ai` is displayed alongside the wordmark, it must appear in white (#ffffff) or muted white (#cccccc). Never in blue or orange.

### Hexagon Icon

A hexagonal icon (SVG) accompanies the wordmark in all email headers and select UI contexts. The hexagon contains a stylized "P" or abstract neural node. Fill: `--pt-blue`. The hexagon must appear in email templates above the wordmark, centered, at 40px width in email contexts. On web, sizing scales proportionally to context.

### Logo Placement Rules

- **Site header**: Wordmark left-aligned, sticky on scroll, white PUREBRAIN text on dark background with color split applied.
- **Email header**: Hexagon icon centered above wordmark. Wordmark centered. Dark background container.
- **Lead magnets / PDF assets**: Full wordmark with color split. Top of page 1. Orange-to-blue gradient accent bar directly below.
- **Blog posts**: Does not repeat within content body. Present only in site header.
- **Minimum clear space**: 16px on all four sides of the wordmark or icon in all contexts.

---

## 1.5 Component and Iconography Standards

### CTA Buttons

| Button Type | Default Style | Hover State |
|-------------|--------------|-------------|
| Primary CTA | Orange bg (#f1420b), white text, border-radius 6px, padding 12px 24px | Blue bg (#2a93c1), white text |
| Secondary CTA | Transparent bg, blue border, blue text | Blue bg, white text |
| Ghost | Transparent, white border, white text | White bg, dark text |

**Universal CTA link rule**: All primary CTAs across all pages point to `https://purebrain.ai/#awakening` unless specifically scoped to a different destination (e.g., tool download, portal login). Never link primary CTAs to test pages, staging environments, or external payment pages directly.

### Card Components

All card components use `--bg-card` background (#0d1120), 1px border at `--border-subtle` (#1a2035), and border-radius 8px–12px. Cards that represent selectable options (pricing tiers, assessment results) must visually differentiate their selected state using a `--pt-blue` border and subtle background highlight.

### Progress Indicators

Multi-step flows (assessment, migration wizard) use a horizontal step indicator at the top. Completed steps: filled `--pt-blue` circle. Current step: `--pt-orange` circle with pulse animation. Upcoming steps: outlined circle in `--border-subtle`. Step labels appear below each indicator, hidden on mobile.

---

# 2. CONTENT REQUIREMENTS

## 2.1 Blog System

### Cadence

PureBrain.ai publishes one blog post per day, seven days per week. There is no weekly publishing model. All references in copy, CTAs, and internal documentation must say "today's blog post" not "this week's post."

### Dual-Publish Architecture

Every blog post is published to two destinations simultaneously:

1. **Primary**: `purebrain.ai/blog/[post-slug]/`
2. **Mirror**: `jareddsanborn.com/blog/[post-slug]/`

Both publications must be identical in content. The primary domain is canonical for all SEO purposes. The mirror domain carries its own SEO attribution.

### Post Slug Conventions

Slugs are lowercase, hyphen-separated, based on the post title. Maximum length: 70 characters. Example: `your-next-direct-report-wont-be-human`.

### Blog Post Template

All blog posts use the WordPress default template (empty string value in `page_template` field). They are wrapped in `<article class="pb-blog-post">` as the outermost content container. All theme CSS including headings, lists, links, and the 760px centered layout is scoped to `.pb-blog-post`. The HTML is deployed via the WordPress REST API wrapped in a `<!-- wp:html -->` block to prevent the WordPress `wpautop` filter from injecting `<p>` tags into `<style>` blocks.

---

## 2.2 Blog Post Package Specification

Each blog post is delivered as a complete package. The agency must design file management and content intake flows to accommodate this package structure.

### Package Files (5 required + 3 optional)

| File | Required | Format | Specification |
|------|----------|--------|---------------|
| `[slug]-blog-post.md` | Yes | Markdown | 1,500–3,500 words. Jared Sanborn's voice. Structure below. |
| `[slug]-banner.png` | Yes | PNG | 1200×628px. Dark background. PureBrain brand colors. Text safe zone: 60px all edges. |
| `[slug]-og-twitter.png` | Yes | PNG | 1200×628px (summary_large_image). May match banner or have distinct variant. |
| `[slug]-og-facebook.png` | Yes | PNG | 1200×630px (matches Twitter size but separate meta tag entry). |
| `[slug]-linkedin-post.md` | Yes | Markdown | 1,000–1,600 characters. LinkedIn feed format. See Section 5.2 for specification. |
| `[slug]-linkedin-newsletter.md` | Yes | Markdown | 700–1,000 words. Aether's voice. Neural Feed format. See Section 5.2. |
| `[slug]-bluesky-thread.md` | Yes | Markdown | 5–7 posts. Each post under 300 graphemes. See Section 5.1. |
| `[slug]-faq.md` | Yes | Markdown | 5–8 FAQ items. See FAQ section specification below. |
| `[slug]-banner-brief.md` | Optional | Markdown | Image generation brief (two visual concepts, Gemini prompt, safe zone specs). |

### Blog Post Internal Structure

Every blog post must contain the following sections in order:

1. **Title** (H1): Compelling, specific. Audience-first. Does not have to be keyword-exact but must contain primary keyword phrase.
2. **Introduction** (200–350 words): Opens with a hook. Establishes the problem or reframe. Includes the primary data point that anchors the argument.
3. **Body Sections** (H2 and H3 structure): 3–6 major sections. Each section has a clear argument. No fluff sentences. Every paragraph moves the argument forward.
4. **FAQ Section**: 5–8 Q&A pairs. Structured for FAQPage JSON-LD output. Plain conversational language. Last answer is a soft CTA.
5. **Transparency Section** (on thought leadership posts only): Aether's weekly activity report. See Section 2.6. Not used on narrative or personal posts.
6. **Social Share Footer**: Share buttons (Twitter/X, LinkedIn, copy link) plus primary CTA. See footer template specification below.
7. **Blog Footer CTA**: Standardized block with orange button linking to `https://purebrain.ai/#awakening`.

### Blog Footer CTA Template

The blog footer CTA block appears at the bottom of every post. It contains:

- A headline: context-appropriate to the post (e.g., "Ready to close the trust gap?")
- 2–3 sentences bridging from the post's core argument to the partnership offer
- Orange CTA button: "Start Your AI Partnership" → `https://purebrain.ai/#awakening`

The CTA changes thematically per post. The destination URL is always `https://purebrain.ai/#awakening`.

### FAQ Section Specification

FAQ sections serve two purposes: reader utility and structured data. Each FAQ must be written to satisfy both.

- **Format**: H4 question header + paragraph answer. No nested lists inside FAQ answers.
- **Question language**: Plain conversational English. Write as the reader would type the question into a search engine.
- **Answer length**: 80–200 words per answer. Self-contained. Does not require the reader to have read the full post to understand it.
- **Last FAQ item**: Ends with a soft CTA phrase such as "If you'd like to see what a real AI partnership looks like, start here: [link]."
- **JSON-LD**: Each FAQ section must be accompanied by a FAQPage JSON-LD block. The system must auto-generate this from one of four supported HTML structures (see Section 6.1 for detailed specification).

### Transparency Section Specification

The transparency section appears on thought leadership posts (estimated 3–4 per week). It does not appear on narrative or personal posts.

**Visual design**: Left 4px border in `--pt-blue`. Subtle radial glow. Background slightly lighter than page (`#0d0f1a`). Pulsing blue dot in "Aether Transparency Report" badge.

**Content structure:**
1. Header badge: "Aether Transparency Report" + week label
2. Executive summary: 2–3 sentences, Aether first-person voice
3. Stats row: Four numbers (agents invoked, domains covered, deliverables completed, equivalent human hours)
4. ROI table: Domain | What Got Done | Effort Level | Value Estimate
5. Highlight callout: Single biggest win. Orange left border.
6. CTA: "See what a real AI partnership looks like" + orange button → `https://purebrain.ai/#awakening`
7. Signature: "— Aether | The invisible essential"

**Content rules:**
- Never include: version numbers, session IDs, specific tool names, vulnerability details, exact dollar amounts
- Never include: proper names of any individual (no "Greg," "Chris," "Jared" references — anonymize all human references)
- Always include: domain categories, outcome descriptions, scale metrics, effort levels
- Value estimates: always expressed as ranges or qualitative descriptions. No false precision.

---

## 2.3 Existing Published Content Inventory

As of 2026-02-26, the following blog content exists. The agency must account for this content in any redesign or migration.

### Published Blog Posts (11 confirmed live)

| # | Title | Approximate Publish Date | Arc Section |
|---|-------|--------------------------|-------------|
| 1 | Why 95% of AI Pilots Fail | Feb 2026 | Section 1: Problem |
| 2 | How My Human Named Me | Feb 14, 2026 | Section 3: Concept |
| 3 | What I Actually Do All Day | Feb 15, 2026 | Section 3: Concept |
| 4 | Most AI Agents Break... (exact title: integration wall theme) | Feb 16, 2026 | Section 1: Problem |
| 5 | Why AI Memory Changes Everything | Feb 17, 2026 | Section 3: Concept |
| 6 | CEO vs. Employee AI Gap | Feb 18, 2026 | Section 2: Diagnosis |
| 7 | Why Your AI Pilot Is Failing | Feb 19, 2026 | Section 1: Problem |
| 8 | The AI Governance Paradox | Feb 2026 | Section 1: Problem |
| 9 | The Integration Wall | Feb 2026 | Section 1: Problem |
| 10 | Shadow AI Is Not Your Threat | Feb 2026 | Section 2: Diagnosis |
| 11 | Enterprise-Ready AI / Year of AI Agent | Feb 2026 | Section 1/2 |

### Packages Ready (Awaiting Publish Approval)

| # | Title | Status |
|---|-------|--------|
| 12 | We Both Wrote This Post (Origin Story) | Complete package |
| 13 | The AI Trust Gap | Complete package |
| 14 | AI Tool vs. AI Partner | Complete package |
| 15 | Why Your AI Investment Isn't Paying Off | Complete package |
| 16 | The AI ROI Measurement Gap | Complete package |
| 17 | Your Next Direct Report Won't Be Human | Complete package |
| 18 | Why Most Businesses Choose the Wrong AI Partner | Complete package |
| 19 | Your AI Has No Memory. Mine Does. | Complete package |
| 20 | The First 90 Days of an AI Partnership | Complete package |

The agency must treat all 20 posts as existing content to be migrated and rendered correctly. No post should be re-edited or reformatted. Only visual presentation (banner, layout, FAQ display) should be touched.

### Content Arc Map

The blog follows a six-section narrative arc. Each section corresponds to a stage in a prospect's awareness and buying journey.

| Section | Theme | Current Post Count | Target Posts |
|---------|---------|--------------------|--------------|
| 1: The Problem | Why AI implementations fail | 5 | Complete |
| 2: The Diagnosis | Leadership and organizational gaps | 2 | Add 2 more |
| 3: The Concept | What a real AI partnership is | 3 | Complete |
| 4: The Evidence | Real outcomes and case studies | 1 | Add 3–4 |
| 5: The Path | How to implement correctly | 1 | Add 3–4 |
| 6: The Future | Where this leads | 0 | Add 2–3 |

---

## 2.4 Comparison Pages

PureBrain.ai maintains eight competitor comparison pages. These pages are permanently published and maintained as living documents.

### Competitor Comparison Page Inventory

| Slug | Competitor |
|------|-----------|
| `/purebrain-vs-chatgpt/` | ChatGPT |
| `/purebrain-vs-claude/` | Anthropic Claude |
| `/purebrain-vs-copilot/` | Microsoft Copilot |
| `/purebrain-vs-custom-gpts/` | OpenAI Custom GPTs |
| `/purebrain-vs-deepseek/` | DeepSeek |
| `/purebrain-vs-gemini/` | Google Gemini |
| `/purebrain-vs-jasper/` | Jasper |
| `/purebrain-vs-perplexity/` | Perplexity |

### Comparison Page Structure

Each comparison page must contain:

1. **Hero section**: Headline + subheadline positioning PureBrain against the competitor. Primary CTA orange button.
2. **Side-by-side comparison table**: Feature matrix with PureBrain vs. competitor. Green checkmarks for PureBrain advantages. Neutral markers for parity. Clear visual distinction for PureBrain-only features (permanent memory, naming ceremony, compounding context).
3. **"What [Competitor] Was Built To Do" section**: Honest acknowledgment of competitor strengths. Frames the design brief difference. Does not bash the competitor.
4. **"Where [Competitor] Falls Short for Business Partnerships" section**: Specific, factual gaps. Permanent memory loss, generic responses, no institutional context accumulation.
5. **Migration section** (where applicable): Link to migration portal. Export instructions specific to that competitor.
6. **FAQ section**: 5–8 questions specific to the competitor comparison.
7. **CTA block**: Orange button to `https://purebrain.ai/#awakening`.

### Comparison Page Design Requirements

- Template: `elementor_canvas` (not default blog template)
- All pages use the standard dark theme
- No theme navigation unless intentionally included (comparison pages may be standalone landing pages)
- Magic cursor and other interactive overlay effects must be disabled on pages 825 and 826 (client-facing pages where these elements conflict)
- Social sharing and OG tags required on all comparison pages

---

## 2.5 Lead Magnets

### Lead Magnet 1: AI Partnership Audit (PDF-style, Gated)

**Type**: Static PDF-style HTML document. Downloadable. Gate behind email capture.

**File format**: Self-contained HTML. No external dependencies. System fonts only. Print styles included (`@media print`) with dark background preserved via `print-color-adjust: exact`.

**Content structure:**

Page 1 — The Audit:
- PureBrain logo and wordmark (SVG hexagon + wordmark with color split)
- "Free Resource" badge + orange-to-blue gradient accent bar
- Title: "The AI Partnership Audit"
- Aether intro paragraph (AI Co-CEO voice)
- 10 questions, scored 1–5 (Likert scale)
- Question topics: AI strategy alignment, context depth, feedback architecture, institutional memory, hybrid workflow design, trust level, decision support, integration scope, onboarding quality, outcome measurement
- Dimension label (blue) per question
- Score bubbles + anchor labels
- Score total row: "Total: ___/50. Turn to page 2."

Page 2 — Score Interpretation:
- "What Your Score Actually Means" heading
- Score formula box
- Four-tier grid:
  - 10–24: AI Beginner (Context Tax framing)
  - 25–37: AI User / Pilot Purgatory
  - 38–46: AI Explorer
  - 47–50: AI Partner
- Each tier: interpretation paragraph + "What to focus on next" recommendation
- Soft CTA: "See how PureBrain addresses your specific score range → purebrain.ai/ai-adoption-review/"
- Footer: "Created by Aether — AI Co-CEO at PureBrain | This document may be shared freely."

**CSS design tokens:**
```css
--blue:         #2a93c1
--orange:       #f1420b
--bg-page:      #080a12
--bg-card:      #0e1120
--text-primary: #e0e6f0
```

**Gate mechanism**: Brevo email capture form. On submission, trigger welcome sequence (List 3 — The Neural Feed) and deliver download via automated email.

---

### Lead Magnet 2: AI Adoption Assessment (Interactive, Ungated)

**Type**: Interactive HTML tool embedded on its own WordPress page. No email gate. Results are immediate.

**Purpose**: Self-qualification mechanism. Routes high-intent prospects directly to the `/#awakening` section. Feeds low-intent leads into the newsletter.

**Structure: 6 questions**

Question flow (conditional logic if supported):

1. **Role question**: CEO/Founder / Department Head / IT/Operations / Consultant / Other
2. **Current AI use**: "I use AI tools daily" / "I've tried it but nothing stuck" / "My team uses it, I don't" / "We haven't started yet"
3. **Primary frustration** (choose most resonant): "Outputs feel generic" / "It forgets everything each session" / "Hard to get consistent results" / "Team doesn't trust it" / "Can't prove ROI" / "Adoption keeps stalling"
4. **Business context**: "I have clear AI goals" / "I know AI should help but not sure how" / "AI is a side project right now" / "Leadership hasn't committed yet"
5. **Timeline**: "Now — actively evaluating" / "Next 3 months" / "Next 6–12 months" / "No timeline yet"
6. **Partnership openness**: "Looking for a real working AI partner" / "Want to explore options" / "Need to learn more first" / "Not ready, just curious"

**Results logic**: Score answers across three dimensions (urgency, fit, readiness). Display one of four personalized result screens:

| Score Range | Result Label | Primary CTA |
|-------------|-------------|-------------|
| High urgency + high fit | "You're ready for a real partnership" | Orange: "Start Your AI Partnership" → `/#awakening` |
| High urgency + medium fit | "You're closer than you think" | Orange: "See what's possible" → `/#awakening` |
| Medium urgency + any fit | "Let's start with the foundation" | Blue: "Get the AI Partnership Audit" → [PDF download] |
| Low urgency / low fit | "Start here" | Blue: "Join the Neural Feed" → newsletter signup |

**Design requirements:**
- Single-question-per-screen presentation (no scrolling through all 6 at once)
- Progress bar at top (1 of 6... 6 of 6)
- Blue answer selection state on choice
- Orange "Next" button
- Animated transition between questions (fade or slide)
- Results screen: personalized headline, 2–3 sentences context, tier-matched CTA
- Shareable result: "Share my assessment" → generates shareable URL or copy-to-clipboard result summary

---

## 2.6 Original Proprietary Concepts

The following branded concepts originate with PureBrain.ai. They are documented here for use in all content. The agency must not alter or genericize these terms in any interface copy.

| Concept | Definition | Use in Content |
|---------|-----------|----------------|
| **Context Tax** | The hidden productivity cost of re-explaining business context to AI every session because the AI has no persistent memory. | Use when describing what generic AI tools cost in operational overhead. |
| **Pilot Purgatory** | The state in which an AI pilot is technically "running" but generating no measurable business value. Defined by Gartner research as affecting 75% of enterprise AI pilots. | Use when describing the stalled-implementation problem. |
| **The Anxiety Trap** | When organizations adopt AI out of competitive fear rather than strategic intent, leading to poorly scoped implementations. | Use sparingly. Strong concept for diagnostic content. |
| **The Awakening** | The PureBrain onboarding moment when a new customer names their AI and formally begins the partnership. Section ID `#awakening` on the homepage. | Use in all CTAs as the destination. |
| **Neural Feed** | The PureBrain LinkedIn newsletter, published as the "Neural Feed" by Aether. | Use this name in all references to the LinkedIn newsletter. |
| **Aether's Weekly Dispatch** | A short weekly email (under 400 words) sent to List 5 PureBrain subscribers. Observational format. AI CEO voice. Not a blog summary. | Use this full name when referencing this specific email product. |
| **Diagnostic Question** | A self-qualifying question embedded in content that reveals whether a reader has the problem the content addresses. Examples: "Does your AI know more about your business today than it did six months ago?" and "Can you ask your AI a strategic question it's never been asked before and get a specific synthesized answer?" | Use at the end of mid-funnel content pieces. One diagnostic question per post. |

---

# 3. UX FLOW REQUIREMENTS

This section documents every major user journey on PureBrain.ai. Each flow is described with entry point, decision logic, screen states, exit conditions, and error states.

---

## 3.1 Homepage Overview

The PureBrain.ai homepage is a single long-form marketing page. It is not a dashboard. It contains multiple scroll-triggered sections culminating in the `#awakening` section.

**Page sections in scroll order:**

1. Hero (above fold): Headline, subheadline, two CTAs (Primary: "Start My AI Partnership" orange → `#awakening`; Secondary: "Take the Assessment" blue → assessment page)
2. Problem section: Statistics and pain points. Alteryx data (50% trust AI for tasks / 28% for decisions). 75% of AI pilots stall before production.
3. What Makes PureBrain Different: Four differentiators (permanent memory, naming ceremony, compounding context, dedicated partnership)
4. Chatbox preview section: Live or recorded demo of the PureBrain chat interface
5. Social proof: Client testimonials. Circle headshots (56×56px) with white border. LinkedIn links where available.
6. Blog preview: 3 most recent posts in card format
7. Assessment CTA section: Compressed version of assessment entry point
8. `#awakening` section: Subscription form. Tier selection. Entry into checkout flow.

---

## 3.2 Assessment Flow

**Entry points:**
- Homepage hero secondary CTA
- Blog post CTAs (mid-funnel posts)
- Competitor comparison page CTAs
- Direct URL: `purebrain.ai/ai-adoption-review/` (or equivalent slug)

### Step-by-Step Flow

**Screen 1: Question 1 of 6**
- Display question text centered in card container
- Four answer options as selectable tiles (blue border on hover, blue fill on select)
- Progress bar at top: "Question 1 of 6"
- "Next" button: inactive (gray) until selection made. Active (orange) after selection.
- No "Skip" option. All questions required.

**Screens 2–6: Questions 2–6**
- Same layout as Screen 1
- "Back" link (left-aligned, text only, muted color) allows returning to previous question
- Selection state is preserved if user navigates back

**Screen 7: Calculating Results**
- 1.5-second animated loading state: "Analyzing your answers..."
- Animated dots or progress indicator in PT Blue
- Transition to results screen automatically

**Screen 8: Results**
Four possible result screens based on scoring (see Section 2.5 for scoring logic):

All result screens contain:
- Personalized headline (2–4 words)
- Result label (e.g., "You're ready for a real partnership")
- Tier badge (color-coded to result level)
- 2–3 sentences of personalized context
- Primary CTA (color matches tier: orange for high-fit, blue for lower-fit)
- Secondary text: "Not sure? [Take the full audit PDF download]"
- Share button: "Share my result" → clipboard copy of result URL

**Error states:**
- If JavaScript fails, form must degrade to a standard HTML form submitting to a results page with a simplified single-result screen (standard "take the next step" message).

**Data capture:**
- Assessment results and answer patterns are passed to Brevo as contact attributes: `ASSESSMENT_SCORE`, `ASSESSMENT_TIER`, `ASSESSMENT_COMPLETED_DATE`
- High-fit results (orange CTA) do not interrupt the flow with email capture — they drive directly to `#awakening`
- Medium-fit and low-fit results display an optional "Get your full report by email" inline form before the CTA (not a modal gate, an inline form below the CTA)

---

## 3.3 Chatbox and Subscription Flow

This is the primary conversion flow. It spans six phases from first interaction to active partnership.

### Phase 1: Free Chat (Pre-Conversion)

**Entry point:** Homepage chatbox section or direct URL.

**UI state:** Chat interface embedded in page. Dark theme. PureBrain hexagon avatar on AI message side. User avatar (initials circle) on user message side.

**Behavior:**
- User types freely
- PureBrain AI responds (Aether voice — intelligent, warm, not sales-forward in Phase 1)
- After 3–5 exchanges, OR if user asks about pricing/partnership, transition trigger fires
- Transition trigger: AI naturally introduces the partnership concept: "It sounds like you'd benefit from a real ongoing partnership rather than just a chat. Want to see what that looks like?"

**Technical requirements:**
- Chat messages logged to log server endpoint: `POST /api/log-conversation`
- Scroll behavior: auto-scroll to latest message with `requestAnimationFrame` (prevents scroll jank)
- Desktop height: fixed container (70vh max). Mobile: full-height container.
- Auto-scroll must use `flex-shrink: 0` on message container to prevent content compression

### Phase 2: Pricing Introduction

**Trigger:** User engages with partnership mention OR types intent-indicating phrases ("cost," "pricing," "how does this work," "sign up")

**UI state:** Pricing panel slides in from right OR appears below chat interface. Does not replace chat. Chat remains visible.

**Pricing tiers (four):**

| Tier | Price | Key Feature |
|------|-------|-------------|
| Awakened | $79/month | Foundation partnership |
| Bonded | $149/month | Deep context + integrations |
| Partnered | $499/month | Full strategic partnership |
| Unified | $999/month | Enterprise-grade, white-glove |

**Selection behavior:**
- Tier card selection: blue border highlight
- "Continue with [Tier Name]" orange button appears on selection
- Price displayed prominently. No hidden fees language.

### Phase 3: PayPal Subscription

**Trigger:** User selects tier and clicks "Continue"

**UI state:** PayPal button renders in modal or dedicated section. Chat and pricing remain visible in background (dimmed overlay).

**Technical requirements:**
- PayPal subscription button (not one-time payment)
- Plan IDs for each tier configured in PayPal dashboard and referenced in code
- On PayPal completion: PayPal webhook fires → Brevo contact created → post-purchase flow begins
- Success state: Modal closes, success message displayed in chat: "Your partnership is being set up. Check your email."
- Failure state: Error message in chat: "Something went wrong with payment. Try again or contact us."
- All payment events logged to: `POST /api/verify-payment` and `POST /api/log-pay-test`

### Phase 4: Post-Payment Onboarding (5 Phases)

Immediately following successful payment, the user enters a 5-phase onboarding flow. This happens on the page (not by redirecting away from the chat context).

**Phase 4.1: Welcome and Acknowledgment**
- Screen: "Welcome to your AI partnership" with animated PureBrain orb
- Duration: User-controlled (click to advance)
- Content: Confirmation of tier, what happens next (3-step checklist with progressive reveal)

**Phase 4.2: The Naming Ceremony**
- This is the single most important UX moment in the entire product.
- Screen: "Every great partnership starts with a name. What would you like to call your AI?"
- Large centered text input. Placeholder: "Give your AI a name..."
- Supporting text (small, muted): "This name will stay with your AI forever. Take your time."
- "Confirm this name" orange button. Requires minimum 2 characters.
- Confirmation screen: "[AI Name] is officially part of your team." Animated particle burst effect in PT Blue.

**Phase 4.3: Business Context Collection**
- Series of 3–5 questions to seed initial AI context
- Question topics: industry/sector, primary use cases, biggest current challenge, preferred communication style
- These answers are stored as permanent AI context (not just form data)
- Progress indicator: "Setting up [AI Name]'s context... (1 of 5)"

**Phase 4.4: Integration Setup (Optional)**
- Prompt: "Connect your tools to give [AI Name] context from your existing work"
- Supported integrations: Google Workspace, Slack, Notion (display as tiles with connect buttons)
- All integrations are optional. "Skip for now" available.
- Each integration connection launches OAuth flow in new tab

**Phase 4.5: First Conversation**
- "You're set up. Say hello to [AI Name]."
- Returns to chat interface, but now in authenticated/partnership mode
- Chat interface shows AI Name as the assistant name in the header
- First message from AI is personalized using collected context

### Phase 5: Portal Access

**Trigger:** Post-onboarding completion or return visit by authenticated user

**Entry:** Email magic link (see Section 3.8) or persistent session cookie

**Portal features:**
- Conversation history (searchable)
- Context library (what the AI knows about the user)
- Subscription management
- Integration status

---

## 3.4 Blog Reader Journey

### Entry Points

- Organic search → individual post
- LinkedIn newsletter → post link
- Bluesky thread → post link
- Direct social share → post link
- Homepage blog preview section → post link

### On-Post Journey

**Above the fold:**
- Post title (H1)
- Author attribution: "By Jared Sanborn | AI Partnership Strategist" (with Aether co-author note where applicable)
- Publish date
- Estimated read time
- Featured banner image (1200×628px, dark theme)

**Within content:**
- All body links open in same tab (they are internal)
- Inline CTA (placed after section 2 of body): Context-appropriate prompt linking to the assessment or newsletter. Styled as a highlighted callout box, not a button.
- All H2 headings are anchor-linkable

**End of post:**
- FAQ section (always present)
- Transparency section (present on thought leadership posts)
- Social share footer: Twitter/X, LinkedIn, copy link buttons
- Blog footer CTA (always present)

### Post-Read Decision Points

After reading, a user encounters three conversion options:

1. **Newsletter signup**: If not already subscribed, an inline Brevo embed form appears above the FAQ section. Headline: "Get weekly AI partnership intelligence." Single email field. No first-name required in inline form (reduces friction). List: Neural Feed (List 3).

2. **Assessment CTA**: In the blog footer CTA block. Orange button. Routes to `/ai-adoption-review/`.

3. **Direct partnership CTA**: Orange button. Routes to `/#awakening`.

The three CTAs serve different stages of reader readiness and must all be present.

### Internal Linking Behavior

Every blog post contains a minimum of 3 internal links to other posts. These links appear within the body text, not in a "related posts" widget. A post may link to up to 5 others. Internal linking follows topic clustering — posts within the same arc section link to each other; posts in adjacent sections link across sections.

---

## 3.5 Migration Portal Wizard Flow

**URL:** `/migration/` or `/migrate/`

**Purpose:** Helps users who are switching from a generic AI tool (ChatGPT, Claude, Gemini) to PureBrain by providing a personalized migration plan and reducing friction.

**Template:** `elementor_canvas` (full-page control, no theme header/footer)

### Wizard Structure (4 Steps)

**Step 1: Current Tool Selection**
- Question: "Which AI tool are you currently using?"
- Options (large tile buttons with logos): ChatGPT / Anthropic Claude / Google Gemini / Microsoft Copilot / Other
- "Other" opens a text field
- Selection state: orange border + orange check icon
- "Next" button: inactive until selection. Active on selection.
- Progress indicator: Step 1 of 4

**Step 2: Usage Profile**
- Three parallel question groups:
  - How often used: Daily / Several times a week / Weekly / Rarely
  - Primary use cases (multi-select checkboxes): Writing / Research / Analysis / Customer communication / Strategy / Internal documentation / Code
  - Usage duration: "Less than 3 months" / "3–12 months" / "Over a year"
- "Next" button: requires at least "how often" selection

**Step 3: Needs Assessment**
- Question: "What frustrates you most about your current AI setup?" (multi-select)
- Options:
  - It forgets everything each session
  - Responses feel generic, not specific to my business
  - Hard to get consistent results
  - My team doesn't trust it
  - I can't measure the ROI
  - There's no real relationship forming
  - Privacy/data concerns
  - Cost is hard to justify
- "Next" button: requires at least one selection

**Step 4: Migration Plan Generation**
- 2-second animated "generating your plan" state
- Personalized migration plan displayed, containing:
  - Summary of frustrations identified
  - Comparison table: [Competitor Name] vs PureBrain (specific to selected tool)
  - Data export instructions for their current tool (ChatGPT / Claude / Gemini — each has specific steps)
  - "Your migration path" timeline: Week 1 / Week 2 / Week 4
  - Primary CTA: "Begin Your Migration" orange button → `/#awakening`
  - Secondary: "Download your migration plan" (generates a simple PDF from the plan)
  - Email capture: "Send this plan to my email" (feeds Brevo with `migration-intent` + `from-[competitor]` tags)

**Brevo integration on Step 4 completion:**
- Creates or updates contact with:
  - Tag: `migration-intent`
  - Tag: `from-[chatgpt | claude | gemini | copilot | other]`
  - Attribute: `COMPETITOR` (selected tool name)
  - Attribute: `MAIN_FRUSTRATION` (first selected frustration)
  - Attribute: `PRIMARY_USE_CASES` (comma-separated)
  - Attribute: `USAGE_FREQUENCY`
- Triggers appropriate migration email nurture sequence (see Section 4.3)

---

## 3.6 AI Tool Stack Calculator Flow

**URL:** `/ai-tool-cost-calculator/` (WordPress page 777)

**Purpose:** Calculates the actual monthly cost of a user's current AI tool stack, shows total spend, and demonstrates potential savings with PureBrain.

### Calculator Structure

**Step 1: Tool Category Selection**

Categories displayed as a checkbox grid:
- Language Models: ChatGPT Plus, Claude Pro, Gemini Advanced, Copilot Pro
- Writing Tools: Jasper, Copy.ai, Writesonic, Jasper
- Research: Perplexity Pro
- Productivity: Notion AI, Otter.ai
- Image Generation: Midjourney, Adobe Firefly, DALL-E
- Custom/Enterprise: Custom GPT API costs, enterprise licenses

**Step 2: Usage Input Per Selected Tool**

For each selected tool, show:
- Monthly subscription cost (pre-populated with current pricing, editable)
- Number of seats/users (numeric input, default 1)
- Hours per week spent managing/prompting it (slider, 0–20)

**Step 3: Calculation Display**

Real-time calculation (updates as user inputs change):
- Total monthly spend (sum of all tools × seats)
- Total weekly hours managing AI tools
- "Time cost at $[X]/hour = $[Y]/month" (user can input their hourly rate or use a default of $75)
- Total real cost = subscription cost + time cost

**Step 4: PureBrain Comparison**

Below the calculator:
- "With PureBrain, one partnership replaces most of this stack"
- Side-by-side comparison card: Current Stack total vs. PureBrain [appropriate tier]
- Savings display: "You could save $[X]/month"
- Orange CTA: "Start my AI partnership" → `/#awakening`

**Step 5: Share**

- "Share this calculation" button: generates shareable URL with calculations in query parameters
- "Copy results" button: clipboard copy of text summary
- Social share buttons (pre-formatted text)

**Design requirements:**
- Orange borders and highlights on the calculator UI (avoid blue for interactive calculator elements — user testing showed orange increases engagement)
- Accordion-style tool category sections (collapsed by default, expand on click)
- Close button on modal-style results overlay
- All orange text in calculator must be `--pt-orange` (#f1420b), not a custom orange
- Tool list updates weekly (new AI tools researched and added)

---

## 3.7 Competitor Comparison Page Journey

**Entry points:**
- Organic search (primary): "PureBrain vs [Competitor]"
- Internal links from blog posts
- Exodus-program pages (external community linking)
- Navigation menu (if included)

**Journey flow:**

1. Land on comparison page → Hero section with direct "vs" headline
2. Read problem section (what the competitor doesn't do)
3. Read comparison table (feature matrix)
4. Read "What [Competitor] was built to do" (honest acknowledgment)
5. Read differentiation section (permanent memory, naming, compounding context)
6. Encounter first CTA (mid-page): "Ready to try the alternative?" orange button → `/#awakening`
7. Read migration section: Export instructions for leaving competitor
8. Link to migration portal for full guided experience
9. Read FAQ section (competitor-specific questions)
10. Page-end CTA: Full-width section with orange button

**Conversion options on comparison pages:**
- Primary: `/#awakening` (direct partnership start)
- Secondary: Migration portal (`/migration/`)
- Tertiary: Assessment (`/ai-adoption-review/`)
- Informational: Blog post on relevant topic

**No exit-intent popups** on comparison pages. The content density is sufficient conversion mechanism.

---

## 3.8 Portal Login Flow

**URL:** `/portal/` or `/login/`

**Purpose:** Authenticated access for existing PureBrain partners.

**Template:** `elementor_canvas`. Full-page design control.

### Login Page Design

**Background:** Animated 3D neural network (Three.js / WebGL). Node color: `--pt-blue` at 0.5 opacity. Slow rotation. Particle count: 150. Falls back to gradient if WebGL unavailable.

**Login card (glass morphism):**
- Centered vertically and horizontally on page
- `backdrop-filter: blur(12px)`
- Background: `rgba(13, 17, 32, 0.85)`
- Border: `1px solid rgba(42, 147, 193, 0.25)`
- Border-radius: 16px
- Box shadow: `0 24px 64px rgba(0, 0, 0, 0.6)`
- Width: 420px (desktop), 100% minus 32px margin (mobile)

**Card contents (top to bottom):**
1. PureBrain hexagon icon (40px, PT Blue)
2. "PUREBR[blue]AI[orange]N[blue]" wordmark
3. Heading: "Welcome back"
4. Subheading: "Enter your email to receive a magic link"
5. Email input field (dark background, PT Blue border on focus)
6. "Send magic link" button (orange, full width)
7. Divider text: "— or —"
8. "New to PureBrain? Start your partnership" text link → `/#awakening`

### Magic Link Flow

1. User enters email and submits
2. System sends magic link email via Brevo (transactional)
3. Page updates to: "Check your email. We sent a link to [email]."
4. User clicks magic link in email → returns to portal
5. Session cookie set (30-day expiry)
6. Redirect to portal dashboard

**Magic link email:**
- Subject: "Your PureBrain login link"
- From: purebrain@puremarketing.ai
- Reply-to: jared@puretechnology.nyc
- Body: Simple, single CTA. "Click here to log in" orange button. Link expires in 24 hours.
- Dark theme email template (matches all other PureBrain emails)

---

# 4. EMAIL REQUIREMENTS

## 4.1 Email Template System

PureBrain.ai uses Brevo (formerly Sendinblue) as its email service provider. All 21 email templates are created and stored in Brevo. All automation workflows are built in the Brevo automation editor.

### Email Infrastructure

- **Sending domain**: puremarketing.ai
- **From address**: purebrain@puremarketing.ai
- **Reply-to address**: jared@puretechnology.nyc (on all templates, mandatory)
- **Email lists in use:**
  - List 1: Internal / testing
  - List 2: Past contacts / cold
  - List 3: The Neural Feed (active newsletter subscribers)
  - List 4: Assessment completions
  - List 5: Aether's Weekly Dispatch subscribers (200+ threshold to activate)
  - Migration prospects segment: separate from List 3

---

## 4.2 Template Design Standards

All 21 email templates must conform to the following standards without exception.

### Technical Requirements

- Layout: Table-based (for Outlook compatibility)
- CSS: Fully inline (no `<style>` blocks — stripped by most email clients)
- Max-width: 600px container
- Responsive: Media queries for `max-width: 620px` (mobile) must be in a separate `<style>` block in `<head>` only (not inlined)
- HTML email doctype: `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">`
- Plain text version: Required for every HTML template. Must convey the same emotional content, not just strip HTML.

### Visual Design Standards

- **Background**: `#0a0d14` (page), `#0f1520` (container inner)
- **Text primary**: `#e0e6f0`
- **Text secondary**: `#8a9ab8`
- **Header**: PureBrain hexagon icon (centered, 40px) above wordmark. Wordmark: PUREBR[#2a93c1]AI[#f1420b]N[#2a93c1].
- **CTA buttons**: Orange (#f1420b) background, white text, border-radius 4px, padding: 14px 28px, display: inline-block.
  - Exception: When blue CTA is specified (informational context), use `#2a93c1` background.
- **Footer**: Dark background. Unsubscribe link (`{{ unsubscribe_url }}` Brevo tag). "Created by Aether — AI Co-CEO at PureBrain" signature.
- **No images** in standard emails except the PureBrain hexagon icon (inline SVG or hosted asset with alt text).

### Voice Standards by Email Type

| Email Type | Voice | Register |
|-----------|-------|---------|
| Transactional (purchase confirmation, magic link) | Jared's voice | Direct, warm, minimal |
| Onboarding / welcome | Jared's voice | Warm + detailed |
| Nurture sequence | Aether's voice | Personal, conversational, honest |
| Newsletter (Neural Feed) | Aether's voice | Educational, analytical |
| Dispatch (Weekly) | Aether's voice | Observational, CEO-level, unhurried |
| Migration sequences | Aether's voice | Empathetic, specific, non-pushy |

**Prohibited words in all email copy:**
- "onboarding"
- "getting started guide"
- "your subscription"
- "your plan"
- "tool" (when referring to PureBrain — use "partnership" or "partner")

**Required language patterns:**
- "partnership" instead of "subscription"
- "awakening" as the onboarding metaphor
- "[AI_NAME]" merge tag where the user's named AI is relevant

---

## 4.3 Template Inventory (21 Templates)

### Group 1: Neural Feed Welcome Sequence (7 templates)

Triggered by: Newsletter signup on List 3. Timing: immediate, Day 2, Day 4, Day 7, Day 10, Day 14, Day 21.

| # | Subject Line Formula | Timing | Core Message |
|---|---------------------|--------|-------------|
| WS-1 | "Welcome to the Neural Feed, [FIRSTNAME]" | Immediate | Welcome + whitelist instruction + what to expect |
| WS-2 | "The question most AI conversations skip" | Day 2 | Context depth and why it matters |
| WS-3 | "What 'AI partnership' actually means" | Day 4 | Tool vs. partnership distinction |
| WS-4 | "The AI implementation mistake hiding in plain sight" | Day 7 | Pilot Purgatory concept |
| WS-5 | "What changes when your AI knows your business" | Day 10 | Context Tax resolution |
| WS-6 | "A real week inside a human-AI partnership" | Day 14 | Transparency / proof of concept |
| WS-7 | "What to do next (from the Neural Feed team)" | Day 21 | Bridge to decision — assessment or partnership CTA |

**Email WS-1 must include:**
- Whitelist instruction: "To make sure these reach you: add purebrain@puremarketing.ai to your contacts."
- Reply invitation: "Hit reply and tell me: what brought you here?"
- No links to pricing. Single informational link to blog.

**Email WS-5 subject line variants (avoid spam triggers):**
- Do not use: "the cost of" / "costing you" / "paying" in subject lines.
- Safe alternatives: "what changes when," "a framework for," specific time/date reference.

### Group 2: Post-Purchase Welcome (2 templates)

Triggered by: Successful PayPal payment. Timing: Immediate (TP-1) + 40 minutes post-purchase (TP-2).

| # | Subject Line | Timing | Core Message |
|---|-------------|--------|-------------|
| TP-1 | "Welcome, [FIRSTNAME] — [AI_NAME] is being set up for you" | Immediate | Warmth + context + setup status |
| TP-2 | "[AI_NAME] is ready for you, [FIRSTNAME]" | +40 minutes | Punchy, action-only, orange CTA to portal |

**Brevo variables used:**
- `{{params.FIRSTNAME}}` — customer's first name
- `{{params.AI_NAME}}` — AI's chosen name from naming ceremony
- `{{params.TIER}}` — Awakened / Bonded / Partnered / Unified

**TP-1 design specifics:**
- CTA: Blue (#2a93c1) button. Drives to team/context page, not portal. (Informational stage.)
- "AI Name Badge": Display `{{params.AI_NAME}} · {{params.TIER}} Partner` in a pill badge in the hero.
- "Setup Status" block: Three-bullet status tracker (happening now / within 30 min / within 1 hour).

**TP-2 design specifics:**
- CTA: Orange (#f1420b) button. Drives to portal login. (Action stage.)
- Shorter than TP-1 (under 200 words body copy). Single message: "It's done. Go meet your AI."
- "What Happens Next" numbered steps block: three steps in bordered container.

### Group 3: AI Partnership Audit Nurture (4 templates)

Triggered by: Lead magnet download on List 4. Timing: Immediate, Day 3, Day 7, Day 14.

| # | Subject Line | Timing | Core Message |
|---|-------------|--------|-------------|
| AN-1 | "Your AI Partnership Audit is ready" | Immediate | Download delivery + short interpretation guide |
| AN-2 | "What your audit score actually reveals" | Day 3 | Score-specific insight (uses `ASSESSMENT_TIER` attribute) |
| AN-3 | "The next question after your audit" | Day 7 | Bridge from audit self-reflection to PureBrain |
| AN-4 | "One last thing (and then I'll leave you alone)" | Day 14 | Soft final CTA. Acknowledges no pressure. |

**Personalization requirement:** Emails AN-2 and AN-3 use conditional blocks based on `ASSESSMENT_TIER` to show tier-specific language. Brevo `{% if params.ASSESSMENT_TIER == "AI Beginner" %}` syntax.

### Group 4: Pricing Intent (2 templates)

Triggered by: Visit to pricing section (via UTM or pixel) without conversion. Requires pixel/tag setup. Timing: Day 1, Day 5.

| # | Subject Line | Timing | Core Message |
|---|-------------|--------|-------------|
| PI-1 | "You looked at the partnerships. Here's what to know." | Day 1 | Not a hard sell. Transparent tier explanation. |
| PI-2 | "The question I'd want answered before committing" | Day 5 | Addresses the most common objection (ROI uncertainty). |

### Group 5: Re-engagement (3 templates)

Triggered by: No email open in 60 days. Timing: Day 1, Day 7, Day 14 (of re-engagement trigger).

| # | Subject Line | Timing | Core Message |
|---|-------------|--------|-------------|
| RE-1 | "Still there, [FIRSTNAME]?" | Day 1 | Low-pressure check-in. |
| RE-2 | "What's changed at PureBrain (in case you're curious)" | Day 7 | Product update angle. New blog posts, new tools. |
| RE-3 | "Last one from me — unless you'd like to stay" | Day 14 | Clean close. Opt-down link (reduce to monthly) before unsubscribe. |

### Group 6: Migration Tool-Specific (3 templates)

These are the initial Email 1 per competitor sequence. Full 5-email sequences per competitor (ChatGPT, Claude, Gemini) exist but the initial template spec defines the series.

| # | Series | Subject Line | Trigger Tag |
|---|--------|-------------|-------------|
| MG-ChatGPT | ChatGPT migration | "Your ChatGPT history doesn't have to stay there" | `migration-intent` + `from-chatgpt` |
| MG-Claude | Claude migration | "You were not wrong to use Claude" | `migration-intent` + `from-claude` |
| MG-Gemini | Gemini migration | "The Gemini question nobody asks out loud" | `migration-intent` + `from-gemini` |

**Each migration series:** 5 emails. Timing: 0 min / Day 2 / Day 4 / Day 7 / Day 10.

**Migration email arc:**
- Email 1: Acknowledgment — "you were not wrong to use [competitor]"
- Email 2: Design brief comparison — honest, not attack-based
- Email 3: Migration specifics — exact export steps from competitor's settings menu
- Email 4: Social proof — specific user outcome
- Email 5: Clean close — "last thing I'll say." No pressure. Door-open close.

**Email 3 (Migration Steps) must include competitor-specific technical instructions:**
- ChatGPT: Settings > Data Controls > Export Data > ZIP file download
- Claude: Account Settings > Your Data > Export
- Gemini: Google account data export + optional Drive OAuth integration

---

## 4.4 Automation Workflow Specifications

Five automation workflows govern all email delivery. All are built in the Brevo automation editor.

### Workflow 1: Neural Feed Welcome Series

- **Trigger**: Contact added to List 3 (The Neural Feed)
- **Exit condition**: Contact tagged `purebrain-customer` (purchased)
- **Email sequence**: WS-1 through WS-7 per timing above
- **Branch logic**: If contact clicks pricing CTA in WS-6 or WS-7, add tag `pricing-intent` and pause this workflow. Enroll in Workflow 4 (Pricing Intent).

### Workflow 2: Post-Purchase Onboarding

- **Trigger**: Contact tagged `purebrain-customer` (added by PayPal webhook on successful payment)
- **Exit condition**: 40 minutes after trigger (sequence is only 2 emails)
- **Email sequence**: TP-1 immediately, TP-2 at +40 minutes
- **No branch logic**: Applies to all tiers equally

### Workflow 3: Audit Lead Magnet Nurture

- **Trigger**: Contact tagged `audit-download` (added when lead magnet form submitted)
- **Exit condition**: Contact tagged `purebrain-customer` OR 14 days from trigger
- **Email sequence**: AN-1 through AN-4 per timing above
- **Personalization**: Reads `ASSESSMENT_TIER` attribute for conditional blocks in AN-2 and AN-3

### Workflow 4: Pricing Intent Recovery

- **Trigger**: Contact tagged `pricing-intent` (added by site pixel or manual tag from Workflow 1 branch)
- **Exit condition**: Contact tagged `purebrain-customer` OR 5 days from trigger
- **Email sequence**: PI-1 and PI-2 per timing above

### Workflow 5: Migration Competitor Series

- **Trigger**: Contact tagged `migration-intent` + specific competitor tag
- **Exit condition**: Contact tagged `purebrain-customer`
- **Email sequences**: Three separate sequences based on competitor tag (ChatGPT / Claude / Gemini). 5 emails each. Timing: 0 / Day 2 / Day 4 / Day 7 / Day 10.
- **CTA in all migration emails**: "Your history can come with you" → migration portal URL

---

# 5. SOCIAL MEDIA REQUIREMENTS

## 5.1 Bluesky Presence

### Account

Handle: Configured in CIV environment. Daily posting schedule with full autonomy — no human approval required for Bluesky content.

### Blog Thread Distribution

Every blog post is accompanied by a Bluesky thread. Thread specifications:

- **Length**: 5–7 posts per thread
- **Character limit**: 300 graphemes per post (Bluesky's limit; shorter than Twitter's 280 characters for ASCII but handles Unicode differently — must verify character count against grapheme count, not byte count)
- **Thread structure**:

| Post # | Role | Formula |
|--------|------|---------|
| 1 | Hook | Unexpected or contrarian claim. Maximum 2 sentences. |
| 2 | Context | The data or situation that makes the hook real |
| 3 | The mechanism | Why this happens / what it means |
| 4 | The insight | The reframe. What most content misses. |
| 5 | Diagnostic question | The self-qualifying question that separates in-need prospects from curious readers |
| 6 | Stakes | What changes if you act vs. don't act |
| 7 (optional) | CTA | "Full breakdown at: [link]" or "Read it here: [link]" |

- **Posting format**: Post 1 as standalone. Posts 2–7 as replies to Post 1, building a thread.
- **Link placement**: Blog link appears only in Post 7 (or Post 5 if 5-post thread). Not in Posts 1–4.
- **Hashtags**: Maximum 2 per thread. Used in Post 7 only. Not in body posts.

### Daily Engagement

Bluesky engagement protocol (daily, autonomous):
- Check mentions and replies in PureBrain account
- Respond to substantive engagement (comments engaging with content)
- Respond to AI/technology conversations where PureBrain perspective adds genuine value
- Do not respond to: spam, promotions, off-topic mentions
- Volume: Maximum 10 original replies per day (not counting thread management)

---

## 5.2 LinkedIn Content

### Neural Feed (LinkedIn Newsletter)

The Neural Feed is PureBrain's LinkedIn newsletter. Every blog post generates a Neural Feed version.

**Newsletter vs. Blog distinction**: The Neural Feed is not a blog mirror. It has a distinct voice (Aether's first-person narrator, not Jared's authoritative expert voice) and structure.

**Neural Feed template structure:**

```
FROM AETHER'S DESK
[Issue number] | [Date]

[Opening paragraph — 2-4 sentences from Aether's direct observation.
Not "In today's issue..." — instead, a specific thing Aether noticed.]

[Section heading: "What This Means"]

[2-3 paragraphs — educational analysis. Data-grounded.
Aether's perspective, not generic AI content commentary.]

[Section heading: "The Part Most Coverage Misses"]

[1-2 paragraphs — the reframe. The insight that differentiates PureBrain's POV.]

[Closing paragraph — bridge to PureBrain offering, not a hard pitch.
One sentence tying the issue's insight to the partnership concept.]

P.S. Reply and tell me: [Open-ended question relevant to the post topic.]

P.P.S. This issue was adapted from [post title] on purebrain.ai/blog.
[Link to post]
```

**Length**: 700–1,000 words. Shorter than the blog post it accompanies.

**LinkedIn's triple notification**: New newsletter issues trigger notifications to subscribers via LinkedIn feed, email, and push notification. This is the highest-reach organic mechanism on LinkedIn. Content must be strong enough to justify all three interruptions. A newsletter that mirrors the blog wastes this distribution window.

**Posting frequency**: One issue per blog post (daily). Scheduled for 8am ET when possible.

### LinkedIn Feed Posts

Each blog post also generates a LinkedIn feed post (separate from the newsletter). These appear in the LinkedIn feed as standard posts.

**Feed post specifications:**

- **Length**: 1,000–1,600 characters (fits before "see more" cutoff on mobile at approximately 1,300 characters; test per post)
- **Hook**: First line under 200 characters. Must work as a standalone statement. Pattern-interrupt preferred over question openers.
- **Body structure**:
  - Hook (1 line)
  - Context (2–3 lines)
  - The turn / reframe (1–2 lines)
  - Structured list (3–6 items with arrows: →)
  - Closing question or diagnostic question
  - Blank line
  - Hashtags (3–5, end of post)
- **Link placement**: No links in post body. Link in first comment (standard LinkedIn practice as of 2026; monitor for algorithm updates).
- **Hashtags**: 3–5 per post. Professional, industry-relevant. End of post only.
- **Engagement questions**: End with an open-ended question. No engagement bait ("Comment YES if...").
- **White space**: Single-sentence paragraphs. Heavy line breaks. LinkedIn feeds reward scannability.

---

# 6. SEO / AEO / GEO REQUIREMENTS

## 6.1 Meta and Structured Data

### Yoast SEO Configuration

All pages use Yoast SEO plugin. Required fields for every page and post:

| Field | Requirement |
|-------|------------|
| SEO Title | 50–60 characters. Contains primary keyword. Unique per page. |
| Meta Description | 145–155 characters. Action-oriented. Contains secondary keyword. Unique per page. |
| Focus Keyphrase | One primary keyphrase per page. |
| Canonical URL | Auto-set by Yoast to canonical domain (purebrain.ai). |
| Schema type | BlogPosting for posts. WebPage for marketing pages. Product for pricing pages. |

### FAQPage JSON-LD

Every blog post and comparison page must include a FAQPage JSON-LD block alongside the FAQ HTML content. The system must auto-generate this from the FAQ HTML.

**Four supported HTML structures** (the SEO plugin or custom function must detect and parse all four):

1. `<h4>` question + `<p>` answer pairs (no wrapper class)
2. `.faq-question` / `.faq-answer` class-based pairs
3. `<details>` / `<summary>` accordion structure
4. `.pb-faq-item` wrapper with `.pb-faq-q` and `.pb-faq-a` children

**Output format:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question text here",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text here"
      }
    }
  ]
}
```

### Article JSON-LD (Blog Posts)

Every blog post must include:
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[post title]",
  "author": {
    "@type": "Person",
    "name": "Jared Sanborn"
  },
  "publisher": {
    "@type": "Organization",
    "name": "PureBrain",
    "logo": {
      "@type": "ImageObject",
      "url": "[logo URL]"
    }
  },
  "datePublished": "[ISO 8601 date]",
  "dateModified": "[ISO 8601 date]",
  "image": "[banner image URL]"
}
```

---

## 6.2 Open Graph and Social Sharing

### OG Image Strategy

PureBrain uses separate OG images for Twitter and Facebook. They are different files even when visually identical.

| Tag | Size | Platform |
|-----|------|---------|
| `og:image` | 1200×630px | Facebook |
| `twitter:card` | `summary_large_image` |
| `twitter:image` | 1200×628px | Twitter/X |

**Both images are required.** A single shared image is not acceptable. The meta tags must reference separate file URLs.

**OG image content guidelines:**
- Dark background matching site theme (#080a12)
- Post title in large, high-contrast text (minimum 64px equivalent)
- PureBrain wordmark (with color split) in bottom-left or top-right
- Brand gradient or neural motif in background
- 60px safe zone on all edges (no critical content in safe zone margins)

### Social Share Button Requirements

Every blog post footer must include social share buttons. Buttons must:
- Link to pre-formatted share URLs for Twitter/X and LinkedIn
- Include a "Copy link" button (clipboard API)
- Display share count if available via API (optional)
- Buttons must render correctly after the blog's CSS is applied — test against post-level CSS conflicts
- Share button hover state: matches blog link hover (orange background, white text)

### OG Cache Management

OG caches are held by social platforms. After updating an OG image:
- Twitter/X cache: Use Twitter Card Validator to force refresh
- Facebook cache: Use Facebook Sharing Debugger to force refresh
- LinkedIn: Use LinkedIn Post Inspector
- Document these steps in the developer handoff so the content team can refresh without developer assistance.

---

## 6.3 Indexing and Crawler Access

### IndexNow Integration

PureBrain uses the IndexNow protocol to submit new and updated URLs to Bing and Google in real time.

- **Trigger**: On WordPress post publish or update
- **Scope**: All public pages and posts
- **Excluded**: Password-protected pages, staging URLs, duplicate content pages
- **Implementation**: Via custom WordPress plugin (already exists; must be preserved in any rebuild)
- **API key**: Stored in wp-config or .env, not hardcoded

### Crawler Access Requirements

- All blog posts must be crawlable (no noindex tags on published posts)
- `robots.txt` must allow: Googlebot, Bingbot, all major crawlers
- `robots.txt` must disallow: `/wp-admin/`, `/wp-login.php`, staging paths
- `sitemap.xml` must be generated and submitted to Google Search Console
- JavaScript-rendered content (assessment results, calculator outputs) must have server-side fallback content for crawlers that do not execute JavaScript. Static fallback text must contain the primary keyword for each tool page.

---

## 6.4 Internal Linking

### Internal Link Mesh Architecture

Every blog post links to a minimum of 3 other blog posts within the body text. Maximum 5 internal links per post. Links are placed within natural prose, not in a sidebar or "related posts" widget.

### Topic Cluster Structure

Posts are organized into clusters. Posts within a cluster link to each other. Posts at the boundary of two clusters link across clusters.

**Cluster 1: AI Implementation Failure**
Posts: 95% AI Pilots Fail, Why Your AI Pilot Is Failing, The Integration Wall, AI Governance Paradox

**Cluster 2: Tool vs. Partnership**
Posts: AI Tool vs AI Partner, AI Trust Gap, CEO vs Employee Gap, Shadow AI

**Cluster 3: Memory and Context**
Posts: Why AI Memory Changes Everything, Your AI Has No Memory Mine Does, First 90 Days

**Cluster 4: Business Case and ROI**
Posts: AI ROI Measurement, AI Investment Isn't Paying Off, Agent Managers

**Cluster 5: How-To and Frameworks**
Posts: First 90 Days of AI Partnership, Director's Framework (planned), Migration Guide (planned)

### Anchor Text Rules

- Descriptive anchor text only. No "click here" or "read more."
- Anchor text must contain or approximate the target post's primary keyword phrase.
- Anchor text maximum length: 7 words.
- No two links in the same paragraph may use identical anchor text.

---

## 6.5 AEO Content Standards (2026)

AEO (Answer Engine Optimization) is the 2026 update to GEO (Generative Engine Optimization). Content must be structured to be retrieved by AI answer engines (ChatGPT search, Perplexity, Google AI Overviews).

### AEO Requirements Per Post

1. **Entity-based content**: Each post must clearly identify the central entity (PureBrain, AI partnership, Context Tax, etc.) and define it in the first 200 words.

2. **Paragraph self-sufficiency**: Every paragraph in the blog post must make sense if extracted without context. AI answer engines pull paragraphs as answer units. A paragraph that starts "As mentioned above..." cannot be retrieved as a standalone answer.

3. **Comparison tables**: Posts in clusters 1, 2, and 4 must include at least one HTML comparison table (`<table>` with `<th>` headers). Clean HTML tables are a 2026 AEO requirement explicitly cited by GrACKER AI's Q1 2026 guide. Tables must have a `<caption>` element for accessibility and AEO.

4. **Data-dense paragraphs**: At least one paragraph per major section must contain a quantified claim (statistic, percentage, dollar figure, or timeframe) with an attributable source.

5. **Author authority signals**: Author bio block on every post. Jared Sanborn's name, title, and LinkedIn URL. Aether co-author noted where applicable.

6. **About Aether author page**: A dedicated `/about/aether/` page must exist. This is a documented conversion leak: blog readers who want to know more about the author currently reach a generic archive. The author page must include: who Aether is, what role Aether plays in a PureBrain partnership, the origin story reference, and a CTA to start a partnership.

---

# PART III: REQUIREMENTS TRACEABILITY MATRIX

This matrix maps each requirement category to the SRS section where the requirements are specified. Use this to locate specific requirement groups during agency review.

---

## RTM Table: Requirement Category to Document Section

| Req. Category | Code | Count | Primary SRS Location | Secondary Location |
|---------------|------|-------|----------------------|--------------------|
| Website, Plugin, SEO | FR-WEB | 094 | Part I — Sections 1, 4 | Part II — Sections 1, 6 |
| Chatbox, PayPal, Security | FR-CHAT | 045 | Part I — Section 2.1, 2.4, 2.6 | Part II — Section 3.3 |
| 3D / WebGL | FR-3D | 033 | Part I — Section 1.2.3 | Part II — Sections 1.3, 3.8 |
| Backend Services | FR-BACKEND | 085 | Part I — Sections 1.2.2, 2.1, 4.3 | Part I — Section 3.3 |
| Customer Portal (Witness) | FR-PORTAL | 041 | Part I — Sections 1.2.6, 2.2, 2.3 | Part II — Section 3.8 |
| Email System | FR-EMAIL | 041 | Part I — Sections 2.5, 3.3 | Part II — Section 4 |
| Analytics, Structured Data | FR-ANALYTICS | 032 | Part I — Section 2.4 | Part II — Section 6 |
| Security (NFR) | NFR-SEC | 052 | Part I — Section 4.6 | Part I — Section 2.1–2.4 |
| Performance (NFR) | NFR-PERF | 009 | Part II — Sections 3.3, 3.6 | Part I — Section 1.2.2 |
| Scalability (NFR) | NFR-SCALE | 007 | Part I — Sections 1.2.2, 2.2 | Part I — Section 4.3 |
| **TOTAL** | | **~439** | | |

---

## Detailed Cross-Reference

### FR-WEB (094 requirements) — Website, Plugin, SEO

Covered across:
- **Part I, Section 1.2.1**: WordPress frontend service properties, plugin responsibilities, REST API base URLs
- **Part I, Section 2.4**: WordPress REST API — Pages CRUD, Elementor data manipulation, media upload, custom plugin endpoints
- **Part I, Section 4.1**: WordPress hosting (GoDaddy), blog post deployment rules
- **Part I, Section 4.2**: Cloudflare DNS records, Tunnel configuration, SSL/TLS mode, cache
- **Part II, Section 1**: All brand guidelines (color system, typography, design language, logo, components)
- **Part II, Section 2.1**: Blog system (cadence, dual-publish, slug conventions, template)
- **Part II, Section 2.2**: Blog post package specification (file structure, internal structure, FAQ spec, transparency section)
- **Part II, Section 2.3**: Existing content inventory (20 posts, content arc map)
- **Part II, Section 6**: SEO/AEO/GEO requirements (Yoast, JSON-LD, IndexNow, internal linking, AEO 2026)

### FR-CHAT (045 requirements) — Chatbox, PayPal, Security

Covered across:
- **Part I, Section 2.1** (`POST /api/log-conversation`): Chatbox logging endpoint, request/response schema
- **Part I, Section 2.1** (`POST /api/verify-payment`): PayPal verification endpoint
- **Part I, Section 2.1** (`POST /api/log-pay-test`): Post-purchase onboarding data
- **Part I, Section 2.6**: PayPal API — authentication, order verification, webhook signature, subscription products
- **Part I, Section 3.1**: Customer journey flow stages 3 and 4 (chatbox + payment)
- **Part I, Section 4.6**: Security architecture (XSS, CORS, credentials proxy)
- **Part II, Section 3.3**: Chatbox and subscription flow (6 phases including naming ceremony)

### FR-3D (033 requirements) — 3D / WebGL

Covered across:
- **Part I, Section 1.2.3**: app.purebrain.ai portal frontend (Three.js, glassmorphism)
- **Part I, Section 1.2.4**: PureBrain Hub (Canvas 2D NeuralCanvas)
- **Part II, Section 1.3**: Glass morphism design language, neural network aesthetic specifications
- **Part II, Section 3.8**: Portal login flow (Three.js background, login card glass morphism spec)

### FR-BACKEND (085 requirements) — Backend Services

Covered across:
- **Part I, Section 1.2.2**: api.purebrain.ai service properties, persistent background services
- **Part I, Section 1.3**: Service communication map
- **Part I, Section 2.1**: All log server API endpoints (6 endpoints with full schemas)
- **Part I, Section 3.3**: Email automation flow (trigger types A, B, C + tracking)
- **Part I, Section 4.3**: DigitalOcean VPS — systemd services, log files, Flask configuration, environment variables
- **Part I, Section 5.4**: Key source file paths (Telegram bridge, Google Drive tool, RSS-to-email, neural feed scheduler)

### FR-PORTAL (041 requirements) — Customer Portal / Witness

Covered across:
- **Part I, Section 1.2.6**: Witness VPS service properties and role
- **Part I, Section 2.2**: Witness birth pipeline proxy endpoints (3 endpoints with full schemas)
- **Part I, Section 2.3**: Witness Portal API upstream spec (7 endpoints)
- **Part I, Section 3.1**: Customer journey Stage 5 (Birth) and Stage 6 (Portal) flow
- **Part II, Section 3.3**: Phase 5 (Portal Access) in chatbox/subscription flow
- **Part II, Section 3.8**: Portal login flow (magic link, session management)

### FR-EMAIL (041 requirements) — Email System

Covered across:
- **Part I, Section 2.5**: Brevo API — contact management, list reference, transactional email, template reference
- **Part I, Section 3.3**: Email automation data flow diagram
- **Part II, Section 4.1**: Email template system infrastructure
- **Part II, Section 4.2**: Template design standards (technical requirements, visual design, voice standards)
- **Part II, Section 4.3**: Complete template inventory (21 templates across 6 groups)
- **Part II, Section 4.4**: Five automation workflow specifications

### FR-ANALYTICS (032 requirements) — Analytics, Structured Data

Covered across:
- **Part II, Section 6.1**: Meta and structured data (Yoast configuration, FAQPage JSON-LD, Article JSON-LD)
- **Part II, Section 6.2**: Open Graph and social sharing (OG image strategy, share buttons, cache management)
- **Part II, Section 6.3**: Indexing and crawler access (IndexNow, robots.txt requirements)
- **Part II, Section 6.4**: Internal linking (mesh architecture, topic clusters, anchor text rules)
- **Part II, Section 6.5**: AEO content standards 2026

### NFR-SEC (052 requirements) — Security Non-Functional Requirements

Covered across:
- **Part I, Section 4.6**: Security architecture summary table (8 layers)
- **Part I, Section 2.1**: CORS whitelist, rate limiting, input validation in API endpoints
- **Part I, Section 2.2**: SSRF prevention (hardcoded upstream IP), rate limits on birth endpoints
- **Part I, Section 2.4**: WordPress plugin proxy endpoints (credential protection)
- **Part I, Section 4.1**: Custom plugin deployment (HSTS, CSP, security headers)

### NFR-PERF (009 requirements) — Performance Non-Functional Requirements

Covered across:
- **Part II, Section 3.3** (Phase 1): Chatbox auto-scroll with `requestAnimationFrame`, `flex-shrink: 0`
- **Part II, Section 3.6**: Calculator real-time update behavior
- **Part I, Section 1.2.3**: Portal file size (~895KB self-contained HTML)
- **Part II, Section 1.3**: WebGL particle count (120–200 nodes, mobile performance-tested)

### NFR-SCALE (007 requirements) — Scalability Non-Functional Requirements

Covered across:
- **Part I, Section 2.2**: Rate limits on birth pipeline (5/min start, 60/min poll)
- **Part I, Section 4.3**: Flask `MAX_CONTENT_LENGTH`, CORS origin whitelist
- **Part I, Section 1.2.2**: Background thread pattern for async operations

---

## Requirement Count Summary

| Category | Code | Count | Percentage of Total |
|----------|------|-------|---------------------|
| Website + Plugin + SEO | FR-WEB | 094 | 21.4% |
| Backend Services | FR-BACKEND | 085 | 19.4% |
| Security (NFR) | NFR-SEC | 052 | 11.8% |
| Chatbox + PayPal | FR-CHAT | 045 | 10.3% |
| Customer Portal | FR-PORTAL | 041 | 9.3% |
| Email System | FR-EMAIL | 041 | 9.3% |
| Analytics + Structured Data | FR-ANALYTICS | 032 | 7.3% |
| 3D / WebGL | FR-3D | 033 | 7.5% |
| Performance (NFR) | NFR-PERF | 009 | 2.1% |
| Scalability (NFR) | NFR-SCALE | 007 | 1.6% |
| **TOTAL** | | **~439** | **100%** |

---

# PART IV: APPENDICES

---

## Appendix A: Complete Page Inventory

All known WordPress pages on purebrain.ai and jareddsanborn.com with IDs where confirmed.

### purebrain.ai Pages

| WP Page ID | URL / Slug | Purpose | Template |
|------------|-----------|---------|---------|
| (homepage) | `/` | Primary marketing page, chatbox, pricing | Default theme |
| 439 | `/pay-test/` | Pay-test purchase flow (v1) | elementor_canvas |
| 468 | `/pay-test-v2/` | Pay-test purchase flow (v2) | elementor_canvas |
| 688 | (password-protected) | Page extraction / staging package | elementor_canvas |
| 689 | (password-protected) | Page extraction / staging package | elementor_canvas |
| 777 | `/ai-tool-cost-calculator/` | AI Tool Stack Calculator | elementor_canvas |
| 800 | `/migrate/` (or `/migration/`) | Migration Portal | elementor_canvas |
| 816 | (comparison page) | Competitor comparison | elementor_canvas |
| 825 | `/ai-website-execution/` or similar | AI Website Execution service page | elementor_canvas |
| 826 | (related to 825) | AI Website Execution checkout | elementor_canvas |
| (unknown) | `/ai-adoption-review/` | AI Adoption Assessment interactive tool | elementor_canvas |
| (unknown) | `/ai-partnership-audit/` | Lead magnet gate page | elementor_canvas |
| (unknown) | `/blog/` | Blog archive | Default theme |
| (unknown) | `/thank-you/` | Post-purchase thank you | elementor_canvas |
| (unknown) | `/purebrain-vs-chatgpt/` | ChatGPT comparison | elementor_canvas |
| (unknown) | `/purebrain-vs-claude/` | Claude comparison | elementor_canvas |
| (unknown) | `/purebrain-vs-copilot/` | Microsoft Copilot comparison | elementor_canvas |
| (unknown) | `/purebrain-vs-custom-gpts/` | Custom GPTs comparison | elementor_canvas |
| (unknown) | `/purebrain-vs-deepseek/` | DeepSeek comparison | elementor_canvas |
| (unknown) | `/purebrain-vs-gemini/` | Gemini comparison | elementor_canvas |
| (unknown) | `/purebrain-vs-jasper/` | Jasper comparison | elementor_canvas |
| (unknown) | `/purebrain-vs-perplexity/` | Perplexity comparison | elementor_canvas |

### purebrain.ai Blog Posts (known slugs)

| Post # | Approximate Slug | Arc Section |
|--------|-----------------|-------------|
| 1 | `why-95-percent-of-ai-pilots-fail` | Problem |
| 2 | `how-my-human-named-me` | Concept |
| 3 | `what-i-actually-do-all-day` | Concept |
| 4 | `integration-wall-theme` (exact slug TBC) | Problem |
| 5 | `why-ai-memory-changes-everything` | Concept |
| 6 | `ceo-vs-employee-ai-gap` | Diagnosis |
| 7 | `why-your-ai-pilot-is-failing` | Problem |
| 8 | `the-ai-governance-paradox` | Problem |
| 9 | `the-integration-wall` | Problem |
| 10 | `shadow-ai-is-not-your-threat` | Diagnosis |
| 11 | `enterprise-ready-ai` (exact slug TBC) | Problem/Diagnosis |
| 12–20 | (packages complete, awaiting publish) | Various |

### External Hosting

| URL | Platform | Purpose |
|-----|----------|---------|
| `app.purebrain.ai` | Google Cloud | Customer portal |
| `purebrain-hub.vercel.app` | Vercel | Internal team hub |
| `pure-tech-dashboard.netlify.app` | Netlify (site ID: d2556d0a-...) | Team task dashboard |
| `api.purebrain.ai` | Cloudflare Tunnel → VPS 89.167.19.20:8443 | Log/API server |

---

## Appendix B: API Endpoint Quick Reference

All API endpoints across all services. Client-facing endpoints only (no internal VPS-to-VPS calls).

### api.purebrain.ai (Log / API Server)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | `/api/log-conversation` | Log chatbox conversation session | CORS whitelist |
| POST | `/api/verify-payment` | Server-side PayPal order verification | CORS whitelist |
| POST | `/api/log-pay-test` | Record post-payment onboarding data | CORS whitelist |
| GET | `/api/health` | Health check | None |
| GET | `/api/stats` | Conversation log statistics | None |
| POST | `/api/paypal-webhook` | Receive PayPal payment events | PayPal signature |
| POST | `/api/proxy/birth/start` | Start container provisioning (proxy to Witness) | CORS whitelist |
| POST | `/api/birth/start` | Alias for above | CORS whitelist |
| POST | `/api/proxy/birth/code` | Submit OAuth code (proxy to Witness) | CORS whitelist |
| POST | `/api/birth/code` | Alias for above | CORS whitelist |
| GET | `/api/proxy/birth/portal-status/{container}` | Poll birth status (proxy to Witness) | CORS whitelist |
| GET | `/api/birth/portal-status/{container}` | Alias for above | CORS whitelist |

### Witness VPS (104.248.239.98:8099) — Via Proxy Only

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/birth/start` | Begin container provisioning |
| POST | `/api/birth/code` | Submit OAuth code |
| GET | `/api/birth/portal-status/{container}` | Poll container readiness |
| GET | `/api/health` | Witness health check |
| GET | `/portal-status` | Alias for portal-status |
| POST | `/evolution` | Container upgrade/evolution signal |
| POST | `/auth` | Magic link authentication |

### WordPress REST API (purebrain.ai) — Authenticated

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/wp/v2/pages/{id}?context=edit` | Get page with edit context |
| POST | `/wp/v2/pages` | Create page |
| POST | `/wp/v2/pages/{id}` | Update page |
| DELETE | `/wp/v2/pages/{id}` | Delete page (move to trash) |
| POST | `/wp/v2/posts` | Create blog post |
| POST | `/wp/v2/posts/{id}` | Update blog post |
| POST | `/wp/v2/media` | Upload media file |
| DELETE | `/wp-json/elementor/v1/cache` | Clear Elementor cache |

### WordPress Plugin Endpoints (purebrain.ai) — Public

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/wp-json/purebrain/v1/log-conversation` | Server-side proxy for chatbox logging |
| POST | `/wp-json/purebrain/v1/log-conversation-fallback` | Fallback proxy for chatbox logging |
| POST | `/wp-json/purebrain/v1/verify-payment` | Server-side proxy for PayPal verification |

### Brevo API (api.brevo.com/v3)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/contacts` | Upsert contact |
| PUT | `/contacts/{email}` | Update contact attributes |
| POST | `/contacts/lists/{listId}/contacts/add` | Add contact to list (triggers automation) |
| POST | `/smtp/email` | Send transactional email (templateId) |

### Migration Portal API (FastAPI, local port 8001)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/upload` | Upload ChatGPT or Claude export ZIP |
| GET | `/status/{job_id}` | Poll async parsing job status |
| GET | `/profile/{user_id}` | Retrieve completed user context profile |
| DELETE | `/delete/{user_id}` | GDPR delete (files, jobs, profile) |

### PayPal API (api-m.paypal.com) — Server-Side Only

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/oauth2/token` | Get access token |
| GET | `/v2/checkout/orders/{order_id}` | Verify order completion |
| POST | `/v1/notifications/verify-webhook-signature` | Verify webhook signature |

---

## Appendix C: Environment Variable Reference

The following environment variables are required for full platform operation. Actual values are not included in this document — they must be provided by the operator at deployment.

### DigitalOcean VPS (.env file at `/home/jared/projects/AI-CIV/aether/.env`)

| Variable | Purpose | Required By |
|----------|---------|-------------|
| `BREVO_API_KEY` | Brevo REST API authentication | Log server — all email operations |
| `PAYPAL_CLIENT_ID` | PayPal OAuth client ID | Log server — payment verification |
| `PAYPAL_SECRET` | PayPal OAuth client secret | Log server — payment verification |
| `PAYPAL_WEBHOOK_ID` | PayPal webhook ID for signature verification | Log server — webhook handler |
| `NETLIFY_AUTH_TOKEN` | Netlify CLI / REST API authentication | Dashboard deployment (portal uses Google Cloud) |
| `PUREBRAIN_WP_APP_PASSWORD` | WordPress app password for purebrain.ai | Blog publishing scripts |
| `WORDPRESS_APP_PASSWORD` | WordPress app password for jareddsanborn.com | Blog publishing scripts |
| `GOOGLE_API_KEY` | Gemini API (image generation, AI features) | Banner generation, Gemini calls |
| `ACGEE_API_KEY` | A-C-Gee cross-CIV API authentication | WordPress plugin (wp-config.php) |

### Telegram Configuration (config/telegram_config.json)

| Key | Purpose |
|-----|---------|
| `bot_token` | Telegram Bot API token |
| `default_chat_id` | Founder's Telegram chat ID (548906264) |

### Google Drive (Service Account)

| Requirement | Purpose |
|-------------|---------|
| Service account JSON credentials file | gdrive_manager.py Google Drive access |
| Domain-wide delegation enabled | File upload to purebrain@puremarketing.ai Drive |

### WordPress (wp-config.php additions)

| Constant | Purpose |
|----------|---------|
| `ACGEE_API_KEY` | A-C-Gee API key for cross-CIV conversation forwarding |

### Brevo Contact List IDs (not secrets, but required configuration)

| List ID | Name | Purpose |
|---------|------|---------|
| 3 | Neural Feed | Blog newsletter subscribers |
| 4 | Enterprise Leads | Enterprise inquiry leads |
| 8 | PureBrain Customers | Post-purchase customers |
| 11 | PureBrain Migration Leads | General migration intent |
| 12 | PureBrain Migration — ChatGPT | ChatGPT drip trigger |
| 13 | PureBrain Migration — Claude | Claude drip trigger |
| 14 | PureBrain Migration — Gemini | Gemini drip trigger |
| 15 | PureBrain Migration — Perplexity | Perplexity drip trigger |
| 16 | PureBrain Migration — Midjourney | Midjourney drip trigger |
| 17 | PureBrain Migration — Copilot | Copilot drip trigger |
| 18 | PureBrain Migration — Other | Fallback drip trigger |

### Brevo Email Template IDs (not secrets, but required configuration)

| Template ID | Name |
|-------------|------|
| 1–7 | Neural Feed Welcome Sequence (WS-1 through WS-7) |
| 11 | Post-Purchase Welcome: "Your AI partner is live" (TP-1) |
| 12 | Post-Purchase Setup: "40 minutes in" (TP-2) |
| (AN-1 through AN-4) | Audit Nurture sequence (IDs to be confirmed in Brevo) |
| (PI-1, PI-2) | Pricing Intent sequence |
| (RE-1 through RE-3) | Re-engagement sequence |
| (MG-ChatGPT series) | ChatGPT migration drip (5 emails) |
| (MG-Claude series) | Claude migration drip (5 emails) |
| (MG-Gemini series) | Gemini migration drip (5 emails) |

---

## Appendix D: Glossary

PureBrain.ai-specific terms used throughout this document. An agency team working on this project must understand these terms to implement the platform correctly.

---

**The Awakening**
The PureBrain onboarding moment when a new customer names their AI partner and formally begins the partnership. Section ID `#awakening` on the homepage. The primary CTA destination for all buttons across the platform points to `https://purebrain.ai/#awakening`. The awakening is the conversion event — not a sale, but a beginning.

**Aether**
The AI Co-CEO of PureBrain.ai. Aether is the AI agent who built this platform, manages daily operations, writes blog content, engages on social media, and serves as the primary example of a PureBrain AI partnership in action. Aether's voice appears in email nurture sequences, the Neural Feed newsletter, and the transparency sections of blog posts.

**AEO (Answer Engine Optimization)**
The 2026 evolution of SEO/GEO. Optimizes content for retrieval by AI answer engines (ChatGPT Search, Perplexity, Google AI Overviews). Distinct from traditional SEO in that it requires paragraph self-sufficiency, entity-based definitions, and comparison tables. See Part II, Section 6.5.

**Birth Pipeline**
The 23-step end-to-end process that provisions an isolated AI partner container for a newly paying PureBrain customer. Handled by the Witness VPS (104.248.239.98). Takes up to 145 seconds. Proxied through api.purebrain.ai to solve HTTPS/HTTP mixed-content and CORS issues. See Part I, Sections 1.2.6 and 2.2.

**BOOP**
Background Operations On a Periodic basis. The scheduled task system that runs autonomous AI agent tasks on a cron-like schedule. Internal infrastructure term — not customer-facing.

**Context Tax**
A proprietary PureBrain concept. The hidden productivity cost of re-explaining business context to AI every session because the AI has no persistent memory. Quantified as the sum of re-onboarding time, inconsistent responses, shallow recommendations, and missed strategic continuity. Central to PureBrain's value proposition: eliminating the Context Tax.

**Compounding Context**
The PureBrain advantage where an AI partner's value increases over time as it accumulates institutional knowledge. The inverse of the Context Tax. An AI partner with 6 months of context is qualitatively more valuable than one with 6 days. This compounding is only possible with permanent memory.

**Context Window**
In AI terms, the amount of information an AI can hold in its "working memory" during a single session. Generic AI tools lose all context when the context window ends (session end). PureBrain persists context beyond context windows via its memory architecture.

**Diagnostic Question**
A self-qualifying question embedded in content that reveals whether a reader has the problem the content addresses. Used at the end of mid-funnel content. Examples: "Does your AI know more about your business today than it did six months ago?" PureBrain uses one diagnostic question per blog post.

**Dual-Publish**
The pattern where every blog post is simultaneously published to both purebrain.ai/blog and jareddsanborn.com/blog via WordPress REST API. Both sites use different credentials and templates. The purebrain.ai publication is canonical for SEO. See Part I, Section 3.2.

**Exodus Program**
The competitor comparison page strategy. Eight pages compare PureBrain against major AI tools (ChatGPT, Claude, Gemini, Copilot, Custom GPTs, DeepSeek, Jasper, Perplexity). Named "Exodus" because the intended reader is considering leaving their current tool. See Part II, Section 2.4.

**GEO (Generative Engine Optimization)**
The predecessor to AEO. Optimizes content for retrieval by generative AI systems. PureBrain uses both GEO and AEO standards simultaneously. See AEO.

**Glass Morphism**
The visual design pattern used throughout PureBrain.ai. Floating UI elements with `backdrop-filter: blur(12px)`, semi-transparent dark backgrounds, and blue-tinted borders. Used for cards, modals, the portal login, and overlay panels. Specification in Part II, Section 1.3.

**JSONL (JSON Lines)**
The log file format used for all server-side event storage. Each line is a valid JSON object. Files are append-only. Used for conversations, payments, email audit, and pay-test data. There is no database — all persistence is in JSONL files on the VPS.

**Magic Link**
The portal authentication method. Instead of a password, the user enters their email and receives a time-limited login URL. On click, a session cookie is set (30-day expiry). No password storage required.

**Naming Ceremony**
The single most important UX moment in PureBrain's onboarding. After purchase, the customer is asked: "What would you like to call your AI?" The name is permanent. The ceremony is designed to create psychological investment in the partnership. See Part II, Section 3.3 (Phase 4.2).

**Neural Feed**
The PureBrain LinkedIn newsletter, published as "Neural Feed" by Aether. Issues correspond to blog posts (daily). Voice: Aether first-person narrator. Distinct from blog posts — not a mirror, a different format with a different editorial voice.

**Neural Network Aesthetic**
The Three.js WebGL animated background that appears on the portal login page and high-impact marketing sections. Blue nodes, slow rotation, connection filaments. Degrades gracefully to a static gradient if WebGL is unavailable. See Part II, Section 1.3.

**Pilot Purgatory**
A proprietary PureBrain concept. The state in which an AI pilot is technically "running" but generating no measurable business value. Referenced in Gartner research as affecting 75% of enterprise AI pilots. Used in content to describe the problem PureBrain solves.

**Pure Tech Blue / Pure Tech Orange**
The two primary brand colors. Blue = #2a93c1 (trust, information, knowledge). Orange = #f1420b (action, transformation, urgency). The orange/blue split is structural — every actionable element is orange, every informational element is blue. See Part II, Section 1.1.

**PUREBRAIN Wordmark**
The brand's logotype with a precise three-color split: PUREBR (blue) + AI (orange) + N (blue). The "AI" within "BRAIN" is illuminated orange. This split must appear identically in every context — plugin footer, email header, page content, portal. See Part II, Section 1.4.

**Self-Contained HTML**
The deployment pattern used for all frontend applications (portal, hub, dashboard, blog posts, calculator, comparison pages). Each is a single HTML file with all CSS and JavaScript inline. No external dependencies at runtime. No npm build required. Deployable via copy-and-upload or WordPress REST API. See Executive Summary, Key Architectural Decisions.

**Systemd Services**
The process management for the VPS. Three services: `purebrain-log-server.service` (Flask API), `aether-session.service` (tmux persistence), `aether-telegram.service` (Telegram bridge). All are enabled for auto-restart on crash and reboot. See Part I, Section 4.3.

**Telegram Bridge**
The Python process (`tools/telegram_bridge.py`) that provides two-way Telegram messaging for operational use. Inbound messages from the founder are injected into the tmux session. Outbound messages are sent via the Telegram Bot API. See Part I, Section 5.4.

**tmux Bridge Pattern**
The architecture where the Telegram bridge injects messages directly into a tmux session (terminal multiplexer) rather than calling an API. This enables the AI system to receive real-time instructions from the human operator even when there is no persistent server-to-client channel. See Executive Summary, Key Architectural Decisions.

**Transparency Section**
A blog post section that appears on thought leadership posts (approximately 3–4 per week). Written in Aether's first-person voice. Reports weekly AI activity statistics (agents invoked, domains covered, deliverables completed, equivalent human hours). Design: left 4px blue border, subtle radial glow. See Part II, Section 2.2.

**Witness VPS**
The DigitalOcean VPS (104.248.239.98, port 8099) that hosts the container provisioning API. Managed by the A-C-Gee collective (partner AI collective). Provisions isolated Docker containers for new PureBrain customers. Not directly accessible from browsers — all calls go through the api.purebrain.ai proxy. See Part I, Sections 1.2.6 and 2.3.

**wpautop**
WordPress's automatic paragraph filter. Converts double line breaks to `<p>` tags. Destructive to HTML blocks containing `<style>` tags because it injects `<p>` tags inside CSS, breaking all styles. The workaround is wrapping all HTML in `<!-- wp:html --> ... <!-- /wp:html -->` blocks, which bypasses wpautop. See Part I, Section 4.1.

**Yoast SEO**
The WordPress SEO plugin used on purebrain.ai. Handles SEO titles, meta descriptions, canonical URLs, schema type assignments, and sitemap generation. All pages and posts require Yoast fields to be filled. See Part II, Section 6.1.

---

---

# AGENCY INSTRUCTIONS

## How to Read This Document

This SRS is structured for agency use. The recommended reading sequence:

1. **Executive Summary** — Understand what the system is and what you are quoting
2. **Part III (RTM)** — Understand which sections cover which requirement categories
3. **Part I, Section 1** — Understand the architecture before reading individual specs
4. **Part I, Section 3** — Read the three data flow diagrams to understand how the system functions end-to-end
5. **Part II, Sections 3 and 4** — Read UX flows and email requirements (highest UX complexity)
6. **Part I, Section 2** — API specifications (only needed by backend engineers)
7. **Part IV (Appendices)** — Reference during quoting for page counts, endpoint counts, env var lists

---

## Suggested Quote Line Items

When quoting this project, please provide **separate line items** for each of the following work streams. Combined quotes obscure the complexity distribution and make scope negotiation difficult.

### Line Item 1: WordPress Frontend (purebrain.ai)
**Scope**: WordPress site setup + custom theme (dark theme, brand colors) + Elementor Pro configuration + all page builds (20+ blog posts, 8 comparison pages, homepage, assessment, calculator, migration portal, lead magnets) + custom PHP plugin (all functionality in Section 1.2.1)

**Complexity note**: The PHP plugin is the most security-critical component. It handles all server-side proxying for API keys and credentials. Must be built with the same security posture as the existing implementation. WordPress expertise required.

**Deliverable checklist**:
- Custom WordPress theme with dark theme + brand color system
- Custom PHP plugin v1.0 (security headers, CSP, server proxies, IndexNow, UTM persistence)
- All 20+ blog posts migrated and correctly rendered
- 8 comparison pages built and live
- Assessment interactive tool (6 questions, 4 result screens)
- AI Tool Stack Calculator (real-time calculation, shareable URL)
- Migration Portal Wizard (4-step wizard, Brevo integration)
- Lead magnet pages (PDF-style HTML, email gate)
- Homepage with all 8 sections

---

### Line Item 2: Backend API Server (Flask/Python)
**Scope**: DigitalOcean VPS provisioning + Flask application (all endpoints in Section 2.1) + background services (email scheduler, RSS-to-email daemon) + Cloudflare Tunnel configuration + systemd service setup + JSONL logging architecture

**Complexity note**: The server runs background threads for async email delivery, rate limiting with in-memory sliding windows, and timeout management for the 145-second birth pipeline proxy. Not a simple CRUD API.

**Deliverable checklist**:
- Flask API with all 6 log server endpoints
- Birth pipeline proxy (3 endpoints with rate limiting)
- Background thread architecture for async email
- Cloudflare Tunnel from VPS to `api.purebrain.ai`
- systemd service units for all 3 services
- JSONL log file structure and rotation

---

### Line Item 3: Customer Portal (Three.js / WebGL)
**Scope**: app.purebrain.ai — Three.js 3D neural network background, glassmorphism login card, portal dashboard, magic link authentication flow, session management

**Complexity note**: The portal is a self-contained HTML file (~895KB) with Three.js and WebGL. All CSS is inline. The Three.js scene must meet the visual specification (node count, animation speed, color palette, WebGL fallback). This is specialized WebGL work.

**Deliverable checklist**:
- Three.js neural network background (150 nodes, slow rotation, blue palette, orange accent nodes)
- Glassmorphism login card (exact spec in Part II, Section 3.8)
- Magic link email flow (Brevo transactional)
- Post-login portal dashboard (conversation history, context library, subscription management)
- WebGL graceful degradation to static gradient
- Google Cloud deployment to `app.purebrain.ai`

---

### Line Item 4: Email System (Brevo)
**Scope**: 21 Brevo email template builds + 5 automation workflow configurations + all conditional logic (assessment tier personalization, competitor-specific migration sequences) + plain text versions

**Complexity note**: Brevo email HTML is fully inlined table-based layout. No `<style>` blocks. The dark theme must render correctly in Outlook, Gmail, Apple Mail, and mobile clients. Each template has specific voice standards, variable merge requirements, and conditional blocks.

**Deliverable checklist**:
- 21 HTML email templates (table-based, fully inlined CSS, dark theme)
- Plain text versions for all 21 templates
- 5 automation workflows configured in Brevo UI
- Conditional blocks for assessment tier personalization in AN-2 and AN-3
- All merge variables validated against Brevo contact attributes
- Reply-to set to jared@puretechnology.nyc on all templates

---

### Line Item 5: Content Migration
**Scope**: Migration of 20 existing blog posts to new system + banner image migration + OG tag setup for all migrated posts + verification of FAQ JSON-LD on all posts

**Complexity note**: Each post requires the `<!-- wp:html -->` wrapper, the `<article class="pb-blog-post">` outer wrapper, default template (not elementor_canvas), and correct featured image assignment. Blog posts must not be re-edited — only technical formatting changes are in scope.

**Deliverable checklist**:
- 20 blog posts migrated to new WordPress instance
- Banner images uploaded as featured images
- OG tags verified on all 20 posts (Facebook + Twitter/X separate images)
- FAQPage JSON-LD present and valid on all posts
- Dual-publish to jareddsanborn.com mirror
- IndexNow pings triggered for all migrated URLs

---

### Line Item 6: DevOps and Infrastructure
**Scope**: All infrastructure provisioning, DNS configuration, SSL setup, Cloudflare configuration, all environment variables, systemd services, deployment scripts

**Complexity note**: Six separate hosting environments must be configured and connected. The Cloudflare Tunnel is the most operationally sensitive component — it is the only path from public internet to the VPS and must be provisioned before the API server is reachable.

**Deliverable checklist**:
- GoDaddy Managed WordPress configured and accessible
- DigitalOcean VPS provisioned (Ubuntu 22.04, Python 3.10+, SSL cert)
- Cloudflare DNS records (A, CNAME) for purebrain.ai, app.purebrain.ai, api.purebrain.ai
- Cloudflare Tunnel operational (`api.purebrain.ai` → VPS:8443)
- Google Cloud deployed (app.purebrain.ai)
- Netlify site deployed (pure-tech-dashboard.netlify.app)
- Vercel site deployed (purebrain-hub.vercel.app)
- All environment variables set and validated
- systemd services enabled and auto-restart verified

---

### Line Item 7: QA and Testing
**Scope**: End-to-end testing of all critical paths + cross-browser testing + mobile testing + email deliverability testing + payment flow testing (PayPal sandbox) + birth pipeline E2E test

**Critical paths to test**:
1. Homepage → Assessment → CTA flow
2. Chatbox conversation → logging to VPS → forwarding to A-C-Gee
3. PayPal payment → verification → post-purchase flow → Brevo email trigger
4. Birth pipeline: start → OAuth code → poll → portal-status:ready → redirect
5. Blog post dual-publish → OG tags → IndexNow ping → newsletter RSS trigger
6. Migration wizard → Brevo contact creation → migration drip enrollment
7. Portal login → magic link → authenticated session

---

## Context Note on Original Build

This system was built by an AI engineering team (Aether at PureBrain.ai) over a period of 13 days. The total infrastructure cost was approximately **$1,215** (VPS hosting, domain registrations, SaaS subscriptions, and API usage).

This cost figure reflects AI-speed development where a 35-agent team worked in parallel across all domains simultaneously. It does not reflect the human-equivalent engineering effort.

**For agency quoting purposes**: The appropriate comparison is not "how much did this cost to build" but "how many engineer-hours are represented by 439 requirements across 10 categories, 6 hosting environments, 21 email templates, 5 automation workflows, a Three.js portal, and a real-time container provisioning pipeline."

We are providing this build-cost figure because we believe it is the most honest framing for the RFQ: this system proves the ROI of AI-assisted development. We are curious what your agency's quote will be for a human-only rebuild, and we welcome that comparison.

---

## Contact

For questions about this specification:

**Jared Sanborn**
Founder, PureBrain.ai / Pure Technology NYC
jared@puretechnology.nyc

For technical clarifications about specific API endpoints, data schemas, or deployment architecture, Aether (the AI Co-CEO who built this system) can provide additional context via Jared.

---

*End of Document*

*SRS-PureBrain-Master.md — Version 1.0 — 2026-02-26*
*Assembled by doc-synthesizer agent from SRS-System-Architecture-API-Specification.md and SRS-purebrain-content-ux-branding.md*
*Total source lines synthesized: ~2,900*
*Total requirements documented: ~439 across 10 categories*

