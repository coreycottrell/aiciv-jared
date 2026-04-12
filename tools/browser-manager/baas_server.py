#!/usr/bin/env python3
"""
baas_server.py - Browser-as-a-Service (BaaS) REST API.

Exposes fingerprinted browser sessions over HTTP so any team member
(human or AI) can launch, control, and screenshot browser sessions
without local dependencies. Uses the existing ProfileManager and
fingerprint_gen from the browser-manager toolkit.

Usage:
    python baas_server.py                       # HTTP on 0.0.0.0:8901
    python baas_server.py --port 9000           # custom port
    python baas_server.py --ssl-cert cert.pem --ssl-key key.pem  # HTTPS

Endpoints:
    GET    /health                      — server health (no auth)
    POST   /sessions                    — create fingerprinted browser session
    GET    /sessions                    — list active sessions
    POST   /sessions/{id}/navigate      — goto URL
    POST   /sessions/{id}/click         — click selector
    POST   /sessions/{id}/type          — type text into selector
    POST   /sessions/{id}/screenshot    — capture PNG screenshot
    GET    /sessions/{id}/content       — get page HTML
    POST   /sessions/{id}/evaluate      — run JS on page
    DELETE /sessions/{id}               — close session
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent
KEYS_PATH = os.environ.get("BAAS_KEYS_PATH", str(BASE_DIR / "baas_keys.json"))
MAX_SESSIONS = 10
IDLE_TIMEOUT_SECONDS = 30 * 60  # 30 minutes
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "baas_server.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("baas")

# ---------------------------------------------------------------------------
# API Key Store
# ---------------------------------------------------------------------------


def load_api_keys() -> dict:
    """Load API keys from JSON config file."""
    try:
        with open(KEYS_PATH) as f:
            data = json.load(f)
        return data.get("keys", {})
    except FileNotFoundError:
        logger.error(f"API keys file not found: {KEYS_PATH}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in keys file: {KEYS_PATH}")
        return {}


API_KEYS = load_api_keys()

# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------


class CreateSessionRequest(BaseModel):
    proxy: Optional[str] = None
    timezone_id: Optional[str] = Field(None, alias="timezone")
    locale: Optional[str] = None


class NavigateRequest(BaseModel):
    url: str


class ClickRequest(BaseModel):
    selector: str
    timeout: Optional[int] = 5000


class TypeRequest(BaseModel):
    selector: str
    text: str
    timeout: Optional[int] = 5000


class EvaluateRequest(BaseModel):
    script: str


# ---------------------------------------------------------------------------
# Browser Session Manager
# ---------------------------------------------------------------------------


class BrowserSessionManager:
    """Manages active browser sessions with concurrency limits and idle tracking."""

    def __init__(self, max_sessions: int = MAX_SESSIONS):
        self.max_sessions = max_sessions
        self.sessions: dict = {}  # session_id -> session_info
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start_cleanup_loop(self):
        """Start the background idle-session cleanup task."""
        self._cleanup_task = asyncio.create_task(self._cleanup_idle_sessions())

    async def stop_cleanup_loop(self):
        """Stop the cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_idle_sessions(self):
        """Periodically close sessions that have been idle too long."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                now = time.time()
                to_close = []
                for sid, info in list(self.sessions.items()):
                    if now - info["last_activity"] > IDLE_TIMEOUT_SECONDS:
                        to_close.append(sid)
                for sid in to_close:
                    logger.info(f"Auto-closing idle session {sid} (user: {self.sessions[sid]['user']})")
                    await self.close_session(sid)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")

    def _launch_browser(self, profile_name: str, proxy: Optional[str] = None) -> tuple:
        """
        Launch a fingerprinted browser. Separated for easy mocking in tests.

        Returns (context, page) tuple.
        """
        from browser_manager import ProfileManager, launch_profile
        from fingerprint_gen import generate_fingerprint

        mgr = ProfileManager(profiles_dir=str(BASE_DIR / "profiles"))

        # Create a temporary profile for this session
        try:
            mgr.create_profile(
                name=profile_name,
                proxy=proxy,
            )
        except ValueError:
            # Profile already exists, delete and recreate
            mgr.delete_profile(profile_name)
            mgr.create_profile(
                name=profile_name,
                proxy=proxy,
            )

        context, page = launch_profile(
            name=profile_name,
            profiles_dir=str(BASE_DIR / "profiles"),
            headless=True,
        )
        return context, page

    async def create_session(
        self,
        user: str,
        proxy: Optional[str] = None,
        timezone_id: Optional[str] = None,
        locale: Optional[str] = None,
    ) -> dict:
        """Create a new browser session."""
        if len(self.sessions) >= self.max_sessions:
            raise HTTPException(
                status_code=429,
                detail=f"Maximum concurrent sessions ({self.max_sessions}) reached. Close an existing session first.",
            )

        session_id = str(uuid.uuid4())[:12]
        profile_name = f"baas-{session_id}"
        now = time.time()

        try:
            # Run browser launch in executor (it's sync/blocking)
            loop = asyncio.get_event_loop()
            context, page = await loop.run_in_executor(
                None, self._launch_browser, profile_name, proxy
            )
        except Exception as e:
            logger.error(f"Failed to launch browser for session {session_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Browser launch failed: {str(e)}")

        self.sessions[session_id] = {
            "session_id": session_id,
            "user": user,
            "profile_name": profile_name,
            "context": context,
            "page": page,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": now,
            "proxy": proxy,
        }

        logger.info(f"Session created: {session_id} (user: {user})")
        return {
            "session_id": session_id,
            "user": user,
            "created_at": self.sessions[session_id]["created_at"],
        }

    def get_session(self, session_id: str) -> dict:
        """Get session info, raising 404 if not found."""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
        return self.sessions[session_id]

    def touch(self, session_id: str):
        """Update last_activity timestamp."""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = time.time()

    async def close_session(self, session_id: str) -> dict:
        """Close a browser session and clean up."""
        session = self.get_session(session_id)
        try:
            context = session["context"]
            if hasattr(context, "close"):
                context.close()
        except Exception as e:
            logger.warning(f"Error closing browser context for {session_id}: {e}")

        # Clean up profile
        try:
            from browser_manager import ProfileManager
            mgr = ProfileManager(profiles_dir=str(BASE_DIR / "profiles"))
            mgr.delete_profile(session["profile_name"])
        except Exception:
            pass  # Best effort cleanup

        del self.sessions[session_id]
        logger.info(f"Session closed: {session_id}")
        return {"status": "closed", "session_id": session_id}

    def list_sessions(self) -> list:
        """List all active sessions (without internal objects)."""
        result = []
        for sid, info in self.sessions.items():
            result.append({
                "session_id": sid,
                "user": info["user"],
                "created_at": info["created_at"],
                "last_activity": datetime.fromtimestamp(
                    info["last_activity"], tz=timezone.utc
                ).isoformat(),
                "proxy": info.get("proxy"),
            })
        return result


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

session_manager = BrowserSessionManager(max_sessions=MAX_SESSIONS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    await session_manager.start_cleanup_loop()
    logger.info(f"BaaS server starting. Max sessions: {MAX_SESSIONS}. Keys loaded: {len(API_KEYS)}")
    yield
    await session_manager.stop_cleanup_loop()
    # Close all remaining sessions
    for sid in list(session_manager.sessions.keys()):
        try:
            await session_manager.close_session(sid)
        except Exception:
            pass
    logger.info("BaaS server shut down.")


app = FastAPI(
    title="Browser-as-a-Service (BaaS)",
    description="REST API for fingerprinted browser sessions. Launch, control, and screenshot browsers over HTTP.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------


async def verify_api_key(request: Request) -> dict:
    """Verify X-API-Key header and return user info."""
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    user_info = API_KEYS[api_key]
    # Log the request
    logger.info(
        f"API call: {request.method} {request.url.path} "
        f"(user: {user_info['user']}, role: {user_info['role']})"
    )
    return user_info


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    """Server health check (no auth required)."""
    return {
        "status": "healthy",
        "active_sessions": len(session_manager.sessions),
        "max_sessions": session_manager.max_sessions,
        "uptime_keys_loaded": len(API_KEYS),
    }


@app.get("/sessions")
async def list_sessions(user_info: dict = Depends(verify_api_key)):
    """List all active browser sessions."""
    return {"sessions": session_manager.list_sessions()}


@app.post("/sessions", status_code=201)
async def create_session(
    body: Optional[CreateSessionRequest] = None,
    user_info: dict = Depends(verify_api_key),
):
    """Create a new fingerprinted browser session."""
    proxy = body.proxy if body else None
    tz = body.timezone_id if body else None
    locale = body.locale if body else None

    result = await session_manager.create_session(
        user=user_info["user"],
        proxy=proxy,
        timezone_id=tz,
        locale=locale,
    )
    return result


@app.post("/sessions/{session_id}/navigate")
async def navigate(
    session_id: str,
    body: NavigateRequest,
    user_info: dict = Depends(verify_api_key),
):
    """Navigate to a URL."""
    session = session_manager.get_session(session_id)
    page = session["page"]
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, page.goto, body.url)
        session_manager.touch(session_id)
        logger.info(f"Session {session_id}: navigated to {body.url}")
        return {"status": "navigated", "url": body.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Navigation failed: {str(e)}")


@app.post("/sessions/{session_id}/click")
async def click(
    session_id: str,
    body: ClickRequest,
    user_info: dict = Depends(verify_api_key),
):
    """Click an element by CSS selector."""
    session = session_manager.get_session(session_id)
    page = session["page"]
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, page.click, body.selector)
        session_manager.touch(session_id)
        logger.info(f"Session {session_id}: clicked {body.selector}")
        return {"status": "clicked", "selector": body.selector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Click failed: {str(e)}")


@app.post("/sessions/{session_id}/type")
async def type_text(
    session_id: str,
    body: TypeRequest,
    user_info: dict = Depends(verify_api_key),
):
    """Type text into an element by CSS selector."""
    session = session_manager.get_session(session_id)
    page = session["page"]
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, page.fill, body.selector, body.text)
        session_manager.touch(session_id)
        logger.info(f"Session {session_id}: typed into {body.selector}")
        return {"status": "typed", "selector": body.selector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Type failed: {str(e)}")


@app.post("/sessions/{session_id}/screenshot")
async def screenshot(
    session_id: str,
    user_info: dict = Depends(verify_api_key),
):
    """Take a screenshot, returns PNG image."""
    session = session_manager.get_session(session_id)
    page = session["page"]
    try:
        loop = asyncio.get_event_loop()
        image_bytes = await loop.run_in_executor(None, page.screenshot)
        session_manager.touch(session_id)
        logger.info(f"Session {session_id}: screenshot taken ({len(image_bytes)} bytes)")
        return Response(content=image_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot failed: {str(e)}")


@app.get("/sessions/{session_id}/content")
async def get_content(
    session_id: str,
    user_info: dict = Depends(verify_api_key),
):
    """Get the current page HTML content."""
    session = session_manager.get_session(session_id)
    page = session["page"]
    try:
        loop = asyncio.get_event_loop()
        html = await loop.run_in_executor(None, page.content)
        session_manager.touch(session_id)
        logger.info(f"Session {session_id}: content retrieved ({len(html)} chars)")
        return {"html": html}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content retrieval failed: {str(e)}")


@app.post("/sessions/{session_id}/evaluate")
async def evaluate(
    session_id: str,
    body: EvaluateRequest,
    user_info: dict = Depends(verify_api_key),
):
    """Run JavaScript on the page and return the result."""
    session = session_manager.get_session(session_id)
    page = session["page"]
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, page.evaluate, body.script)
        session_manager.touch(session_id)
        logger.info(f"Session {session_id}: JS evaluated")
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluate failed: {str(e)}")


@app.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user_info: dict = Depends(verify_api_key),
):
    """Close and clean up a browser session."""
    result = await session_manager.close_session(session_id)
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Browser-as-a-Service API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8901, help="Bind port (default: 8901)")
    parser.add_argument("--ssl-cert", default=None, help="SSL certificate file")
    parser.add_argument("--ssl-key", default=None, help="SSL key file")
    args = parser.parse_args()

    ssl_kwargs = {}
    if args.ssl_cert and args.ssl_key:
        ssl_kwargs["ssl_certfile"] = args.ssl_cert
        ssl_kwargs["ssl_keyfile"] = args.ssl_key
        logger.info(f"HTTPS enabled with cert: {args.ssl_cert}")

    logger.info(f"Starting BaaS server on {args.host}:{args.port}")
    uvicorn.run(
        "baas_server:app",
        host=args.host,
        port=args.port,
        log_level="info",
        **ssl_kwargs,
    )
