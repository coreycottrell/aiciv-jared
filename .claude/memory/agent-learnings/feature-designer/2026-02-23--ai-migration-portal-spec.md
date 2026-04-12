# AI Migration Portal — Design Session Memory

**Date**: 2026-02-23
**Agent**: feature-designer
**Type**: synthesis
**Topic**: Designing an AI migration portal that eliminates switching cost anxiety
**Confidence**: high
**Tags**: purebrain, portal, ux, migration, chatgpt, oauth, data-import, switching-cost

---

## Context

Jared asked for a complete feature spec for an "AI Migration Portal" inside PureBrain's product. The portal helps new customers transition from their old AI tools (ChatGPT, Claude, Notion, etc.) into PureBrain by importing conversation history, custom instructions, brand context, and other data.

---

## Core Design Insight: Loss Reframed as Foundation

The entire UX premise is one psychological reframe:

- **Old framing**: "I'm losing everything I built up with ChatGPT"
- **New framing**: "Everything I built with ChatGPT becomes PureBrain's starting point"

This is the antidote to switching cost anxiety. The portal makes concrete what could otherwise feel abstract: "We analyzed 847 conversations and identified your top 5 use patterns." Numbers make the value real.

---

## Key Patterns Discovered

### 1. Step 3 (Learning Phase) is the Emotional Core

The progress bar step where PureBrain "learns from" the imported data is not a passive waiting screen. It must actively surface insights in real time:
- "You asked about market analysis 23 times — flagged as a core use pattern"
- "Your Custom Instructions prefer direct answers without preamble — absorbed"

A blank progress bar during import would undercut the entire value proposition. The insights appearing is the feature.

### 2. Midjourney Has No API — Manual Capture is Still High Value

Midjourney has no official public API (as of 2026). But users' developed prompting styles (e.g., "cinematic, moody, wide angle, film grain, 1970s color palette") are highly valuable for PureBrain's image generation context. A short style description form is the right design — frame it as a feature, not a workaround. "Tell us about your visual style" — not "Midjourney doesn't have an API so..."

### 3. CRM Data Carries Third-Party PII

HubSpot integration exposes contacts (the user's customers). Individual records must not be stored — only structural data (pipeline names, deal stages, counts). This is both a legal requirement (GDPR) and a trust issue.

### 4. File Upload is More Reliable Than OAuth for Conversation History

ChatGPT and Claude have no conversation history APIs. File upload (from the built-in export) is the primary path, not a fallback. OpenAI's conversations.json is well-documented. Design the upload UX to be high-trust (clear instructions, "How to export" modal, show what was found after parsing).

### 5. Pre-Portal Data Collection Personalizes the Portal

Adding 4 questions to the exodus landing pages (primary use cases, frequency, custom config level, main frustration) directly feeds portal personalization. The frustration answer ("it never remembered anything") can be echoed back in the migration flow to create resonance.

---

## Integration Feasibility Summary

| Tool | Method | Feasibility |
|---|---|---|
| ChatGPT | File upload (conversations.zip) | HIGH |
| Claude | File upload (export ZIP) | HIGH |
| Notion | OAuth2 API | HIGH |
| Canva | OAuth2 Connect API (PKCE) | HIGH |
| HubSpot | OAuth2 API (careful PII scoping) | MEDIUM-HIGH |
| Gemini | Google OAuth (Drive context only) | MEDIUM |
| Perplexity | Text paste (no API) | LOW/MANUAL |
| Midjourney | Style description form (no API) | LOW/MANUAL |

---

## MVP Boundary (Critical for Scope Control)

MVP = ChatGPT + Claude file upload only. Prove the value proposition before building OAuth integrations. OAuth adds complexity, security surface, and maintenance burden. The file upload MVP can ship in 4-6 weeks and validate whether users actually use the migration flow.

---

## Files

- Full spec: `/home/jared/projects/AI-CIV/aether/exports/ai-migration-portal-spec.md`
