#!/usr/bin/env python3
"""Patch purebrain_log_server.py to rewrite magic links to purebrain.ai subdomains."""
import sys

FILE = '/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py'

with open(FILE, 'r') as f:
    content = f.read()

# === PATCH 1: Rewrite magic_link to purebrain.ai subdomain ===
old_block = "        # Use portal_url as the link if magic_link not provided\n        link = magic_link or portal_url\n\n        # 3. Idempotency check"

new_block = """        # Use portal_url as the link if magic_link not provided
        link = magic_link or portal_url

        # 2b. Derive purebrain.ai subdomain and rewrite magic link
        # Pattern: {ainame}{humanfirstname}.purebrain.ai (lowercase, no hyphens)
        import re as _re_url
        from urllib.parse import urlparse as _urlparse
        _pb_subdomain = ''
        _pb_url = ''
        if civ_name and human_name:
            _ai_part = _re_url.sub(r'[^a-z0-9]', '', civ_name.lower())
            _first_part = _re_url.sub(r'[^a-z0-9]', '', human_name.lower().split()[0]) if human_name else ''
            _pb_subdomain = (_ai_part + _first_part)[:63]
            if _pb_subdomain and link:
                _parsed = _urlparse(link)
                _path = _parsed.path if _parsed.path and _parsed.path != '/' else ''
                _query = f'?{_parsed.query}' if _parsed.query else ''
                _pb_url = f'https://{_pb_subdomain}.purebrain.ai{_path}{_query}'
                if not _path and not _query:
                    _pb_url = f'https://{_pb_subdomain}.purebrain.ai/'
                logger.info(f'Magic link rewritten: {link} -> {_pb_url}')
            elif _pb_subdomain:
                _pb_url = f'https://{_pb_subdomain}.purebrain.ai/'

        # Use purebrain.ai URL if available, original link as fallback
        customer_link = _pb_url or link

        # 3. Idempotency check"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print('PATCH 1: Applied (magic link rewrite)')
else:
    print('PATCH 1: FAILED - block not found')
    sys.exit(1)

# === PATCH 2: Update log entry to store both URLs ===
old_log = "            'magic_link': link,"
new_log = "            'magic_link': customer_link,\n            'original_magic_link': link,\n            'purebrain_url': _pb_url,\n            'purebrain_subdomain': _pb_subdomain,"

if old_log in content:
    content = content.replace(old_log, new_log, 1)
    print('PATCH 2: Applied (log stores both URLs + subdomain)')
else:
    print('PATCH 2: FAILED')

# === PATCH 3: Email uses customer_link ===
old_email = "        _send_birth_complete_email(human_email, human_name, civ_name, link)"
new_email = "        _send_birth_complete_email(human_email, human_name, civ_name, customer_link)"
if old_email in content:
    content = content.replace(old_email, new_email, 1)
    print('PATCH 3: Applied (email uses purebrain.ai URL)')
else:
    print('PATCH 3: FAILED')

# === PATCH 4: Telegram notification uses customer_link ===
old_tg = "        _notify_jared_birth_complete(human_email, human_name, civ_name, container, link)"
new_tg = "        _notify_jared_birth_complete(human_email, human_name, civ_name, container, customer_link)"
if old_tg in content:
    content = content.replace(old_tg, new_tg, 1)
    print('PATCH 4: Applied (Telegram uses purebrain.ai URL)')
else:
    print('PATCH 4: FAILED')

# === PATCH 5: portal-status endpoint returns purebrain_url if available ===
old_portal = "                            return jsonify({\n                                'ready': True,\n                                'portalUrl': entry.get('magic_link', ''),"
new_portal = "                            return jsonify({\n                                'ready': True,\n                                'portalUrl': entry.get('purebrain_url') or entry.get('magic_link', ''),"

if old_portal in content:
    content = content.replace(old_portal, new_portal, 1)
    print('PATCH 5: Applied (portal-status returns purebrain.ai URL)')
else:
    print('PATCH 5: SKIPPED (portal-status format differs)')

with open(FILE, 'w') as f:
    f.write(content)

print('\nAll patches written successfully.')
