#!/usr/bin/env python3
"""FIX 2: Re-enable TLS pre-navigation for LinkedIn cookie injection.

Uncomments the 11 lines marked TLS-REMOVED to restore the flow:
1. Navigate to linkedin.com/robots.txt (establishes TLS session)
2. Wait for page load
3. THEN inject cookies
4. THEN navigate to /feed/
"""
import sys

filepath = '/opt/baas/baas_server_simple.py'

with open(filepath, 'r') as f:
    content = f.read()

# The TLS-REMOVED block to uncomment
old_tls = """                # TLS-REMOVED: # Step 1: Navigate to establish TLS session with each auth domain
# TLS-REMOVED:                 if 'linkedin.com' in cookie_domains and auth_cookie_names:
# TLS-REMOVED:                     log.info(f'Session {session_id}: establishing TLS with linkedin.com BEFORE cookie injection...')
# TLS-REMOVED:                     try:
# TLS-REMOVED:                         await page.goto('https://www.linkedin.com/robots.txt', wait_until='domcontentloaded', timeout=20000)
# TLS-REMOVED:                         await asyncio.sleep(1)  # Let TLS session stabilize
# TLS-REMOVED:                         log.info(f'Session {session_id}: TLS session established with linkedin.com')
# TLS-REMOVED:                     except Exception as nav_err:
# TLS-REMOVED:                         log.warning(f'Session {session_id}: TLS pre-navigation failed: {nav_err} (proceeding anyway)')
# TLS-REMOVED:
# TLS-REMOVED:                 # Step 2: Now inject cookies (with domain normalization)"""

new_tls = """                # Step 1: Navigate to establish TLS session with each auth domain
                if 'linkedin.com' in cookie_domains and auth_cookie_names:
                    log.info(f'Session {session_id}: establishing TLS with linkedin.com BEFORE cookie injection...')
                    try:
                        await page.goto('https://www.linkedin.com/robots.txt', wait_until='domcontentloaded', timeout=20000)
                        await asyncio.sleep(1)  # Let TLS session stabilize
                        log.info(f'Session {session_id}: TLS session established with linkedin.com')
                    except Exception as nav_err:
                        log.warning(f'Session {session_id}: TLS pre-navigation failed: {nav_err} (proceeding anyway)')

                # Step 2: Now inject cookies (with domain normalization)"""

count = content.count(old_tls)
if count == 0:
    print("ERROR: Could not find TLS-REMOVED block to uncomment")
    sys.exit(1)
content = content.replace(old_tls, new_tls)
print(f"FIX 2: Re-enabled TLS pre-navigation ({count} occurrences)")

with open(filepath, 'w') as f:
    f.write(content)

print("FIX 2: COMPLETE — TLS pre-navigation restored")
