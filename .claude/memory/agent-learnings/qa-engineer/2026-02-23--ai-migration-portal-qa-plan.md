# QA Learning: AI Migration Portal Test Plan

**Date**: 2026-02-23
**Type**: teaching
**Topic**: AI Migration Portal QA — file upload portals, personalization testing, migration flow patterns

---

## Key Patterns Discovered

### 1. Personalization Trust Failure Mode
Migration portals have a unique failure mode: when the product premise is "we know you," any generic output constitutes a broken promise, not merely a bug. Every personalization claim must be testable and falsifiable. "Task contains specific count from import" is a valid test. "Task feels personalized" is not.

### 2. Four Independent File Upload Security Controls
These four controls do NOT subsume each other — all four must be present:
1. Size limit enforcement (server-side, not just client-side)
2. MIME type validation via magic bytes (not file extension)
3. ZIP bomb detection (decompression ratio check)
4. Path traversal prevention (sandbox temp directory, strip `..` entries)

### 3. Temp File Deletion Must Be Verified Programmatically
Never assume temp files are deleted. Check the server temp directory after processing. A common failure mode: processing succeeds but cleanup job fails silently. Sensitive PII remains on disk.

### 4. Processing Timeout Is a Product Problem, Not Just Performance
The 5-minute timeout with email fallback is a user flow branch, not an error state. It requires its own test path. Users who trigger the timeout and receive an email have a different re-entry UX than users who wait for completion.

### 5. Non-English Content Is a High-Failure Area
Non-Latin character sets frequently break in:
- Topic extraction (NLP pipelines often trained on English)
- HTML display (encoding issues, mojibake)
- RTL text direction in insight cards
- Character count calculations (multi-byte vs single-byte)

### 6. Mobile File Upload Needs Explicit Testing
Safari on iOS has different file input behavior. When a user taps "upload," iOS presents camera roll by default. The user needs to navigate to Files app to find their ZIP. This is not self-evident. Test it manually on real device.

---

## Test Data That Must Be Prepared Before Testing

The most common QA failure is starting testing without proper test data. For migration portals:
- Empty conversations.json (not just missing — empty array)
- Valid large export (10,000+ conversations)
- Non-English export (Japanese, Arabic, Russian)
- XSS payload in conversation content
- ZIP with path traversal entry names
- ZIP bomb
- Real file renamed with .zip extension
- File with special chars in custom instructions (emoji, RTL, quotes)

---

## Output File

Full test plan at:
`/home/jared/projects/AI-CIV/aether/exports/migration-portal-qa-test-plan.md`

Total test cases: ~70 across functional, edge case, security, responsive, performance, acceptance criteria.
