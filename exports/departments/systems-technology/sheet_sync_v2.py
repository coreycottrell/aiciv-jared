"""PureSurf Social Suite — Sheet Sync v2
Auto-sync BaaS schedule records to Google Sheets.

When ANY schedule record is created/updated/deleted:
1. Find or create corresponding row in spreadsheet by baas_id
2. Update all columns: title, date, time, status, Drive URL, blog URL, LinkedIn URL, content type
3. Store the spreadsheet row number back in BaaS record
4. Log the sync timestamp

Uses Google Sheets REST API via httpx with OAuth2 credentials.

Author: dept-systems-technology
Date: 2026-04-06
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

import httpx

log = logging.getLogger('baas.sheet_sync_v2')

# ==================== CONFIGURATION ====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OAUTH_TOKEN_PATH = os.path.join(BASE_DIR, 'oauth-token.json')

SHEETS_API_BASE = 'https://sheets.googleapis.com/v4/spreadsheets'

# Default spreadsheet (LinkedIn Post Content Calendar)
DEFAULT_SHEET_ID = '1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4'
DEFAULT_TAB = 'Linkedin Post Content Calendar'

SCHEDULED_POSTS_FILE = os.path.join(BASE_DIR, 'scheduled_posts.json')

# Extended column mapping for v2:
# A=baas_id, B=Day, C=Date, D=Platform, E=Content Type, F=Title,
# G=Post Text (truncated), H=Status, I=Drive Folder, J=Blog URL,
# K=LinkedIn URL, L=Banner URL, M=Synced At
HEADER_ROW = [
    'baas_id', 'Day', 'Date', 'Platform', 'Content Type', 'Title',
    'Post Text', 'Status', 'Drive Folder', 'Blog URL',
    'LinkedIn URL', 'Banner URL', 'Synced At'
]

# ==================== GOOGLE AUTH ====================

_cached_token: dict = {}
_token_expiry: float = 0


def _load_oauth_token() -> dict:
    global _cached_token, _token_expiry
    if _cached_token and time.time() < _token_expiry:
        return _cached_token
    if not os.path.exists(OAUTH_TOKEN_PATH):
        raise RuntimeError(f'OAuth token not found at {OAUTH_TOKEN_PATH}')
    with open(OAUTH_TOKEN_PATH) as f:
        token_data = json.load(f)
    _cached_token = token_data
    _token_expiry = time.time() + 2400
    return token_data


def _refresh_token(token_data: dict) -> str:
    global _cached_token, _token_expiry
    resp = httpx.post('https://oauth2.googleapis.com/token', data={
        'client_id': token_data['client_id'],
        'client_secret': token_data['client_secret'],
        'refresh_token': token_data['refresh_token'],
        'grant_type': 'refresh_token',
    })
    if resp.status_code != 200:
        log.error(f'Token refresh failed: {resp.status_code} {resp.text}')
        raise RuntimeError(f'Google OAuth token refresh failed: {resp.status_code}')
    new_token = resp.json()['access_token']
    token_data['token'] = new_token
    _cached_token = token_data
    _token_expiry = time.time() + 2400
    try:
        with open(OAUTH_TOKEN_PATH, 'w') as f:
            json.dump(token_data, f, indent=2)
    except Exception as e:
        log.warning(f'Failed to persist refreshed token: {e}')
    return new_token


def _get_access_token() -> str:
    token_data = _load_oauth_token()
    access_token = token_data.get('token', '')
    if not access_token or time.time() >= _token_expiry - 600:
        return _refresh_token(token_data)
    return access_token


# ==================== SHEETS OPERATIONS ====================

STATUS_COLORS = {
    'draft': {'red': 0.92, 'green': 0.36, 'blue': 0.36},
    'approved': {'red': 0.26, 'green': 0.52, 'blue': 0.96},
    'scheduled': {'red': 1.0, 'green': 0.85, 'blue': 0.0},
    'publishing': {'red': 1.0, 'green': 0.65, 'blue': 0.0},
    'posted': {'red': 0.34, 'green': 0.73, 'blue': 0.38},
    'failed': {'red': 0.6, 'green': 0.0, 'blue': 0.0},
}

STATUS_MAP = {
    'draft': 'Draft',
    'approved': 'Final',
    'scheduled': 'Scheduled',
    'publishing': 'Publishing',
    'posted': 'Live',
    'failed': 'Failed',
}


async def _ensure_header_row(access_token: str, sheet_id: str, tab: str):
    """Ensure the first row has our column headers."""
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'{SHEETS_API_BASE}/{sheet_id}/values/{tab}!A1:M1'

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code == 401:
        raise RuntimeError('TOKEN_EXPIRED')
    if resp.status_code != 200:
        log.warning(f'Could not read header row: {resp.status_code}')
        return

    data = resp.json()
    existing = data.get('values', [[]])
    first_row = existing[0] if existing else []

    # Check if headers already present
    if first_row and first_row[0] == 'baas_id':
        return

    # Write header row
    headers_req = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    url = f'{SHEETS_API_BASE}/{sheet_id}/values/{tab}!A1:M1?valueInputOption=USER_ENTERED'
    async with httpx.AsyncClient(timeout=15) as client:
        await client.put(url, headers=headers_req, json={
            'range': f'{tab}!A1:M1',
            'majorDimension': 'ROWS',
            'values': [HEADER_ROW],
        })
    log.info('Sheet header row written')


async def _find_row_by_baas_id(access_token: str, sheet_id: str, tab: str,
                                baas_id: str) -> Optional[int]:
    """Find the row index (0-based) that has this baas_id in column A.
    Returns None if not found."""
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'{SHEETS_API_BASE}/{sheet_id}/values/{tab}!A1:A500'

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code == 401:
        raise RuntimeError('TOKEN_EXPIRED')
    if resp.status_code != 200:
        log.error(f'Sheets API read failed: {resp.status_code} {resp.text}')
        return None

    rows = resp.json().get('values', [])
    for i, row in enumerate(rows):
        if i == 0:
            continue  # Skip header
        if row and row[0] == baas_id:
            return i
    return None


async def _find_next_empty_row(access_token: str, sheet_id: str, tab: str) -> int:
    """Find the next empty row (0-based index)."""
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'{SHEETS_API_BASE}/{sheet_id}/values/{tab}!A1:A500'

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code == 401:
        raise RuntimeError('TOKEN_EXPIRED')

    rows = resp.json().get('values', [])
    # Return the index after the last non-empty row
    return len(rows)


async def _write_post_to_row(access_token: str, sheet_id: str, tab: str,
                              row_idx: int, post: dict):
    """Write post data to a specific row (0-based index)."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    sheet_row = row_idx + 1  # Sheets API is 1-indexed
    now = datetime.now(timezone.utc)

    sched_time = post.get('scheduled_time', '')
    if sched_time:
        try:
            dt = datetime.fromisoformat(sched_time.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d')
            day_name = dt.strftime('%A')
        except Exception:
            date_str = sched_time[:10] if len(sched_time) >= 10 else sched_time
            day_name = ''
    else:
        date_str = now.strftime('%Y-%m-%d')
        day_name = now.strftime('%A')

    status = post.get('status', 'draft')
    status_display = STATUS_MAP.get(status, status.capitalize())

    row_values = [
        post.get('baas_id', post.get('id', '')),       # A: baas_id
        day_name,                                        # B: Day
        date_str,                                        # C: Date
        (post.get('platform', 'linkedin')).capitalize(), # D: Platform
        post.get('content_type', 'standalone'),          # E: Content Type
        post.get('title', ''),                           # F: Title
        (post.get('content', ''))[:500],                 # G: Post Text
        status_display,                                  # H: Status
        post.get('drive_folder_url', ''),                # I: Drive Folder
        post.get('blog_url', ''),                        # J: Blog URL
        post.get('linkedin_post_url', ''),               # K: LinkedIn URL
        post.get('banner_url', post.get('banner_image', '')),  # L: Banner URL
        now.isoformat(),                                 # M: Synced At
    ]

    url = f'{SHEETS_API_BASE}/{sheet_id}/values/{tab}!A{sheet_row}:M{sheet_row}?valueInputOption=USER_ENTERED'
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.put(url, headers=headers, json={
            'range': f'{tab}!A{sheet_row}:M{sheet_row}',
            'majorDimension': 'ROWS',
            'values': [row_values],
        })

    if resp.status_code == 401:
        raise RuntimeError('TOKEN_EXPIRED')
    if resp.status_code not in (200, 201):
        log.error(f'Sheets write failed: {resp.status_code} {resp.text}')
        raise RuntimeError(f'Sheets write error: {resp.status_code}')

    log.info(f'Sheet sync: wrote row {sheet_row} — baas_id={post.get("id")} status={status_display}')

    # Apply status cell color
    await _format_status_cell(access_token, sheet_id, tab, row_idx, status)

    return sheet_row


async def _delete_row_by_baas_id(access_token: str, sheet_id: str, tab: str,
                                  baas_id: str):
    """Clear the row for a deleted post (don't actually delete the row to avoid shifting)."""
    row_idx = await _find_row_by_baas_id(access_token, sheet_id, tab, baas_id)
    if row_idx is None:
        return

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    sheet_row = row_idx + 1
    empty_row = [''] * len(HEADER_ROW)

    url = f'{SHEETS_API_BASE}/{sheet_id}/values/{tab}!A{sheet_row}:M{sheet_row}?valueInputOption=USER_ENTERED'
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.put(url, headers=headers, json={
            'range': f'{tab}!A{sheet_row}:M{sheet_row}',
            'majorDimension': 'ROWS',
            'values': [empty_row],
        })

    if resp.status_code in (200, 201):
        log.info(f'Sheet sync: cleared row {sheet_row} (deleted baas_id={baas_id})')


async def _format_status_cell(access_token: str, sheet_id: str, tab: str,
                                row_idx: int, status: str):
    """Apply background color to the status cell (column H = index 7)."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    tab_sheet_id = await _get_tab_sheet_id(access_token, sheet_id, tab)
    if tab_sheet_id is None:
        return

    color = STATUS_COLORS.get(status, {'red': 0.8, 'green': 0.8, 'blue': 0.8})

    batch_body = {
        'requests': [{
            'repeatCell': {
                'range': {
                    'sheetId': tab_sheet_id,
                    'startRowIndex': row_idx,
                    'endRowIndex': row_idx + 1,
                    'startColumnIndex': 7,  # Column H
                    'endColumnIndex': 8,
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': color,
                        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)',
            }
        }]
    }

    url = f'{SHEETS_API_BASE}/{sheet_id}:batchUpdate'
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json=batch_body)

    if resp.status_code not in (200, 201):
        log.warning(f'Status color format failed: {resp.status_code}')


async def _get_tab_sheet_id(access_token: str, sheet_id: str, tab: str) -> Optional[int]:
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'{SHEETS_API_BASE}/{sheet_id}?fields=sheets.properties'
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=headers)
    if resp.status_code != 200:
        return None
    for sheet in resp.json().get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('title') == tab:
            return props.get('sheetId')
    return None


# ==================== MAIN SYNC FUNCTION ====================

async def sync_post_to_sheet(post: dict, action: str = 'upsert',
                              sheet_id: str = None, tab: str = None):
    """
    Main sync entry point. Called after every BaaS schedule write.

    - action='upsert': create or update row
    - action='delete': clear the row
    """
    sheet_id = sheet_id or DEFAULT_SHEET_ID
    tab = tab or DEFAULT_TAB
    baas_id = post.get('baas_id', post.get('id', ''))

    if not baas_id:
        log.warning('Cannot sync post without baas_id')
        return

    # Get access token with retry
    for attempt in range(2):
        try:
            access_token = _get_access_token()

            if action == 'delete':
                await _delete_row_by_baas_id(access_token, sheet_id, tab, baas_id)
                return

            # Ensure headers exist
            await _ensure_header_row(access_token, sheet_id, tab)

            # Find existing row or create new
            row_idx = await _find_row_by_baas_id(access_token, sheet_id, tab, baas_id)
            if row_idx is None:
                row_idx = await _find_next_empty_row(access_token, sheet_id, tab)

            # Write the row
            sheet_row = await _write_post_to_row(access_token, sheet_id, tab, row_idx, post)

            # Store row number back in BaaS record
            _update_post_row(baas_id, sheet_row)

            log.info(f'Sheet sync complete: {baas_id} -> row {sheet_row}')
            return

        except RuntimeError as e:
            if str(e) == 'TOKEN_EXPIRED' and attempt == 0:
                log.info('Token expired during sync, refreshing...')
                token_data = _load_oauth_token()
                _refresh_token(token_data)
                continue
            raise


def _update_post_row(baas_id: str, sheet_row: int):
    """Update the spreadsheet_row field in the scheduled posts file."""
    try:
        with open(SCHEDULED_POSTS_FILE) as f:
            posts = json.load(f)
        if baas_id in posts:
            posts[baas_id]['spreadsheet_row'] = sheet_row
            with open(SCHEDULED_POSTS_FILE, 'w') as f:
                json.dump(posts, f, indent=2, default=str)
    except Exception as e:
        log.warning(f'Failed to update spreadsheet_row for {baas_id}: {e}')


# ==================== LEGACY COMPAT: extend_sheet_sync_router ====================

def extend_sheet_sync_router(router, sessions_ref: dict, auth_fn):
    """Add /sheet-sync endpoint to the social router (backward compat)."""

    from pydantic import BaseModel as _BM
    from typing import Optional as _Opt
    from fastapi import Header as _H, HTTPException as _HE

    class SheetSyncRequest(_BM):
        spreadsheet_id: _Opt[str] = None
        tab: _Opt[str] = None
        platform: str = 'unknown'
        content: str = ''
        status: str = 'Draft'
        scheduled_date: _Opt[str] = None
        post_id: str = ''

    @router.post('/sheet-sync')
    async def sheet_sync(req: SheetSyncRequest, x_api_key: str = _H(None)):
        auth_fn(x_api_key)

        # Convert to v2 post format and sync
        post = {
            'id': req.post_id,
            'baas_id': req.post_id,
            'platform': req.platform,
            'content': req.content,
            'status': req.status.lower(),
            'scheduled_time': req.scheduled_date,
        }

        try:
            await sync_post_to_sheet(
                post, 'upsert',
                sheet_id=req.spreadsheet_id or DEFAULT_SHEET_ID,
                tab=req.tab or DEFAULT_TAB,
            )
            return {'ok': True, 'post_id': req.post_id, 'status': req.status}
        except Exception as e:
            log.error(f'Sheet sync failed: {e}')
            raise _HE(500, f'Sheet sync failed: {e}')

    log.info('Sheet sync v2 endpoints registered')
