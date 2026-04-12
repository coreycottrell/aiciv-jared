#!/usr/bin/env python3
"""
Experiential Intent Engine - Main Orchestrator

This is the main entry point for the Intent Engine. It can be run:
1. Manually: python -m intent_engine.main [command]
2. Via cron: Schedule daily runs
3. Via Make webhook: Triggered by Apify completion

Commands:
- collect: Run Apify to collect LinkedIn signals
- process: Process signals through OpenAI classifier
- dashboard: Generate and send daily dashboard email
- full: Run complete pipeline (collect → process → dashboard)
- preview: Preview dashboard without sending
"""

import sys
import argparse
from datetime import datetime

from . import airtable_client
from . import openai_classifier
from . import apify_collector
from . import twitter_collector
from . import email_dashboard
from . import company_monitor
from . import employee_scraper
from . import prospect_discovery
from . import icp_config


def run_collect():
    """Collect LinkedIn signals via Apify"""
    print("=" * 50)
    print("STEP 1: Collecting LinkedIn Signals")
    print("=" * 50)

    # Get all people with LinkedIn URLs
    people = airtable_client.get_people_with_linkedin()
    print(f"Found {len(people)} people with LinkedIn URLs")

    if not people:
        print("No people to process. Add prospects to Airtable first.")
        return []

    # Extract LinkedIn URLs
    urls = []
    for person in people:
        url = person.get("fields", {}).get("LinkedIn URL")
        if url:
            urls.append(url)

    print(f"Collecting signals for {len(urls)} LinkedIn profiles...")

    # Run Apify collection
    results = apify_collector.collect_signals(urls)

    print(f"✅ Collected data for {len(results)} profiles")
    return results


def run_process(apify_results=None):
    """Process collected signals through OpenAI classifier"""
    print("\n" + "=" * 50)
    print("STEP 2: Processing Signals")
    print("=" * 50)

    signals_created = 0

    if apify_results is None:
        print("No Apify results provided. Using test data.")
        # For testing without Apify
        test_profiles = [
            {
                "linkedin_url": "https://linkedin.com/in/test",
                "name": "Test User",
                "headline": "VP Marketing at Test Corp",
                "company": "Test Corp",
                "posts": [{"text": "Launching our experiential campaign!", "likes": 50}],
                "activities": [],
            }
        ]
        apify_results = test_profiles

    for raw_profile in apify_results:
        # Parse profile data
        profile = apify_collector.parse_profile_for_signals(raw_profile)

        print(f"\nProcessing: {profile['name']}")

        # Classify signals
        signals = openai_classifier.classify_linkedin_activity(
            name=profile["name"],
            headline=profile["headline"],
            company=profile["company"],
            posts=profile["posts"],
            activities=profile["activities"],
            job_title=profile.get("title", ""),
            job_started=profile.get("job_started", ""),
        )

        if not signals:
            print("  No signals detected")
            continue

        # Find or create person record
        person = airtable_client.find_person_by_linkedin(profile["linkedin_url"])
        person_id = person["id"] if person else None

        if not person:
            print(f"  Creating new person record...")
            new_person = airtable_client.create_person(
                name=profile["name"],
                linkedin_url=profile["linkedin_url"],
                title=profile["headline"],
            )
            person_id = new_person["id"]

        # Create signal records
        for sig in signals:
            print(f"  Signal: {sig['type']} (strength: {sig['strength']})")
            airtable_client.create_signal(
                signal_type=sig["type"],
                signal_strength=sig["strength"],
                source="LinkedIn",
                linkedin_url=profile["linkedin_url"],
                person_record_id=person_id,
            )
            signals_created += 1

    print(f"\n✅ Created {signals_created} signal records")
    return signals_created


def run_dashboard(send=True):
    """Generate and optionally send dashboard email"""
    print("\n" + "=" * 50)
    print("STEP 3: Dashboard Generation")
    print("=" * 50)

    # Fetch data
    ready = airtable_client.get_ready_prospects(10)
    warm = airtable_client.get_warm_prospects(10)
    signals = airtable_client.get_recent_signals(24)
    counts = airtable_client.count_by_status()

    print(f"Dashboard data:")
    print(f"  Ready prospects: {len(ready)}")
    print(f"  Warm prospects: {len(warm)}")
    print(f"  Recent signals: {len(signals)}")
    print(f"  Total counts: {counts}")

    if send:
        success = email_dashboard.send_dashboard_email(
            ready_prospects=ready,
            warm_prospects=warm,
            recent_signals=signals,
            counts=counts,
        )
        return success
    else:
        email_dashboard.preview_dashboard()
        return True


def run_full_pipeline():
    """Run the complete pipeline"""
    print("=" * 60)
    print("EXPERIENTIAL INTENT ENGINE - FULL PIPELINE")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    # Step 1: Collect
    results = run_collect()

    # Step 2: Process
    if results:
        run_process(results)
    else:
        print("\nSkipping processing (no data collected)")

    # Step 3: Dashboard
    run_dashboard(send=True)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print(f"Finished: {datetime.now().isoformat()}")
    print("=" * 60)


def run_collect_twitter():
    """Collect Twitter signals for tracked people using Apify"""
    print("=" * 50)
    print("Collecting Twitter Signals (via Apify)")
    print("=" * 50)

    # Get all people with Twitter handles or URLs
    people = airtable_client.get_people_with_twitter()
    print(f"Found {len(people)} people with Twitter info")

    if not people:
        print("No people with Twitter handles/URLs to process.")
        return []

    # Extract Twitter handles or URLs
    # collect_twitter_signals can handle both handles and URLs
    handles_or_urls = []
    for person in people:
        fields = person.get("fields", {})
        # Try Twitter Handle first, then Twitter URL
        handle = fields.get("Twitter Handle")
        if handle:
            handles_or_urls.append(handle)
        else:
            url = fields.get("Twitter URL")
            if url:
                # The collector will extract handle from URL
                handles_or_urls.append(url)

    print(f"Collecting signals for {len(handles_or_urls)} Twitter handles/URLs...")

    # Run Twitter collection via Apify
    results = twitter_collector.collect_twitter_signals(handles_or_urls)

    print(f"Got Twitter data for {len(results)} handles")
    return results


def run_collect_all():
    """
    Collect signals from ALL sources: LinkedIn + Twitter.

    Returns combined list of results from both sources.
    """
    print("=" * 60)
    print("COLLECTING ALL SIGNALS (LinkedIn + Twitter)")
    print("=" * 60)

    all_results = []

    # LinkedIn signals
    print("\n--- LinkedIn ---")
    linkedin_results = run_collect()
    if linkedin_results:
        for result in linkedin_results:
            result["source"] = "LinkedIn"
        all_results.extend(linkedin_results)

    # Twitter signals
    print("\n--- Twitter ---")
    twitter_results = run_collect_twitter()
    if twitter_results:
        for result in twitter_results:
            result["source"] = "Twitter"
        all_results.extend(twitter_results)

    print(f"\nTotal results: {len(all_results)}")
    print(f"  LinkedIn: {len(linkedin_results) if linkedin_results else 0}")
    print(f"  Twitter: {len(twitter_results) if twitter_results else 0}")

    return all_results


def run_companies():
    """Monitor tracked companies for signals"""
    print("\n" + "=" * 50)
    print("STEP: Company Signal Monitoring")
    print("=" * 50)

    result = company_monitor.monitor_companies()

    print(f"\nCompany monitoring complete")
    print(f"   Companies monitored: {result['companies']}")
    print(f"   Signals found: {result['signals']}")

    return result


def run_add_company(company_url: str, max_employees: int = 500):
    """Add a company's ICP employees to monitoring"""
    print("\n" + "=" * 50)
    print("Adding Company to Monitoring")
    print("=" * 50)

    result = employee_scraper.add_company(company_url, max_employees)

    print(f"\n✅ Company added")
    print(f"   Employees scraped: {result['total_scraped']}")
    print(f"   ICP matches: {result['icp_matches']}")
    print(f"   Added to monitoring: {result['added']}")

    return result


def run_cleanup_inactive(days: int = 90, grace_period_days: int = 30, dry_run: bool = True):
    """
    Clean up inactive contacts to reduce API costs and keep prospect list fresh.

    Args:
        days: Number of days without signals to be considered inactive (default: 90)
        grace_period_days: Protect recently added people (default: 30)
        dry_run: If True, only report what would be removed (default: True for safety)

    Returns:
        Summary dict with would_remove, removed, inactive_days, and people list
    """
    print("\n" + "=" * 50)
    print("CLEANUP: Inactive Contact Removal")
    print("=" * 50)
    print(f"Parameters:")
    print(f"  Inactive threshold: {days} days")
    print(f"  Grace period: {grace_period_days} days")
    print(f"  Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will archive)'}")
    print("-" * 50)

    result = airtable_client.cleanup_inactive(
        days=days,
        grace_period_days=grace_period_days,
        dry_run=dry_run,
    )

    if result["would_remove"] == 0:
        print("\nNo inactive contacts found.")
    else:
        print(f"\nFound {result['would_remove']} inactive contacts:")
        for person in result["people"]:
            print(f"  - {person['name']} ({person['id']})")

        if dry_run:
            print(f"\nDRY RUN: No contacts were removed.")
            print(f"Run with --execute to actually archive these contacts.")
        else:
            print(f"\nArchived {result['removed']} contacts.")

    return result


def run_add_profiles(urls_file_or_urls: str, company_name: str = None):
    """Add profiles from URLs (file path or comma-separated URLs)"""
    print("\n" + "=" * 50)
    print("Adding Profiles to Monitoring")
    print("=" * 50)

    # Check if it's a file or direct URLs
    import os
    if os.path.isfile(urls_file_or_urls):
        print(f"Reading URLs from file: {urls_file_or_urls}")
        with open(urls_file_or_urls) as f:
            urls = [line.strip() for line in f if line.strip() and "linkedin.com" in line]
    else:
        # Treat as comma-separated URLs
        urls = [u.strip() for u in urls_file_or_urls.split(",") if "linkedin.com" in u]

    print(f"Found {len(urls)} LinkedIn URLs")

    if not urls:
        print("❌ No valid LinkedIn URLs found")
        return {"added": 0}

    result = employee_scraper.add_profiles_from_urls(urls, company_name)

    print(f"\n✅ Profiles added")
    print(f"   Scraped: {result['total_scraped']}")
    print(f"   ICP matches: {result['icp_matches']}")
    print(f"   Added: {result['added']}")

    return result


def run_test():
    """Quick test of all components"""
    print("=" * 50)
    print("TESTING INTENT ENGINE COMPONENTS")
    print("=" * 50)

    print("\n1. Testing Airtable connection...")
    try:
        counts = airtable_client.count_by_status()
        print(f"   ✅ Connected. Status counts: {counts}")
    except Exception as e:
        print(f"   ❌ Airtable error: {e}")

    print("\n2. Testing OpenAI classifier...")
    try:
        signals = openai_classifier.classify_linkedin_activity(
            name="Test User",
            headline="VP Marketing",
            company="Test Corp",
            posts=[{"text": "Launching experiential campaign!", "likes": 10}],
            activities=[],
        )
        print(f"   ✅ Classifier working. Found {len(signals)} signals")
    except Exception as e:
        print(f"   ❌ OpenAI error: {e}")

    print("\n3. Testing Apify connection...")
    try:
        tasks = apify_collector.list_tasks()
        print(f"   ✅ Connected. Found {len(tasks)} existing tasks")
    except Exception as e:
        print(f"   ❌ Apify error: {e}")

    print("\n4. Testing dashboard generation...")
    try:
        email_dashboard.preview_dashboard()
        print("   ✅ Dashboard preview generated")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")

    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)


def run_discover(icp_name: str = None, limit: int = 50):
    """Discover new prospects matching ICP criteria"""
    print("\n" + "=" * 50)
    print("AUTO-PROSPECT DISCOVERY")
    print("=" * 50)

    if icp_name:
        # Discover for specific ICP
        result = prospect_discovery.discover_prospects(icp_name, limit)
        return result
    else:
        # Discover for all ICPs
        result = prospect_discovery.discover_all_icps(limit)
        return result


def run_learn():
    """Learn from human feedback on Lead Fit"""
    print("\n" + "=" * 50)
    print("LEARNING FROM FEEDBACK")
    print("=" * 50)

    result = prospect_discovery.learn_from_feedback()

    print(f"\nLearning complete:")
    print(f"  Feedback records: {result['feedback_count']}")
    print(f"  Good fit: {result.get('good_fit', 0)}")
    print(f"  Bad fit: {result.get('bad_fit', 0)}")
    print(f"  Learnings updated: {result['learnings_updated']}")

    return result


def run_list_icps():
    """List available ICP configurations"""
    print("\n" + "=" * 50)
    print("AVAILABLE ICPs")
    print("=" * 50)

    icps = icp_config.list_icps()
    for name in icps:
        config = icp_config.load_icp_config(name)
        display = icp_config.get_icp_display_name(name)
        print(f"\n  {display} ({name})")
        print(f"    Titles: {len(config.get('target_titles', []))}")
        print(f"    Industries: {len(config.get('target_industries', []))}")
        print(f"    Keywords: {len(config.get('keywords_in_profile', []))}")

    return icps


def main():
    parser = argparse.ArgumentParser(
        description="Experiential Intent Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  test         Test all components
  collect      Collect LinkedIn signals for tracked people
  process      Process signals through OpenAI classifier
  dashboard    Send daily dashboard email
  preview      Preview dashboard without sending
  companies    Monitor tracked companies for signals
  add-profiles Add profiles from URLs (file or comma-separated)
  cleanup      Remove inactive contacts (no signals in 90+ days)
  discover     Auto-discover prospects matching ICPs
  learn        Learn from Lead Fit feedback
  list-icps    List available ICP configurations
  full         Run complete pipeline

Examples:
  python -m tools.intent_engine.main full
  python -m tools.intent_engine.main add-profiles urls.txt
  python -m tools.intent_engine.main add-profiles "url1,url2,url3" --company "Acme Corp"
  python -m tools.intent_engine.main cleanup --days 90
  python -m tools.intent_engine.main cleanup --days 90 --execute
  python -m tools.intent_engine.main discover --icp megan_patel --limit 50
  python -m tools.intent_engine.main discover --all --limit 25
  python -m tools.intent_engine.main learn
  python -m tools.intent_engine.main list-icps
        """,
    )

    parser.add_argument(
        "command",
        choices=["test", "collect", "process", "dashboard", "preview", "companies", "add-profiles", "cleanup", "discover", "learn", "list-icps", "full"],
        help="Command to run",
    )

    parser.add_argument(
        "urls",
        nargs="?",
        default=None,
        help="LinkedIn URLs - file path or comma-separated (for add-profiles)",
    )

    parser.add_argument(
        "--company",
        type=str,
        default=None,
        help="Company name to associate with profiles",
    )

    parser.add_argument(
        "--max-employees",
        type=int,
        default=500,
        help="Maximum employees to scrape (default: 500)",
    )

    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Days of inactivity for cleanup (default: 90)",
    )

    parser.add_argument(
        "--grace-period",
        type=int,
        default=30,
        help="Grace period for new contacts in cleanup (default: 30)",
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform cleanup (without this flag, runs in dry-run mode)",
    )

    parser.add_argument(
        "--icp",
        type=str,
        default=None,
        help="ICP name for discovery (e.g., megan_patel, david_brown)",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        dest="all_icps",
        help="Discover prospects for all ICPs",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum prospects to discover per ICP (default: 50)",
    )

    args = parser.parse_args()

    if args.command == "test":
        run_test()
    elif args.command == "collect":
        run_collect()
    elif args.command == "process":
        run_process()
    elif args.command == "dashboard":
        run_dashboard(send=True)
    elif args.command == "preview":
        run_dashboard(send=False)
    elif args.command == "companies":
        run_companies()
    elif args.command == "add-profiles":
        if not args.urls:
            print("Error: Please provide LinkedIn URLs (file path or comma-separated)")
            print("Usage: python -m tools.intent_engine.main add-profiles urls.txt")
            print("   or: python -m tools.intent_engine.main add-profiles 'url1,url2' --company 'Acme'")
            sys.exit(1)
        run_add_profiles(args.urls, args.company)
    elif args.command == "cleanup":
        run_cleanup_inactive(
            days=args.days,
            grace_period_days=args.grace_period,
            dry_run=not args.execute,
        )
    elif args.command == "discover":
        if args.all_icps:
            run_discover(icp_name=None, limit=args.limit)
        elif args.icp:
            run_discover(icp_name=args.icp, limit=args.limit)
        else:
            print("Error: Please specify --icp <name> or --all")
            print("Available ICPs:", ", ".join(icp_config.list_icps()))
            sys.exit(1)
    elif args.command == "learn":
        run_learn()
    elif args.command == "list-icps":
        run_list_icps()
    elif args.command == "full":
        run_full_pipeline()


if __name__ == "__main__":
    main()
