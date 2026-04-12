"""
Migration API — FastAPI Endpoints
===================================

Handles the server-side of the Migration Portal file upload and processing.

Endpoints:
    POST   /api/migration/upload              — Accept file upload, return job_id
    GET    /api/migration/status/:job_id      — Return processing status + partial results
    GET    /api/migration/profile/:user_id    — Return completed user_context_profile
    DELETE /api/migration/data/:user_id       — Delete all migration data (GDPR erasure)

Security:
    - Files stored in /tmp/purebrain-migration/<user_id>/
    - Auto-deleted after processing (TTL enforced by cleanup task)
    - Max file size: 50 MB (ZIP), 10 MB (CSV/JSON)
    - Allowed types: .zip, .json, .csv
    - Simple API key auth header (X-Migration-Key) — replace with JWT in production

Usage:
    uvicorn tools.migration.migration_api:app --host 0.0.0.0 --port 8001
    or import and mount on existing FastAPI/Flask app.

Dependencies:
    pip install fastapi uvicorn python-multipart
"""

import os
import uuid
import shutil
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Conditional FastAPI import (graceful failure if not installed)
# ---------------------------------------------------------------------------

try:
    from fastapi import FastAPI, UploadFile, File, HTTPException, Header, BackgroundTasks
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("FastAPI not installed. Install with: pip install fastapi uvicorn python-multipart")

# ---------------------------------------------------------------------------
# Local imports
# ---------------------------------------------------------------------------

from tools.migration.chatgpt_parser import parse_chatgpt_export
from tools.migration.claude_parser import parse_claude_export
from tools.migration.generic_parser import parse_generic_file, parse_generic_bytes
from tools.migration.pattern_extractor import extract_user_context_profile

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TEMP_DIR = Path("/tmp/purebrain-migration")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# In production: use a secrets vault, not env var directly
API_KEY = os.environ.get("MIGRATION_API_KEY", "dev-key-change-in-production")

MAX_ZIP_SIZE = 50 * 1024 * 1024   # 50 MB
MAX_CSV_SIZE = 10 * 1024 * 1024   # 10 MB
FILE_TTL_HOURS = 24

ALLOWED_EXTENSIONS = {".zip", ".json", ".csv"}

# In-memory job store (replace with Redis or DB in production)
_jobs: dict = {}       # job_id -> {status, user_id, created_at, result, error}
_profiles: dict = {}   # user_id -> user_context_profile


# ---------------------------------------------------------------------------
# FastAPI app setup
# ---------------------------------------------------------------------------

def _create_app():
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI is required. pip install fastapi uvicorn python-multipart")

    app = FastAPI(
        title="PureBrain Migration API",
        description="Parses AI tool exports and builds user context profiles",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://purebrain.ai", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["*"],
    )

    return app


if FASTAPI_AVAILABLE:
    app = _create_app()
else:
    app = None


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _verify_api_key(key: Optional[str]) -> bool:
    if not key:
        return False
    return hmac.compare_digest(key.encode(), API_KEY.encode())


def _require_auth(x_migration_key: Optional[str]):
    if not _verify_api_key(x_migration_key):
        raise HTTPException(status_code=401, detail="Invalid or missing X-Migration-Key header")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

if FASTAPI_AVAILABLE:

    @app.post("/api/migration/upload")
    async def upload_migration_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        source: str = "auto",
        user_id: str = "anonymous",
        custom_instructions: Optional[str] = None,
        x_migration_key: Optional[str] = Header(None),
    ):
        """
        Accept a file upload and start async processing.

        Args:
            file:                 The uploaded file (ZIP, JSON, or CSV)
            source:               Hint: "chatgpt" | "claude" | "auto" (default auto-detect)
            user_id:              User identifier for profile storage
            custom_instructions:  Optional text (Claude doesn't include this in export)
            x_migration_key:      API authentication header

        Returns:
            { job_id: str, status: "processing" }
        """
        _require_auth(x_migration_key)

        # Validate file
        filename = file.filename or "upload"
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        content = await file.read()
        max_size = MAX_ZIP_SIZE if ext == ".zip" else MAX_CSV_SIZE
        if len(content) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {max_size // 1024 // 1024} MB"
            )

        # Save to temp storage
        user_dir = TEMP_DIR / _sanitize_user_id(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        temp_path = user_dir / filename
        temp_path.write_bytes(content)

        # Auto-detect source from filename if not specified
        if source == "auto":
            source = _detect_source(filename, ext)

        # Create job
        job_id = str(uuid.uuid4())
        _jobs[job_id] = {
            "status": "processing",
            "user_id": user_id,
            "source": source,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "result": None,
            "error": None,
        }

        # Process in background
        background_tasks.add_task(
            _process_file_job,
            job_id=job_id,
            file_path=str(temp_path),
            source=source,
            user_id=user_id,
            custom_instructions=custom_instructions,
        )

        logger.info("Upload accepted: job_id=%s, user=%s, source=%s, file=%s",
                    job_id, user_id, source, filename)

        return JSONResponse(
            status_code=202,
            content={
                "job_id": job_id,
                "status": "processing",
                "message": "File received. Processing started.",
            }
        )


    @app.get("/api/migration/status/{job_id}")
    async def get_job_status(
        job_id: str,
        x_migration_key: Optional[str] = Header(None),
    ):
        """
        Poll job status.

        Returns:
            {
                job_id:     str,
                status:     "processing" | "complete" | "error",
                user_id:    str,
                progress:   { message: str, percent: int },  # when processing
                summary:    { conversation_count, message_count, top_topics },  # when complete
                error:      str | null
            }
        """
        _require_auth(x_migration_key)

        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        response = {
            "job_id": job_id,
            "status": job["status"],
            "user_id": job["user_id"],
            "error": job.get("error"),
        }

        if job["status"] == "complete" and job.get("result"):
            profile = job["result"]
            response["summary"] = {
                "conversation_count": profile.get("conversation_count", 0),
                "message_count": profile.get("message_count", 0),
                "date_range_years": profile.get("date_range_years", 0),
                "top_topics": [t["topic"] for t in (profile.get("top_topics") or [])[:5]],
                "communication_style": profile.get("communication_style"),
                "custom_instructions_found": bool(profile.get("custom_instructions_raw")),
            }
        elif job["status"] == "processing":
            response["progress"] = {
                "message": "Parsing conversation history...",
                "percent": 50,
            }

        return response


    @app.get("/api/migration/profile/{user_id}")
    async def get_user_profile(
        user_id: str,
        x_migration_key: Optional[str] = Header(None),
    ):
        """
        Return completed user_context_profile for a user.

        Returns the full profile if migration is complete, 404 if not found.
        """
        _require_auth(x_migration_key)

        profile = _profiles.get(user_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"No migration profile found for user {user_id}"
            )

        return profile


    @app.delete("/api/migration/data/{user_id}")
    async def delete_migration_data(
        user_id: str,
        x_migration_key: Optional[str] = Header(None),
    ):
        """
        Delete all migration data for a user (GDPR Right to Erasure).

        Removes:
            - All temp files in /tmp/purebrain-migration/<user_id>/
            - All in-memory job records for this user
            - The stored user_context_profile
        """
        _require_auth(x_migration_key)

        deleted = []

        # Delete temp files
        user_dir = TEMP_DIR / _sanitize_user_id(user_id)
        if user_dir.exists():
            shutil.rmtree(user_dir, ignore_errors=True)
            deleted.append(f"temp_dir:{user_dir}")

        # Delete jobs
        jobs_to_delete = [jid for jid, j in _jobs.items() if j["user_id"] == user_id]
        for jid in jobs_to_delete:
            del _jobs[jid]
        if jobs_to_delete:
            deleted.append(f"jobs:{jobs_to_delete}")

        # Delete profile
        if user_id in _profiles:
            del _profiles[user_id]
            deleted.append(f"profile:{user_id}")

        logger.info("Migration data deleted for user %s: %s", user_id, deleted)

        return {
            "user_id": user_id,
            "deleted": deleted,
            "message": "All migration data removed.",
        }


    @app.get("/api/migration/health")
    async def health_check():
        return {
            "status": "ok",
            "service": "purebrain-migration-api",
            "version": "1.0.0",
            "temp_dir": str(TEMP_DIR),
            "active_jobs": len(_jobs),
            "stored_profiles": len(_profiles),
        }


# ---------------------------------------------------------------------------
# Background job processor
# ---------------------------------------------------------------------------

def _process_file_job(
    job_id: str,
    file_path: str,
    source: str,
    user_id: str,
    custom_instructions: Optional[str] = None,
):
    """
    Synchronous worker that parses the file and stores the context profile.
    Runs in a FastAPI BackgroundTask thread.
    """
    try:
        logger.info("Processing job %s: source=%s, file=%s", job_id, source, file_path)
        path = Path(file_path)

        # Step 1: Parse based on source
        if source == "chatgpt" or (source == "auto" and path.suffix == ".zip"):
            migration_profile = parse_chatgpt_export(file_path)
        elif source == "claude":
            migration_profile = parse_claude_export(file_path, custom_instructions=custom_instructions)
        elif path.suffix in (".csv", ".json"):
            migration_profile = parse_generic_file(file_path)
            if custom_instructions:
                migration_profile["custom_instructions"] = custom_instructions
        else:
            raise ValueError(f"Cannot determine how to parse: {file_path}")

        # Step 2: Extract user context profile
        context_profile = extract_user_context_profile(migration_profile)

        # Step 3: Store profile
        _profiles[user_id] = context_profile
        _jobs[job_id]["status"] = "complete"
        _jobs[job_id]["result"] = context_profile

        logger.info(
            "Job %s complete: %d conversations, %d topics",
            job_id,
            context_profile.get("conversation_count", 0),
            len(context_profile.get("top_topics", [])),
        )

    except Exception as exc:
        logger.error("Job %s failed: %s", job_id, exc, exc_info=True)
        _jobs[job_id]["status"] = "error"
        _jobs[job_id]["error"] = str(exc)

    finally:
        # Always delete the temp file after processing
        try:
            Path(file_path).unlink(missing_ok=True)
            logger.info("Temp file deleted: %s", file_path)
        except Exception as exc:
            logger.warning("Failed to delete temp file %s: %s", file_path, exc)


# ---------------------------------------------------------------------------
# Cleanup task (call periodically, e.g., every hour)
# ---------------------------------------------------------------------------

def cleanup_stale_jobs():
    """
    Remove jobs and profiles older than FILE_TTL_HOURS.
    Call this from a scheduler or cron job.
    """
    cutoff = datetime.utcnow() - timedelta(hours=FILE_TTL_HOURS)
    stale_jobs = [
        jid for jid, j in list(_jobs.items())
        if datetime.fromisoformat(j["created_at"].replace("Z", "")) < cutoff
    ]
    for jid in stale_jobs:
        del _jobs[jid]

    # Clean up stale temp directories
    if TEMP_DIR.exists():
        for user_dir in TEMP_DIR.iterdir():
            if user_dir.is_dir():
                try:
                    mtime = datetime.utcfromtimestamp(user_dir.stat().st_mtime)
                    if mtime < cutoff:
                        shutil.rmtree(user_dir, ignore_errors=True)
                        logger.info("Cleaned up stale temp dir: %s", user_dir)
                except Exception:
                    pass

    if stale_jobs:
        logger.info("Cleanup: removed %d stale jobs", len(stale_jobs))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sanitize_user_id(user_id: str) -> str:
    """Sanitize user_id to safe directory name."""
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", user_id)[:64]


def _detect_source(filename: str, ext: str) -> str:
    """Auto-detect source from filename."""
    name_lower = filename.lower()
    if "chatgpt" in name_lower or "openai" in name_lower or "conversations" in name_lower:
        return "chatgpt"
    if "claude" in name_lower or "anthropic" in name_lower:
        return "claude"
    if ext == ".zip":
        return "chatgpt"  # Default ZIP to ChatGPT
    return "generic"


# ---------------------------------------------------------------------------
# Avoid import error if regex not imported
# ---------------------------------------------------------------------------

import re


# ---------------------------------------------------------------------------
# CLI runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run("tools.migration.migration_api:app", host="0.0.0.0", port=8001, reload=True)
    except ImportError:
        print("Install uvicorn: pip install uvicorn")
