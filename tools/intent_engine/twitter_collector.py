"""
Twitter/X Signal Collector for Experiential Intent Engine

Collects signals from Twitter/X for monitored staff members using Apify:
- Tweets (posts about launches, campaigns, etc.)
- Retweets (sharing experiential content)
- Replies (engaging with competitors, industry content)

Uses Apify Twitter scrapers instead of official Twitter API.
Set APIFY_API_KEY in .env file.
"""
import re
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
from .config import APIFY_API_KEY

# Apify Twitter scraper actor
# Using apidojo/tweet-scraper as recommended - reliable and cost-effective
TWITTER_ACTOR = "apidojo/tweet-scraper"

# Keywords that indicate experiential marketing signals
EXPERIENTIAL_KEYWORDS = [
    "experiential", "activation", "brand experience", "launch",
    "campaign", "event", "sampling", "immersive", "pop-up",
    "brand activation", "consumer engagement",
]

# Competitor accounts to track engagement with
COMPETITOR_ACCOUNTS = [
    "PopLabs", "FlamingoXP", "InvisibleNorth", "MKGCreative",
    "GMR_Marketing", "Momentum_WW", "GeorgeP_Johnson",
]


def extract_handle_from_url(url_or_handle: str) -> Optional[str]:
    """
    Extract Twitter handle from a URL or return the handle directly.

    Supports:
    - https://twitter.com/username
    - https://x.com/username
    - https://www.twitter.com/username
    - https://twitter.com/username/status/123456
    - @username
    - username

    Args:
        url_or_handle: Twitter URL or handle

    Returns:
        Clean handle without @ prefix, or None if invalid
    """
    if not url_or_handle:
        return None

    url_or_handle = url_or_handle.strip()

    # If it's a URL, extract the handle
    # Matches twitter.com/username or x.com/username
    url_pattern = r"(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)"
    match = re.match(url_pattern, url_or_handle)
    if match:
        return match.group(1)

    # If it starts with @, remove it
    if url_or_handle.startswith("@"):
        return url_or_handle[1:]

    # Assume it's already a clean handle
    if re.match(r"^[a-zA-Z0-9_]+$", url_or_handle):
        return url_or_handle

    return None


def _run_apify_twitter_actor(handles: List[str], tweets_per_user: int = 20) -> List[Dict]:
    """
    Run the Apify Twitter scraper actor.

    Args:
        handles: List of Twitter handles to scrape
        tweets_per_user: Number of tweets to fetch per user

    Returns:
        List of tweet objects from Apify
    """
    if not APIFY_API_KEY:
        print("Warning: APIFY_API_KEY not set. Twitter collection disabled.")
        return []

    if not handles:
        return []

    # Clean handles (remove @ if present)
    clean_handles = [h.lstrip("@") for h in handles]

    # Apify actor input
    run_input = {
        "handles": clean_handles,
        "tweetsDesired": tweets_per_user,
        "includeReplies": True,
        "includeRetweets": True,
    }

    # Start the actor run
    url = f"https://api.apify.com/v2/acts/{TWITTER_ACTOR}/runs?token={APIFY_API_KEY}"

    try:
        print(f"  Starting Apify Twitter scraper for {len(clean_handles)} handles...")
        resp = requests.post(url, json=run_input)
        resp.raise_for_status()
        run_id = resp.json()["data"]["id"]
        print(f"    Run ID: {run_id}")

        # Wait for completion and get results
        return _wait_for_apify_run(run_id)

    except requests.exceptions.RequestException as e:
        print(f"  Error starting Apify run: {e}")
        return []


def _wait_for_apify_run(run_id: str, timeout: int = 600, poll_interval: int = 10) -> List[Dict]:
    """
    Wait for an Apify run to complete and return results.

    Args:
        run_id: Apify run ID
        timeout: Maximum seconds to wait
        poll_interval: Seconds between status checks

    Returns:
        List of result items from the dataset
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_API_KEY}"
        resp = requests.get(status_url)
        resp.raise_for_status()
        status = resp.json()["data"]

        state = status.get("status")
        if state == "SUCCEEDED":
            # Get dataset items
            dataset_id = status.get("defaultDatasetId")
            if dataset_id:
                items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_API_KEY}"
                items_resp = requests.get(items_url)
                items_resp.raise_for_status()
                return items_resp.json()
            return []
        elif state in ["FAILED", "ABORTED", "TIMED-OUT"]:
            print(f"    Apify run failed: {state}")
            return []

        print(f"    Status: {state}, waiting...")
        time.sleep(poll_interval)

    print(f"    Run timed out after {timeout}s")
    return []


def _parse_apify_response(apify_tweets: List[Dict]) -> Dict[str, Dict]:
    """
    Parse Apify tweet response into our internal format grouped by user.

    Args:
        apify_tweets: List of tweet objects from Apify

    Returns:
        Dict mapping handle to user data with tweets, retweets, replies
    """
    users = {}

    for tweet in apify_tweets:
        # Get user info - handle various Apify actor response formats
        user_info = tweet.get("user", {})
        handle = (
            user_info.get("screen_name") or
            user_info.get("username") or
            tweet.get("author", {}).get("username") or
            tweet.get("screen_name") or
            ""
        )

        if not handle:
            continue

        handle = handle.lstrip("@")

        # Initialize user entry if needed
        if handle not in users:
            users[handle] = {
                "handle": f"@{handle}",
                "name": user_info.get("name", handle),
                "tweets": [],
                "retweets": [],
                "replies": [],
            }

        # Extract tweet text - handle various formats
        text = (
            tweet.get("full_text") or
            tweet.get("text") or
            tweet.get("content") or
            ""
        )

        # Parse timestamp
        created_at = (
            tweet.get("created_at") or
            tweet.get("timestamp") or
            tweet.get("createdAt") or
            ""
        )

        # Get metrics
        likes = (
            tweet.get("favorite_count") or
            tweet.get("likes") or
            tweet.get("likeCount") or
            0
        )
        retweet_count = (
            tweet.get("retweet_count") or
            tweet.get("retweets") or
            tweet.get("retweetCount") or
            0
        )

        # Determine tweet type
        retweeted_status = tweet.get("retweeted_status") or tweet.get("retweet")
        in_reply_to = (
            tweet.get("in_reply_to_screen_name") or
            tweet.get("inReplyToUsername") or
            tweet.get("in_reply_to")
        )

        if retweeted_status:
            # This is a retweet
            original_text = (
                retweeted_status.get("full_text") or
                retweeted_status.get("text") or
                text
            )
            users[handle]["retweets"].append({
                "original_text": original_text,
                "created_at": created_at,
            })
        elif in_reply_to:
            # This is a reply
            users[handle]["replies"].append({
                "text": text,
                "created_at": created_at,
                "in_reply_to": in_reply_to,
                "original_text": "",  # May not be available from scraper
            })
        else:
            # This is an original tweet
            users[handle]["tweets"].append({
                "text": text,
                "created_at": created_at,
                "likes": likes,
                "retweets": retweet_count,
            })

    return users


def collect_twitter_signals(handles: List[str]) -> List[Dict]:
    """
    Collect Twitter data for a list of handles using Apify.

    Args:
        handles: List of Twitter handles (with or without @)
                 Can also be Twitter URLs (twitter.com/user or x.com/user)

    Returns:
        List of Twitter data dicts with tweets, retweets, replies
    """
    if not handles:
        return []

    # Extract handles from URLs if needed
    clean_handles = []
    for h in handles:
        extracted = extract_handle_from_url(h)
        if extracted:
            clean_handles.append(extracted)

    if not clean_handles:
        return []

    print(f"Collecting Twitter signals for {len(clean_handles)} handles...")

    # Run Apify actor
    apify_results = _run_apify_twitter_actor(clean_handles)

    if not apify_results:
        print("  No results from Apify")
        return []

    # Parse into our format
    users_data = _parse_apify_response(apify_results)

    # Convert to list format matching expected return type
    results = list(users_data.values())
    print(f"  Got data for {len(results)} handles")

    return results


def parse_twitter_signals(twitter_data: Dict) -> List[Dict]:
    """
    Parse Twitter data into intent signals.

    Matches the same signal structure as LinkedIn signals.

    Args:
        twitter_data: Dict with handle, name, tweets, retweets, replies

    Returns:
        List of signal dicts with type, strength, evidence, source
    """
    signals = []

    handle = twitter_data.get("handle", "")

    # Process tweets (original posts)
    for tweet in twitter_data.get("tweets", []):
        text = tweet.get("text", "").lower()

        # Check for experiential/launch keywords
        if any(kw in text for kw in EXPERIENTIAL_KEYWORDS):
            # Check if it's about a launch
            if any(word in text for word in ["launch", "launching", "new product", "announcing"]):
                signals.append({
                    "type": "posted_about_launch",
                    "strength": 8,
                    "evidence": f"Tweet: {tweet.get('text', '')[:200]}...",
                    "source": "Twitter",
                    "timestamp": tweet.get("created_at", ""),
                })
            else:
                # General experiential content
                signals.append({
                    "type": "posted_about_launch",
                    "strength": 6,
                    "evidence": f"Tweet about experiential: {tweet.get('text', '')[:200]}...",
                    "source": "Twitter",
                    "timestamp": tweet.get("created_at", ""),
                })

    # Process retweets (sharing content)
    for retweet in twitter_data.get("retweets", []):
        text = retweet.get("original_text", "").lower()

        if any(kw in text for kw in EXPERIENTIAL_KEYWORDS):
            signals.append({
                "type": "liked_experiential_post",
                "strength": 5,
                "evidence": f"Retweeted: {retweet.get('original_text', '')[:200]}...",
                "source": "Twitter",
                "timestamp": retweet.get("created_at", ""),
            })

    # Process replies (engagement)
    for reply in twitter_data.get("replies", []):
        text = reply.get("text", "").lower()
        in_reply_to = str(reply.get("in_reply_to", "")).lower()
        original_text = reply.get("original_text", "").lower()

        # Check if reply is to a competitor or about experiential content
        is_competitor_reply = any(comp.lower() in in_reply_to for comp in COMPETITOR_ACCOUNTS)
        has_experiential_content = any(kw in original_text for kw in EXPERIENTIAL_KEYWORDS)

        if is_competitor_reply or has_experiential_content:
            signals.append({
                "type": "commented_on_competitor",
                "strength": 7,
                "evidence": f"Reply to competitor: {reply.get('text', '')[:200]}...",
                "source": "Twitter",
                "timestamp": reply.get("created_at", ""),
            })
        elif any(kw in text for kw in EXPERIENTIAL_KEYWORDS):
            signals.append({
                "type": "commented_on_activation",
                "strength": 5,
                "evidence": f"Reply about experiential: {reply.get('text', '')[:200]}...",
                "source": "Twitter",
                "timestamp": reply.get("created_at", ""),
            })

    return signals


if __name__ == "__main__":
    # Test the collector
    print("Testing Apify-based Twitter Collector...")

    if not APIFY_API_KEY:
        print("APIFY_API_KEY not set - cannot test live collection")
        print("Set APIFY_API_KEY in your .env file to enable Twitter collection")
    else:
        # Test with a known public account
        test_data = collect_twitter_signals(["@twitter"])
        if test_data:
            print(f"Got data for {len(test_data)} handles")
            for data in test_data:
                print(f"  {data['handle']}: {len(data.get('tweets', []))} tweets")

                # Parse signals
                signals = parse_twitter_signals(data)
                print(f"    Found {len(signals)} signals")
                for sig in signals[:3]:
                    print(f"      - {sig['type']} (strength: {sig['strength']})")
        else:
            print("No data returned")

    # Test URL extraction
    print("\nTesting URL extraction:")
    test_urls = [
        "https://twitter.com/elonmusk",
        "https://x.com/elonmusk",
        "https://www.twitter.com/test_user",
        "https://twitter.com/user/status/12345",
        "@username",
        "username",
    ]
    for url in test_urls:
        handle = extract_handle_from_url(url)
        print(f"  {url} -> {handle}")

    print("\nTwitter Collector ready! (using Apify)")
