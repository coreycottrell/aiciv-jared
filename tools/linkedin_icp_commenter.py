#!/usr/bin/env python3
"""
LinkedIn ICP Commenter
======================

Comments on N ICP profiles' recent posts, with:
  - 90-second spacing between comments (rate-limit safety)
  - team block-list enforcement (NEVER comment on team members)
  - reaction rotation: Support / Celebrate / Insightful / Love (NEVER Like)
  - per-profile state tracking (last_commented_at) for fair rotation
  - dry-run mode

Usage:
    python3 tools/linkedin_icp_commenter.py --user jared --count 3
    python3 tools/linkedin_icp_commenter.py --user jared --count 1 --dry-run

Inputs:
    configs/linkedin_icps.json       — ICP profiles, segments, block-list
    configs/linkedin_icp_state.json  — last_commented_at per profile (auto-created)

Constraints (CONSTITUTIONAL):
    - Load LinkedIn skills reference before ANY LinkedIn work
    - NEVER comment on team profiles (block_list)
    - NEVER more than one comment per 90s
    - Short, contextual replies only (8-25 words)
    - Reactions rotate — NEVER "Like"

Author: full-stack-developer (2026-04-14)
"""
from __future__ import annotations
import argparse
import json
import logging
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

ICP_CONFIG       = ROOT / "configs" / "linkedin_icps.json"
STATE_FILE       = ROOT / "configs" / "linkedin_icp_state.json"
PERSONAS_DIR     = ROOT / "configs" / "icp_personas"
DISCOVERY_LOG    = ROOT / "configs" / "linkedin_icp_discovery_log.jsonl"
CANDIDATES_FILE  = ROOT / "configs" / "linkedin_icp_candidates.json"
LOG_FILE         = ROOT / "logs" / "linkedin_icp_commenter.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Persona-fit threshold: candidate must match >=N of the persona's keywords
FIT_THRESHOLD    = 3
ROTATION_DAYS    = 14  # no profile commented on more than 1x per 14 days
PERSONA_DRIVE_ID = "1dI3uyCeVgmkLctIt2yIv6AG2vgJKjZM3"

SPACING_SEC      = 90
COMMENT_MIN_W    = 8
COMMENT_MAX_W    = 25
REACTIONS        = ["APPRECIATION", "EMPATHY", "INTEREST", "PRAISE"]  # Support, Love, Insightful, Celebrate
# NEVER include "LIKE" — constitutional rule.

# ── Logging ──────────────────────────────────────────────────────────────────
def get_logger() -> logging.Logger:
    lg = logging.getLogger("linkedin_icp_commenter")
    lg.setLevel(logging.INFO)
    if not lg.handlers:
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                                datefmt="%Y-%m-%d %H:%M:%S")
        fh = logging.FileHandler(LOG_FILE); fh.setFormatter(fmt); lg.addHandler(fh)
        sh = logging.StreamHandler(sys.stdout); sh.setFormatter(fmt); lg.addHandler(sh)
    return lg


# ── Config / state ───────────────────────────────────────────────────────────
def load_config() -> dict:
    if not ICP_CONFIG.exists():
        raise FileNotFoundError(f"{ICP_CONFIG} not found — run the Drive sync first.")
    return json.loads(ICP_CONFIG.read_text())


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"profiles": {}}  # {handle: {last_commented_at, count}}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def handle_from_url(url: str) -> Optional[str]:
    m = re.search(r"linkedin\.com/in/([A-Za-z0-9_\-\.]+)", url or "")
    return m.group(1).rstrip("/") if m else None


# ── Rotation ─────────────────────────────────────────────────────────────────
def select_profiles(cfg: dict, state: dict, count: int, log: logging.Logger) -> list[dict]:
    block = {b["handle"].lower() for b in cfg.get("block_list", [])}
    profiles = cfg.get("profiles", [])
    if not profiles:
        log.warning(
            "No profiles in configs/linkedin_icps.json. ICP list is empty. "
            "Seed it with real LinkedIn profile URLs before running live. "
            "See docs/LINKEDIN-AUTOMATION-PIPELINE.md for how to add ICPs."
        )
        return []

    usable = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=ROTATION_DAYS)
    for p in profiles:
        h = (p.get("handle") or handle_from_url(p.get("url",""))  or "").lower()
        if not h or h in block:
            continue
        last_raw = state["profiles"].get(h, {}).get("last_commented_at") or "1970-01-01T00:00:00+00:00"
        # Enforce 14-day rotation rule
        try:
            last_dt = datetime.fromisoformat(last_raw.replace("Z", "+00:00"))
            if last_dt > cutoff:
                log.info(f"  skip {h}: commented within last {ROTATION_DAYS} days ({last_raw})")
                continue
        except Exception:
            pass
        usable.append((last_raw, p | {"handle": h}))

    # Least-recently-engaged first
    usable.sort(key=lambda x: x[0])
    return [p for _, p in usable[:count]]


# ── Comment generation ───────────────────────────────────────────────────────
# Short, contextual templates. Kept ASCII-safe so the LinkedIn UGC API is happy.
_COMMENT_TEMPLATES = [
    "This resonates — especially the point about {hook}. How are you measuring impact so far?",
    "Really appreciate this framing. The part on {hook} is where most teams get stuck, in my experience.",
    "Strong take. Curious how you'd extend the {hook} idea into teams that already have heavy legacy tooling.",
    "Agree on {hook}. The hardest part is usually the first 90 days of adoption, not the tech itself.",
    "Good reminder. {hook} is underrated — we see the same pattern in SMBs we work with.",
    "The {hook} angle is the interesting one. Most of the noise online skips it completely.",
]
_GENERIC_HOOKS = ["adoption", "workflow fit", "team buy-in", "measurement", "context carry-over", "compound effect"]

def synth_comment(post_excerpt: str) -> str:
    """Generate an 8-25 word contextual comment. Picks a hook from the post if available."""
    hook = None
    if post_excerpt:
        # Grab a short salient phrase
        words = re.findall(r"\b[a-zA-Z]{4,}\b", post_excerpt)
        if words:
            # Prefer middle of distribution (not the first word)
            hook = random.choice(words[:20]).lower()
    hook = hook or random.choice(_GENERIC_HOOKS)
    template = random.choice(_COMMENT_TEMPLATES)
    comment = template.format(hook=hook)

    # Word count bounds
    wc = len(comment.split())
    if wc < COMMENT_MIN_W or wc > COMMENT_MAX_W:
        # Fallback to safe, in-bound comment
        comment = f"This resonates — the {hook} point is where most teams actually get stuck."
    return comment


# ── LinkedIn search / API wrappers ───────────────────────────────────────────
def fetch_recent_post_urn(handle: str, user: str, log: logging.Logger) -> Optional[tuple[str, str]]:
    """
    Try to resolve a recent post URN for a given profile handle.

    LIMITATION: The v2/rest.li LinkedIn API requires an elevated scope
    (`r_member_social`) to read other members' posts. Most personal tokens do
    NOT have this. We attempt a best-effort via `linkedin_api.li_get` and
    gracefully skip on 403/404.

    Returns (urn, excerpt) on success, else None.
    """
    try:
        import linkedin_api as li
    except Exception as e:
        log.error(f"linkedin_api import failed: {e}")
        return None

    # Best-effort: the LinkedIn UGC read API is restricted. We document this
    # clearly so Jared knows the gap. When PureSurf browser-side scraping is
    # wired in, this function is the single place to swap implementations.
    try:
        # Personal vanityName lookup is limited. Try profile resolution first.
        _ = li.li_get(f"/v2/people/(vanityName:{handle})", user=user)
    except Exception as e:
        log.warning(f"[{handle}] profile lookup not permitted via API: {type(e).__name__}: {e}")
    # No public endpoint returns a stranger's recent posts on free scopes.
    # Return None — caller will skip or use dry-run scaffolding.
    return None


def do_comment(post_urn: str, text: str, user: str, log: logging.Logger) -> bool:
    try:
        import linkedin_api as li
        res = li.comment_on_post(post_urn, text, user=user)
        log.info(f"Comment OK on {post_urn}: {res.get('id','?')}")
        return True
    except Exception as e:
        log.error(f"Comment FAILED on {post_urn}: {type(e).__name__}: {e}")
        return False


def do_reaction(post_urn: str, user: str, log: logging.Logger) -> Optional[str]:
    """Rotate reactions Support/Celebrate/Insightful/Love. Never LIKE."""
    reaction = random.choice(REACTIONS)
    try:
        import linkedin_api as li
        # Reactions v2 endpoint: /v2/reactions?actor={personUrn}
        # Most tokens lack scope; best-effort only.
        actor = li._get_person_urn(user=user)
        body = {"root": post_urn, "reactionType": reaction}
        li.li_post(f"/v2/reactions?actor={actor}", body, user=user)
        log.info(f"Reaction {reaction} OK on {post_urn}")
        return reaction
    except Exception as e:
        log.warning(f"Reaction {reaction} FAILED on {post_urn} (likely scope-limited): {type(e).__name__}: {e}")
        return None


# ── Main loop ────────────────────────────────────────────────────────────────
def run(user: str, count: int, dry_run: bool) -> int:
    log = get_logger()
    log.info(f"=== ICP commenter START user={user} count={count} dry_run={dry_run} ===")

    cfg   = load_config()
    state = load_state()

    picks = select_profiles(cfg, state, count, log)
    if not picks:
        log.info("No eligible ICP profiles to process. Exiting clean.")
        return 0

    block_count = len(cfg.get("block_list", []))
    log.info(f"Loaded: {len(cfg.get('profiles',[]))} total ICPs, {block_count} blocked, selected {len(picks)} for this run")

    success = 0
    for i, p in enumerate(picks):
        handle = p["handle"]
        url    = p.get("url") or f"https://linkedin.com/in/{handle}/"
        seg    = p.get("segment","")
        log.info(f"[{i+1}/{len(picks)}] handle={handle} segment={seg} url={url}")

        fetch = fetch_recent_post_urn(handle, user, log)
        if fetch is None:
            if dry_run:
                # Simulate for dry-run visibility
                fake_urn = f"urn:li:share:DRYRUN_{handle}_{int(time.time())}"
                excerpt  = f"(simulated post excerpt for {handle})"
                comment  = synth_comment(excerpt)
                log.info(f"  [DRY-RUN] Would fetch recent post. Using simulated URN: {fake_urn}")
                log.info(f"  [DRY-RUN] Would comment: {comment!r}")
                log.info(f"  [DRY-RUN] Would rotate reaction from: {REACTIONS}")
                success += 1
            else:
                log.warning(f"  Skipping {handle}: could not resolve a recent post URN (API scope limitation).")
            # Spacing even on dry-run? Only sleep between REAL actions.
            if not dry_run and i < len(picks)-1:
                log.info(f"  sleeping {SPACING_SEC}s before next profile")
                time.sleep(SPACING_SEC)
            continue

        post_urn, excerpt = fetch
        comment_text = synth_comment(excerpt)
        log.info(f"  post_urn={post_urn}")
        log.info(f"  comment={comment_text!r}")

        if dry_run:
            log.info(f"  [DRY-RUN] No API call.")
            success += 1
        else:
            ok = do_comment(post_urn, comment_text, user, log)
            if ok:
                reaction = do_reaction(post_urn, user, log)
                state["profiles"][handle] = {
                    "last_commented_at": datetime.now(timezone.utc).isoformat(),
                    "last_post_urn": post_urn,
                    "last_comment": comment_text,
                    "last_reaction": reaction,
                    "count": state["profiles"].get(handle,{}).get("count", 0) + 1,
                }
                save_state(state)
                success += 1
            if i < len(picks)-1:
                log.info(f"  sleeping {SPACING_SEC}s (rate-limit safety)")
                time.sleep(SPACING_SEC)

    log.info(f"=== ICP commenter DONE user={user} success={success}/{len(picks)} dry_run={dry_run} ===")
    return 0 if success else 1


# ═════════════════════════════════════════════════════════════════════════════
# ICP DISCOVERY LAYER
# ═════════════════════════════════════════════════════════════════════════════
# Given a persona .md file, extract keywords and FIND real LinkedIn profiles
# matching that persona. Populates configs/linkedin_icp_candidates.json for
# HUMAN REVIEW before any live comments are made against them.
#
# Backends tried in order (first available wins):
#   1. Proxycurl  (env: PROXYCURL_API_KEY)     — paid, reliable, ToS-clean
#   2. Apollo.io  (env: APOLLO_API_KEY)         — paid, people-search
#   3. PhantomBuster (env: PHANTOMBUSTER_API_KEY) — LinkedIn Sales Nav scrape
#   4. PureSurf browser-scrape (env: PURESURF_BROWSER_URL + PURESURF_LI_COOKIE)
#   5. None → stub mode, log what's needed, don't fake data
# ═════════════════════════════════════════════════════════════════════════════

PERSONA_KEYWORD_FIELDS = {
    # section header → how we categorize it
    "title":      ["Title", "Professional Profile", "Role"],
    "industry":   ["Company type", "Industry", "Sector"],
    "company":    ["Revenue", "Team size", "Company size"],
    "location":   ["Location", "Geography"],
}


def fetch_personas_from_drive(log: logging.Logger) -> int:
    """Sync 6 persona .md files from Drive → configs/icp_personas/.
    Returns number of files synced. Non-fatal if Drive not reachable."""
    PERSONAS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        from gdrive_manager import GDriveManager  # local import
    except Exception as e:
        log.warning(f"gdrive_manager unavailable ({e}); using cached personas at {PERSONAS_DIR}")
        return 0
    try:
        g = GDriveManager()
        files = g.list_files(PERSONA_DRIVE_ID)
        n = 0
        for f in files:
            if not f.get("name", "").endswith(".md"):
                continue
            dest_dir = PERSONAS_DIR / f["name"]
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp = dest_dir / f["name"]
            try:
                g.download_file(f["id"], str(tmp))
                # gdrive_manager.download_file nests weirdly; flatten
                nested = tmp / f["name"]
                target = PERSONAS_DIR / f["name"]
                if nested.exists():
                    nested.replace(target)
                    try: tmp.rmdir()
                    except Exception: pass
                elif tmp.exists() and tmp.is_file():
                    tmp.replace(target)
                n += 1
            except Exception as ee:
                log.warning(f"persona download failed {f['name']}: {ee}")
        log.info(f"personas synced from Drive: {n}")
        return n
    except Exception as e:
        log.warning(f"persona Drive sync failed: {e}")
        return 0


def load_persona(segment_key: str, log: logging.Logger) -> Optional[dict]:
    """Load a cached persona .md and extract keyword signal."""
    path = PERSONAS_DIR / f"icp-{segment_key}.md"
    if not path.exists():
        log.error(f"persona not found: {path} — run --sync-personas first")
        return None
    text = path.read_text()

    def grab(label: str) -> Optional[str]:
        m = re.search(rf"\*\*{re.escape(label)}\*\*\s*:\s*(.+)", text)
        return m.group(1).strip() if m else None

    # Pull crisp signals
    title    = grab("Title") or grab("Role") or ""
    company  = grab("Company type") or grab("Company") or ""
    location = grab("Location") or ""
    team     = grab("Team size") or grab("Company size") or ""
    revenue  = grab("Revenue") or ""

    # Build a keyword set. We want ~5 meaningful tokens.
    raw = " ".join([title, company, location, team, revenue])
    # Industry hints from text body
    industry_hints = []
    for kw in ["marketing", "agency", "e-commerce", "ecommerce", "shopify", "real estate",
               "finance", "operations", "founder", "consultant", "fractional", "saas"]:
        if re.search(rf"\b{kw}\b", text, re.I):
            industry_hints.append(kw.lower())

    # Normalize keywords
    kws: list[str] = []
    for s in [title, company, location]:
        for token in re.split(r"[,/()|\-]+", s or ""):
            token = token.strip().lower()
            if len(token) >= 4 and token not in kws:
                kws.append(token)
    for h in industry_hints:
        if h not in kws:
            kws.append(h)

    # Top 5 keywords for scoring (persona fit threshold)
    keywords_top5 = kws[:5] if len(kws) >= 5 else kws + industry_hints[: max(0, 5 - len(kws))]

    return {
        "segment": segment_key,
        "title": title,
        "company_type": company,
        "location": location,
        "team_size": team,
        "revenue": revenue,
        "keywords": kws[:15],
        "keywords_top5": keywords_top5[:5],
        "industry_hints": industry_hints,
        "search_query": " ".join([title, industry_hints[0] if industry_hints else ""]).strip(),
    }


def pick_backend(log: logging.Logger) -> tuple[str, dict]:
    """
    Return (backend_name, creds_dict). 'none' if nothing configured.

    Priority order (CONSTITUTIONAL, 2026-04-15):
      1. puresurf  — our own browser automation via surf.purebrain.ai, uses
                     persistent LinkedIn profile (OAuth session anchored under
                     PURESURF_LI_PROFILE). NO external paid API. Preferred.
      2. proxycurl — paid people-search API, fallback if PureSurf unavailable
      3. apollo    — scaffolded, not implemented
      4. phantombuster — scaffolded, not implemented
      5. none      — stub (logs requirement, returns empty)
    """
    # .env may not be auto-loaded in this tool; best-effort
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except Exception:
        pass

    # PureSurf takes priority — we own this infra, no per-call cost
    if os.getenv("BAAS_API_KEY"):
        return "puresurf", {
            "api_key":     os.getenv("BAAS_API_KEY"),
            "base_url":    os.getenv("PURESURF_BASE_URL", "https://surf.purebrain.ai"),
            "profile":     os.getenv("PURESURF_LI_PROFILE", "aether-linkedin"),
            "proxy":       os.getenv("PURESURF_PROXY", "floppydata-jared"),
            "device":      os.getenv("PURESURF_DEVICE", "macbook"),
        }

    if os.getenv("PROXYCURL_API_KEY"):
        return "proxycurl", {"api_key": os.getenv("PROXYCURL_API_KEY")}
    if os.getenv("APOLLO_API_KEY"):
        return "apollo", {"api_key": os.getenv("APOLLO_API_KEY")}
    if os.getenv("PHANTOMBUSTER_API_KEY"):
        return "phantombuster", {"api_key": os.getenv("PHANTOMBUSTER_API_KEY")}
    return "none", {}


# ---------------------------------------------------------------------------
# PureSurf backend (CONSTITUTIONAL — preferred path)
# ---------------------------------------------------------------------------

PURESURF_SEARCH_JS = r"""
(() => {
  const out = [];
  const seen = new Set();
  // LinkedIn people-search results: each card has an <a href="/in/{handle}/...">
  // with aria-hidden text block nearby for name, plus subtitle for headline.
  const anchors = Array.from(document.querySelectorAll('a[href*="/in/"]'));
  for (const a of anchors) {
    const href = a.href || '';
    const m = href.match(/\/in\/([A-Za-z0-9\-\_\%]+)\/?/);
    if (!m) continue;
    const handle = decodeURIComponent(m[1]).toLowerCase();
    if (seen.has(handle)) continue;
    // walk up to the result container
    let container = a;
    for (let i = 0; i < 6 && container && container.parentElement; i++) {
      container = container.parentElement;
      if (container.querySelector && container.querySelectorAll('a[href*="/in/"]').length === 1) {
        // container encloses exactly this one result anchor
        const txt = (container.innerText || '').split('\n').map(s => s.trim()).filter(Boolean);
        if (txt.length >= 2) {
          // name = first line, headline typically 2nd, company/location 3rd
          const name = txt[0] || '';
          const headline = txt[1] || '';
          const subline  = txt[2] || '';
          // filter out "status is online" / "Open to work" LinkedIn tags
          if (name && !name.toLowerCase().startsWith('status is')) {
            out.push({
              handle: handle,
              url: 'https://www.linkedin.com/in/' + handle + '/',
              name: name,
              headline: headline,
              subline: subline,
            });
            seen.add(handle);
          }
        }
        break;
      }
    }
    if (out.length >= 25) break;
  }
  return JSON.stringify(out);
})()
"""


def _puresurf_request(method: str, path: str, creds: dict, log: logging.Logger,
                      json_body: Optional[dict] = None, timeout: int = 30) -> Optional[dict]:
    """Thin wrapper around requests for PureSurf BaaS endpoints."""
    try:
        import requests
    except Exception:
        log.error("requests library missing")
        return None
    url = f"{creds['base_url'].rstrip('/')}{path}"
    headers = {"x-api-key": creds["api_key"], "Content-Type": "application/json"}
    try:
        r = requests.request(method, url, headers=headers, json=json_body, timeout=timeout)
        if r.status_code >= 400:
            log.warning(f"puresurf {method} {path} -> {r.status_code}: {r.text[:300]}")
            # return parsed JSON anyway so callers can inspect "detail"
            try:
                return r.json()
            except Exception:
                return None
        try:
            return r.json()
        except Exception:
            return {"_raw": r.text}
    except Exception as e:
        log.warning(f"puresurf {method} {path} error: {e}")
        return None


def _puresurf_force_close_for_profile(creds: dict, log: logging.Logger) -> bool:
    """
    On 409 conflict ('Profile X already has an active session'), find the
    leaked session for this profile and force-delete it with save_cookies=false.

    CRITICAL: We pass save_cookies=false so a session that landed on a login
    page (which is WHY it was probably abandoned) doesn't overwrite cookies.json
    with empty/login-page cookies. This anti-pattern destroyed cookies in the
    past (see memory: 2026-04-06--cookie-overwrite-on-session-close.md).
    """
    profile = creds.get("profile")
    if not profile:
        return False

    # Try profile-keyed delete first (some BaaS APIs accept profile_name)
    resp = _puresurf_request(
        "DELETE", f"/sessions/{profile}?save_cookies=false",
        creds, log, timeout=15,
    )
    if resp and not resp.get("detail"):
        log.info(f"[puresurf] force-closed leaked session for profile={profile} (profile-keyed)")
        return True

    # Fall back: list sessions and find one matching this profile
    listing = _puresurf_request("GET", "/sessions", creds, log, timeout=15)
    if not listing:
        return False
    sessions = listing.get("sessions") or listing.get("data") or []
    for sess in sessions:
        if not isinstance(sess, dict):
            continue
        if sess.get("profile_name") == profile or sess.get("profile") == profile:
            sid = sess.get("session_id") or sess.get("id")
            if sid:
                _puresurf_request(
                    "DELETE", f"/sessions/{sid}?save_cookies=false",
                    creds, log, timeout=15,
                )
                log.info(f"[puresurf] force-closed leaked session sid={sid} for profile={profile}")
                return True
    log.warning(f"[puresurf] could not locate leaked session for profile={profile}")
    return False


def _puresurf_profile_has_li_at(creds: dict, log: logging.Logger) -> bool:
    """
    Pre-flight check: does the profile have a li_at cookie?
    If 0 cookies, no point creating a session — it'll just land on login
    and likely get destroyed by save-on-close. Returns True if li_at present
    OR if the cookie endpoint isn't supported (unknown == proceed).
    """
    profile = creds.get("profile")
    if not profile:
        return True  # don't block if profile not configured
    resp = _puresurf_request(
        "GET", f"/api/v1/profiles/{profile}/cookies",
        creds, log, timeout=15,
    )
    if not resp:
        # Endpoint missing or transient error — proceed (don't block)
        return True
    cookies = resp.get("cookies") or []
    if not isinstance(cookies, list):
        return True
    li_at = [c for c in cookies if isinstance(c, dict) and c.get("name") == "li_at"]
    if li_at:
        return True
    log.error(
        f"[puresurf] PRE-FLIGHT FAIL: profile={profile} has 0 li_at cookies. "
        f"Cannot start LinkedIn automation. Human one-time login required: "
        f"open https://surf.purebrain.ai , select profile '{profile}', log into "
        f"linkedin.com manually, then re-run. (See memory: "
        f"2026-04-06--cookie-overwrite-on-session-close.md for why this happens.)"
    )
    return False


def _puresurf_ensure_session(creds: dict, log: logging.Logger) -> Optional[str]:
    """
    Create (or reuse) a LinkedIn-anchored session keyed by profile_name.
    PureSurf's profile_name is the persistence anchor — same name == same
    cookies/logged-in state across runs. Returns session_id or None.
    Reuses a cached session within a single `run_discovery` invocation.

    Idempotent: if profile already has an active session (409), force-closes
    it with save_cookies=false (to protect the cookie store) and retries once.
    """
    cached_sid = _PURESURF_SESSION_CACHE.get("sid")
    if cached_sid:
        # Verify it's still alive
        resp = _puresurf_request("GET", f"/sessions/{cached_sid}", creds, log, timeout=10)
        if resp and not resp.get("detail"):
            return cached_sid
        _PURESURF_SESSION_CACHE.clear()

    # Pre-flight: don't waste a session on a profile with no li_at — it'll
    # just land on the login page and risk overwriting cookies on close.
    if not _puresurf_profile_has_li_at(creds, log):
        return None

    body = {
        "profile_name":   creds["profile"],
        "proxy_provider": creds["proxy"],
        "device_profile": creds["device"],
    }

    def _try_create() -> Optional[dict]:
        return _puresurf_request("POST", "/sessions", creds, log, json_body=body, timeout=45)

    resp = _try_create()
    # 409 retry path: leaked session from prior run — force-close + retry
    if resp and isinstance(resp.get("detail"), str) and "already has an active session" in resp["detail"].lower():
        log.warning(f"[puresurf] 409 conflict on session create — attempting force-close + retry")
        if _puresurf_force_close_for_profile(creds, log):
            time.sleep(2)
            resp = _try_create()

    if not resp:
        return None
    sid = resp.get("session_id") or resp.get("id")
    if not sid:
        log.warning(f"puresurf session create returned no session_id: {resp}")
        return None
    log.info(f"[puresurf] session_id={sid} profile={creds['profile']}")
    _PURESURF_SESSION_CACHE["sid"] = sid
    _PURESURF_SESSION_CACHE["logged_in_verified"] = False
    # small warm-up — session needs a beat before first navigate
    time.sleep(3)
    return sid


def _puresurf_navigate(sid: str, url: str, creds: dict, log: logging.Logger) -> bool:
    resp = _puresurf_request("POST", f"/sessions/{sid}/navigate", creds, log,
                              json_body={"url": url}, timeout=45)
    if not resp:
        return False
    # some versions return {"status":"ok"} / {"success":true} / {"url": ...}
    if resp.get("detail"):
        return False
    return True


def _puresurf_evaluate(sid: str, script: str, creds: dict, log: logging.Logger) -> Optional[str]:
    """Run JS in the page, return the string result (script return value)."""
    resp = _puresurf_request("POST", f"/sessions/{sid}/evaluate", creds, log,
                              json_body={"script": script}, timeout=30)
    if not resp:
        return None
    # common shapes: {"result": "..."} or {"value": "..."} or {"_raw": "..."}
    for k in ("result", "value", "_raw", "output"):
        if k in resp and isinstance(resp[k], str):
            return resp[k]
    # sometimes returns {"result": {...parsed JSON...}}
    if "result" in resp:
        try:
            return json.dumps(resp["result"])
        except Exception:
            return str(resp["result"])
    return None


def _puresurf_check_logged_in(sid: str, creds: dict, log: logging.Logger) -> bool:
    """Visit /feed/ and confirm we're not redirected to login."""
    if not _puresurf_navigate(sid, "https://www.linkedin.com/feed/", creds, log):
        return False
    time.sleep(5)
    js = "JSON.stringify({url: window.location.href, title: document.title})"
    raw = _puresurf_evaluate(sid, js, creds, log)
    if not raw:
        return False
    try:
        state = json.loads(raw) if raw.startswith('{') else json.loads(json.loads(raw))
    except Exception:
        log.warning(f"[puresurf] could not parse feed state: {raw[:200]}")
        return False
    cur = (state.get("url") or "").lower()
    logged_in = "/feed" in cur and "login" not in cur and "authwall" not in cur
    log.info(f"[puresurf] logged_in={logged_in} current_url={cur[:100]}")
    return logged_in


def backend_puresurf_search(persona: dict, count: int, creds: dict,
                            log: logging.Logger) -> list[dict]:
    """
    Use PureSurf (surf.purebrain.ai) to run a LinkedIn people-search for the
    persona's search_query, scrape results from the DOM, and return them in
    the shape score_candidate() expects.

    Session uses a persistent profile_name (default: 'aether-linkedin') which
    anchors the LinkedIn OAuth cookies. If the profile is not yet logged in,
    this returns empty with a clear log message — human must log in once via
    surf.purebrain.ai UI, after which the cookies persist.

    Rate limits: LinkedIn allows ~60 navigations/hour per session (proactive
    rate limit enforced by PureSurf). One search = one nav, so ~60 searches/hr
    ceiling. Callers should space persona sweeps accordingly.
    """
    sid = _puresurf_ensure_session(creds, log)
    if not sid:
        return []
    try:
        # 1. Login check (only once per run — costs a nav against 60/hr budget)
        if not _PURESURF_SESSION_CACHE.get("logged_in_verified"):
            if not _puresurf_check_logged_in(sid, creds, log):
                log.error(
                    "[puresurf] Profile '%s' is NOT logged into LinkedIn. "
                    "Log in ONCE via surf.purebrain.ai UI for this profile_name, "
                    "then re-run discovery. Cookies persist after first login.",
                    creds["profile"],
                )
                return []
            _PURESURF_SESSION_CACHE["logged_in_verified"] = True

        # 2. Build people-search URL
        query = persona.get("search_query") or persona.get("title", "")
        if not query.strip():
            log.warning(f"[puresurf] empty search_query for {persona.get('segment')}")
            return []
        search_url = (
            "https://www.linkedin.com/search/results/people/"
            f"?keywords={quote_plus(query)}&origin=GLOBAL_SEARCH_HEADER"
        )
        log.info(f"[puresurf] searching: {query!r}")
        if not _puresurf_navigate(sid, search_url, creds, log):
            log.warning("[puresurf] people-search navigate failed")
            return []

        # 3. Wait for results to render (LinkedIn is SPA, cards lazy-load)
        time.sleep(8)

        # 4. Scroll once to pull in additional results beyond the fold
        _puresurf_evaluate(sid, "window.scrollTo(0, document.body.scrollHeight/2); null;", creds, log)
        time.sleep(3)

        # 5. Scrape
        raw_json = _puresurf_evaluate(sid, PURESURF_SEARCH_JS, creds, log)
        if not raw_json:
            log.warning("[puresurf] evaluate returned nothing")
            return []
        # evaluate may return the JSON string itself, or a JSON string containing a JSON string
        try:
            results = json.loads(raw_json)
            if isinstance(results, str):
                results = json.loads(results)
        except Exception as e:
            log.warning(f"[puresurf] could not parse results JSON: {e} raw={raw_json[:200]}")
            return []

        out = []
        for item in results[: count * 3]:
            h = (item.get("handle") or "").lower()
            if not h or h in {"unknown", "in"}:
                continue
            out.append({
                "handle": h,
                "url":    item.get("url") or f"https://www.linkedin.com/in/{h}/",
                "_raw_title":   item.get("headline", ""),
                "_raw_company": item.get("subline", ""),
                "_raw_name":    item.get("name", ""),
            })
        log.info(f"[puresurf] scraped {len(out)} raw candidates for '{query}'")
        return out
    finally:
        # Keep session alive between personas in the same run (rate-limit friendly)
        # but delete if we're the last persona. Caller handles cross-persona reuse
        # via _PURESURF_SESSION_CACHE (see discover_icp_profiles).
        pass


# Module-level cache so multi-persona runs reuse the same session
_PURESURF_SESSION_CACHE: dict = {}


def _puresurf_cleanup(creds: dict, log: logging.Logger) -> None:
    """
    Delete the cached session at end of run_discovery.

    CRITICAL (CONSTITUTIONAL — see memory 2026-04-06--cookie-overwrite-on-session-close.md):
    When closing a session, PureSurf saves the browser's current cookies back
    to cookies.json by default. If the session is on a login page (because
    li_at was invalid), this OVERWRITES the profile's cookies with empty/
    login-page cookies, destroying any future hope of re-using the profile.

    Rule: if logged_in_verified is False, pass save_cookies=false. Always.
    Better to leave a session to expire via TTL than to corrupt cookies.json.
    """
    sid = _PURESURF_SESSION_CACHE.get("sid")
    if not sid:
        return
    logged_in = bool(_PURESURF_SESSION_CACHE.get("logged_in_verified"))
    if logged_in:
        # Safe to save cookies — we know the session was on /feed/, not login
        _puresurf_request("DELETE", f"/sessions/{sid}", creds, log, timeout=10)
        log.info(f"[puresurf] deleted session {sid} (cookies saved)")
    else:
        # Session never reached /feed/ — DO NOT save cookies. This protects
        # the profile from being wiped if the session landed on a login page.
        _puresurf_request("DELETE", f"/sessions/{sid}?save_cookies=false",
                          creds, log, timeout=10)
        log.info(f"[puresurf] deleted session {sid} (save_cookies=false — protected profile)")
    _PURESURF_SESSION_CACHE.clear()


def backend_proxycurl_search(persona: dict, count: int, creds: dict, log: logging.Logger) -> list[dict]:
    """Proxycurl person-search. Real API call, paid."""
    try:
        import requests
    except Exception:
        return []
    headers = {"Authorization": f"Bearer {creds['api_key']}"}
    params = {
        "page_size": str(min(count, 10)),
        "current_role_title": persona.get("title", ""),
        "country": "us",
    }
    try:
        r = requests.get(
            "https://nubela.co/proxycurl/api/search/person",
            headers=headers, params=params, timeout=30,
        )
        if r.status_code != 200:
            log.warning(f"proxycurl {r.status_code}: {r.text[:200]}")
            return []
        out = []
        for item in (r.json().get("results") or [])[:count]:
            url = item.get("linkedin_profile_url") or item.get("profile_url") or ""
            h = handle_from_url(url)
            if not h: continue
            out.append({"handle": h, "url": url,
                        "_raw_title": item.get("title", ""),
                        "_raw_company": item.get("company", "")})
        return out
    except Exception as e:
        log.warning(f"proxycurl error: {e}")
        return []


def backend_stub(persona: dict, count: int, log: logging.Logger) -> list[dict]:
    """No backend configured — return empty with clear ask."""
    log.error(
        "DISCOVERY REQUIRES one of: "
        "PROXYCURL_API_KEY | APOLLO_API_KEY | PHANTOMBUSTER_API_KEY | "
        "(PURESURF_BROWSER_URL + PURESURF_LI_COOKIE). "
        f"Persona '{persona['segment']}' search would query: {persona['search_query']!r}"
    )
    return []


def score_candidate(candidate: dict, persona: dict) -> tuple[int, list[str]]:
    """Match candidate text vs persona.keywords_top5. Return (score, matched_list)."""
    hay = " ".join([
        candidate.get("_raw_title", ""),
        candidate.get("_raw_company", ""),
        candidate.get("handle", ""),
    ]).lower()
    matched = [kw for kw in persona["keywords_top5"] if kw and kw.lower() in hay]
    return len(matched), matched


def log_discovery_run(segment: str, backend: str, query: str,
                      raw_results: int, kept: int, threshold: int) -> None:
    DISCOVERY_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "segment": segment,
        "backend": backend,
        "query": query,
        "raw_results": raw_results,
        "kept_above_threshold": kept,
        "threshold": threshold,
    }
    with DISCOVERY_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def discover_icp_profiles(segment: str, count: int, dry_run: bool,
                          log: logging.Logger, cfg: dict) -> list[dict]:
    """
    Given a persona segment key, find `count` LinkedIn profiles matching it.
    Writes candidates to configs/linkedin_icp_candidates.json for human review.
    NEVER auto-populates configs/linkedin_icps.json.profiles[].
    """
    persona = load_persona(segment, log)
    if not persona:
        return []

    # Exclude existing profiles + block_list
    existing = {(p.get("handle") or "").lower() for p in cfg.get("profiles", [])}
    blocked  = {b["handle"].lower() for b in cfg.get("block_list", [])}
    excluded = existing | blocked

    backend, creds = pick_backend(log)
    log.info(f"[discover] segment={segment} backend={backend} count={count} query={persona['search_query']!r}")

    if backend == "puresurf":
        raw = backend_puresurf_search(persona, count, creds, log)
    elif backend == "proxycurl":
        raw = backend_proxycurl_search(persona, count * 3, creds, log)
    elif backend == "none":
        raw = backend_stub(persona, count, log)
    else:
        log.warning(f"backend {backend} not yet implemented in code; treating as stub")
        raw = backend_stub(persona, count, log)

    # Score + filter
    kept = []
    for cand in raw:
        h = cand["handle"].lower()
        if h in excluded:
            continue
        score, matched = score_candidate(cand, persona)
        if score < FIT_THRESHOLD:
            continue
        kept.append({
            "handle":  h,
            "url":     cand["url"],
            "segment": segment,
            "matched_keywords": matched,
            "match_score": score,
            "added":             datetime.now(timezone.utc).date().isoformat(),
            "last_commented_at": None,
            "source_backend":    backend,
            "approved":          False,  # human must flip this
        })
        if len(kept) >= count:
            break

    log_discovery_run(segment, backend, persona["search_query"], len(raw), len(kept), FIT_THRESHOLD)

    # Write to candidates file (NOT profiles — human review required)
    candidates = {"candidates": []}
    if CANDIDATES_FILE.exists():
        try:
            candidates = json.loads(CANDIDATES_FILE.read_text())
        except Exception:
            pass
    # Dedupe by handle+segment
    existing_cand = {(c["handle"], c["segment"]) for c in candidates.get("candidates", [])}
    for c in kept:
        if (c["handle"], c["segment"]) not in existing_cand:
            candidates["candidates"].append(c)
    CANDIDATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATES_FILE.write_text(json.dumps(candidates, indent=2))

    if dry_run:
        log.info(f"[DRY-RUN] segment={segment}: {len(kept)} candidates written to {CANDIDATES_FILE}")
        for c in kept:
            log.info(f"  - @{c['handle']} score={c['match_score']} matched={c['matched_keywords']}")
        if not kept and backend == "none":
            log.info(f"  (no backend configured — see log above for what Jared needs to provision)")
    return kept


def run_discovery(segment: Optional[str], run_all: bool, count: int,
                  dry_run: bool, sync_personas: bool, auto_approve: bool = False) -> int:
    log = get_logger()
    log.info(f"=== ICP discovery START segment={segment} all={run_all} count={count} dry_run={dry_run} ===")
    cfg = load_config()

    if sync_personas:
        fetch_personas_from_drive(log)

    if run_all:
        segments = [s["key"] for s in cfg.get("segments", [])]
    elif segment:
        segments = [segment]
    else:
        log.error("Provide --persona <segment> or --all")
        return 2

    total = 0
    backend, creds = pick_backend(log)
    try:
        for i, seg in enumerate(segments):
            kept = discover_icp_profiles(seg, count, dry_run, log, cfg)
            total += len(kept)
            # Inter-persona spacing to respect LinkedIn's 60 navs/hour cap.
            # One search = ~2 navs (feed check + search). 10s buffer between personas.
            if backend == "puresurf" and i < len(segments) - 1:
                spacing = 10 + random.randint(0, 5)
                log.info(f"[puresurf] inter-persona spacing: {spacing}s")
                time.sleep(spacing)
    finally:
        if backend == "puresurf":
            _puresurf_cleanup(creds, log)

    log.info(f"=== ICP discovery DONE total_candidates={total} dry_run={dry_run} ===")

    # Auto-approve: promote candidates to profiles
    if auto_approve and not dry_run and total > 0:
        profiles_file = Path("configs/linkedin_icps.json")
        if not profiles_file.exists():
            log.error(f"[auto-approve] profiles file not found: {profiles_file}")
            return 1

        # Load candidates
        candidates = {}
        if CANDIDATES_FILE.exists():
            try:
                candidates = json.loads(CANDIDATES_FILE.read_text())
            except Exception as e:
                log.error(f"[auto-approve] Failed to read candidates: {e}")
                return 1

        # Load profiles config
        try:
            profiles_cfg = json.loads(profiles_file.read_text())
        except Exception as e:
            log.error(f"[auto-approve] Failed to read profiles config: {e}")
            return 1

        # Get block_list to respect it during promotion
        block_list = set(profiles_cfg.get("block_list", []))

        # Build existing profile handles (case-insensitive dedup)
        existing_handles = {p["handle"].lower() for p in profiles_cfg.get("profiles", [])}

        promoted = 0
        skipped_duplicate = 0
        skipped_blocked = 0

        for cand in candidates.get("candidates", []):
            handle = cand["handle"]
            handle_lower = handle.lower()

            # Skip if blocked
            if handle_lower in block_list:
                skipped_blocked += 1
                continue

            # Skip if already in profiles
            if handle_lower in existing_handles:
                skipped_duplicate += 1
                continue

            # Promote to profiles
            new_profile = {
                "handle": handle,
                "segment": cand["segment"],
                "approved": True,
                "added_via": "auto-approve",
                "added_at": datetime.utcnow().strftime("%Y-%m-%d"),
                "match_score": cand.get("match_score"),
                "matched_keywords": cand.get("matched_keywords", [])
            }
            profiles_cfg["profiles"].append(new_profile)
            existing_handles.add(handle_lower)
            promoted += 1

        # Write back profiles config
        if promoted > 0:
            try:
                profiles_file.write_text(json.dumps(profiles_cfg, indent=2))
                log.info(f"[auto-approve] Promoted {promoted} candidates → profiles, skipped {skipped_duplicate} duplicates, {skipped_blocked} blocked")
            except Exception as e:
                log.error(f"[auto-approve] Failed to write profiles config: {e}")
                return 1
        else:
            log.info(f"[auto-approve] No new candidates to promote (duplicates={skipped_duplicate}, blocked={skipped_blocked})")

    if not auto_approve:
        log.info(f"Review candidates: {CANDIDATES_FILE}")
        log.info(f"After review, copy approved entries into configs/linkedin_icps.json profiles[]")

    return 0


def main() -> None:
    p = argparse.ArgumentParser(description="LinkedIn ICP commenter + discovery (90s spacing, reaction rotation, team block-list)")
    p.add_argument("--user", default="jared")
    p.add_argument("--count", type=int, default=3)
    p.add_argument("--dry-run", action="store_true")
    # Discovery mode
    p.add_argument("--discover", action="store_true", help="Run ICP discovery instead of commenting")
    p.add_argument("--persona",  help="Persona segment key (e.g. agency-director)")
    p.add_argument("--all",      action="store_true", help="Discover across all personas")
    p.add_argument("--sync-personas", action="store_true", help="Pull persona .md files from Drive first")
    p.add_argument("--auto-approve", action="store_true", help="Auto-promote discovered candidates into profiles (skip human review)")
    args = p.parse_args()

    if args.discover:
        sys.exit(run_discovery(args.persona, args.all, args.count, args.dry_run, args.sync_personas, args.auto_approve))
    sys.exit(run(args.user, args.count, args.dry_run))


if __name__ == "__main__":
    main()
