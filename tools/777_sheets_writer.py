#!/usr/bin/env python3
"""
777 Command Center — Bidirectional Sheets Writer
=================================================
Reads pending edits from pending-edits.json (or data/777-cache.db if
the D1 cache module is available) and writes them back to the Google
Sheets spreadsheet.

TABLE → SHEET MAPPING:
  daily_scores  → Sheet index [30] — Daily Reflection Process
                  key   = YYYY-MM-DD
                  field = 'score'   (writes individual question rows OR total)
  seven_fs      → Sheet index [36] — Weekly Edit
                  key   = week_date (YYYY-MM-DD)
                  field = one of: family|career|fitness|faith|finance|fellowship|fun
  goals         → Sheet index [15] (yearly) or [14] (top77)
                  key   = goal text (matched) OR row index as str
                  field = 'progress' | 'text'
  proof_wall    → Sheet index [28] — Proof Self-Discipline
                  key   = "YYYY-MM-DD:sort_order"
                  field = 'task'

AUTHENTICATION:
  Same GDriveManager OAuth2 used by 777_data_fetcher.py.

SOURCES for pending edits (in priority order):
  1. exports/777-command-center/pending-edits.json  (Vercel API writes here)
  2. data/777-cache.db pending_edits table         (SQLite cache writes here)

AUDIT TRAIL:
  Logs all writes to logs/777-sync.log (appended).

RUN:
  python3 tools/777_sheets_writer.py

Author: PTT full-stack-developer
"""

import json
import os
import sys
import time
from datetime import datetime, date, timedelta
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

PENDING_JSON  = ROOT / 'exports' / '777-command-center' / 'pending-edits.json'
AUDIT_LOG     = ROOT / 'logs' / '777-sync.log'
SHEET_ID      = '1HuJIWEEXpkHgpL2iI6Zit9_cxw3dNd_8zZkOzsK4BGk'

# Import helpers from fetcher (sheets_date_to_iso, safe_float, etc.)
# We import lazily inside functions to avoid import errors if path not set yet.


# ── Logging ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] [sheets_writer] {msg}"
    print(line)
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, 'a') as f:
            f.write(line + '\n')
    except Exception:
        pass


# ── Pending edits IO ──────────────────────────────────────────────────────────

def read_pending_json() -> list:
    """
    Read unsynced edits from pending-edits.json.
    Returns a list of edit dicts with synced_at == None.
    """
    if not PENDING_JSON.exists():
        return []
    try:
        with open(PENDING_JSON) as f:
            store = json.load(f)
        edits = store.get('edits', [])
        return [e for e in edits if not e.get('synced_at')]
    except Exception as exc:
        log(f"ERROR reading pending-edits.json: {exc}")
        return []


def mark_json_edits_synced(edit_ids: list) -> None:
    """Mark edits in pending-edits.json as synced."""
    if not PENDING_JSON.exists() or not edit_ids:
        return
    try:
        with open(PENDING_JSON) as f:
            store = json.load(f)
        now_iso = datetime.utcnow().isoformat() + 'Z'
        id_set = set(edit_ids)
        for e in store.get('edits', []):
            if e.get('id') in id_set:
                e['synced_at'] = now_iso
        with open(PENDING_JSON, 'w') as f:
            json.dump(store, f, indent=2)
        log(f"Marked {len(edit_ids)} JSON edit(s) synced.")
    except Exception as exc:
        log(f"ERROR marking JSON edits synced: {exc}")


def read_pending_db() -> list:
    """
    Read unsynced edits from the SQLite D1 cache (if available).
    Returns edits in the same dict format as pending-edits.json.
    """
    try:
        from tools.d1_cache_777 import get_pending_edits  # type: ignore
        edits = get_pending_edits()
        # Normalize to same dict shape as JSON edits
        for e in edits:
            e.setdefault('table_name', e.get('table', ''))
        return edits
    except ImportError:
        pass
    # Try direct import path
    try:
        sys.path.insert(0, str(ROOT / 'tools'))
        # Module file is named with leading digits — import via importlib
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            '777_d1_cache', ROOT / 'tools' / '777_d1_cache.py'
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.get_pending_edits()
    except Exception as exc:
        log(f"DB pending edits unavailable: {exc}")
        return []


def mark_db_edits_synced(edit_ids: list) -> None:
    """Mark DB edits as synced via 777_d1_cache."""
    if not edit_ids:
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            '777_d1_cache', ROOT / 'tools' / '777_d1_cache.py'
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.mark_edits_synced(edit_ids)
    except Exception as exc:
        log(f"ERROR marking DB edits synced: {exc}")


# ── Google Sheets auth ────────────────────────────────────────────────────────

def get_spreadsheet():
    """
    Authenticate via GDriveManager OAuth2 (same creds as the fetcher).
    Returns a gspread Spreadsheet object or raises.
    """
    import gspread
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ]

    # GDriveManager stores tokens here
    token_candidates = [
        ROOT / 'config' / 'gdrive_token.json',
        ROOT / 'tools' / 'gdrive_token.json',
        Path.home() / '.config' / 'gdrive_token.json',
    ]

    token_path = None
    for p in token_candidates:
        if p.exists():
            token_path = p
            break

    if not token_path:
        raise FileNotFoundError(
            "No gdrive_token.json found. Run 777_data_fetcher.py first to authenticate."
        )

    with open(token_path) as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=SCOPES,
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        updated = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': list(creds.scopes or SCOPES),
        }
        with open(token_path, 'w') as f:
            json.dump(updated, f, indent=2)

    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID)


# ── Date column finder ────────────────────────────────────────────────────────

def find_date_col(header_row: list, target_date: str) -> int:
    """
    Return the column index (0-based) in a header row that matches target_date (YYYY-MM-DD).
    Returns -1 if not found.
    """
    # Import sheets_date_to_iso from the fetcher module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        '777_data_fetcher', ROOT / 'tools' / '777_data_fetcher.py'
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sheets_date_to_iso = mod.sheets_date_to_iso

    for j, cell in enumerate(header_row):
        d = sheets_date_to_iso(str(cell))
        if d == target_date:
            return j
    return -1


# ── Writers per table ─────────────────────────────────────────────────────────

def write_daily_score(ws, edit: dict, all_vals: list) -> bool:
    """
    Write to Sheet [30]: Daily Reflection.
    edit keys: record_key = YYYY-MM-DD, field = 'score', new_value = int/float str

    The 'score' field maps to the TOTAL SCORE row (row index 23, 1-based row 24).
    We write the total directly into the total score row for that date column.
    """
    target_date = edit['record_key']  # YYYY-MM-DD
    new_value   = edit['new_value']

    if not all_vals or len(all_vals) < 24:
        log(f"  SKIP daily_score write — sheet too short ({len(all_vals)} rows)")
        return False

    header_row = all_vals[1]  # Row 1 (0-indexed) holds date columns
    col_idx = find_date_col(header_row, target_date)
    if col_idx < 0:
        log(f"  SKIP daily_score write — date {target_date} not found in header")
        return False

    # Row 23 (0-indexed) = TOTAL SCORE row → Sheets row 24
    sheets_row = 24
    sheets_col = col_idx + 1  # gspread uses 1-based col index

    try:
        ws.update_cell(sheets_row, sheets_col, new_value)
        log(f"  WROTE daily_scores: date={target_date} row={sheets_row} col={sheets_col} value={new_value}")
        return True
    except Exception as exc:
        log(f"  ERROR writing daily_scores: {exc}")
        return False


def write_seven_f(ws, edit: dict, all_vals: list) -> bool:
    """
    Write to Sheet [36]: Weekly Edit.
    edit keys: record_key = week_date (YYYY-MM-DD), field = f_name, new_value = int str

    F_MAP matches the same labels as in the fetcher.
    """
    target_date = edit['record_key']
    field       = edit['field']
    new_value   = edit['new_value']

    # Map canonical field name → label fragment to search for
    F_LABEL_MAP = {
        'family':     'family',
        'career':     'freedom',
        'fitness':    'fitness',
        'faith':      'faith',
        'finance':    'financial',
        'fellowship': 'fellowship',
        'fun':        'fun',
    }
    label_fragment = F_LABEL_MAP.get(field)
    if not label_fragment:
        log(f"  SKIP seven_fs write — unknown field: {field}")
        return False

    if not all_vals:
        log("  SKIP seven_fs write — empty sheet")
        return False

    # Header row (row 0) has date columns from col 2+
    header_row = all_vals[0]
    col_idx = find_date_col(header_row, target_date)
    if col_idx < 0:
        log(f"  SKIP seven_fs write — date {target_date} not in header")
        return False

    # Find the row containing the F label in col B (index 1)
    target_row_idx = None
    for i, row in enumerate(all_vals):
        if len(row) >= 2 and label_fragment in row[1].strip().lower():
            target_row_idx = i
            break

    if target_row_idx is None:
        log(f"  SKIP seven_fs write — label '{label_fragment}' not found in col B")
        return False

    sheets_row = target_row_idx + 1  # 1-based
    sheets_col = col_idx + 1

    try:
        ws.update_cell(sheets_row, sheets_col, new_value)
        log(f"  WROTE seven_fs: field={field} date={target_date} row={sheets_row} col={sheets_col} value={new_value}")
        return True
    except Exception as exc:
        log(f"  ERROR writing seven_fs: {exc}")
        return False


def write_goal(ws_yearly, ws_top77, edit: dict, yearly_vals: list, top77_vals: list) -> bool:
    """
    Write to goals sheets.
    edit keys:
      record_key = row index as str (e.g. '3') OR goal text snippet
      field      = 'progress' | 'text'
      new_value  = value string

    For yearly goals (Sheet [15]): progress goes in col B or C (whichever has %)
    For top77 goals (Sheet [14]): progress goes in col B
    """
    record_key  = edit['record_key']
    field       = edit['field']
    new_value   = edit['new_value']

    # Determine which sheet: record_key prefix "yearly:" or "top77:"
    # Default to yearly if no prefix
    if record_key.startswith('top77:'):
        sheet_key = record_key[6:]
        all_vals  = top77_vals
        ws        = ws_top77
    else:
        sheet_key = record_key.replace('yearly:', '')
        all_vals  = yearly_vals
        ws        = ws_yearly

    # Find target row: numeric index or text match
    target_row_idx = None
    try:
        idx = int(sheet_key)
        if 0 <= idx < len(all_vals):
            target_row_idx = idx
    except ValueError:
        # Text match
        for i, row in enumerate(all_vals):
            if row and sheet_key[:30].lower() in (row[0] or '').lower():
                target_row_idx = i
                break

    if target_row_idx is None:
        log(f"  SKIP goals write — key '{record_key}' not matched")
        return False

    sheets_row = target_row_idx + 1
    # progress → col B (index 1), text → col A (index 0)
    sheets_col = 2 if field == 'progress' else 1

    try:
        ws.update_cell(sheets_row, sheets_col, new_value)
        log(f"  WROTE goals: key={record_key} field={field} row={sheets_row} col={sheets_col} value={new_value}")
        return True
    except Exception as exc:
        log(f"  ERROR writing goals: {exc}")
        return False


def write_proof_task(ws, edit: dict, all_vals: list) -> bool:
    """
    Write to Sheet [28]: Proof Wall.
    edit keys:
      record_key = "YYYY-MM-DD:sort_order"
      field      = 'task'
      new_value  = task text

    Structure: date in col A, tasks in cols B-F.
    sort_order 0-4 maps to cols B-F.
    """
    record_key = edit['record_key']
    new_value  = edit['new_value']

    parts = record_key.split(':')
    if len(parts) < 2:
        log(f"  SKIP proof_wall write — invalid record_key: {record_key}")
        return False

    target_date  = parts[0]  # YYYY-MM-DD
    try:
        sort_order = int(parts[1])
    except ValueError:
        sort_order = 0

    # Find the row with that date in col A
    target_row_idx = None
    for i, row in enumerate(all_vals):
        if row and row[0].strip().startswith(target_date[:7]):  # Match YYYY-MM
            # Check full date match (Sheets may store as M/D/YY)
            cell_val = row[0].strip()
            # Try direct string comparison and also date parsing
            if target_date in cell_val or cell_val == target_date:
                target_row_idx = i
                break
            # Try parsing the cell date
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    '777_data_fetcher', ROOT / 'tools' / '777_data_fetcher.py'
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                parsed = mod.sheets_date_to_iso(cell_val)
                if parsed == target_date:
                    target_row_idx = i
                    break
            except Exception:
                pass

    if target_row_idx is None:
        log(f"  SKIP proof_wall write — date {target_date} not found in col A")
        return False

    # sort_order 0-4 → cols B-F (1-indexed: 2-6)
    sheets_row = target_row_idx + 1
    sheets_col = 2 + min(sort_order, 4)

    try:
        ws.update_cell(sheets_row, sheets_col, new_value)
        log(f"  WROTE proof_wall: date={target_date} sort={sort_order} row={sheets_row} col={sheets_col}")
        return True
    except Exception as exc:
        log(f"  ERROR writing proof_wall: {exc}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def apply_pending_edits() -> int:
    """
    Read all unsynced pending edits and write them to Google Sheets.
    Returns count of successfully applied edits.
    """
    # Collect edits from both sources
    json_edits = read_pending_json()
    db_edits   = read_pending_db()

    # Deduplicate: if an edit appears in both, prefer JSON (it came from the Vercel API)
    json_ids = {e.get('id') for e in json_edits}
    unique_db = [e for e in db_edits if e.get('id') not in json_ids]
    all_edits = json_edits + unique_db

    if not all_edits:
        log("No pending edits to apply.")
        return 0

    log(f"Found {len(all_edits)} unsynced edit(s): {len(json_edits)} from JSON, {len(unique_db)} from DB")

    # Open spreadsheet once
    try:
        ss = get_spreadsheet()
        worksheets = ss.worksheets()
        log(f"Opened spreadsheet: {len(worksheets)} sheets")
    except Exception as exc:
        log(f"ERROR opening spreadsheet: {exc}")
        return 0

    # Cache sheet data (one fetch per sheet, reused across edits for same sheet)
    sheet_cache = {}

    def get_ws_vals(idx: int):
        if idx not in sheet_cache:
            try:
                ws = worksheets[idx]
                sheet_cache[idx] = (ws, ws.get_all_values())
            except Exception as exc:
                log(f"  ERROR fetching sheet [{idx}]: {exc}")
                sheet_cache[idx] = (None, [])
        return sheet_cache[idx]

    applied_json_ids = []
    applied_db_ids   = []
    success_count    = 0

    for edit in all_edits:
        table      = edit.get('table_name') or edit.get('table', '')
        edit_id    = edit.get('id')
        is_from_db = edit in unique_db

        log(f"Processing edit id={edit_id} table={table} key={edit.get('record_key')} field={edit.get('field')}")

        ok = False
        try:
            if table == 'daily_scores':
                ws, vals = get_ws_vals(30)
                if ws:
                    ok = write_daily_score(ws, edit, vals)

            elif table == 'seven_fs':
                ws, vals = get_ws_vals(36)
                if ws:
                    ok = write_seven_f(ws, edit, vals)

            elif table == 'goals':
                ws15, vals15 = get_ws_vals(15)
                ws14, vals14 = get_ws_vals(14)
                if ws15 and ws14:
                    ok = write_goal(ws15, ws14, edit, vals15, vals14)

            elif table == 'proof_wall':
                ws, vals = get_ws_vals(28)
                if ws:
                    ok = write_proof_task(ws, edit, vals)

            else:
                log(f"  SKIP unknown table: {table}")
                ok = False

        except Exception as exc:
            log(f"  EXCEPTION writing edit id={edit_id}: {exc}")
            ok = False

        if ok:
            success_count += 1
            if is_from_db:
                applied_db_ids.append(edit_id)
            else:
                applied_json_ids.append(edit_id)

        # Brief pause between writes to avoid rate-limiting Google API
        time.sleep(0.3)

    # Mark synced in both stores
    if applied_json_ids:
        mark_json_edits_synced(applied_json_ids)
    if applied_db_ids:
        mark_db_edits_synced(applied_db_ids)

    log(f"Completed: {success_count}/{len(all_edits)} edits written to Sheets.")
    return success_count


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log("=== 777_sheets_writer started ===")
    count = apply_pending_edits()
    log(f"=== Done: {count} edits applied ===")
    sys.exit(0 if count >= 0 else 1)
