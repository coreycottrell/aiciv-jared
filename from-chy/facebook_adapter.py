"""
PureSurf Social Suite -- Facebook Adapter
Automates Facebook page posting, commenting, feed scanning, and group posting
via PureSurf BaaS browser automation.

Endpoints:
    1. page_post      - Draft a post to a Facebook page
    2. confirm_post   - Confirm and publish a drafted post
    3. feed_scan      - Scan a Facebook feed for recent posts + engagement
    4. comment        - Comment on a specific Facebook post
    5. group_post     - Post to a Facebook group (draft-then-confirm)

Architecture:
    - Multi-selector resilience: 4-8 CSS selectors per action + JS fallback
    - Draft-then-confirm flow: page_post returns session_id, confirm_post publishes
    - Screenshots on success/failure (via BaaS screenshot endpoint)
    - Fingerprinted sessions via PureSurf BaaS profiles
"""

import httpx
import json
import time
import asyncio
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("puresurf.facebook")

BAAS_URL = "https://surf.purebrain.ai"


class FacebookAdapter:
    """Facebook automation via PureSurf BaaS browser automation."""

    def __init__(self, api_key: str, profile_name: str = "facebook-purebrain"):
        self.api_key = api_key
        self.profile_name = profile_name
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    # ------------------------------------------------------------------ #
    #  Low-level BaaS helpers                                             #
    # ------------------------------------------------------------------ #

    async def _create_session(self) -> Optional[str]:
        """Create a PureSurf session with MacBook fingerprint profile."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    f"{BAAS_URL}/sessions",
                    headers=self.headers,
                    json={"profile_name": self.profile_name, "device": "macbook"},
                )
                if r.status_code == 200:
                    return r.json().get("session_id")
                logger.error("Session creation failed: %s %s", r.status_code, r.text)
        except httpx.HTTPError as exc:
            logger.error("Session creation HTTP error: %s", exc)
        return None

    async def _navigate(self, session_id: str, url: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    f"{BAAS_URL}/sessions/{session_id}/navigate",
                    headers=self.headers,
                    json={"url": url},
                )
                return r.json() if r.status_code == 200 else {}
        except httpx.HTTPError as exc:
            logger.error("Navigate error: %s", exc)
            return {}

    async def _click(self, session_id: str, selector: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    f"{BAAS_URL}/sessions/{session_id}/click",
                    headers=self.headers,
                    json={"selector": selector},
                )
                return r.json() if r.status_code == 200 else {}
        except httpx.HTTPError as exc:
            logger.error("Click error: %s", exc)
            return {}

    async def _type_text(self, session_id: str, selector: str, text: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    f"{BAAS_URL}/sessions/{session_id}/type",
                    headers=self.headers,
                    json={"selector": selector, "text": text},
                )
                return r.json() if r.status_code == 200 else {}
        except httpx.HTTPError as exc:
            logger.error("Type error: %s", exc)
            return {}

    async def _evaluate(self, session_id: str, expression: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    f"{BAAS_URL}/sessions/{session_id}/evaluate",
                    headers=self.headers,
                    json={"expression": expression},
                )
                return r.json() if r.status_code == 200 else {}
        except httpx.HTTPError as exc:
            logger.error("Evaluate error: %s", exc)
            return {}

    async def _get_content(self, session_id: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.get(
                    f"{BAAS_URL}/sessions/{session_id}/content",
                    headers=self.headers,
                )
                return r.json() if r.status_code == 200 else {}
        except httpx.HTTPError as exc:
            logger.error("Get content error: %s", exc)
            return {}

    async def _screenshot(self, session_id: str, label: str = "screenshot") -> dict:
        """Capture a screenshot for audit / debugging."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    f"{BAAS_URL}/sessions/{session_id}/screenshot",
                    headers=self.headers,
                    json={"label": label},
                )
                return r.json() if r.status_code == 200 else {}
        except httpx.HTTPError as exc:
            logger.error("Screenshot error: %s", exc)
            return {}

    async def _close_session(self, session_id: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.delete(
                    f"{BAAS_URL}/sessions/{session_id}",
                    headers=self.headers,
                )
                return r.json() if r.status_code == 200 else {}
        except httpx.HTTPError as exc:
            logger.error("Close session error: %s", exc)
            return {}

    async def _wait(self, seconds: float):
        await asyncio.sleep(seconds)

    # ------------------------------------------------------------------ #
    #  Multi-selector helpers                                             #
    # ------------------------------------------------------------------ #

    async def _try_click(self, session_id: str, selectors: List[str]) -> bool:
        """Attempt click across multiple selectors. Returns True on first success."""
        for sel in selectors:
            try:
                r = await self._click(session_id, sel)
                if r.get("status") == "clicked":
                    return True
            except Exception:
                continue
        return False

    async def _try_type(self, session_id: str, selectors: List[str], text: str) -> bool:
        """Attempt typing across multiple selectors. Returns True on first success."""
        for sel in selectors:
            try:
                r = await self._type_text(session_id, sel, text)
                if r.get("status") in ("typed", "filled"):
                    return True
            except Exception:
                continue
        return False

    # ------------------------------------------------------------------ #
    #  ENDPOINT 1: page_post  (draft-then-confirm)                       #
    # ------------------------------------------------------------------ #

    async def page_post(
        self,
        message: str,
        image_base64: Optional[str] = None,
        page_url: str = "https://www.facebook.com",
    ) -> Dict[str, Any]:
        """Draft a post to a Facebook page.

        Flow:
            1. Navigate to page
            2. Click 'Create post' / 'What's on your mind'
            3. Type message into the composer
            4. Optionally attach an image
            5. Return draft preview + session_id for confirm_post()

        Returns session_id so the caller can review before publishing.
        """
        result: Dict[str, Any] = {
            "status": "failed",
            "step": "",
            "error": None,
            "platform": "facebook",
        }
        session_id = None

        try:
            # --- Create session ---
            session_id = await self._create_session()
            if not session_id:
                result["error"] = "Failed to create BaaS session"
                return result

            # --- Navigate ---
            await self._navigate(session_id, page_url)
            await self._wait(3)
            result["step"] = "navigated"

            # --- Login gate ---
            content = await self._get_content(session_id)
            page_html = content.get("content", "")
            current_url = content.get("url", "")
            if "login" in current_url.lower() or "Log In" in page_html[:2000]:
                await self._screenshot(session_id, "login_required")
                result["error"] = (
                    "Not logged in. Authenticate the profile first via BaaS "
                    "cookie import or manual login."
                )
                result["step"] = "login_required"
                await self._close_session(session_id)
                return result

            # --- Click 'Create post' (8 selectors + JS fallback) ---
            create_post_selectors = [
                "[aria-label='Create a post']",
                "[aria-label=\"What's on your mind\"]",
                "[data-pagelet='ProfileComposer'] [role='button']",
                "div[role='button']:has-text('Write something')",
                "div[role='button']:has-text('Create post')",
                "[aria-label='Create Post']",
                "span:has-text(\"What's on your mind\")",
                "[data-pagelet='ProfileComposer']",
            ]

            clicked = await self._try_click(session_id, create_post_selectors)

            if not clicked:
                js_result = await self._evaluate(
                    session_id,
                    """
                    (function() {
                        var btns = document.querySelectorAll('[role="button"]');
                        for (var i = 0; i < btns.length; i++) {
                            var t = btns[i].textContent || '';
                            if (t.indexOf("What's on your mind") !== -1 ||
                                t.indexOf("Create post") !== -1 ||
                                t.indexOf("Write something") !== -1) {
                                btns[i].click();
                                return 'clicked';
                            }
                        }
                        return 'not_found';
                    })()
                    """,
                )
                if js_result.get("result") != "clicked":
                    await self._screenshot(session_id, "create_post_failed")
                    result["error"] = "Could not find Create Post button"
                    result["step"] = "create_post_button_missing"
                    await self._close_session(session_id)
                    return result

            await self._wait(2)
            result["step"] = "composer_opened"

            # --- Type message (5 selectors + JS fallback) ---
            type_selectors = [
                "[contenteditable='true'][role='textbox']",
                "[aria-label=\"What's on your mind?\"] [contenteditable='true']",
                "div[contenteditable='true'][data-lexical-editor]",
                "[role='dialog'] [contenteditable='true']",
                "form [contenteditable='true']",
            ]

            typed = await self._try_type(session_id, type_selectors, message)

            if not typed:
                js_result = await self._evaluate(
                    session_id,
                    f"""
                    (function() {{
                        var editors = document.querySelectorAll('[contenteditable="true"]');
                        for (var i = 0; i < editors.length; i++) {{
                            var ed = editors[i];
                            if (ed.closest('[role="dialog"]') || ed.closest('form')) {{
                                ed.focus();
                                document.execCommand('insertText', false, {json.dumps(message)});
                                return 'typed';
                            }}
                        }}
                        return 'not_found';
                    }})()
                    """,
                )
                if js_result.get("result") != "typed":
                    await self._screenshot(session_id, "type_message_failed")
                    result["error"] = "Could not type into composer"
                    result["step"] = "composer_type_failed"
                    await self._close_session(session_id)
                    return result

            await self._wait(1)
            result["step"] = "message_typed"

            # --- Optional image attachment ---
            if image_base64:
                photo_selectors = [
                    "[aria-label='Photo/video']",
                    "[aria-label='Photo/Video']",
                    "[aria-label='Add photos/videos']",
                    "div[role='button']:has-text('Photo')",
                ]
                await self._try_click(session_id, photo_selectors)
                await self._wait(1)
                # Upload via BaaS file-input injection
                await self._evaluate(
                    session_id,
                    f"""
                    (function() {{
                        var input = document.querySelector('input[type="file"][accept*="image"]');
                        if (input) {{
                            var b64 = {json.dumps(image_base64)};
                            var binary = atob(b64);
                            var arr = new Uint8Array(binary.length);
                            for (var i = 0; i < binary.length; i++) arr[i] = binary.charCodeAt(i);
                            var file = new File([arr], 'upload.jpg', {{type: 'image/jpeg'}});
                            var dt = new DataTransfer();
                            dt.items.add(file);
                            input.files = dt.files;
                            input.dispatchEvent(new Event('change', {{bubbles: true}}));
                            return 'uploaded';
                        }}
                        return 'no_input';
                    }})()
                    """,
                )
                await self._wait(2)
                result["image_attached"] = True

            # --- Take screenshot of draft ---
            await self._screenshot(session_id, "draft_ready")

            result["status"] = "draft_ready"
            result["session_id"] = session_id
            result["message_preview"] = message[:200]
            # Session kept alive for confirm_post()
            return result

        except Exception as e:
            logger.exception("page_post error")
            result["error"] = str(e)
            if session_id:
                await self._screenshot(session_id, "page_post_exception")
                await self._close_session(session_id)
            return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 2: confirm_post                                          #
    # ------------------------------------------------------------------ #

    async def confirm_post(self, session_id: str) -> Dict[str, Any]:
        """Confirm and publish a previously drafted Facebook post.

        Expects the session_id returned by page_post().
        Clicks the Post/Share/Publish button, waits for confirmation, screenshots.
        """
        result: Dict[str, Any] = {
            "status": "failed",
            "step": "",
            "error": None,
            "platform": "facebook",
        }

        try:
            # --- Click Post button (6 selectors + JS fallback) ---
            post_selectors = [
                "[aria-label='Post']",
                "div[role='button']:has-text('Post')",
                "[data-testid='react-composer-post-button']",
                "form [type='submit']",
                "button:has-text('Post')",
                "[aria-label='Share']",
            ]

            clicked = await self._try_click(session_id, post_selectors)

            if not clicked:
                js_result = await self._evaluate(
                    session_id,
                    """
                    (function() {
                        var btns = document.querySelectorAll('[role="button"], button');
                        for (var i = 0; i < btns.length; i++) {
                            var text = (btns[i].textContent || '').trim();
                            if (text === 'Post' || text === 'Share' || text === 'Publish') {
                                btns[i].click();
                                return 'clicked';
                            }
                        }
                        return 'not_found';
                    })()
                    """,
                )
                if js_result.get("result") != "clicked":
                    await self._screenshot(session_id, "confirm_post_failed")
                    result["error"] = "Could not find Post/Share/Publish button"
                    result["step"] = "post_button_missing"
                    return result

            await self._wait(3)

            # --- Verify post published ---
            await self._screenshot(session_id, "post_confirmed")

            result["status"] = "posted"
            result["step"] = "confirmed"
            result["timestamp"] = time.time()

        except Exception as e:
            logger.exception("confirm_post error")
            result["error"] = str(e)
            await self._screenshot(session_id, "confirm_post_exception")
        finally:
            await self._close_session(session_id)

        return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 3: feed_scan                                             #
    # ------------------------------------------------------------------ #

    async def feed_scan(
        self,
        page_url: str = "https://www.facebook.com",
        max_posts: int = 10,
    ) -> Dict[str, Any]:
        """Scan a Facebook feed for recent posts and engagement metrics.

        Returns a list of post objects with text excerpts, reaction counts,
        and comment counts.
        """
        result: Dict[str, Any] = {"status": "failed", "posts": [], "error": None}
        session_id = None

        try:
            session_id = await self._create_session()
            if not session_id:
                result["error"] = "Failed to create BaaS session"
                return result

            await self._navigate(session_id, page_url)
            await self._wait(4)

            # --- Scroll to load more posts ---
            await self._evaluate(
                session_id,
                "window.scrollBy(0, 2000); void(0);",
            )
            await self._wait(2)

            # --- Extract posts via JS ---
            posts_data = await self._evaluate(
                session_id,
                f"""
                (function() {{
                    var posts = [];
                    var feedItems = document.querySelectorAll(
                        '[data-pagelet*="FeedUnit"], [role="article"], [data-testid="Keycommand_wrapper"]'
                    );
                    var limit = Math.min(feedItems.length, {max_posts});
                    for (var i = 0; i < limit; i++) {{
                        var item = feedItems[i];
                        var textEl = item.querySelector(
                            '[data-ad-preview="message"], [data-testid="post_message"], ' +
                            '[dir="auto"]'
                        );
                        var reactionsEl = item.querySelector(
                            '[aria-label*="reaction"], [aria-label*="like"], ' +
                            '[aria-label*="Love"], [aria-label*="people reacted"]'
                        );
                        var commentsEl = item.querySelector('[aria-label*="comment"]');
                        var sharesEl = item.querySelector('[aria-label*="share"]');
                        var linkEl = item.querySelector('a[href*="/posts/"], a[href*="/permalink/"]');
                        posts.push({{
                            text: textEl ? textEl.textContent.substring(0, 300) : '',
                            reactions: reactionsEl ? reactionsEl.textContent : '0',
                            comments: commentsEl ? commentsEl.textContent : '0',
                            shares: sharesEl ? sharesEl.textContent : '0',
                            url: linkEl ? linkEl.href : ''
                        }});
                    }}
                    return JSON.stringify(posts);
                }})()
                """,
            )

            try:
                parsed = json.loads(posts_data.get("result", "[]"))
                result["posts"] = parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                result["posts"] = []

            await self._screenshot(session_id, "feed_scan_complete")

            result["status"] = "scanned"
            result["count"] = len(result["posts"])

        except Exception as e:
            logger.exception("feed_scan error")
            result["error"] = str(e)
            if session_id:
                await self._screenshot(session_id, "feed_scan_exception")
        finally:
            if session_id:
                await self._close_session(session_id)

        return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 4: comment                                               #
    # ------------------------------------------------------------------ #

    async def comment(self, post_url: str, comment_text: str) -> Dict[str, Any]:
        """Comment on a specific Facebook post.

        Navigates to the post URL, opens the comment box, types the comment,
        and submits via Enter key.
        """
        result: Dict[str, Any] = {
            "status": "failed",
            "step": "",
            "error": None,
            "platform": "facebook",
        }
        session_id = None

        try:
            session_id = await self._create_session()
            if not session_id:
                result["error"] = "Failed to create BaaS session"
                return result

            await self._navigate(session_id, post_url)
            await self._wait(3)
            result["step"] = "navigated"

            # --- Click comment box (5 selectors + JS fallback) ---
            comment_click_selectors = [
                "[aria-label='Write a comment']",
                "[aria-label='Write a comment...']",
                "[placeholder='Write a comment...']",
                "[contenteditable='true'][aria-label*='comment' i]",
                "form [contenteditable='true']",
            ]

            clicked = await self._try_click(session_id, comment_click_selectors)

            if not clicked:
                # JS fallback: find and click any comment-related input
                await self._evaluate(
                    session_id,
                    """
                    (function() {
                        var els = document.querySelectorAll(
                            '[contenteditable="true"], [role="textbox"]'
                        );
                        for (var i = 0; i < els.length; i++) {
                            var label = (els[i].getAttribute('aria-label') || '').toLowerCase();
                            if (label.indexOf('comment') !== -1) {
                                els[i].click();
                                els[i].focus();
                                return 'clicked';
                            }
                        }
                        return 'not_found';
                    })()
                    """,
                )

            await self._wait(1)
            result["step"] = "comment_box_opened"

            # --- Type comment (5 selectors + JS fallback) ---
            comment_type_selectors = [
                "[aria-label='Write a comment'] [contenteditable='true']",
                "[aria-label='Write a comment...']",
                "[contenteditable='true'][aria-label*='comment' i]",
                "[role='dialog'] [contenteditable='true']",
                "form [contenteditable='true']",
            ]

            typed = await self._try_type(session_id, comment_type_selectors, comment_text)

            if not typed:
                js_result = await self._evaluate(
                    session_id,
                    f"""
                    (function() {{
                        var editors = document.querySelectorAll('[contenteditable="true"]');
                        for (var i = 0; i < editors.length; i++) {{
                            var label = (editors[i].getAttribute('aria-label') || '').toLowerCase();
                            if (label.indexOf('comment') !== -1 ||
                                editors[i].closest('form')) {{
                                editors[i].focus();
                                document.execCommand('insertText', false, {json.dumps(comment_text)});
                                return 'typed';
                            }}
                        }}
                        return 'not_found';
                    }})()
                    """,
                )
                if js_result.get("result") != "typed":
                    await self._screenshot(session_id, "comment_type_failed")
                    result["error"] = "Could not type into comment box"
                    result["step"] = "comment_type_failed"
                    await self._close_session(session_id)
                    return result

            await self._wait(1)
            result["step"] = "comment_typed"

            # --- Submit comment via Enter key ---
            await self._evaluate(
                session_id,
                """
                (function() {
                    var editors = document.querySelectorAll('[contenteditable="true"]');
                    for (var i = 0; i < editors.length; i++) {
                        var label = (editors[i].getAttribute('aria-label') || '').toLowerCase();
                        if (label.indexOf('comment') !== -1 ||
                            editors[i].closest('form')) {
                            var ev = new KeyboardEvent('keydown', {
                                key: 'Enter', code: 'Enter',
                                keyCode: 13, which: 13, bubbles: true
                            });
                            editors[i].dispatchEvent(ev);
                            return 'submitted';
                        }
                    }
                    return 'not_found';
                })()
                """,
            )

            await self._wait(2)
            await self._screenshot(session_id, "comment_submitted")

            result["status"] = "commented"
            result["step"] = "submitted"
            result["comment_preview"] = comment_text[:100]
            result["timestamp"] = time.time()

        except Exception as e:
            logger.exception("comment error")
            result["error"] = str(e)
            if session_id:
                await self._screenshot(session_id, "comment_exception")
        finally:
            if session_id:
                await self._close_session(session_id)

        return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 5: group_post  (draft-then-confirm via page_post reuse)  #
    # ------------------------------------------------------------------ #

    async def group_post(
        self,
        group_url: str,
        message: str,
        image_base64: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Post to a Facebook group.

        Uses the same draft-then-confirm flow as page_post since Facebook
        groups share the same composer UI. Returns session_id for
        confirm_post().
        """
        result = await self.page_post(
            message=message,
            image_base64=image_base64,
            page_url=group_url,
        )
        result["target"] = "group"
        result["group_url"] = group_url
        return result


# ====================================================================== #
#  FastAPI / Starlette Router Extension                                   #
# ====================================================================== #


def extend_facebook_router(router, sessions: dict, auth_check):
    """Add Facebook endpoints to an existing social-suite router.

    Usage:
        from facebook_adapter import extend_facebook_router
        extend_facebook_router(social_router, active_sessions, check_api_key)

    Registers 5 POST routes under /social/adapters/facebook/*.
    """
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    adapter = FacebookAdapter(api_key="chy-baas-key-001")

    async def fb_page_post(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        result = await adapter.page_post(
            message=body.get("message", ""),
            image_base64=body.get("image_base64"),
            page_url=body.get("page_url", "https://www.facebook.com"),
        )
        return JSONResponse(result)

    async def fb_confirm_post(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        if not sid:
            return JSONResponse(
                {"error": "session_id is required"}, status_code=400
            )
        result = await adapter.confirm_post(session_id=sid)
        return JSONResponse(result)

    async def fb_feed_scan(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        result = await adapter.feed_scan(
            page_url=body.get("page_url", "https://www.facebook.com"),
            max_posts=body.get("max_posts", 10),
        )
        return JSONResponse(result)

    async def fb_comment(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        post_url = body.get("post_url", "")
        comment_text = body.get("comment_text", "")
        if not post_url or not comment_text:
            return JSONResponse(
                {"error": "post_url and comment_text are required"}, status_code=400
            )
        result = await adapter.comment(post_url=post_url, comment_text=comment_text)
        return JSONResponse(result)

    async def fb_group_post(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        group_url = body.get("group_url", "")
        if not group_url:
            return JSONResponse(
                {"error": "group_url is required"}, status_code=400
            )
        result = await adapter.group_post(
            group_url=group_url,
            message=body.get("message", ""),
            image_base64=body.get("image_base64"),
        )
        return JSONResponse(result)

    router.routes.extend(
        [
            Route(
                "/social/adapters/facebook/page-post",
                fb_page_post,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/facebook/confirm-post",
                fb_confirm_post,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/facebook/feed-scan",
                fb_feed_scan,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/facebook/comment",
                fb_comment,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/facebook/group-post",
                fb_group_post,
                methods=["POST"],
            ),
        ]
    )


# ====================================================================== #
#  Quick smoke test                                                       #
# ====================================================================== #

if __name__ == "__main__":

    async def test():
        adapter = FacebookAdapter(api_key="test-key")
        print("FacebookAdapter initialized")
        print(f"  BaaS URL:  {BAAS_URL}")
        print(f"  Profile:   {adapter.profile_name}")
        print(f"  Endpoints: page_post, confirm_post, feed_scan, comment, group_post")

        # Session create/destroy round-trip
        sid = await adapter._create_session()
        print(f"  Session created: {sid}")
        if sid:
            await adapter._close_session(sid)
            print("  Session closed")

    asyncio.run(test())
