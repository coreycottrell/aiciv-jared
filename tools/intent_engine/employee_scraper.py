"""
Auto Employee Scraper
Automatically finds and adds ICP-matching employees from target companies.

Usage:
  python -m tools.intent_engine.main add-company "https://linkedin.com/company/general-mills"

This will:
1. Scrape all employees from the company
2. Filter by ICP criteria (marketing roles, brand managers, etc.)
3. Add matching people to Airtable for monitoring
"""
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
from .config import (
    APIFY_API_KEY,
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    PEOPLE_TABLE,
    COMPANIES_TABLE,
)

# Apify actors - using ones we know work
PROFILE_ACTOR = "dev_fusion~Linkedin-Profile-Scraper"
POSTS_ACTOR = "harvestapi~linkedin-profile-posts"

# ICP (Ideal Customer Profile) criteria
# Job titles that indicate decision-makers for experiential marketing
ICP_TITLE_KEYWORDS = [
    # Marketing leadership
    "marketing", "brand", "creative", "content",
    # Specific experiential roles
    "experiential", "activation", "events", "field marketing",
    # Leadership levels
    "vp", "vice president", "director", "head of", "chief",
    "manager", "lead", "senior",
    # Related functions
    "communications", "pr", "public relations",
    "shopper", "trade", "retail marketing",
    "innovation", "product marketing",
]

# Titles to EXCLUDE (too junior or irrelevant)
EXCLUDE_KEYWORDS = [
    "intern", "assistant", "coordinator", "associate",
    "analyst", "specialist",  # Usually too junior
    "sales rep", "account executive",  # Sales, not marketing
    "engineer", "developer", "data",  # Technical roles
    "finance", "accounting", "legal", "hr",
]

# Seniority levels we want
TARGET_SENIORITY = ["C-Level", "VP+", "Director", "Senior Manager", "Manager"]


def _run_actor(actor_id: str, payload: Dict) -> str:
    """Start an Apify actor run and return run ID"""
    url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_API_KEY}"
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def _wait_for_run(run_id: str, timeout: int = 900, poll_interval: int = 15) -> List[Dict]:
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


def matches_icp(employee: Dict) -> bool:
    """Check if an employee matches our ICP criteria"""
    title = (employee.get("headline", "") or employee.get("title", "") or "").lower()

    # Check for exclusions first
    for exclude in EXCLUDE_KEYWORDS:
        if exclude in title:
            return False

    # Check for ICP matches
    for keyword in ICP_TITLE_KEYWORDS:
        if keyword in title:
            return True

    return False


def detect_seniority(title: str) -> str:
    """
    Detect seniority level from job title.

    Maps to Airtable Seniority dropdown values:
    - C-Level
    - VP+
    - Director
    - Senior Manager
    - Manager
    - Associate
    - IC (Individual Contributor)
    """
    import re
    title_lower = title.lower()

    # Check for Associate level (but NOT Associate Director, which is Director-level)
    # This prevents "Associate Marketing Manager" from matching "Manager"
    associate_patterns = ["associate ", "assoc ", "assoc. "]
    has_associate = any(p in title_lower for p in associate_patterns) or title_lower.endswith(" associate")
    # Don't return Associate if this is "Associate Director" - that's Director level
    if has_associate and "director" not in title_lower:
        return "Associate"

    # C-Level - expanded to include more C-suite titles
    # Use word boundaries to avoid matching "coordinator" -> "coo"
    c_level_word_patterns = [
        r'\bceo\b', r'\bcfo\b', r'\bcmo\b', r'\bcoo\b', r'\bcto\b',
        r'\bcro\b', r'\bcio\b', r'\bcpo\b',  # C-suite acronyms as whole words
        r'\bchief\b',  # Chief X Officer
        r'c-suite', r'c-level',
    ]
    if any(re.search(p, title_lower) for p in c_level_word_patterns):
        return "C-Level"

    # VP Level - include V.P. variations
    vp_patterns = [
        r'\bvice president\b', r'\bv\.p\.', r'\bv\.p\b',  # Full and abbreviated
        r'\bvp\b',  # VP as whole word
        r'\bsvp\b', r'\bevp\b', r'\bavp\b', r'\bgvp\b',  # Senior/Executive/Associate/Group VP
    ]
    if any(re.search(p, title_lower) for p in vp_patterns):
        return "VP+"

    # Director Level - include Dir/Dir. abbreviations and Head of
    director_patterns = [
        r'\bdirector\b',
        r'\bdir\b', r'\bdir\.',  # Director abbreviations
        r'\bhead of\b',  # Head of X is typically Director level
    ]
    if any(re.search(p, title_lower) for p in director_patterns):
        return "Director"

    # Senior Manager - check for "Senior X Manager" or "Sr X Manager" patterns
    # Must check BEFORE general Manager check
    senior_manager_patterns = [
        r'\bsenior manager\b', r'\bsr manager\b', r'\bsr\. manager\b',
        r'\bsen manager\b', r'\bsen\. manager\b',
    ]
    if any(re.search(p, title_lower) for p in senior_manager_patterns):
        return "Senior Manager"

    # Check for "Senior X Manager" pattern (e.g., "Senior Marketing Manager")
    # Also "Sr X Manager", "Sr. X Manager"
    senior_x_manager = re.search(r'\b(senior|sr\.?|sen\.?)\s+\w+\s+manager\b', title_lower)
    if senior_x_manager:
        return "Senior Manager"

    # Manager Level - includes Mgr abbreviation and Lead
    manager_patterns = [
        r'\bmanager\b',
        r'\bmgr\b', r'\bmgr\.',  # Manager abbreviations
        r'\bteam lead\b', r'\blead\b',  # Lead roles
    ]
    if any(re.search(p, title_lower) for p in manager_patterns):
        return "Manager"

    # Default to Individual Contributor
    return "IC"


def detect_function(title: str) -> str:
    """Detect function from job title"""
    title_lower = title.lower()

    if any(x in title_lower for x in ["marketing", "brand", "creative", "content", "social"]):
        return "Marketing"
    elif any(x in title_lower for x in ["sales", "business development", "account"]):
        return "Sales"
    elif any(x in title_lower for x in ["product", "innovation"]):
        return "Product"
    elif any(x in title_lower for x in ["communications", "pr", "public relations"]):
        return "Communications"
    elif any(x in title_lower for x in ["experiential", "events", "activation"]):
        return "Experiential"
    else:
        return "Other"


def scrape_profiles(linkedin_urls: List[str]) -> List[Dict]:
    """
    Scrape profile data from a list of LinkedIn URLs.
    Uses our working profile scraper actor.

    Args:
        linkedin_urls: List of LinkedIn profile URLs

    Returns:
        List of profile data dicts
    """
    print(f"Scraping {len(linkedin_urls)} profiles...")

    run_id = _run_actor(PROFILE_ACTOR, {
        "profileUrls": linkedin_urls,
    })
    print(f"  Run ID: {run_id}")

    profiles = _wait_for_run(run_id, timeout=600)
    print(f"  Got {len(profiles)} profiles")

    return profiles


def scrape_company_employees(company_url: str, max_employees: int = 500) -> List[Dict]:
    """
    NOTE: Company employee scrapers require paid Apify rentals.
    Use add_profiles_from_urls() instead with manually collected URLs.

    Workaround: Go to company LinkedIn → See all employees → Copy URLs
    Then use: add_profiles_from_urls(urls)
    """
    print(f"⚠️  Company employee scrapers require paid Apify rentals.")
    print(f"    Please use add_profiles_from_urls() instead.")
    print(f"\n    Workaround:")
    print(f"    1. Go to {company_url}")
    print(f"    2. Click 'See all X employees'")
    print(f"    3. Copy employee profile URLs")
    print(f"    4. Run: python -m tools.intent_engine.main add-profiles urls.txt")
    return []


def filter_icp_employees(employees: List[Dict]) -> List[Dict]:
    """Filter employees to those matching ICP criteria"""
    matching = []

    for emp in employees:
        if matches_icp(emp):
            matching.append(emp)

    print(f"  {len(matching)} employees match ICP criteria")
    return matching


def get_existing_linkedin_urls() -> set:
    """Get all LinkedIn URLs already in Airtable"""
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


def calculate_account_multiplier(
    employee_count: int = None,
    industry: str = None,
) -> float:
    """
    Calculate Account Multiplier based on company characteristics.

    Higher multiplier = higher value account (more likely to buy).

    Args:
        employee_count: Number of employees (larger = higher multiplier)
        industry: Company industry (CPG = higher multiplier)

    Returns:
        Account multiplier value (default 1.0)
    """
    multiplier = 1.0

    # Employee count factor
    if employee_count:
        if employee_count >= 10000:
            multiplier += 0.5  # Large enterprise
        elif employee_count >= 1000:
            multiplier += 0.3  # Mid-market
        elif employee_count >= 100:
            multiplier += 0.1  # SMB

    # Industry factor - CPG/Consumer Goods is our target market
    cpg_industries = [
        "consumer goods", "cpg", "food", "beverage",
        "consumer products", "fmcg", "retail",
    ]
    if industry:
        industry_lower = industry.lower()
        if any(ind in industry_lower for ind in cpg_industries):
            multiplier += 0.5  # Target industry bonus

    return multiplier


def get_or_create_company(
    company_name: str,
    company_url: str,
    employee_count: int = None,
    industry: str = None,
) -> str:
    """
    Get existing company record or create new one, return record ID.

    When creating, sets Account Multiplier based on company characteristics.
    """
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Check if company exists
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{COMPANIES_TABLE}"
    params = {"filterByFormula": f'{{Company Name}} = "{company_name}"'}

    resp = requests.get(url, headers=headers, params=params)
    records = resp.json().get("records", [])

    if records:
        return records[0]["id"]

    # Calculate account multiplier
    multiplier = calculate_account_multiplier(
        employee_count=employee_count,
        industry=industry,
    )

    # Create new company with Account Multiplier
    resp = requests.post(url, headers=headers, json={
        "fields": {
            "Company Name": company_name,
            "LinkedIn URL": company_url,
            "Account Multiplier": multiplier,
        }
    })

    if resp.status_code == 200:
        return resp.json()["id"]
    else:
        print(f"    Warning: Could not create company record: {resp.text[:100]}")
        return None


def add_employees_to_airtable(employees: List[Dict], company_url: str) -> int:
    """Add ICP-matching employees to Airtable People table"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Get existing LinkedIn URLs to avoid duplicates
    existing = get_existing_linkedin_urls()
    print(f"  {len(existing)} people already in database")

    # Get company info
    company_name = employees[0].get("companyName", "Unknown") if employees else "Unknown"
    company_id = get_or_create_company(company_name, company_url)

    added = 0
    skipped = 0

    for emp in employees:
        # Get LinkedIn URL
        linkedin_url = emp.get("profileUrl", emp.get("linkedinUrl", emp.get("url", "")))
        if not linkedin_url:
            continue

        # Check for duplicate
        if linkedin_url.rstrip("/").lower() in existing:
            skipped += 1
            continue

        # Extract data
        name = emp.get("fullName", emp.get("name", f"{emp.get('firstName', '')} {emp.get('lastName', '')}".strip()))
        title = emp.get("headline", emp.get("title", emp.get("jobTitle", "")))
        seniority = detect_seniority(title)
        function = detect_function(title)

        # Build record
        fields = {
            "Name": name,
            "LinkedIn URL": linkedin_url,
            "Title": title,
            "Seniority": seniority,
            "Function": function,
            "Function Type": function,
            "Last Checked": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        # Link to company if we have a record
        if company_id:
            fields["Company (link)"] = [company_id]

        # Create record
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{PEOPLE_TABLE}"
        resp = requests.post(url, headers=headers, json={"fields": fields})

        if resp.status_code == 200:
            added += 1
            if added <= 10:
                print(f"    ✓ Added: {name} ({seniority})")
            elif added == 11:
                print("    ...")
        else:
            print(f"    ✗ Failed to add {name}: {resp.text[:50]}")

    print(f"\n  ✅ Added {added} new people ({skipped} duplicates skipped)")
    return added


def add_profiles_from_urls(linkedin_urls: List[str], company_name: str = None) -> Dict:
    """
    Add ICP-matching profiles from a list of LinkedIn URLs.

    This is the main function for adding new prospects. Works with our
    existing Apify actors (no paid rentals needed).

    Args:
        linkedin_urls: List of LinkedIn profile URLs
        company_name: Optional company name to associate

    Returns:
        Summary dict with counts
    """
    print("=" * 60)
    print("ADD PROFILES FROM URLs")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"URLs provided: {len(linkedin_urls)}")
    print("=" * 60)

    if not linkedin_urls:
        print("❌ No URLs provided")
        return {"total_scraped": 0, "icp_matches": 0, "added": 0}

    # Filter out existing profiles
    existing = get_existing_linkedin_urls()
    new_urls = [u for u in linkedin_urls if u.rstrip("/").lower() not in existing]
    print(f"\n  {len(linkedin_urls)} URLs provided")
    print(f"  {len(existing)} already in database")
    print(f"  {len(new_urls)} new profiles to scrape")

    if not new_urls:
        print("❌ All profiles already exist in database")
        return {"total_scraped": 0, "icp_matches": 0, "added": 0}

    # Step 1: Scrape profiles
    print("\n📥 Step 1: Scraping profiles...")
    profiles = scrape_profiles(new_urls)

    if not profiles:
        print("❌ No profiles returned")
        return {"total_scraped": 0, "icp_matches": 0, "added": 0}

    # Step 2: Filter by ICP
    print("\n🎯 Step 2: Filtering by ICP criteria...")
    icp_profiles = filter_icp_employees(profiles)

    # Step 3: Add to Airtable
    print("\n📊 Step 3: Adding to Airtable...")
    added = add_profiles_to_airtable(icp_profiles, company_name)

    # Summary
    print("\n" + "=" * 60)
    print("COMPLETE")
    print(f"  Profiles scraped: {len(profiles)}")
    print(f"  ICP matches: {len(icp_profiles)}")
    print(f"  New people added: {added}")
    print("=" * 60)

    return {
        "total_scraped": len(profiles),
        "icp_matches": len(icp_profiles),
        "added": added,
    }


def add_profiles_to_airtable(profiles: List[Dict], company_name: str = None) -> int:
    """Add profiles to Airtable People table"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Get or create company if provided
    company_id = None
    if company_name:
        company_id = get_or_create_company(company_name, "")

    added = 0

    for profile in profiles:
        # Extract data
        linkedin_url = profile.get("linkedinUrl", profile.get("profileUrl", ""))
        name = profile.get("fullName", f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip())
        title = profile.get("headline", profile.get("jobTitle", ""))
        company = profile.get("companyName", company_name or "")
        seniority = detect_seniority(title)
        function = detect_function(title)

        # Build record
        fields = {
            "Name": name,
            "LinkedIn URL": linkedin_url,
            "Title": title,
            "Seniority": seniority,
            "Function": function,
            "Function Type": function,
            "Last Checked": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        # Link to company if we have one
        if company_id:
            fields["Company (link)"] = [company_id]
        elif company:
            # Try to find/create company
            cid = get_or_create_company(company, "")
            if cid:
                fields["Company (link)"] = [cid]

        # Create record
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{PEOPLE_TABLE}"
        resp = requests.post(url, headers=headers, json={"fields": fields})

        if resp.status_code == 200:
            added += 1
            if added <= 10:
                print(f"    ✓ Added: {name} ({seniority} - {function})")
            elif added == 11:
                print("    ...")
        else:
            print(f"    ✗ Failed: {name}: {resp.text[:50]}")

    return added


def add_company(company_url: str, max_employees: int = 500) -> Dict:
    """
    Main function: Add a company's ICP employees to monitoring.

    Args:
        company_url: LinkedIn company URL
        max_employees: Maximum employees to scrape

    Returns:
        Summary dict with counts
    """
    print("=" * 60)
    print("AUTO EMPLOYEE SCRAPER")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Company: {company_url}")
    print("=" * 60)

    # Step 1: Scrape employees
    print("\n📥 Step 1: Scraping employees...")
    employees = scrape_company_employees(company_url, max_employees)

    if not employees:
        print("❌ No employees found")
        return {"total_scraped": 0, "icp_matches": 0, "added": 0}

    # Step 2: Filter by ICP
    print("\n🎯 Step 2: Filtering by ICP criteria...")
    icp_employees = filter_icp_employees(employees)

    if not icp_employees:
        print("❌ No employees match ICP criteria")
        return {"total_scraped": len(employees), "icp_matches": 0, "added": 0}

    # Step 3: Add to Airtable
    print("\n📊 Step 3: Adding to Airtable...")
    added = add_employees_to_airtable(icp_employees, company_url)

    # Summary
    print("\n" + "=" * 60)
    print("COMPLETE")
    print(f"  Total employees scraped: {len(employees)}")
    print(f"  ICP matches: {len(icp_employees)}")
    print(f"  New people added: {added}")
    print("=" * 60)

    return {
        "total_scraped": len(employees),
        "icp_matches": len(icp_employees),
        "added": added,
    }


if __name__ == "__main__":
    # Test with General Mills
    result = add_company("https://www.linkedin.com/company/general-mills/", max_employees=100)
    print(f"\nResult: {result}")
