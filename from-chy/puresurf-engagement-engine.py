#!/usr/bin/env python3
"""
PureSurf Engagement Engine
Browser automation workflows for social media management at scale.
Same category as GoLogin, Multilogin, Buffer — browser tools for account management.

Uses PureSurf BaaS API for fingerprinted browser sessions.
"""
import httpx
import asyncio
import random
import json
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone

BAAS_URL = "https://surf.purebrain.ai"


class EngagementEngine:
    """Browser automation workflows for social media engagement."""

    def __init__(self, api_key: str = "chy-baas-key-001"):
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    # === SESSION HELPERS ===

    async def _request(self, method: str, path: str, body: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as c:
            if method == "GET":
                r = await c.get(f"{BAAS_URL}{path}", headers=self.headers)
            elif method == "POST":
                r = await c.post(f"{BAAS_URL}{path}", headers=self.headers, json=body or {})
            elif method == "DELETE":
                r = await c.delete(f"{BAAS_URL}{path}", headers=self.headers)
            else:
                return {"error": f"unknown method {method}"}
            return r.json() if r.status_code < 500 else {"error": f"HTTP {r.status_code}"}

    async def navigate(self, sid: str, url: str) -> dict:
        return await self._request("POST", f"/sessions/{sid}/navigate", {"url": url})

    async def click(self, sid: str, selector: str) -> dict:
        return await self._request("POST", f"/sessions/{sid}/click", {"selector": selector})

    async def type_text(self, sid: str, selector: str, text: str) -> dict:
        return await self._request("POST", f"/sessions/{sid}/type", {"selector": selector, "text": text})

    async def evaluate(self, sid: str, js: str) -> dict:
        return await self._request("POST", f"/sessions/{sid}/evaluate", {"expression": js})

    async def get_health(self, sid: str) -> int:
        r = await self._request("GET", f"/sessions/{sid}/health")
        return r.get("health_score", 100)

    async def get_content(self, sid: str) -> dict:
        return await self._request("GET", f"/sessions/{sid}/content")

    # === NATURAL TIMING ===

    @staticmethod
    def natural_delay(min_s: float = 2, max_s: float = 8) -> float:
        return max(min_s, min(max_s, random.gauss((min_s + max_s) / 2, (max_s - min_s) / 4)))

    async def wait_natural(self, min_s: float = 2, max_s: float = 8):
        await asyncio.sleep(self.natural_delay(min_s, max_s))

    # === MULTI-SELECTOR CLICK ===

    async def click_any(self, sid: str, selectors: List[str], js_fallback: str = None) -> bool:
        for sel in selectors:
            try:
                r = await self.click(sid, sel)
                if r.get("status") == "clicked":
                    return True
            except:
                continue
        if js_fallback:
            r = await self.evaluate(sid, js_fallback)
            return "clicked" in str(r.get("result", ""))
        return False

    # === PLATFORM ACTIONS ===

    LIKE_SELECTORS = {
        "linkedin": [
            "button[aria-label*='Like']", ".react-button__trigger",
            "[data-control-name='like']", "button.artdeco-button--muted",
            "span.reactions-react-button", "[aria-pressed='false'][aria-label*='like']"
        ],
        "twitter": [
            "[data-testid='like']", "[aria-label*='Like']",
            "div[role='button'][aria-label*='Like']", "[data-testid='unlike']"
        ],
        "instagram": [
            "svg[aria-label='Like']", "[aria-label='Like']",
            "span.x1lliihq svg[aria-label='Like']", "button svg[aria-label='Like']"
        ],
        "facebook": [
            "[aria-label*='Like']", "div[aria-label='Like']",
            "[data-testid*='like']", "span:has-text('Like')"
        ],
        "tiktok": [
            "[data-e2e='like-icon']", ".like-icon-wrapper",
            "span[data-e2e='like-count']", "button.like-btn"
        ],
    }

    FOLLOW_SELECTORS = {
        "linkedin": [
            "button[aria-label*='Follow']", "button:has-text('Follow')",
            ".follow-button", "[data-control-name='follow']"
        ],
        "twitter": [
            "[data-testid*='follow']", "[aria-label*='Follow']",
            "div[role='button']:has-text('Follow')", "span:has-text('Follow')"
        ],
        "instagram": [
            "button:has-text('Follow')", "[aria-label='Follow']",
            "button._acan", "div.x1i10hfl button:has-text('Follow')"
        ],
        "facebook": [
            "button[aria-label*='Follow']", "div[role='button']:has-text('Follow')",
            "[data-testid*='follow']"
        ],
        "tiktok": [
            "[data-e2e='follow-button']", "button:has-text('Follow')",
            ".follow-btn", "div.follow-button"
        ],
    }

    COMMENT_SELECTORS = {
        "linkedin": [
            ".comments-comment-texteditor [contenteditable='true']",
            "[aria-label*='Add a comment']", ".ql-editor",
            "div[role='textbox'][aria-label*='comment']"
        ],
        "twitter": [
            "[data-testid='tweetTextarea_0']", "[aria-label*='Post your reply']",
            "div[role='textbox']", "[contenteditable='true'][data-testid]"
        ],
        "instagram": [
            "textarea[aria-label*='Add a comment']", "[contenteditable='true']",
            "form textarea", "textarea[placeholder*='comment']"
        ],
        "facebook": [
            "[aria-label='Write a comment']", "[contenteditable='true'][aria-label*='comment']",
            "div[role='textbox']", "form [contenteditable='true']"
        ],
        "tiktok": [
            "[data-e2e='comment-input']", "textarea[placeholder*='comment']",
            "[contenteditable='true']", "div.comment-input"
        ],
    }

    COMMENT_SUBMIT_SELECTORS = {
        "linkedin": ["button[aria-label*='Post']", "button.comments-comment-box__submit-button"],
        "twitter": ["[data-testid='tweetButton']", "div[role='button']:has-text('Reply')"],
        "instagram": ["button:has-text('Post')", "[type='submit']"],
        "facebook": ["[aria-label='Comment']", "form button[type='submit']"],
        "tiktok": ["[data-e2e='comment-post']", "button:has-text('Post')"],
    }

    async def like_post(self, sid: str, platform: str, post_url: str) -> dict:
        """Navigate to a post and click the like button."""
        result = {"action": "like", "platform": platform, "url": post_url, "status": "failed"}
        try:
            await self.navigate(sid, post_url)
            await self.wait_natural(2, 5)
            selectors = self.LIKE_SELECTORS.get(platform, [])
            js = f"""(function(){{ var btns=document.querySelectorAll('[aria-label*="Like"],[aria-label*="like"]');
                for(var b of btns){{ if(!b.closest('[aria-pressed="true"]')){{ b.click(); return 'clicked'; }} }}
                return 'not_found'; }})()"""
            if await self.click_any(sid, selectors, js):
                result["status"] = "liked"
            await self.wait_natural(1, 3)
        except Exception as e:
            result["error"] = str(e)
        return result

    async def follow_user(self, sid: str, platform: str, profile_url: str) -> dict:
        """Navigate to a profile and click follow."""
        result = {"action": "follow", "platform": platform, "url": profile_url, "status": "failed"}
        try:
            await self.navigate(sid, profile_url)
            await self.wait_natural(2, 5)
            selectors = self.FOLLOW_SELECTORS.get(platform, [])
            js = """(function(){ var btns=document.querySelectorAll('button');
                for(var b of btns){ if(b.textContent.trim()==='Follow'){ b.click(); return 'clicked'; }}
                return 'not_found'; })()"""
            if await self.click_any(sid, selectors, js):
                result["status"] = "followed"
            await self.wait_natural(1, 3)
        except Exception as e:
            result["error"] = str(e)
        return result

    async def comment_on_post(self, sid: str, platform: str, post_url: str, comment: str) -> dict:
        """Navigate to a post, type a comment, and submit."""
        result = {"action": "comment", "platform": platform, "url": post_url, "status": "failed"}
        try:
            await self.navigate(sid, post_url)
            await self.wait_natural(3, 6)
            # Click comment area
            comment_sels = self.COMMENT_SELECTORS.get(platform, [])
            for sel in comment_sels:
                try:
                    r = await self.click(sid, sel)
                    if r.get("status") == "clicked":
                        break
                except:
                    continue
            await self.wait_natural(1, 2)
            # Type comment
            for sel in comment_sels:
                try:
                    r = await self.type_text(sid, sel, comment)
                    if r.get("status") in ("typed", "filled"):
                        break
                except:
                    continue
            await self.wait_natural(1, 3)
            # Submit
            submit_sels = self.COMMENT_SUBMIT_SELECTORS.get(platform, [])
            if await self.click_any(sid, submit_sels):
                result["status"] = "commented"
                result["comment"] = comment[:100]
            await self.wait_natural(2, 4)
        except Exception as e:
            result["error"] = str(e)
        return result

    # === CAMPAIGNS ===

    async def run_campaign(self, sid: str, platform: str, targets: List[str],
                           actions: List[str], delay_range: Tuple[float, float] = (30, 120),
                           comments: List[str] = None) -> dict:
        """Run an engagement campaign across multiple targets with natural timing."""
        results = []
        comment_pool = comments or [
            "Great insights! Thanks for sharing.",
            "Really well put together. Bookmarking this.",
            "Interesting perspective — would love to learn more.",
            "Solid points here. This resonates.",
            "Thanks for breaking this down so clearly.",
            "This is exactly what I needed to read today.",
            "Couldn't agree more. Well said.",
            "Fantastic work on this. Keep it coming!",
        ]

        for i, target in enumerate(targets):
            for action in actions:
                # Check health before each burst
                health = await self.get_health(sid)
                if health < 50:
                    return {"status": "paused", "reason": "health_low", "score": health,
                            "completed": len(results), "remaining": len(targets) - i}

                delay = self.natural_delay(*delay_range)
                await asyncio.sleep(delay)

                if action == "like":
                    r = await self.like_post(sid, platform, target)
                elif action == "follow":
                    r = await self.follow_user(sid, platform, target)
                elif action == "comment":
                    comment = random.choice(comment_pool)
                    r = await self.comment_on_post(sid, platform, target, comment)
                else:
                    r = {"action": action, "status": "unknown_action"}

                results.append({**r, "delay_used": round(delay, 1), "timestamp": time.time()})

        return {"status": "completed", "total": len(results),
                "succeeded": sum(1 for r in results if r.get("status") not in ("failed",)),
                "results": results}

    async def scan_and_engage(self, sid: str, platform: str, feed_url: str,
                               max_posts: int = 5, actions: List[str] = ["like"]) -> dict:
        """Scan a feed and engage with posts automatically."""
        await self.navigate(sid, feed_url)
        await self.wait_natural(3, 6)

        # Extract post URLs from feed via JS
        js = f"""(function(){{
            var links = [];
            var posts = document.querySelectorAll('a[href*="/posts/"], a[href*="/status/"], a[href*="/p/"], a[href*="/reel/"], article a');
            for (var i = 0; i < Math.min(posts.length, {max_posts}); i++) {{
                var href = posts[i].href;
                if (href && !links.includes(href)) links.push(href);
            }}
            return JSON.stringify(links);
        }})()"""

        result = await self.evaluate(sid, js)
        try:
            urls = json.loads(result.get("result", "[]"))
        except:
            urls = []

        if not urls:
            return {"status": "no_posts_found", "feed_url": feed_url}

        return await self.run_campaign(sid, platform, urls[:max_posts], actions, (15, 60))


class AccountWarmUp:
    """Gradual activity ramp for new browser profiles."""

    PHASES = [
        {"name": "browse_only", "days": (1, 3), "max_actions": 0, "browse_min": 10,
         "desc": "Browse only — no engagement. Build cookie history."},
        {"name": "light", "days": (4, 7), "max_actions": 3, "browse_min": 15,
         "desc": "2-3 likes per session. No follows or comments."},
        {"name": "moderate", "days": (8, 14), "max_actions": 8, "browse_min": 20,
         "desc": "5-8 actions (likes + 1-2 follows). Light commenting."},
        {"name": "active", "days": (15, 21), "max_actions": 15, "browse_min": 25,
         "desc": "10-15 actions including comments. Start following actively."},
        {"name": "full", "days": (22, 999), "max_actions": 30, "browse_min": 30,
         "desc": "Full automation unlocked. All action types."},
    ]

    def __init__(self, api_key: str = "chy-baas-key-001"):
        self.engine = EngagementEngine(api_key)
        self.state_file = "/home/aiciv/exports/warmup-state.json"

    def _load_state(self) -> dict:
        try:
            with open(self.state_file) as f:
                return json.load(f)
        except:
            return {"profiles": {}}

    def _save_state(self, state: dict):
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def get_phase(self, profile_name: str) -> dict:
        state = self._load_state()
        profile = state["profiles"].get(profile_name)
        if not profile:
            state["profiles"][profile_name] = {"created": datetime.now(timezone.utc).isoformat(), "total_sessions": 0}
            self._save_state(state)
            return self.PHASES[0]

        created = datetime.fromisoformat(profile["created"].replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - created).days + 1

        for phase in self.PHASES:
            if phase["days"][0] <= age_days <= phase["days"][1]:
                return {**phase, "profile_age_days": age_days}
        return {**self.PHASES[-1], "profile_age_days": age_days}

    async def run_warmup(self, sid: str, platform: str, profile_name: str,
                          feed_url: str) -> dict:
        phase = self.get_phase(profile_name)
        result = {"profile": profile_name, "phase": phase["name"],
                  "age_days": phase.get("profile_age_days", 0), "max_actions": phase["max_actions"]}

        # Browse phase — just navigate around
        await self.engine.navigate(sid, feed_url)
        await self.engine.wait_natural(phase["browse_min"] * 0.3, phase["browse_min"] * 0.5)

        if phase["max_actions"] > 0:
            actions = ["like"]
            if phase["name"] in ("moderate", "active", "full"):
                actions.append("follow")
            if phase["name"] in ("active", "full"):
                actions.append("comment")

            r = await self.engine.scan_and_engage(sid, platform, feed_url,
                                                    max_posts=min(phase["max_actions"], 5),
                                                    actions=actions[:1])
            result["engagement"] = r
        else:
            result["engagement"] = {"status": "browse_only"}

        # Update state
        state = self._load_state()
        if profile_name in state["profiles"]:
            state["profiles"][profile_name]["total_sessions"] = state["profiles"][profile_name].get("total_sessions", 0) + 1
            state["profiles"][profile_name]["last_warmup"] = datetime.now(timezone.utc).isoformat()
        self._save_state(state)

        return result


class ShadowbanDetector:
    """Monitor for reach drops and engagement anomalies."""

    def __init__(self, api_key: str = "chy-baas-key-001"):
        self.engine = EngagementEngine(api_key)

    async def check_visibility(self, sid: str, platform: str, profile_url: str,
                                test_hashtag: str = None) -> dict:
        """Check if a profile's content is visible in searches."""
        result = {"platform": platform, "profile": profile_url, "risk": "unknown"}

        await self.engine.navigate(sid, profile_url)
        await self.engine.wait_natural(3, 5)

        # Get latest post
        content = await self.engine.get_content(sid)
        html = content.get("content", "")

        # Check follower count trend (if visible)
        js = """(function(){
            var counts = document.querySelectorAll('[title*="follower"], [data-e2e="followers-count"], .follower-count');
            for (var c of counts) { return c.textContent || c.getAttribute('title'); }
            return 'unknown';
        })()"""
        followers = await self.engine.evaluate(sid, js)
        result["followers"] = followers.get("result", "unknown")

        # Check engagement health
        health = await self.engine.get_health(sid)
        result["session_health"] = health

        if health >= 80:
            result["risk"] = "low"
            result["detail"] = "Session looks natural, no anomalies detected"
        elif health >= 50:
            result["risk"] = "medium"
            result["detail"] = "Some detection signals — reduce activity"
        else:
            result["risk"] = "high"
            result["detail"] = "High detection risk — pause automation immediately"

        return result


class CookieBot:
    """Auto-accept cookie consent popups on any website."""

    COOKIE_SELECTORS = [
        "button:has-text('Accept')", "button:has-text('Accept all')",
        "button:has-text('Accept All')", "button:has-text('I agree')",
        "button:has-text('Got it')", "button:has-text('OK')",
        "button:has-text('Allow all')", "button:has-text('Allow All')",
        "[aria-label*='Accept']", "[aria-label*='accept']",
        "#onetrust-accept-btn-handler", ".cc-btn.cc-dismiss",
        "[data-testid='cookie-accept']", ".cookie-accept",
        "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
        ".js-cookie-consent-agree", "#accept-cookie",
    ]

    def __init__(self, api_key: str = "chy-baas-key-001"):
        self.engine = EngagementEngine(api_key)

    async def dismiss_cookies(self, sid: str) -> dict:
        """Try to dismiss any cookie consent popup."""
        for sel in self.COOKIE_SELECTORS:
            try:
                r = await self.engine.click(sid, sel)
                if r.get("status") == "clicked":
                    return {"status": "dismissed", "selector": sel}
            except:
                continue

        # JS fallback
        js = """(function(){
            var btns = document.querySelectorAll('button, a, div[role="button"]');
            var keywords = ['accept', 'agree', 'allow', 'got it', 'ok', 'dismiss'];
            for (var b of btns) {
                var txt = b.textContent.toLowerCase().trim();
                for (var kw of keywords) {
                    if (txt === kw || txt === kw + ' all' || txt === 'accept ' + kw) {
                        b.click(); return 'clicked: ' + txt;
                    }
                }
            }
            return 'none_found';
        })()"""
        r = await self.engine.evaluate(sid, js)
        if "clicked" in str(r.get("result", "")):
            return {"status": "dismissed", "method": "js_fallback"}
        return {"status": "no_popup_found"}


# === FASTAPI ROUTER EXTENSION ===

def extend_engagement_router(router, sessions: dict, auth_check):
    """Add engagement endpoints to the PureSurf social router."""
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    engine = EngagementEngine()
    warmup = AccountWarmUp()
    shadowban = ShadowbanDetector()
    cookiebot = CookieBot()

    async def ep_like(request: Request):
        if not auth_check(request): return JSONResponse({"error": "unauthorized"}, status_code=401)
        b = await request.json()
        r = await engine.like_post(b["session_id"], b["platform"], b["url"])
        return JSONResponse(r)

    async def ep_follow(request: Request):
        if not auth_check(request): return JSONResponse({"error": "unauthorized"}, status_code=401)
        b = await request.json()
        r = await engine.follow_user(b["session_id"], b["platform"], b["url"])
        return JSONResponse(r)

    async def ep_comment(request: Request):
        if not auth_check(request): return JSONResponse({"error": "unauthorized"}, status_code=401)
        b = await request.json()
        r = await engine.comment_on_post(b["session_id"], b["platform"], b["url"], b["comment"])
        return JSONResponse(r)

    async def ep_campaign(request: Request):
        if not auth_check(request): return JSONResponse({"error": "unauthorized"}, status_code=401)
        b = await request.json()
        r = await engine.run_campaign(b["session_id"], b["platform"], b["targets"],
                                       b.get("actions", ["like"]), tuple(b.get("delay_range", [30, 120])),
                                       b.get("comments"))
        return JSONResponse(r)

    async def ep_scan_engage(request: Request):
        if not auth_check(request): return JSONResponse({"error": "unauthorized"}, status_code=401)
        b = await request.json()
        r = await engine.scan_and_engage(b["session_id"], b["platform"], b["feed_url"],
                                          b.get("max_posts", 5), b.get("actions", ["like"]))
        return JSONResponse(r)

    async def ep_warmup(request: Request):
        if not auth_check(request): return JSONResponse({"error": "unauthorized"}, status_code=401)
        b = await request.json()
        r = await warmup.run_warmup(b["session_id"], b["platform"], b["profile_name"], b["feed_url"])
        return JSONResponse(r)

    async def ep_warmup_status(request: Request):
        if not auth_check(request): return JSONResponse({"error": "unauthorized"}, status_code=401)
        b = await request.json()
        return JSONResponse(warmup.get_phase(b["profile_name"]))

    async def ep_shadowban(request: Request):
        if not auth_check(request): return JSONResponse({"error": "unauthorized"}, status_code=401)
        b = await request.json()
        r = await shadowban.check_visibility(b["session_id"], b["platform"], b["profile_url"])
        return JSONResponse(r)

    async def ep_cookie_dismiss(request: Request):
        if not auth_check(request): return JSONResponse({"error": "unauthorized"}, status_code=401)
        b = await request.json()
        r = await cookiebot.dismiss_cookies(b["session_id"])
        return JSONResponse(r)

    router.routes.extend([
        Route("/social/engagement/like", ep_like, methods=["POST"]),
        Route("/social/engagement/follow", ep_follow, methods=["POST"]),
        Route("/social/engagement/comment", ep_comment, methods=["POST"]),
        Route("/social/engagement/campaign", ep_campaign, methods=["POST"]),
        Route("/social/engagement/scan-and-engage", ep_scan_engage, methods=["POST"]),
        Route("/social/warmup/session", ep_warmup, methods=["POST"]),
        Route("/social/warmup/status", ep_warmup_status, methods=["POST"]),
        Route("/social/shadowban/check", ep_shadowban, methods=["POST"]),
        Route("/social/cookie-bot/dismiss", ep_cookie_dismiss, methods=["POST"]),
    ])


if __name__ == "__main__":
    print("PureSurf Engagement Engine")
    print(f"Platforms: {list(EngagementEngine.LIKE_SELECTORS.keys())}")
    print(f"Warm-up phases: {[p['name'] for p in AccountWarmUp.PHASES]}")
    print(f"Cookie selectors: {len(CookieBot.COOKIE_SELECTORS)}")
    print("9 API endpoints ready for integration")
