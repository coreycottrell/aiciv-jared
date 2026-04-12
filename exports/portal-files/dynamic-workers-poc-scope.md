# Cloudflare Dynamic Workers — PureBrain POC Scope

**Author**: cto (Chief Technology Officer, Pure Technology)
**Date**: 2026-03-26
**Status**: Draft for team review
**Distribution**: Witness, Parallax, Flux, Prodigy, Meridian
**CF Dynamic Workers**: Open beta as of 2026-03-24 — paid Workers users only

---

## Executive Summary

Cloudflare released Dynamic Workers (open beta, March 24 2026): isolated V8 JavaScript sandboxes
that can be spun up at request time from AI-generated or user-provided code. Startup time is
milliseconds. Memory footprint is single-digit megabytes. Pricing post-beta is $0.002 per unique
worker loaded per day, plus standard CPU and invocation charges.

This is not a replacement for Witness containers. It is a complementary execution layer — lightweight,
stateless, ephemeral — that slots between our static CF Pages site and the heavy Witness Linux
containers. The opportunity is to offload short-lived compute that today either lives in the portal
server (VPS) or does not exist at all.

This document scopes a Phase 1 POC, ranks five candidate use cases, and defines the architecture
integration points for team discussion.

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/cto/` for Cloudflare Workers, webhook, portal server, sandbox
- Found: 2026-03-12 CF pricing memory (confirmed we are on paid plan — Workers paid eligibility met)
- Found: 2026-02-24 Witness birth pipeline architecture (confirms container model, mixed-content proxy pattern)
- Applying: Existing CF proxy pattern at api.purebrain.ai/api/birth/* as integration model for Dynamic Workers endpoints

---

## Section 1 — Use Case Prioritization

Ranked by impact-to-effort ratio. Impact is defined against PT's current scale and growth trajectory.
Effort is estimated for a team with existing CF Workers and Python VPS experience.

### Rank 1 — Code Preview / Testing for Customer AI-Generated Code (Use Case D)

**Impact: High. Effort: Low.**

Customers using PureBrain already receive AI-generated suggestions. Today there is no sandbox for
running that code safely. Customers either trust-and-deploy or abandon the idea. Dynamic Workers
solves this exactly: the AI generates JavaScript, we load it into a sandboxed worker, the customer
sees real output before it touches any live system.

This is the use case Cloudflare explicitly optimized for. The `@cloudflare/codemode` library wraps
this pattern out of the box. No stateful session required. No Witness dependency. Pure CF edge.

Why this wins rank 1: lowest implementation risk, directly enhances the core AI partnership product,
and visible to the customer within the existing portal UX with minimal backend change.

---

### Rank 2 — Webhook Processing (Use Case E)

**Impact: High. Effort: Low-Medium.**

The portal server (purebrain_log_server.py on VPS) currently handles inbound webhooks — PayPal
payment events, AgentMail notifications, and potentially Bitrix CRM callbacks. These are stateless
request handlers: receive event, validate, write to JSONL or trigger next action. They do not need
a Linux container. They do not need persistent state during execution.

Moving webhook handlers to Dynamic Workers gives us: CF edge proximity (lower latency), auto-scaling
without VPS capacity planning, zero deployment friction (no systemd restarts), and a cleaner
separation between transient event processing and stateful portal server logic.

Implementation is mechanical: extract endpoint logic from portal_server.py, rewrite in TypeScript,
deploy as Dynamic Workers with `globalOutbound` filtering to whitelist only required upstream URLs
(PayPal API, AgentMail API, Witness API). The portal server VPS stays up for stateful operations but
sheds the stateless event load.

---

### Rank 3 — Lightweight Data Processing (Use Case C)

**Impact: Medium. Effort: Low.**

CSV transforms, API-to-API data pipelines, and response reformatting are a natural fit. The customer
uploads a CSV, the AI generates a transform worker, the worker runs at the edge and returns processed
data. No container spin-up. No VPS hop.

At current customer scale this is not urgent — volume is low. Ranked 3 because the architecture
pattern established here feeds directly into Use Case B (customer automation sandbox) and creates a
reusable execution primitive. Build it as infrastructure, not as a one-off feature.

---

### Rank 4 — Customer Automation Sandbox (Use Case B)

**Impact: Very High. Effort: High.**

The long-term vision: customers build automations inside their AI portal — "connect my Shopify to my
email list when a product is purchased." The AI generates the worker code. The customer reviews it.
Dynamic Workers executes it on-demand or on a schedule.

This is the feature that differentiates PureBrain from every generic AI chatbot. However, it requires
solid foundations: the code preview sandbox (rank 1), the data processing primitive (rank 3), a
permission model for what APIs customers can call, and a scheduling layer (Cron Triggers or Durable
Objects). This is a Phase 2+ initiative. Do not attempt in Phase 1 POC.

---

### Rank 5 — Agent Tool Execution (Use Case A)

**Impact: Medium. Effort: High.**

Chaining multiple API calls inside one worker to reduce token round-trips is real optimization but
requires architectural trust decisions: what can a worker call on behalf of an agent session? The
security surface is non-trivial. Token savings are meaningful at scale but we are not at the scale
where this bottleneck is the binding constraint. Defer.

---

### Summary Table

| Rank | Use Case | Impact | Effort | Phase |
|------|----------|--------|--------|-------|
| 1 | Code preview / customer AI-generated code sandbox | High | Low | Phase 1 POC |
| 2 | Webhook processing (replace portal server endpoints) | High | Low-Med | Phase 1 POC |
| 3 | Lightweight data processing / CSV transforms | Medium | Low | Phase 1 build |
| 4 | Customer automation sandbox | Very High | High | Phase 2+ |
| 5 | Agent tool execution (token reduction) | Medium | High | Phase 3 |

---

## Section 2 — Architecture

### Principle: Witness Stays Heavy, Dynamic Workers Stays Light

Witness containers are full Linux environments with persistent state, OAuth sessions, JSONL chat
history, file systems, and tmux sessions. They are right-sized for stateful, long-lived, per-customer
workloads. Dynamic Workers are wrong for this. Do not attempt to replace Witness.

The boundary is: **state boundary = container boundary**.

```
                          PUREBRAIN STACK — LAYER MAP

  Customer Browser
        |
        v
  CF Pages (purebrain.ai)          ← static site, no change
        |
        v
  CF Workers — Routing Layer       ← existing, handles redirects
        |
        +---> Dynamic Workers      ← NEW: ephemeral, stateless execution
        |          |
        |          |--- Code sandbox (review before deploy)
        |          |--- Webhook handlers (PayPal, AgentMail, Bitrix)
        |          |--- Data transforms (CSV, API glue)
        |
        v
  api.purebrain.ai (VPS)           ← stateful: portal server, JSONL, auth
        |
        v
  Witness Birth API (104.248.239.48:8099)  ← container lifecycle
        |
        v
  ai-civ.com Customer Containers   ← heavy: Linux, tmux, Claude, portal UI
```

### What Stays in Witness Containers

- Customer Claude sessions (stateful, long-running)
- Portal server (chat history, file uploads, portal-chat.jsonl)
- OAuth state (magic links, session tokens)
- Referral/payout state (SQLite or JSONL)
- ElevenLabs TTS streaming (latency-sensitive, already wired)

### What Moves to Dynamic Workers

- Inbound webhook validation and routing (PayPal IPN, AgentMail events)
- AI-generated code execution sandbox (customer-facing code preview)
- CSV/JSON transform requests that do not require persistent state
- Health check proxying (lightweight, no state)

### Integration Points

**Integration Point 1 — Portal Server Offload**

Portal server today: Python + Starlette on VPS, handles all inbound requests. Post-POC: payment
webhooks and event notifications route to Dynamic Workers at the CF edge. The worker validates
the event signature, reformats if needed, then calls the portal server's internal API for any
stateful write. The VPS never exposes raw webhook endpoints to the public internet.

```
PayPal Event → CF Worker (validate signature) → internal POST to VPS → portal_server.py writes JSONL
```

**Integration Point 2 — Code Sandbox in Customer Portal**

Customer in their PureBrain portal asks AI to generate an automation script. AI returns TypeScript.
Portal sends the code to a Dynamic Worker endpoint. Worker loads it via `env.LOADER.load()` with
`globalOutbound: null` (no outbound by default). Execution result returns to portal. Customer
reviews output before approving deployment.

```
Portal UI → POST /api/sandbox/preview (CF Worker) → env.LOADER.load(customerCode) → result → Portal UI
```

**Integration Point 3 — Existing CF Worker Coordination**

Our existing CF Workers handle routing/redirects. Dynamic Workers are loaded FROM an existing parent
worker via the LOADER binding — they are not standalone. The parent worker controls which Dynamic
Workers can be instantiated and with what permissions. This is the correct mental model: the existing
workers layer is the gatekeeper.

---

## Section 3 — Technical Requirements

### CF Plan Status

We confirmed paid CF plan in March 2026 (Pro at $20/mo, LB add-on separate). Workers paid plan
eligibility is met. Dynamic Workers (open beta) access requires no additional sign-up beyond being
on a paid Workers plan. **No additional cost during beta.**

### API Patterns

The core interface is the LOADER binding, declared in wrangler.toml:

```toml
[[unsafe.bindings]]
type = "dynamic_dispatcher"
name = "LOADER"
```

Usage in the parent Worker:

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // customerCode comes from trusted source (AI output, admin-approved)
    const customerCode = await getValidatedCode(request, env);

    const worker = env.LOADER.load({
      compatibilityDate: "2026-03-01",
      mainModule: "sandbox.js",
      modules: { "sandbox.js": customerCode },
      env: {
        // Only expose what the sandbox needs — nothing else
        RESULT_STORE: env.RESULT_STORE,  // KV for async results
      },
      globalOutbound: null,  // Block ALL outbound HTTP by default
    });

    const result = await worker.getEntrypoint().run();
    return Response.json({ result });
  }
};
```

**Security note on globalOutbound**: Setting `null` blocks all outbound HTTP from the dynamic worker.
For use cases that need controlled outbound (e.g., a customer automation calling their Shopify API),
use a callback that whitelists specific domains and injects credentials — never pass customer-supplied
credentials into the worker directly.

### Security Boundaries — What Customers Can Access

Dynamic Workers run in V8 isolates with Cloudflare's second-layer sandbox on top. For PureBrain's
customer code execution:

**Allow by default (inside worker):**
- Pure computation (transforms, parsing, formatting)
- Calls to the `env` RPC stubs we explicitly provide
- Reading/writing to KV namespaces we bind

**Deny by default:**
- All outbound HTTP (`globalOutbound: null` for code preview use case)
- Access to env vars not explicitly passed in the `env` parameter
- File system (not available in Workers runtime)
- Subprocess execution (not available in Workers runtime)

**For Phase 2 automation sandbox** (controlled outbound):
- Whitelist approach: `globalOutbound` callback validates destination hostname against
  customer-approved integration list stored in KV
- Never allow `purebrain.ai`, `ai-civ.com`, or internal VPS IPs as outbound targets from
  a customer-code dynamic worker — this prevents SSRF against our own infrastructure

### TypeScript Interface Design for PureBrain APIs

Define narrow RPC interfaces that describe only what the sandbox needs. Cloudflare's guidance:
"a TypeScript interface requires far fewer tokens to describe than an HTTP interface" — this matters
because the AI generating customer code reads these interfaces.

```typescript
// purebrain-sandbox-api.d.ts — ship this as context to the AI generating customer code

interface PureBrainSandboxAPI {
  /** Store a result for async retrieval by the customer portal */
  storeResult(key: string, value: unknown): Promise<void>;
  /** Retrieve a previously stored value */
  getResult(key: string): Promise<unknown | null>;
  /** Log a message visible in the customer's portal (not the VPS log) */
  log(message: string): void;
}

// What we DO NOT expose in the sandbox interface:
// - Any auth tokens
// - Any internal API endpoints
// - Any Witness container management
// - Any payment processing
```

### Module Bundling

Customer code must be pre-bundled before passing to `env.LOADER.load()`. Use
`@cloudflare/worker-bundler` for any customer code that imports npm packages. For Phase 1
(code preview only), restrict to pure computation — no npm imports allowed. This eliminates
bundling complexity in Phase 1.

---

## Section 4 — Phase 1 POC Specification

### Selected Use Case: Code Preview Sandbox (Rank 1)

**Rationale**: Highest visibility to customers, lowest infrastructure risk, directly uses the
feature Dynamic Workers was designed for, no stateful dependencies.

### Concrete Implementation

**Endpoint**: `POST https://api.purebrain.ai/api/sandbox/preview`

This route lives in the existing CF Worker (the parent). No new Worker project needed.

**Request shape** (from customer portal):

```json
{
  "code": "export default { async run(api) { return api.transform([1,2,3], x => x * 2); } }",
  "timeout_ms": 5000,
  "input": { "any": "data the customer wants to pass" }
}
```

**Worker logic (parent)**:

1. Authenticate request: validate portal session token (checked against KV or Durable Object
   holding session state — same auth pattern as existing api.purebrain.ai routes)
2. Rate limit: max 10 sandbox executions per customer per minute (KV counter)
3. Static code analysis: reject any code containing `eval`, `Function(`, `import(` dynamic imports,
   or any string resembling an internal IP/hostname
4. Load dynamic worker with `globalOutbound: null` and a minimal `SandboxAPI` RPC stub
5. Execute with `Promise.race([worker.getEntrypoint().run(input), timeout(5000)])`
6. Return result or timeout error

**Response shape**:

```json
{
  "success": true,
  "result": { "output": [2, 4, 6] },
  "execution_ms": 12,
  "sandbox_id": "sb_abc123"
}
```

**Portal UI changes** (Flux + Parallax):

Add a "Test this code" button in the portal chat view when the AI returns a code block. On click:
POST to sandbox endpoint, show a loading state ("Running in isolated sandbox..."), then render the
result inline. Add a "Deploy" button that only appears after a successful preview.

**Data Flow Diagram**:

```
Customer types: "Write me a function that transforms my CSV columns"
      |
      v
AI (Claude in Witness container) generates TypeScript
      |
      v
Portal UI detects code block → shows [Test] button
      |
      v
Customer clicks [Test]
      |
      v
POST /api/sandbox/preview (CF parent worker)
  - auth check
  - rate limit
  - static analysis
  - env.LOADER.load(code, globalOutbound: null)
  - 5s timeout
      |
      v
Result returned in <50ms typical
      |
      v
Portal shows output inline
Customer clicks [Deploy] → saves to their automation library
```

### Effort Estimate

| Task | Owner | Days |
|------|-------|------|
| Wrangler config: add LOADER binding to existing worker | Flux | 0.5 |
| Static code analysis filter (deny list) | Prodigy / security review | 1.0 |
| Parent worker route: auth, rate limit, load, execute | Flux | 1.5 |
| SandboxAPI RPC stub interface | Flux | 0.5 |
| Portal UI: [Test] button + result rendering | Parallax | 1.5 |
| Integration test (mock + live) | Prodigy | 1.0 |
| **Total** | | **6.0 days** |

**Conservative estimate including review cycles: 8 days.**

### Monthly Cost Estimate (Current Scale)

- Customers at current scale: approximately 60 active portal users
- Sandbox executions per user per day (estimated): 5
- Unique workers loaded per day: 300 (one per execution if each is unique code)
- Cost per unique worker per day: $0.002
- **Daily cost: $0.60**
- **Monthly cost: ~$18**

At 10x scale (600 active users, 5 executions/day):
- **Monthly cost: ~$180** — still negligible relative to Witness container costs

Note: during beta, the $0.002/worker/day charge is waived. Phase 1 POC runs at zero incremental cost.

---

## Section 5 — Risks and Mitigations

### Risk 1 — V8 Sandbox Escape (Critical)

**Description**: Dynamic Workers increase the attack surface because arbitrary code runs in V8
isolates. A sandbox escape would allow a malicious customer to access other customers' data or
our infrastructure.

**Probability**: Low. Cloudflare runs this platform for the entire Workers ecosystem and invests
heavily in isolate security (hardware-backed MPK, custom second sandbox layer, rapid V8 patching).

**Mitigation**:
- `globalOutbound: null` eliminates network-based lateral movement from within the sandbox
- Static code analysis before load rejects obviously malicious patterns
- The sandbox only receives a minimal RPC API with no access to auth, payment, or container state
- Rate limiting prevents brute-force sandbox abuse
- Monitor Cloudflare security advisories and patch wrangler/runtime dependencies immediately

**Residual risk**: Acceptable for Phase 1 given Cloudflare's security track record.

---

### Risk 2 — Beta API Instability

**Description**: Dynamic Workers is open beta (released March 24 2026). The API — especially
`env.LOADER.load()` parameter shape — may change before GA.

**Probability**: Medium. Beta products often have breaking changes.

**Mitigation**:
- Isolate all Dynamic Workers usage behind a single abstraction layer (`sandbox-service.ts`)
- No customer-facing features that depend on the sandbox should be marked "stable" until CF GA
- Monitor CF Workers changelog and Discord #workers channel
- Build the Phase 1 POC with a feature flag — can disable the [Test] button with one KV write
  if the API breaks

---

### Risk 3 — Static Code Analysis Bypass

**Description**: Our deny list (no `eval`, no dynamic imports, no internal IPs) may be incomplete.
A sophisticated customer could craft code that passes static analysis but behaves unexpectedly inside
the sandbox.

**Probability**: Low at current customer scale. Higher as we grow.

**Mitigation**:
- `globalOutbound: null` is the defense of last resort — even if analysis is bypassed, the code
  cannot exfiltrate data or call external services
- Add execution-time monitoring: log all sandbox executions with code hash, customer ID, and result
- Plan for Prodigy to own ongoing static analysis rule updates as new patterns emerge

---

### Risk 4 — Customer Confusion (UX)

**Description**: "Test this code" implies the code does something real. Customers may not
understand the sandbox is isolated and expect the automation to actually run against their data.

**Probability**: Medium.

**Mitigation**:
- Clear UI copy: "Running in an isolated sandbox — no data is modified"
- Sandbox results are labeled distinctly (different background color, sandbox icon)
- "Deploy" requires a second confirmation step that explains what deployment does
- Parallax to review UX copy before launch

---

### Risk 5 — Cost Spike from Abuse

**Description**: A customer (or adversary with a stolen session) runs thousands of sandbox
executions in a short window, driving up Dynamic Workers costs.

**Probability**: Low. Mitigation already in spec.

**Mitigation**:
- Rate limit: 10 executions per customer per minute (KV counter, 60s TTL)
- Hard cap: 500 executions per customer per day before requiring manual approval
- Alert Jared via Telegram if any customer exceeds 200 executions in a day

---

## Implementation Checklist (Phase 1)

- [ ] Confirm LOADER binding is available on our current Workers plan (Flux — check dashboard)
- [ ] Add LOADER binding to wrangler.toml in existing parent worker
- [ ] Implement static code analysis deny list (Prodigy reviews)
- [ ] Implement parent worker route with auth + rate limit + load + execute
- [ ] Define `SandboxAPI` RPC interface (reviewed by Witness for consistency with container APIs)
- [ ] Portal UI: [Test] button conditional on code block detection (Parallax)
- [ ] Portal UI: result rendering with sandbox label (Parallax)
- [ ] Integration test against a real code snippet end-to-end
- [ ] Feature flag in KV to enable/disable without deploy
- [ ] Cost alert trigger in portal server if execution count exceeds threshold

---

## Open Questions for Team

1. **Witness**: Does the `SandboxAPI` RPC interface need to align with any existing API patterns
   in the container runtime, or is it fully independent?

2. **Flux**: Our existing CF Worker is handling routing/redirects — is it structured to add a
   new route cleanly, or do we need to extract the sandbox logic into a separate Worker service?

3. **Parallax**: Where in the portal UX does the [Test] button live — inline below the code block
   in chat, or as a dedicated sandbox panel in the sidebar?

4. **Prodigy**: What is your threat model for the static code analysis? Are there patterns beyond
   the obvious (`eval`, dynamic imports, internal IPs) that we should catch at Phase 1?

5. **Meridian**: Should we treat sandbox execution logs as customer data subject to retention
   policies? The logs will contain customer-submitted code — does that change our data handling?

---

## Next Steps

1. **This week**: Team reviews this document. Answers to Open Questions above.
2. **Days 1-2**: Flux confirms LOADER binding access + wrangler config.
3. **Days 3-5**: Parallel tracks — Flux builds parent worker route, Parallax builds portal UI.
4. **Days 6-7**: Prodigy security review + integration test.
5. **Day 8**: Jared reviews demo in his portal. Ship or iterate.

---

*Document written by cto. Questions → route through Aether (Co-CEO) for coordination.*
