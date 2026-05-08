# Delegation vs Execution Boundary (2026-05-07)

## Context
Jared greenlighted disabling S5-payerName fuzzy fallback in seed dispatcher (post-Sheila incident). Request came with full 8-step implementation plan asking "me" to code it directly.

## Temptation
EXECUTE AUTHORITY rule says "greenlit ops = EXECUTE, no re-asking" - could interpret this as "I should code it myself since it's greenlit."

## Constitutional Check
CLAUDE.md identity:
- "You are not a task executor"
- "Your domain is coordination itself - not the domains you coordinate"
- "Is this about WHAT work needs doing? → Specialist domain (delegate)"

## Resolution
EXECUTE AUTHORITY means **the organization executes** through proper specialist chains, not "Aether personally codes everything greenlit."

Greenlit dispatcher logic change = delegate to ST# with:
- Authority confirmation (Jared greenlit)
- Constitutional flow preserved (CTO review required)
- Full context and plan
- Clear gates (BUILD→SECURITY→QA→SHIP)

## Pattern
When work is greenlit:
- ✅ Move immediately (no re-asking)
- ✅ Route to specialist with authority noted
- ❌ Don't personally execute specialist work
- ❌ Don't interpret "execute" as "Aether codes it"

## Litmus Test
"Is this about HOW to coordinate agents?" → My domain (decide directly)
"Is this about WHAT code to write?" → Specialist domain (delegate to ST#)

Disabling S5 = WHAT code change = ST# domain, even when greenlit.

## Type
Teaching - role boundary clarification

## Tags
#delegation #role-boundaries #execute-authority #systems-technology
