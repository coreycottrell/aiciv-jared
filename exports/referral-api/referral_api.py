#!/usr/bin/env python3
"""
PureBrain Referral API — Standalone FastAPI Service
Runs on Hetzner at /opt/referral-api/ on port 8099
Replaces Chy container dependency and CF D1 dependency.

Deploy: referral-api.purebrain.ai -> localhost:8099
"""

import os
import sys
import time
import hmac
import hashlib
import secrets
import smtplib
import logging
import sqlite3
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from contextlib import asynccontextmanager

import aiosqlite
import bcrypt
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# ── Configuration ───────────────────────────────────────────────────────────

DB_PATH = os.environ.get("REFERRAL_DB_PATH", "/opt/referral-api/referrals.db")
PORTAL_BEARER_TOKEN = os.environ.get("PORTAL_BEARER_TOKEN", "")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "purebrain@puremarketing.ai")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

# PayPal Payouts
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "")
PAYPAL_SECRET = os.environ.get("PAYPAL_SECRET", "")
PAYPAL_BASE_URL = os.environ.get("PAYPAL_BASE_URL", "https://api-m.paypal.com")
if os.environ.get("PAYPAL_USE_SANDBOX", "").lower() == "true":
    PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com"

# Telegram notification
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
TG_ADMIN_CHAT_ID = os.environ.get("TG_ADMIN_CHAT_ID", "548906264")

PAYOUT_MIN_AMOUNT = 25.0
PAYOUT_COOLDOWN_DAYS = 30

REFERRAL_CODE_PREFIX = "PB-"
REFERRAL_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
REFERRAL_CODE_LENGTH = 4
REFERRAL_COMMISSION_RATE = 0.05
SESSION_TTL_SECS = 86400 * 7  # 7 days
LOGIN_MAX_ATTEMPTS = 10
LOGIN_WINDOW_SECS = 900  # 15 minutes
TRACK_MAX_PER_WINDOW = 30
TRACK_WINDOW_SECS = 300  # 5 minutes
PASSWORD_RESET_EXPIRY = 3600  # 1 hour

ALLOWED_ORIGINS = [
    "https://purebrain.ai",
    "https://www.purebrain.ai",
    "https://purebrain-staging.pages.dev",
    "https://referral-api.purebrain.ai",
    "https://app.purebrain.ai",
    "https://surf.purebrain.ai",
    "https://portal.purebrain.ai",
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("referral-api")


# ── Database Setup ──────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS referrers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name     TEXT NOT NULL DEFAULT '',
    user_email    TEXT NOT NULL UNIQUE COLLATE NOCASE,
    referral_code TEXT NOT NULL UNIQUE COLLATE NOCASE,
    paypal_email  TEXT NOT NULL DEFAULT '',
    password_hash TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS referrals (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id  INTEGER NOT NULL REFERENCES referrers(id),
    referred_email TEXT NOT NULL DEFAULT '' COLLATE NOCASE,
    referred_name  TEXT NOT NULL DEFAULT '',
    status       TEXT NOT NULL DEFAULT 'pending',
    created_at   TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS referral_clicks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    referral_code TEXT NOT NULL COLLATE NOCASE,
    ip_hash      TEXT NOT NULL DEFAULT '',
    clicked_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rewards (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER NOT NULL REFERENCES referrers(id),
    referral_id INTEGER REFERENCES referrals(id),
    reward_type TEXT NOT NULL DEFAULT 'cash',
    reward_value REAL NOT NULL DEFAULT 0.0,
    issued_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS commission_payments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id     INTEGER NOT NULL REFERENCES referrers(id),
    referral_id     INTEGER NOT NULL REFERENCES referrals(id),
    payer_email     TEXT NOT NULL DEFAULT '' COLLATE NOCASE,
    order_id        TEXT NOT NULL DEFAULT '',
    payment_amount  REAL NOT NULL DEFAULT 0.0,
    commission_rate REAL NOT NULL DEFAULT 0.05,
    commission_value REAL NOT NULL DEFAULT 0.0,
    tier            TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admin_tokens (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    token      TEXT NOT NULL UNIQUE,
    email      TEXT NOT NULL DEFAULT '',
    name       TEXT NOT NULL DEFAULT '',
    role       TEXT NOT NULL DEFAULT 'viewer',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS affiliate_sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    token         TEXT NOT NULL UNIQUE,
    referral_code TEXT NOT NULL COLLATE NOCASE,
    expires_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rate_limits (
    key          TEXT PRIMARY KEY,
    count        INTEGER NOT NULL DEFAULT 0,
    window_start INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    token      TEXT NOT NULL UNIQUE,
    email      TEXT NOT NULL COLLATE NOCASE,
    expires_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS payout_requests (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id    TEXT NOT NULL UNIQUE,
    referral_code TEXT NOT NULL COLLATE NOCASE,
    paypal_email  TEXT NOT NULL DEFAULT '',
    amount        REAL NOT NULL DEFAULT 0.0,
    status        TEXT NOT NULL DEFAULT 'pending',
    created_at    TEXT NOT NULL,
    created_at_ts INTEGER NOT NULL DEFAULT 0,
    paid_at       TEXT,
    batch_id      TEXT DEFAULT '',
    notes         TEXT DEFAULT ''
);
"""


def init_db_sync():
    """Initialize database schema synchronously (called at startup)."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


async def get_db() -> aiosqlite.Connection:
    """Get an async database connection."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


# ── Password Hashing ───────────────────────────────────────────────────────

def hash_password_bcrypt(password: str) -> str:
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, stored_hash: str) -> tuple[bool, bool]:
    """
    Verify password against stored hash.
    Returns (is_valid, needs_migration).
    Supports: bcrypt ($2b$/$2a$), legacy SHA-256 (salt:hex), pbkdf2 format.
    """
    if not stored_hash:
        return False, False

    # bcrypt format
    if stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$"):
        try:
            valid = bcrypt.checkpw(password.encode(), stored_hash.encode())
            return valid, False  # Already bcrypt, no migration needed
        except Exception:
            return False, False

    # PBKDF2 format from CF Workers (pbkdf2:iterations:salt_hex:hash_hex)
    if stored_hash.startswith("pbkdf2:"):
        parts = stored_hash.split(":")
        if len(parts) != 4:
            return False, False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = parts[3]
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations, dklen=32)
        valid = dk.hex() == expected_hash
        return valid, valid  # Migrate from pbkdf2 to bcrypt

    # Legacy SHA-256 format: salt:hexdigest
    if ":" in stored_hash:
        idx = stored_hash.index(":")
        salt_val = stored_hash[:idx]
        expected_hex = stored_hash[idx + 1:]
        computed = hashlib.sha256(f"{salt_val}:{password}".encode()).hexdigest()
        valid = hmac.compare_digest(computed, expected_hex)
        return valid, valid  # Migrate to bcrypt

    return False, False


# ── Helpers ─────────────────────────────────────────────────────────────────

def generate_referral_code() -> str:
    """Generate a random referral code like PB-XXXX."""
    suffix = "".join(secrets.choice(REFERRAL_CODE_CHARS) for _ in range(REFERRAL_CODE_LENGTH))
    return f"{REFERRAL_CODE_PREFIX}{suffix}"


async def generate_unique_code(db: aiosqlite.Connection) -> str:
    """Generate a unique referral code."""
    for _ in range(50):
        code = generate_referral_code()
        async with db.execute(
            "SELECT id FROM referrers WHERE referral_code = ? COLLATE NOCASE", (code,)
        ) as cursor:
            if not await cursor.fetchone():
                return code
    raise RuntimeError("Could not generate unique referral code after 50 attempts")


def referral_link(code: str) -> str:
    return f"https://purebrain.ai/?ref={code}"


def hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def get_client_ip(request: Request) -> str:
    # Caddy forwards X-Forwarded-For
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


async def is_rate_limited(db: aiosqlite.Connection, key: str, max_per_window: int, window_secs: int) -> bool:
    now = int(time.time())
    async with db.execute("SELECT count, window_start FROM rate_limits WHERE key = ?", (key,)) as cursor:
        row = await cursor.fetchone()

    if not row:
        await db.execute(
            "INSERT OR REPLACE INTO rate_limits (key, count, window_start) VALUES (?, 1, ?)",
            (key, now),
        )
        await db.commit()
        return False

    if now - row["window_start"] > window_secs:
        await db.execute("UPDATE rate_limits SET count = 1, window_start = ? WHERE key = ?", (now, key))
        await db.commit()
        return False

    if row["count"] >= max_per_window:
        return True

    await db.execute("UPDATE rate_limits SET count = count + 1 WHERE key = ?", (key,))
    await db.commit()
    return False


async def verify_affiliate_session(db: aiosqlite.Connection, token: str) -> Optional[str]:
    if not token:
        return None
    async with db.execute(
        "SELECT referral_code, expires_at FROM affiliate_sessions WHERE token = ?", (token,)
    ) as cursor:
        row = await cursor.fetchone()
    if not row:
        return None
    now = int(time.time())
    if now > row["expires_at"]:
        await db.execute("DELETE FROM affiliate_sessions WHERE token = ?", (token,))
        await db.commit()
        return None
    return row["referral_code"]


async def create_affiliate_session(db: aiosqlite.Connection, referral_code: str) -> str:
    token = secrets.token_hex(32)
    now = int(time.time())
    expires_at = now + SESSION_TTL_SECS
    await db.execute(
        "INSERT INTO affiliate_sessions (token, referral_code, expires_at) VALUES (?, ?, ?)",
        (token, referral_code.upper(), expires_at),
    )
    await db.commit()
    return token


def check_portal_auth(request: Request) -> bool:
    if not PORTAL_BEARER_TOKEN:
        return False
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip() == PORTAL_BEARER_TOKEN
    return False


def get_session_token(request: Request, body: dict = None) -> str:
    if body and body.get("session_token"):
        return str(body["session_token"]).strip()
    return (
        request.headers.get("X-Affiliate-Session", "")
        or request.query_params.get("session", "")
    ).strip()


def send_reset_email(to_email: str, reset_url: str) -> bool:
    """Send password reset email via Gmail SMTP."""
    if not SMTP_PASSWORD:
        logger.error("SMTP_PASSWORD not configured, cannot send reset email")
        return False

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="background:#080a12;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:32px;">
<div style="max-width:500px;margin:0 auto;background:#0d1120;border:1px solid #1e2a40;border-radius:12px;padding:40px;">
  <div style="text-align:center;margin-bottom:24px;">
    <span style="font-size:22px;font-weight:700;">
      <span style="color:#2a93c1;">PUREBR</span><span style="color:#f1420b;">AI</span><span style="color:#2a93c1;">N</span>
    </span>
  </div>
  <h2 style="color:#fff;font-size:20px;margin:0 0 16px;">Reset Your Password</h2>
  <p style="color:#9ca3af;font-size:14px;line-height:1.6;margin:0 0 24px;">
    Click the button below to reset your affiliate dashboard password. This link expires in 1 hour.
  </p>
  <div style="text-align:center;margin:32px 0;">
    <a href="{reset_url}" style="display:inline-block;background:linear-gradient(135deg,#2a93c1,#1d6e99);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;box-shadow:0 4px 16px rgba(42,147,193,0.4);">
      Reset Password
    </a>
  </div>
  <p style="color:#6b7280;font-size:12px;text-align:center;">If you didn't request this, you can safely ignore this email.</p>
</div>
</body></html>"""

    text = f"Reset your PureBrain affiliate password:\n\n{reset_url}\n\nThis link expires in 1 hour."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset Your PureBrain Affiliate Password"
    msg["From"] = f"PureBrain <{SMTP_EMAIL}>"
    msg["To"] = to_email
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Reset email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send reset email to {to_email}: {e}")
        return False


# ── Lifespan ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_sync()
    logger.info("Referral API started on port 8099")
    yield
    logger.info("Referral API shutting down")


# ── FastAPI App ─────────────────────────────────────────────────────────────

app = FastAPI(title="PureBrain Referral API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Affiliate-Session", "X-Admin-Token"],
    max_age=86400,
)


# ── Request Models ──────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = ""
    email: str
    password: str = ""
    paypal_email: str = ""


class SessionRequest(BaseModel):
    referral_code: str = ""
    email: str = ""
    password: str


class TrackRequest(BaseModel):
    referral_code: str


class ForgotPasswordRequest(BaseModel):
    email: str = ""
    referral_code: str = ""


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class CompleteRequest(BaseModel):
    referral_code: str
    referred_email: str = ""
    referred_name: str = ""
    order_id: str = ""


class PaypalEmailRequest(BaseModel):
    email: str
    paypal_email: str
    password: str = ""
    session_token: str = ""


class PayoutRequestModel(BaseModel):
    paypal_email: str
    amount: float
    referral_code: str = ""
    session_token: str = ""


class AdminPayoutAction(BaseModel):
    request_id: str
    action: str  # "approve" or "reject"
    notes: str = ""
    admin_token: str = ""


# ── Health Check ────────────────────────────────────────────────────────────

@app.get("/")
async def health():
    return {"status": "ok", "service": "purebrain-referral-api", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# ── POST /api/referral/register ─────────────────────────────────────────────

@app.post("/api/referral/register")
async def register(body: RegisterRequest):
    email = body.email.strip().lower()
    name = body.name.strip()
    password = body.password.strip()
    paypal_email = body.paypal_email.strip()

    if not email or "@" not in email or "." not in email.split("@")[-1]:
        return JSONResponse({"error": "invalid email"}, status_code=400)

    # Auto-generate password if not provided or too short
    pw = password if password and len(password) >= 6 else secrets.token_urlsafe(16)
    pw_hash = hash_password_bcrypt(pw)

    db = await get_db()
    try:
        # Check existing
        async with db.execute(
            "SELECT id, referral_code FROM referrers WHERE user_email = ? COLLATE NOCASE", (email,)
        ) as cursor:
            existing = await cursor.fetchone()

        if existing:
            return JSONResponse({
                "ok": True,
                "referral_code": existing["referral_code"],
                "referral_link": referral_link(existing["referral_code"]),
                "existing": True,
                "message": "You are already registered. Here is your existing referral link.",
            })

        code = await generate_unique_code(db)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        await db.execute(
            "INSERT INTO referrers (user_name, user_email, referral_code, password_hash, paypal_email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, code, pw_hash, paypal_email, now),
        )
        await db.commit()

        return JSONResponse({
            "ok": True,
            "referral_code": code,
            "referral_link": referral_link(code),
            "existing": False,
            "message": "Registration successful!",
        })
    finally:
        await db.close()


# ── POST /api/referral/session ──────────────────────────────────────────────

@app.post("/api/referral/session")
async def session(body: SessionRequest, request: Request):
    code = body.referral_code.strip().upper()
    email = body.email.strip().lower()
    password = body.password.strip()

    if not password:
        return JSONResponse({"error": "password required"}, status_code=400)
    if not code and not email:
        return JSONResponse({"error": "referral_code or email required"}, status_code=400)

    db = await get_db()
    try:
        # Rate limit
        client_ip = get_client_ip(request)
        ip_h = hash_ip(client_ip)
        if await is_rate_limited(db, f"login:{ip_h}", LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECS):
            return JSONResponse({"error": "too many login attempts. Please wait 15 minutes."}, status_code=429)

        # Look up referrer
        if code:
            async with db.execute(
                "SELECT referral_code, password_hash FROM referrers WHERE referral_code = ? COLLATE NOCASE", (code,)
            ) as cursor:
                row = await cursor.fetchone()
        else:
            async with db.execute(
                "SELECT referral_code, password_hash FROM referrers WHERE user_email = ? COLLATE NOCASE", (email,)
            ) as cursor:
                row = await cursor.fetchone()

        if not row:
            return JSONResponse({"error": "account not found"}, status_code=404)

        stored_hash = row["password_hash"]
        ref_code = row["referral_code"]

        if not stored_hash:
            # First login — set password
            new_hash = hash_password_bcrypt(password)
            await db.execute(
                "UPDATE referrers SET password_hash = ? WHERE referral_code = ? COLLATE NOCASE",
                (new_hash, ref_code),
            )
            await db.commit()
            logger.info(f"[SECURITY] First-login password claim for affiliate code {ref_code}")
        else:
            valid, needs_migration = verify_password(password, stored_hash)
            if not valid:
                return JSONResponse({"error": "incorrect password"}, status_code=401)

            # Auto-migrate legacy hashes to bcrypt
            if needs_migration:
                migrated_hash = hash_password_bcrypt(password)
                await db.execute(
                    "UPDATE referrers SET password_hash = ? WHERE referral_code = ? COLLATE NOCASE",
                    (migrated_hash, ref_code),
                )
                await db.commit()
                logger.info(f"Migrated password hash to bcrypt for {ref_code}")

        # Create session
        session_token = await create_affiliate_session(db, ref_code)

        return JSONResponse({
            "ok": True,
            "session_token": session_token,
            "referral_code": ref_code,
            "expires_in": SESSION_TTL_SECS,
        })
    finally:
        await db.close()


# ── GET /api/referral/dashboard ─────────────────────────────────────────────

@app.get("/api/referral/dashboard")
async def dashboard(request: Request):
    """Proxy dashboard from source of truth, with session validation"""
    import httpx
    
    code = request.query_params.get("code", "").strip().upper()
    email = request.query_params.get("email", "").strip().lower()
    session_token = request.query_params.get("session", "").strip()
    
    # If no code/email, try to derive from session
    if not code and not email and session_token:
        try:
            async with aiosqlite.connect(str(DB_PATH)) as db2:
                cur2 = await db2.execute("SELECT referral_code FROM sessions WHERE token = ?", (session_token,))
                row2 = await cur2.fetchone()
                if row2:
                    code = row2[0]
        except:
            pass
    
    if not code and not email:
        return JSONResponse({"error": "missing code or email"}, status_code=400)
    
    # Validate session
    if session_token:
        try:
            async with aiosqlite.connect(str(DB_PATH)) as db2:
                cur2 = await db2.execute("SELECT referral_code FROM sessions WHERE token = ?", (session_token,))
                row2 = await cur2.fetchone()
                if row2 and code and row2[0] != code:
                    return JSONResponse({"error": "session mismatch"}, status_code=403)
        except:
            pass
    
    # Try full dashboard proxy from chy-jared (has all data including history)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"http://37.27.237.109:8113/api/referral/dashboard?code={code}",
                headers={"Authorization": "Bearer u5avgCe3SY_CRd31zKZKr1kymNLnRFVsRo9uEdukWBU"}
            )
            if r.status_code == 200:
                data = r.json()
                # Add local PayPal email if available
                try:
                    async with aiosqlite.connect(str(DB_PATH)) as db2:
                        cur2 = await db2.execute("SELECT paypal_email FROM referrers WHERE referral_code = ? COLLATE NOCASE", (code,))
                        row2 = await cur2.fetchone()
                        if row2 and row2[0]:
                            data["paypal_email"] = row2[0]
                except:
                    pass
                return JSONResponse(data)
    except:
        pass

    # Get real stats from leaderboard (public endpoint, has real counts)
    real_stats = {"completed": 0, "total_earned": 0.0}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("http://37.27.237.109:8113/api/referral/leaderboard?limit=50")
            if r.status_code == 200:
                for entry in r.json().get("leaderboard", []):
                    if entry.get("referral_code", "").upper() == code.upper():
                        real_stats["completed"] = entry.get("completed", 0)
                        real_stats["total_earned"] = entry.get("total_earned", 0.0)
                        break
    except:
        pass
    
    # Fallback: return basic data from local DB
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            lookup = code if code else email
            field = "referral_code" if code else "user_email"
            cur = await db.execute(f"SELECT user_name, user_email, referral_code, paypal_email FROM referrers WHERE {field} = ? COLLATE NOCASE", (lookup,))
            row = await cur.fetchone()
            if not row:
                return JSONResponse({"error": "referrer not found"}, status_code=404)
            return JSONResponse({
                "referral_code": row[2],
                "referral_link": f"https://purebrain.ai/?ref={row[2]}",
                "name": row[0],
                "email": row[1],
                "paypal_email": row[3] or "",
                "total_clicks": 0,
                "total_referrals": real_stats["completed"], "referrals": real_stats["completed"],
                "completed": real_stats["completed"], "completed_referrals": real_stats["completed"],
                "earnings": real_stats["total_earned"], "total_earned": real_stats["total_earned"],
                "pending_amount": 0.0,
                "history": [],
                "commission_rate": 0.05,
                "commission_rate_pct": "5.0%",
                "model": "recurring",
                "pending": 0,
                "completed": real_stats["completed"],
                "earnings": real_stats["total_earned"],
            })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/referral/track")
async def track(body: TrackRequest, request: Request):
    code = body.referral_code.strip().upper()
    if not code:
        return JSONResponse({"error": "missing referral_code"}, status_code=400)

    client_ip = get_client_ip(request)
    ip_h = hash_ip(client_ip)

    db = await get_db()
    try:
        if await is_rate_limited(db, f"track:{ip_h}", TRACK_MAX_PER_WINDOW, TRACK_WINDOW_SECS):
            return JSONResponse({"error": "rate limited"}, status_code=429)

        async with db.execute(
            "SELECT id FROM referrers WHERE referral_code = ? COLLATE NOCASE", (code,)
        ) as cursor:
            referrer = await cursor.fetchone()

        if not referrer:
            return JSONResponse({"error": "invalid referral code"}, status_code=404)

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        await db.execute(
            "INSERT INTO referral_clicks (referral_code, ip_hash, clicked_at) VALUES (?, ?, ?)",
            (code, ip_h, now),
        )
        await db.commit()

        return JSONResponse({"ok": True})
    finally:
        await db.close()


# ── POST /api/referral/forgot-password ──────────────────────────────────────

@app.post("/api/referral/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    email = body.email.strip().lower()
    code = body.referral_code.strip().upper() if hasattr(body, "referral_code") else ""
    success_msg = {"ok": True, "message": "If that account is registered, a reset link has been sent."}

    if not email and not code:
        return JSONResponse({"error": "email or referral code required"}, status_code=400)

    db = await get_db()
    try:
        row = None
        if code:
            async with db.execute(
                "SELECT referral_code, user_email FROM referrers WHERE referral_code = ? COLLATE NOCASE", (code,)
            ) as cursor:
                row = await cursor.fetchone()
            if row:
                email = row["user_email"]
        elif email and "@" in email:
            async with db.execute(
                "SELECT referral_code, user_email FROM referrers WHERE user_email = ? COLLATE NOCASE", (email,)
            ) as cursor:
                row = await cursor.fetchone()

        if not row:
            return JSONResponse(success_msg)

        # Check if account has a placeholder email (can't send reset to fake email)
        account_email = row["user_email"]
        if account_email.endswith("@affiliate.purebrain.ai"):
            return JSONResponse({
                "ok": True,
                "message": "Your account does not have an email on file. Please contact support@puremarketing.ai or log in using your referral code and the password you set when you first logged in. If this is your first login, enter any password to set it."
            })

        # Generate token
        token = secrets.token_urlsafe(32)
        now = int(time.time())
        expires_at = now + PASSWORD_RESET_EXPIRY

        await db.execute(
            "INSERT INTO password_reset_tokens (token, email, expires_at) VALUES (?, ?, ?)",
            (token, email, expires_at),
        )
        # Clean expired tokens
        await db.execute("DELETE FROM password_reset_tokens WHERE expires_at < ?", (now,))
        await db.commit()

        reset_url = f"https://purebrain.ai/refer/?reset={token}"
        send_reset_email(email, reset_url)

        return JSONResponse(success_msg)
    finally:
        await db.close()


# ── POST /api/referral/reset-password ───────────────────────────────────────

@app.post("/api/referral/reset-password")
async def reset_password(body: ResetPasswordRequest):
    token = body.token.strip()
    new_password = body.password.strip()

    if not token:
        return JSONResponse({"error": "reset token required"}, status_code=400)
    if not new_password or len(new_password) < 6:
        return JSONResponse({"error": "password must be at least 6 characters"}, status_code=400)

    db = await get_db()
    try:
        async with db.execute(
            "SELECT email, expires_at FROM password_reset_tokens WHERE token = ?", (token,)
        ) as cursor:
            token_data = await cursor.fetchone()

        if not token_data:
            return JSONResponse(
                {"error": "invalid or expired reset link. Please request a new one."}, status_code=400
            )

        now = int(time.time())
        if now > token_data["expires_at"]:
            await db.execute("DELETE FROM password_reset_tokens WHERE token = ?", (token,))
            await db.commit()
            return JSONResponse(
                {"error": "reset link has expired. Please request a new one."}, status_code=400
            )

        email = token_data["email"]
        pw_hash = hash_password_bcrypt(new_password)

        await db.execute(
            "UPDATE referrers SET password_hash = ? WHERE user_email = ? COLLATE NOCASE",
            (pw_hash, email),
        )
        await db.execute("DELETE FROM password_reset_tokens WHERE token = ?", (token,))
        await db.commit()

        return JSONResponse({"ok": True, "message": "Password updated successfully. You can now log in."})
    finally:
        await db.close()


# ── GET /api/referral/leaderboard ───────────────────────────────────────────

@app.get("/api/referral/leaderboard")
async def leaderboard(request: Request):
    """Proxy leaderboard from source of truth at app.purebrain.ai"""
    import httpx
    limit = request.query_params.get("limit", "10")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"https://app.purebrain.ai/api/referral/leaderboard?limit={limit}")
            if r.status_code == 200:
                return JSONResponse(r.json())
    except:
        pass
    # Fallback to local DB if proxy fails
    try:
        limit_int = min(int(limit), 50)
    except:
        limit_int = 10
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cur = await db.execute(
            "SELECT user_name, referral_code FROM referrers LIMIT ?",
            (limit_int,)
        )
        rows = await cur.fetchall()
    leaders = [{"name": r[0], "referral_code": r[1], "completed": 0, "total_earned": 0.0} for r in rows]
    return JSONResponse({"leaderboard": leaders})


@app.post("/api/referral/complete")
async def complete(body: CompleteRequest):
    referral_code = body.referral_code.strip().upper()
    referred_email = body.referred_email.strip().lower()
    referred_name = body.referred_name.strip()
    order_id = body.order_id.strip()

    if not referral_code:
        return JSONResponse({"error": "missing referral_code"}, status_code=400)

    # referred_email is optional for subscription payments
    if not referred_email or "@" not in referred_email:
        if order_id:
            referred_email = f"paypal_{order_id.lower()}@pending"
        else:
            return JSONResponse({"error": "invalid referred_email"}, status_code=400)

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    db = await get_db()
    try:
        async with db.execute(
            "SELECT id FROM referrers WHERE referral_code = ? COLLATE NOCASE", (referral_code,)
        ) as cursor:
            referrer = await cursor.fetchone()

        if not referrer:
            return JSONResponse({"error": "invalid referral code"}, status_code=404)

        referrer_id = referrer["id"]

        # Single-referrer enforcement
        if "@pending" not in referred_email:
            await db.execute(
                "DELETE FROM referrals WHERE referred_email = ? COLLATE NOCASE AND referrer_id != ?",
                (referred_email, referrer_id),
            )

        # Check existing
        existing = None
        if "@pending" not in referred_email:
            async with db.execute(
                "SELECT id, status FROM referrals WHERE referrer_id = ? AND referred_email = ? COLLATE NOCASE",
                (referrer_id, referred_email),
            ) as cursor:
                existing = await cursor.fetchone()

        if existing:
            if existing["status"] == "completed":
                return JSONResponse({"ok": True, "message": "already completed"})
            await db.execute(
                "UPDATE referrals SET status = 'completed', completed_at = ?, referred_name = ? WHERE id = ?",
                (now, referred_name or "", existing["id"]),
            )
        else:
            await db.execute(
                "INSERT INTO referrals (referrer_id, referred_email, referred_name, status, created_at, completed_at) VALUES (?, ?, ?, 'completed', ?, ?)",
                (referrer_id, referred_email, referred_name, now, now),
            )

        await db.commit()
        logger.info(f"[referral] complete: {referral_code} -> {referred_email}")

        return JSONResponse({
            "ok": True,
            "message": "Referral recorded. You will earn 5% of every payment this member makes.",
        })
    finally:
        await db.close()


# ── POST /api/referral/paypal-email ─────────────────────────────────────────

@app.post("/api/referral/paypal-email")
async def paypal_email(body: PaypalEmailRequest, request: Request):
    email = body.email.strip().lower()
    paypal_email_val = body.paypal_email.strip().lower()
    password = body.password.strip()

    if not email or "@" not in email:
        return JSONResponse({"error": "invalid email"}, status_code=400)
    if not paypal_email_val or "@" not in paypal_email_val:
        return JSONResponse({"error": "invalid paypal_email"}, status_code=400)

    portal_authed = check_portal_auth(request)

    db = await get_db()
    try:
        if not portal_authed:
            session_token = get_session_token(request, body.model_dump())
            session_code = await verify_affiliate_session(db, session_token)

            if not session_code:
                # Fallback to password
                async with db.execute(
                    "SELECT password_hash FROM referrers WHERE user_email = ? COLLATE NOCASE", (email,)
                ) as cursor:
                    row = await cursor.fetchone()
                if not row:
                    return JSONResponse({"error": "referrer not found"}, status_code=404)
                if row["password_hash"]:
                    valid, _ = verify_password(password, row["password_hash"])
                    if not valid:
                        return JSONResponse({"error": "incorrect password or session required"}, status_code=401)

        # Update PayPal email
        async with db.execute(
            "UPDATE referrers SET paypal_email = ? WHERE user_email = ? COLLATE NOCASE",
            (paypal_email_val, email),
        ) as cursor:
            pass
        await db.commit()

        # Check if actually updated (changes = 0 means no row matched)
        async with db.execute(
            "SELECT id FROM referrers WHERE user_email = ? COLLATE NOCASE", (email,)
        ) as cursor:
            exists = await cursor.fetchone()

        if not exists:
            if portal_authed:
                # Auto-create referrer
                code = await generate_unique_code(db)
                now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                name = email.split("@")[0]
                random_pw = secrets.token_urlsafe(16)
                pw_hash = hash_password_bcrypt(random_pw)
                await db.execute(
                    "INSERT INTO referrers (user_name, user_email, referral_code, password_hash, paypal_email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, email, code, pw_hash, paypal_email_val, now),
                )
                await db.commit()
            else:
                return JSONResponse({"error": "referrer not found"}, status_code=404)

        return JSONResponse({"ok": True})
    finally:
        await db.close()


# ── POST /api/referral/payout-request ────────────────────────────────────────

@app.post("/api/referral/payout-request")
async def payout_request(body: PayoutRequestModel, request: Request):
    """User requests a payout of their earnings via PayPal."""
    paypal_email = body.paypal_email.strip().lower()
    amount = round(body.amount, 2)
    referral_code = body.referral_code.strip().upper()

    if not paypal_email or "@" not in paypal_email:
        return JSONResponse({"error": "valid PayPal email required"}, status_code=400)
    if amount < PAYOUT_MIN_AMOUNT:
        return JSONResponse({"error": f"minimum payout is ${PAYOUT_MIN_AMOUNT:.2f}"}, status_code=400)

    db = await get_db()
    try:
        # Auth: require session token
        session_token = get_session_token(request, body.model_dump())
        session_code = await verify_affiliate_session(db, session_token)

        if not session_code:
            portal_authed = check_portal_auth(request)
            if not portal_authed:
                return JSONResponse({"error": "authentication required"}, status_code=401)
            if not referral_code:
                return JSONResponse({"error": "referral_code required for portal auth"}, status_code=400)
            session_code = referral_code

        # Verify referral_code matches session if provided
        if referral_code and session_code.upper() != referral_code.upper():
            return JSONResponse({"error": "code mismatch"}, status_code=403)

        code = session_code.upper()

        # Look up referrer
        async with db.execute(
            "SELECT id, user_name, user_email FROM referrers WHERE referral_code = ? COLLATE NOCASE", (code,)
        ) as cursor:
            referrer = await cursor.fetchone()

        if not referrer:
            return JSONResponse({"error": "referrer not found"}, status_code=404)

        referrer_id = referrer["id"]

        # Check earnings
        async with db.execute(
            "SELECT COALESCE(SUM(reward_value), 0) as total FROM rewards WHERE referrer_id = ?", (referrer_id,)
        ) as cursor:
            earnings = float((await cursor.fetchone())["total"])

        # Subtract already-paid/pending payouts
        async with db.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM payout_requests WHERE referral_code = ? AND status IN ('pending', 'processing', 'paid')",
            (code,)
        ) as cursor:
            already_claimed = float((await cursor.fetchone())["total"])

        available = round(earnings - already_claimed, 2)
        if amount > available:
            return JSONResponse({"error": f"insufficient balance. Available: ${available:.2f}"}, status_code=400)

        # Cooldown check
        async with db.execute(
            "SELECT created_at_ts FROM payout_requests WHERE referral_code = ? AND status IN ('pending', 'processing') ORDER BY created_at_ts DESC LIMIT 1",
            (code,)
        ) as cursor:
            last_req = await cursor.fetchone()

        if last_req:
            days_since = (int(time.time()) - last_req["created_at_ts"]) / 86400
            if days_since < PAYOUT_COOLDOWN_DAYS:
                return JSONResponse({
                    "error": f"payout cooldown: you have a pending request. Next request available in {int(PAYOUT_COOLDOWN_DAYS - days_since)} days."
                }, status_code=400)

        # Create payout request
        now_ts = int(time.time())
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        request_id = f"payout-{code}-{now_ts}"

        await db.execute(
            "INSERT INTO payout_requests (request_id, referral_code, paypal_email, amount, status, created_at, created_at_ts) VALUES (?, ?, ?, ?, 'pending', ?, ?)",
            (request_id, code, paypal_email, amount, now_iso, now_ts)
        )
        await db.commit()

        # Send Telegram notification to admin
        _send_payout_notification(
            f"New Payout Request\n"
            f"Affiliate: {referrer['user_name']} ({code})\n"
            f"Amount: ${amount:.2f}\n"
            f"PayPal: {paypal_email}\n"
            f"Request ID: {request_id}\n"
            f"Available earnings: ${available:.2f}\n\n"
            f"Approve: POST /api/referral/admin/payout-action"
        )

        logger.info(f"[payout] Request created: {request_id} for {code} ${amount:.2f} -> {paypal_email}")

        return JSONResponse({
            "ok": True,
            "request_id": request_id,
            "amount": amount,
            "status": "pending",
            "message": "Payout request submitted. You will be notified when it is processed."
        })
    finally:
        await db.close()


# ── GET /api/referral/payout-history ────────────────────────────────────────

@app.get("/api/referral/payout-history")
async def payout_history(request: Request):
    """Get payout request history for a referral code."""
    code = (request.query_params.get("code") or request.query_params.get("referral_code") or "").strip().upper()

    if not code:
        return JSONResponse({"error": "missing referral_code"}, status_code=400)

    db = await get_db()
    try:
        # Auth check
        session_token = get_session_token(request)
        session_code = await verify_affiliate_session(db, session_token)

        if not session_code:
            portal_authed = check_portal_auth(request)
            if not portal_authed:
                return JSONResponse({"error": "authentication required"}, status_code=401)
            session_code = code

        if session_code.upper() != code.upper():
            return JSONResponse({"error": "session does not match requested code"}, status_code=403)

        async with db.execute(
            "SELECT request_id, paypal_email, amount, status, created_at, paid_at, notes FROM payout_requests WHERE referral_code = ? ORDER BY created_at_ts DESC",
            (code,)
        ) as cursor:
            rows = await cursor.fetchall()

        history = [
            {
                "request_id": row["request_id"],
                "paypal_email": row["paypal_email"],
                "amount": row["amount"],
                "status": row["status"],
                "created_at": row["created_at"],
                "paid_at": row["paid_at"],
                "notes": row["notes"] or "",
            }
            for row in rows
        ]

        return JSONResponse({"ok": True, "payouts": history, "requests": history})
    finally:
        await db.close()


# ── POST /api/referral/admin/payout-action ──────────────────────────────────

@app.post("/api/referral/admin/payout-action")
async def admin_payout_action(body: AdminPayoutAction, request: Request):
    """Admin approves or rejects a payout request. Approved payouts trigger PayPal Payouts API."""
    admin_token = body.admin_token or request.headers.get("X-Admin-Token", "")

    # Auth: require either portal bearer token or admin token
    if not check_portal_auth(request):
        if not admin_token:
            return JSONResponse({"error": "admin authentication required"}, status_code=401)
        db = await get_db()
        try:
            async with db.execute("SELECT role FROM admin_tokens WHERE token = ?", (admin_token,)) as cursor:
                admin_row = await cursor.fetchone()
            if not admin_row or admin_row["role"] not in ("admin", "owner"):
                return JSONResponse({"error": "insufficient admin privileges"}, status_code=403)
        finally:
            await db.close()

    request_id = body.request_id.strip()
    action = body.action.strip().lower()
    notes = body.notes.strip()

    if action not in ("approve", "reject"):
        return JSONResponse({"error": "action must be 'approve' or 'reject'"}, status_code=400)

    db = await get_db()
    try:
        async with db.execute(
            "SELECT * FROM payout_requests WHERE request_id = ?", (request_id,)
        ) as cursor:
            payout = await cursor.fetchone()

        if not payout:
            return JSONResponse({"error": "payout request not found"}, status_code=404)

        if payout["status"] != "pending":
            return JSONResponse({"error": f"payout is already {payout['status']}"}, status_code=400)

        if action == "reject":
            await db.execute(
                "UPDATE payout_requests SET status = 'rejected', notes = ? WHERE request_id = ?",
                (notes or "Rejected by admin", request_id)
            )
            await db.commit()
            logger.info(f"[payout] Rejected: {request_id}")
            return JSONResponse({"ok": True, "status": "rejected"})

        # Approve: attempt PayPal payout
        amount = payout["amount"]
        paypal_email = payout["paypal_email"]

        await db.execute(
            "UPDATE payout_requests SET status = 'processing' WHERE request_id = ?", (request_id,)
        )
        await db.commit()

        # Fire PayPal payout
        try:
            result = await _fire_paypal_payout(amount, paypal_email, request_id)
            now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            await db.execute(
                "UPDATE payout_requests SET status = 'paid', paid_at = ?, batch_id = ?, notes = ? WHERE request_id = ?",
                (now_iso, result.get("batch_id", ""), notes or f"PayPal batch: {result.get('batch_id', 'N/A')}", request_id)
            )
            await db.commit()

            _send_payout_notification(
                f"Payout SENT\n"
                f"Request: {request_id}\n"
                f"Amount: ${amount:.2f}\n"
                f"To: {paypal_email}\n"
                f"Batch ID: {result.get('batch_id', 'N/A')}"
            )

            logger.info(f"[payout] Approved and sent: {request_id} ${amount:.2f} -> {paypal_email}")
            return JSONResponse({"ok": True, "status": "paid", "batch_id": result.get("batch_id", "")})

        except Exception as e:
            await db.execute(
                "UPDATE payout_requests SET status = 'failed', notes = ? WHERE request_id = ?",
                (f"PayPal error: {str(e)[:200]}", request_id)
            )
            await db.commit()

            _send_payout_notification(f"Payout FAILED\nRequest: {request_id}\nError: {str(e)[:200]}")
            logger.error(f"[payout] Failed: {request_id} - {e}")

            return JSONResponse({"ok": False, "status": "failed", "error": str(e)[:200]}, status_code=500)
    finally:
        await db.close()


# ── PayPal Payouts API ──────────────────────────────────────────────────────

async def _fire_paypal_payout(amount: float, paypal_email: str, request_id: str) -> dict:
    """Fire a PayPal Payout. Returns dict with batch_id."""
    if not PAYPAL_CLIENT_ID or not PAYPAL_SECRET:
        raise ValueError("PayPal credentials not configured (PAYPAL_CLIENT_ID / PAYPAL_SECRET)")

    async with httpx.AsyncClient(timeout=30) as client:
        # Get access token
        token_resp = await client.post(
            f"{PAYPAL_BASE_URL}/v1/oauth2/token",
            auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
            data={"grant_type": "client_credentials"},
            headers={"Accept": "application/json"},
        )
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]

        # Create payout
        payout_resp = await client.post(
            f"{PAYPAL_BASE_URL}/v1/payments/payouts",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            json={
                "sender_batch_header": {
                    "sender_batch_id": request_id,
                    "email_subject": "PureBrain Affiliate Payout",
                    "email_message": "Your referral earnings payout from PureBrain."
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {"value": f"{amount:.2f}", "currency": "USD"},
                    "receiver": paypal_email,
                    "note": f"PureBrain affiliate payout: {request_id}",
                }]
            }
        )
        payout_resp.raise_for_status()
        data = payout_resp.json()
        batch_id = data.get("batch_header", {}).get("payout_batch_id", "UNKNOWN")
        return {"batch_id": batch_id, "status": data.get("batch_header", {}).get("batch_status", "UNKNOWN")}


def _send_payout_notification(message: str):
    """Send Telegram notification about payout events."""
    if not TG_BOT_TOKEN:
        # Try reading from config file
        try:
            import json as _json
            cfg_path = os.path.join(os.path.dirname(__file__), "telegram_config.json")
            if not os.path.exists(cfg_path):
                cfg_path = "/home/jared/projects/AI-CIV/aether/config/telegram_config.json"
            if os.path.exists(cfg_path):
                with open(cfg_path) as f:
                    cfg = _json.load(f)
                token = cfg.get("bot_token", "")
                if token:
                    import urllib.request
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    data = json.dumps({"chat_id": TG_ADMIN_CHAT_ID, "text": f"[Referral API] {message}"}).encode()
                    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                    urllib.request.urlopen(req, timeout=5)
                    return
        except Exception:
            pass
        logger.warning(f"[payout] No TG token — notification not sent: {message[:100]}")
        return

    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TG_ADMIN_CHAT_ID, "text": f"[Referral API] {message}"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        logger.error(f"[payout] TG notification failed: {e}")


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8099, log_level="info")
