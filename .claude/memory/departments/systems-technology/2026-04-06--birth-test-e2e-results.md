# Birth Test E2E — 2026-04-06

**Type**: operational
**Topic**: Full onboarding pipeline E2E test results

## Key Findings

- Pipeline is HEALTHY — all API endpoints operational
- verify-payment-pages.sh: 111/113 checks passed
- 86 magic links stored, 26 seeds fired historically
- Domain rewrite (.ai-civ.com -> .app.purebrain.ai) working correctly
- Conversation lookup fallback chain (S1-S5) working

## Issues Found (Low Priority)

1. `/pay-test-sandbox-3/` and `/pay-test-sandbox-5/` still have legacy post-payment chatbox code (7 refs each)
2. `/insiders/awakened/` missing from local deploy dir but serves 200 on live site
3. Conversation-payment UUID mismatch only happens in test (real flow uses single UUID)

## API Field Names (for future tests)

- `/api/send-seed`: uses `session_uuid`, `ai_name`, `human_name`, `human_email`, `tier`, `order_id`, `is_sandbox`, `conversation`
- `/api/verify-payment`: uses `sessionUuid`, `orderId`, `subscriptionId`, `tier`, `amount`, `payerEmail`, `payerName`, `isSandbox` (camelCase!)
- `/api/log-conversation`: uses `session_uuid`, `page_url`, `messages`, `metadata`

## Test UUIDs Used

- `e2e-birth-test-1775480209` (seed test)
- `e2e-birth-test-verify-1775480265` (payment verify test)

## File References

- Report: `exports/departments/systems-technology/2026-04-06--birth-test-e2e-report.md`
- Onboarding spec: `.claude/ONBOARDING-SPEC-DEFINITIVE.md`
- Verification script: `tools/verify-payment-pages.sh`
