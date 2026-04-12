#!/usr/bin/env python3
"""PureBrain Avatar Generation API.

Lightweight Flask API that receives a visual description from the chatbox
client JS and returns a generated avatar image URL.

Endpoints:
    POST /api/avatar/generate
        Body: { "description": "...", "name": "...", "user_id": "..." }
        Returns: { "url": "https://purebrain.ai/wp-content/.../avatar.png", "id": 123 }

    GET /api/avatar/status/<hash>
        Returns generation status for async requests

    GET /api/health
        Health check

Usage:
    # Development
    python tools/avatar_api.py

    # Production (behind nginx/gunicorn)
    gunicorn -w 2 -b 0.0.0.0:5050 tools.avatar_api:app
"""

import os
import sys
import json
import hashlib
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

app = Flask(__name__)

# CORS: Allow requests from purebrain.ai
CORS(app, origins=[
    'https://purebrain.ai',
    'https://www.purebrain.ai',
    'http://localhost:3000',  # Dev
    'http://localhost:5050',
])

# In-memory job tracking (use Redis in production)
generation_jobs = {}

# Rate limiting (simple in-memory, per IP)
rate_limits = {}
MAX_REQUESTS_PER_HOUR = 20


def check_rate_limit(ip: str) -> bool:
    """Simple rate limiter - MAX_REQUESTS_PER_HOUR per IP."""
    now = datetime.now()
    if ip not in rate_limits:
        rate_limits[ip] = []

    # Clean old entries
    rate_limits[ip] = [t for t in rate_limits[ip] if (now - t).seconds < 3600]

    if len(rate_limits[ip]) >= MAX_REQUESTS_PER_HOUR:
        return False

    rate_limits[ip].append(now)
    return True


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "purebrain-avatar-api"})


@app.route('/api/avatar/generate', methods=['POST'])
def generate():
    """Generate an avatar from a visual description.

    Body:
        description (str, required): AI's visual self-description
        name (str, optional): AI's chosen name
        user_id (str, optional): User identifier
        async (bool, optional): If true, returns immediately with job ID
    """
    # Rate limit
    client_ip = request.remote_addr
    if not check_rate_limit(client_ip):
        return jsonify({"error": "Rate limit exceeded. Max 20 per hour."}), 429

    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify({"error": "Missing 'description' field"}), 400

    description = data['description']
    ai_name = data.get('name', '')
    user_id = data.get('user_id', '')
    is_async = data.get('async', False)

    # Validate description length
    if len(description) < 10:
        return jsonify({"error": "Description too short (min 10 chars)"}), 400
    if len(description) > 2000:
        return jsonify({"error": "Description too long (max 2000 chars)"}), 400

    # Generate hash for deduplication
    desc_hash = hashlib.md5(f"{description}:{ai_name}".encode()).hexdigest()[:12]

    # Check if already generated
    if desc_hash in generation_jobs and generation_jobs[desc_hash].get('status') == 'complete':
        return jsonify(generation_jobs[desc_hash])

    if is_async:
        # Async: start generation in background, return job ID
        generation_jobs[desc_hash] = {"status": "generating", "hash": desc_hash}
        thread = threading.Thread(
            target=_generate_and_upload,
            args=(description, ai_name, user_id, desc_hash)
        )
        thread.start()
        return jsonify({"status": "generating", "hash": desc_hash}), 202
    else:
        # Sync: generate and return
        result = _generate_and_upload(description, ai_name, user_id, desc_hash)
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Avatar generation failed"}), 500


@app.route('/api/avatar/status/<hash_id>', methods=['GET'])
def status(hash_id):
    """Check the status of an async avatar generation job."""
    if hash_id in generation_jobs:
        return jsonify(generation_jobs[hash_id])
    return jsonify({"error": "Job not found"}), 404


def _generate_and_upload(description: str, ai_name: str, user_id: str, desc_hash: str) -> dict:
    """Generate avatar and upload to WordPress."""
    try:
        from tools.avatar_generator import generate_avatar, upload_avatar_to_wordpress

        # Generate the avatar
        result = generate_avatar(
            visual_description=description,
            ai_name=ai_name,
            user_id=user_id,
            size="1:1",
            resolution="1K",  # 1K for faster API response, 2K for quality
            send_telegram=False
        )

        if not result:
            generation_jobs[desc_hash] = {"status": "failed", "error": "Generation returned None"}
            return None

        # Upload to WordPress
        wp_result = upload_avatar_to_wordpress(result['path'], ai_name)

        if wp_result:
            final = {
                "status": "complete",
                "hash": desc_hash,
                "url": wp_result['url'],
                "wp_id": wp_result['id'],
                "name": ai_name,
                "timestamp": result['timestamp']
            }
        else:
            # Fallback: return local path (for dev)
            final = {
                "status": "complete",
                "hash": desc_hash,
                "url": None,
                "local_path": result['path'],
                "name": ai_name,
                "timestamp": result['timestamp'],
                "note": "WordPress upload failed, local path available"
            }

        generation_jobs[desc_hash] = final
        return final

    except Exception as e:
        error_result = {"status": "failed", "error": str(e), "hash": desc_hash}
        generation_jobs[desc_hash] = error_result
        print(f"[AVATAR API] Error: {e}")
        return None


if __name__ == '__main__':
    port = int(os.environ.get('AVATAR_API_PORT', 5050))
    print(f"Starting PureBrain Avatar API on port {port}")
    print(f"  POST /api/avatar/generate")
    print(f"  GET  /api/avatar/status/<hash>")
    print(f"  GET  /api/health")
    app.run(host='0.0.0.0', port=port, debug=True)
