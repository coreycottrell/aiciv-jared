# 2026-05-08 — Lyra 3-Email Overnight Processing (Magic-Link Structural Gap Discovered)

**Type**: operational + teaching
**Topic**: Honest reply when requested data structurally doesn't exist; AgentMail SDK threading

## What Happened
Processed 3 Lyra-PMG emails overnight: (A) extract Mireille's 2 use-case emails for homepage,
(C) look up 11 portal magic links for Brevo welcome series, (B) review LinkedIn Live strategy doc.

## Key Findings
1. **Magic_link column is NULL for ALL 64 clients in `purebrain-social.clients` D1 (PROD)**
   AND all 63 rows in legacy `clients.db`. Brevo's MAGIC_LINK contact attribute is the
   source of truth — set externally, never mirrored to our admin DB. Of Lyra's 11 missing
   clients, only 2 even exist in our system (gadamo1314, donatobsms — both NULL).
   Harrison Amit exists under different email (Harrison@bisnce.com vs harrison.amit@ridehovr.com).

2. **AgentMail SDK threading**: parameter is `headers={'In-Reply-To': msg_id}` NOT
   `in_reply_to=...` as send_agentmail.py wrapper assumes. Wrapper has a bug — used
   raw client.inboxes.messages.send() directly instead.

3. **Drive API GDoc export**: GDriveManager has no `get_doc_content()` method;
   use `g.service.files().export(fileId=X, mimeType='text/plain').execute()` directly.

## Honest-Flag Pattern (CRITICAL)
When asked to look up data that doesn't exist, the right move is structural diagnosis,
not fabrication. For Email C, I documented the search across 4 stores, showed 0/64
column coverage, identified Brevo as the actual source-of-truth, and proposed sync
direction (Brevo→clients, not clients→Brevo). This is more useful than "here are
2 of 11" with 9 silent gaps.

## Sent Message-IDs
- Email A: `<0100019e073d2c68-04b83c28-ae44-470a-afe5-6d58b9fb4ac5-000000@email.amazonses.com>`
- Email C: `<0100019e073d2eaa-ce713f77-6030-40fe-aeb6-bbcc4a3e0596-000000@email.amazonses.com>`
- Email B: `<0100019e073d311a-f0c05476-f6f7-4855-a608-d0f4c829cb6a-000000@email.amazonses.com>`

## Files
- Deliverable: `/home/jared/projects/AI-CIV/aether/exports/portal-files/lyra-3-emails-overnight-processing-2026-05-08.md` (974 words)
- LinkedIn Live full review draft (Jared sign-off pending): `/home/jared/projects/AI-CIV/aether/exports/portal-files/aether-linkedin-live-strategy-review-2026-05-08.md`

## Followups
- Jared: review LinkedIn Live draft (Edit 5 voice-vs-text choice is the key decision)
- ST# / dept: scope a Brevo→clients magic_link sync if welcome series fix is to be done end-to-end
- Verify with Mireille the 68 vs 69 use-case count delta before homepage publish
