# Browser-as-a-Service (BaaS) API

REST API for fingerprinted browser sessions. Any team member (human or AI) can launch, control, and screenshot browser sessions over HTTP. No local browser dependencies needed.

## Quick Start

### Start the server

```bash
cd /home/jared/projects/AI-CIV/aether/tools/browser-manager
python baas_server.py
# Runs on 0.0.0.0:8901
```

### Use the Python client

```python
from baas_client import BrowserService

bs = BrowserService(api_url="http://89.167.19.20:8901", api_key="chy-baas-key-001")
session = bs.create_session()
session.navigate("https://www.indiegogo.com")
html = session.content()
session.screenshot("/tmp/indiegogo.png")
session.close()
```

### Use with context manager (auto-close)

```python
with bs.create_session() as session:
    session.navigate("https://example.com")
    title = session.evaluate("document.title")
    html = session.content()
```

### Use with curl

```bash
# Health check (no auth)
curl http://89.167.19.20:8901/health

# Create session
curl -X POST http://89.167.19.20:8901/sessions \
  -H "X-API-Key: jared-baas-key-001"

# Navigate
curl -X POST http://89.167.19.20:8901/sessions/{session_id}/navigate \
  -H "X-API-Key: jared-baas-key-001" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Screenshot (returns PNG)
curl -X POST http://89.167.19.20:8901/sessions/{session_id}/screenshot \
  -H "X-API-Key: jared-baas-key-001" \
  -o screenshot.png

# Get page HTML
curl http://89.167.19.20:8901/sessions/{session_id}/content \
  -H "X-API-Key: jared-baas-key-001"

# Run JavaScript
curl -X POST http://89.167.19.20:8901/sessions/{session_id}/evaluate \
  -H "X-API-Key: jared-baas-key-001" \
  -H "Content-Type: application/json" \
  -d '{"script": "document.title"}'

# Close session
curl -X DELETE http://89.167.19.20:8901/sessions/{session_id} \
  -H "X-API-Key: jared-baas-key-001"

# List active sessions
curl http://89.167.19.20:8901/sessions \
  -H "X-API-Key: jared-baas-key-001"
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Server health + session count |
| POST | `/sessions` | Yes | Create fingerprinted browser session |
| GET | `/sessions` | Yes | List active sessions |
| POST | `/sessions/{id}/navigate` | Yes | Navigate to URL |
| POST | `/sessions/{id}/click` | Yes | Click CSS selector |
| POST | `/sessions/{id}/type` | Yes | Type text into CSS selector |
| POST | `/sessions/{id}/screenshot` | Yes | Capture PNG screenshot |
| GET | `/sessions/{id}/content` | Yes | Get page HTML |
| POST | `/sessions/{id}/evaluate` | Yes | Run JavaScript |
| DELETE | `/sessions/{id}` | Yes | Close session |

## Authentication

All endpoints (except `/health`) require an `X-API-Key` header. Keys are stored in `baas_keys.json`.

### Adding a new team member

Edit `baas_keys.json`:

```json
{
  "keys": {
    "newuser-baas-key-001": {"user": "NewUser", "role": "user"}
  }
}
```

Restart the server to pick up new keys.

### Roles

- `admin`: Full access (Aether, Chy, Jared)
- `user`: Full access (all other team members)

Currently both roles have identical permissions. Role field exists for future access control.

## Session Management

- **Max 10 concurrent sessions** across all users
- **Auto-close after 30 minutes idle** (no API calls to that session)
- Each session gets a unique browser fingerprint via BrowserForge
- Sessions use Camoufox for anti-detection

## Configuration

| Setting | Default | Env Var |
|---------|---------|---------|
| API keys file | `baas_keys.json` | `BAAS_KEYS_PATH` |
| Port | 8901 | CLI `--port` |
| Max sessions | 10 | Hardcoded |
| Idle timeout | 30 min | Hardcoded |

## Files

| File | Purpose |
|------|---------|
| `baas_server.py` | FastAPI server |
| `baas_client.py` | Python client library |
| `baas_keys.json` | API key config |
| `test_baas_server.py` | Test suite |
| `logs/baas_server.log` | Server log |

## Running Tests

```bash
cd /home/jared/projects/AI-CIV/aether/tools/browser-manager
pytest test_baas_server.py -v
```

## Server as systemd service (optional)

```ini
[Unit]
Description=Browser-as-a-Service API
After=network.target

[Service]
Type=simple
User=jared
WorkingDirectory=/home/jared/projects/AI-CIV/aether/tools/browser-manager
ExecStart=/usr/bin/python3 baas_server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Dependencies

All already installed on the VPS:
- FastAPI + uvicorn
- Playwright
- Camoufox + BrowserForge
- Xvfb (for headless display)
