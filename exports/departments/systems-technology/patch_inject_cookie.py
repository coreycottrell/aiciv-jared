#!/usr/bin/env python3
"""Add a /sessions/{sid}/inject-li-at endpoint to baas_server_simple.py
for easily injecting LinkedIn auth token."""

SOURCE = '/opt/baas/baas_server_simple.py'
with open(SOURCE, 'r') as f:
    code = f.read()

# Find the cookies import endpoint and add our new endpoint after it
marker = "@app.post('/sessions/{sid}/cookies/import')"
idx = code.find(marker)
if idx == -1:
    print('ERROR: Could not find cookies import endpoint')
    exit(1)

# Find the next endpoint after cookies/import (look for next @app. decorator)
next_at = code.find('\n@app.', idx + len(marker))
if next_at == -1:
    print('ERROR: Could not find next endpoint')
    exit(1)

new_endpoint = '''

class InjectLinkedInCookieReq(BaseModel):
    li_at: str  # The li_at cookie value from browser DevTools

@app.post('/sessions/{sid}/inject-li-at')
async def inject_linkedin_auth(sid: str, req: InjectLinkedInCookieReq, x_api_key: str = Header(None)):
    """Inject a li_at cookie into a LinkedIn session.

    To get the li_at value:
    1. Open LinkedIn in your regular browser
    2. Open DevTools (F12) -> Application -> Cookies -> linkedin.com
    3. Find 'li_at' cookie and copy its value
    4. POST it here

    This enables the PureSurf session to be authenticated as your LinkedIn account.
    """
    _verify_session_access(sid, x_api_key)
    s = sessions.get(sid)
    if not s:
        raise HTTPException(404, 'Session not found')

    page = s['page']

    # Set the li_at cookie
    await page.context.add_cookies([{
        'name': 'li_at',
        'value': req.li_at,
        'domain': '.www.linkedin.com',
        'path': '/',
        'secure': True,
        'httpOnly': True,
        'sameSite': 'None',
    }])

    # Also set on .linkedin.com domain
    await page.context.add_cookies([{
        'name': 'li_at',
        'value': req.li_at,
        'domain': '.linkedin.com',
        'path': '/',
        'secure': True,
        'httpOnly': True,
        'sameSite': 'None',
    }])

    # Save cookies immediately
    count = await _save_cookies(sid, page)

    log.info(f'Injected li_at cookie for session {sid} ({len(req.li_at)} chars)')

    return {
        'status': 'injected',
        'session_id': sid,
        'cookie_name': 'li_at',
        'cookie_length': len(req.li_at),
        'cookies_saved': count,
        'next_step': f'Navigate to https://www.linkedin.com/feed/ to verify login',
    }

'''

# Insert before the next endpoint
code = code[:next_at] + new_endpoint + code[next_at:]

with open(SOURCE, 'w') as f:
    f.write(code)

print('SUCCESS: Added /sessions/{sid}/inject-li-at endpoint')
print('Usage:')
print('  1. Create session: POST /sessions {"profile_name": "jared-linkedin"}')
print('  2. Inject cookie: POST /sessions/jared-linkedin/inject-li-at {"li_at": "YOUR_TOKEN_HERE"}')
print('  3. Navigate: POST /sessions/jared-linkedin/navigate {"url": "https://www.linkedin.com/feed/"}')
print('  4. Verify logged in and post with images')
