#!/usr/bin/env python3
"""
777 Command Center — D1-Compatible SQLite Cache
================================================
SQLite cache with a schema compatible with Cloudflare D1 for future migration.

DATABASE:
  data/777-cache.db

TABLES:
  sync_state     — last sync time, etag, misc KV
  daily_scores   — per-day reflection scores
  seven_fs       — weekly 7 F's scores
  goals          — vision + yearly goals + top 77
  proof_wall     — daily proof/win entries
  pending_edits  — queued UI edits awaiting Sheets write

USAGE:
  from tools.777_d1_cache import init_db, cache_data, get_cached_data
  init_db()
  cache_data(data_dict)   # from data.json
  data = get_cached_data()

Author: PTT full-stack-developer
"""

import json
import sqlite3
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / 'data' / '777-cache.db'

# ── Helpers ───────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    """Current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _get_conn() -> sqlite3.Connection:
    """Open a connection to the cache DB. Creates data/ dir if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrent read performance
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ── init_db ───────────────────────────────────────────────────────────────────

def init_db() -> None:
    """
    Create all tables if they do not already exist.
    D1-compatible schema (TEXT primary keys, no AUTOINCREMENT on TEXT PKs).
    """
    with _get_conn() as conn:
        conn.executescript("""
        -- Key-value store for sync metadata (last_sync, etag, etc.)
        CREATE TABLE IF NOT EXISTS sync_state (
            key        TEXT PRIMARY KEY,
            value      TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        -- Daily reflection scores (one row per date)
        CREATE TABLE IF NOT EXISTS daily_scores (
            date           TEXT PRIMARY KEY,  -- YYYY-MM-DD
            score          INTEGER NOT NULL DEFAULT 0,
            max_score      INTEGER NOT NULL DEFAULT 20,
            questions_json TEXT NOT NULL DEFAULT '[]'  -- JSON array of {label,score,max}
        );

        -- Weekly 7 F's scores (one row per week start date)
        CREATE TABLE IF NOT EXISTS seven_fs (
            week_date   TEXT PRIMARY KEY,  -- YYYY-MM-DD of the week
            family      INTEGER NOT NULL DEFAULT 0,
            career      INTEGER NOT NULL DEFAULT 0,
            fitness     INTEGER NOT NULL DEFAULT 0,
            faith       INTEGER NOT NULL DEFAULT 0,
            finance     INTEGER NOT NULL DEFAULT 0,
            fellowship  INTEGER NOT NULL DEFAULT 0,
            fun         INTEGER NOT NULL DEFAULT 0
        );

        -- Goals: vision statement + yearly goals + top 77 lifetime goals
        CREATE TABLE IF NOT EXISTS goals (
            id          INTEGER PRIMARY KEY,
            type        TEXT NOT NULL,    -- 'vision' | 'yearly' | 'top77' | 'category'
            text        TEXT NOT NULL DEFAULT '',
            progress    INTEGER NOT NULL DEFAULT 0,   -- 0-100 percentage
            year        TEXT NOT NULL DEFAULT '',
            sort_order  INTEGER NOT NULL DEFAULT 0
        );

        -- Daily proof wall entries
        CREATE TABLE IF NOT EXISTS proof_wall (
            date       TEXT NOT NULL,   -- YYYY-MM-DD
            task       TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (date, sort_order)
        );

        -- Pending bidirectional edits: queued UI changes awaiting Sheets write
        CREATE TABLE IF NOT EXISTS pending_edits (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name  TEXT NOT NULL,
            record_key  TEXT NOT NULL,  -- e.g. date string or goal id
            field       TEXT NOT NULL,
            new_value   TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            synced_at   TEXT            -- NULL until written to Sheets
        );
        """)
    print(f"[777_d1_cache] DB initialized at {DB_PATH}")


# ── cache_data ────────────────────────────────────────────────────────────────

def cache_data(data_dict: Dict[str, Any]) -> None:
    """
    Write a parsed data.json dict into the SQLite tables.
    Replaces existing rows for updated records (upsert).

    Expected data_dict structure mirrors data.json output from 777_data_fetcher.py:
      {
        "daily_reflection": {
          "heatmap": [{date, score}, ...],
          "today": {score, max, questions: [{label, score, max}]}
        },
        "seven_fs": {
          "current": {family, career, fitness, faith, finance, fellowship, fun},
          "last_date": "YYYY-MM-DD"
        },
        "goals": {
          "vision": "...",
          "yearly": [{text, progress, year, sort_order}, ...],
          "top77": [{text, sort_order, category}, ...]
        },
        "proof_wall": [{date, task, sort_order}, ...]
      }
    """
    now = _now_iso()
    with _get_conn() as conn:
        # -- sync_state: record this cache write time
        conn.execute(
            "INSERT OR REPLACE INTO sync_state (key, value, updated_at) VALUES (?, ?, ?)",
            ("last_cache_write", now, now)
        )

        # -- daily_scores: heatmap + today questions
        # Support both "daily_pulse" (live data.json) and "daily_reflection" (legacy)
        dr = data_dict.get("daily_pulse", data_dict.get("daily_reflection", {}))
        heatmap = dr.get("heatmap", [])
        today_obj = dr.get("today", {})
        today_questions = today_obj.get("questions", [])

        # Build a quick map of date → score from heatmap
        heatmap_map = {h["date"]: h["score"] for h in heatmap if "date" in h}

        # Upsert heatmap rows (questions_json only available for today)
        for entry in heatmap:
            d = entry.get("date")
            s = entry.get("score", 0)
            if not d:
                continue
            # We don't have per-question detail for historical dates — keep existing
            conn.execute("""
                INSERT INTO daily_scores (date, score, max_score, questions_json)
                VALUES (?, ?, 20, '[]')
                ON CONFLICT(date) DO UPDATE SET score=excluded.score
            """, (d, s))

        # Upsert today with full question detail if available
        if today_obj:
            from datetime import date as _date
            today_str = _date.today().isoformat()
            conn.execute("""
                INSERT INTO daily_scores (date, score, max_score, questions_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    score=excluded.score,
                    max_score=excluded.max_score,
                    questions_json=excluded.questions_json
            """, (
                today_str,
                today_obj.get("score", 0),
                today_obj.get("max", 20),
                json.dumps(today_questions)
            ))

        # -- seven_fs
        sfs = data_dict.get("seven_fs", {})
        current_fs = sfs.get("current", {})
        last_date = sfs.get("last_date", "")
        if current_fs and last_date:
            conn.execute("""
                INSERT OR REPLACE INTO seven_fs
                    (week_date, family, career, fitness, faith, finance, fellowship, fun)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                last_date,
                current_fs.get("family", 0),
                current_fs.get("career", 0),
                current_fs.get("fitness", 0),
                current_fs.get("faith", 0),
                current_fs.get("finance", 0),
                current_fs.get("fellowship", 0),
                current_fs.get("fun", 0),
            ))

        # -- goals: clear and re-insert (goals list can change order)
        goals_obj = data_dict.get("goals", {})
        if goals_obj:
            conn.execute("DELETE FROM goals")
            vision = goals_obj.get("vision", "")
            if vision:
                conn.execute(
                    "INSERT INTO goals (type, text, progress, year, sort_order) VALUES (?,?,0,'',0)",
                    ("vision", vision)
                )
            for i, g in enumerate(goals_obj.get("yearly", []), start=1):
                conn.execute(
                    "INSERT INTO goals (type, text, progress, year, sort_order) VALUES (?,?,?,?,?)",
                    ("yearly", g.get("text", ""), g.get("progress", 0), g.get("year", ""), i)
                )
            for i, g in enumerate(goals_obj.get("top77", []), start=1):
                conn.execute(
                    "INSERT INTO goals (type, text, progress, year, sort_order) VALUES (?,?,?,?,?)",
                    ("top77", g.get("text", ""), g.get("progress", 0), g.get("category", ""), i)
                )

        # -- proof_wall: clear and re-insert
        proof_obj = data_dict.get("proof_wall", {})
        proof_recent = proof_obj.get("recent", []) if isinstance(proof_obj, dict) else []
        if proof_recent:
            conn.execute("DELETE FROM proof_wall")
            for i, entry in enumerate(proof_recent):
                if isinstance(entry, dict):
                    conn.execute(
                        "INSERT INTO proof_wall (date, task, sort_order) VALUES (?,?,?)",
                        (entry.get("date", ""), entry.get("task", ""), i)
                    )

    print(f"[777_d1_cache] cache_data: {len(heatmap)} heatmap rows, goals={'yes' if goals_obj else 'no'}, proof={len(proof_recent)}")


# ── get_cached_data ───────────────────────────────────────────────────────────

def get_cached_data() -> Dict[str, Any]:
    """
    Read the SQLite cache and return a dict in the same shape as data.json.
    Returns an empty structure if DB doesn't exist yet.
    """
    if not DB_PATH.exists():
        return {}

    from datetime import date as _date, timedelta
    today_str = _date.today().isoformat()

    with _get_conn() as conn:
        # -- daily_reflection
        # Heatmap: last 90 days
        heatmap = []
        for i in range(89, -1, -1):
            d = (_date.today() - timedelta(days=i)).isoformat()
            row = conn.execute(
                "SELECT score FROM daily_scores WHERE date=?", (d,)
            ).fetchone()
            heatmap.append({"date": d, "score": row["score"] if row else 0})

        # Today detail
        today_row = conn.execute(
            "SELECT score, max_score, questions_json FROM daily_scores WHERE date=?",
            (today_str,)
        ).fetchone()
        today_obj = {
            "score": today_row["score"] if today_row else 0,
            "max": today_row["max_score"] if today_row else 20,
            "questions": json.loads(today_row["questions_json"]) if today_row else []
        }

        # -- seven_fs: most recent week
        fs_row = conn.execute(
            "SELECT * FROM seven_fs ORDER BY week_date DESC LIMIT 1"
        ).fetchone()
        if fs_row:
            current_fs = {
                "family": fs_row["family"],
                "career": fs_row["career"],
                "fitness": fs_row["fitness"],
                "faith": fs_row["faith"],
                "finance": fs_row["finance"],
                "fellowship": fs_row["fellowship"],
                "fun": fs_row["fun"],
            }
            last_date = fs_row["week_date"]
        else:
            current_fs = {k: 5 for k in ["family", "career", "fitness", "faith", "finance", "fellowship", "fun"]}
            last_date = ""

        # Previous week
        prev_row = conn.execute(
            "SELECT * FROM seven_fs ORDER BY week_date DESC LIMIT 1 OFFSET 1"
        ).fetchone()
        previous_fs = {
            "family": prev_row["family"] if prev_row else 5,
            "career": prev_row["career"] if prev_row else 5,
            "fitness": prev_row["fitness"] if prev_row else 5,
            "faith": prev_row["faith"] if prev_row else 5,
            "finance": prev_row["finance"] if prev_row else 5,
            "fellowship": prev_row["fellowship"] if prev_row else 5,
            "fun": prev_row["fun"] if prev_row else 5,
        }

        # -- goals
        vision_row = conn.execute(
            "SELECT text FROM goals WHERE type='vision' LIMIT 1"
        ).fetchone()
        yearly_rows = conn.execute(
            "SELECT text, progress, year, sort_order FROM goals WHERE type='yearly' ORDER BY sort_order"
        ).fetchall()
        top77_rows = conn.execute(
            "SELECT text, progress, year AS category, sort_order FROM goals WHERE type='top77' ORDER BY sort_order"
        ).fetchall()

        goals_obj = {
            "vision": vision_row["text"] if vision_row else "",
            "yearly": [
                {"text": r["text"], "progress": r["progress"], "year": r["year"], "sort_order": r["sort_order"]}
                for r in yearly_rows
            ],
            "top77": [
                {"text": r["text"], "progress": r["progress"], "category": r["category"], "sort_order": r["sort_order"]}
                for r in top77_rows
            ]
        }

        # -- proof_wall
        proof_rows = conn.execute(
            "SELECT date, task, sort_order FROM proof_wall ORDER BY date DESC, sort_order"
        ).fetchall()
        proof_list = [{"date": r["date"], "task": r["task"], "sort_order": r["sort_order"]} for r in proof_rows]

        return {
            "daily_reflection": {
                "heatmap": heatmap,
                "today": today_obj,
            },
            "seven_fs": {
                "current": current_fs,
                "previous": previous_fs,
                "last_date": last_date,
            },
            "goals": goals_obj,
            "proof_wall": proof_list,
        }


# ── add_pending_edit ──────────────────────────────────────────────────────────

def add_pending_edit(table: str, key: str, field: str, value: str) -> int:
    """
    Record a UI edit queued for the next Sheets write cycle.
    Returns the new edit's id.
    """
    with _get_conn() as conn:
        cursor = conn.execute("""
            INSERT INTO pending_edits (table_name, record_key, field, new_value, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (table, key, field, str(value), _now_iso()))
        return cursor.lastrowid


# ── get_pending_edits ─────────────────────────────────────────────────────────

def get_pending_edits() -> List[Dict[str, Any]]:
    """
    Return all unsynced pending edits as a list of dicts.
    """
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT id, table_name, record_key, field, new_value, created_at
            FROM pending_edits
            WHERE synced_at IS NULL
            ORDER BY id ASC
        """).fetchall()
        return [dict(r) for r in rows]


# ── mark_edits_synced ─────────────────────────────────────────────────────────

def mark_edits_synced(edit_ids: List[int]) -> None:
    """
    Mark a list of edit IDs as synced (sets synced_at to now).
    """
    if not edit_ids:
        return
    now = _now_iso()
    placeholders = ",".join("?" * len(edit_ids))
    with _get_conn() as conn:
        conn.execute(
            f"UPDATE pending_edits SET synced_at=? WHERE id IN ({placeholders})",
            [now] + list(edit_ids)
        )
    print(f"[777_d1_cache] Marked {len(edit_ids)} edit(s) as synced.")


# ── needs_refresh ─────────────────────────────────────────────────────────────

def needs_refresh(max_age_seconds: int = 60) -> bool:
    """
    Returns True if the cache hasn't been written within max_age_seconds,
    or if the DB doesn't exist yet.
    """
    if not DB_PATH.exists():
        return True

    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT value FROM sync_state WHERE key='last_cache_write'"
            ).fetchone()
            if not row:
                return True
            last_write = datetime.fromisoformat(row["value"])
            now = datetime.now(timezone.utc)
            # Make last_write timezone-aware if it isn't
            if last_write.tzinfo is None:
                last_write = last_write.replace(tzinfo=timezone.utc)
            age_seconds = (now - last_write).total_seconds()
            return age_seconds > max_age_seconds
    except Exception as e:
        print(f"[777_d1_cache] needs_refresh error: {e}")
        return True


# ── CLI entrypoint ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """Quick test: init DB and print status."""
    init_db()
    stale = needs_refresh(60)
    print(f"Cache stale: {stale}")
    pending = get_pending_edits()
    print(f"Pending edits: {len(pending)}")

    # If data.json exists, warm the cache
    data_json_path = ROOT / 'exports' / '777-command-center' / 'data.json'
    if data_json_path.exists():
        with open(data_json_path) as f:
            data = json.load(f)
        cache_data(data)
        print("Cache warmed from data.json")
        cached = get_cached_data()
        heatmap_len = len(cached.get("daily_reflection", {}).get("heatmap", []))
        print(f"get_cached_data(): heatmap has {heatmap_len} entries")
    else:
        print("No data.json found — skipping cache warm")
