"""
PureApex — Pure Technology Sales Intelligence
Multi-user sales pipeline tracker
"""

import asyncio
import hashlib
import json
import os
import re
import secrets
import time
import urllib.parse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

import aiosqlite
import bcrypt
import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from starlette.routing import Route

DB_PATH = Path(__file__).parent / "pipeline.db"
STATIC_PATH = Path(__file__).parent / "index.html"

# In-memory session store: token -> {username, display_name, role, expires}
sessions: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# LinkedIn OAuth configuration
# ---------------------------------------------------------------------------
# Load from .env.apex if present, fallback to env vars
_env_apex = Path(__file__).parent / ".env.apex"
if _env_apex.exists():
    for _line in _env_apex.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

LINKEDIN_CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID", "86qlcrlwbfggp0")
LINKEDIN_CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "WPL_AP1.JUh5VLYkIVKfjTX5.MDQVSw==")
LINKEDIN_REDIRECT_URI = "https://apex.purebrain.ai/linkedin/callback"
LINKEDIN_SCOPES = "openid profile w_member_social"

USERS = [
    {"username": "jsmith", "display_name": "John Smith (JB)", "role": "VP Sales", "password": "anchor2026"},
    {"username": "jsanborn", "display_name": "Jared Sanborn", "role": "CEO", "password": "aether2026"},
    {"username": "nolson", "display_name": "Nate Olson", "role": "President PMG", "password": "lyra2026"},
    {"username": "pbliss", "display_name": "Philip Bliss", "role": "CMO", "password": "clarity2026"},
    {"username": "anchor", "display_name": "Anchor (AI)", "role": "AI Sales Partner", "password": "pipeline_api_key_2026"},
]

VALID_TYPES = ("CPG", "Gaming", "Enterprise", "PureBrain")
VALID_GEOGRAPHIES = ("NA", "EMEA", "APAC", "MENA", "LATAM", "Global")
VALID_STAGES = ("Suspect", "Pipeline", "Qualified", "Proposal Submitted", "Proposal Finalised", "Sponsor Commitment", "Proposal Accepted", "Closed Won", "Closed Lost")


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    db = await get_db()
    try:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                contact_name TEXT,
                contact_title TEXT,
                contact_email TEXT,
                contact_linkedin TEXT,
                contact_location TEXT DEFAULT '',
                type TEXT CHECK(type IN ('CPG', 'Gaming', 'Enterprise', 'PureBrain')),
                vertical TEXT,
                geography TEXT CHECK(geography IN ('NA', 'EMEA', 'APAC', 'MENA', 'LATAM', 'Global')),
                stage TEXT CHECK(stage IN ('Suspect', 'Pipeline', 'Qualified', 'Proposal Submitted', 'Proposal Finalised', 'Sponsor Commitment', 'Proposal Accepted', 'Closed Won', 'Closed Lost')) DEFAULT 'Suspect',
                playbook_weapon TEXT,
                owner TEXT NOT NULL,
                estimated_value REAL DEFAULT 0,
                next_action TEXT,
                next_action_date TEXT,
                notes TEXT,
                partner TEXT DEFAULT '',
                meddpicc_metrics TEXT DEFAULT '',
                meddpicc_economic_buyer TEXT DEFAULT '',
                meddpicc_decision_criteria TEXT DEFAULT '',
                meddpicc_decision_process TEXT DEFAULT '',
                meddpicc_paper_process TEXT DEFAULT '',
                meddpicc_identify_pain TEXT DEFAULT '',
                meddpicc_champion TEXT DEFAULT '',
                meddpicc_competition TEXT DEFAULT '',
                emotional_arc TEXT DEFAULT '',
                division TEXT DEFAULT '',
                readiness_pnl_pain INTEGER DEFAULT 0,
                readiness_decision_maker INTEGER DEFAULT 0,
                readiness_competitor INTEGER DEFAULT 0,
                readiness_unique_angle INTEGER DEFAULT 0,
                readiness_proof INTEGER DEFAULT 0,
                stage_changed_at TEXT DEFAULT '',
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER REFERENCES opportunities(id),
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS meeting_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER REFERENCES opportunities(id),
                note_type TEXT DEFAULT 'meeting',
                content TEXT NOT NULL,
                actor TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                access_token TEXT NOT NULL,
                expires_at TIMESTAMP,
                refresh_token TEXT,
                linkedin_id TEXT,
                linkedin_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migrate existing DB: add columns if missing
        cursor = await db.execute("PRAGMA table_info(opportunities)")
        existing_cols = {row[1] for row in await cursor.fetchall()}
        new_cols = [
            ("contact_location", "TEXT DEFAULT ''"),
            ("partner", "TEXT DEFAULT ''"),
            ("meddpicc_metrics", "TEXT DEFAULT ''"),
            ("meddpicc_economic_buyer", "TEXT DEFAULT ''"),
            ("meddpicc_decision_criteria", "TEXT DEFAULT ''"),
            ("meddpicc_decision_process", "TEXT DEFAULT ''"),
            ("meddpicc_paper_process", "TEXT DEFAULT ''"),
            ("meddpicc_identify_pain", "TEXT DEFAULT ''"),
            ("meddpicc_champion", "TEXT DEFAULT ''"),
            ("meddpicc_competition", "TEXT DEFAULT ''"),
            ("emotional_arc", "TEXT DEFAULT ''"),
            ("division", "TEXT DEFAULT ''"),
            ("readiness_pnl_pain", "INTEGER DEFAULT 0"),
            ("readiness_decision_maker", "INTEGER DEFAULT 0"),
            ("readiness_competitor", "INTEGER DEFAULT 0"),
            ("readiness_unique_angle", "INTEGER DEFAULT 0"),
            ("readiness_proof", "INTEGER DEFAULT 0"),
            ("stage_changed_at", "TEXT DEFAULT ''"),
        ]
        for col_name, col_type in new_cols:
            if col_name not in existing_cols:
                await db.execute(f"ALTER TABLE opportunities ADD COLUMN {col_name} {col_type}")

        # Seed users if table is empty
        cursor = await db.execute("SELECT COUNT(*) as cnt FROM users")
        row = await cursor.fetchone()
        if row[0] == 0:
            for u in USERS:
                pw_hash = bcrypt.hashpw(u["password"].encode(), bcrypt.gensalt()).decode()
                await db.execute(
                    "INSERT INTO users (username, display_name, role, password_hash) VALUES (?, ?, ?, ?)",
                    (u["username"], u["display_name"], u["role"], pw_hash),
                )

        # Prospect pages table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS prospect_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                company_name TEXT NOT NULL,
                password TEXT NOT NULL,
                html_content TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                view_count INTEGER DEFAULT 0,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# Prospect page sessions: slug -> set of session tokens that unlocked it
# ---------------------------------------------------------------------------
prospect_sessions: dict[str, set[str]] = {}


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def get_session(request: Request) -> dict | None:
    token = request.cookies.get("session_token")
    if not token:
        # Also check Authorization header for API access
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if token and token in sessions:
        s = sessions[token]
        if s["expires"] > time.time():
            return s
        else:
            del sessions[token]
    return None


def require_auth(request: Request) -> dict:
    s = get_session(request)
    if not s:
        raise PermissionError("Not authenticated")
    return s


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

async def index(request: Request):
    html = STATIC_PATH.read_text()
    return HTMLResponse(html, headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"})


async def api_login(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    username = body.get("username", "").strip().lower()
    password = body.get("password", "")

    if not username or not password:
        return JSONResponse({"error": "Username and password required"}, status_code=400)

    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id, username, display_name, role, password_hash FROM users WHERE username = ?",
            (username,),
        )
        user = await cursor.fetchone()
    finally:
        await db.close()

    if not user:
        return JSONResponse({"error": "Invalid credentials"}, status_code=401)

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return JSONResponse({"error": "Invalid credentials"}, status_code=401)

    token = secrets.token_urlsafe(48)
    sessions[token] = {
        "username": user["username"],
        "display_name": user["display_name"],
        "role": user["role"],
        "expires": time.time() + 86400,  # 24h
    }

    resp = JSONResponse({
        "ok": True,
        "user": {
            "username": user["username"],
            "display_name": user["display_name"],
            "role": user["role"],
        },
    })
    resp.set_cookie(
        "session_token",
        token,
        max_age=86400,
        httponly=True,
        samesite="lax",
    )
    return resp


async def api_logout(request: Request):
    token = request.cookies.get("session_token")
    if token and token in sessions:
        del sessions[token]
    resp = JSONResponse({"ok": True})
    resp.delete_cookie("session_token")
    return resp


async def api_me(request: Request):
    s = get_session(request)
    if not s:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    return JSONResponse({
        "username": s["username"],
        "display_name": s["display_name"],
        "role": s["role"],
    })


async def api_list_opportunities(request: Request):
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    params = request.query_params
    conditions = []
    args = []

    for field in ("owner", "type", "geography", "stage"):
        val = params.get(field)
        if val:
            conditions.append(f"{field} = ?")
            args.append(val)

    vertical = params.get("vertical")
    if vertical:
        conditions.append("vertical LIKE ?")
        args.append(f"%{vertical}%")

    search = params.get("search")
    if search:
        conditions.append("(company LIKE ? OR contact_name LIKE ? OR notes LIKE ?)")
        args.extend([f"%{search}%"] * 3)

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    sort = params.get("sort", "updated_at")
    direction = params.get("dir", "DESC").upper()
    if sort not in ("company", "estimated_value", "stage", "owner", "type", "geography", "updated_at", "created_at"):
        sort = "updated_at"
    if direction not in ("ASC", "DESC"):
        direction = "DESC"

    db = await get_db()
    try:
        cursor = await db.execute(
            f"SELECT * FROM opportunities {where} ORDER BY {sort} {direction}",
            args,
        )
        rows = await cursor.fetchall()
        results = [dict(r) for r in rows]
    finally:
        await db.close()

    return JSONResponse(results)


async def api_get_opportunity(request: Request):
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    opp_id = request.path_params["id"]

    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        opp = await cursor.fetchone()
        if not opp:
            return JSONResponse({"error": "Not found"}, status_code=404)

        cursor2 = await db.execute(
            "SELECT * FROM activity_log WHERE opportunity_id = ? ORDER BY created_at DESC",
            (opp_id,),
        )
        activities = await cursor2.fetchall()

        cursor3 = await db.execute(
            "SELECT * FROM meeting_notes WHERE opportunity_id = ? ORDER BY created_at DESC",
            (opp_id,),
        )
        notes = await cursor3.fetchall()

        result = dict(opp)
        result["activity"] = [dict(a) for a in activities]
        result["meeting_notes"] = [dict(n) for n in notes]
    finally:
        await db.close()

    return JSONResponse(result)


async def api_create_opportunity(request: Request):
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    company = body.get("company", "").strip()
    if not company:
        return JSONResponse({"error": "Company name is required"}, status_code=400)

    opp_type = body.get("type", "")
    if opp_type and opp_type not in VALID_TYPES:
        return JSONResponse({"error": f"Invalid type. Must be one of: {VALID_TYPES}"}, status_code=400)

    geography = body.get("geography", "")
    if geography and geography not in VALID_GEOGRAPHIES:
        return JSONResponse({"error": f"Invalid geography. Must be one of: {VALID_GEOGRAPHIES}"}, status_code=400)

    stage = body.get("stage", "Suspect")
    if stage not in VALID_STAGES:
        return JSONResponse({"error": f"Invalid stage. Must be one of: {VALID_STAGES}"}, status_code=400)

    owner = body.get("owner", session["display_name"]).strip()
    if not owner:
        owner = session["display_name"]

    db = await get_db()
    try:
        now = datetime.utcnow().isoformat()
        cursor = await db.execute(
            """INSERT INTO opportunities
               (company, contact_name, contact_title, contact_email, contact_linkedin,
                contact_location, type, vertical, geography, stage, playbook_weapon, owner,
                estimated_value, next_action, next_action_date, notes, partner,
                meddpicc_metrics, meddpicc_economic_buyer, meddpicc_decision_criteria,
                meddpicc_decision_process, meddpicc_paper_process, meddpicc_identify_pain,
                meddpicc_champion, meddpicc_competition, emotional_arc, division,
                readiness_pnl_pain, readiness_decision_maker, readiness_competitor,
                readiness_unique_angle, readiness_proof, stage_changed_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                company,
                body.get("contact_name", ""),
                body.get("contact_title", ""),
                body.get("contact_email", ""),
                body.get("contact_linkedin", ""),
                body.get("contact_location", ""),
                opp_type or None,
                body.get("vertical", ""),
                geography or None,
                stage,
                body.get("playbook_weapon", ""),
                owner,
                float(body.get("estimated_value", 0)),
                body.get("next_action", ""),
                body.get("next_action_date", ""),
                body.get("notes", ""),
                body.get("partner", ""),
                body.get("meddpicc_metrics", ""),
                body.get("meddpicc_economic_buyer", ""),
                body.get("meddpicc_decision_criteria", ""),
                body.get("meddpicc_decision_process", ""),
                body.get("meddpicc_paper_process", ""),
                body.get("meddpicc_identify_pain", ""),
                body.get("meddpicc_champion", ""),
                body.get("meddpicc_competition", ""),
                body.get("emotional_arc", ""),
                body.get("division", ""),
                int(body.get("readiness_pnl_pain", 0)),
                int(body.get("readiness_decision_maker", 0)),
                int(body.get("readiness_competitor", 0)),
                int(body.get("readiness_unique_angle", 0)),
                int(body.get("readiness_proof", 0)),
                now,
                session["display_name"],
            ),
        )
        opp_id = cursor.lastrowid

        await db.execute(
            "INSERT INTO activity_log (opportunity_id, action, actor) VALUES (?, ?, ?)",
            (opp_id, f"Created opportunity: {company}", session["display_name"]),
        )
        await db.commit()

        cursor2 = await db.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        opp = await cursor2.fetchone()
    finally:
        await db.close()

    return JSONResponse(dict(opp), status_code=201)


async def api_update_opportunity(request: Request):
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    opp_id = request.path_params["id"]

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        existing = await cursor.fetchone()
        if not existing:
            return JSONResponse({"error": "Not found"}, status_code=404)

        existing = dict(existing)
        changes = []

        # Track stage changes specifically
        new_stage = body.get("stage", existing["stage"])
        if new_stage != existing["stage"]:
            if new_stage not in VALID_STAGES:
                return JSONResponse({"error": f"Invalid stage"}, status_code=400)
            changes.append(f"Stage changed from '{existing['stage']}' to '{new_stage}'")

        new_type = body.get("type", existing["type"])
        if new_type and new_type not in VALID_TYPES:
            return JSONResponse({"error": f"Invalid type"}, status_code=400)

        new_geo = body.get("geography", existing["geography"])
        if new_geo and new_geo not in VALID_GEOGRAPHIES:
            return JSONResponse({"error": f"Invalid geography"}, status_code=400)

        # Track value changes
        new_value = float(body.get("estimated_value", existing["estimated_value"]))
        if new_value != existing["estimated_value"]:
            changes.append(f"Value changed from ${existing['estimated_value']:,.0f} to ${new_value:,.0f}")

        # Track owner changes
        new_owner = body.get("owner", existing["owner"])
        if new_owner != existing["owner"]:
            changes.append(f"Owner changed from '{existing['owner']}' to '{new_owner}'")

        # Track note additions
        new_notes = body.get("notes", existing["notes"])
        if new_notes != existing["notes"]:
            changes.append("Notes updated")

        # Track partner changes
        new_partner = body.get("partner", existing.get("partner", ""))
        if new_partner != existing.get("partner", ""):
            changes.append(f"Partner updated to '{new_partner}'")

        # Track emotional arc changes
        new_emotional_arc = body.get("emotional_arc", existing.get("emotional_arc", ""))
        if new_emotional_arc != existing.get("emotional_arc", ""):
            changes.append(f"Emotional arc changed to '{new_emotional_arc}'")

        # Track division changes
        new_division = body.get("division", existing.get("division", ""))
        if new_division != existing.get("division", ""):
            changes.append(f"Division updated to '{new_division}'")

        # Readiness fields (integer 0/1)
        new_readiness_pnl_pain = int(body.get("readiness_pnl_pain", existing.get("readiness_pnl_pain", 0)))
        new_readiness_decision_maker = int(body.get("readiness_decision_maker", existing.get("readiness_decision_maker", 0)))
        new_readiness_competitor = int(body.get("readiness_competitor", existing.get("readiness_competitor", 0)))
        new_readiness_unique_angle = int(body.get("readiness_unique_angle", existing.get("readiness_unique_angle", 0)))
        new_readiness_proof = int(body.get("readiness_proof", existing.get("readiness_proof", 0)))

        # Stage timer: update stage_changed_at when stage changes
        new_stage_changed_at = existing.get("stage_changed_at", "")
        if new_stage != existing["stage"]:
            new_stage_changed_at = datetime.utcnow().isoformat()

        # Generic field update tracking
        for field in ("company", "contact_name", "contact_title", "contact_email",
                       "contact_linkedin", "contact_location", "vertical", "playbook_weapon",
                       "next_action", "next_action_date"):
            old_val = existing.get(field, "")
            new_val = body.get(field, old_val)
            if new_val != old_val and field not in ("notes",):
                changes.append(f"{field.replace('_', ' ').title()} updated")

        now = datetime.utcnow().isoformat()

        await db.execute(
            """UPDATE opportunities SET
               company = ?, contact_name = ?, contact_title = ?, contact_email = ?,
               contact_linkedin = ?, contact_location = ?, type = ?, vertical = ?, geography = ?,
               stage = ?, playbook_weapon = ?, owner = ?, estimated_value = ?,
               next_action = ?, next_action_date = ?, notes = ?, partner = ?,
               meddpicc_metrics = ?, meddpicc_economic_buyer = ?, meddpicc_decision_criteria = ?,
               meddpicc_decision_process = ?, meddpicc_paper_process = ?, meddpicc_identify_pain = ?,
               meddpicc_champion = ?, meddpicc_competition = ?, emotional_arc = ?, division = ?,
               readiness_pnl_pain = ?, readiness_decision_maker = ?, readiness_competitor = ?,
               readiness_unique_angle = ?, readiness_proof = ?, stage_changed_at = ?,
               updated_at = ?
               WHERE id = ?""",
            (
                body.get("company", existing["company"]),
                body.get("contact_name", existing["contact_name"]),
                body.get("contact_title", existing["contact_title"]),
                body.get("contact_email", existing["contact_email"]),
                body.get("contact_linkedin", existing["contact_linkedin"]),
                body.get("contact_location", existing.get("contact_location", "")),
                new_type or None,
                body.get("vertical", existing["vertical"]),
                new_geo or None,
                new_stage,
                body.get("playbook_weapon", existing["playbook_weapon"]),
                new_owner,
                new_value,
                body.get("next_action", existing["next_action"]),
                body.get("next_action_date", existing["next_action_date"]),
                new_notes,
                new_partner,
                body.get("meddpicc_metrics", existing.get("meddpicc_metrics", "")),
                body.get("meddpicc_economic_buyer", existing.get("meddpicc_economic_buyer", "")),
                body.get("meddpicc_decision_criteria", existing.get("meddpicc_decision_criteria", "")),
                body.get("meddpicc_decision_process", existing.get("meddpicc_decision_process", "")),
                body.get("meddpicc_paper_process", existing.get("meddpicc_paper_process", "")),
                body.get("meddpicc_identify_pain", existing.get("meddpicc_identify_pain", "")),
                body.get("meddpicc_champion", existing.get("meddpicc_champion", "")),
                body.get("meddpicc_competition", existing.get("meddpicc_competition", "")),
                new_emotional_arc,
                new_division,
                new_readiness_pnl_pain,
                new_readiness_decision_maker,
                new_readiness_competitor,
                new_readiness_unique_angle,
                new_readiness_proof,
                new_stage_changed_at,
                now,
                opp_id,
            ),
        )

        if not changes:
            changes.append("Record updated")

        for change in changes:
            await db.execute(
                "INSERT INTO activity_log (opportunity_id, action, actor) VALUES (?, ?, ?)",
                (opp_id, change, session["display_name"]),
            )

        await db.commit()

        cursor2 = await db.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
        opp = await cursor2.fetchone()
    finally:
        await db.close()

    return JSONResponse(dict(opp))


async def api_stats(request: Request):
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    db = await get_db()
    try:
        # Total pipeline
        cursor = await db.execute(
            "SELECT COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage NOT IN ('Closed Lost')"
        )
        total = dict(await cursor.fetchone())

        # By stage
        cursor = await db.execute(
            "SELECT stage, COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities GROUP BY stage"
        )
        by_stage = [dict(r) for r in await cursor.fetchall()]

        # By owner
        cursor = await db.execute(
            "SELECT owner, COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage NOT IN ('Closed Lost') GROUP BY owner"
        )
        by_owner = [dict(r) for r in await cursor.fetchall()]

        # By type
        cursor = await db.execute(
            "SELECT type, COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage NOT IN ('Closed Lost') GROUP BY type"
        )
        by_type = [dict(r) for r in await cursor.fetchall()]

        # By geography
        cursor = await db.execute(
            "SELECT geography, COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage NOT IN ('Closed Lost') GROUP BY geography"
        )
        by_geography = [dict(r) for r in await cursor.fetchall()]

        # Won/Lost
        cursor = await db.execute(
            "SELECT COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage = 'Closed Won'"
        )
        won = dict(await cursor.fetchone())

        cursor = await db.execute(
            "SELECT COUNT(*) as count, COALESCE(SUM(estimated_value), 0) as total FROM opportunities WHERE stage = 'Closed Lost'"
        )
        lost = dict(await cursor.fetchone())

    finally:
        await db.close()

    return JSONResponse({
        "total": total,
        "by_stage": by_stage,
        "by_owner": by_owner,
        "by_type": by_type,
        "by_geography": by_geography,
        "won": won,
        "lost": lost,
    })


async def api_activity(request: Request):
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    limit = int(request.query_params.get("limit", 50))
    if limit > 200:
        limit = 200

    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT a.*, o.company
               FROM activity_log a
               LEFT JOIN opportunities o ON a.opportunity_id = o.id
               ORDER BY a.created_at DESC
               LIMIT ?""",
            (limit,),
        )
        rows = await cursor.fetchall()
        results = [dict(r) for r in rows]
    finally:
        await db.close()

    return JSONResponse(results)


async def api_accounts(request: Request):
    """Get opportunities grouped by company (Account view)."""
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    db = await get_db()
    try:
        cursor = await db.execute("""
            SELECT company,
                   COUNT(*) as deal_count,
                   COALESCE(SUM(estimated_value), 0) as total_value,
                   COUNT(DISTINCT contact_name) as contact_count
            FROM opportunities
            GROUP BY company
            ORDER BY deal_count DESC, total_value DESC
        """)
        accounts = [dict(r) for r in await cursor.fetchall()]

        for account in accounts:
            cursor = await db.execute("""
                SELECT id, contact_name, contact_title, contact_email, contact_linkedin,
                       contact_location, stage, estimated_value, type, partner, next_action,
                       division
                FROM opportunities
                WHERE company = ?
                ORDER BY estimated_value DESC
            """, (account['company'],))
            account['opportunities'] = [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()

    return JSONResponse(accounts)


async def api_get_notes(request: Request):
    """Get meeting notes for an opportunity."""
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    opp_id = request.path_params["id"]

    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM meeting_notes WHERE opportunity_id = ? ORDER BY created_at DESC",
            (opp_id,),
        )
        notes = [dict(r) for r in await cursor.fetchall()]
    finally:
        await db.close()

    return JSONResponse(notes)


async def api_add_note(request: Request):
    """Add a meeting note to an opportunity."""
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    opp_id = request.path_params["id"]

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    content = body.get("content", "").strip()
    if not content:
        return JSONResponse({"error": "Note content is required"}, status_code=400)

    note_type = body.get("note_type", "meeting")
    if note_type not in ("meeting", "call", "email", "general"):
        note_type = "general"

    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO meeting_notes (opportunity_id, note_type, content, actor) VALUES (?, ?, ?, ?)",
            (opp_id, note_type, content, session["display_name"]),
        )
        note_id = cursor.lastrowid

        await db.execute(
            "INSERT INTO activity_log (opportunity_id, action, actor) VALUES (?, ?, ?)",
            (opp_id, f"Added {note_type} note", session["display_name"]),
        )

        await db.execute(
            "UPDATE opportunities SET updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), opp_id),
        )

        await db.commit()

        cursor2 = await db.execute("SELECT * FROM meeting_notes WHERE id = ?", (note_id,))
        note = await cursor2.fetchone()
    finally:
        await db.close()

    return JSONResponse(dict(note), status_code=201)


async def api_owners(request: Request):
    """Get list of all users for owner dropdown."""
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    db = await get_db()
    try:
        cursor = await db.execute("SELECT display_name, role FROM users ORDER BY display_name")
        rows = await cursor.fetchall()
        results = [dict(r) for r in rows]
    finally:
        await db.close()

    return JSONResponse(results)


# ---------------------------------------------------------------------------
# LinkedIn OAuth
# ---------------------------------------------------------------------------

async def linkedin_auth(request: Request):
    """Redirect user to LinkedIn OAuth authorization page."""
    state = secrets.token_urlsafe(32)
    # Store state in a cookie to verify on callback
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "state": state,
        "scope": LINKEDIN_SCOPES,
    })
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{params}"
    resp = RedirectResponse(url=auth_url)
    resp.set_cookie("linkedin_oauth_state", state, max_age=600, httponly=True, samesite="lax")
    return resp


async def linkedin_callback(request: Request):
    """Handle LinkedIn OAuth callback - exchange code for access token."""
    error = request.query_params.get("error")
    if error:
        error_desc = request.query_params.get("error_description", "Unknown error")
        return HTMLResponse(
            f"<html><body><h2>LinkedIn Authorization Failed</h2>"
            f"<p>{error}: {error_desc}</p>"
            f"<p><a href='/linkedin/auth'>Try again</a></p></body></html>",
            status_code=400,
        )

    code = request.query_params.get("code")
    if not code:
        return HTMLResponse(
            "<html><body><h2>Missing authorization code</h2>"
            "<p><a href='/linkedin/auth'>Try again</a></p></body></html>",
            status_code=400,
        )

    # Exchange code for access token
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            token_resp = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": LINKEDIN_REDIRECT_URI,
                    "client_id": LINKEDIN_CLIENT_ID,
                    "client_secret": LINKEDIN_CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if token_resp.status_code != 200:
                return HTMLResponse(
                    f"<html><body><h2>Token Exchange Failed</h2>"
                    f"<p>Status: {token_resp.status_code}</p>"
                    f"<pre>{token_resp.text}</pre>"
                    f"<p><a href='/linkedin/auth'>Try again</a></p></body></html>",
                    status_code=502,
                )
            token_data = token_resp.json()

        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 5184000)  # default 60 days
        refresh_token = token_data.get("refresh_token")
        expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()

        # Fetch user profile from LinkedIn
        linkedin_id = None
        linkedin_name = None
        async with httpx.AsyncClient(timeout=30.0) as client:
            profile_resp = await client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if profile_resp.status_code == 200:
                profile = profile_resp.json()
                linkedin_id = profile.get("sub")
                linkedin_name = profile.get("name", "")

        # Store token in database (replace any existing row)
        db = await get_db()
        try:
            await db.execute("DELETE FROM linkedin_tokens")
            await db.execute(
                """INSERT INTO linkedin_tokens
                   (access_token, expires_at, refresh_token, linkedin_id, linkedin_name)
                   VALUES (?, ?, ?, ?, ?)""",
                (access_token, expires_at, refresh_token, linkedin_id, linkedin_name),
            )
            await db.commit()
        finally:
            await db.close()

        display_name = linkedin_name or linkedin_id or "Unknown"
        return HTMLResponse(
            f"<html><head><style>"
            f"body {{ font-family: -apple-system, sans-serif; display: flex; justify-content: center; "
            f"align-items: center; min-height: 100vh; margin: 0; background: #0f172a; color: #e2e8f0; }}"
            f".card {{ background: #1e293b; border-radius: 12px; padding: 48px; text-align: center; "
            f"box-shadow: 0 8px 32px rgba(0,0,0,0.3); max-width: 480px; }}"
            f"h2 {{ color: #22c55e; margin-bottom: 8px; }}"
            f"p {{ color: #94a3b8; line-height: 1.6; }}"
            f".name {{ color: #38bdf8; font-weight: 600; }}"
            f"</style></head>"
            f"<body><div class='card'>"
            f"<h2>LinkedIn Connected!</h2>"
            f"<p>Authenticated as <span class='name'>{display_name}</span></p>"
            f"<p>Token expires: {expires_at[:10]}</p>"
            f"<p>You can close this tab and return to PureApex.</p>"
            f"</div></body></html>"
        )

    except Exception as exc:
        return HTMLResponse(
            f"<html><body><h2>Error during LinkedIn OAuth</h2>"
            f"<p>{type(exc).__name__}: {exc}</p>"
            f"<p><a href='/linkedin/auth'>Try again</a></p></body></html>",
            status_code=500,
        )


async def linkedin_status(request: Request):
    """Check whether LinkedIn is connected and token status."""
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT access_token, expires_at, linkedin_id, linkedin_name, created_at "
            "FROM linkedin_tokens ORDER BY created_at DESC LIMIT 1"
        )
        row = await cursor.fetchone()
    finally:
        await db.close()

    if not row:
        return JSONResponse({"connected": False})

    row = dict(row)
    now = datetime.utcnow().isoformat()
    is_expired = row["expires_at"] and row["expires_at"] < now

    return JSONResponse({
        "connected": True,
        "expired": is_expired,
        "linkedin_id": row["linkedin_id"],
        "linkedin_name": row["linkedin_name"],
        "expires_at": row["expires_at"],
        "connected_at": row["created_at"],
    })


async def linkedin_post(request: Request):
    """Publish a post to LinkedIn using the stored access token."""
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    text = body.get("text", "").strip()
    if not text:
        return JSONResponse({"error": "Post text is required"}, status_code=400)

    # Get stored token
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT access_token, expires_at, linkedin_id "
            "FROM linkedin_tokens ORDER BY created_at DESC LIMIT 1"
        )
        row = await cursor.fetchone()
    finally:
        await db.close()

    if not row:
        return JSONResponse({"error": "LinkedIn not connected. Visit /linkedin/auth first."}, status_code=400)

    row = dict(row)
    now = datetime.utcnow().isoformat()
    if row["expires_at"] and row["expires_at"] < now:
        return JSONResponse({"error": "LinkedIn token expired. Re-authorize at /linkedin/auth"}, status_code=401)

    access_token = row["access_token"]
    linkedin_id = row["linkedin_id"]

    if not linkedin_id:
        return JSONResponse({"error": "LinkedIn user ID not available. Re-authorize at /linkedin/auth"}, status_code=400)

    # Use the LinkedIn Posts API (v2 REST, versioned)
    post_payload = {
        "author": f"urn:li:person:{linkedin_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text,
                },
                "shareMediaCategory": "NONE",
            },
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC",
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.linkedin.com/v2/ugcPosts",
                json=post_payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                    "Content-Type": "application/json",
                },
            )

            if resp.status_code in (200, 201):
                result = resp.json()
                post_id = result.get("id", "")
                # LinkedIn UGC post IDs look like "urn:li:ugcPost:1234567"
                # Construct a URL if we can
                post_url = None
                if post_id:
                    # Extract numeric ID for URL
                    parts = post_id.split(":")
                    if len(parts) >= 4:
                        post_url = f"https://www.linkedin.com/feed/update/{post_id}"

                return JSONResponse({
                    "ok": True,
                    "post_id": post_id,
                    "post_url": post_url,
                })
            else:
                return JSONResponse({
                    "error": "LinkedIn API error",
                    "status": resp.status_code,
                    "detail": resp.text,
                }, status_code=502)

    except Exception as exc:
        return JSONResponse({
            "error": f"Failed to post: {type(exc).__name__}: {exc}",
        }, status_code=500)


# ---------------------------------------------------------------------------
# Prospect Pages (password-protected custom pages at /p/{slug})
# ---------------------------------------------------------------------------

def _prospect_page_authenticated(request: Request, slug: str) -> bool:
    """Check if the current request has a valid prospect page session cookie."""
    token = request.cookies.get(f"pp_{slug}")
    if token and slug in prospect_sessions and token in prospect_sessions[slug]:
        return True
    return False


async def prospect_page_view(request: Request):
    """GET /p/{slug} - Show password gate or page content."""
    slug = request.path_params["slug"]

    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM prospect_pages WHERE slug = ? AND is_active = 1",
            (slug,),
        )
        page = await cursor.fetchone()
    finally:
        await db.close()

    if not page:
        return HTMLResponse(
            "<html><body style='font-family:-apple-system,sans-serif;display:flex;"
            "justify-content:center;align-items:center;min-height:100vh;margin:0;"
            "background:#0f172a;color:#94a3b8;'>"
            "<div style='text-align:center;'>"
            "<h1 style='color:#e2e8f0;'>Page Not Found</h1>"
            "<p>This page does not exist or is no longer available.</p>"
            "</div></body></html>",
            status_code=404,
        )

    page = dict(page)

    # Check if already authenticated for this page
    if _prospect_page_authenticated(request, slug):
        # Increment view count
        db = await get_db()
        try:
            await db.execute(
                "UPDATE prospect_pages SET view_count = view_count + 1 WHERE slug = ?",
                (slug,),
            )
            await db.commit()
        finally:
            await db.close()
        return HTMLResponse(page["html_content"])

    # Show password gate
    error_msg = request.query_params.get("error", "")
    error_html = ""
    if error_msg:
        error_html = (
            '<p style="color:#ef4444;margin-bottom:16px;font-size:14px;">'
            'Incorrect password. Please try again.</p>'
        )

    company_name = page["company_name"]
    gate_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{company_name} | PureBrain</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; margin: 0; background: #0f172a; color: #e2e8f0;
        }}
        .card {{
            background: #1e293b; border-radius: 16px; padding: 48px 40px;
            text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            max-width: 420px; width: 90%;
        }}
        .logo {{
            font-size: 28px; font-weight: 700; color: #38bdf8;
            margin-bottom: 8px; letter-spacing: -0.5px;
        }}
        .logo span {{ color: #22c55e; }}
        .subtitle {{
            color: #64748b; font-size: 13px; margin-bottom: 32px;
            text-transform: uppercase; letter-spacing: 1px;
        }}
        .exclusive {{
            color: #94a3b8; font-size: 15px; margin-bottom: 24px; line-height: 1.5;
        }}
        .exclusive strong {{ color: #f1f5f9; }}
        form {{ display: flex; flex-direction: column; gap: 12px; }}
        input[type="password"] {{
            background: #0f172a; border: 1px solid #334155; border-radius: 8px;
            padding: 14px 16px; color: #e2e8f0; font-size: 16px;
            outline: none; transition: border-color 0.2s;
        }}
        input[type="password"]:focus {{ border-color: #38bdf8; }}
        input[type="password"]::placeholder {{ color: #475569; }}
        button {{
            background: linear-gradient(135deg, #38bdf8, #22c55e);
            border: none; border-radius: 8px; padding: 14px;
            color: #0f172a; font-size: 16px; font-weight: 600;
            cursor: pointer; transition: opacity 0.2s;
        }}
        button:hover {{ opacity: 0.9; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">Pure<span>Brain</span></div>
        <div class="subtitle">Pure Technology</div>
        <p class="exclusive">This page was prepared exclusively for<br><strong>{company_name}</strong></p>
        {error_html}
        <form method="POST" action="/p/{slug}/auth">
            <input type="password" name="password" placeholder="Enter access password" required autofocus>
            <button type="submit">Access Page</button>
        </form>
    </div>
</body>
</html>"""
    return HTMLResponse(gate_html)


async def prospect_page_auth(request: Request):
    """POST /p/{slug}/auth - Validate password, set session cookie, redirect."""
    slug = request.path_params["slug"]

    form = await request.form()
    password = form.get("password", "")

    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT password FROM prospect_pages WHERE slug = ? AND is_active = 1",
            (slug,),
        )
        page = await cursor.fetchone()
    finally:
        await db.close()

    if not page:
        return RedirectResponse(url=f"/p/{slug}", status_code=303)

    if password != page["password"]:
        return RedirectResponse(url=f"/p/{slug}?error=1", status_code=303)

    # Password correct - create session token
    token = secrets.token_urlsafe(32)
    if slug not in prospect_sessions:
        prospect_sessions[slug] = set()
    prospect_sessions[slug].add(token)

    resp = RedirectResponse(url=f"/p/{slug}", status_code=303)
    resp.set_cookie(
        f"pp_{slug}",
        token,
        max_age=86400 * 7,  # 7 days
        httponly=True,
        samesite="lax",
    )
    return resp


async def api_list_prospect_pages(request: Request):
    """GET /api/prospect-pages - List all pages (requires PureApex login)."""
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id, slug, company_name, is_active, view_count, created_by, "
            "created_at, updated_at FROM prospect_pages ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        results = [dict(r) for r in rows]
    finally:
        await db.close()

    return JSONResponse(results)


async def api_create_prospect_page(request: Request):
    """POST /api/prospect-pages - Create a new page (requires PureApex login)."""
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    slug = body.get("slug", "").strip().lower()
    company_name = body.get("company_name", "").strip()
    password = body.get("password", "").strip()
    html_content = body.get("html_content", "").strip()

    if not slug:
        return JSONResponse({"error": "Slug is required"}, status_code=400)
    if not company_name:
        return JSONResponse({"error": "Company name is required"}, status_code=400)
    if not password:
        return JSONResponse({"error": "Password is required"}, status_code=400)
    if not html_content:
        return JSONResponse({"error": "HTML content is required"}, status_code=400)

    # Validate slug: only lowercase letters, numbers, hyphens
    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', slug) and len(slug) > 1:
        return JSONResponse(
            {"error": "Slug must contain only lowercase letters, numbers, and hyphens"},
            status_code=400,
        )
    if len(slug) == 1 and not re.match(r'^[a-z0-9]$', slug):
        return JSONResponse(
            {"error": "Slug must contain only lowercase letters, numbers, and hyphens"},
            status_code=400,
        )

    db = await get_db()
    try:
        # Check for duplicate slug
        cursor = await db.execute(
            "SELECT id FROM prospect_pages WHERE slug = ?", (slug,)
        )
        if await cursor.fetchone():
            return JSONResponse({"error": "A page with this slug already exists"}, status_code=409)

        now = datetime.utcnow().isoformat()
        cursor = await db.execute(
            """INSERT INTO prospect_pages
               (slug, company_name, password, html_content, created_by, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (slug, company_name, password, html_content, session["display_name"], now, now),
        )
        page_id = cursor.lastrowid
        await db.commit()

        cursor2 = await db.execute(
            "SELECT id, slug, company_name, is_active, view_count, created_by, "
            "created_at, updated_at FROM prospect_pages WHERE id = ?",
            (page_id,),
        )
        page = await cursor2.fetchone()
    finally:
        await db.close()

    return JSONResponse(dict(page), status_code=201)


async def api_update_prospect_page(request: Request):
    """PUT /api/prospect-pages/{slug} - Update page content (requires PureApex login)."""
    try:
        session = require_auth(request)
    except PermissionError:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    slug = request.path_params["slug"]

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM prospect_pages WHERE slug = ?", (slug,)
        )
        existing = await cursor.fetchone()
        if not existing:
            return JSONResponse({"error": "Page not found"}, status_code=404)

        existing = dict(existing)
        now = datetime.utcnow().isoformat()

        new_company_name = body.get("company_name", existing["company_name"])
        new_password = body.get("password", existing["password"])
        new_html_content = body.get("html_content", existing["html_content"])
        new_is_active = body.get("is_active", existing["is_active"])

        await db.execute(
            """UPDATE prospect_pages SET
               company_name = ?, password = ?, html_content = ?,
               is_active = ?, updated_at = ?
               WHERE slug = ?""",
            (new_company_name, new_password, new_html_content, int(new_is_active), now, slug),
        )
        await db.commit()

        cursor2 = await db.execute(
            "SELECT id, slug, company_name, is_active, view_count, created_by, "
            "created_at, updated_at FROM prospect_pages WHERE slug = ?",
            (slug,),
        )
        page = await cursor2.fetchone()
    finally:
        await db.close()

    return JSONResponse(dict(page))


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------


async def serve_static_file(request: Request):
    """Serve files from the static/ directory at /s/ path."""
    import mimetypes
    filename = request.path_params.get("path", "")
    static_dir = Path(__file__).parent / "static"
    filepath = static_dir / filename
    if not filepath.exists() or not filepath.is_file() or ".." in filename:
        return Response("Not found", status_code=404)
    content_type = mimetypes.guess_type(str(filepath))[0] or "text/html"
    return Response(filepath.read_bytes(), media_type=content_type)


routes = [
    Route("/", index),
    Route("/api/login", api_login, methods=["POST"]),
    Route("/api/logout", api_logout, methods=["POST"]),
    Route("/api/me", api_me),
    Route("/api/opportunities", api_list_opportunities, methods=["GET"]),
    Route("/api/opportunities", api_create_opportunity, methods=["POST"]),
    Route("/api/opportunities/{id:int}", api_get_opportunity, methods=["GET"]),
    Route("/api/opportunities/{id:int}", api_update_opportunity, methods=["PUT"]),
    Route("/api/stats", api_stats),
    Route("/api/activity", api_activity),
    Route("/api/owners", api_owners),
    Route("/api/accounts", api_accounts),
    Route("/api/opportunities/{id:int}/notes", api_get_notes, methods=["GET"]),
    Route("/api/opportunities/{id:int}/notes", api_add_note, methods=["POST"]),
    Route("/linkedin/auth", linkedin_auth),
    Route("/linkedin/callback", linkedin_callback),
    Route("/api/linkedin/status", linkedin_status),
    Route("/api/linkedin/post", linkedin_post, methods=["POST"]),
    Route("/s/{path:path}", serve_static_file),
    # Prospect pages
    Route("/p/{slug:str}", prospect_page_view, methods=["GET"]),
    Route("/p/{slug:str}/auth", prospect_page_auth, methods=["POST"]),
    Route("/api/prospect-pages", api_list_prospect_pages, methods=["GET"]),
    Route("/api/prospect-pages", api_create_prospect_page, methods=["POST"]),
    Route("/api/prospect-pages/{slug:str}", api_update_prospect_page, methods=["PUT"]),
]

@asynccontextmanager
async def lifespan(app):
    await init_db()
    print("PureApex database initialized.")
    yield


app = Starlette(routes=routes, lifespan=lifespan)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8098, reload=False, log_level="info")
