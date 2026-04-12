#!/usr/bin/env python3
"""
Edit the Blog page via WordPress XML-RPC.
XML-RPC uses regular credentials and might work where REST API doesn't.
"""

import sys
from xmlrpc.client import ServerProxy, Error as XMLRPCError

# Configuration
WP_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"
BLOG_PAGE_ID = 95

HTML_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-blog-page-v2.html"


def main():
    print("=" * 70)
    print("WordPress XML-RPC Blog Page Editor")
    print("=" * 70)

    # Read HTML content
    try:
        with open(HTML_FILE, 'r') as f:
            html_content = f.read()
        print(f"HTML content loaded: {len(html_content)} characters")
    except FileNotFoundError:
        print(f"ERROR: HTML file not found: {HTML_FILE}")
        return 1

    # Connect to XML-RPC
    xmlrpc_url = f"{WP_URL}/xmlrpc.php"
    print(f"\n[Step 1] Connecting to XML-RPC at {xmlrpc_url}...")

    try:
        server = ServerProxy(xmlrpc_url)

        # Test connection with getUsersBlogs
        print("\n[Step 2] Testing authentication...")
        blogs = server.wp.getUsersBlogs(WP_USER, WP_PASS)
        print(f"  Authenticated! Found {len(blogs)} blog(s)")
        for blog in blogs:
            print(f"    - {blog.get('blogName', 'N/A')} (ID: {blog.get('blogid', 'N/A')})")

        blog_id = blogs[0]['blogid'] if blogs else 1

        # Get current page content
        print(f"\n[Step 3] Getting current page content (ID: {BLOG_PAGE_ID})...")
        page = server.wp.getPost(blog_id, WP_USER, WP_PASS, BLOG_PAGE_ID)
        print(f"  Page title: {page.get('post_title', 'N/A')}")
        print(f"  Page status: {page.get('post_status', 'N/A')}")
        print(f"  Content length: {len(page.get('post_content', ''))}")

        # Update page content
        print(f"\n[Step 4] Updating page content...")
        content = {
            'post_content': html_content,
        }

        result = server.wp.editPost(blog_id, WP_USER, WP_PASS, BLOG_PAGE_ID, content)
        if result:
            print("  SUCCESS! Page updated.")
        else:
            print("  Update returned False")

        # Verify
        print(f"\n[Step 5] Verifying update...")
        page = server.wp.getPost(blog_id, WP_USER, WP_PASS, BLOG_PAGE_ID)
        new_content = page.get('post_content', '')
        print(f"  New content length: {len(new_content)}")

        if 'purebrain-blog' in new_content.lower() or 'video-background' in new_content.lower():
            print("  Content verified! New HTML detected.")
        else:
            print("  Warning: Expected markers not found")
            print(f"  Content preview: {new_content[:300]}")

    except XMLRPCError as e:
        print(f"\nXML-RPC Error: {e}")
        if "403" in str(e) or "Forbidden" in str(e):
            print("\nXML-RPC might be disabled on this WordPress installation.")
            print("This is a common security measure.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("\nView the page at: https://purebrain.ai/blog/")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
