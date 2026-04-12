"""PureSurf Social Suite — Sheet Sync
Google Sheets sync endpoint for the social dashboard.

When a post is approved/updated in the social dashboard, the frontend calls
POST /social/sheet-sync to write the status back to the LinkedIn Post Content
Calendar spreadsheet.

Uses Google Sheets REST API directly via httpx (no google-api-python-client needed).

INTEGRATION:
  This module exports `extend_sheet_sync_router()` which takes the existing
  social router + sessions_ref + auth_fn and adds the sheet-sync endpoint.
  Call it after `create_social_router()` in baas_server_simple.py.

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
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

log = logging.getLogger('baas.social.sheet_sync')

# ==================== CONFIGURATION ====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OAUTH_TOKEN_PATH = os.path.join(BASE_DIR, 'oauth-token.json')

SHEETS_API_BASE = 'https://sheets.googleapis.com/v4/spreadsheets'

# Default spreadsheet (LinkedIn Post Content Calendar)
DEFAULT_SHEET_ID = '1yIjmsxFNujvNsopTuTdnbPqzTUVW-FKumLfiwCjA-d4'
DEFAULT_TAB = 'Linkedin Post Content Calendar'

# Column mapping for the spreadsheet:
# A=Week, B=Day, C=Date, D=Platform, E=Type, F=Post Text, G=Status
COL_PLATFORM = 'D'
COL_CONTENT = 'F'
COL_STATUS = 'G'


# ==================== MODELS ====================

class SheetSyncRequest(BaseModel):
    spreadsheet_id: Optional[str] = None
    tab: Optional[str] = None
    platform: str = 'unknown'
    content: str = ''
    status: str = 'Draft'  # Draft | Final | Live | Failed
    scheduled_date: Optional[str] = None
    post_id: str = ''


# ==================== GOOGLE SHEETS AUTH ====================

_cached_token: dict = {}
_token_expiry: float = 0


def _load_oauth_token() -> dict:
    """Load OAuth token from disk."""
    global _cached_token, _token_expiry

    # Return cached if still fresh (tokens last 1 hour, refresh at 50 min)
    if _cached_token and time.time() < _token_expiry:
        return _cached_token

    if not os.path.exists(OAUTH_TOKEN_PATH):
        raise RuntimeError(f'OAuth token not found at {OAUTH_TOKEN_PATH}')

    with open(OAUTH_TOKEN_PATH) as f:
        token_data = json.load(f)

    _cached_token = token_data
    _token_expiry = time.time() + 2400  # Cache for 40 min (refresh before expiry)
    return token_data


def _refresh_token(token_data: dict) -> str:
    """Refresh the OAuth2 access token using the refresh token."""
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

    # Update cached + disk
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
    """Get a valid access token, refreshing if needed."""
    token_data = _load_oauth_token()
    access_token = token_data.get('token', '')

    # Quick validation: try a lightweight API call
    # For efficiency, just always refresh if we don't have a recent token
    if not access_token or time.time() >= _token_expiry - 600:
        return _refresh_token(token_data)

    return access_token


# ==================== SHEETS OPERATIONS ====================

def _status_color(status: str) -> dict:
    """Return Google Sheets cell color for status.
    Draft=red, Final=yellow, Live=green, Failed=dark red."""
    colors = {
        'Draft': {'red': 0.92, 'green': 0.36, 'blue': 0.36},   # Red
        'Final': {'red': 1.0, 'green': 0.85, 'blue': 0.0},     # Yellow
        'Live':  {'red': 0.34, 'green': 0.73, 'blue': 0.38},   # Green
        'Failed': {'red': 0.6, 'green': 0.0, 'blue': 0.0},     # Dark red
    }
    return colors.get(status, {'red': 0.8, 'green': 0.8, 'blue': 0.8})


async def _find_or_append_row(access_token: str, sheet_id: str, tab: str,
                               post_id: str, platform: str) -> int:
    """Find existing row for post_id, or find next empty row.
    Returns 0-indexed row number."""

    headers = {'Authorization': f'Bearer {access_token}'}

    # Read column A (post IDs or week labels) + column D (platform) to find existing row
    # Also check a dedicated post_id column if it exists, or scan content
    url = f'{SHEETS_API_BASE}/{sheet_id}/values/{tab}!A1:G200'
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, headers=headers)

    if resp.status_code == 401:
        # Token expired, caller should retry after refresh
        raise RuntimeError('TOKEN_EXPIRED')
    if resp.status_code != 200:
        log.error(f'Sheets API read failed: {resp.status_code} {resp.text}')
        raise RuntimeError(f'Sheets API error: {resp.status_code}')

    data = resp.json()
    rows = data.get('values', [])

    # Look for a row that already has this post_id in column A or content match
    for i, row in enumerate(rows):
        # Skip header row
        if i == 0:
            continue
        # Check if column A contains the post_id
        if len(row) > 0 and row[0] == post_id:
            return i

    # No existing row found — find first empty row
    # An empty row is one where columns A through G are all empty
    for i, row in enumerate(rows):
        if i == 0:
            continue
        if not any(cell.strip() for cell in row if cell):
            return i

    # All rows filled — append at the end
    return len(rows)


async def _write_row(access_token: str, sheet_id: str, tab: str,
                      row_idx: int, post_id: str, platform: str,
                      content: str, status: str, scheduled_date: str):
    """Write post data to a specific row."""

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Row is 0-indexed internally, Sheets API uses 1-indexed
    sheet_row = row_idx + 1

    # Write values: A=post_id, D=platform, F=content, G=status
    # We'll write the whole A:G range for this row
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    day_name = datetime.now(timezone.utc).strftime('%A')

    row_values = [
        post_id,                          # A: Post ID
        day_name,                         # B: Day
        scheduled_date or today,          # C: Date
        platform.capitalize(),            # D: Platform
        'Social Post',                    # E: Type
        content[:500] if content else '', # F: Post Text (clipped)
        status,                           # G: Status
    ]

    url = f'{SHEETS_API_BASE}/{sheet_id}/values/{tab}!A{sheet_row}:G{sheet_row}?valueInputOption=USER_ENTERED'
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.put(url, headers=headers, json={
            'range': f'{tab}!A{sheet_row}:G{sheet_row}',
            'majorDimension': 'ROWS',
            'values': [row_values],
        })

    if resp.status_code == 401:
        raise RuntimeError('TOKEN_EXPIRED')
    if resp.status_code not in (200, 201):
        log.error(f'Sheets write failed: {resp.status_code} {resp.text}')
        raise RuntimeError(f'Sheets write error: {resp.status_code}')

    log.info(f'Sheet sync: wrote row {sheet_row} — post_id={post_id} status={status}')

    # Now apply cell formatting (status color) via batchUpdate
    await _format_status_cell(access_token, sheet_id, tab, row_idx, status)


async def _format_status_cell(access_token: str, sheet_id: str, tab: str,
                                row_idx: int, status: str):
    """Apply background color to the status cell (column G)."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Get sheet ID (gid) for the tab
    tab_sheet_id = await _get_tab_sheet_id(access_token, sheet_id, tab)
    if tab_sheet_id is None:
        log.warning(f'Could not find sheet gid for tab "{tab}", skipping color format')
        return

    color = _status_color(status)

    batch_body = {
        'requests': [{
            'repeatCell': {
                'range': {
                    'sheetId': tab_sheet_id,
                    'startRowIndex': row_idx,
                    'endRowIndex': row_idx + 1,
                    'startColumnIndex': 6,  # Column G = index 6
                    'endColumnIndex': 7,
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': color,
                        'textFormat': {'bold': True},
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
        log.warning(f'Status color format failed: {resp.status_code} {resp.text}')
    else:
        log.info(f'Sheet sync: colored status cell row {row_idx + 1} → {status}')


async def _get_tab_sheet_id(access_token: str, sheet_id: str, tab: str) -> Optional[int]:
    """Get the numeric sheet ID (gid) for a tab name."""
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


# ==================== ROUTER EXTENSION ====================

def extend_sheet_sync_router(router: APIRouter, sessions_ref: dict, auth_fn):
    """Add /sheet-sync endpoint to the social router."""

    @router.post('/sheet-sync')
    async def sheet_sync(req: SheetSyncRequest, x_api_key: str = Header(None)):
        """Sync a social post status to Google Sheets spreadsheet."""
        auth_fn(x_api_key)

        sheet_id = req.spreadsheet_id or DEFAULT_SHEET_ID
        tab = req.tab or DEFAULT_TAB

        try:
            access_token = _get_access_token()
        except RuntimeError as e:
            log.error(f'Sheet sync auth failed: {e}')
            raise HTTPException(500, f'Google Sheets auth failed: {e}')

        # Retry once on token expiry
        for attempt in range(2):
            try:
                row_idx = await _find_or_append_row(
                    access_token, sheet_id, tab, req.post_id, req.platform
                )
                await _write_row(
                    access_token, sheet_id, tab, row_idx,
                    req.post_id, req.platform, req.content,
                    req.status, req.scheduled_date
                )
                return {
                    'ok': True,
                    'row': row_idx + 1,
                    'post_id': req.post_id,
                    'status': req.status,
                }
            except RuntimeError as e:
                if str(e) == 'TOKEN_EXPIRED' and attempt == 0:
                    log.info('Token expired, refreshing...')
                    token_data = _load_oauth_token()
                    access_token = _refresh_token(token_data)
                    continue
                raise HTTPException(500, f'Sheet sync failed: {e}')

    log.info('Sheet sync endpoint registered at /social/sheet-sync')
