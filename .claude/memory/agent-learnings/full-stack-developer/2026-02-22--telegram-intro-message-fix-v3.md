# Telegram Intro Message Fix — pay-test-chat-flow-v3.js

**Date**: 2026-02-22
**Type**: operational
**Topic**: Surgical text-only fix to runTelegramSetup intro messages, deployed to pages 688 and 689

## What Was Changed

In `runTelegramSetup` function inside `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v3.js`:

### Old text (2 messages combined into one aiSay call):
```
`Alright ${firstName}, let's set up ${aiName}'s direct line to you.<br><br>` +
`${aiName} will reach you through <strong>Telegram</strong> \u2014 it's private, fast, and works everywhere. ` +
`Do you already have it installed on your phone?`
```

### New text (same aiSay call, new content):
```
`Alright ${firstName}, let's set up ${aiName}'s direct line back up connection to you.<br><br>` +
`Outside of ${aiName}'s main portal (Their Brain Stream), which will be set up by the end of this chat, ` +
`you can also communicate with ${aiName} on <strong>Telegram</strong>. ` +
`It's private, fast, and works everywhere, so let's connect it. ` +
`Do you already have it installed on your phone or computer?`
```

## Deployment Method

- Used Elementor REST API + full script block replacement
- Script start marker: `/* === Post-Payment Chat Flow v3`
- Script end detection: `window.logPayTestData  = logPayTestData;\n}`
- The entire JS block between those markers was replaced with the updated local file content
- Then elementor cache cleared via `DELETE /wp-json/elementor/v1/cache`

## Pages Affected
- Page 688: purebrain.ai/pay-test (PASS)
- Page 689: purebrain.ai/pay-test-sandbox (PASS)

## Key Pattern
When doing surgical JS edits to Elementor HTML widgets:
1. GET page with `?context=edit`
2. Parse `meta._elementor_data` JSON
3. Walk elements recursively to find HTML widget by content marker
4. Replace full script block (safer than string surgery on complex JS)
5. PUT back via REST
6. DELETE elementor cache

## Verification
Both pages confirmed via fresh REST GET: new text present, old text absent.
