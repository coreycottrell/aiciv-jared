# Memory: PureBrain.ai SRS — Technical Requirements Synthesis

**Date**: 2026-02-26
**Type**: synthesis
**Agent**: code-archaeologist

## What Was Produced

A complete Software Requirements Specification (technical sections) for
the PureBrain.ai platform and app.purebrain.ai portal, reverse-engineered
from 351 full-stack-developer memory files + 5 prior code-archaeologist
analyses. Covers all 15 major requirement areas with formal FR-/NFR- numbered
requirements.

## Key Finding

This system is architecturally non-trivial. A development agency quoting
this work should understand:
- The "tmux bridge" pattern (gateway injects to terminal, not API calls)
- The self-contained HTML deployment pattern (no React build, no bundler)
- The WP plugin as all-in-one security + CSS + proxy layer
- The birth pipeline 23-step E2E (145s provisioning time)
- The dual-storage pattern (localStorage + Supabase for internal tools)

## Requirement Count

- FR-WEB: 094 requirements (website + plugin + SEO)
- FR-CHAT: 045 requirements (chatbox v1-v4.7 + PayPal + security)
- FR-3D: 033 requirements (GLSL avatar + Three.js portal + hub canvas)
- FR-BACKEND: 085 requirements (log server + Telegram + Drive + Gmail + BOOP + Hub + Dashboard)
- FR-PORTAL: 041 requirements (Witness architecture + containers + auth)
- FR-EMAIL: 041 requirements (Brevo templates + automations + delivery)
- FR-ANALYTICS: 032 requirements (GA4 + JSON-LD + IndexNow + UTM)
- NFR-SEC: 052 requirements (headers + XSS + API keys + proxy security + data privacy)
- NFR-PERF: 009 requirements
- NFR-SCALE: 007 requirements

## When To Apply

When Jared needs agency quotes, investor materials on development investment,
or onboarding new team members to the platform architecture. Also useful
when rebuilding or extending any subsystem — the data models section captures
exact field names and payload formats.
