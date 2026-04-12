"""
Company Signal Monitor
Monitors LinkedIn company pages for signals:
- Company posts (launches, campaigns, announcements)
- Job postings (hiring signals = growth/expansion)

Uses Apify actors:
- harvestapi~linkedin-company-posts: Company posts
- fetchclub~linkedin-jobs-scraper: Job postings
"""
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .config import APIFY_API_KEY, AIRTABLE_API_KEY, AIRTABLE_BASE_ID, COMPANIES_TABLE, SIGNALS_TABLE

# Apify Actors for company monitoring
COMPANY_POSTS_ACTOR = "harvestapi~linkedin-company-posts"
JOBS_ACTOR = "fetchclub~linkedin-jobs-scraper"


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


def get_tracked_companies() -> List[Dict]:
    """Get all companies with LinkedIn URLs from Airtable"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{COMPANIES_TABLE}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    companies = []
    for record in resp.json().get("records", []):
        fields = record.get("fields", {})
        linkedin_url = fields.get("LinkedIn URL", "")
        if linkedin_url:
            companies.append({
                "id": record["id"],
                "name": fields.get("Company Name", "Unknown"),
                "linkedin_url": linkedin_url,
            })

    return companies


def collect_company_posts(company_urls: List[str], max_posts: int = 20) -> List[Dict]:
    """
    Collect recent posts from company LinkedIn pages.

    Returns list of posts with company URL, post content, engagement, etc.
    """
    if not company_urls:
        return []

    print(f"Collecting posts from {len(company_urls)} companies...")

    run_id = _run_actor(COMPANY_POSTS_ACTOR, {
        "companyUrls": company_urls,
        "maxPosts": max_posts,
    })
    print(f"  Run ID: {run_id}")

    return _wait_for_run(run_id, timeout=600)


def collect_company_jobs(company_urls: List[str], max_jobs: int = 50) -> List[Dict]:
    """
    Collect job postings from company LinkedIn pages.

    Job postings indicate hiring = growth signals.
    """
    if not company_urls:
        return []

    print(f"Collecting job postings from {len(company_urls)} companies...")

    # Convert company URLs to search queries
    # fetchclub jobs scraper uses company name search
    run_id = _run_actor(JOBS_ACTOR, {
        "companyUrls": company_urls,
        "maxResults": max_jobs,
    })
    print(f"  Run ID: {run_id}")

    return _wait_for_run(run_id, timeout=600)


def parse_company_post_signals(posts: List[Dict]) -> List[Dict]:
    """
    Parse company posts for intent signals.

    Looks for:
    - Product launches
    - Campaign announcements
    - Event mentions
    - Partnership news
    """
    signals = []

    # Keywords that indicate actionable signals
    LAUNCH_KEYWORDS = ["launch", "introducing", "new product", "now available", "coming soon"]
    CAMPAIGN_KEYWORDS = ["campaign", "activation", "experiential", "sampling", "event"]
    HIRING_KEYWORDS = ["hiring", "join our team", "we're growing", "open position"]

    for post in posts:
        text = (post.get("text", "") or post.get("postText", "") or "").lower()
        company_url = post.get("companyUrl", post.get("profileUrl", ""))

        signal_type = None
        signal_strength = 3  # Base strength

        # Check for launch signals
        if any(kw in text for kw in LAUNCH_KEYWORDS):
            signal_type = "company_launch"
            signal_strength = 8
        # Check for campaign signals
        elif any(kw in text for kw in CAMPAIGN_KEYWORDS):
            signal_type = "company_campaign"
            signal_strength = 7
        # Check for hiring signals
        elif any(kw in text for kw in HIRING_KEYWORDS):
            signal_type = "company_hiring"
            signal_strength = 5

        if signal_type:
            signals.append({
                "type": signal_type,
                "strength": signal_strength,
                "source": "LinkedIn Company Post",
                "company_url": company_url,
                "post_text": text[:500],
                "engagement": post.get("likes", 0) + post.get("comments", 0),
                "timestamp": post.get("postedAt", post.get("timestamp", "")),
            })

    return signals


def parse_job_signals(jobs: List[Dict]) -> List[Dict]:
    """
    Parse job postings for hiring signals.

    Marketing/brand jobs = potential experiential needs.
    """
    signals = []

    # Keywords that indicate experiential marketing needs
    EXPERIENTIAL_KEYWORDS = ["experiential", "brand experience", "activation", "events", "sampling"]
    MARKETING_KEYWORDS = ["marketing manager", "brand manager", "campaign", "field marketing"]

    for job in jobs:
        title = (job.get("title", "") or "").lower()
        description = (job.get("description", "") or "").lower()
        company_url = job.get("companyUrl", "")

        combined_text = f"{title} {description}"

        signal_type = None
        signal_strength = 3

        # Experiential-specific roles
        if any(kw in combined_text for kw in EXPERIENTIAL_KEYWORDS):
            signal_type = "company_hiring_experiential"
            signal_strength = 9  # High signal!
        # General marketing roles
        elif any(kw in combined_text for kw in MARKETING_KEYWORDS):
            signal_type = "company_hiring_marketing"
            signal_strength = 6

        if signal_type:
            signals.append({
                "type": signal_type,
                "strength": signal_strength,
                "source": "LinkedIn Job Posting",
                "company_url": company_url,
                "job_title": job.get("title", ""),
                "location": job.get("location", ""),
                "timestamp": job.get("postedAt", datetime.now().isoformat()),
            })

    return signals


def create_company_signal(signal: Dict, company_record_id: str) -> Dict:
    """Create a signal record linked to a company"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{SIGNALS_TABLE}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Build signal ID
    signal_id = f"{signal['type']} ({signal['strength']}) - Company Signal - {datetime.now().strftime('%Y-%m-%d')}"

    fields = {
        "Signal ID (formula)": signal_id,
        "Signal Type": signal["type"] if signal["type"] in [
            "liked_experiential_post", "commented_on_activation",
            "posted_about_launch", "follows_experiential_page",
            "commented_on_competitor", "timing_trigger"
        ] else "timing_trigger",  # Map to existing dropdown option
        "Signal Strength": signal["strength"],
        "Source": "LinkedIn",
        "LinkedIn URL": signal.get("company_url", ""),
        "Signal Timestamp": datetime.utcnow().isoformat() + "Z",
        "Last Checked": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Function": "Company Signal",
        "Title": signal.get("job_title", signal.get("type", "")),
    }

    resp = requests.post(url, headers=headers, json={"fields": fields})
    return resp.json() if resp.status_code == 200 else {"error": resp.text}


def monitor_companies(max_posts: int = 20, max_jobs: int = 50) -> Dict:
    """
    Main function to monitor all tracked companies for signals.

    Returns summary of signals found.
    """
    print("=" * 60)
    print("COMPANY SIGNAL MONITOR")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # Get tracked companies
    companies = get_tracked_companies()
    print(f"\nTracking {len(companies)} companies:")
    for c in companies:
        print(f"  • {c['name']}: {c['linkedin_url']}")

    if not companies:
        print("No companies with LinkedIn URLs to monitor")
        return {"companies": 0, "signals": 0}

    company_urls = [c["linkedin_url"] for c in companies]
    company_map = {c["linkedin_url"]: c for c in companies}

    all_signals = []

    # Collect company posts
    print("\n" + "-" * 40)
    print("STEP 1: Collecting Company Posts")
    print("-" * 40)
    try:
        posts = collect_company_posts(company_urls, max_posts)
        print(f"  Got {len(posts)} posts")

        post_signals = parse_company_post_signals(posts)
        print(f"  Found {len(post_signals)} post signals")
        all_signals.extend(post_signals)
    except Exception as e:
        print(f"  ⚠️ Posts collection failed: {e}")

    # Collect job postings
    print("\n" + "-" * 40)
    print("STEP 2: Collecting Job Postings")
    print("-" * 40)
    try:
        jobs = collect_company_jobs(company_urls, max_jobs)
        print(f"  Got {len(jobs)} job postings")

        job_signals = parse_job_signals(jobs)
        print(f"  Found {len(job_signals)} hiring signals")
        all_signals.extend(job_signals)
    except Exception as e:
        print(f"  ⚠️ Jobs collection failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print(f"COMPANY MONITORING COMPLETE")
    print(f"  Companies monitored: {len(companies)}")
    print(f"  Total signals found: {len(all_signals)}")
    print("=" * 60)

    return {
        "companies": len(companies),
        "signals": len(all_signals),
        "signal_details": all_signals,
    }


if __name__ == "__main__":
    # Test the company monitor
    print("Testing Company Monitor...")
    companies = get_tracked_companies()
    print(f"\nTracked companies: {len(companies)}")
    for c in companies:
        print(f"  • {c['name']}: {c['linkedin_url']}")
