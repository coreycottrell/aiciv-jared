#!/usr/bin/env python3
"""
Emergency Blog Reschedule - Feb 16, 2026
Reschedule Pilot Purgatory to tomorrow, schedule Enterprise-Ready AI for today
"""

import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

def load_env():
    """Load environment variables from .env file"""
    env_vars = {}
    env_path = '/home/jared/projects/AI-CIV/aether/.env'
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars

def reschedule_post(site_url, auth, post_id, new_datetime):
    """Reschedule an existing post to a new datetime"""
    response = requests.post(
        f'{site_url}/wp-json/wp/v2/posts/{post_id}',
        auth=auth,
        json={
            'date': new_datetime,
            'status': 'future'
        }
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"  ❌ Reschedule failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def main():
    env = load_env()

    # Site 1: jareddsanborn.com
    site1_url = 'https://jareddsanborn.com'
    site1_auth = HTTPBasicAuth(
        env.get('WORDPRESS_USER'),
        env.get('WORDPRESS_APP_PASSWORD')
    )

    # Site 2: purebrain.ai
    site2_url = 'https://purebrain.ai'
    site2_auth = HTTPBasicAuth(
        'Aether',
        env.get('PUREBRAIN_WP_APP_PASSWORD')
    )

    print("\n" + "="*70)
    print("BLOG SCHEDULE EMERGENCY SHIFT - FEB 16, 2026")
    print("="*70)

    # Task 1: Reschedule Pilot Purgatory to tomorrow 9am ET (14:00 UTC)
    print("\n🔄 TASK 1: Rescheduling Pilot Purgatory to Feb 17, 9am ET...")

    print("\n  📍 jareddsanborn.com (Post ID: 1047)...")
    result1 = reschedule_post(site1_url, site1_auth, 1047, '2026-02-17T14:00:00')
    if result1:
        print(f"  ✅ Rescheduled to {result1.get('date')}")
        print(f"     URL: {result1.get('link')}")

    print("\n  📍 purebrain.ai (Post ID: 241)...")
    result2 = reschedule_post(site2_url, site2_auth, 241, '2026-02-17T14:00:00')
    if result2:
        print(f"  ✅ Rescheduled to {result2.get('date')}")
        print(f"     URL: {result2.get('link')}")

    print("\n" + "="*70)
    print("PILOT PURGATORY RESCHEDULED SUCCESSFULLY")
    print("="*70)

    # Task 2 will be handled by schedule_dual_blog.py
    print("\n✨ Ready for Task 2: Schedule Enterprise-Ready AI for today 8am ET")
    print("   Run: python3 tools/schedule_dual_blog.py \\")
    print("        'Most AI Agents Break the Moment You Ask Where the Data Goes' \\")
    print("        exports/blog-content/2026-02-15-enterprise-ready-ai/blog.md \\")
    print("        '2026-02-16T13:00:00' \\")
    print("        exports/blog-content/2026-02-15-enterprise-ready-ai/blog-header.png")

if __name__ == "__main__":
    main()
