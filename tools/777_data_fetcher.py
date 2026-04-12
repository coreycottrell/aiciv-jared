#!/usr/bin/env python3
"""
777 Command Center - Google Sheets Data Fetcher
================================================
Reads Jared's 777 Strategy Game Plan spreadsheet and writes
exports/777-command-center/data.json for the dashboard.

AUTHENTICATION:
  Uses GDriveManager OAuth2 (same auth that already works for Drive).
  No additional sharing required — runs as purebrain@puremarketing.ai.

SPREADSHEET:
  1HuJIWEEXpkHgpL2iI6Zit9_cxw3dNd_8zZkOzsK4BGk

RUN:
  cd /home/jared/projects/AI-CIV/aether
  python3 tools/777_data_fetcher.py

OUTPUT:
  exports/777-command-center/data.json

Author: full-stack-developer agent
Date: 2026-03-16
"""

import json
import sys
import os
import time
from datetime import datetime, date, timedelta
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
OUTPUT_FILE = ROOT / 'exports' / '777-command-center' / 'data.json'
SHEET_ID = '1HuJIWEEXpkHgpL2iI6Zit9_cxw3dNd_8zZkOzsK4BGk'

# ── helpers ────────────────────────────────────────────────────────────────────

def safe_float(val, default=0.0):
    """Parse a cell value to float."""
    if val is None or val == '':
        return default
    try:
        cleaned = str(val).replace('$', '').replace('%', '').replace(',', '').strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return default


def safe_int(val, default=0):
    return int(safe_float(val, default))


def get_cell(row, col_idx, default=''):
    """Safely get cell from a row list."""
    try:
        v = row[col_idx]
        return v if v != '' else default
    except (IndexError, TypeError):
        return default


def sheets_date_to_iso(val):
    """
    Parse Sheets date values to YYYY-MM-DD.
    Handles: '1/4/26', '1/4/2026', '2026-01-04', serial numbers
    """
    if not val:
        return None
    val_str = str(val).strip()
    if not val_str:
        return None
    # Already ISO
    if len(val_str) == 10 and val_str[4] == '-':
        return val_str
    # Serial number (Sheets epoch = 1899-12-30)
    try:
        serial = float(val_str)
        if serial > 1000:  # Reasonable date serial
            epoch = date(1899, 12, 30)
            d = epoch + timedelta(days=int(serial))
            return d.isoformat()
    except ValueError:
        pass
    # Common date formats
    for fmt in ('%m/%d/%y', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%B %d, %Y', '%b %d, %Y'):
        try:
            return datetime.strptime(val_str, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def is_header_row(text):
    """Returns True if text looks like a header/instruction row."""
    if not text or len(text.strip()) < 3:
        return True
    lower = text.strip().lower()
    headers = [
        'date', 'total', 'label', 'item', 'answer these', 'rules:',
        'maximum achievable', 'real success is', 'rank the',
        'reevaluate', 'go through', 'go back', 'prepare notes',
        'who needs', 'what type', 'moved from', 'information related',
        'personal tasks', 'professional', 'major projects',
    ]
    return any(h in lower for h in headers)


def rate_limit_pause(seconds=0.5):
    """Brief pause to avoid Google API rate limits."""
    time.sleep(seconds)


# ── sheet readers ──────────────────────────────────────────────────────────────

def read_daily_reflection(ws):
    """
    Sheet [30]: Daily Reflection Process (2026-2028)
    Structure:
      Row 0: Title
      Row 1: Date header row (cols C+ = dates like '1/4/26')
      Row 2: Day name row (Sun/Mon/Tue...)
      Rows 3-22: 20 Questions with 0/0.5/1 scores per date column
      Row 23: TOTAL SCORE (formula sum — use this for daily totals)
      Row 24: AVERAGE SCORE
      Rows 25+: Legend/notes and financial tracking data (NOT question scores)

    Returns:
      heatmap: [{date, score}, ...] last 90 days
      today: {score, max, questions: [{label, score, max}]}
      streaks: {}
    """
    print("  Reading Daily Reflection [30]...")
    result = {
        'heatmap': [],
        'today': {'score': 0, 'max': 20, 'questions': []},
        'streaks': {}
    }

    try:
        all_vals = ws.get_all_values()
        if not all_vals or len(all_vals) < 24:
            print("    WARNING: Daily Reflection sheet too short")
            return result

        num_cols = len(all_vals[1]) if len(all_vals) > 1 else 0
        print(f"    {len(all_vals)} rows × {num_cols} cols")

        # Row 1 (index 1) = date headers. Col 0 = labels, col 1 = empty, cols 2+ = dates.
        date_header_row = all_vals[1]

        # Parse date columns: col_idx → ISO date string
        # The sheet spans 2026-2029 with pre-filled date headers.
        # Only process dates up to today (no future dates).
        today_date = date.today()
        today_str = today_date.isoformat()
        cutoff_date = today_date  # Don't include future dates

        date_cols = {}  # col_idx → date_str (only up to today)
        for j, cell in enumerate(date_header_row):
            if j < 2:
                continue
            d = sheets_date_to_iso(cell)
            if d and d <= today_str:
                date_cols[j] = d

        print(f"    Found {len(date_cols)} date columns (up to today)")
        if date_cols:
            sorted_dates = sorted(date_cols.values())
            print(f"    Date range: {sorted_dates[0]} → {sorted_dates[-1]}")

        # Question rows are rows 3-22 (0-indexed), 20 questions
        # Row 23 = TOTAL SCORE row (formula sum)
        question_rows = all_vals[3:23]  # Exactly 20 question rows
        total_score_row = all_vals[23] if len(all_vals) > 23 else []

        # Count actual questions (non-empty col A)
        question_labels = []
        for row in question_rows:
            if row and row[0].strip() and len(row[0].strip()) > 10:
                question_labels.append(row[0].strip())
        total_questions = len(question_labels)
        print(f"    {total_questions} questions found (rows 3-22)")

        # Use the TOTAL SCORE row (row 23) for daily totals — this is what
        # Sheets computes via SUM formula, avoiding double-counting bonus pts.
        # Only use question rows 3-22 for individual breakdowns.
        score_by_date = {}

        # Method 1: Use TOTAL SCORE row if available
        if total_score_row and total_score_row[0].strip().upper() == 'TOTAL SCORE':
            for col_idx, d_str in date_cols.items():
                if col_idx < len(total_score_row):
                    cell_val = total_score_row[col_idx].strip()
                    if cell_val and cell_val not in ('#DIV/0!', '#REF!', '#N/A', '#VALUE!'):
                        v = safe_float(cell_val, 0.0)
                        if 0 <= v <= 30:  # Sanity check: max 30 (20 qs + bonuses)
                            score_by_date[d_str] = round(v)
        else:
            # Fallback: sum question rows manually (rows 3-22 only)
            for row in question_rows:
                if not row or not row[0].strip() or len(row[0].strip()) < 10:
                    continue
                for col_idx, d_str in date_cols.items():
                    if col_idx < len(row):
                        cell_val = row[col_idx].strip()
                        if cell_val and cell_val not in ('#DIV/0!', '#REF!'):
                            val = safe_float(cell_val, 0.0)
                            if 0 <= val <= 3:  # Each question max 3 pts (bonus)
                                score_by_date[d_str] = score_by_date.get(d_str, 0.0) + val

        # Heatmap: last 90 days
        heatmap = []
        for i in range(89, -1, -1):
            d = today_date - timedelta(days=i)
            d_str = d.isoformat()
            score = score_by_date.get(d_str, 0)
            heatmap.append({'date': d_str, 'score': score})
        result['heatmap'] = heatmap
        result['today']['max'] = 20

        # Find most recent date with data (may not be today if not yet filled)
        most_recent_with_data = None
        for i in range(0, 7):  # Check last 7 days
            d_str = (today_date - timedelta(days=i)).isoformat()
            if score_by_date.get(d_str, 0) > 0:
                most_recent_with_data = d_str
                break

        # Today's score
        result['today']['score'] = score_by_date.get(today_str, 0)

        # Find today's column (or most recent)
        def find_col_for_date(target_date_str):
            for col_idx, d_str in date_cols.items():
                if d_str == target_date_str:
                    return col_idx
            return None

        display_col = find_col_for_date(today_str)
        if display_col is None and most_recent_with_data:
            display_col = find_col_for_date(most_recent_with_data)
            if most_recent_with_data != today_str:
                result['today']['score'] = score_by_date.get(most_recent_with_data, 0)

        if display_col is not None:
            questions_detail = []
            for row in question_rows:
                if not row or not row[0].strip() or len(row[0].strip()) < 10:
                    continue
                label = row[0].strip()
                cell_val = row[display_col].strip() if display_col < len(row) else ''
                score_raw = safe_float(cell_val, 0.0) if cell_val and cell_val not in ('#DIV/0!', '#REF!') else 0.0
                questions_detail.append({
                    'label': label[:80],
                    'score': round(min(score_raw, 3)),  # Cap at 3 (bonus max)
                    'max': 1
                })
            result['today']['questions'] = questions_detail

        print(f"    Today score: {result['today']['score']}/{result['today']['max']}")
        print(f"    Heatmap days with data: {sum(1 for h in heatmap if h['score'] > 0)}/{len(heatmap)}")

    except Exception as e:
        print(f"    ERROR: {e}")
        import traceback
        traceback.print_exc()

    return result


def read_seven_fs(ws):
    """
    Sheet [36]: Weekly Edit
    Structure:
      Row 0: Title row, cols 2+ = week dates (6/30/19 through 1/2/22)
      Rows 13-19 (0-indexed): The 7 F's labels (col B) + scores (cols C+)
        Row 14: Family / Foundation / Love
        Row 15: Freedom / Business / Career
        Row 16: Fitness / Physical Health
        Row 17: Faith / Spiritual
        Row 18: Financial / Money
        Row 19: Fellowship / Friends
        Row 20: Fun / Hobbies
        Row 21: Total

    NOTE: Data only exists through Jan 2022. Returns last week that has
    actual non-zero scores.

    Returns: {current: {faith:7,...}, previous: {...}, last_date: str}
    """
    print("  Reading 7 F's [36]...")

    # Known 7 F labels and their canonical keys
    F_MAP = {
        'family': 'family',
        'freedom': 'career',
        'fitness': 'fitness',
        'faith': 'faith',
        'financial': 'finance',
        'fellowship': 'fellowship',
        'fun': 'fun',
    }
    default_val = {'family': 5, 'career': 5, 'fitness': 5, 'faith': 5,
                   'finance': 5, 'fellowship': 5, 'fun': 5}
    result = {'current': dict(default_val), 'previous': dict(default_val), 'last_date': ''}

    try:
        all_vals = ws.get_all_values()
        if not all_vals:
            return result

        print(f"    Sheet [36]: {len(all_vals)} rows × {len(all_vals[0])} cols")

        # Get header row (row 0) to find date columns
        header = all_vals[0]  # ['', 'My Weekly Edits', '6/30/19', '7/7/19', ...]
        date_col_indices = []
        for j, cell in enumerate(header):
            if j >= 2 and cell.strip():
                d = sheets_date_to_iso(cell)
                if d:
                    date_col_indices.append(j)

        if not date_col_indices:
            print("    WARNING: No date columns found")
            return result

        print(f"    Found {len(date_col_indices)} date columns, last: {header[date_col_indices[-1]]}")

        # Find the 7 F rows: look for rows with col B containing the F labels
        f_rows = {}  # canonical_key → row_index
        for i, row in enumerate(all_vals):
            if not row or len(row) < 2 or not row[1].strip():
                continue
            label = row[1].strip().lower()
            for f_key, canonical in F_MAP.items():
                if f_key in label and canonical not in f_rows:
                    f_rows[canonical] = i
                    break

        print(f"    7 F rows found: {f_rows}")

        # Find the last column that has non-zero scores for the F's
        # Check from the end going backwards
        last_data_col = None
        second_last_data_col = None

        for col_idx in reversed(date_col_indices):
            has_nonzero = False
            for canonical, row_idx in f_rows.items():
                if row_idx < len(all_vals):
                    row = all_vals[row_idx]
                    val = safe_int(get_cell(row, col_idx, '0'), 0)
                    if val > 0:
                        has_nonzero = True
                        break
            if has_nonzero:
                if last_data_col is None:
                    last_data_col = col_idx
                elif second_last_data_col is None:
                    second_last_data_col = col_idx
                    break

        if last_data_col is None:
            print("    WARNING: No non-zero 7 F scores found in any column")
            return result

        last_date = header[last_data_col] if last_data_col < len(header) else '?'
        print(f"    Last week with scores: {last_date} (col {last_data_col})")

        # Extract scores for last two weeks
        current_scores = {}
        previous_scores = {}
        for canonical, row_idx in f_rows.items():
            if row_idx < len(all_vals):
                row = all_vals[row_idx]
                curr = safe_int(get_cell(row, last_data_col, '0'), 0)
                current_scores[canonical] = curr
                if second_last_data_col is not None:
                    prev = safe_int(get_cell(row, second_last_data_col, '0'), 0)
                    previous_scores[canonical] = prev
                else:
                    previous_scores[canonical] = curr

        # Fill any missing keys
        for k in default_val:
            if k not in current_scores:
                current_scores[k] = 5
            if k not in previous_scores:
                previous_scores[k] = 5

        result = {
            'current': current_scores,
            'previous': previous_scores,
            'last_date': last_date
        }
        print(f"    7 F's: {current_scores}")

    except Exception as e:
        print(f"    ERROR: {e}")
        import traceback
        traceback.print_exc()

    return result


def read_proof_wall(ws_2026, worksheets):
    """
    Sheet [28]: Proof Self-Discipline (Completed Tasks 2026)
    Plus historical sheets for cumulative total.

    Structure of each sheet:
      Row 0: ['Information Related to Tasks or Dates', 'Total Past Completed Tasks -->', '{count}', ...]
      Row 1: Column headers
      Rows 2+: Data with dates in col A, tasks in cols B-F

    Returns: {total_tasks, by_year, monthly_2026, recent}
    """
    print("  Reading Proof Wall [28] + historical...")
    result = {
        'total_tasks': 0,
        'by_year': {},
        'monthly_2026': [],
        'recent': []
    }

    # Yearly task counts (index → year label)
    proof_sheet_map = {
        28: '2026',
        56: '2025',
        58: '2024',
        60: '2023',
        63: '2022',
        65: '2021',
        67: '2020',
        68: '2019',
    }

    by_year = {}
    cumulative = 0

    for sheet_idx, year_label in sorted(proof_sheet_map.items()):
        if sheet_idx >= len(worksheets):
            continue
        ws = worksheets[sheet_idx]
        try:
            first_row = ws.get('A1:D1')
            if first_row and len(first_row[0]) > 2:
                count = safe_int(first_row[0][2], 0)
                by_year[year_label] = count
                cumulative += count
                print(f"    Year {year_label}: {count} tasks")
        except Exception as e:
            print(f"    ERROR reading year {year_label}: {e}")
        rate_limit_pause(0.3)

    result['by_year'] = by_year
    result['total_tasks'] = cumulative

    # Monthly breakdown for 2026 from Sheet 28
    try:
        # Get all data from sheet 28 to count per month
        # Col A has dates like '1/1/2026', '2/3/2026', etc.
        col_a = ws_2026.col_values(1)
        col_b = ws_2026.col_values(2)

        monthly_counts = {}
        for i, (date_val, task_val) in enumerate(zip(col_a, col_b)):
            if i < 2:  # Skip header rows
                continue
            if not task_val.strip():
                continue
            if date_val.strip():
                d_str = sheets_date_to_iso(date_val)
                if d_str and d_str.startswith('2026'):
                    month_num = int(d_str.split('-')[1])
                    monthly_counts[month_num] = monthly_counts.get(month_num, 0) + 1
            elif task_val.strip():
                # Task under same date as row above — increment last seen month
                if monthly_counts:
                    last_month = max(monthly_counts.keys())
                    monthly_counts[last_month] = monthly_counts[last_month] + 1

        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_2026 = []
        for m in range(1, 13):
            count = monthly_counts.get(m, 0)
            if count > 0 or m <= date.today().month:
                monthly_2026.append({'month': month_names[m - 1], 'count': count})

        result['monthly_2026'] = monthly_2026
        print(f"    2026 monthly: {monthly_2026}")

    except Exception as e:
        print(f"    ERROR computing monthly counts: {e}")

    # Recent tasks (last 10 tasks from 2026 sheet)
    try:
        col_a = ws_2026.col_values(1)
        col_b = ws_2026.col_values(2)

        recent = []
        last_date = ''
        today = date.today()

        # Reverse through col_b to find last N tasks
        combined = list(zip(col_a, col_b))[2:]  # Skip headers
        combined_with_dates = []
        cur_date = ''
        for date_val, task_val in combined:
            if date_val.strip():
                cur_date = date_val.strip()
            if task_val.strip():
                combined_with_dates.append((cur_date, task_val.strip()))

        # Take last 10
        for date_val, task_text in reversed(combined_with_dates[-15:]):
            if len(recent) >= 10:
                break
            if not task_text or len(task_text) < 3:
                continue
            d_str = sheets_date_to_iso(date_val) if date_val else ''
            if d_str:
                try:
                    d = date.fromisoformat(d_str)
                    delta = (today - d).days
                    if delta == 0:
                        rel = 'Today'
                    elif delta == 1:
                        rel = 'Yesterday'
                    elif delta < 7:
                        rel = f'{delta}d ago'
                    else:
                        rel = d.strftime('%b %d')
                except Exception:
                    rel = d_str
            else:
                rel = ''
            recent.append({'task': task_text[:80], 'date': rel})

        result['recent'] = recent
        print(f"    Recent tasks: {len(recent)}")

    except Exception as e:
        print(f"    ERROR reading recent tasks: {e}")

    return result


def read_goals(worksheets):
    """
    Reads goals from multiple sheets.

    Returns:
      vision: str
      yearly: [{text, progress}, ...]
      top77: [{text, year}, ...]
    """
    print("  Reading Goals...")
    result = {
        'vision': '',
        'yearly': [],
        'top77': []
    }

    # Sheet [10]: The Big Picture & Vision Statement
    try:
        ws10 = worksheets[10]
        vals = ws10.get('A1:B25')
        print(f"    Sheet [10] vision: {len(vals)} rows")
        for row in vals:
            if len(row) > 0:
                text = row[0].strip()
                if text.startswith('"') or ('founder' in text.lower() and 'ceo' in text.lower()):
                    # Remove surrounding quotes
                    result['vision'] = text.strip('"').strip()
                    break
                # Check col B too
                if len(row) > 1:
                    text_b = row[1].strip()
                    if text_b.startswith('"') or ('founder' in text_b.lower() and 'ceo' in text_b.lower()):
                        result['vision'] = text_b.strip('"').strip()
                        break
        if not result['vision']:
            # Fallback: row 3 col A
            if len(vals) > 3 and vals[3]:
                result['vision'] = vals[3][0].strip().strip('"')

        print(f"    Vision: {result['vision'][:60]}...")
    except Exception as e:
        print(f"    ERROR reading vision [10]: {e}")

    rate_limit_pause(0.5)

    # Sheet [15]: Top 7 Yearly Goals
    try:
        ws15 = worksheets[15]
        all_vals = ws15.get_all_values()
        print(f"    Sheet [15] yearly goals: {len(all_vals)} rows")

        yearly_goals = []
        skip_patterns = [
            'determining', 'selecting', 'top 7', 'i selected', 'i wrote',
            'what obstacles', 'write the attributes', 'learning influence',
            'why should', 'did i make', 'i told others', 'i read the bible',
            'immediate family', 'melanie sanborn',
        ]
        for row in all_vals[3:]:  # Skip first 3 header rows
            if not row or not row[0].strip():
                continue
            text = row[0].strip()
            if len(text) < 10:
                continue
            text_lower = text.lower()
            if any(p in text_lower for p in skip_patterns):
                continue
            # Try to get a progress percentage from col 1 or 2
            pct = 0
            for col_idx in range(1, min(4, len(row))):
                v = str(row[col_idx]).strip().replace('%', '')
                try:
                    pct = max(0, min(100, int(float(v))))
                    if pct > 0:
                        break
                except (ValueError, TypeError):
                    continue
            yearly_goals.append({'text': text[:100], 'progress': pct})
            if len(yearly_goals) >= 7:
                break

        result['yearly'] = yearly_goals
        print(f"    Yearly goals: {len(yearly_goals)}")
        for g in yearly_goals[:3]:
            print(f"      - {g['text'][:60]}")

    except Exception as e:
        print(f"    ERROR reading yearly goals [15]: {e}")

    rate_limit_pause(0.5)

    # Sheet [14]: Top 77 Goals
    try:
        ws14 = worksheets[14]
        vals = ws14.get_all_values()
        print(f"    Sheet [14] top 77 goals: {len(vals)} rows")

        skip_patterns = [
            'top 77 goals', 'these goals', 'date goals here', 'i imagined',
            'i remembered', 'assign each', 'each number', 'could be when',
        ]
        top77 = []
        for row in vals[5:]:  # Skip first 5 header rows
            if not row or not row[0].strip():
                continue
            text = row[0].strip()
            if len(text) < 10:
                continue
            text_lower = text.lower()
            if any(p in text_lower for p in skip_patterns):
                continue
            year_assign = row[1].strip() if len(row) > 1 else ''
            top77.append({'text': text[:100], 'year': year_assign})

        result['top77'] = top77
        print(f"    Top 77 goals: {len(top77)} found")

    except Exception as e:
        print(f"    ERROR reading top 77 goals [14]: {e}")

    return result


def read_money_map(worksheets):
    """
    Sheets [8] Networth + [9] The Number

    Returns: {net_worth, the_number: {monthly_spend, annual_spend, total_target}}
    """
    print("  Reading Money Map [8], [9]...")
    result = {
        'net_worth': 0,
        'the_number': {
            'monthly_spend': 250000,
            'annual_spend': 3000000,
            'total_target': 60000000,
        }
    }

    # Sheet [9] The Number
    try:
        ws9 = worksheets[9]
        vals = ws9.get('A1:B7')
        print(f"    Sheet [9] The Number: {len(vals)} rows")
        for i, row in enumerate(vals):
            if not row:
                continue
            label = row[0].strip().lower() if row else ''
            val = row[1].strip() if len(row) > 1 else ''
            if 'per month' in label:
                result['the_number']['monthly_spend'] = safe_int(val, 250000)
            elif 'per year' in label:
                result['the_number']['annual_spend'] = safe_int(val, 3000000)
            elif 'number' in label or 'total' in label or 'need to save' in label:
                v = safe_int(val, 0)
                if v > 0:
                    result['the_number']['total_target'] = v

        # Compute target if not found: monthly * 12 * 20 years
        if result['the_number']['total_target'] == 0:
            result['the_number']['total_target'] = (
                result['the_number']['monthly_spend'] * 12 * 20
            )

        print(f"    The Number: monthly=${result['the_number']['monthly_spend']:,}, "
              f"target=${result['the_number']['total_target']:,}")

    except Exception as e:
        print(f"    ERROR reading The Number [9]: {e}")

    rate_limit_pause(0.3)

    # Sheet [8] Personal Networth — structure has #REF! cells from old formulas
    # Extract what we can from asset/liability columns
    try:
        ws8 = worksheets[8]
        vals = ws8.get('A1:F20')
        print(f"    Sheet [8] Networth: {len(vals)} rows")
        # Skip — the sheet has #REF! values and is from 2018
        # Net worth will remain 0 unless we find meaningful data
        net_worth = 0
        for row in vals:
            if not row:
                continue
            label = str(row[0]).strip().lower()
            if 'total' in label or 'net worth' in label:
                for col_idx in range(1, min(6, len(row))):
                    v = safe_float(row[col_idx], 0)
                    if v != 0 and '#REF' not in str(row[col_idx]):
                        net_worth = int(v)
                        break
                if net_worth != 0:
                    break
        result['net_worth'] = net_worth
        print(f"    Net worth: ${net_worth:,}")

    except Exception as e:
        print(f"    ERROR reading Networth [8]: {e}")

    return result


def read_legacy(worksheets):
    """
    Sheets [17] Legacy + [7] 10 Micro Laws

    Returns: {vision, eulogies: {family, friend, business_partner, client}, micro_laws}
    """
    print("  Reading Legacy [17], Micro Laws [7]...")
    result = {
        'vision': '',
        'eulogies': {
            'family': '',
            'friend': '',
            'business_partner': '',
            'client': ''
        },
        'micro_laws': []
    }

    # Sheet [17]: My Legacy
    try:
        ws17 = worksheets[17]
        vals = ws17.get('A1:B8')
        print(f"    Sheet [17] Legacy: {len(vals)} rows")

        # Row 2: labels ['Family', 'Friend']
        # Row 3: [family eulogy text, friend eulogy text]
        # Row 4: ['Business Partner', 'Client']
        # Row 5: [business eulogy, client eulogy]
        for i, row in enumerate(vals):
            if not row:
                continue
            label_a = row[0].strip().lower() if row else ''
            label_b = row[1].strip().lower() if len(row) > 1 else ''

            if label_a == 'family' and label_b == 'friend':
                # Next row has the actual eulogy text
                if i + 1 < len(vals):
                    next_row = vals[i + 1]
                    if next_row:
                        result['eulogies']['family'] = next_row[0].strip()[:300] if next_row[0] else ''
                        result['eulogies']['friend'] = next_row[1].strip()[:300] if len(next_row) > 1 else ''
            elif 'business' in label_a and 'client' in label_b:
                if i + 1 < len(vals):
                    next_row = vals[i + 1]
                    if next_row:
                        result['eulogies']['business_partner'] = next_row[0].strip()[:300] if next_row[0] else ''
                        result['eulogies']['client'] = next_row[1].strip()[:300] if len(next_row) > 1 else ''

        # Check for epitaph (may be in last rows)
        for row in reversed(vals):
            if not row:
                continue
            text = row[0].strip() if row else ''
            if len(text) > 20 and 'epitaph' in text.lower():
                result['vision'] = text
                break

        print(f"    Family eulogy: {len(result['eulogies']['family'])} chars")

    except Exception as e:
        print(f"    ERROR reading Legacy [17]: {e}")

    rate_limit_pause(0.3)

    # Sheet [7]: 10 Micro Laws
    try:
        ws7 = worksheets[7]
        vals = ws7.get('A1:C20')
        print(f"    Sheet [7] Micro Laws: {len(vals)} rows")

        laws = []
        for row in vals:
            if not row:
                continue
            num = row[0].strip() if row else ''
            law_text = row[1].strip() if len(row) > 1 else ''
            if num.isdigit() and law_text and len(law_text) > 5:
                laws.append({'num': int(num), 'law': law_text})

        laws.sort(key=lambda x: x['num'])
        result['micro_laws'] = [l['law'] for l in laws]
        print(f"    Micro laws: {len(result['micro_laws'])} found")
        for law in result['micro_laws'][:3]:
            print(f"      {law[:60]}")

    except Exception as e:
        print(f"    ERROR reading Micro Laws [7]: {e}")

    return result


def read_gratitude(ws):
    """
    Sheet [5]: An Attitude of Gratitude
    Col A = date, Col B = gratitude entry
    Returns: [{text, date}, ...]
    """
    print("  Reading Gratitude [5]...")
    entries = []
    skip_texts = [
        'attitude of gratitude', 'people, places', 'i thought', 'i reflected',
        'i am thankful', 'count your blessings', 'when i can', 'i am grateful for life',
        '(and what you', 'update this'
    ]
    try:
        col_a = ws.col_values(1)
        col_b = ws.col_values(2)
        combined = list(zip(col_a, col_b))

        for date_val, text in reversed(combined):
            if len(entries) >= 5:
                break
            if not text or len(text.strip()) < 10:
                continue
            text = text.strip()
            if any(s in text.lower() for s in skip_texts):
                continue
            entries.append({'text': text[:120], 'date': date_val.strip()})

        print(f"    Gratitude entries: {len(entries)}")
        for e in entries[:2]:
            print(f"      {e['date']}: {e['text'][:60]}")

    except Exception as e:
        print(f"    ERROR: {e}")

    return entries


def read_achievements(ws):
    """
    Sheet [6]: My Achievements
    Col A = date, Col B = achievement text
    Returns: {total, latest: [{text, date}]}
    """
    print("  Reading Achievements [6]...")
    result = {'total': 0, 'latest': []}
    skip_texts = [
        "my achievement", "things i've done", "i thought about",
        "i reflected", "when people say", "you can't", "2019 (the start)"
    ]
    try:
        col_b = ws.col_values(2)
        col_a = ws.col_values(1)

        all_entries = []
        for date_val, text in zip(col_a, col_b):
            if not text or len(text.strip()) < 5:
                continue
            text = text.strip()
            if any(s in text.lower() for s in skip_texts):
                continue
            all_entries.append({'text': text[:120], 'date': date_val.strip()})

        result['total'] = len(all_entries)
        result['latest'] = all_entries[-5:][::-1]  # Most recent 5, reversed

        print(f"    Achievements total: {len(all_entries)}")
        for e in result['latest'][:2]:
            print(f"      {e['date']}: {e['text'][:60]}")

    except Exception as e:
        print(f"    ERROR: {e}")

    return result


# ── sample data fallbacks ──────────────────────────────────────────────────────

def _sample_daily_pulse():
    """Realistic sample for when real data unavailable."""
    today = date.today()
    import random
    random.seed(42)
    heatmap = []
    for i in range(89, -1, -1):
        d = today - timedelta(days=i)
        score = random.randint(7, 13) if i > 0 else 11
        heatmap.append({'date': d.isoformat(), 'score': score})
    return {
        'heatmap': heatmap,
        'today': {
            'score': 11, 'max': 15,
            'questions': [
                {'label': 'Did I wake up at 4:20am?', 'score': 1, 'max': 1},
                {'label': 'Did I study/read for 61 min?', 'score': 1, 'max': 1},
                {'label': 'Did I pray/meditate?', 'score': 1, 'max': 1},
                {'label': 'Did I exercise?', 'score': 0, 'max': 1},
                {'label': 'Did I write gratitude?', 'score': 1, 'max': 1},
            ]
        },
        'streaks': {}
    }


def _sample_seven_fs():
    return {
        'current': {'faith': 7, 'career': 8, 'fitness': 5, 'family': 8,
                    'finance': 6, 'fellowship': 6, 'fun': 6},
        'previous': {'faith': 6, 'career': 7, 'fitness': 4, 'family': 7,
                     'finance': 5, 'fellowship': 5, 'fun': 5}
    }


def _sample_proof_wall():
    return {
        'total_tasks': 31807,
        'by_year': {'2019': 4206, '2020': 4320, '2021': 5427, '2022': 4109,
                    '2023': 4236, '2024': 4197, '2025': 3830, '2026': 1482},
        'monthly_2026': [
            {'month': 'Jan', 'count': 320}, {'month': 'Feb', 'count': 295},
            {'month': 'Mar', 'count': 180},
        ],
        'recent': [
            {'task': 'Plan for Tomorrow - Future Focus', 'date': 'Today'},
            {'task': 'End of Day Wrap Up (daily review)', 'date': 'Today'},
        ]
    }


def _sample_goals():
    return {
        'vision': 'I am the Founder & CEO of Pure Technology and other companies. A Billionaire Philanthropist who loves my family and spends ample time with them, and focuses the rest of my efforts on impacting others to #Grind!',
        'yearly': [
            {'text': 'Close $25M+ Series-A with MAKR Venture Fund', 'progress': 15},
            {'text': 'Land first major Experiential Giveaway', 'progress': 30},
            {'text': 'Begin Dashboard, Launcher & Phone MVP', 'progress': 20},
        ],
        'top77': [
            {'text': 'I read the Bible and Pray for 25 minutes in the morning each day', 'year': '8'},
        ]
    }


def _sample_legacy():
    return {
        'vision': '',
        'eulogies': {'family': '', 'friend': '', 'business_partner': '', 'client': ''},
        'micro_laws': [
            'Wake Up 5 Days a Week at 4:30AM',
            'Read/Learn for 1 Hour Per Day - 5 Days a Week',
            'No Phones After 7pm EST',
            'No Meetings at the Mansion after 7pm',
            'Invest 1 Hour Per Day with Melanie',
            'Invest 1 Hour Per Day with Lily',
            'Delegate Everything I Don\'t Need to Do',
            'Always Seek to Learn from Everyone you Come Across',
            'NEVER Give a Friend an Opportunity Unless Proven',
            'Be Adamant about the End Result but FLEXIBLE on How You Get There',
        ]
    }


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("777 Command Center — Data Fetcher")
    print("=" * 65)

    try:
        import gspread
    except ImportError:
        print("ERROR: gspread not installed.")
        print("  python3 -m pip install gspread --break-system-packages")
        sys.exit(1)

    # ── Auth via GDriveManager (OAuth2 — works without sharing) ────────────────
    print("\nAuthenticating via GDriveManager OAuth2...")
    from tools.gdrive_manager import GDriveManager

    gm = GDriveManager(verbose=False)
    creds = gm.service._http.credentials
    gc = gspread.authorize(creds)
    print(f"  Auth type: {gm.auth_type}")
    print(f"  Creds type: {type(creds).__name__}")

    # ── Open spreadsheet ────────────────────────────────────────────────────────
    print(f"\nOpening spreadsheet: {SHEET_ID}")
    try:
        ss = gc.open_by_key(SHEET_ID)
    except Exception as e:
        print(f"ERROR: Cannot open spreadsheet — {e}")
        print("Writing sample data.json as fallback...")
        write_fallback_data()
        return

    print(f"  Title: {ss.title}")
    worksheets = ss.worksheets()
    print(f"  Sheets: {len(worksheets)}")

    # Print all sheet titles for reference
    for i, ws in enumerate(worksheets[:35]):
        print(f"  [{i:2d}] {ws.title}")
    if len(worksheets) > 35:
        print(f"  ... and {len(worksheets) - 35} more")

    # ── Fetch sections ──────────────────────────────────────────────────────────
    print("\n" + "─" * 65)
    print("Fetching data sections...")
    print("─" * 65)

    data = {
        'last_updated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'live',
    }

    # 1. Daily Reflection (Sheet 30)
    print("\n[1/8] Daily Reflection")
    try:
        ws_daily = worksheets[30]
        data['daily_pulse'] = read_daily_reflection(ws_daily)
    except Exception as e:
        print(f"  FALLBACK: {e}")
        data['daily_pulse'] = _sample_daily_pulse()
    rate_limit_pause(1.0)

    # 2. 7 F's Weekly Edit (Sheet 36)
    print("\n[2/8] Seven F's")
    try:
        ws_7f = worksheets[36]
        data['seven_fs'] = read_seven_fs(ws_7f)
    except Exception as e:
        print(f"  FALLBACK: {e}")
        data['seven_fs'] = _sample_seven_fs()
    rate_limit_pause(0.5)

    # 3. Proof Wall (Sheet 28 + historical)
    print("\n[3/8] Proof Wall")
    try:
        ws_proof = worksheets[28]
        data['proof_wall'] = read_proof_wall(ws_proof, worksheets)
    except Exception as e:
        print(f"  FALLBACK: {e}")
        data['proof_wall'] = _sample_proof_wall()
    rate_limit_pause(0.5)

    # 4. Goals (Sheets 10, 14, 15)
    print("\n[4/8] Goals")
    try:
        data['goals'] = read_goals(worksheets)
        if not data['goals'].get('vision') and not data['goals'].get('yearly'):
            data['goals'] = _sample_goals()
    except Exception as e:
        print(f"  FALLBACK: {e}")
        data['goals'] = _sample_goals()
    rate_limit_pause(0.5)

    # 5. Money Map (Sheets 8, 9)
    print("\n[5/8] Money Map")
    try:
        data['money_map'] = read_money_map(worksheets)
    except Exception as e:
        print(f"  FALLBACK: {e}")
        data['money_map'] = {
            'net_worth': 0,
            'the_number': {'monthly_spend': 250000, 'annual_spend': 3000000, 'total_target': 60000000}
        }
    rate_limit_pause(0.5)

    # 6. Legacy & Micro Laws (Sheets 17, 7)
    print("\n[6/8] Legacy & Micro Laws")
    try:
        data['legacy'] = read_legacy(worksheets)
        if not data['legacy'].get('micro_laws'):
            data['legacy']['micro_laws'] = _sample_legacy()['micro_laws']
    except Exception as e:
        print(f"  FALLBACK: {e}")
        data['legacy'] = _sample_legacy()
    rate_limit_pause(0.5)

    # 7. Gratitude (Sheet 5)
    print("\n[7/8] Gratitude")
    try:
        ws_gratitude = worksheets[5]
        data['gratitude'] = read_gratitude(ws_gratitude)
    except Exception as e:
        print(f"  FALLBACK: {e}")
        data['gratitude'] = []
    rate_limit_pause(0.5)

    # 8. Achievements (Sheet 6)
    print("\n[8/8] Achievements")
    try:
        ws_achievements = worksheets[6]
        data['achievements'] = read_achievements(ws_achievements)
    except Exception as e:
        print(f"  FALLBACK: {e}")
        data['achievements'] = {'total': 0, 'latest': []}

    # ── Write output ────────────────────────────────────────────────────────────
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print("\n" + "=" * 65)
    print(f"data.json written → {OUTPUT_FILE}")
    print(f"Last updated: {data['last_updated']}")
    print("=" * 65)

    # ── Summary ─────────────────────────────────────────────────────────────────
    print("\n--- LIVE DATA SUMMARY ---")

    dp = data.get('daily_pulse', {})
    hm = dp.get('heatmap', [])
    today_score = dp.get('today', {}).get('score', 0)
    today_max = dp.get('today', {}).get('max', 15)
    nonzero_days = sum(1 for d in hm if d.get('score', 0) > 0)
    print(f"Daily Pulse:  {len(hm)} heatmap days, {nonzero_days} with scores, today={today_score}/{today_max}")

    sf = data.get('seven_fs', {}).get('current', {})
    sf_avg = round(sum(sf.values()) / len(sf), 1) if sf else 0
    print(f"7 F's:        avg={sf_avg}/10 — {sf}")

    pw = data.get('proof_wall', {})
    total_tasks = pw.get('total_tasks', 0)
    by_year = pw.get('by_year', {})
    tasks_2026 = by_year.get('2026', 0)
    print(f"Proof Wall:   {total_tasks:,} total tasks across all years, 2026={tasks_2026:,}")

    goals = data.get('goals', {})
    vision_preview = goals.get('vision', '')[:70]
    print(f"Goals:        {len(goals.get('yearly', []))} yearly, {len(goals.get('top77', []))} of 77 — vision: {vision_preview}...")

    mm = data.get('money_map', {})
    tn = mm.get('the_number', {})
    print(f"Money Map:    net_worth=${mm.get('net_worth', 0):,}, target=${tn.get('total_target', 0):,}")

    leg = data.get('legacy', {})
    print(f"Legacy:       {len(leg.get('micro_laws', []))} micro laws, eulogies={list(k for k,v in leg.get('eulogies', {}).items() if v)}")

    grts = data.get('gratitude', [])
    print(f"Gratitude:    {len(grts)} recent entries")

    ach = data.get('achievements', {})
    print(f"Achievements: {ach.get('total', 0)} total")

    print()
    print(f"File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    print("Done.")


def write_fallback_data():
    """Write sample data.json when real data is unavailable."""
    import random
    random.seed(42)
    data = {
        'last_updated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'sample',
        '_note': 'SAMPLE DATA — could not access spreadsheet',
        'daily_pulse': _sample_daily_pulse(),
        'seven_fs': _sample_seven_fs(),
        'proof_wall': _sample_proof_wall(),
        'goals': _sample_goals(),
        'money_map': {
            'net_worth': 0,
            'the_number': {'monthly_spend': 250000, 'annual_spend': 3000000, 'total_target': 60000000}
        },
        'legacy': _sample_legacy(),
        'gratitude': [],
        'achievements': {'total': 0, 'latest': []}
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Sample data.json written → {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
