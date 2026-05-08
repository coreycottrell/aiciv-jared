#!/usr/bin/env python3
"""
linkedin_api.py — Multi-User LinkedIn API Helper
================================================
Handles all LinkedIn API interactions via OAuth 2.0 (member authorization)
for MULTIPLE authorized users (Jared + team members).

Each user has their own token file: .credentials/linkedin_tokens_{user_slug}.json

Functions accept a `user` argument (default: "jared") that selects the token file.

CREDENTIALS:
  - .credentials/linkedin_tokens_{user}.json — per-user tokens
  - .env LINKEDIN_CLIENT_ID                  — shared OAuth app client ID
  - .env LINKEDIN_CLIENT_SECRET              — shared OAuth app client secret
  - .env LINKEDIN_REDIRECT_URI               — OAuth redirect URI

SCOPES REQUIRED:
  - w_member_social        (post on behalf of user)
  - r_member_social        (read user's own posts) [optional]
  - openid profile email   (Sign In with LinkedIn using OIDC)

ONBOARDING A NEW USER (7 steps):
  1. python3 tools/linkedin_api.py oauth-url --user nathan
     → returns consent URL with state=nathan
  2. Jared emails URL to Nathan (template: linkedin-team-onboarding-template.md)
  3. Nathan authorizes, lands on callback with ?code=...&state=nathan
  4. Nathan sends code back to Jared
  5. Jared sends code to Aether
  6. python3 tools/linkedin_api.py exchange-code --user nathan --code AQ...
  7. Done — python3 tools/linkedin_api.py --user nathan --post "..." now works

USAGE:
  python3 tools/linkedin_api.py --user jared --status
  python3 tools/linkedin_api.py --user jared --profile
  python3 tools/linkedin_api.py --user nathan --post "Your post text"
  python3 tools/linkedin_api.py list-users
  python3 tools/linkedin_api.py oauth-url --user nathan
  python3 tools/linkedin_api.py exchange-code --user nathan --code AQ...
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
AETHER_ROOT = Path(__file__).parent.parent
CREDENTIALS_DIR = AETHER_ROOT / ".credentials"
ENV_FILE = AETHER_ROOT / ".env"

# LinkedIn API base
LINKEDIN_API = "https://api.linkedin.com"
LINKEDIN_OAUTH = "https://www.linkedin.com/oauth/v2"

# OAuth scopes requested for every user
DEFAULT_SCOPES = "openid profile email w_member_social"


# ---------------------------------------------------------------------------
# .env loader
# ---------------------------------------------------------------------------
def load_env(env_path: Path = ENV_FILE) -> dict:
    env = {}
    if not env_path.exists():
        return env
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


# ---------------------------------------------------------------------------
# Multi-user token paths
# ---------------------------------------------------------------------------
def _normalize_slug(user: str) -> str:
    """Lowercase, alnum + underscores only — protects file system."""
    slug = re.sub(r"[^a-z0-9_]", "", (user or "").lower())
    if not slug:
        raise ValueError(f"Invalid user slug: {user!r}")
    return slug


def tokens_file_for(user: str) -> Path:
    return CREDENTIALS_DIR / f"linkedin_tokens_{_normalize_slug(user)}.json"


# ---------------------------------------------------------------------------
# Token management (per user)
# ---------------------------------------------------------------------------
def load_tokens(user: str = "jared") -> dict:
    """Load tokens from disk for the given user."""
    path = tokens_file_for(user)
    if not path.exists():
        raise FileNotFoundError(
            f"LinkedIn tokens file not found for user '{user}': {path}\n"
            f"Run the OAuth flow:\n"
            f"  python3 tools/linkedin_api.py oauth-url --user {user}\n"
            f"  python3 tools/linkedin_api.py exchange-code --user {user} --code <code>"
        )
    with open(path) as f:
        return json.load(f)


def save_tokens(tokens: dict, user: str = "jared") -> None:
    """Persist tokens to disk with updated saved_at."""
    tokens["saved_at"] = datetime.now(timezone.utc).isoformat()
    tokens["user"] = _normalize_slug(user)
    path = tokens_file_for(user)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(tokens, f, indent=2)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass
    print(f"[linkedin_api] Tokens saved to {path}", file=sys.stderr)


def is_token_expired(tokens: dict) -> bool:
    """LinkedIn access tokens expire in 60 days. 5-min buffer."""
    saved_at_str = tokens.get("saved_at")
    if not saved_at_str:
        return True
    try:
        saved_at = datetime.fromisoformat(saved_at_str)
        expires_in = tokens.get("expires_in", 5184000)
        expiry = saved_at + timedelta(seconds=expires_in - 300)
        return datetime.now(timezone.utc) >= expiry
    except Exception:
        return True


def refresh_tokens(tokens: dict, env: dict, user: str = "jared") -> dict:
    """Refresh access token using refresh_token grant. Persists per-user."""
    client_id = env.get("LINKEDIN_CLIENT_ID") or tokens.get("client_id")
    client_secret = env.get("LINKEDIN_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env"
        )

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise ValueError(
            f"No refresh_token for user '{user}'. Re-run OAuth flow.\n"
            "(LinkedIn only issues refresh tokens for approved apps.)"
        )

    print(f"[linkedin_api] Refreshing access token for '{user}'...", file=sys.stderr)
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()

    req = urllib.request.Request(
        f"{LINKEDIN_OAUTH}/accessToken",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            new_tokens = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        raise RuntimeError(f"Token refresh failed for '{user}': HTTP {e.code}\n{body_text}")

    tokens.update(new_tokens)
    save_tokens(tokens, user=user)
    return tokens


def get_valid_token(user: str = "jared") -> str:
    """Returns valid access_token for user, refreshing if needed."""
    env = load_env()
    tokens = load_tokens(user)
    if is_token_expired(tokens):
        try:
            tokens = refresh_tokens(tokens, env, user=user)
        except ValueError as e:
            raise RuntimeError(
                f"Access token for '{user}' expired and cannot be refreshed.\n{e}"
            )
    access_token = tokens.get("access_token")
    if not access_token:
        raise ValueError(f"No access_token in tokens for user '{user}'")
    return access_token


# ---------------------------------------------------------------------------
# OAuth: generate consent URL + exchange code
# ---------------------------------------------------------------------------
def generate_oauth_url(user_slug: str, scopes: str = DEFAULT_SCOPES) -> str:
    """
    Build the LinkedIn OAuth consent URL with state=<user_slug>.
    Jared emails this URL to the team member.
    """
    env = load_env()
    client_id = env.get("LINKEDIN_CLIENT_ID")
    redirect_uri = env.get("LINKEDIN_REDIRECT_URI")
    if not client_id or not redirect_uri:
        raise ValueError("LINKEDIN_CLIENT_ID and LINKEDIN_REDIRECT_URI must be set in .env")

    slug = _normalize_slug(user_slug)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": slug,
        "scope": scopes,
    }
    return f"{LINKEDIN_OAUTH}/authorization?" + urllib.parse.urlencode(params)


def exchange_code(code: str, user_slug: str) -> dict:
    """
    Exchange OAuth authorization_code for tokens, save under user_slug.
    Also fetches /v2/userinfo to cache person_urn + profile_name.
    """
    env = load_env()
    client_id = env.get("LINKEDIN_CLIENT_ID")
    client_secret = env.get("LINKEDIN_CLIENT_SECRET")
    redirect_uri = env.get("LINKEDIN_REDIRECT_URI")
    if not (client_id and client_secret and redirect_uri):
        raise ValueError("LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, and LINKEDIN_REDIRECT_URI must all be in .env")

    slug = _normalize_slug(user_slug)
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(
        f"{LINKEDIN_OAUTH}/accessToken",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            tokens = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        raise RuntimeError(f"Code exchange failed for '{slug}': HTTP {e.code}\n{body_text}")

    tokens["client_id"] = client_id
    save_tokens(tokens, user=slug)

    # Fetch profile to cache person_urn
    try:
        profile = get_profile(user=slug)
        print(f"[linkedin_api] Onboarded '{slug}' as {profile.get('name')}", file=sys.stderr)
    except Exception as e:
        print(f"[linkedin_api] WARNING: tokens saved but profile fetch failed: {e}", file=sys.stderr)

    return tokens


# ---------------------------------------------------------------------------
# User listing
# ---------------------------------------------------------------------------
def list_users() -> list:
    """Return list of all onboarded users with their names + URNs."""
    if not CREDENTIALS_DIR.exists():
        return []
    users = []
    for f in sorted(CREDENTIALS_DIR.glob("linkedin_tokens_*.json")):
        slug = f.stem.replace("linkedin_tokens_", "")
        try:
            with open(f) as fh:
                t = json.load(fh)
            users.append({
                "slug": slug,
                "name": t.get("profile_name", "(unknown — run --profile)"),
                "person_urn": t.get("person_urn"),
                "saved_at": t.get("saved_at"),
                "expired": is_token_expired(t),
            })
        except Exception as e:
            users.append({"slug": slug, "name": f"(error: {e})"})
    return users


# ---------------------------------------------------------------------------
# HTTP helpers (per-user)
# ---------------------------------------------------------------------------
def _auth_headers(access_token: str, extra: dict = None) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202401",
    }
    if extra:
        headers.update(extra)
    return headers


def li_get(endpoint: str, params: dict = None, user: str = "jared") -> dict:
    access_token = get_valid_token(user)
    url = f"{LINKEDIN_API}{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params, safe="():,")
    req = urllib.request.Request(url, headers=_auth_headers(access_token))
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        if e.code == 401:
            print(f"[linkedin_api] 401 for '{user}' — refresh + retry", file=sys.stderr)
            env = load_env()
            tokens = refresh_tokens(load_tokens(user), env, user=user)
            req2 = urllib.request.Request(url, headers=_auth_headers(tokens["access_token"]))
            with urllib.request.urlopen(req2, timeout=30) as resp2:
                return json.loads(resp2.read())
        raise RuntimeError(f"LinkedIn GET {endpoint} failed for '{user}' ({e.code}):\n{body_text}")


def li_post(endpoint: str, body: dict, extra_headers: dict = None, user: str = "jared") -> dict:
    access_token = get_valid_token(user)
    url = f"{LINKEDIN_API}{endpoint}"
    data = json.dumps(body).encode()
    headers = _auth_headers(access_token, {"Content-Type": "application/json"})
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            response_header_urn = resp.headers.get("x-restli-id") or resp.headers.get("x-linkedin-id")
            out = json.loads(raw) if raw else {}
            if response_header_urn and "id" not in out:
                out["id"] = response_header_urn
            out["_status"] = resp.status
            return out
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        if e.code == 401:
            print(f"[linkedin_api] 401 for '{user}' — refresh + retry", file=sys.stderr)
            env = load_env()
            tokens = refresh_tokens(load_tokens(user), env, user=user)
            headers["Authorization"] = f"Bearer {tokens['access_token']}"
            req2 = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req2, timeout=30) as resp2:
                raw = resp2.read()
                return json.loads(raw) if raw else {"_status": resp2.status}
        raise RuntimeError(f"LinkedIn POST {endpoint} failed for '{user}' ({e.code}):\n{body_text}")


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------
def get_profile(user: str = "jared") -> dict:
    profile = li_get("/v2/userinfo", user=user)
    if "sub" in profile:
        tokens = load_tokens(user)
        person_urn = f"urn:li:person:{profile['sub']}"
        if tokens.get("person_urn") != person_urn or tokens.get("profile_name") != profile.get("name"):
            tokens["person_urn"] = person_urn
            tokens["profile_name"] = profile.get("name")
            save_tokens(tokens, user=user)
    return profile


def _get_person_urn(user: str = "jared") -> str:
    tokens = load_tokens(user)
    urn = tokens.get("person_urn")
    if urn:
        return urn
    profile = get_profile(user=user)
    return f"urn:li:person:{profile['sub']}"


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------
def post_text(content: str, user: str = "jared", visibility: str = "PUBLIC") -> dict:
    if not content or not content.strip():
        raise ValueError("Post content cannot be empty")
    if len(content) > 3000:
        raise ValueError(f"Post content exceeds 3000 char limit ({len(content)})")
    if visibility not in ("PUBLIC", "CONNECTIONS"):
        raise ValueError("visibility must be 'PUBLIC' or 'CONNECTIONS'")

    person_urn = _get_person_urn(user)
    body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
    }
    return li_post("/v2/ugcPosts", body, user=user)


def post_text_with_image(content: str, image_path: str, user: str = "jared",
                         visibility: str = "PUBLIC",
                         image_title: str = "", image_description: str = "") -> dict:
    """Post with an attached image using LinkedIn's 3-step asset upload flow.

    Steps:
      1. POST /v2/assets?action=registerUpload → returns asset URN + upload URL
      2. PUT image bytes to upload URL with correct Content-Type
      3. POST /v2/ugcPosts with media asset URN

    Returns the ugcPost response with the post URN.
    """
    import os
    if not content or not content.strip():
        raise ValueError("Post content cannot be empty")
    if len(content) > 3000:
        raise ValueError(f"Post content exceeds 3000 char limit ({len(content)})")
    if not os.path.isfile(image_path):
        raise ValueError(f"Image file not found: {image_path}")
    if visibility not in ("PUBLIC", "CONNECTIONS"):
        raise ValueError("visibility must be 'PUBLIC' or 'CONNECTIONS'")

    # Auto-detect MIME type from extension
    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif'}
    content_type = mime_map.get(ext, 'image/png')

    person_urn = _get_person_urn(user)
    access_token = get_valid_token(user)

    # STEP 1: Register upload
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": person_urn,
            "serviceRelationships": [
                {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
            ],
        }
    }
    reg_resp = li_post("/v2/assets?action=registerUpload", register_body, user=user)
    asset_urn = reg_resp["value"]["asset"]
    upload_url = reg_resp["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]

    # STEP 2: PUT image bytes
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    put_req = urllib.request.Request(
        upload_url,
        data=img_bytes,
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": content_type},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(put_req, timeout=120) as resp:
            if resp.status not in (200, 201):
                raise RuntimeError(f"Image upload failed: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")[:500]
        raise RuntimeError(f"Image upload failed: HTTP {e.code} — {err_body}")

    # STEP 3: Create ugcPost with asset
    post_body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "description": {"text": image_description or "Image"},
                    "media": asset_urn,
                    "title": {"text": image_title or "Image"},
                }],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
    }
    return li_post("/v2/ugcPosts", post_body, user=user)


def comment_on_post(post_urn: str, comment_text: str, user: str = "jared") -> dict:
    if not post_urn.startswith("urn:li:"):
        raise ValueError("post_urn must be a full URN")
    if not comment_text or not comment_text.strip():
        raise ValueError("Comment cannot be empty")

    person_urn = _get_person_urn(user)
    encoded_urn = urllib.parse.quote(post_urn, safe="")
    body = {
        "actor": person_urn,
        "object": post_urn,
        "message": {"text": comment_text},
    }
    return li_post(f"/v2/socialActions/{encoded_urn}/comments", body, user=user)


def get_recent_posts(count: int = 10, user: str = "jared") -> dict:
    person_urn = _get_person_urn(user)
    params = {
        "q": "authors",
        "authors": f"List({person_urn})",
        "count": count,
        "sortBy": "LAST_MODIFIED",
    }
    return li_get("/v2/ugcPosts", params, user=user)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Multi-user LinkedIn API helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Positional sub-commands (no flag) for list-users / oauth-url / exchange-code
    parser.add_argument("subcommand", nargs="?", choices=["list-users", "oauth-url", "exchange-code"],
                        help="Sub-command (list-users | oauth-url | exchange-code)")
    parser.add_argument("--user", default="jared", help="User slug (default: jared)")
    parser.add_argument("--code", help="OAuth authorization code (for exchange-code)")
    parser.add_argument("--status", action="store_true", help="Show token status")
    parser.add_argument("--refresh", action="store_true", help="Force token refresh")
    parser.add_argument("--profile", action="store_true", help="Fetch /v2/userinfo profile")
    parser.add_argument("--post", metavar="TEXT", help="Create a text post")
    parser.add_argument("--post-with-image", action="store_true", help="Create a post with an attached image (requires --image and --text)")
    parser.add_argument("--image", metavar="PATH", help="Path to image file (for --post-with-image)")
    parser.add_argument("--text", metavar="TEXT", help="Post text (for --post-with-image)")
    parser.add_argument("--image-title", default="", help="Title for image (for --post-with-image)")
    parser.add_argument("--visibility", default="PUBLIC", choices=["PUBLIC", "CONNECTIONS"])
    parser.add_argument("--comment", nargs=2, metavar=("POST_URN", "TEXT"), help="Comment on a post")
    parser.add_argument("--recent", action="store_true", help="List recent posts")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without posting")

    args = parser.parse_args()

    try:
        # --- Sub-commands (no --user-specific token required for some) ---
        if args.subcommand == "list-users":
            users = list_users()
            print(json.dumps(users, indent=2))
            return

        if args.subcommand == "oauth-url":
            url = generate_oauth_url(args.user)
            print(url)
            return

        if args.subcommand == "exchange-code":
            if not args.code:
                print("ERROR: --code required for exchange-code", file=sys.stderr)
                sys.exit(2)
            tokens = exchange_code(args.code, args.user)
            print(f"OK — onboarded user '{args.user}'")
            print(f"  person_urn: {tokens.get('person_urn')}")
            print(f"  profile_name: {tokens.get('profile_name')}")
            print(f"  expires_in: {tokens.get('expires_in')}s")
            return

        # --- Per-user actions ---
        user = args.user

        if args.status:
            path = tokens_file_for(user)
            if not path.exists():
                print(f"No tokens for user '{user}'.")
                print(f"Expected: {path}")
                print(f"\nRun: python3 tools/linkedin_api.py oauth-url --user {user}")
                sys.exit(1)
            tokens = load_tokens(user)
            env = load_env()
            print(f"User:              {user}")
            print(f"Tokens file:       {path}")
            print(f"Saved at:          {tokens.get('saved_at', 'unknown')}")
            print(f"Expires in:        {tokens.get('expires_in', '?')}s")
            print(f"Token expired:     {is_token_expired(tokens)}")
            print(f"Scope:             {tokens.get('scope', '?')}")
            print(f"Person URN:        {tokens.get('person_urn', '(run --profile)')}")
            print(f"Profile name:      {tokens.get('profile_name', '(run --profile)')}")
            print(f"Has refresh token: {bool(tokens.get('refresh_token'))}")
            print(f"CLIENT_ID in .env: {bool(env.get('LINKEDIN_CLIENT_ID'))}")
            print(f"CLIENT_SECRET:     {bool(env.get('LINKEDIN_CLIENT_SECRET'))}")

        elif args.refresh:
            tokens = refresh_tokens(load_tokens(user), load_env(), user=user)
            print(f"Refreshed '{user}'. Expires in: {tokens.get('expires_in')}s")

        elif args.profile:
            print(json.dumps(get_profile(user=user), indent=2))

        elif args.post:
            result = post_text(args.post, user=user, visibility=args.visibility)
            print(json.dumps(result, indent=2))

        elif getattr(args, 'post_with_image', False):
            if not args.image or not args.text:
                print("ERROR: --post-with-image requires --image PATH and --text TEXT", file=sys.stderr)
                sys.exit(2)
            if args.dry_run:
                print(f"[DRY-RUN] Would post with image:")
                print(f"  User:        {user}")
                print(f"  Image:       {args.image}")
                print(f"  Image title: {args.image_title or '(none)'}")
                print(f"  Text (first 200): {args.text[:200]}")
                print(f"  Visibility:  {args.visibility}")
                return
            result = post_text_with_image(
                content=args.text,
                image_path=args.image,
                user=user,
                visibility=args.visibility,
                image_title=args.image_title,
            )
            print(json.dumps(result, indent=2))

        elif args.comment:
            post_urn, text = args.comment
            result = comment_on_post(post_urn, text, user=user)
            print(json.dumps(result, indent=2))

        elif args.recent:
            result = get_recent_posts(user=user)
            print(json.dumps(result, indent=2))

        else:
            parser.print_help()

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
