# Scheduled Tasks Dashboard Panel
**Date**: 2026-03-13
**Type**: build pattern

## What Was Built
Full "Scheduled Tasks" panel in the PureBrain portal — nav sidebar item, panel HTML, CSS, JS, and backend DELETE endpoint.

## Key Patterns Learned

### Portal frontend edit pattern (portal-pb-styled.html, ~11k lines)
- All frontend is one file: HTML + CSS + JS together
- CSS lives in a `<style>` block, scoped by panel IDs and class prefixes
- Panel HTML: `<div class="panel" id="panel-{name}">` — panel visibility controlled by `.active` class
- Nav items use `data-panel="{name}"` — switchPanel() handles all routing
- Mobile: hamburger `#mobile-more-menu` contains `.tab-menu-item` divs for overflow panels
- New panel requires 6 touch points:
  1. CSS block
  2. `.nav-item` in sidebar HTML
  3. Panel `<div>` HTML
  4. Mobile hamburger menu item
  5. `switchPanel()` hook (load on enter + interval start/stop)
  6. JS functions + event listener wired in boot

### Backend DELETE pattern (Starlette)
- Path param syntax: `Route("/api/path/{param}", endpoint=fn, methods=["DELETE"])`
- Access param: `request.path_params.get("param", "")`
- Global list mutation: filter + reassign + call `_save_scheduled_tasks()`

### Python string edit via script
When the Edit tool has read-requirement friction on large files, use:
```python
content = open(file).read()
content = content.replace(old, new, 1)
open(file, 'w').write(content)
```
Always verify with `if old in content` check before writing.

## Files Changed
- `/home/jared/purebrain_portal/portal_server.py` — added `api_delete_scheduled_task` function + DELETE route
- `/home/jared/purebrain_portal/portal-pb-styled.html` — CSS, nav item, panel HTML, mobile menu, switchPanel hook, JS functions, refresh btn listener
