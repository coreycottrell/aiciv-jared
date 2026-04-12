# Portal: Reply References Made Clickable with Scroll-to-Original

**Date**: 2026-03-20
**Type**: operational + teaching
**File**: ~/purebrain_portal/portal-pb-styled.html

## What Was Done

Made reply quote blocks in the PureBrain Portal chat clickable so clicking scrolls to the original message being replied to, with a gold highlight animation.

## What Already Existed

The quote block already had cursor:pointer CSS, a title tooltip, and a text-search click handler. The handler was fragile: searched all bubbles for first 40 chars of quoted text — could match wrong message or quote block itself.

## Changes Made (5 total)

1. **ID embedded in reply prefix** (send logic): `[replying to Sender (id:MSG_ID): "text"]`
2. **Updated parse regex** (both addMessage + startAssistantStream): extracts 3 groups — sender, optional id, text
3. **quoteMeta.origId**: new field populated from regex group 2
4. **Click handler**: direct `querySelector('[data-id="origId"]')` lookup first, text-search fallback for old messages
5. **CSS reply-highlight animation**: gold pulse keyframe animation instead of inline style.outline

## Key Pattern

`data-id` attribute on `.msg` elements is the correct scroll target. ID-first lookup is O(1). Always include text-search fallback for chat history predating the ID-embedding change.

## Portal Server

Port 8097 (default). Process: `python3 ~/purebrain_portal/portal_server.py`
