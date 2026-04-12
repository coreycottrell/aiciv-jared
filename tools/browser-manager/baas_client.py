#!/usr/bin/env python3
"""
baas_client.py - Python client for Browser-as-a-Service (BaaS) API.

Makes it dead simple for any team member to control remote browser sessions:

    from baas_client import BrowserService

    bs = BrowserService(api_url="http://89.167.19.20:8901", api_key="chy-baas-key-001")
    session = bs.create_session()
    session.navigate("https://www.indiegogo.com")
    html = session.content()
    session.screenshot("/tmp/indiegogo.png")
    session.close()
"""

import json
import os
from typing import Optional

import requests


class BrowserSession:
    """Represents a single remote browser session."""

    def __init__(self, service: "BrowserService", session_id: str, user: str):
        self.service = service
        self.session_id = session_id
        self.user = user

    def _url(self, path: str = "") -> str:
        return f"{self.service.api_url}/sessions/{self.session_id}{path}"

    def _headers(self) -> dict:
        return {"X-API-Key": self.service.api_key}

    def navigate(self, url: str) -> dict:
        """Navigate the browser to a URL."""
        resp = requests.post(
            self._url("/navigate"),
            headers=self._headers(),
            json={"url": url},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def click(self, selector: str, timeout: int = 5000) -> dict:
        """Click an element by CSS selector."""
        resp = requests.post(
            self._url("/click"),
            headers=self._headers(),
            json={"selector": selector, "timeout": timeout},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def type_text(self, selector: str, text: str, timeout: int = 5000) -> dict:
        """Type text into an element by CSS selector."""
        resp = requests.post(
            self._url("/type"),
            headers=self._headers(),
            json={"selector": selector, "text": text, "timeout": timeout},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def screenshot(self, save_path: Optional[str] = None) -> bytes:
        """
        Take a screenshot. Returns PNG bytes.
        If save_path is provided, also saves to disk.
        """
        resp = requests.post(
            self._url("/screenshot"),
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        image_data = resp.content
        if save_path:
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(image_data)
        return image_data

    def content(self) -> str:
        """Get the current page HTML."""
        resp = requests.get(
            self._url("/content"),
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["html"]

    def evaluate(self, script: str):
        """Run JavaScript on the page and return the result."""
        resp = requests.post(
            self._url("/evaluate"),
            headers=self._headers(),
            json={"script": script},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["result"]

    def close(self) -> dict:
        """Close this browser session."""
        resp = requests.delete(
            self._url(),
            headers=self._headers(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def __repr__(self):
        return f"BrowserSession(id={self.session_id!r}, user={self.user!r})"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            self.close()
        except Exception:
            pass


class BrowserService:
    """
    Client for the Browser-as-a-Service API.

    Usage:
        bs = BrowserService(
            api_url="http://89.167.19.20:8901",
            api_key="chy-baas-key-001",
        )
        session = bs.create_session()
        session.navigate("https://example.com")
        session.close()

    With context manager:
        with bs.create_session() as session:
            session.navigate("https://example.com")
            html = session.content()
    """

    def __init__(
        self,
        api_url: str = "http://89.167.19.20:8901",
        api_key: Optional[str] = None,
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key or os.environ.get("BAAS_API_KEY", "")

    def _headers(self) -> dict:
        return {"X-API-Key": self.api_key}

    def health(self) -> dict:
        """Check server health (no auth required)."""
        resp = requests.get(f"{self.api_url}/health", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def create_session(
        self,
        proxy: Optional[str] = None,
        timezone: Optional[str] = None,
        locale: Optional[str] = None,
    ) -> BrowserSession:
        """
        Create a new fingerprinted browser session.

        Returns a BrowserSession object for controlling the browser.
        """
        body = {}
        if proxy:
            body["proxy"] = proxy
        if timezone:
            body["timezone"] = timezone
        if locale:
            body["locale"] = locale

        resp = requests.post(
            f"{self.api_url}/sessions",
            headers=self._headers(),
            json=body or None,
            timeout=60,  # Browser launch can take a moment
        )
        resp.raise_for_status()
        data = resp.json()
        return BrowserSession(
            service=self,
            session_id=data["session_id"],
            user=data["user"],
        )

    def list_sessions(self) -> list:
        """List all active browser sessions."""
        resp = requests.get(
            f"{self.api_url}/sessions",
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["sessions"]

    def __repr__(self):
        return f"BrowserService(api_url={self.api_url!r})"


# ---------------------------------------------------------------------------
# CLI usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BaaS Client CLI")
    parser.add_argument("--url", default="http://89.167.19.20:8901", help="API URL")
    parser.add_argument("--key", required=True, help="API key")
    parser.add_argument("action", choices=["health", "list", "test"], help="Action")
    args = parser.parse_args()

    bs = BrowserService(api_url=args.url, api_key=args.key)

    if args.action == "health":
        print(json.dumps(bs.health(), indent=2))
    elif args.action == "list":
        sessions = bs.list_sessions()
        print(json.dumps(sessions, indent=2))
    elif args.action == "test":
        print("Creating session...")
        with bs.create_session() as session:
            print(f"  Session: {session.session_id}")
            session.navigate("https://example.com")
            print("  Navigated to example.com")
            html = session.content()
            print(f"  Page HTML: {len(html)} chars")
            session.screenshot("/tmp/baas_test.png")
            print("  Screenshot saved to /tmp/baas_test.png")
        print("Session closed.")
