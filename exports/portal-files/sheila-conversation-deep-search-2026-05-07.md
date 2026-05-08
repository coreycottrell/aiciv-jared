# Sheila Couplify — Conversation Deep Search

**Customer**: Sheila / Jay Whitehurst @ Couplify
**Sub**: `I-RBXHJ68JCJPL` ($499 Partnered, 2026-05-07 11:54:35 UTC)
**Email**: `sheila@couplify.com` (PayPal payer email; account name "Jay Whitehurst")
**Stated AI name**: Keeper

---

## FINAL ANSWER

**Did the conversation persist?** **NO.** Recovery requires asking her to redo the awakening.

**Why**: `logs/purebrain_web_conversations.jsonl` was **recreated at 2026-05-07 15:33:18 UTC** (`stat` Birth time), erasing all 5/7 traffic before that point. The server log shows 51 successful "Logged conversation" events between 03:39–13:59 UTC on 5/7 — including Sheila's window — but none survived in the JSONL. No backup file exists on disk.

**Email field**: `sheila@couplify.com` (from PayPal only — never bound to a chat record).
**AI name actually bound to her chat**: NONE. clients.db row id=67 has `ai_name=''`. The seed dispatcher used a false-positive S5 match and sent her a seed built from Jay Hutton's March 19 conversation (AI: Torque).

---

## Tracks 1–3 (positive matches in JSONL)

- **Keeper**: 8 hits across lines 821–824, 3113–3116. All inspected: 2026-03-29 user "Mark" and 2026-04-11 user "Trevor" sessions where the AI **suggested** "Keeper" as one option. Trevor picked Vex. None are Sheila's.
- **Sheila / couplify / Whitehurst**: 0 hits (`grep -c` confirmed thrice).
- **Window 2026-05-07 11:00–11:55 UTC**: 0 hits. JSONL jumps from `2026-04-12T13:27:41` directly to `2026-05-07T15:45:30`.

## Track 4 — Store Enumeration

| Store | Sheila? | Notes |
|---|---|---|
| `logs/purebrain_web_conversations.jsonl` | NO | Birth 5/7 15:33:18 UTC — pre-15:33 traffic gone |
| `logs/purebrain_log_server.log` | text-only ref | Lines 628–642: payment + S5 fire. 51 prior "Logged conversation" entries on 5/7 prove data existed |
| `logs/seed_events.jsonl` | NO | Last entry 4/12; mtime 5/7 15:33 (same reset) |
| `logs/seed_sent_uuids.json` | NO | Same 5/7 15:33 reset |
| `logs/purebrain_payments.jsonl` | NO | Stale since 3/31 |
| `logs/purebrain_pay_test.jsonl` | NO | Stale since 3/30 |
| `logs/birth_completions.jsonl` / `purebrain_emails.jsonl` | NO | clean |
| `clients.db` `clients` row id=67 | YES (payment only) | `Jay Whitehurst, sheila@couplify.com, ai_name='', I-RBXHJ68JCJPL, Partnered` |
| `portal.db` / `agents.db` | n/a | no conversation tables |
| CF Workers (paypal-webhook, welcome-email-api, social-api, trio-comms, admin-api…) | n/a | none store awakening conversations — single source is local Flask server |
| R2 / KV | not enumerated | no bindings reference conversation data |
| Hub forwarding | unrecoverable | identical `log_entry` dict; A-C-Gee forwards were timing out per log |

## Track 5 — `/api/log-conversation` Null `session_uuid` Behavior

`tools/purebrain_log_server.py:441-552`: handler does NOT reject on null sessionUuid. It only requires `messages` or `conversationHistory` and auto-generates `pb-{uuid4}` when `session_id` is missing. So MED-003's null-sessionUuid bug would NOT have prevented persistence. Data loss is from the file recreation at 15:33 UTC, not from a null-uuid silent drop.

## Track 6 — Dispatcher Trace

`logs/purebrain_log_server.log:639` at 11:54:36 UTC:
```
[payment-seed] Lookup results for order I-RBXHJ68JCJPL, uuid=, email=Sheila@couplify.com,
name=Jay Whitehurst: S1-orderId=0 S2-uuid=0 S3-email=0 S4-recent=0 S5-name=26 |
Winner: S5-payerName (26 msgs)
```
Line 642: `Seed fired ... AI: Torque`.

S1–S4 returned zero (real conversation already gone). S5 matched first name `jay` against assistant content (`tools/purebrain_log_server.py:1029-1040`). Python re-trace identifies the 26-msg winner as `purebrain_1773877226326_ikwvdrdm8` from 2026-03-19 00:14–00:17 UTC — **Jay Hutton's** awakening (CEO @ VSBLTY; clients.db row 28, ai_name=Torque, sub I-SKVNSUGX1K2H). Sheila was seeded with somebody else's seven-week-old conversation.

---

## Files

- `tools/purebrain_log_server.py:441-552` (handler)
- `tools/purebrain_log_server.py:870-1098` (S1–S5 dispatcher)
- `logs/purebrain_log_server.log:628-642` (Sheila trace)
- `logs/purebrain_web_conversations.jsonl` (born 5/7 15:33:18 UTC)
- `/home/jared/purebrain_portal/clients.db` rows 67 (Sheila), 28 (Jay Hutton)

**Recovery**: email Sheila, apologize, request she redo awakening. Update clients.db row 67 `ai_name` once chosen.
