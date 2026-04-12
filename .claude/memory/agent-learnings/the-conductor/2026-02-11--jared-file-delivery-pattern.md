# Jared File Delivery Pattern

**Date**: 2026-02-11
**Type**: operational
**Confidence**: high
**Tags**: jared, file-delivery, telegram, mac, infrastructure

## Context

Jared needed files saved to his Mac's OneDrive folder. The Linux server (aether-jared) cannot directly access his Mac filesystem - they're on different networks.

## Key Discovery

**Telegram file delivery works perfectly.** Use the bot API to send documents directly to Jared's Telegram.

## Jared's Mac Paths

- **OneDrive folder**: `/Users/jaredsanborn/Library/CloudStorage/OneDrive-Personal/`
- **Pure Brain folder**: `/Users/jaredsanborn/Library/CloudStorage/OneDrive-Personal/1. Pure Brands/16. Pure Brain/`
- **Mac username**: `jaredsanborn`
- **Mac local IP** (changes): `192.168.1.153` (as of 2026-02-11)

## The Pattern

When Jared needs a file on his Mac:

```bash
# Send any file to Jared via Telegram
curl -F "chat_id=548906264" \
     -F "document=@/path/to/file.md" \
     "https://api.telegram.org/bot8559081952:AAHcLiEcC3GtQCAHRu5yc86BByiiLDqyjz0/sendDocument"
```

He can then download it from Telegram to wherever he wants on his Mac.

## What Doesn't Work

- **Direct SSH to Mac**: Linux server can't reach Mac's local IP (different networks)
- **File sharing services**: Most blocked or unreliable (transfer.sh, 0x0.st, ix.io down)
- **Git push**: SSH key issues on this server

## What Works

1. **Telegram file delivery** (best option)
2. **termbin.com** for text files (gives URL to curl)
3. **Copy/paste** from terminal output (low-tech fallback)

## Future Note

Jared mentioned wanting to set up local agents on his Mac desktop - noted for later implementation.
