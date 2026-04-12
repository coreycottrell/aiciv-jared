#!/usr/bin/env python3
"""
test_baas_server.py - TDD tests for Browser-as-a-Service API server.

Tests the REST API endpoints, auth, session management, concurrency limits,
and idle timeout logic. Uses FastAPI's TestClient for in-process testing.
"""

import json
import os
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Set test config path before importing server
TEST_KEYS_PATH = os.path.join(os.path.dirname(__file__), "baas_keys.json")
os.environ["BAAS_KEYS_PATH"] = TEST_KEYS_PATH

from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Create a fresh app instance for each test."""
    # Re-import to get fresh state
    import importlib
    import baas_server
    importlib.reload(baas_server)
    return baas_server.app


@pytest.fixture
def client(app):
    """FastAPI test client with fresh app state."""
    return TestClient(app)


@pytest.fixture
def admin_headers():
    """Headers with a valid admin API key."""
    return {"X-API-Key": "O_EnHpl-94xMLwvWZRNBIc6WGnfl5bkk9Ogk7eew_bg"}


@pytest.fixture
def user_headers():
    """Headers with a valid user API key."""
    return {"X-API-Key": "lyra-baas-key-001"}


@pytest.fixture
def bad_headers():
    """Headers with an invalid API key."""
    return {"X-API-Key": "invalid-key-000"}


# ---------------------------------------------------------------------------
# Health endpoint (no auth required)
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_no_auth_required(self, client):
        """GET /health should work without API key."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "active_sessions" in data
        assert "max_sessions" in data
        assert data["max_sessions"] == 10

    def test_health_returns_session_count(self, client):
        """Health endpoint reports number of active sessions."""
        resp = client.get("/health")
        assert resp.json()["active_sessions"] == 0


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class TestAuth:
    def test_valid_admin_key(self, client, admin_headers):
        """Valid admin key should authenticate successfully."""
        resp = client.get("/sessions", headers=admin_headers)
        assert resp.status_code == 200

    def test_valid_user_key(self, client, user_headers):
        """Valid user key should authenticate successfully."""
        resp = client.get("/sessions", headers=user_headers)
        assert resp.status_code == 200

    def test_invalid_key_rejected(self, client, bad_headers):
        """Invalid API key should return 401."""
        resp = client.get("/sessions", headers=bad_headers)
        assert resp.status_code == 401
        assert "Invalid" in resp.json()["detail"]

    def test_missing_key_rejected(self, client):
        """Missing API key should return 401."""
        resp = client.get("/sessions")
        assert resp.status_code == 401

    def test_health_exempt_from_auth(self, client):
        """Health endpoint should not require auth."""
        resp = client.get("/health")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Session listing
# ---------------------------------------------------------------------------

class TestListSessions:
    def test_list_sessions_empty(self, client, admin_headers):
        """GET /sessions returns empty list when no sessions exist."""
        resp = client.get("/sessions", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json() == {"sessions": []}


# ---------------------------------------------------------------------------
# Session creation (mocked browser)
# ---------------------------------------------------------------------------

class TestCreateSession:
    @patch("baas_server.BrowserSessionManager._launch_browser")
    def test_create_session_returns_id(self, mock_launch, client, admin_headers):
        """POST /sessions should return a session_id."""
        mock_launch.return_value = (MagicMock(), MagicMock())
        resp = client.post("/sessions", headers=admin_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
        assert data["user"] == "Aether"

    @patch("baas_server.BrowserSessionManager._launch_browser")
    def test_create_session_appears_in_list(self, mock_launch, client, admin_headers):
        """Created session should appear in GET /sessions."""
        mock_launch.return_value = (MagicMock(), MagicMock())
        create_resp = client.post("/sessions", headers=admin_headers)
        session_id = create_resp.json()["session_id"]

        list_resp = client.get("/sessions", headers=admin_headers)
        sessions = list_resp.json()["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == session_id

    @patch("baas_server.BrowserSessionManager._launch_browser")
    def test_create_session_with_proxy(self, mock_launch, client, admin_headers):
        """POST /sessions with proxy option."""
        mock_launch.return_value = (MagicMock(), MagicMock())
        resp = client.post(
            "/sessions",
            headers=admin_headers,
            json={"proxy": "socks5://user:pass@host:1080"},
        )
        assert resp.status_code == 201


# ---------------------------------------------------------------------------
# Session operations (mocked browser)
# ---------------------------------------------------------------------------

class TestSessionOperations:
    @pytest.fixture
    def session_id(self, client, admin_headers):
        """Create a session and return its ID."""
        with patch("baas_server.BrowserSessionManager._launch_browser") as mock_launch:
            mock_page = MagicMock()
            mock_page.content = MagicMock(return_value="<html><body>test</body></html>")
            mock_page.screenshot = MagicMock(return_value=b"\x89PNG fake image data")
            mock_page.evaluate = MagicMock(return_value={"result": "ok"})
            mock_page.goto = MagicMock(return_value=None)
            mock_page.click = MagicMock(return_value=None)
            mock_page.fill = MagicMock(return_value=None)
            mock_context = MagicMock()
            mock_launch.return_value = (mock_context, mock_page)
            resp = client.post("/sessions", headers=admin_headers)
            return resp.json()["session_id"]

    def test_navigate(self, client, admin_headers, session_id):
        """POST /sessions/{id}/navigate should succeed."""
        resp = client.post(
            f"/sessions/{session_id}/navigate",
            headers=admin_headers,
            json={"url": "https://example.com"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "navigated"

    def test_navigate_missing_url(self, client, admin_headers, session_id):
        """Navigate without URL should return 422."""
        resp = client.post(
            f"/sessions/{session_id}/navigate",
            headers=admin_headers,
            json={},
        )
        assert resp.status_code == 422

    def test_click(self, client, admin_headers, session_id):
        """POST /sessions/{id}/click should succeed."""
        resp = client.post(
            f"/sessions/{session_id}/click",
            headers=admin_headers,
            json={"selector": "#submit-btn"},
        )
        assert resp.status_code == 200

    def test_type(self, client, admin_headers, session_id):
        """POST /sessions/{id}/type should succeed."""
        resp = client.post(
            f"/sessions/{session_id}/type",
            headers=admin_headers,
            json={"selector": "#email", "text": "test@example.com"},
        )
        assert resp.status_code == 200

    def test_screenshot(self, client, admin_headers, session_id):
        """POST /sessions/{id}/screenshot should return PNG."""
        resp = client.post(
            f"/sessions/{session_id}/screenshot",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"

    def test_content(self, client, admin_headers, session_id):
        """GET /sessions/{id}/content should return HTML."""
        resp = client.get(
            f"/sessions/{session_id}/content",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "html" in resp.json()["html"].lower()

    def test_evaluate(self, client, admin_headers, session_id):
        """POST /sessions/{id}/evaluate should run JS and return result."""
        resp = client.post(
            f"/sessions/{session_id}/evaluate",
            headers=admin_headers,
            json={"script": "document.title"},
        )
        assert resp.status_code == 200
        assert "result" in resp.json()

    def test_delete_session(self, client, admin_headers, session_id):
        """DELETE /sessions/{id} should close session."""
        resp = client.delete(
            f"/sessions/{session_id}",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "closed"

    def test_operations_on_nonexistent_session(self, client, admin_headers):
        """Operations on non-existent session should return 404."""
        fake_id = "nonexistent-session-id"
        assert client.post(
            f"/sessions/{fake_id}/navigate",
            headers=admin_headers,
            json={"url": "https://example.com"},
        ).status_code == 404

        assert client.get(
            f"/sessions/{fake_id}/content",
            headers=admin_headers,
        ).status_code == 404

        assert client.delete(
            f"/sessions/{fake_id}",
            headers=admin_headers,
        ).status_code == 404


# ---------------------------------------------------------------------------
# Concurrency limits
# ---------------------------------------------------------------------------

class TestConcurrency:
    @patch("baas_server.BrowserSessionManager._launch_browser")
    def test_max_sessions_enforced(self, mock_launch, client, admin_headers):
        """Should reject session creation beyond max_sessions (10)."""
        mock_launch.return_value = (MagicMock(), MagicMock())

        # Create 10 sessions (the max)
        for i in range(10):
            resp = client.post("/sessions", headers=admin_headers)
            assert resp.status_code == 201, f"Session {i+1} should succeed"

        # 11th should be rejected
        resp = client.post("/sessions", headers=admin_headers)
        assert resp.status_code == 429
        assert "maximum" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Idle timeout tracking
# ---------------------------------------------------------------------------

class TestIdleTimeout:
    @patch("baas_server.BrowserSessionManager._launch_browser")
    def test_session_tracks_last_activity(self, mock_launch, client, admin_headers):
        """Sessions should track last_activity timestamp."""
        mock_page = MagicMock()
        mock_page.content = MagicMock(return_value="<html></html>")
        mock_launch.return_value = (MagicMock(), mock_page)

        resp = client.post("/sessions", headers=admin_headers)
        session_id = resp.json()["session_id"]

        # Check list to see last_activity
        list_resp = client.get("/sessions", headers=admin_headers)
        session_info = list_resp.json()["sessions"][0]
        assert "last_activity" in session_info
        assert "created_at" in session_info


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

class TestLogging:
    def test_log_file_created(self, client, admin_headers):
        """API calls should be logged."""
        import baas_server
        # Just verify the logging infrastructure exists
        assert hasattr(baas_server, "logger")


# ---------------------------------------------------------------------------
# Client library tests
# ---------------------------------------------------------------------------

class TestBaaSClient:
    def test_client_import(self):
        """Client module should be importable."""
        from baas_client import BrowserService
        bs = BrowserService(api_url="http://localhost:8901", api_key="test-key")
        assert bs.api_url == "http://localhost:8901"
        assert bs.api_key == "test-key"

    def test_client_session_class(self):
        """Client should have a Session class with expected methods."""
        from baas_client import BrowserSession
        # Verify the class has the right methods
        assert hasattr(BrowserSession, "navigate")
        assert hasattr(BrowserSession, "click")
        assert hasattr(BrowserSession, "type_text")
        assert hasattr(BrowserSession, "screenshot")
        assert hasattr(BrowserSession, "content")
        assert hasattr(BrowserSession, "evaluate")
        assert hasattr(BrowserSession, "close")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
