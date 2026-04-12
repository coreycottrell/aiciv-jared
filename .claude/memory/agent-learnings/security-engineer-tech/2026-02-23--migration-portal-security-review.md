# Security Review Memory: AI Migration Portal Pre-Implementation Review

**Agent**: security-engineer-tech
**Date**: 2026-02-23
**Type**: security-analysis
**Target**: AI Migration Portal Feature Spec v1.0
**Spec Source**: `docs/from-telegram/ai-migration-portal-spec.md`
**Output**: `exports/migration-portal-security-review.md`

---

## Risk Summary

- CRITICAL: 4
- HIGH: 12
- MEDIUM: 10
- LOW: 5

**Blocking items (P0 — must fix before any implementation):**
- CRIT-001: ZIP bomb prevention (size limits before decompression)
- CRIT-002: Zip slip path traversal (safe_unzip pattern required)
- CRIT-003: Canva PKCE enforcement (their API requires it)
- CRIT-004: HubSpot PII architectural enforcement (in-memory only, CI test asserts no PII in output)

---

## Key Patterns Learned

### 1. File Upload Security Triad
Every file upload pipeline needs THREE distinct checks:
1. **Compressed size limit** (before any decompression): 50MB cap at HTTP layer + application layer
2. **Decompression bomb prevention**: Stream decompression, abort on > 500MB total
3. **Path traversal check**: `os.realpath()` comparison against extract root for every ZIP entry

These are three separate vulnerabilities. Fixing one does not fix the others.

### 2. HubSpot / CRM Integration Pattern (GDPR Critical)
Any CRM integration (HubSpot, Salesforce, etc.) that contains third-party contact PII requires:
- In-memory processing ONLY — no write to disk or database at any stage
- Output contains ONLY structural/aggregate data (counts, pipeline names, stage names)
- `assert_no_pii()` test mandatory in CI — cannot be skipped or removed
- Raw contact objects explicitly deleted from memory after extraction

Storing third-party CRM contact data has no lawful basis under GDPR Article 6 — this is not a "nice to have" — it's a compliance hard stop.

### 3. OAuth Security Requires All Four Controls
Four separate OAuth controls, all required:
1. **PKCE** (proof key for code exchange) — prevents auth code interception
2. **State parameter** — prevents CSRF on the callback
3. **Vault storage** — prevents token theft from DB breach
4. **Minimum scope** — limits blast radius if tokens are stolen

Missing any one of these creates a distinct exploitable attack path.

### 4. Vault Architecture is a Day-One Decision
The vault infrastructure decision (HashiCorp Vault vs KMS envelope encryption) must be made before ANY OAuth integration work begins. It affects the entire token storage layer. This is not something that can be "added later" without refactoring every OAuth integration.

### 5. Safe ZIP Extraction Pattern (Python)
```python
def _safe_extract_member(zf, info, extract_to):
    extract_root = os.path.realpath(extract_to)
    target_path = os.path.realpath(os.path.join(extract_root, info.filename))
    if not target_path.startswith(extract_root + os.sep):
        raise ValueError(f"Zip slip detected: {info.filename}")
    zf.extract(info, extract_to)
```
This is the canonical zip slip prevention pattern. Memorize it.

### 6. Prior Review Context
Previous chatbox v3 review blocked deployment for similar innerHTML/XSS patterns (line 910, 958, 967).
The migration portal has the same risk: conversation content from ChatGPT may contain HTML/JS payloads
that reach innerHTML in the insight cards on Step 3. Apply same fix: textContent everywhere, DOMPurify
only when HTML rendering is genuinely required.

---

## Review Output Files
- Full review: `exports/migration-portal-security-review.md`
- 28 findings total, with implementation code examples
- Sequenced implementation plan aligned with spec's 6-week timeline
