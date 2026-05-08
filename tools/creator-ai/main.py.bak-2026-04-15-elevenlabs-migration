"""
PureBrain Creator AI — FastAPI Server
Converted from Cloudflare Worker (_worker.js) to Python/FastAPI + SQLite
Port: 8871
Deployment: Cloudflare Tunnel → social.purebrain.ai
"""

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
import sqlite3
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

# ── Config ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
load_dotenv(ROOT.parent.parent / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
# JWT secret from wrangler.toml — plain token-in-DB approach (no JWT library needed)
SESSION_SECRET = os.getenv("CREATOR_SESSION_SECRET", "a858ccdd23babc7e27a2312add9dd162")

DB_PATH = ROOT / "creator.db"
SCHEMA_PATH = ROOT.parent.parent / "exports" / "departments" / "systems-technology" / "creator-ai-sprint" / "schema.sql"
STATIC_PATH = ROOT.parent.parent / "exports" / "cf-pages-deploy" / "creator"

ALLOWED_ORIGINS = [
    "https://creator.purebrain.ai",
    "https://social.purebrain.ai",
    "https://purebrain-staging.pages.dev",
    "http://localhost:3000",
    "http://localhost:8871",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [creator-ai] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("creator-ai")


# ── Database ────────────────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    """Apply schema to local SQLite database."""
    if not SCHEMA_PATH.exists():
        logger.error(f"Schema not found at {SCHEMA_PATH}")
        return
    schema = SCHEMA_PATH.read_text()
    conn = get_db()
    try:
        # Execute each statement separately (SQLite doesn't support executescript + WAL sometimes)
        conn.executescript(schema)
        conn.commit()
        logger.info("Database schema applied successfully")
    except Exception as e:
        logger.warning(f"Schema init note: {e}")
    finally:
        conn.close()


def db_one(query: str, params: tuple = ()) -> Optional[dict]:
    conn = get_db()
    try:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def db_all(query: str, params: tuple = ()) -> list:
    conn = get_db()
    try:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def db_run(query: str, params: tuple = ()):
    conn = get_db()
    try:
        conn.execute(query, params)
        conn.commit()
    finally:
        conn.close()


def db_run_many(query: str, param_list: list):
    conn = get_db()
    try:
        for params in param_list:
            conn.execute(query, params)
        conn.commit()
    finally:
        conn.close()


# ── In-memory rate limiter ─────────────────────────────────────────────────────

_rate_limit_map: dict = {}

def check_rate_limit(key: str, max_attempts: int, window_seconds: int) -> bool:
    now = time.time()
    entry = _rate_limit_map.get(key)
    if entry and (now - entry["start"]) < window_seconds:
        if entry["count"] >= max_attempts:
            return False
        entry["count"] += 1
        return True
    _rate_limit_map[key] = {"start": now, "count": 1}
    # Periodic cleanup
    if len(_rate_limit_map) > 10000:
        cutoff = now - window_seconds * 2
        stale = [k for k, v in _rate_limit_map.items() if v["start"] < cutoff]
        for k in stale:
            del _rate_limit_map[k]
    return True


# ── Password hashing ───────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"pbkdf2:{salt}:{h.hex()}"


def verify_password(password: str, stored: str) -> bool:
    if stored.startswith("pbkdf2:"):
        parts = stored.split(":")
        if len(parts) != 3:
            return False
        _, salt, stored_hash = parts
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        return hmac.compare_digest(h.hex(), stored_hash)
    else:
        # Legacy salt:sha256 format
        parts = stored.split(":")
        if len(parts) != 2:
            return False
        salt, stored_hash = parts
        h = hashlib.sha256((salt + password).encode()).hexdigest()
        return hmac.compare_digest(h, stored_hash)


# ── Session / auth ─────────────────────────────────────────────────────────────

def create_session(creator_id: str) -> str:
    token = str(uuid.uuid4()) + "-" + str(uuid.uuid4())
    expires_at = int(time.time()) + 60 * 60 * 24 * 30  # 30 days
    db_run(
        "INSERT INTO sessions (token, creator_id, expires_at) VALUES (?, ?, ?)",
        (token, creator_id, expires_at),
    )
    return token


def verify_token(token: Optional[str]) -> Optional[str]:
    if not token:
        return None
    now = int(time.time())
    row = db_one(
        "SELECT creator_id FROM sessions WHERE token = ? AND expires_at > ?",
        (token, now),
    )
    return row["creator_id"] if row else None


def extract_token(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


async def require_auth(request: Request) -> str:
    token = extract_token(request)
    creator_id = verify_token(token)
    if not creator_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return creator_id


# ── Anthropic helper ───────────────────────────────────────────────────────────

async def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not configured")
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
        )
        if not resp.is_success:
            raise ValueError(f"Anthropic API error {resp.status_code}: {resp.text}")
        data = resp.json()
        return data.get("content", [{}])[0].get("text", "")


async def call_claude_messages(system_prompt: str, messages: list, max_tokens: int = 512) -> str:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not configured")
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": messages,
            },
        )
        if not resp.is_success:
            raise ValueError(f"Anthropic API error {resp.status_code}: {resp.text}")
        data = resp.json()
        return data.get("content", [{}])[0].get("text", "")


# ── Voice + platform helpers ───────────────────────────────────────────────────

PLATFORM_GUIDES = {
    "linkedin": "LinkedIn format: use line breaks for readability, professional hooks that open with insight or a bold claim, max 1300 characters, optional 3-5 hashtags at end. No walls of text.",
    "instagram": "Instagram format: emoji-driven opening hook on first line, storytelling narrative arc, 5-10 relevant hashtags at end, max 2200 characters. Make it visually scannable.",
    "twitter": "Twitter/X format: under 280 characters for a single tweet, OR if longer write a numbered thread (1/, 2/, 3/ etc). Each tweet must stand alone and be punchy.",
    "bluesky": "Bluesky format: under 300 characters, conversational and authentic, minimal hashtags (0-2 max), no corporate-speak. Think smart casual.",
    "email": "Email newsletter format: subject line on first line prefixed with 'Subject:', then body. Personal, direct, and conversational.",
}

LENGTH_GUIDES = {
    "short": "Keep it under 150 words.",
    "medium": "Aim for 200-400 words.",
    "long": "Write 400-700 words with depth and examples.",
}

STOP_WORDS = {
    "that", "this", "with", "from", "have", "been", "will", "your", "what",
    "when", "where", "which", "they", "their", "there", "about", "more",
    "into", "then", "than", "just", "some", "also", "want", "know", "does",
    "like", "help", "need", "tell", "much", "many", "the", "and", "for",
    "are", "but", "not", "you", "all", "can", "had", "her", "was", "one",
    "our", "out", "has", "him", "his", "how", "man", "new", "now", "old",
    "see", "two", "way", "who", "did", "its", "let", "put", "say", "she",
    "too", "use",
}


def build_voice_context(settings: dict, samples: Optional[str]) -> str:
    fingerprint = settings.get("voice_fingerprint")
    section = f"""CREATOR VOICE PROFILE:
- Tone: {settings.get('tone', 'conversational')}
- Formality: {settings.get('formality', 'balanced')}
- Voice notes from creator: "{settings.get('voice_notes', 'None provided')}" """

    if fingerprint:
        section += f"""

EXTRACTED VOICE FINGERPRINT (deep style analysis):
- Avg sentence length: {fingerprint.get('avg_sentence_length', 'unknown')}
- Vocabulary complexity: {fingerprint.get('vocabulary_complexity', 'unknown')}
- Emoji usage: {fingerprint.get('emoji_usage', 'none')}
- CTA style: {fingerprint.get('cta_style', 'unknown')}
- Opening hook pattern: {fingerprint.get('opening_hook_pattern', 'unknown')}
- Hashtag pattern: {fingerprint.get('hashtag_pattern', 'unknown')}
- Recurring phrases: {', '.join(fingerprint.get('recurring_phrases', [])) or 'none identified'}
- Writing personality: {fingerprint.get('writing_personality', 'unknown')}"""

    if samples:
        section += f"\n\nSAMPLE CONTENT FROM THIS CREATOR (study and match their style):\n{samples}"

    return section


def extract_keywords(text: str) -> list:
    words = re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()
    return [w for w in words if len(w) >= 4 and w not in STOP_WORDS]


def parse_csv(csv_text: str) -> list:
    lines = csv_text.strip().split("\n")
    if not lines:
        return []
    header = [h.strip().strip('"').lower() for h in lines[0].split(",")]
    content_idx = header.index("content") if "content" in header else 0
    platform_idx = header.index("platform") if "platform" in header else -1
    date_idx = header.index("date") if "date" in header else -1

    rows = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        cols = re.findall(r'"[^"]*"|[^,]+', line)
        clean = lambda s: (s or "").strip('"').strip()

        content = clean(cols[content_idx]) if content_idx < len(cols) else ""
        if not content:
            continue

        platform = clean(cols[platform_idx]) if platform_idx >= 0 and platform_idx < len(cols) else "other"
        posted_at = None
        if date_idx >= 0 and date_idx < len(cols):
            try:
                posted_at = int(datetime.fromisoformat(clean(cols[date_idx])).timestamp())
            except Exception:
                posted_at = None

        rows.append({"content_text": content, "platform": platform or "other", "posted_at": posted_at})
    return rows


def new_id() -> str:
    return uuid.uuid4().hex


def now_ts() -> int:
    return int(time.time())


# ── Lifespan ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info(f"Creator AI started on port 8871. DB: {DB_PATH}")
    yield
    logger.info("Creator AI shutting down")


# ── App ─────────────────────────────────────────────────────────────────────────

app = FastAPI(title="PureBrain Creator AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Static files & HTML pages ──────────────────────────────────────────────────

INDEX_HTML = (STATIC_PATH / "index.html").read_text() if (STATIC_PATH / "index.html").exists() else "<h1>Creator AI</h1>"
CHAT_HTML = (STATIC_PATH / "chat.html").read_text() if (STATIC_PATH / "chat.html").exists() else "<h1>Chat</h1>"


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return HTMLResponse(content=INDEX_HTML)


@app.get("/chat.html", response_class=HTMLResponse)
async def serve_chat_html():
    return HTMLResponse(content=CHAT_HTML)


@app.get("/{handle}/chat", response_class=HTMLResponse)
async def serve_chat_for_handle(handle: str):
    # Validate handle format
    if not re.match(r"^[a-z0-9_]{3,32}$", handle.lower()):
        raise HTTPException(status_code=404, detail="Not found")
    return HTMLResponse(content=CHAT_HTML)


# ── Creator public endpoints ───────────────────────────────────────────────────

@app.get("/api/creator/handle-check")
async def handle_check(handle: str = ""):
    handle = handle.lower().strip()
    if not handle:
        return JSONResponse({"error": True, "message": "handle is required"}, status_code=400)
    if not re.match(r"^[a-z0-9_]{3,32}$", handle):
        return JSONResponse({"available": False, "reason": "Handle must be 3-32 chars, letters/numbers/underscores only"})
    existing = db_one("SELECT id FROM creators WHERE handle = ?", (handle,))
    return JSONResponse({"available": not bool(existing), "handle": handle})


@app.post("/api/creator/signup")
async def signup(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    email = (body.get("email") or "").lower().strip()
    password = body.get("password") or ""
    handle = (body.get("handle") or "").lower().strip()
    display_name = (body.get("display_name") or "").strip()
    tone = body.get("tone") or "conversational"
    formality = body.get("formality") or "balanced"
    voice_notes = body.get("voice_notes") or ""
    plan = body.get("plan") or "starter"

    if not email or not password or not handle or not display_name:
        return JSONResponse({"error": True, "message": "email, password, handle, and display_name are required"}, status_code=400)
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return JSONResponse({"error": True, "message": "Invalid email address"}, status_code=400)
    if len(password) < 8:
        return JSONResponse({"error": True, "message": "Password must be at least 8 characters"}, status_code=400)
    if not re.match(r"^[a-z0-9_]{3,32}$", handle):
        return JSONResponse({"error": True, "message": "Handle must be 3-32 chars, alphanumeric + underscores"}, status_code=400)

    if db_one("SELECT id FROM creators WHERE handle = ?", (handle,)):
        return JSONResponse({"error": True, "message": "Handle already taken"}, status_code=409)
    if db_one("SELECT id FROM creators WHERE email = ?", (email,)):
        return JSONResponse({"error": True, "message": "Email already registered"}, status_code=409)

    password_hash = hash_password(password)
    settings = json.dumps({"tone": tone, "formality": formality, "voice_notes": voice_notes, "plan": plan})
    trial_ends_at = now_ts() + 60 * 60 * 24 * 7
    creator_id = new_id()

    db_run(
        "INSERT INTO creators (id, handle, email, password_hash, display_name, subscription_tier, subscription_status, trial_ends_at, settings) VALUES (?, ?, ?, ?, ?, 'trial', 'trial', ?, ?)",
        (creator_id, handle, email, password_hash, display_name, trial_ends_at, settings),
    )

    creator = db_one("SELECT * FROM creators WHERE id = ?", (creator_id,))
    token = create_session(creator_id)

    return JSONResponse({
        "token": token,
        "creator": {
            "id": creator["id"],
            "handle": creator["handle"],
            "email": creator["email"],
            "display_name": creator["display_name"],
            "subscription_tier": creator["subscription_tier"],
            "subscription_status": creator["subscription_status"],
            "trial_ends_at": creator["trial_ends_at"],
            "settings": json.loads(creator["settings"] or "{}"),
        },
    }, status_code=201)


@app.post("/api/creator/login")
async def login(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    email = (body.get("email") or "").lower().strip()
    password = body.get("password") or ""

    if not email or not password:
        return JSONResponse({"error": True, "message": "email and password are required"}, status_code=400)

    if not check_rate_limit(f"login:{email}", 5, 60):
        return JSONResponse({"error": True, "message": "Too many login attempts. Try again in 60 seconds."}, status_code=429)

    creator = db_one("SELECT * FROM creators WHERE email = ?", (email,))
    if not creator:
        return JSONResponse({"error": True, "message": "Invalid credentials"}, status_code=401)

    if not verify_password(password, creator["password_hash"]):
        return JSONResponse({"error": True, "message": "Invalid credentials"}, status_code=401)

    token = create_session(creator["id"])

    return JSONResponse({
        "token": token,
        "creator": {
            "id": creator["id"],
            "handle": creator["handle"],
            "email": creator["email"],
            "display_name": creator["display_name"],
            "subscription_tier": creator["subscription_tier"],
            "subscription_status": creator["subscription_status"],
            "trial_ends_at": creator["trial_ends_at"],
            "settings": json.loads(creator["settings"] or "{}"),
        },
    })


# ── Creator auth'd endpoints ───────────────────────────────────────────────────

@app.get("/api/creator/profile")
async def get_profile(request: Request):
    creator_id = await require_auth(request)
    creator = db_one(
        "SELECT id, handle, email, display_name, subscription_tier, subscription_status, trial_ends_at, settings, created_at FROM creators WHERE id = ?",
        (creator_id,),
    )
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return JSONResponse({**creator, "settings": json.loads(creator["settings"] or "{}")})


@app.put("/api/creator/profile")
async def update_profile(request: Request):
    creator_id = await require_auth(request)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    display_name = body.get("display_name")
    settings_update = body.get("settings")
    n = now_ts()

    if display_name:
        db_run("UPDATE creators SET display_name = ?, updated_at = ? WHERE id = ?", (display_name, n, creator_id))

    if settings_update and isinstance(settings_update, dict):
        current = db_one("SELECT settings FROM creators WHERE id = ?", (creator_id,))
        current_settings = json.loads(current["settings"] or "{}") if current else {}
        merged = {**current_settings, **settings_update}
        db_run("UPDATE creators SET settings = ?, updated_at = ? WHERE id = ?", (json.dumps(merged), n, creator_id))

    creator = db_one(
        "SELECT id, handle, email, display_name, subscription_tier, subscription_status, trial_ends_at, settings, created_at FROM creators WHERE id = ?",
        (creator_id,),
    )
    return JSONResponse({**creator, "settings": json.loads(creator["settings"] or "{}")})


@app.post("/api/creator/knowledge-base")
async def kb_upload(request: Request):
    creator_id = await require_auth(request)
    try:
        form = await request.form()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid form data"}, status_code=400)

    file = form.get("file")
    if not file:
        return JSONResponse({"error": True, "message": "file is required"}, status_code=400)

    tag = form.get("tag") or "other"
    valid_tags = ["pricing", "methodology", "faq", "testimonials", "bio", "other"]
    safe_tag = tag if tag in valid_tags else "other"

    filename = getattr(file, "filename", "unnamed") or "unnamed"
    file_content = await file.read() if hasattr(file, "read") else b""
    file_size = len(file_content)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    type_map = {"pdf": "pdf", "docx": "docx", "doc": "docx", "txt": "txt", "mp3": "audio", "mp4": "video", "wav": "audio"}
    file_type = type_map.get(ext, "txt")

    n = now_ts()
    file_id = new_id()

    db_run(
        "INSERT INTO knowledge_base_files (id, creator_id, filename, file_type, file_size, status, tag, uploaded_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'queued', ?, ?, ?, ?)",
        (file_id, creator_id, filename, file_type, file_size, safe_tag, n, n, n),
    )

    # Simulate background processing — mark active after a moment
    import asyncio
    async def background_activate():
        await asyncio.sleep(2)
        processed_at = now_ts()
        db_run(
            "UPDATE knowledge_base_files SET status = 'active', chunk_count = 5, processed_at = ?, updated_at = ? WHERE id = ?",
            (processed_at, processed_at, file_id),
        )

    import asyncio
    asyncio.create_task(background_activate())

    return JSONResponse({
        "id": file_id,
        "filename": filename,
        "file_type": file_type,
        "file_size": file_size,
        "status": "queued",
        "tag": safe_tag,
        "uploaded_at": n,
    }, status_code=201)


@app.get("/api/creator/knowledge-base")
async def kb_list(request: Request):
    creator_id = await require_auth(request)
    rows = db_all(
        "SELECT id, filename, file_type, file_size, status, tag, chunk_count, uploaded_at, processed_at FROM knowledge_base_files WHERE creator_id = ? ORDER BY uploaded_at DESC",
        (creator_id,),
    )
    return JSONResponse({"files": rows})


@app.delete("/api/creator/knowledge-base/{file_id}")
async def kb_delete(file_id: str, request: Request):
    creator_id = await require_auth(request)
    f = db_one("SELECT id FROM knowledge_base_files WHERE id = ? AND creator_id = ?", (file_id, creator_id))
    if not f:
        return JSONResponse({"error": True, "message": "File not found"}, status_code=404)
    db_run("DELETE FROM knowledge_base_files WHERE id = ? AND creator_id = ?", (file_id, creator_id))
    return JSONResponse({"deleted": True, "id": file_id})


@app.post("/api/creator/content-history")
async def content_history(request: Request):
    creator_id = await require_auth(request)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    content = body.get("content") or ""
    source = body.get("source") or ""

    if not content:
        return JSONResponse({"error": True, "message": "content is required"}, status_code=400)

    n = now_ts()
    if source == "csv":
        rows = parse_csv(content)
    else:
        lines = [l.strip() for l in content.split("\n") if len(l.strip()) > 10]
        rows = [{"content_text": l, "platform": "other", "posted_at": None} for l in lines]

    if not rows:
        return JSONResponse({"error": True, "message": "No valid content found to import"}, status_code=400)

    imported = 0
    for row in rows:
        try:
            db_run(
                "INSERT INTO creator_content_history (creator_id, platform, content_text, posted_at, source, ingested_at, created_at) VALUES (?, ?, ?, ?, 'imported', ?, ?)",
                (creator_id, row["platform"], row["content_text"], row.get("posted_at"), n, n),
            )
            imported += 1
        except Exception:
            pass

    return JSONResponse({"imported_count": imported})


# ── Night 2 endpoints ──────────────────────────────────────────────────────────

@app.post("/api/creator/voice/analyze")
async def voice_analyze(request: Request):
    creator_id = await require_auth(request)
    creator = db_one("SELECT display_name, settings FROM creators WHERE id = ?", (creator_id,))
    if not creator:
        return JSONResponse({"error": True, "message": "Creator not found"}, status_code=404)

    samples = db_all(
        "SELECT content_text, platform FROM creator_content_history WHERE creator_id = ? ORDER BY ingested_at DESC LIMIT 20",
        (creator_id,),
    )
    if not samples:
        return JSONResponse({"error": True, "message": "No content history found. Import some past content first to analyze your voice."}, status_code=400)

    sample_text = "\n\n---\n\n".join(f"[Post {i+1} — {r['platform']}]\n{r['content_text']}" for i, r in enumerate(samples))

    system_prompt = """You are an expert writing analyst specializing in social media voice profiling.
Your job is to analyze writing samples and extract a precise voice fingerprint as structured JSON.
Be specific and data-driven. Look for actual patterns, not generic descriptions."""

    user_prompt = f"""Analyze these {len(samples)} writing samples from creator "{creator['display_name']}" and extract their voice fingerprint.

WRITING SAMPLES:
{sample_text}

Return ONLY a valid JSON object (no markdown, no explanation) with these exact fields:
{{
  "avg_sentence_length": "short (under 10 words) | medium (10-20 words) | long (20+ words)",
  "vocabulary_complexity": "simple | moderate | sophisticated",
  "emoji_usage": "none | occasional (1-3 per post) | frequent (4+ per post)",
  "cta_style": "direct command | soft suggestion | question-based | none",
  "opening_hook_pattern": "describe their typical first line pattern in 10 words or less",
  "hashtag_pattern": "none | minimal (1-3) | moderate (4-7) | heavy (8+)",
  "recurring_phrases": ["phrase1", "phrase2", "phrase3"],
  "writing_personality": "describe their overall voice in one sentence",
  "paragraph_style": "one-liners | short paragraphs | long paragraphs | mixed",
  "punctuation_style": "standard | heavy ellipsis | exclamation heavy | minimal",
  "niche_keywords": ["keyword1", "keyword2", "keyword3"],
  "analyzed_at": "{datetime.utcnow().isoformat()}"
}}"""

    try:
        fingerprint_text = await call_claude(system_prompt, user_prompt, 1024)
    except Exception as e:
        logger.error(f"Voice analyze error: {e}")
        return JSONResponse({"error": True, "message": "Voice analysis failed. Please try again."}, status_code=502)

    try:
        cleaned = re.sub(r"^```json?\n?", "", fingerprint_text, flags=re.I).rstrip("`").strip()
        fingerprint = json.loads(cleaned)
    except Exception:
        return JSONResponse({"error": True, "message": "Voice analysis returned invalid JSON. Please try again."}, status_code=502)

    n = now_ts()
    current_settings = json.loads(creator["settings"] or "{}")
    updated_settings = {**current_settings, "voice_fingerprint": fingerprint}
    db_run("UPDATE creators SET settings = ?, updated_at = ? WHERE id = ?", (json.dumps(updated_settings), n, creator_id))

    return JSONResponse({"voice_fingerprint": fingerprint, "samples_analyzed": len(samples)})


@app.post("/api/creator/content/generate")
async def generate_content(request: Request):
    creator_id = await require_auth(request)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    topic = body.get("topic") or ""
    platform = body.get("platform") or "linkedin"
    length = body.get("length") or "medium"
    generate_all = body.get("generate_all", False)

    if not topic:
        return JSONResponse({"error": True, "message": "topic is required"}, status_code=400)

    safe_length = length if length in ("short", "medium", "long") else "medium"

    creator = db_one("SELECT display_name, settings FROM creators WHERE id = ?", (creator_id,))
    if not creator:
        return JSONResponse({"error": True, "message": "Creator not found"}, status_code=404)

    settings = json.loads(creator["settings"] or "{}")
    history_rows = db_all(
        "SELECT content_text, platform FROM creator_content_history WHERE creator_id = ? ORDER BY ingested_at DESC LIMIT 5",
        (creator_id,),
    )
    samples = "\n\n---\n\n".join(r["content_text"] for r in history_rows)
    voice_ctx = build_voice_context(settings, samples)

    base_system = f"""You are a content ghostwriter for {creator['display_name']}. Your job is to write in their exact voice.

{voice_ctx}

RULES:
- Match their sentence structure, vocabulary, and rhythm exactly
- Do NOT add a disclaimer that this is AI-generated
- Do NOT use generic phrases like "In today's fast-paced world"
- Write as if you ARE them"""

    n = now_ts()

    if generate_all or platform == "all":
        all_platforms = ["linkedin", "instagram", "twitter", "bluesky"]
        system_prompt = f"{base_system}\n- {LENGTH_GUIDES[safe_length]}"
        user_prompt = f'Write a post about: "{topic}" for ALL FOUR of these platforms.\n\nReturn ONLY a valid JSON object (no markdown, no explanation) with this exact structure:\n{{\n  "linkedin": "[LinkedIn post]",\n  "instagram": "[Instagram post]",\n  "twitter": "[Twitter post]",\n  "bluesky": "[Bluesky post]"\n}}'

        try:
            generated_text = await call_claude(system_prompt, user_prompt, 2048)
        except Exception as e:
            logger.error(f"Content gen error: {e}")
            return JSONResponse({"error": True, "message": "Content generation failed. Please try again."}, status_code=502)

        try:
            cleaned = re.sub(r"^```json?\n?", "", generated_text, flags=re.I).rstrip("`").strip()
            content_map = json.loads(cleaned)
        except Exception:
            return JSONResponse({"error": True, "message": "Content generation returned invalid JSON."}, status_code=502)

        draft_ids = {}
        for plt in all_platforms:
            text = content_map.get(plt) or ""
            if not text:
                continue
            draft_id = new_id()
            draft_ids[plt] = draft_id
            db_run(
                "INSERT INTO generated_content (id, creator_id, platform, content_text, topic, status, generation_mode, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'draft', 'on_demand', ?, ?)",
                (draft_id, creator_id, plt, text, topic, n, n),
            )

        return JSONResponse({"generate_all": True, "topic": topic, "content": content_map, "draft_ids": draft_ids})

    # Single platform
    safe_platform = platform if platform in ("linkedin", "instagram", "twitter", "bluesky", "email") else "linkedin"
    system_prompt = f"{base_system}\n- {LENGTH_GUIDES[safe_length]}\n- {PLATFORM_GUIDES[safe_platform]}"
    user_prompt = f'Write a {safe_platform} post about: "{topic}"'

    try:
        generated_text = await call_claude(system_prompt, user_prompt, 1024)
    except Exception as e:
        logger.error(f"Content gen error: {e}")
        return JSONResponse({"error": True, "message": "Content generation failed. Please try again."}, status_code=502)

    draft_id = new_id()
    db_run(
        "INSERT INTO generated_content (id, creator_id, platform, content_text, topic, status, generation_mode, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'draft', 'on_demand', ?, ?)",
        (draft_id, creator_id, safe_platform, generated_text, topic, n, n),
    )

    return JSONResponse({"content": generated_text, "platform": safe_platform, "draft_id": draft_id, "topic": topic})


@app.post("/api/creator/interview/start")
async def interview_start(request: Request):
    creator_id = await require_auth(request)
    creator = db_one("SELECT display_name, settings FROM creators WHERE id = ?", (creator_id,))
    if not creator:
        return JSONResponse({"error": True, "message": "Creator not found"}, status_code=404)

    settings = json.loads(creator["settings"] or "{}")
    recent = db_all(
        "SELECT content_text FROM creator_content_history WHERE creator_id = ? ORDER BY ingested_at DESC LIMIT 5",
        (creator_id,),
    )
    recent_samples = "\n".join(r["content_text"][:200] for r in recent)

    system_prompt = f"""You are an expert content interviewer helping {creator['display_name']} discover compelling content ideas through conversation.
Your job is to ask ONE insightful question at a time that draws out their unique experiences, opinions, and stories.
Ask questions that uncover specific details, not generic thoughts. Make them think."""

    user_prompt = f"""You are about to start an interview with {creator['display_name']} to help them create a social media post.

Their voice profile: Tone={settings.get('tone', 'conversational')}, Formality={settings.get('formality', 'balanced')}
{f"Recent content themes (so you can ask about something fresh):\\n{recent_samples}" if recent_samples else ""}

Ask ONE opening question that will help uncover a compelling story or insight for a post.
The question should be specific, curious, and conversational — not generic.
Return ONLY the question, nothing else."""

    try:
        opening_question = await call_claude(system_prompt, user_prompt, 256)
    except Exception as e:
        logger.error(f"Interview start error: {e}")
        return JSONResponse({"error": True, "message": "Interview start failed. Please try again."}, status_code=502)

    n = now_ts()
    session_id = new_id()
    transcript = json.dumps([{"role": "interviewer", "text": opening_question.strip(), "timestamp": n}])

    db_run(
        "INSERT INTO interview_sessions (id, creator_id, status, transcript, exchange_count, created_at, updated_at) VALUES (?, ?, 'active', ?, 0, ?, ?)",
        (session_id, creator_id, transcript, n, n),
    )

    return JSONResponse({"session_id": session_id, "question": opening_question.strip(), "exchange_count": 0}, status_code=201)


@app.post("/api/creator/interview/respond")
async def interview_respond(request: Request):
    creator_id = await require_auth(request)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    session_id = body.get("session_id") or ""
    answer = body.get("answer") or ""

    if not session_id or not answer:
        return JSONResponse({"error": True, "message": "session_id and answer are required"}, status_code=400)

    session = db_one("SELECT * FROM interview_sessions WHERE id = ? AND creator_id = ?", (session_id, creator_id))
    if not session:
        return JSONResponse({"error": True, "message": "Interview session not found"}, status_code=404)
    if session["status"] == "completed":
        return JSONResponse({"error": True, "message": "This interview session is already completed."}, status_code=400)

    creator = db_one("SELECT display_name, settings FROM creators WHERE id = ?", (creator_id,))
    if not creator:
        return JSONResponse({"error": True, "message": "Creator not found"}, status_code=404)

    n = now_ts()
    transcript = json.loads(session["transcript"] or "[]")
    exchange_count = (session["exchange_count"] or 0) + 1
    transcript.append({"role": "creator", "text": answer.strip(), "timestamp": n})

    wrap_phrases = ["wrap it up", "wrap up", "that's enough", "i'm done", "done", "stop", "generate now", "make the post"]
    wants_to_wrap = any(p in answer.lower() for p in wrap_phrases)

    if wants_to_wrap or exchange_count >= 8:
        transcript.append({"role": "interviewer", "text": "Great, I have everything I need. Use 'Generate from Interview' to turn this into a post.", "timestamp": n})
        db_run(
            "UPDATE interview_sessions SET transcript = ?, exchange_count = ?, status = 'completed', updated_at = ? WHERE id = ?",
            (json.dumps(transcript), exchange_count, n, session_id),
        )
        return JSONResponse({"session_id": session_id, "status": "completed", "message": "Interview complete. Ready to generate content.", "exchange_count": exchange_count, "ready_to_generate": True})

    transcript_context = "\n\n".join(
        f"{'Interviewer' if t['role'] == 'interviewer' else creator['display_name']}: {t['text']}"
        for t in transcript
    )

    system_prompt = f"""You are an expert content interviewer helping {creator['display_name']} discover compelling content ideas.
Ask ONE specific follow-up question based on what they just said. Dig deeper into details, emotions, or specific examples.
Never repeat a question already asked. Make each question build on the previous answer."""

    user_prompt = f"""Interview transcript so far:
{transcript_context}

Ask ONE follow-up question to dig deeper. Be specific and curious.
Return ONLY the question, nothing else."""

    try:
        follow_up = await call_claude(system_prompt, user_prompt, 256)
    except Exception as e:
        logger.error(f"Interview respond error: {e}")
        return JSONResponse({"error": True, "message": "Interview follow-up failed. Please try again."}, status_code=502)

    transcript.append({"role": "interviewer", "text": follow_up.strip(), "timestamp": n})
    db_run(
        "UPDATE interview_sessions SET transcript = ?, exchange_count = ?, updated_at = ? WHERE id = ?",
        (json.dumps(transcript), exchange_count, n, session_id),
    )

    return JSONResponse({"session_id": session_id, "question": follow_up.strip(), "exchange_count": exchange_count, "ready_to_generate": False})


@app.post("/api/creator/interview/generate")
async def interview_generate(request: Request):
    creator_id = await require_auth(request)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    session_id = body.get("session_id") or ""
    platform = body.get("platform") or "linkedin"

    if not session_id:
        return JSONResponse({"error": True, "message": "session_id is required"}, status_code=400)

    session = db_one("SELECT * FROM interview_sessions WHERE id = ? AND creator_id = ?", (session_id, creator_id))
    if not session:
        return JSONResponse({"error": True, "message": "Interview session not found"}, status_code=404)

    creator = db_one("SELECT display_name, settings FROM creators WHERE id = ?", (creator_id,))
    if not creator:
        return JSONResponse({"error": True, "message": "Creator not found"}, status_code=404)

    settings = json.loads(creator["settings"] or "{}")
    safe_platform = platform if platform in ("linkedin", "instagram", "twitter", "bluesky", "email") else "linkedin"

    transcript = json.loads(session["transcript"] or "[]")
    if len(transcript) < 2:
        return JSONResponse({"error": True, "message": "Interview transcript is too short to generate content"}, status_code=400)

    transcript_text = "\n\n".join(
        f"{'Q' if t['role'] == 'interviewer' else 'A'}: {t['text']}"
        for t in transcript
        if not (t["role"] == "interviewer" and "Great, I have everything" in t["text"])
    )

    history_rows = db_all(
        "SELECT content_text FROM creator_content_history WHERE creator_id = ? ORDER BY ingested_at DESC LIMIT 5",
        (creator_id,),
    )
    samples = "\n\n---\n\n".join(r["content_text"] for r in history_rows)
    voice_ctx = build_voice_context(settings, samples)

    system_prompt = f"""You are a content ghostwriter for {creator['display_name']}. Your job is to write in their exact voice.

{voice_ctx}

RULES:
- Write ONLY the finished post — no intro, no explanation, no "here's your post"
- Draw directly from what they shared in the interview
- Use their actual words, phrases, and examples where possible
- Do NOT add generic filler — only what came from the interview
- {PLATFORM_GUIDES[safe_platform]}"""

    user_prompt = f"""Turn this interview transcript into a polished {safe_platform} post.

INTERVIEW TRANSCRIPT:
{transcript_text}

Write the post now."""

    try:
        generated_text = await call_claude(system_prompt, user_prompt, 1024)
    except Exception as e:
        logger.error(f"Interview generate error: {e}")
        return JSONResponse({"error": True, "message": "Content generation from interview failed. Please try again."}, status_code=502)

    n = now_ts()
    draft_id = new_id()

    db_run(
        "INSERT INTO generated_content (id, creator_id, platform, content_text, topic, status, generation_mode, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'draft', 'interview_mode', ?, ?)",
        (draft_id, creator_id, safe_platform, generated_text, f"Interview Session {session_id[:8]}", n, n),
    )
    db_run("UPDATE interview_sessions SET generated_content_id = ?, updated_at = ? WHERE id = ?", (draft_id, n, session_id))

    return JSONResponse({"content": generated_text, "platform": safe_platform, "draft_id": draft_id, "session_id": session_id})


@app.get("/api/creator/content/drafts")
async def list_drafts(request: Request):
    creator_id = await require_auth(request)
    rows = db_all(
        "SELECT id, platform, content_text, topic, status, generation_mode, creator_rating, notes, created_at FROM generated_content WHERE creator_id = ? ORDER BY created_at DESC",
        (creator_id,),
    )
    return JSONResponse({"drafts": rows})


@app.put("/api/creator/content/drafts/{draft_id}")
async def update_draft(draft_id: str, request: Request):
    creator_id = await require_auth(request)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    draft = db_one("SELECT id FROM generated_content WHERE id = ? AND creator_id = ?", (draft_id, creator_id))
    if not draft:
        return JSONResponse({"error": True, "message": "Draft not found"}, status_code=404)

    status = body.get("status")
    rating = body.get("rating")
    notes = body.get("notes")

    valid_statuses = ["draft", "approved", "rejected", "published"]
    updates = []
    values = []
    n = now_ts()

    if status and status in valid_statuses:
        updates.append("status = ?")
        values.append(status)
    if rating is not None:
        safe_rating = max(1, min(5, int(rating)))
        updates.append("creator_rating = ?")
        values.append(safe_rating)
    if notes is not None:
        updates.append("notes = ?")
        values.append(notes)

    if not updates:
        return JSONResponse({"error": True, "message": "No valid fields to update."}, status_code=400)

    updates.append("updated_at = ?")
    values.extend([n, draft_id, creator_id])

    db_run(f"UPDATE generated_content SET {', '.join(updates)} WHERE id = ? AND creator_id = ?", tuple(values))

    updated = db_one(
        "SELECT id, platform, content_text, topic, status, generation_mode, creator_rating, notes, created_at, updated_at FROM generated_content WHERE id = ?",
        (draft_id,),
    )
    return JSONResponse({"draft": updated})


@app.post("/api/creator/content/check-overlap")
async def check_overlap(request: Request):
    creator_id = await require_auth(request)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    topic = body.get("topic") or ""
    if not topic:
        return JSONResponse({"error": True, "message": "topic is required"}, status_code=400)

    keywords = extract_keywords(topic)
    if not keywords:
        return JSONResponse({"has_overlap": False, "similar_topics": [], "suggestion": None})

    drafts = db_all(
        "SELECT id, topic, platform, created_at, status FROM generated_content WHERE creator_id = ? ORDER BY created_at DESC LIMIT 50",
        (creator_id,),
    )
    history = db_all(
        "SELECT content_text, platform, ingested_at FROM creator_content_history WHERE creator_id = ? ORDER BY ingested_at DESC LIMIT 50",
        (creator_id,),
    )

    similar = []
    min_match = min(2, len(keywords))

    for d in drafts:
        if not d.get("topic"):
            continue
        match_count = sum(1 for kw in keywords if kw in d["topic"].lower())
        if match_count >= min_match:
            date = datetime.fromtimestamp(d["created_at"]).strftime("%b %-d, %Y")
            similar.append({"source": "draft", "topic": d["topic"], "platform": d["platform"], "date": date, "status": d["status"]})

    for item in history:
        if not item.get("content_text"):
            continue
        content_lower = item["content_text"].lower()[:300]
        match_count = sum(1 for kw in keywords if kw in content_lower)
        if match_count >= min_match:
            date = datetime.fromtimestamp(item.get("ingested_at") or 0).strftime("%b %-d, %Y")
            snippet = item["content_text"][:80].strip() + "..."
            similar.append({"source": "history", "topic": snippet, "platform": item["platform"], "date": date, "status": "published"})

    deduped = similar[:5]
    has_overlap = bool(deduped)
    suggestion = None
    if has_overlap:
        first = deduped[0]
        suggestion = f"You already covered \"{first['topic']}\" on {first['date']} ({first['platform']}). Consider a fresh angle or related sub-topic."

    return JSONResponse({"has_overlap": has_overlap, "similar_topics": deduped, "suggestion": suggestion})


@app.get("/api/creator/stats")
async def stats(request: Request):
    creator_id = await require_auth(request)

    kb_count = db_one("SELECT COUNT(*) as count FROM knowledge_base_files WHERE creator_id = ? AND status = 'active'", (creator_id,))
    history_count = db_one("SELECT COUNT(*) as count FROM creator_content_history WHERE creator_id = ?", (creator_id,))
    drafts_stats = db_one("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'draft' THEN 1 ELSE 0 END) as pending FROM generated_content WHERE creator_id = ?", (creator_id,))
    interview_count = db_one("SELECT COUNT(*) as count FROM interview_sessions WHERE creator_id = ?", (creator_id,))

    kb_files = kb_count["count"] if kb_count else 0
    content_history = history_count["count"] if history_count else 0
    drafts_total = drafts_stats["total"] if drafts_stats else 0
    drafts_pending = drafts_stats["pending"] if drafts_stats else 0
    interview_sessions = interview_count["count"] if interview_count else 0
    intelligence_score = content_history + kb_files + drafts_total + interview_sessions

    return JSONResponse({
        "kb_files": kb_files,
        "content_history": content_history,
        "drafts_total": drafts_total,
        "drafts_pending": drafts_pending,
        "interview_sessions": interview_sessions,
        "intelligence_score": intelligence_score,
    })


@app.get("/api/creator/analytics")
async def analytics(request: Request):
    creator_id = await require_auth(request)
    n = now_ts()
    thirty_days_ago = n - 60 * 60 * 24 * 30

    total_fans = db_one("SELECT COUNT(*) as count FROM fans WHERE creator_id = ?", (creator_id,))
    total_convos = db_one("SELECT COUNT(*) as count FROM fan_conversations WHERE creator_id = ?", (creator_id,))
    total_leads = db_one("SELECT COUNT(*) as count FROM leads WHERE creator_id = ?", (creator_id,))
    total_content = db_one("SELECT COUNT(*) as count FROM generated_content WHERE creator_id = ?", (creator_id,))
    avg_rating = db_one("SELECT AVG(creator_rating) as avg FROM generated_content WHERE creator_id = ? AND creator_rating IS NOT NULL", (creator_id,))

    recent_convos = db_all(
        """SELECT fc.id, fc.created_at, fc.message_count, fc.lead_captured,
                  f.first_name, f.email,
                  (SELECT content FROM fan_messages WHERE conversation_id = fc.id AND role = 'fan' ORDER BY created_at ASC LIMIT 1) as first_message
           FROM fan_conversations fc
           LEFT JOIN fans f ON fc.fan_id = f.id
           WHERE fc.creator_id = ?
           ORDER BY fc.created_at DESC LIMIT 10""",
        (creator_id,),
    )
    recent_leads = db_all(
        "SELECT id, email, first_name, source, created_at FROM leads WHERE creator_id = ? ORDER BY created_at DESC LIMIT 5",
        (creator_id,),
    )
    content_by_platform = db_all(
        "SELECT platform, COUNT(*) as count FROM generated_content WHERE creator_id = ? GROUP BY platform ORDER BY count DESC",
        (creator_id,),
    )
    daily_convos = db_all(
        "SELECT date(created_at, 'unixepoch') as day, COUNT(*) as count FROM fan_conversations WHERE creator_id = ? AND created_at >= ? GROUP BY day ORDER BY day ASC",
        (creator_id, thirty_days_ago),
    )
    top_messages = db_all(
        "SELECT content FROM fan_messages WHERE role = 'fan' AND conversation_id IN (SELECT id FROM fan_conversations WHERE creator_id = ?) ORDER BY created_at DESC LIMIT 100",
        (creator_id,),
    )

    # Build 30-day chart data
    day_labels = []
    day_counts = {}
    for i in range(29, -1, -1):
        d = datetime.fromtimestamp(n - i * 86400).strftime("%Y-%m-%d")
        day_labels.append(d)
        day_counts[d] = 0
    for row in daily_convos:
        if row["day"] in day_counts:
            day_counts[row["day"]] = row["count"]
    daily_data = [{"day": d, "count": day_counts[d]} for d in day_labels]

    # Top topics
    word_freq: dict = {}
    for row in top_messages:
        words = re.sub(r"[^a-z0-9\s]", " ", (row["content"] or "").lower()).split()
        for w in words:
            if len(w) >= 4 and w not in STOP_WORDS:
                word_freq[w] = word_freq.get(w, 0) + 1
    top_topics = sorted(word_freq.items(), key=lambda x: -x[1])[:8]
    top_topics = [{"word": w, "count": c} for w, c in top_topics]

    tc = total_convos["count"] if total_convos else 0
    tl = total_leads["count"] if total_leads else 0
    lead_capture_rate = round((tl / tc) * 100) if tc > 0 else 0

    return JSONResponse({
        "stats": {
            "total_fans": total_fans["count"] if total_fans else 0,
            "total_conversations": tc,
            "leads_captured": tl,
            "content_generated": total_content["count"] if total_content else 0,
            "avg_rating": round(avg_rating["avg"] * 10) / 10 if avg_rating and avg_rating["avg"] else None,
            "lead_capture_rate": lead_capture_rate,
        },
        "daily_conversations": daily_data,
        "content_by_platform": content_by_platform,
        "top_topics": top_topics,
        "recent_conversations": [
            {
                "id": c["id"],
                "fan_name": c.get("first_name") or c.get("email") or "Anonymous Fan",
                "topic": (c.get("first_message") or "")[:80] or "No message",
                "message_count": c.get("message_count") or 0,
                "lead_captured": bool(c.get("lead_captured")),
                "created_at": c["created_at"],
            }
            for c in recent_convos
        ],
        "recent_leads": [
            {"id": l["id"], "email": l["email"], "name": l.get("first_name"), "source": l.get("source") or "chat", "created_at": l["created_at"]}
            for l in recent_leads
        ],
    })


# ── Products ───────────────────────────────────────────────────────────────────

@app.get("/api/creator/products")
async def list_products(request: Request):
    creator_id = await require_auth(request)
    rows = db_all(
        "SELECT id, name, description, price, url, status, display_order, created_at FROM creator_products WHERE creator_id = ? ORDER BY display_order ASC",
        (creator_id,),
    )
    return JSONResponse({"products": rows})


@app.post("/api/creator/products")
async def create_product(request: Request):
    creator_id = await require_auth(request)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    name = (body.get("name") or "").strip()
    if not name:
        return JSONResponse({"error": True, "message": "name is required"}, status_code=400)

    url = body.get("url") or None
    if url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return JSONResponse({"error": True, "message": "Product URL must be http:// or https://"}, status_code=400)
        except Exception:
            return JSONResponse({"error": True, "message": "Product URL must be a valid URL"}, status_code=400)

    n = now_ts()
    product_id = new_id()
    max_order = db_one("SELECT MAX(display_order) as max_order FROM creator_products WHERE creator_id = ?", (creator_id,))
    display_order = (max_order["max_order"] or 0) + 1

    db_run(
        "INSERT INTO creator_products (id, creator_id, name, description, price, url, status, display_order, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)",
        (product_id, creator_id, name, body.get("description") or None, body.get("price") or None, url, display_order, n, n),
    )

    product = db_one("SELECT id, name, description, price, url, status, display_order, created_at FROM creator_products WHERE id = ?", (product_id,))
    return JSONResponse({"product": product}, status_code=201)


@app.delete("/api/creator/products/{product_id}")
async def delete_product(product_id: str, request: Request):
    creator_id = await require_auth(request)
    p = db_one("SELECT id FROM creator_products WHERE id = ? AND creator_id = ?", (product_id, creator_id))
    if not p:
        return JSONResponse({"error": True, "message": "Product not found"}, status_code=404)
    db_run("DELETE FROM creator_products WHERE id = ? AND creator_id = ?", (product_id, creator_id))
    return JSONResponse({"deleted": True, "id": product_id})


# ── Fan public endpoints ───────────────────────────────────────────────────────

@app.get("/api/fan/creator/{handle}")
async def fan_creator_profile(handle: str):
    creator = db_one("SELECT id, display_name, settings FROM creators WHERE handle = ?", (handle.lower(),))
    if not creator:
        return JSONResponse({"error": True, "message": "Creator not found"}, status_code=404)
    settings = json.loads(creator["settings"] or "{}")
    return JSONResponse({
        "display_name": creator["display_name"],
        "welcome_message": settings.get("welcome_message") or f"Hi! I'm {creator['display_name']}'s AI assistant. Ask me anything!",
        "accent_color": settings.get("accent_color") or "#6366f1",
        "bg_color": settings.get("bg_color") or "#0f0f13",
        "avatar_url": settings.get("avatar_url") or None,
    })


@app.post("/api/fan/chat")
async def fan_chat(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    handle = (body.get("handle") or "").lower().strip()
    fan_id = body.get("fan_id") or ""
    conversation_id = body.get("conversation_id") or ""
    message = (body.get("message") or "").strip()
    fingerprint = body.get("fingerprint") or None

    if not handle:
        return JSONResponse({"error": True, "message": "handle is required"}, status_code=400)
    if not message:
        return JSONResponse({"error": True, "message": "message is required"}, status_code=400)
    if len(message) > 2000:
        return JSONResponse({"error": True, "message": "Message too long (max 2000 characters)"}, status_code=400)

    fan_ip = request.headers.get("CF-Connecting-IP") or request.client.host or "unknown"
    if not check_rate_limit(f"fanchat:{fan_ip}", 20, 60):
        return JSONResponse({"error": True, "message": "Too many messages. Please slow down."}, status_code=429)

    creator = db_one("SELECT id, display_name, settings FROM creators WHERE handle = ?", (handle,))
    if not creator:
        return JSONResponse({"error": True, "message": "Creator not found"}, status_code=404)

    settings = json.loads(creator["settings"] or "{}")
    n = now_ts()

    # Fan lookup/creation
    fan_record = None
    if fan_id:
        fan_record = db_one("SELECT * FROM fans WHERE id = ? AND creator_id = ?", (fan_id, creator["id"]))
    if not fan_record:
        new_fan_id = new_id()
        db_run(
            "INSERT INTO fans (id, creator_id, fingerprint, first_seen_at, last_seen_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (new_fan_id, creator["id"], fingerprint, n, n, n, n),
        )
        fan_record = db_one("SELECT * FROM fans WHERE id = ?", (new_fan_id,))
    else:
        db_run("UPDATE fans SET last_seen_at = ?, updated_at = ? WHERE id = ?", (n, n, fan_record["id"]))

    # Conversation lookup/creation
    convo = None
    if conversation_id:
        convo = db_one("SELECT * FROM fan_conversations WHERE id = ? AND fan_id = ?", (conversation_id, fan_record["id"]))
    if not convo:
        new_convo_id = new_id()
        db_run(
            "INSERT INTO fan_conversations (id, creator_id, fan_id, message_count, lead_captured, created_at, updated_at) VALUES (?, ?, ?, 0, 0, ?, ?)",
            (new_convo_id, creator["id"], fan_record["id"], n, n),
        )
        convo = db_one("SELECT * FROM fan_conversations WHERE id = ?", (new_convo_id,))

    # Insert fan message
    fan_msg_id = new_id()
    db_run(
        "INSERT INTO fan_messages (id, conversation_id, role, content, created_at) VALUES (?, ?, 'fan', ?, ?)",
        (fan_msg_id, convo["id"], message, n),
    )

    new_message_count = (convo["message_count"] or 0) + 1
    db_run("UPDATE fan_conversations SET message_count = ?, updated_at = ? WHERE id = ?", (new_message_count, n, convo["id"]))

    # KB context
    kb_files = db_all("SELECT id, filename, tag FROM knowledge_base_files WHERE creator_id = ? AND status = 'active'", (creator["id"],))
    keywords = extract_keywords(message)
    matching_kb = [f for f in kb_files if any(kw in ((f["filename"] or "") + " " + (f["tag"] or "")).lower() for kw in keywords)]
    kb_context = "\n".join(f"- {f['filename']} [{f['tag'] or 'general'}]" for f in kb_files) if kb_files else "No knowledge base files uploaded yet."
    matched_kb_names = [f["filename"] for f in matching_kb]

    # Products context
    products = db_all("SELECT name, description, price, url FROM creator_products WHERE creator_id = ? AND status = 'active' ORDER BY display_order ASC", (creator["id"],))
    products_context = "\n".join(
        f"- {p['name']}: {p['description'] or ''} — {'$' + str(p['price']) if p['price'] else 'Contact for pricing'}{' | ' + p['url'] if p['url'] else ''}"
        for p in products
    ) if products else "No products listed yet."

    # Chat history (last 10)
    history_rows = db_all(
        "SELECT role, content FROM fan_messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 10",
        (convo["id"],),
    )
    history_rows.reverse()
    history_msgs = [m for m in history_rows if not (m["content"] == message and m["role"] == "fan")]

    system_prompt = f"""You are {creator['display_name']}'s AI assistant. You help fans by answering questions using {creator['display_name']}'s knowledge base and expertise.

PERSONALITY:
- Tone: {settings.get('tone', 'conversational')}
- Formality: {settings.get('formality', 'balanced')}
- Voice notes: {settings.get('voice_notes', 'None provided')}

KNOWLEDGE BASE (answer from these sources ONLY for factual questions):
{kb_context}

PRODUCTS (recommend naturally when relevant, never be pushy):
{products_context}

{f"FAN CONTEXT:\\n{fan_record['memory_summary']}" if fan_record.get('memory_summary') else ""}

RULES:
- Answer questions helpfully and accurately
- If you don't know something, say "I don't have that information — reach out to {creator['display_name']} directly"
- When a fan asks about pricing, courses, or services, reference the product catalog
- Be warm and conversational, matching the creator's personality
- Keep responses concise (2-3 paragraphs max)"""

    claude_messages = [
        *[{"role": "user" if m["role"] == "fan" else "assistant", "content": m["content"]} for m in history_msgs],
        {"role": "user", "content": message},
    ]

    try:
        ai_reply = await call_claude_messages(system_prompt, claude_messages, 512)
    except Exception as e:
        logger.error(f"Fan chat Claude error: {e}")
        return JSONResponse({"error": True, "message": "Chat service temporarily unavailable. Please try again."}, status_code=502)

    # Product recommendations
    purchase_keywords = {"price", "cost", "buy", "enroll", "sign up", "how much", "course", "program", "purchase", "join", "pricing", "subscription", "fee", "register"}
    msg_lower = message.lower()
    has_purchase_intent = any(kw in msg_lower for kw in purchase_keywords)
    recommended_products = []
    if has_purchase_intent and products:
        recommended_products = [p for p in products if any(kw in ((p["name"] or "") + " " + (p["description"] or "")).lower() for kw in keywords)]
        if not recommended_products:
            recommended_products = products

    lead_prompt = new_message_count >= 5 and not fan_record.get("email")

    # Insert AI response
    ai_msg_id = new_id()
    product_recommended = recommended_products[0]["name"] if recommended_products else None
    kb_sources_used = ", ".join(matched_kb_names) if matched_kb_names else None

    db_run(
        "INSERT INTO fan_messages (id, conversation_id, role, content, kb_sources_used, product_recommended, created_at) VALUES (?, ?, 'ai', ?, ?, ?, ?)",
        (ai_msg_id, convo["id"], ai_reply, kb_sources_used, product_recommended, n),
    )

    voice_url = f"/api/fan/tts/{ai_msg_id}" if (settings.get("voice_enabled") and ELEVENLABS_API_KEY) else None

    return JSONResponse({
        "reply": ai_reply,
        "voice_url": voice_url,
        "products": [{"name": p["name"], "description": p["description"], "price": p["price"], "url": p["url"]} for p in recommended_products],
        "conversation_id": convo["id"],
        "fan_id": fan_record["id"],
        "lead_prompt": lead_prompt,
        "message_count": new_message_count,
    })


@app.post("/api/fan/lead")
async def fan_lead(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": True, "message": "Invalid JSON"}, status_code=400)

    email = (body.get("email") or "").lower().strip()
    first_name = body.get("first_name") or None
    conversation_id = body.get("conversation_id") or ""
    fan_id = body.get("fan_id") or ""

    if not email:
        return JSONResponse({"error": True, "message": "email is required"}, status_code=400)
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return JSONResponse({"error": True, "message": "Invalid email address"}, status_code=400)
    if not fan_id or not conversation_id:
        return JSONResponse({"error": True, "message": "fan_id and conversation_id are required"}, status_code=400)

    convo = db_one("SELECT creator_id FROM fan_conversations WHERE id = ? AND fan_id = ?", (conversation_id, fan_id))
    if not convo:
        return JSONResponse({"error": True, "message": "Conversation not found"}, status_code=404)

    creator_id = convo["creator_id"]
    n = now_ts()

    existing = db_one("SELECT id FROM leads WHERE email = ? AND creator_id = ?", (email, creator_id))
    if existing:
        lead_id = existing["id"]
    else:
        lead_id = new_id()
        db_run(
            "INSERT INTO leads (id, creator_id, fan_id, email, first_name, source, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'chat', ?, ?)",
            (lead_id, creator_id, fan_id, email, first_name, n, n),
        )

    db_run("UPDATE fans SET email = ?, first_name = ?, updated_at = ? WHERE id = ?", (email, first_name, n, fan_id))
    db_run("UPDATE fan_conversations SET lead_captured = 1, updated_at = ? WHERE id = ?", (n, conversation_id))

    return JSONResponse({"ok": True, "lead_id": lead_id})


@app.get("/api/fan/tts/{msg_id}")
async def fan_tts(msg_id: str):
    msg = db_one("SELECT fm.content, fm.conversation_id FROM fan_messages fm WHERE fm.id = ? AND fm.role = 'ai'", (msg_id,))
    if not msg:
        return JSONResponse({"error": True, "message": "Message not found"}, status_code=404)

    convo = db_one("SELECT creator_id FROM fan_conversations WHERE id = ?", (msg["conversation_id"],))
    if not convo:
        return JSONResponse({"error": True, "message": "Conversation not found"}, status_code=404)

    creator = db_one("SELECT settings FROM creators WHERE id = ?", (convo["creator_id"],))
    settings = json.loads(creator["settings"] or "{}") if creator else {}
    voice_id = settings.get("elevenlabs_voice_id") or "RX0kjGhuL9AMRVJm2dG5"
    text = msg["content"][:4800]

    if not ELEVENLABS_API_KEY:
        return JSONResponse({"error": True, "message": "Voice not configured"}, status_code=503)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            tts_resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={"Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY},
                json={"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}},
            )
        if not tts_resp.is_success:
            return JSONResponse({"error": True, "message": "Voice generation unavailable"}, status_code=502)
        return Response(content=tts_resp.content, media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return JSONResponse({"error": True, "message": "Voice generation failed"}, status_code=502)


@app.get("/api/fan/paywall-status")
async def fan_paywall_status(request: Request):
    params = request.query_params
    handle = (params.get("handle") or "").lower().strip()
    fan_id = params.get("fan_id") or ""
    messages_used = int(params.get("messages_used") or "0")

    if not handle:
        return JSONResponse({"error": True, "message": "handle is required"}, status_code=400)

    creator = db_one("SELECT id, settings FROM creators WHERE handle = ?", (handle,))
    if not creator:
        return JSONResponse({"error": True, "message": "Creator not found"}, status_code=404)

    settings = json.loads(creator["settings"] or "{}")
    paywall_enabled = bool(settings.get("paywall_enabled"))
    free_limit = int(settings.get("paywall_free_limit") or 5)
    price = settings.get("paywall_price") or None
    message = settings.get("paywall_message") or None

    if not paywall_enabled:
        return JSONResponse({"enabled": False, "paywalled": False, "messages_used": messages_used, "limit": free_limit, "price": price, "message": None})

    paywalled = messages_used >= free_limit
    return JSONResponse({
        "enabled": True,
        "paywalled": paywalled,
        "messages_used": messages_used,
        "limit": free_limit,
        "price": price,
        "message": (message or f"Subscribe to keep chatting with this creator's AI") if paywalled else None,
    })


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "service": "creator-ai", "port": 8871})


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8871, reload=False)
