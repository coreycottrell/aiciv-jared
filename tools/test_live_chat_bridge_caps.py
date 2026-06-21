#!/usr/bin/env python3
"""Standalone self-test for live-chat-bridge inbound size caps + inbox rotation.

NO live server, NO Flask app run. Imports the pure helpers from purebrain_log_server
and asserts the disk-fill DoS hardening behaves correctly:

  - _bridge_oversized_field(): caps ALL 4 inbound types' free-text string fields
    (new_message.body / state_change.state / typing.who /
     visitor_presence.geo|page|ip_country) at LIVE_CHAT_BRIDGE_MAX_TEXT, and
    conversation_id at LIVE_CHAT_BRIDGE_MAX_CONVO_ID.
  - _rotate_inbox_if_needed(): single-roll size-based rotation of the append-only
    inbox JSONL to '<inbox>.1' once it crosses LIVE_CHAT_BRIDGE_INBOX_ROTATE_BYTES.

Run:  python3 tools/test_live_chat_bridge_caps.py
Exit code 0 == all assertions passed.
"""

import os
import sys
import tempfile

# Make sure we can import the server module regardless of CWD.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import purebrain_log_server as pls  # noqa: E402 (path set above)

MAX_TEXT = pls.LIVE_CHAT_BRIDGE_MAX_TEXT
MAX_CONVO = pls.LIVE_CHAT_BRIDGE_MAX_CONVO_ID
ROTATE = pls.LIVE_CHAT_BRIDGE_INBOX_ROTATE_BYTES

over_text = 'x' * (MAX_TEXT + 1)
at_text = 'x' * MAX_TEXT          # exactly at the cap == allowed (cap is strict '>')
over_convo = 'c' * (MAX_CONVO + 1)
ok_convo = 'c' * MAX_CONVO

_passed = 0


def check(label, cond):
    global _passed
    assert cond, f'FAILED: {label}'
    _passed += 1
    print(f'  ok  {label}')


def test_oversized_rejected():
    print('[1] oversized free-text fields are REJECTED (one per inbound type):')
    cases = [
        ('new_message.body',          {'type': 'new_message', 'body': over_text}),
        ('state_change.state',        {'type': 'state_change', 'state': over_text}),
        ('typing.who',                {'type': 'typing', 'who': over_text}),
        ('visitor_presence.geo',      {'type': 'visitor_presence', 'geo': over_text}),
        ('visitor_presence.page',     {'type': 'visitor_presence', 'page': over_text}),
        ('visitor_presence.ip_country', {'type': 'visitor_presence', 'ip_country': over_text}),
        ('conversation_id',           {'type': 'new_message', 'conversation_id': over_convo, 'body': 'hi'}),
    ]
    for label, payload in cases:
        offending = pls._bridge_oversized_field(payload)
        check(f'{label} -> rejected (offending={offending})', offending is not None)


def test_valid_accepted():
    print('[2] under-cap (valid) payloads are ACCEPTED for every inbound type:')
    cases = [
        ('new_message',      {'type': 'new_message', 'conversation_id': ok_convo,
                              'body': at_text, 'sender': 'visitor', 'msg_seq': 1}),
        ('state_change',     {'type': 'state_change', 'conversation_id': ok_convo,
                              'state': 'open'}),
        ('typing',           {'type': 'typing', 'conversation_id': ok_convo,
                              'who': 'visitor', 'typing': True}),
        ('visitor_presence', {'type': 'visitor_presence', 'conversation_id': ok_convo,
                              'geo': 'US-NY', 'page': '/pricing', 'ip_country': 'US'}),
    ]
    for label, payload in cases:
        offending = pls._bridge_oversized_field(payload)
        check(f'{label} -> accepted (offending={offending})', offending is None)


def test_rotation():
    print('[3] inbox rotation: file > threshold rolls to .1 (sparse file, no 50MB write):')
    tmpdir = tempfile.mkdtemp(prefix='lcb_caps_test_')
    inbox = os.path.join(tmpdir, 'inbox.jsonl')
    rolled = inbox + '.1'
    orig_inbox = pls.LIVE_CHAT_BRIDGE_INBOX
    try:
        # Point the helper at our temp inbox.
        pls.LIVE_CHAT_BRIDGE_INBOX = inbox

        # No file yet -> rotation is a safe no-op.
        pls._rotate_inbox_if_needed()
        check('no-file -> no-op (no .1 created)', not os.path.exists(rolled))

        # Small file under threshold -> no rotation.
        with open(inbox, 'w') as f:
            f.write('{"line": 1}\n')
        pls._rotate_inbox_if_needed()
        check('under-threshold -> not rotated', os.path.exists(inbox) and not os.path.exists(rolled))

        # Create a SPARSE file just over the threshold (truncate/seek, no real bytes).
        with open(inbox, 'wb') as f:
            f.truncate(ROTATE + 1)
        check('sparse file is > threshold', os.path.getsize(inbox) > ROTATE)

        # Put a stale .1 in place to prove single-roll OVERWRITES it.
        with open(rolled, 'w') as f:
            f.write('STALE')

        pls._rotate_inbox_if_needed()
        check('over-threshold -> main rotated away', not os.path.exists(inbox))
        check('over-threshold -> .1 exists', os.path.exists(rolled))
        check('over-threshold -> .1 overwrote stale (size matches rolled main)',
              os.path.getsize(rolled) == ROTATE + 1)
    finally:
        pls.LIVE_CHAT_BRIDGE_INBOX = orig_inbox
        for p in (inbox, rolled):
            try:
                os.remove(p)
            except OSError:
                pass
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass


def main():
    print('=== live-chat-bridge cap + rotation self-test ===')
    print(f'LIVE_CHAT_BRIDGE_MAX_TEXT          = {MAX_TEXT}')
    print(f'LIVE_CHAT_BRIDGE_MAX_CONVO_ID      = {MAX_CONVO}')
    print(f'LIVE_CHAT_BRIDGE_INBOX_ROTATE_BYTES= {ROTATE}')
    print()
    test_oversized_rejected()
    print()
    test_valid_accepted()
    print()
    test_rotation()
    print()
    print(f'ALL {_passed} ASSERTIONS PASSED')


if __name__ == '__main__':
    main()
