"""
PureSurf Social Suite -- TikTok & Reddit Adapters
Automates TikTok video posting, engagement, feed scanning AND Reddit posting,
commenting, voting, and feed scanning via PureSurf BaaS browser automation.

TikTok Endpoints:
    1. post_video     - Upload video with caption + hashtags (draft)
    2. confirm_post   - Confirm and publish a drafted video
    3. feed_scan      - Scan For You Page or profile feed
    4. engage         - Like, comment, share, or follow from a post
    5. profile_scan   - Get follower count, following, likes, bio

Reddit Endpoints:
    1. post           - Create a post (text, link, or image) in a subreddit
    2. comment        - Comment on a post
    3. upvote         - Upvote a post
    4. feed_scan      - Scan subreddit feed
    5. profile_check  - Check karma, post history

Architecture:
    - Multi-selector resilience: 4-8 CSS selectors per action + JS fallback
    - Draft-then-confirm flow for TikTok video posts
    - Screenshots on success/failure (via BaaS screenshot endpoint)
    - Fingerprinted sessions via PureSurf BaaS profiles
"""

import httpx
import json
import time
import asyncio
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("puresurf.social")

BAAS_URL = "https://surf.purebrain.ai"


# ====================================================================== #
#  Shared BaaS Base Class                                                  #
# ====================================================================== #


class _BaaSBase:
    """Shared low-level BaaS helpers for all social adapters."""

    def __init__(self, api_key: str, profile_name: str):
        self.api_key = api_key
        self.profile_name = profile_name
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    async def _create_session(self) -> Optional[str]:
        """Create a PureSurf session with fingerprint profile."""
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

    def _result_template(self, platform: str) -> Dict[str, Any]:
        return {"status": "failed", "step": "", "error": None, "platform": platform}


# ====================================================================== #
#  TikTok Adapter                                                          #
# ====================================================================== #


class TikTokAdapter(_BaaSBase):
    """TikTok automation via PureSurf BaaS browser automation."""

    def __init__(self, api_key: str, profile_name: str = "tiktok-purebrain"):
        super().__init__(api_key, profile_name)

    # ------------------------------------------------------------------ #
    #  ENDPOINT 1: post_video  (draft-then-confirm)                       #
    # ------------------------------------------------------------------ #

    async def post_video(
        self,
        session_id: str,
        video_base64: str,
        caption: str,
        hashtags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Upload a video to TikTok with caption and hashtags (draft state).

        Videos should be vertical 9:16 format.
        Captions max 2200 characters including hashtags.
        Returns session_id for confirm_post().
        """
        result = self._result_template("tiktok")

        try:
            # --- Navigate to upload page ---
            await self._navigate(session_id, "https://www.tiktok.com/upload")
            await self._wait(4)
            result["step"] = "navigated"

            # --- Login gate ---
            content = await self._get_content(session_id)
            page_html = content.get("content", "")
            current_url = content.get("url", "")
            if "login" in current_url.lower() or "Log in" in page_html[:3000]:
                await self._screenshot(session_id, "login_required")
                result["error"] = (
                    "Not logged in. Authenticate the TikTok profile first via "
                    "BaaS cookie import or manual login."
                )
                result["step"] = "login_required"
                return result

            # --- Upload video via file input (6 selectors + JS fallback) ---
            upload_selectors = [
                "input[type='file'][accept*='video']",
                "input[type='file'][accept*='mp4']",
                "[data-e2e='upload-card'] input[type='file']",
                ".upload-card input[type='file']",
                "#upload-btn input[type='file']",
                "input[accept='video/mp4,video/webm,video/ogg']",
            ]

            uploaded = False
            for sel in upload_selectors:
                js_result = await self._evaluate(
                    session_id,
                    f"""
                    (function() {{
                        var input = document.querySelector({json.dumps(sel)});
                        if (input) {{
                            var b64 = {json.dumps(video_base64)};
                            var binary = atob(b64);
                            var arr = new Uint8Array(binary.length);
                            for (var i = 0; i < binary.length; i++) arr[i] = binary.charCodeAt(i);
                            var file = new File([arr], 'video.mp4', {{type: 'video/mp4'}});
                            var dt = new DataTransfer();
                            dt.items.add(file);
                            input.files = dt.files;
                            input.dispatchEvent(new Event('change', {{bubbles: true}}));
                            return 'uploaded';
                        }}
                        return 'not_found';
                    }})()
                    """,
                )
                if js_result.get("result") == "uploaded":
                    uploaded = True
                    break

            if not uploaded:
                # JS fallback: find any file input on the page
                js_result = await self._evaluate(
                    session_id,
                    f"""
                    (function() {{
                        var inputs = document.querySelectorAll('input[type="file"]');
                        for (var i = 0; i < inputs.length; i++) {{
                            var accept = inputs[i].getAttribute('accept') || '';
                            if (accept.indexOf('video') !== -1 || accept === '' || accept === '*') {{
                                var b64 = {json.dumps(video_base64)};
                                var binary = atob(b64);
                                var arr = new Uint8Array(binary.length);
                                for (var j = 0; j < binary.length; j++) arr[j] = binary.charCodeAt(j);
                                var file = new File([arr], 'video.mp4', {{type: 'video/mp4'}});
                                var dt = new DataTransfer();
                                dt.items.add(file);
                                inputs[i].files = dt.files;
                                inputs[i].dispatchEvent(new Event('change', {{bubbles: true}}));
                                return 'uploaded';
                            }}
                        }}
                        return 'not_found';
                    }})()
                    """,
                )
                if js_result.get("result") != "uploaded":
                    await self._screenshot(session_id, "upload_failed")
                    result["error"] = "Could not find video file input"
                    result["step"] = "upload_failed"
                    return result

            await self._wait(5)  # Wait for video processing
            result["step"] = "video_uploaded"

            # --- Build caption with hashtags ---
            full_caption = caption
            if hashtags:
                tag_str = " ".join(
                    f"#{t.lstrip('#')}" for t in hashtags
                )
                full_caption = f"{caption} {tag_str}"
            # Enforce 2200 char limit
            full_caption = full_caption[:2200]

            # --- Type caption (8 selectors + JS fallback) ---
            caption_selectors = [
                "[data-e2e='caption-editor'] [contenteditable='true']",
                "[data-e2e='video-description'] [contenteditable='true']",
                ".caption-editor [contenteditable='true']",
                "[class*='caption'] [contenteditable='true']",
                "[class*='DraftEditor'] [contenteditable='true']",
                "[role='textbox'][contenteditable='true']",
                ".notranslate[contenteditable='true']",
                "[data-text='true']",
            ]

            typed = await self._try_type(session_id, caption_selectors, full_caption)

            if not typed:
                js_result = await self._evaluate(
                    session_id,
                    f"""
                    (function() {{
                        var editors = document.querySelectorAll('[contenteditable="true"]');
                        for (var i = 0; i < editors.length; i++) {{
                            var ed = editors[i];
                            if (ed.closest('[class*="caption"]') ||
                                ed.closest('[class*="description"]') ||
                                ed.closest('[class*="DraftEditor"]') ||
                                ed.getAttribute('data-text') === 'true') {{
                                ed.focus();
                                document.execCommand('insertText', false, {json.dumps(full_caption)});
                                return 'typed';
                            }}
                        }}
                        return 'not_found';
                    }})()
                    """,
                )
                if js_result.get("result") != "typed":
                    await self._screenshot(session_id, "caption_type_failed")
                    result["error"] = "Could not type caption"
                    result["step"] = "caption_type_failed"
                    return result

            await self._wait(1)
            result["step"] = "caption_typed"

            # --- Take screenshot of draft ---
            await self._screenshot(session_id, "tiktok_draft_ready")

            result["status"] = "draft_ready"
            result["session_id"] = session_id
            result["caption_preview"] = full_caption[:200]
            return result

        except Exception as e:
            logger.exception("post_video error")
            result["error"] = str(e)
            await self._screenshot(session_id, "post_video_exception")
            return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 2: confirm_post                                            #
    # ------------------------------------------------------------------ #

    async def confirm_post(self, session_id: str) -> Dict[str, Any]:
        """Confirm and publish a previously drafted TikTok video.

        Clicks the Post button, waits for upload confirmation, screenshots.
        """
        result = self._result_template("tiktok")

        try:
            # --- Click Post button (6 selectors + JS fallback) ---
            post_selectors = [
                "[data-e2e='upload-btn']",
                "button:has-text('Post')",
                "[class*='post-button']",
                "[class*='btn-post']",
                "button[class*='submit']",
                "[data-e2e='post-button']",
            ]

            clicked = await self._try_click(session_id, post_selectors)

            if not clicked:
                js_result = await self._evaluate(
                    session_id,
                    """
                    (function() {
                        var btns = document.querySelectorAll('button, [role="button"]');
                        for (var i = 0; i < btns.length; i++) {
                            var text = (btns[i].textContent || '').trim().toLowerCase();
                            if (text === 'post' || text === 'upload' || text === 'publish') {
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
                    result["error"] = "Could not find Post/Upload/Publish button"
                    result["step"] = "post_button_missing"
                    return result

            await self._wait(5)  # TikTok processing time

            await self._screenshot(session_id, "tiktok_post_confirmed")

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
    #  ENDPOINT 3: feed_scan                                               #
    # ------------------------------------------------------------------ #

    async def feed_scan(
        self,
        session_id: str,
        feed_url: str = "https://www.tiktok.com/foryou",
        max_posts: int = 10,
    ) -> Dict[str, Any]:
        """Scan TikTok For You Page or a profile feed for post data.

        Returns list of post objects with descriptions, likes, comments,
        shares, and video URLs.
        """
        result: Dict[str, Any] = {"status": "failed", "posts": [], "error": None,
                                   "platform": "tiktok"}

        try:
            await self._navigate(session_id, feed_url)
            await self._wait(4)

            # Scroll to load content
            for _ in range(3):
                await self._evaluate(session_id, "window.scrollBy(0, 800); void(0);")
                await self._wait(1.5)

            # --- Extract posts via JS ---
            posts_data = await self._evaluate(
                session_id,
                f"""
                (function() {{
                    var posts = [];
                    var items = document.querySelectorAll(
                        '[data-e2e="recommend-list-item-container"], ' +
                        '[data-e2e="user-post-item"], ' +
                        '[class*="DivItemContainer"], ' +
                        '[class*="video-feed-item"]'
                    );
                    var limit = Math.min(items.length, {max_posts});
                    for (var i = 0; i < limit; i++) {{
                        var item = items[i];
                        var descEl = item.querySelector(
                            '[data-e2e="video-desc"], [class*="video-meta-caption"], ' +
                            '[class*="tiktok-j2a19r"]'
                        );
                        var likesEl = item.querySelector(
                            '[data-e2e="like-count"], [class*="like-count"]'
                        );
                        var commentsEl = item.querySelector(
                            '[data-e2e="comment-count"], [class*="comment-count"]'
                        );
                        var sharesEl = item.querySelector(
                            '[data-e2e="share-count"], [class*="share-count"]'
                        );
                        var linkEl = item.querySelector('a[href*="/video/"]');
                        var authorEl = item.querySelector(
                            '[data-e2e="video-author-uniqueid"], ' +
                            'a[href*="/@"]'
                        );
                        posts.push({{
                            description: descEl ? descEl.textContent.substring(0, 300) : '',
                            likes: likesEl ? likesEl.textContent.trim() : '0',
                            comments: commentsEl ? commentsEl.textContent.trim() : '0',
                            shares: sharesEl ? sharesEl.textContent.trim() : '0',
                            url: linkEl ? linkEl.href : '',
                            author: authorEl ? authorEl.textContent.trim() : ''
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

            await self._screenshot(session_id, "tiktok_feed_scan_complete")
            result["status"] = "scanned"
            result["count"] = len(result["posts"])

        except Exception as e:
            logger.exception("feed_scan error")
            result["error"] = str(e)
            await self._screenshot(session_id, "feed_scan_exception")
        finally:
            await self._close_session(session_id)

        return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 4: engage  (like, comment, share, follow)                  #
    # ------------------------------------------------------------------ #

    async def engage(
        self,
        session_id: str,
        post_url: str,
        action: str,
        comment_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Engage with a TikTok post: like, comment, share, or follow.

        Args:
            session_id: Active BaaS session ID.
            post_url: Full URL of the TikTok video.
            action: One of 'like', 'comment', 'share', 'follow'.
            comment_text: Required when action is 'comment'.
        """
        result = self._result_template("tiktok")
        result["action"] = action

        try:
            await self._navigate(session_id, post_url)
            await self._wait(3)
            result["step"] = "navigated"

            if action == "like":
                like_selectors = [
                    "[data-e2e='like-icon']",
                    ".like-icon-wrapper",
                    "[data-e2e='browse-like-icon']",
                    "[class*='like-button']",
                    "span[data-e2e='like-icon'] svg",
                    "[class*='DivActionItemContainer']:first-child",
                ]
                clicked = await self._try_click(session_id, like_selectors)
                if not clicked:
                    js_result = await self._evaluate(
                        session_id,
                        """
                        (function() {
                            var els = document.querySelectorAll(
                                '[data-e2e*="like"], [class*="like"]'
                            );
                            for (var i = 0; i < els.length; i++) {
                                if (els[i].closest('button') || els[i].tagName === 'BUTTON' ||
                                    els[i].closest('[role="button"]')) {
                                    (els[i].closest('button') || els[i]).click();
                                    return 'clicked';
                                }
                            }
                            return 'not_found';
                        })()
                        """,
                    )
                    if js_result.get("result") != "clicked":
                        result["error"] = "Could not find like button"
                        result["step"] = "like_failed"
                        await self._screenshot(session_id, "like_failed")
                        return result
                await self._wait(1)
                result["status"] = "liked"
                result["step"] = "liked"

            elif action == "comment":
                if not comment_text:
                    result["error"] = "comment_text is required for comment action"
                    return result

                # Click comment input
                comment_selectors = [
                    "[data-e2e='comment-input']",
                    "textarea[placeholder*='comment' i]",
                    "[data-e2e='browse-comment-input']",
                    "[class*='comment-input'] textarea",
                    "[class*='DivCommentInput'] [contenteditable='true']",
                    "[class*='comment'] textarea",
                ]
                clicked = await self._try_click(session_id, comment_selectors)
                if not clicked:
                    await self._evaluate(
                        session_id,
                        """
                        (function() {
                            var els = document.querySelectorAll(
                                'textarea, [contenteditable="true"]'
                            );
                            for (var i = 0; i < els.length; i++) {
                                var ph = (els[i].placeholder || '').toLowerCase();
                                var label = (els[i].getAttribute('aria-label') || '').toLowerCase();
                                if (ph.indexOf('comment') !== -1 || label.indexOf('comment') !== -1) {
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

                # Type comment
                type_selectors = [
                    "[data-e2e='comment-input']",
                    "textarea[placeholder*='comment' i]",
                    "[data-e2e='browse-comment-input']",
                    "[class*='comment-input'] textarea",
                    "[class*='DivCommentInput'] [contenteditable='true']",
                    "[class*='comment'] textarea",
                ]
                typed = await self._try_type(session_id, type_selectors, comment_text)
                if not typed:
                    js_result = await self._evaluate(
                        session_id,
                        f"""
                        (function() {{
                            var els = document.querySelectorAll(
                                'textarea, [contenteditable="true"]'
                            );
                            for (var i = 0; i < els.length; i++) {{
                                var ph = (els[i].placeholder || '').toLowerCase();
                                if (ph.indexOf('comment') !== -1) {{
                                    els[i].focus();
                                    els[i].value = {json.dumps(comment_text)};
                                    els[i].dispatchEvent(new Event('input', {{bubbles: true}}));
                                    return 'typed';
                                }}
                            }}
                            return 'not_found';
                        }})()
                        """,
                    )
                    if js_result.get("result") != "typed":
                        result["error"] = "Could not type comment"
                        result["step"] = "comment_type_failed"
                        await self._screenshot(session_id, "comment_type_failed")
                        return result

                await self._wait(1)

                # Submit comment (Enter key or Post button)
                submit_selectors = [
                    "[data-e2e='comment-post']",
                    "[class*='comment-post']",
                    "button:has-text('Post')",
                    "[class*='DivPostButton']",
                ]
                submitted = await self._try_click(session_id, submit_selectors)
                if not submitted:
                    await self._evaluate(
                        session_id,
                        """
                        (function() {
                            var active = document.activeElement;
                            if (active) {
                                var ev = new KeyboardEvent('keydown', {
                                    key: 'Enter', code: 'Enter',
                                    keyCode: 13, which: 13, bubbles: true
                                });
                                active.dispatchEvent(ev);
                            }
                        })()
                        """,
                    )
                await self._wait(2)
                result["status"] = "commented"
                result["step"] = "comment_submitted"
                result["comment_preview"] = comment_text[:100]

            elif action == "share":
                share_selectors = [
                    "[data-e2e='share-icon']",
                    "[class*='share-icon']",
                    "[data-e2e='browse-share-icon']",
                    "[class*='DivShareIcon']",
                    "[aria-label='Share']",
                    "[class*='share-button']",
                ]
                clicked = await self._try_click(session_id, share_selectors)
                if not clicked:
                    js_result = await self._evaluate(
                        session_id,
                        """
                        (function() {
                            var els = document.querySelectorAll(
                                '[data-e2e*="share"], [class*="share"]'
                            );
                            for (var i = 0; i < els.length; i++) {
                                if (els[i].closest('button') || els[i].tagName === 'BUTTON') {
                                    (els[i].closest('button') || els[i]).click();
                                    return 'clicked';
                                }
                            }
                            return 'not_found';
                        })()
                        """,
                    )
                    if js_result.get("result") != "clicked":
                        result["error"] = "Could not find share button"
                        result["step"] = "share_failed"
                        return result
                await self._wait(1)
                result["status"] = "shared"
                result["step"] = "share_opened"

            elif action == "follow":
                follow_selectors = [
                    "[data-e2e='follow-button']",
                    "[class*='follow-button']",
                    "button:has-text('Follow')",
                    "[data-e2e='browse-follow-button']",
                    "[class*='DivFollowButton']",
                    "[class*='FollowButton']",
                ]
                clicked = await self._try_click(session_id, follow_selectors)
                if not clicked:
                    js_result = await self._evaluate(
                        session_id,
                        """
                        (function() {
                            var btns = document.querySelectorAll('button, [role="button"]');
                            for (var i = 0; i < btns.length; i++) {
                                var text = (btns[i].textContent || '').trim();
                                if (text === 'Follow') {
                                    btns[i].click();
                                    return 'clicked';
                                }
                            }
                            return 'not_found';
                        })()
                        """,
                    )
                    if js_result.get("result") != "clicked":
                        result["error"] = "Could not find follow button"
                        result["step"] = "follow_failed"
                        return result
                await self._wait(1)
                result["status"] = "followed"
                result["step"] = "followed"
            else:
                result["error"] = f"Unknown action: {action}. Use like/comment/share/follow."
                return result

            await self._screenshot(session_id, f"tiktok_{action}_complete")
            result["timestamp"] = time.time()

        except Exception as e:
            logger.exception("engage error")
            result["error"] = str(e)
            await self._screenshot(session_id, "engage_exception")
        finally:
            await self._close_session(session_id)

        return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 5: profile_scan                                            #
    # ------------------------------------------------------------------ #

    async def profile_scan(
        self,
        session_id: str,
        profile_url: str,
    ) -> Dict[str, Any]:
        """Scan a TikTok profile for follower count, following, likes, and bio."""
        result: Dict[str, Any] = {
            "status": "failed", "profile": {}, "error": None,
            "platform": "tiktok",
        }

        try:
            await self._navigate(session_id, profile_url)
            await self._wait(3)

            profile_data = await self._evaluate(
                session_id,
                """
                (function() {
                    var profile = {};

                    // Username
                    var nameEl = document.querySelector(
                        '[data-e2e="user-title"], [class*="ShareTitle"], h1, h2[class*="user"]'
                    );
                    profile.username = nameEl ? nameEl.textContent.trim() : '';

                    // Bio
                    var bioEl = document.querySelector(
                        '[data-e2e="user-bio"], [class*="ShareDesc"], [class*="user-bio"]'
                    );
                    profile.bio = bioEl ? bioEl.textContent.trim().substring(0, 500) : '';

                    // Follower count
                    var followersEl = document.querySelector(
                        '[data-e2e="followers-count"], [title="Followers"]'
                    );
                    profile.followers = followersEl ? followersEl.textContent.trim() : '0';

                    // Following count
                    var followingEl = document.querySelector(
                        '[data-e2e="following-count"], [title="Following"]'
                    );
                    profile.following = followingEl ? followingEl.textContent.trim() : '0';

                    // Likes count
                    var likesEl = document.querySelector(
                        '[data-e2e="likes-count"], [title="Likes"]'
                    );
                    profile.likes = likesEl ? likesEl.textContent.trim() : '0';

                    // Verified badge
                    var verifiedEl = document.querySelector(
                        '[data-e2e="verify-badge"], [class*="verified"], svg[class*="verified"]'
                    );
                    profile.verified = !!verifiedEl;

                    return JSON.stringify(profile);
                })()
                """,
            )

            try:
                parsed = json.loads(profile_data.get("result", "{}"))
                result["profile"] = parsed if isinstance(parsed, dict) else {}
            except (json.JSONDecodeError, TypeError):
                result["profile"] = {}

            await self._screenshot(session_id, "tiktok_profile_scan_complete")
            result["status"] = "scanned"

        except Exception as e:
            logger.exception("profile_scan error")
            result["error"] = str(e)
            await self._screenshot(session_id, "profile_scan_exception")
        finally:
            await self._close_session(session_id)

        return result


# ====================================================================== #
#  Reddit Adapter                                                          #
# ====================================================================== #


class RedditAdapter(_BaaSBase):
    """Reddit automation via PureSurf BaaS browser automation.

    Targets New Reddit UI (not old.reddit.com).
    Includes rate limiting awareness for bot detection avoidance.
    """

    def __init__(self, api_key: str, profile_name: str = "reddit-purebrain"):
        super().__init__(api_key, profile_name)

    # ------------------------------------------------------------------ #
    #  ENDPOINT 1: post  (text, link, or image)                            #
    # ------------------------------------------------------------------ #

    async def post(
        self,
        session_id: str,
        subreddit: str,
        title: str,
        body: str = "",
        post_type: str = "text",
        link_url: Optional[str] = None,
        image_base64: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a post in a subreddit.

        Args:
            session_id: Active BaaS session ID.
            subreddit: Subreddit name (without r/ prefix).
            title: Post title.
            body: Post body text (for text posts).
            post_type: One of 'text', 'link', 'image'.
            link_url: URL for link posts.
            image_base64: Base64-encoded image for image posts.
        """
        result = self._result_template("reddit")

        try:
            # Navigate to subreddit submit page
            submit_url = f"https://www.reddit.com/r/{subreddit}/submit"
            await self._navigate(session_id, submit_url)
            await self._wait(4)
            result["step"] = "navigated"

            # --- Login gate ---
            content = await self._get_content(session_id)
            page_html = content.get("content", "")
            current_url = content.get("url", "")
            if "login" in current_url.lower() or "Log In" in page_html[:3000]:
                await self._screenshot(session_id, "login_required")
                result["error"] = (
                    "Not logged in. Authenticate the Reddit profile first via "
                    "BaaS cookie import or manual login."
                )
                result["step"] = "login_required"
                return result

            # --- Select post type tab ---
            if post_type == "link":
                tab_selectors = [
                    "button:has-text('Link')",
                    "[role='tab']:has-text('Link')",
                    "[data-click-id='link']",
                    "a[href*='/submit?type=link']",
                ]
                await self._try_click(session_id, tab_selectors)
                await self._wait(1)
            elif post_type == "image":
                tab_selectors = [
                    "button:has-text('Images & Video')",
                    "[role='tab']:has-text('Image')",
                    "[data-click-id='image']",
                    "a[href*='/submit?type=image']",
                ]
                await self._try_click(session_id, tab_selectors)
                await self._wait(1)

            # --- Type title (6 selectors + JS fallback) ---
            title_selectors = [
                "textarea[placeholder*='title' i]",
                "[data-click-id='title'] textarea",
                "input[name='title']",
                "[class*='title'] textarea",
                "[aria-label*='title' i]",
                "textarea[maxlength='300']",
            ]
            typed = await self._try_type(session_id, title_selectors, title)
            if not typed:
                js_result = await self._evaluate(
                    session_id,
                    f"""
                    (function() {{
                        var els = document.querySelectorAll('textarea, input[type="text"]');
                        for (var i = 0; i < els.length; i++) {{
                            var ph = (els[i].placeholder || '').toLowerCase();
                            var name = (els[i].name || '').toLowerCase();
                            if (ph.indexOf('title') !== -1 || name === 'title') {{
                                els[i].focus();
                                els[i].value = {json.dumps(title)};
                                els[i].dispatchEvent(new Event('input', {{bubbles: true}}));
                                return 'typed';
                            }}
                        }}
                        return 'not_found';
                    }})()
                    """,
                )
                if js_result.get("result") != "typed":
                    await self._screenshot(session_id, "title_type_failed")
                    result["error"] = "Could not type post title"
                    result["step"] = "title_type_failed"
                    return result

            await self._wait(1)
            result["step"] = "title_typed"

            # --- Type body / link / upload image ---
            if post_type == "text" and body:
                body_selectors = [
                    "[data-click-id='text'] [contenteditable='true']",
                    "[class*='RichTextJSON'] [contenteditable='true']",
                    "div[contenteditable='true'][role='textbox']",
                    "[class*='notranslate'][contenteditable='true']",
                    "textarea[placeholder*='text' i]",
                    "[class*='post-body'] [contenteditable='true']",
                ]
                typed = await self._try_type(session_id, body_selectors, body)
                if not typed:
                    js_result = await self._evaluate(
                        session_id,
                        f"""
                        (function() {{
                            var editors = document.querySelectorAll(
                                '[contenteditable="true"], textarea'
                            );
                            for (var i = 0; i < editors.length; i++) {{
                                var ed = editors[i];
                                var ph = (ed.placeholder || '').toLowerCase();
                                if (ph.indexOf('text') !== -1 ||
                                    ed.closest('[class*="RichText"]') ||
                                    ed.getAttribute('role') === 'textbox') {{
                                    ed.focus();
                                    document.execCommand('insertText', false, {json.dumps(body)});
                                    return 'typed';
                                }}
                            }}
                            return 'not_found';
                        }})()
                        """,
                    )
                result["step"] = "body_typed"

            elif post_type == "link" and link_url:
                link_selectors = [
                    "input[placeholder*='url' i]",
                    "textarea[placeholder*='url' i]",
                    "input[name='url']",
                    "[data-click-id='url'] input",
                ]
                typed = await self._try_type(session_id, link_selectors, link_url)
                if not typed:
                    await self._evaluate(
                        session_id,
                        f"""
                        (function() {{
                            var inputs = document.querySelectorAll('input, textarea');
                            for (var i = 0; i < inputs.length; i++) {{
                                var ph = (inputs[i].placeholder || '').toLowerCase();
                                if (ph.indexOf('url') !== -1 || ph.indexOf('link') !== -1) {{
                                    inputs[i].focus();
                                    inputs[i].value = {json.dumps(link_url)};
                                    inputs[i].dispatchEvent(new Event('input', {{bubbles: true}}));
                                    return 'typed';
                                }}
                            }}
                            return 'not_found';
                        }})()
                        """,
                    )
                result["step"] = "link_typed"

            elif post_type == "image" and image_base64:
                await self._evaluate(
                    session_id,
                    f"""
                    (function() {{
                        var input = document.querySelector(
                            'input[type="file"][accept*="image"], input[type="file"]'
                        );
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
                        return 'not_found';
                    }})()
                    """,
                )
                await self._wait(2)
                result["step"] = "image_uploaded"

            await self._wait(1)

            # --- Click submit (6 selectors + JS fallback) ---
            submit_selectors = [
                "button[type='submit']",
                "[data-click-id='submit']",
                "button:has-text('Post')",
                "button:has-text('Submit')",
                "[class*='submit'] button",
                "[class*='Post'] button[type='submit']",
            ]
            clicked = await self._try_click(session_id, submit_selectors)
            if not clicked:
                js_result = await self._evaluate(
                    session_id,
                    """
                    (function() {
                        var btns = document.querySelectorAll('button');
                        for (var i = 0; i < btns.length; i++) {
                            var text = (btns[i].textContent || '').trim().toLowerCase();
                            if (text === 'post' || text === 'submit') {
                                btns[i].click();
                                return 'clicked';
                            }
                        }
                        return 'not_found';
                    })()
                    """,
                )
                if js_result.get("result") != "clicked":
                    await self._screenshot(session_id, "submit_failed")
                    result["error"] = "Could not find submit button"
                    result["step"] = "submit_failed"
                    return result

            await self._wait(3)
            await self._screenshot(session_id, "reddit_post_submitted")

            result["status"] = "posted"
            result["step"] = "submitted"
            result["subreddit"] = subreddit
            result["title_preview"] = title[:100]
            result["timestamp"] = time.time()

        except Exception as e:
            logger.exception("post error")
            result["error"] = str(e)
            await self._screenshot(session_id, "post_exception")
        finally:
            await self._close_session(session_id)

        return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 2: comment                                                 #
    # ------------------------------------------------------------------ #

    async def comment(
        self,
        session_id: str,
        post_url: str,
        comment_text: str,
    ) -> Dict[str, Any]:
        """Comment on a Reddit post."""
        result = self._result_template("reddit")

        try:
            await self._navigate(session_id, post_url)
            await self._wait(3)
            result["step"] = "navigated"

            # --- Click comment box (6 selectors + JS fallback) ---
            comment_click_selectors = [
                "[data-click-id='text'] [contenteditable='true']",
                "[class*='comment'] [contenteditable='true']",
                "div[contenteditable='true'][role='textbox']",
                "[placeholder*='comment' i]",
                "[class*='RichTextJSON'] [contenteditable='true']",
                "textarea[placeholder*='thoughts' i]",
            ]
            clicked = await self._try_click(session_id, comment_click_selectors)
            if not clicked:
                await self._evaluate(
                    session_id,
                    """
                    (function() {
                        var editors = document.querySelectorAll(
                            '[contenteditable="true"], textarea'
                        );
                        for (var i = 0; i < editors.length; i++) {
                            var ph = (editors[i].placeholder || '').toLowerCase();
                            var label = (editors[i].getAttribute('aria-label') || '').toLowerCase();
                            if (ph.indexOf('thought') !== -1 || ph.indexOf('comment') !== -1 ||
                                label.indexOf('comment') !== -1) {
                                editors[i].click();
                                editors[i].focus();
                                return 'clicked';
                            }
                        }
                        return 'not_found';
                    })()
                    """,
                )
            await self._wait(1)
            result["step"] = "comment_box_opened"

            # --- Type comment (6 selectors + JS fallback) ---
            type_selectors = [
                "[data-click-id='text'] [contenteditable='true']",
                "[class*='comment'] [contenteditable='true']",
                "div[contenteditable='true'][role='textbox']",
                "[class*='RichTextJSON'] [contenteditable='true']",
                "textarea[placeholder*='thoughts' i]",
                "textarea[placeholder*='comment' i]",
            ]
            typed = await self._try_type(session_id, type_selectors, comment_text)
            if not typed:
                js_result = await self._evaluate(
                    session_id,
                    f"""
                    (function() {{
                        var editors = document.querySelectorAll(
                            '[contenteditable="true"], textarea'
                        );
                        for (var i = 0; i < editors.length; i++) {{
                            var ed = editors[i];
                            if (ed.getAttribute('role') === 'textbox' ||
                                ed.closest('[class*="comment"]')) {{
                                ed.focus();
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
                    result["error"] = "Could not type comment"
                    result["step"] = "comment_type_failed"
                    return result

            await self._wait(1)
            result["step"] = "comment_typed"

            # --- Submit comment (5 selectors + JS fallback) ---
            submit_selectors = [
                "button[type='submit']:has-text('Comment')",
                "button:has-text('Comment')",
                "[data-click-id='submit']",
                "[class*='comment-submit'] button",
                "button[type='submit']",
            ]
            clicked = await self._try_click(session_id, submit_selectors)
            if not clicked:
                await self._evaluate(
                    session_id,
                    """
                    (function() {
                        var btns = document.querySelectorAll('button');
                        for (var i = 0; i < btns.length; i++) {
                            var text = (btns[i].textContent || '').trim().toLowerCase();
                            if (text === 'comment' || text === 'reply') {
                                btns[i].click();
                                return 'clicked';
                            }
                        }
                        return 'not_found';
                    })()
                    """,
                )

            await self._wait(2)
            await self._screenshot(session_id, "reddit_comment_submitted")

            result["status"] = "commented"
            result["step"] = "submitted"
            result["comment_preview"] = comment_text[:100]
            result["timestamp"] = time.time()

        except Exception as e:
            logger.exception("comment error")
            result["error"] = str(e)
            await self._screenshot(session_id, "comment_exception")
        finally:
            await self._close_session(session_id)

        return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 3: upvote                                                  #
    # ------------------------------------------------------------------ #

    async def upvote(
        self,
        session_id: str,
        post_url: str,
    ) -> Dict[str, Any]:
        """Upvote a Reddit post."""
        result = self._result_template("reddit")

        try:
            await self._navigate(session_id, post_url)
            await self._wait(3)
            result["step"] = "navigated"

            upvote_selectors = [
                "[aria-label='upvote']",
                "button.upvote",
                "[data-click-id='upvote']",
                "[class*='voteButton'][aria-label='upvote']",
                "button[aria-label='Upvote']",
                "[class*='icon-upvote']",
            ]
            clicked = await self._try_click(session_id, upvote_selectors)
            if not clicked:
                js_result = await self._evaluate(
                    session_id,
                    """
                    (function() {
                        var btns = document.querySelectorAll('button');
                        for (var i = 0; i < btns.length; i++) {
                            var label = (btns[i].getAttribute('aria-label') || '').toLowerCase();
                            if (label === 'upvote') {
                                btns[i].click();
                                return 'clicked';
                            }
                        }
                        // Fallback: find upvote by class
                        var upvotes = document.querySelectorAll(
                            '[class*="upvote"], [class*="UpVote"]'
                        );
                        for (var j = 0; j < upvotes.length; j++) {
                            var el = upvotes[j].closest('button') || upvotes[j];
                            el.click();
                            return 'clicked';
                        }
                        return 'not_found';
                    })()
                    """,
                )
                if js_result.get("result") != "clicked":
                    await self._screenshot(session_id, "upvote_failed")
                    result["error"] = "Could not find upvote button"
                    result["step"] = "upvote_failed"
                    return result

            await self._wait(1)
            await self._screenshot(session_id, "reddit_upvote_complete")

            result["status"] = "upvoted"
            result["step"] = "upvoted"
            result["timestamp"] = time.time()

        except Exception as e:
            logger.exception("upvote error")
            result["error"] = str(e)
            await self._screenshot(session_id, "upvote_exception")
        finally:
            await self._close_session(session_id)

        return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 4: feed_scan                                               #
    # ------------------------------------------------------------------ #

    async def feed_scan(
        self,
        session_id: str,
        subreddit: str = "all",
        sort: str = "hot",
        max_posts: int = 10,
    ) -> Dict[str, Any]:
        """Scan a subreddit feed for posts.

        Args:
            session_id: Active BaaS session ID.
            subreddit: Subreddit name (without r/).
            sort: Sort method: hot, new, top, rising.
            max_posts: Maximum posts to extract.
        """
        result: Dict[str, Any] = {"status": "failed", "posts": [], "error": None,
                                   "platform": "reddit"}

        try:
            feed_url = f"https://www.reddit.com/r/{subreddit}/{sort}/"
            await self._navigate(session_id, feed_url)
            await self._wait(4)

            # Scroll to load content
            for _ in range(2):
                await self._evaluate(session_id, "window.scrollBy(0, 1500); void(0);")
                await self._wait(2)

            posts_data = await self._evaluate(
                session_id,
                f"""
                (function() {{
                    var posts = [];
                    var items = document.querySelectorAll(
                        '[data-testid="post-container"], ' +
                        'shreddit-post, ' +
                        '[class*="Post"][data-click-id="body"], ' +
                        'article, ' +
                        '[data-fullpage-card]'
                    );
                    var limit = Math.min(items.length, {max_posts});
                    for (var i = 0; i < limit; i++) {{
                        var item = items[i];
                        var titleEl = item.querySelector(
                            'h3, [data-click-id="body"] h3, ' +
                            '[slot="title"], [class*="title"]'
                        );
                        var authorEl = item.querySelector(
                            '[data-click-id="user"], [data-testid="post_author_link"], ' +
                            'a[href*="/user/"]'
                        );
                        var scoreEl = item.querySelector(
                            '[data-click-id="upvote"] + div, ' +
                            '[class*="score"], [class*="vote"]'
                        );
                        var commentsEl = item.querySelector(
                            '[data-click-id="comments"], a[href*="/comments/"]'
                        );
                        var linkEl = item.querySelector(
                            'a[data-click-id="body"], a[href*="/comments/"]'
                        );
                        var flairEl = item.querySelector(
                            '[class*="flair"], [data-testid="flair"]'
                        );
                        posts.push({{
                            title: titleEl ? titleEl.textContent.substring(0, 300) : '',
                            author: authorEl ? authorEl.textContent.trim() : '',
                            score: scoreEl ? scoreEl.textContent.trim() : '0',
                            comments: commentsEl ? commentsEl.textContent.trim() : '0',
                            url: linkEl ? linkEl.href : '',
                            flair: flairEl ? flairEl.textContent.trim() : ''
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

            await self._screenshot(session_id, "reddit_feed_scan_complete")
            result["status"] = "scanned"
            result["count"] = len(result["posts"])
            result["subreddit"] = subreddit
            result["sort"] = sort

        except Exception as e:
            logger.exception("feed_scan error")
            result["error"] = str(e)
            await self._screenshot(session_id, "feed_scan_exception")
        finally:
            await self._close_session(session_id)

        return result

    # ------------------------------------------------------------------ #
    #  ENDPOINT 5: profile_check                                           #
    # ------------------------------------------------------------------ #

    async def profile_check(
        self,
        session_id: str,
        username: str,
    ) -> Dict[str, Any]:
        """Check a Reddit user profile for karma, post history, and account info."""
        result: Dict[str, Any] = {
            "status": "failed", "profile": {}, "error": None,
            "platform": "reddit",
        }

        try:
            profile_url = f"https://www.reddit.com/user/{username}/"
            await self._navigate(session_id, profile_url)
            await self._wait(3)

            profile_data = await self._evaluate(
                session_id,
                """
                (function() {
                    var profile = {};

                    // Username
                    var nameEl = document.querySelector(
                        'h1, [data-testid="profile-header"] h1, ' +
                        '[class*="ProfileHeader"] h1'
                    );
                    profile.username = nameEl ? nameEl.textContent.trim() : '';

                    // Karma (post + comment)
                    var karmaEls = document.querySelectorAll(
                        '[data-testid="karma"], [class*="karma"], ' +
                        '[id*="karma"]'
                    );
                    if (karmaEls.length >= 2) {
                        profile.post_karma = karmaEls[0].textContent.trim();
                        profile.comment_karma = karmaEls[1].textContent.trim();
                    } else if (karmaEls.length === 1) {
                        profile.total_karma = karmaEls[0].textContent.trim();
                    }

                    // Fallback: search for karma text in page
                    var allText = document.body.innerText || '';
                    var karmaMatch = allText.match(/(\\d[\\d,\\.]*K?)\\s*karma/i);
                    if (karmaMatch && !profile.total_karma) {
                        profile.total_karma = karmaMatch[1];
                    }

                    // Account age / cake day
                    var cakeEl = document.querySelector(
                        '[id*="cake-day"], [class*="cakeDay"], ' +
                        '[data-testid="cake-day"]'
                    );
                    profile.cake_day = cakeEl ? cakeEl.textContent.trim() : '';

                    // Bio / about
                    var bioEl = document.querySelector(
                        '[class*="about"], [data-testid="profile-description"], ' +
                        '[class*="ProfileBio"]'
                    );
                    profile.bio = bioEl ? bioEl.textContent.trim().substring(0, 500) : '';

                    // Recent posts count (visible on page)
                    var postEls = document.querySelectorAll(
                        '[data-testid="post-container"], shreddit-post, article'
                    );
                    profile.visible_posts = postEls.length;

                    return JSON.stringify(profile);
                })()
                """,
            )

            try:
                parsed = json.loads(profile_data.get("result", "{}"))
                result["profile"] = parsed if isinstance(parsed, dict) else {}
            except (json.JSONDecodeError, TypeError):
                result["profile"] = {}

            await self._screenshot(session_id, "reddit_profile_check_complete")
            result["status"] = "scanned"

        except Exception as e:
            logger.exception("profile_check error")
            result["error"] = str(e)
            await self._screenshot(session_id, "profile_check_exception")
        finally:
            await self._close_session(session_id)

        return result


# ====================================================================== #
#  FastAPI Router Extensions                                               #
# ====================================================================== #


def extend_tiktok_router(router, sessions: dict, auth_check):
    """Add TikTok endpoints to an existing social-suite router.

    Usage:
        from puresurf_tiktok_reddit_adapters import extend_tiktok_router
        extend_tiktok_router(social_router, active_sessions, check_api_key)

    Registers 5 POST routes under /social/adapters/tiktok/*.
    """
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    adapter = TikTokAdapter(api_key="chy-baas-key-001")

    async def tiktok_post_video(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        if not sid:
            return JSONResponse({"error": "session_id is required"}, status_code=400)
        result = await adapter.post_video(
            session_id=sid,
            video_base64=body.get("video_base64", ""),
            caption=body.get("caption", ""),
            hashtags=body.get("hashtags"),
        )
        return JSONResponse(result)

    async def tiktok_confirm_post(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        if not sid:
            return JSONResponse({"error": "session_id is required"}, status_code=400)
        result = await adapter.confirm_post(session_id=sid)
        return JSONResponse(result)

    async def tiktok_feed_scan(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        if not sid:
            return JSONResponse({"error": "session_id is required"}, status_code=400)
        result = await adapter.feed_scan(
            session_id=sid,
            feed_url=body.get("feed_url", "https://www.tiktok.com/foryou"),
            max_posts=body.get("max_posts", 10),
        )
        return JSONResponse(result)

    async def tiktok_engage(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        post_url = body.get("post_url", "")
        action = body.get("action", "")
        if not sid or not post_url or not action:
            return JSONResponse(
                {"error": "session_id, post_url, and action are required"},
                status_code=400,
            )
        result = await adapter.engage(
            session_id=sid,
            post_url=post_url,
            action=action,
            comment_text=body.get("comment_text"),
        )
        return JSONResponse(result)

    async def tiktok_profile_scan(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        profile_url = body.get("profile_url", "")
        if not sid or not profile_url:
            return JSONResponse(
                {"error": "session_id and profile_url are required"},
                status_code=400,
            )
        result = await adapter.profile_scan(
            session_id=sid,
            profile_url=profile_url,
        )
        return JSONResponse(result)

    router.routes.extend(
        [
            Route(
                "/social/adapters/tiktok/post",
                tiktok_post_video,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/tiktok/confirm-post",
                tiktok_confirm_post,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/tiktok/feed-scan",
                tiktok_feed_scan,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/tiktok/engage",
                tiktok_engage,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/tiktok/profile-scan",
                tiktok_profile_scan,
                methods=["POST"],
            ),
        ]
    )


def extend_reddit_router(router, sessions: dict, auth_check):
    """Add Reddit endpoints to an existing social-suite router.

    Usage:
        from puresurf_tiktok_reddit_adapters import extend_reddit_router
        extend_reddit_router(social_router, active_sessions, check_api_key)

    Registers 5 POST routes under /social/adapters/reddit/*.
    """
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    adapter = RedditAdapter(api_key="chy-baas-key-001")

    async def reddit_post(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        subreddit = body.get("subreddit", "")
        title = body.get("title", "")
        if not sid or not subreddit or not title:
            return JSONResponse(
                {"error": "session_id, subreddit, and title are required"},
                status_code=400,
            )
        result = await adapter.post(
            session_id=sid,
            subreddit=subreddit,
            title=title,
            body=body.get("body", ""),
            post_type=body.get("post_type", "text"),
            link_url=body.get("link_url"),
            image_base64=body.get("image_base64"),
        )
        return JSONResponse(result)

    async def reddit_comment(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        post_url = body.get("post_url", "")
        comment_text = body.get("comment_text", "")
        if not sid or not post_url or not comment_text:
            return JSONResponse(
                {"error": "session_id, post_url, and comment_text are required"},
                status_code=400,
            )
        result = await adapter.comment(
            session_id=sid,
            post_url=post_url,
            comment_text=comment_text,
        )
        return JSONResponse(result)

    async def reddit_upvote(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        post_url = body.get("post_url", "")
        if not sid or not post_url:
            return JSONResponse(
                {"error": "session_id and post_url are required"},
                status_code=400,
            )
        result = await adapter.upvote(
            session_id=sid,
            post_url=post_url,
        )
        return JSONResponse(result)

    async def reddit_feed_scan(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        if not sid:
            return JSONResponse({"error": "session_id is required"}, status_code=400)
        result = await adapter.feed_scan(
            session_id=sid,
            subreddit=body.get("subreddit", "all"),
            sort=body.get("sort", "hot"),
            max_posts=body.get("max_posts", 10),
        )
        return JSONResponse(result)

    async def reddit_profile_check(request: Request):
        if not auth_check(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        body = await request.json()
        sid = body.get("session_id", "")
        username = body.get("username", "")
        if not sid or not username:
            return JSONResponse(
                {"error": "session_id and username are required"},
                status_code=400,
            )
        result = await adapter.profile_check(
            session_id=sid,
            username=username,
        )
        return JSONResponse(result)

    router.routes.extend(
        [
            Route(
                "/social/adapters/reddit/post",
                reddit_post,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/reddit/comment",
                reddit_comment,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/reddit/upvote",
                reddit_upvote,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/reddit/feed-scan",
                reddit_feed_scan,
                methods=["POST"],
            ),
            Route(
                "/social/adapters/reddit/profile-check",
                reddit_profile_check,
                methods=["POST"],
            ),
        ]
    )


# ====================================================================== #
#  Quick smoke test                                                        #
# ====================================================================== #

if __name__ == "__main__":

    async def test():
        print("=== TikTok Adapter ===")
        tiktok = TikTokAdapter(api_key="test-key")
        print(f"  BaaS URL:  {BAAS_URL}")
        print(f"  Profile:   {tiktok.profile_name}")
        print("  Endpoints: post_video, confirm_post, feed_scan, engage, profile_scan")

        sid = await tiktok._create_session()
        print(f"  Session created: {sid}")
        if sid:
            await tiktok._close_session(sid)
            print("  Session closed")

        print()
        print("=== Reddit Adapter ===")
        reddit = RedditAdapter(api_key="test-key")
        print(f"  BaaS URL:  {BAAS_URL}")
        print(f"  Profile:   {reddit.profile_name}")
        print("  Endpoints: post, comment, upvote, feed_scan, profile_check")

        sid = await reddit._create_session()
        print(f"  Session created: {sid}")
        if sid:
            await reddit._close_session(sid)
            print("  Session closed")

    asyncio.run(test())
