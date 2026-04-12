"""
Apify LinkedIn Signal Collector
Collects LinkedIn profile data AND posts for prospect analysis
Uses multiple actors for complete signal coverage

Cost optimization:
- Profile scraper: runs every 2 weeks (profiles don't change often)
- Posts scraper: runs every time (to catch new activity)
"""
import time
import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from .config import APIFY_API_KEY

# Apify Actors
PROFILE_ACTOR = "dev_fusion~Linkedin-Profile-Scraper"  # Profile data
POSTS_ACTOR = "harvestapi~linkedin-profile-posts"  # Posts data

# Cache settings
CACHE_DIR = Path(__file__).parent.parent.parent / ".cache"
PROFILE_CACHE_FILE = CACHE_DIR / "linkedin_profiles.json"
PROFILE_CACHE_DAYS = 14  # Re-scrape profiles every 2 weeks


def _load_profile_cache() -> Dict:
    """Load cached profile data"""
    if PROFILE_CACHE_FILE.exists():
        try:
            with open(PROFILE_CACHE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"last_scraped": None, "profiles": {}}


def _save_profile_cache(cache: Dict):
    """Save profile cache to disk"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2, default=str)


def _is_profile_cache_fresh() -> bool:
    """Check if profile cache is less than 2 weeks old"""
    cache = _load_profile_cache()
    last_scraped = cache.get("last_scraped")
    if not last_scraped:
        return False
    try:
        last_date = datetime.fromisoformat(last_scraped)
        return datetime.now() - last_date < timedelta(days=PROFILE_CACHE_DAYS)
    except:
        return False


def _run_actor(actor_id: str, payload: Dict) -> str:
    """Start an Apify actor run and return run ID"""
    url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_API_KEY}"
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def _wait_for_run(run_id: str, timeout: int = 600, poll_interval: int = 10) -> List[Dict]:
    """Wait for run to complete and return results"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_API_KEY}"
        resp = requests.get(url)
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
            raise Exception(f"Apify run failed: {state}")

        print(f"    Status: {state}, waiting...")
        time.sleep(poll_interval)

    raise Exception(f"Run timed out after {timeout}s")


def collect_profiles(linkedin_urls: List[str], force_refresh: bool = False) -> List[Dict]:
    """
    Collect profile data (name, title, company, email).
    Uses cache to avoid re-scraping within 2 weeks (saves ~$5 per 1000 profiles).
    """
    cache = _load_profile_cache()
    cached_profiles = cache.get("profiles", {})
    cache_fresh = _is_profile_cache_fresh()

    # If cache is fresh, use it for profiles we have
    if not force_refresh and cache_fresh:
        results = []
        urls_to_scrape = []

        for url in linkedin_urls:
            if url in cached_profiles:
                results.append(cached_profiles[url])
            else:
                urls_to_scrape.append(url)

        if not urls_to_scrape:
            print(f"  [1/2] Using cached profiles ({len(results)} profiles)")
            print(f"    Cache valid for {PROFILE_CACHE_DAYS - (datetime.now() - datetime.fromisoformat(cache.get('last_scraped', datetime.now().isoformat()))).days} more days")
            return results

        # Scrape only new URLs
        if urls_to_scrape:
            print(f"  [1/2] Cache hit: {len(results)} profiles, scraping {len(urls_to_scrape)} new...")
            run_id = _run_actor(PROFILE_ACTOR, {"profileUrls": urls_to_scrape})
            print(f"    Run ID: {run_id}")
            new_profiles = _wait_for_run(run_id)

            # Update cache with new profiles
            for p in new_profiles:
                url = p.get("linkedinUrl", "")
                if url:
                    cached_profiles[url] = p
                    results.append(p)

            cache["profiles"] = cached_profiles
            _save_profile_cache(cache)

        return results

    # Cache expired or force refresh - scrape all
    print(f"  [1/2] Scraping {len(linkedin_urls)} profiles (cache {'forced refresh' if force_refresh else 'expired'})...")
    run_id = _run_actor(PROFILE_ACTOR, {"profileUrls": linkedin_urls})
    print(f"    Run ID: {run_id}")
    new_profiles = _wait_for_run(run_id)

    # Update cache
    for p in new_profiles:
        url = p.get("linkedinUrl", "")
        if url:
            cached_profiles[url] = p

    cache["profiles"] = cached_profiles
    cache["last_scraped"] = datetime.now().isoformat()
    _save_profile_cache(cache)

    return new_profiles


def collect_posts(linkedin_urls: List[str]) -> List[Dict]:
    """Collect posts from profiles"""
    print(f"  [2/2] Scraping posts for {len(linkedin_urls)} profiles...")
    run_id = _run_actor(POSTS_ACTOR, {
        "profileUrls": linkedin_urls,
        "maxPosts": 10,
    })
    print(f"    Run ID: {run_id}")
    return _wait_for_run(run_id, timeout=900)  # Posts take longer


def collect_signals(linkedin_urls: List[str], force_profile_refresh: bool = False) -> List[Dict]:
    """
    Collect complete LinkedIn data: profiles + posts.

    Cost optimization:
    - Profiles: cached for 2 weeks (don't change often)
    - Posts: scraped every run (to catch new activity)
    """
    if not linkedin_urls:
        print("No LinkedIn URLs provided")
        return []

    print(f"Starting collection for {len(linkedin_urls)} profiles...")

    # Step 1: Get profile data (uses cache if fresh)
    profiles = collect_profiles(linkedin_urls, force_refresh=force_profile_refresh)
    print(f"    Got {len(profiles)} profiles")

    # Build lookup by URL
    profile_map = {}
    for p in profiles:
        url = p.get("linkedinUrl", "")
        if url:
            profile_map[url] = p

    # Step 2: Get posts (ALWAYS scrape - this is where signals come from)
    found_urls = list(profile_map.keys())
    posts_data = []
    if found_urls:
        try:
            posts_data = collect_posts(found_urls)
            print(f"    Got posts for {len(posts_data)} profiles")
        except Exception as e:
            print(f"    Warning: Posts scrape failed: {e}")
            print(f"    Continuing with profile data only...")

    # Build posts lookup
    posts_map = {}
    for p in posts_data:
        url = p.get("profileUrl", p.get("linkedinUrl", ""))
        if url:
            if url not in posts_map:
                posts_map[url] = []
            posts_map[url].append(p)

    # Step 3: Combine data
    combined = []
    for url, profile in profile_map.items():
        profile["posts"] = posts_map.get(url, [])
        combined.append(profile)

    print(f"  Combined data for {len(combined)} profiles")
    return combined


def parse_profile_for_signals(profile_data: Dict) -> Dict:
    """Parse combined profile+posts data into signal format"""
    # Get posts from combined data
    posts_raw = profile_data.get("posts", [])
    posts = []
    for p in posts_raw:
        posts.append({
            "text": p.get("text", p.get("postText", ""))[:500],
            "likes": p.get("likes", p.get("likesCount", 0)),
            "comments": p.get("comments", p.get("commentsCount", 0)),
            "timestamp": p.get("postedAt", p.get("timestamp", "")),
        })

    return {
        "linkedin_url": profile_data.get("linkedinUrl", ""),
        "name": profile_data.get("fullName", profile_data.get("firstName", "") + " " + profile_data.get("lastName", "")),
        "headline": profile_data.get("headline", ""),
        "company": profile_data.get("companyName", ""),
        "title": profile_data.get("jobTitle", ""),
        "email": profile_data.get("email", ""),
        "job_started": profile_data.get("jobStartedOn", ""),
        "posts": posts,
        "activities": [],  # Activity data not available from these actors
    }


def get_run_status(run_id: str) -> Dict:
    """Check the status of an Apify run"""
    url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_API_KEY}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()["data"]


def get_run_results(run_id: str) -> List[Dict]:
    """Get the results from a completed Apify run"""
    status = get_run_status(run_id)
    dataset_id = status.get("defaultDatasetId")
    if not dataset_id:
        return []
    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_API_KEY}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def list_tasks() -> List[Dict]:
    """List all Apify tasks for this account"""
    url = f"https://api.apify.com/v2/actor-tasks?token={APIFY_API_KEY}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()["data"]["items"]


if __name__ == "__main__":
    print("Testing Apify Collector (multi-actor)...")
    tasks = list_tasks()
    print(f"\nExisting tasks: {len(tasks)}")
    print("\n✅ Collector ready!")
