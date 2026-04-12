# LIACL: Lightweight Inter-Agent Compression Language

**Purpose**: Reduce token overhead in agent-to-agent handoffs by 3:1 to 5:1.

## When to Use

- Agent-to-agent handoffs (status reports, audit findings, structured results)
- BOOP cycle reports
- Multi-agent synthesis inputs

## When NOT to Use

- Human-facing output (Jared, Telegram, blog content)
- First-time explanations of novel concepts
- Creative/narrative content

## Standard Vocabulary

| Key | Values | Meaning |
|-----|--------|---------|
| `status:` | complete\|in-progress\|blocked\|error | Task status |
| `issues:N` | integer | Count of problems found |
| `P1/P2/P3` | prefix | Priority levels (1=critical) |
| `files:` | comma-separated paths | Files involved |
| `rec:` | text | Recommendation |
| `affects:` | scope descriptor | Impact scope |
| `fix:` | text | Recommended fix |
| `tokens:` | integer | Estimated token count |
| `delta:` | +N/-N | Change from previous |
| `blocked-by:` | text | What's blocking |
| `deps:` | comma-separated | Dependencies |
| `conf:` | high\|med\|low | Confidence level |

## Format Rules

1. One concept per line
2. Key:value pairs, pipe-separated for multiple values on one line
3. No articles (a, an, the), no filler words
4. Paths abbreviated: `tools/telegram_bridge.py` → `tg_bridge.py`
5. Section headers in `[BRACKETS]`

## Examples

### Security Audit

```
[SECURITY-AUDIT] status:complete issues:3
P1: XSS@chatbox.js:45 innerHTML=user-input fix:textContent
P2: OAuth URL missing hostname-allowlist
P3: window.*=sensitive-state fix:remove-exports
rec:fix-P1-first affects:all-users
```

### Token Audit

```
[TOKEN-AUDIT] status:complete
CLAUDE.md: 174L ~3200tok delta:-5190
CLAUDE-CORE.md: 420L ~4800tok delta:0
CLAUDE-OPS.md: 580L ~5200tok delta:-200
MEMORY.md: 195L ~1600tok delta:+50
total: ~14800tok target:<10000 delta:-5340
rec:compress-CLAUDE-OPS stale-sections-found:3
```

### Research Summary

```
[RESEARCH] topic:competitor-pricing status:complete
sources:5 conf:high
finding-1: competitor-X raised tier-2 $99→$149
finding-2: market-avg SMB=$120/mo
finding-3: churn-rate industry=8%
full-report:/tmp/research-pricing-2026-02-27.md
rec:hold-current-pricing competitive-position:strong
```

### Build Report

```
[BUILD] status:complete files:3
exports/plugin-v465.php: CSP+connect-src added
exports/chatbox-v44.html: env-detect+body-fix+flowComplete
wp-pages:688,689 updated
tests:passed security:reviewed qa:passed
blocked-by:none ship:ready
```

## Invocation Prompt Addition

Add to agent prompts when LIACL is appropriate:

> "Respond in LIACL format: key:value pairs, [SECTION] headers, no prose. One concept per line. See .claude/templates/LIACL-REFERENCE.md for vocabulary."
