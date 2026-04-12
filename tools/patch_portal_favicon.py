#!/usr/bin/env python3
"""Patch portal_server.py to serve favicon + update page title."""

FILE = '/home/jared/purebrain_portal/portal_server.py'

with open(FILE, 'r') as f:
    content = f.read()

# === PATCH 1: Add favicon route function before "# Routes" comment ===
favicon_func = '''
# ── Favicon ──────────────────────────────────────────────────────────────

async def favicon(request: Request):
    """Serve PureBrain favicon for unified branding across all subdomains."""
    ico = SCRIPT_DIR / "favicon.ico"
    if ico.exists():
        return FileResponse(str(ico), media_type="image/x-icon")
    return Response(status_code=204)

async def favicon_png(request: Request):
    """Serve 32px favicon PNG."""
    png = SCRIPT_DIR / "favicon-32.png"
    if png.exists():
        return FileResponse(str(png), media_type="image/png")
    return Response(status_code=204)

async def apple_touch_icon(request: Request):
    """Serve Apple touch icon."""
    icon = SCRIPT_DIR / "apple-touch-icon.png"
    if icon.exists():
        return FileResponse(str(icon), media_type="image/png")
    return Response(status_code=204)

'''

old_routes_marker = "# Routes"
if old_routes_marker in content and "async def favicon" not in content:
    content = content.replace("# Routes", favicon_func + "# Routes")
    print("PATCH 1: Applied (favicon route functions)")
else:
    if "async def favicon" in content:
        print("PATCH 1: SKIPPED (already exists)")
    else:
        print("PATCH 1: FAILED (marker not found)")

# === PATCH 2: Add favicon routes to routes list ===
old_routes_list = '    Route("/", endpoint=index),'
new_routes_list = '''    Route("/favicon.ico", endpoint=favicon),
    Route("/favicon-32.png", endpoint=favicon_png),
    Route("/apple-touch-icon.png", endpoint=apple_touch_icon),
    Route("/", endpoint=index),'''

if old_routes_list in content and 'Route("/favicon.ico"' not in content:
    content = content.replace(old_routes_list, new_routes_list)
    print("PATCH 2: Applied (favicon routes added)")
else:
    if 'Route("/favicon.ico"' in content:
        print("PATCH 2: SKIPPED (already exists)")
    else:
        print("PATCH 2: FAILED")

with open(FILE, 'w') as f:
    f.write(content)

print("\nPortal server patches complete.")
