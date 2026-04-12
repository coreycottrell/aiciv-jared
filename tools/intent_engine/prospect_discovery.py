"""
Auto-Prospect Discovery Module

Automatically finds prospects matching ICPs using Apify scrapers
and adds them to Airtable for monitoring.

Usage:
    python -m tools.intent_engine.main discover --icp megan_patel --limit 50
    python -m tools.intent_engine.main discover --all --limit 25
    python -m tools.intent_engine.main learn
"""
import json
import os
import time
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import (
    APIFY_API_KEY,
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    PEOPLE_TABLE,
)
from .icp_config import load_icp_config, get_icp_display_name, update_icp_exclusions


# Paths
LEARNINGS_FILE = Path(__file__).parent / "icp_learnings.json"
CACHE_DIR = Path(__file__).parent.parent.parent / ".cache" / "prospect_discovery"

# Apify actors
GOOGLE_SEARCH_ACTOR = "apify/google-search-scraper"
PROFILE_ACTOR = "dev_fusion~Linkedin-Profile-Scraper"


def load_learnings() -> Dict:
    """
    Load learned patterns from feedback.

    Returns:
        Dict with "bad_titles", "bad_industries", "bad_keywords" lists
    """
    if not LEARNINGS_FILE.exists():
        return {
            "bad_titles": [],
            "bad_industries": [],
            "bad_keywords": [],
            "good_titles": [],
            "good_industries": [],
        }

    try:
        with open(LEARNINGS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {
            "bad_titles": [],
            "bad_industries": [],
            "bad_keywords": [],
            "good_titles": [],
            "good_industries": [],
        }


def save_learnings(learnings: Dict) -> None:
    """Save learnings to file."""
    LEARNINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LEARNINGS_FILE, "w") as f:
        json.dump(learnings, f, indent=2)


def apply_learnings(score: float, prospect: Dict, learnings: Dict) -> float:
    """
    Apply learned patterns to adjust score.

    Args:
        score: Original score
        prospect: Prospect data
        learnings: Learned patterns

    Returns:
        Adjusted score
    """
    title = prospect.get("title", "").lower()
    industry = prospect.get("industry", "").lower()

    # Reduce score for learned bad patterns
    for bad_title in learnings.get("bad_titles", []):
        if bad_title.lower() in title:
            score -= 20

    for bad_industry in learnings.get("bad_industries", []):
        if bad_industry.lower() in industry:
            score -= 15

    for bad_keyword in learnings.get("bad_keywords", []):
        profile_text = prospect.get("profile_text", "").lower()
        if bad_keyword.lower() in profile_text:
            score -= 10

    # Boost score for learned good patterns
    for good_title in learnings.get("good_titles", []):
        if good_title.lower() in title:
            score += 10

    return max(0, min(100, score))  # Clamp to 0-100


def score_prospect(
    prospect: Dict,
    icp: Dict,
    learnings: Optional[Dict] = None,
) -> float:
    """
    Score a prospect against ICP criteria.

    Scoring breakdown (100 points max):
    - Title match: 40 points
    - Industry match: 30 points
    - Company size: 15 points
    - Keywords in profile: 15 points

    Args:
        prospect: Prospect data with title, industry, company_size, profile_text
        icp: ICP configuration
        learnings: Optional learned patterns to apply

    Returns:
        Score from 0-100
    """
    score = 0.0

    # Get weights from ICP config (defaults if not specified)
    scoring = icp.get("scoring", {})
    title_weight = scoring.get("title_weight", 40)
    industry_weight = scoring.get("industry_weight", 30)
    size_weight = scoring.get("company_size_weight", 15)
    keywords_weight = scoring.get("keywords_weight", 15)

    # 1. Title matching (40 points default)
    title = prospect.get("title", "").lower()
    target_titles = [t.lower() for t in icp.get("target_titles", [])]

    # Check for exact or partial title match
    title_score = 0
    for target in target_titles:
        if target in title:
            title_score = title_weight  # Full match
            break
        # Check for partial matches (e.g., "marketing" in "marketing coordinator")
        words = target.split()
        if len(words) > 1 and any(w in title for w in words):
            title_score = max(title_score, title_weight * 0.3)  # Partial match

    score += title_score

    # 2. Industry matching (30 points default)
    industry = prospect.get("industry", "").lower()
    target_industries = [i.lower() for i in icp.get("target_industries", [])]

    for target_ind in target_industries:
        if target_ind in industry or industry in target_ind:
            score += industry_weight
            break

    # 3. Company size (15 points default)
    company_size = prospect.get("company_size", 0)
    if company_size:
        if 100 <= company_size <= 10000:
            score += size_weight  # Mid-size is ideal
        elif company_size > 10000:
            score += size_weight * 0.7  # Large is okay
        elif company_size > 50:
            score += size_weight * 0.5  # Small is less ideal

    # 4. Keywords in profile (15 points default)
    profile_text = prospect.get("profile_text", "").lower()
    keywords = [k.lower() for k in icp.get("keywords_in_profile", [])]

    keyword_matches = sum(1 for k in keywords if k in profile_text)
    if keyword_matches > 0:
        keyword_score = min(keywords_weight, (keyword_matches / len(keywords)) * keywords_weight * 2)
        score += keyword_score

    # Apply learned patterns if provided
    if learnings:
        score = apply_learnings(score, prospect, learnings)

    return round(score, 1)


def filter_by_icp(
    prospects: List[Dict],
    icp: Dict,
    min_score: float = 50,
    learnings: Optional[Dict] = None,
) -> List[Dict]:
    """
    Filter prospects by ICP score threshold.

    Args:
        prospects: List of prospect dicts
        icp: ICP configuration
        min_score: Minimum score to include (default 50)
        learnings: Optional learned patterns

    Returns:
        Filtered list with _icp_score added to each prospect
    """
    if learnings is None:
        learnings = load_learnings()

    filtered = []
    for prospect in prospects:
        score = score_prospect(prospect, icp, learnings)
        if score >= min_score:
            prospect["_icp_score"] = score
            filtered.append(prospect)

    # Sort by score descending
    filtered.sort(key=lambda p: p.get("_icp_score", 0), reverse=True)

    return filtered


def build_search_queries(icp: Dict, limit: int = 50) -> List[str]:
    """
    Build Google search queries for prospect discovery.

    Args:
        icp: ICP configuration
        limit: Target number of prospects

    Returns:
        List of search query strings
    """
    queries = []

    titles = icp.get("target_titles", [])[:5]  # Top 5 titles
    industries = icp.get("target_industries", [])[:3]  # Top 3 industries

    # Generate queries combining titles and industries
    for title in titles:
        for industry in industries:
            query = f'site:linkedin.com/in "{title}" "{industry}"'
            queries.append(query)

            if len(queries) >= limit // 10:
                break
        if len(queries) >= limit // 10:
            break

    # Add some title-only queries
    for title in titles[:3]:
        query = f'site:linkedin.com/in "{title}"'
        if query not in queries:
            queries.append(query)

    return queries[:limit // 10 + 1]  # Don't need more queries than needed


def parse_search_results(google_results: List[Dict]) -> List[str]:
    """
    Extract LinkedIn profile URLs from Google search results.

    Args:
        google_results: Raw Google search results

    Returns:
        List of LinkedIn profile URLs
    """
    urls = []

    for result in google_results:
        url = result.get("url", "")
        # Match linkedin.com/in/ profiles
        if "linkedin.com/in/" in url.lower():
            # Normalize URL
            if not url.startswith("http"):
                url = "https://" + url
            urls.append(url)

    return list(set(urls))  # Remove duplicates


def _run_apify_actor(actor_id: str, payload: Dict, timeout: int = 600) -> List[Dict]:
    """Run an Apify actor and return results."""
    # Start the run
    url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_API_KEY}"
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    run_id = resp.json()["data"]["id"]

    print(f"    Apify run started: {run_id}")

    # Wait for completion
    start_time = time.time()
    while time.time() - start_time < timeout:
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_API_KEY}"
        status_resp = requests.get(status_url)
        status_resp.raise_for_status()
        status = status_resp.json()["data"]

        state = status.get("status")
        if state == "SUCCEEDED":
            # Get results
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
        time.sleep(15)

    raise Exception(f"Apify run timed out after {timeout}s")


def search_prospects_apify(icp: Dict, limit: int = 50) -> List[Dict]:
    """
    Search for prospects matching ICP using Apify.

    Strategy:
    1. Use Google Search to find LinkedIn profiles
    2. Scrape those profiles for detailed data
    3. Score and filter by ICP

    Args:
        icp: ICP configuration
        limit: Maximum prospects to return

    Returns:
        List of prospect dicts with profile data
    """
    print(f"\n  Step 1: Building search queries...")
    queries = build_search_queries(icp, limit)
    print(f"    Generated {len(queries)} queries")

    # Step 2: Run Google searches
    print(f"\n  Step 2: Running Google searches...")
    all_urls = []

    for i, query in enumerate(queries):
        print(f"    Query {i+1}/{len(queries)}: {query[:50]}...")

        try:
            results = _run_apify_actor(GOOGLE_SEARCH_ACTOR, {
                "queries": query,
                "maxPagesPerQuery": 2,
                "resultsPerPage": 10,
            })

            urls = parse_search_results(results)
            all_urls.extend(urls)
            print(f"      Found {len(urls)} LinkedIn URLs")

            # Rate limiting
            if i < len(queries) - 1:
                time.sleep(2)

        except Exception as e:
            print(f"      Error: {e}")
            continue

        # Stop if we have enough URLs
        if len(all_urls) >= limit * 2:
            break

    # Deduplicate
    all_urls = list(set(all_urls))
    print(f"    Total unique URLs: {len(all_urls)}")

    if not all_urls:
        print("    No URLs found")
        return []

    # Step 3: Scrape profiles
    print(f"\n  Step 3: Scraping {min(len(all_urls), limit)} profiles...")

    urls_to_scrape = all_urls[:limit]
    try:
        profiles = _run_apify_actor(PROFILE_ACTOR, {
            "profileUrls": urls_to_scrape,
        }, timeout=900)

        print(f"    Scraped {len(profiles)} profiles")
    except Exception as e:
        print(f"    Profile scrape failed: {e}")
        return []

    # Step 4: Transform to standard format
    prospects = []
    for p in profiles:
        prospect = {
            "name": p.get("fullName", f"{p.get('firstName', '')} {p.get('lastName', '')}".strip()),
            "linkedin_url": p.get("linkedinUrl", p.get("profileUrl", "")),
            "title": p.get("headline", p.get("jobTitle", "")),
            "company": p.get("companyName", ""),
            "industry": p.get("industry", ""),
            "profile_text": " ".join([
                p.get("headline", ""),
                p.get("summary", ""),
                p.get("about", ""),
            ]),
            "company_size": p.get("companySize", 0),
        }
        prospects.append(prospect)

    return prospects


def get_existing_linkedin_urls() -> set:
    """Get all LinkedIn URLs already in Airtable."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{PEOPLE_TABLE}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

    existing = set()
    offset = None

    while True:
        params = {}
        if offset:
            params["offset"] = offset

        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

        for record in data.get("records", []):
            linkedin = record.get("fields", {}).get("LinkedIn URL", "")
            if linkedin:
                existing.add(linkedin.rstrip("/").lower())

        offset = data.get("offset")
        if not offset:
            break

    return existing


def add_prospects_to_airtable(
    prospects: List[Dict],
    icp_name: str,
) -> Dict:
    """
    Add prospects to Airtable with ICP metadata.

    Args:
        prospects: List of prospect dicts
        icp_name: Name of ICP they matched

    Returns:
        Summary dict with added/skipped counts
    """
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }

    # Get existing URLs to avoid duplicates
    existing = get_existing_linkedin_urls()
    print(f"    {len(existing)} people already in database")

    added = 0
    skipped = 0

    display_name = get_icp_display_name(icp_name)

    for prospect in prospects:
        linkedin_url = prospect.get("linkedin_url", "")

        # Skip if duplicate
        if linkedin_url.rstrip("/").lower() in existing:
            skipped += 1
            continue

        # Build record
        fields = {
            "Name": prospect.get("name", "Unknown"),
            "LinkedIn URL": linkedin_url,
            "Title": prospect.get("title", ""),
            "ICP Match": display_name,
            "Discovery Source": "Auto-Discovery via Apify",
            "Discovery Date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "Lead Fit": "Pending Review",
        }

        # Set seniority if we can detect it
        from .employee_scraper import detect_seniority, detect_function
        title = prospect.get("title", "")
        fields["Seniority"] = detect_seniority(title)
        fields["Function Type"] = detect_function(title)

        # Create record
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{PEOPLE_TABLE}"
        resp = requests.post(url, headers=headers, json={"fields": fields})

        if resp.status_code == 200:
            added += 1
            if added <= 10:
                print(f"      + Added: {fields['Name']} ({fields.get('Seniority', 'Unknown')})")
            elif added == 11:
                print("      ...")
        else:
            print(f"      ! Failed: {fields['Name']}: {resp.text[:50]}")

    print(f"\n    Added {added} new prospects ({skipped} duplicates skipped)")

    return {
        "added": added,
        "skipped": skipped,
    }


def update_learnings_from_feedback(feedback: List[Dict]) -> None:
    """
    Update learnings based on human feedback.

    Args:
        feedback: List of dicts with "title", "fit", "notes" keys
    """
    learnings = load_learnings()

    for item in feedback:
        fit = item.get("fit", "")
        title = item.get("title", "")

        if fit == "Bad Fit" and title:
            if title not in learnings["bad_titles"]:
                learnings["bad_titles"].append(title)
        elif fit == "Good Fit" and title:
            if title not in learnings["good_titles"]:
                learnings["good_titles"].append(title)

    save_learnings(learnings)


def get_feedback_from_airtable() -> List[Dict]:
    """
    Get Lead Fit feedback from Airtable for learning.

    Returns:
        List of feedback dicts with title, fit, notes
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{PEOPLE_TABLE}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

    # Get people with Lead Fit set
    params = {
        "filterByFormula": "NOT({Lead Fit} = '')",
    }

    feedback = []
    offset = None

    while True:
        if offset:
            params["offset"] = offset

        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

        for record in data.get("records", []):
            fields = record.get("fields", {})
            feedback.append({
                "title": fields.get("Title", ""),
                "fit": fields.get("Lead Fit", ""),
                "notes": fields.get("Lead Notes", ""),
                "industry": fields.get("Industry", ""),
            })

        offset = data.get("offset")
        if not offset:
            break

    return feedback


def learn_from_feedback() -> Dict:
    """
    Learn from human feedback and update ICP exclusions.

    Returns:
        Summary of learning results
    """
    print("\n  Loading feedback from Airtable...")
    feedback = get_feedback_from_airtable()

    if not feedback:
        print("    No feedback found")
        return {"feedback_count": 0, "learnings_updated": False}

    # Count by fit
    good = [f for f in feedback if f.get("fit") == "Good Fit"]
    bad = [f for f in feedback if f.get("fit") == "Bad Fit"]

    print(f"    Found {len(good)} Good Fit, {len(bad)} Bad Fit")

    if bad:
        print("\n  Analyzing bad fit patterns...")

        # Count bad titles
        from collections import Counter
        bad_titles = Counter(f.get("title", "") for f in bad if f.get("title"))
        bad_industries = Counter(f.get("industry", "") for f in bad if f.get("industry"))

        # Update learnings
        update_learnings_from_feedback(feedback)

        print(f"    Bad titles: {dict(bad_titles.most_common(5))}")
        print(f"    Bad industries: {dict(bad_industries.most_common(5))}")

    return {
        "feedback_count": len(feedback),
        "good_fit": len(good),
        "bad_fit": len(bad),
        "learnings_updated": len(bad) > 0,
    }


def discover_prospects(
    icp_name: str,
    limit: int = 50,
) -> Dict:
    """
    Main discovery function: find prospects matching ICP and add to Airtable.

    Args:
        icp_name: Name of ICP to match (e.g., "megan_patel")
        limit: Maximum prospects to discover

    Returns:
        Summary dict with prospects_found, added, skipped
    """
    print("=" * 60)
    print(f"PROSPECT DISCOVERY: {get_icp_display_name(icp_name)}")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Target limit: {limit}")
    print("=" * 60)

    # Load ICP
    icp = load_icp_config(icp_name)

    # Load learnings
    learnings = load_learnings()

    # Search for prospects
    print("\nPhase 1: Search for prospects...")
    prospects = search_prospects_apify(icp, limit)

    if not prospects:
        print("\nNo prospects found")
        return {"prospects_found": 0, "added": 0, "skipped": 0}

    # Score and filter
    print(f"\nPhase 2: Scoring {len(prospects)} prospects...")
    filtered = filter_by_icp(prospects, icp, min_score=50, learnings=learnings)
    print(f"    {len(filtered)} prospects scored 50+")

    if not filtered:
        print("\nNo prospects met minimum score")
        return {"prospects_found": len(prospects), "added": 0, "skipped": 0}

    # Add to Airtable
    print(f"\nPhase 3: Adding to Airtable...")
    result = add_prospects_to_airtable(filtered, icp_name)

    # Summary
    print("\n" + "=" * 60)
    print("DISCOVERY COMPLETE")
    print(f"  Prospects found: {len(prospects)}")
    print(f"  Prospects qualified: {len(filtered)}")
    print(f"  Added to Airtable: {result['added']}")
    print(f"  Duplicates skipped: {result['skipped']}")
    print("=" * 60)

    return {
        "prospects_found": len(prospects),
        "prospects_qualified": len(filtered),
        "added": result["added"],
        "skipped": result["skipped"],
    }


def discover_all_icps(limit_per_icp: int = 25) -> Dict:
    """
    Discover prospects for all ICPs.

    Args:
        limit_per_icp: Maximum prospects per ICP

    Returns:
        Summary dict with per-ICP results
    """
    from .icp_config import list_icps

    results = {}
    total_added = 0
    total_found = 0

    for icp_name in list_icps():
        print(f"\n{'='*60}")
        print(f"Processing ICP: {icp_name}")
        print(f"{'='*60}")

        result = discover_prospects(icp_name, limit_per_icp)
        results[icp_name] = result
        total_added += result.get("added", 0)
        total_found += result.get("prospects_found", 0)

    print(f"\n{'='*60}")
    print("ALL ICPs COMPLETE")
    print(f"  Total found: {total_found}")
    print(f"  Total added: {total_added}")
    print(f"{'='*60}")

    return results


if __name__ == "__main__":
    # Test discovery
    result = discover_prospects("megan_patel", limit=10)
    print(f"\nResult: {result}")
