#!/usr/bin/env python3
"""
WordPress REST API Publisher for jaredsanborn.com

Publishes blog posts and uploads media to WordPress via REST API.
Uses Basic Auth with Application Password.

Usage:
    python tools/wordpress_publisher.py test
    python tools/wordpress_publisher.py publish --title "Title" --content "Content" --status draft
    python tools/wordpress_publisher.py upload-media --file /path/to/image.jpg
    python tools/wordpress_publisher.py list-posts
    python tools/wordpress_publisher.py list-categories
    python tools/wordpress_publisher.py list-tags

Requirements:
    pip install httpx python-dotenv

Environment Variables (in .env):
    WORDPRESS_URL=https://jaredsanborn.com
    WORDPRESS_USER=jared
    WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
"""

import argparse
import base64
import json
import mimetypes
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    import os
    # Load .env from project root
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")
    import os


@dataclass
class WordPressConfig:
    """WordPress API configuration."""
    url: str
    user: str
    app_password: str

    @classmethod
    def from_env(cls) -> "WordPressConfig":
        """Load configuration from environment variables."""
        url = os.getenv("WORDPRESS_URL")
        user = os.getenv("WORDPRESS_USER")
        app_password = os.getenv("WORDPRESS_APP_PASSWORD")

        if not url:
            raise ValueError("WORDPRESS_URL not set in environment")
        if not user:
            raise ValueError("WORDPRESS_USER not set in environment")
        if not app_password:
            raise ValueError("WORDPRESS_APP_PASSWORD not set in environment")

        # Normalize URL (remove trailing slash)
        url = url.rstrip("/")

        return cls(url=url, user=user, app_password=app_password)

    def get_auth_header(self) -> str:
        """Generate Basic Auth header value."""
        # WordPress app passwords may have spaces - they're valid
        credentials = f"{self.user}:{self.app_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"


class WordPressPublisher:
    """WordPress REST API client for publishing content."""

    def __init__(self, config: Optional[WordPressConfig] = None):
        """Initialize with config or load from environment."""
        self.config = config or WordPressConfig.from_env()
        self.api_base = f"{self.config.url}/wp-json/wp/v2"
        self.headers = {
            "Authorization": self.config.get_auth_header(),
            "Content-Type": "application/json"
        }
        self.client = httpx.Client(timeout=30)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def test_connection(self) -> dict:
        """
        Test API connection and authentication.

        Returns dict with:
            - success: bool
            - message: str
            - user_info: dict (if successful)
        """
        try:
            # First test if we can reach the API
            resp = self.client.get(f"{self.api_base}")
            if resp.status_code != 200:
                return {
                    "success": False,
                    "message": f"API not reachable: HTTP {resp.status_code}",
                    "user_info": None
                }

            # Test authentication by getting current user
            resp = self.client.get(
                f"{self.api_base}/users/me",
                headers=self.headers
            )

            if resp.status_code == 200:
                user_info = resp.json()
                return {
                    "success": True,
                    "message": f"Connected as: {user_info.get('name')} ({user_info.get('slug')})",
                    "user_info": user_info
                }
            elif resp.status_code == 401:
                return {
                    "success": False,
                    "message": "Authentication failed. Check WORDPRESS_USER and WORDPRESS_APP_PASSWORD",
                    "user_info": None
                }
            else:
                return {
                    "success": False,
                    "message": f"Unexpected response: HTTP {resp.status_code} - {resp.text}",
                    "user_info": None
                }

        except httpx.ConnectError as e:
            return {
                "success": False,
                "message": f"Connection failed: {e}",
                "user_info": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {e}",
                "user_info": None
            }

    def upload_media(self, file_path: str, alt_text: str = "", caption: str = "") -> dict:
        """
        Upload media file (image) to WordPress.

        Args:
            file_path: Path to the media file
            alt_text: Alt text for the image
            caption: Caption for the image

        Returns:
            dict with media ID and URL on success, or error info
        """
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        # Determine content type
        content_type, _ = mimetypes.guess_type(str(path))
        if not content_type:
            content_type = "application/octet-stream"

        # Read file
        with open(path, "rb") as f:
            file_content = f.read()

        # Prepare headers for file upload
        upload_headers = {
            "Authorization": self.config.get_auth_header(),
            "Content-Type": content_type,
            "Content-Disposition": f'attachment; filename="{path.name}"'
        }

        try:
            resp = self.client.post(
                f"{self.api_base}/media",
                headers=upload_headers,
                content=file_content
            )

            if resp.status_code in [200, 201]:
                media = resp.json()
                media_id = media.get("id")

                # Update alt text and caption if provided
                if alt_text or caption:
                    update_data = {}
                    if alt_text:
                        update_data["alt_text"] = alt_text
                    if caption:
                        update_data["caption"] = caption

                    self.client.post(
                        f"{self.api_base}/media/{media_id}",
                        headers=self.headers,
                        json=update_data
                    )

                return {
                    "success": True,
                    "media_id": media_id,
                    "url": media.get("source_url"),
                    "title": media.get("title", {}).get("rendered", "")
                }
            else:
                return {
                    "success": False,
                    "error": f"Upload failed: HTTP {resp.status_code} - {resp.text}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def publish_post(
        self,
        title: str,
        content: str,
        status: str = "draft",
        excerpt: str = "",
        featured_image_id: Optional[int] = None,
        categories: Optional[list] = None,
        tags: Optional[list] = None,
        slug: Optional[str] = None
    ) -> dict:
        """
        Publish a blog post.

        Args:
            title: Post title
            content: Post content (HTML)
            status: 'draft', 'publish', 'pending', 'private'
            excerpt: Post excerpt/summary
            featured_image_id: Media ID for featured image
            categories: List of category IDs or names
            tags: List of tag IDs or names
            slug: URL slug (auto-generated from title if not provided)

        Returns:
            dict with post ID and URL on success, or error info
        """
        if status not in ["draft", "publish", "pending", "private", "future"]:
            return {"success": False, "error": f"Invalid status: {status}"}

        post_data = {
            "title": title,
            "content": content,
            "status": status
        }

        if excerpt:
            post_data["excerpt"] = excerpt

        if featured_image_id:
            post_data["featured_media"] = featured_image_id

        if slug:
            post_data["slug"] = slug

        # Handle categories - can be IDs or names
        if categories:
            category_ids = self._resolve_categories(categories)
            if category_ids:
                post_data["categories"] = category_ids

        # Handle tags - can be IDs or names
        if tags:
            tag_ids = self._resolve_tags(tags)
            if tag_ids:
                post_data["tags"] = tag_ids

        try:
            resp = self.client.post(
                f"{self.api_base}/posts",
                headers=self.headers,
                json=post_data
            )

            if resp.status_code in [200, 201]:
                post = resp.json()
                return {
                    "success": True,
                    "post_id": post.get("id"),
                    "url": post.get("link"),
                    "status": post.get("status"),
                    "title": post.get("title", {}).get("rendered", title)
                }
            else:
                return {
                    "success": False,
                    "error": f"Publish failed: HTTP {resp.status_code} - {resp.text}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _resolve_categories(self, categories: list) -> list:
        """Convert category names to IDs if needed."""
        category_ids = []
        for cat in categories:
            if isinstance(cat, int):
                category_ids.append(cat)
            else:
                # Try to find by name
                cat_id = self._get_category_id_by_name(str(cat))
                if cat_id:
                    category_ids.append(cat_id)
        return category_ids

    def _resolve_tags(self, tags: list) -> list:
        """Convert tag names to IDs, creating if necessary."""
        tag_ids = []
        for tag in tags:
            if isinstance(tag, int):
                tag_ids.append(tag)
            else:
                # Try to find or create tag
                tag_id = self._get_or_create_tag(str(tag))
                if tag_id:
                    tag_ids.append(tag_id)
        return tag_ids

    def _get_category_id_by_name(self, name: str) -> Optional[int]:
        """Get category ID by name."""
        try:
            resp = self.client.get(
                f"{self.api_base}/categories",
                headers=self.headers,
                params={"search": name, "per_page": 10}
            )
            if resp.status_code == 200:
                categories = resp.json()
                # Find exact match (case-insensitive)
                for cat in categories:
                    if cat.get("name", "").lower() == name.lower():
                        return cat.get("id")
                # If no exact match, return first partial match
                if categories:
                    return categories[0].get("id")
            return None
        except Exception:
            return None

    def _get_or_create_tag(self, name: str) -> Optional[int]:
        """Get tag ID by name, creating if it doesn't exist."""
        try:
            # Try to find existing tag
            resp = self.client.get(
                f"{self.api_base}/tags",
                headers=self.headers,
                params={"search": name, "per_page": 10}
            )
            if resp.status_code == 200:
                tags = resp.json()
                for tag in tags:
                    if tag.get("name", "").lower() == name.lower():
                        return tag.get("id")

            # Tag doesn't exist - create it
            resp = self.client.post(
                f"{self.api_base}/tags",
                headers=self.headers,
                json={"name": name}
            )
            if resp.status_code in [200, 201]:
                return resp.json().get("id")

            return None
        except Exception:
            return None

    def list_posts(self, limit: int = 10, status: str = "any") -> list:
        """List recent posts."""
        try:
            params = {"per_page": limit}
            if status != "any":
                params["status"] = status

            resp = self.client.get(
                f"{self.api_base}/posts",
                headers=self.headers,
                params=params
            )

            if resp.status_code == 200:
                posts = resp.json()
                return [{
                    "id": p.get("id"),
                    "title": p.get("title", {}).get("rendered", ""),
                    "status": p.get("status"),
                    "url": p.get("link"),
                    "date": p.get("date")
                } for p in posts]
            return []
        except Exception:
            return []

    def list_categories(self) -> list:
        """List all categories."""
        try:
            resp = self.client.get(
                f"{self.api_base}/categories",
                headers=self.headers,
                params={"per_page": 100}
            )

            if resp.status_code == 200:
                return [{
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "slug": c.get("slug"),
                    "count": c.get("count")
                } for c in resp.json()]
            return []
        except Exception:
            return []

    def list_tags(self) -> list:
        """List all tags."""
        try:
            resp = self.client.get(
                f"{self.api_base}/tags",
                headers=self.headers,
                params={"per_page": 100}
            )

            if resp.status_code == 200:
                return [{
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "slug": t.get("slug"),
                    "count": t.get("count")
                } for t in resp.json()]
            return []
        except Exception:
            return []


def main():
    """CLI interface for WordPress publisher."""
    parser = argparse.ArgumentParser(
        description="WordPress REST API Publisher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    Test connection:
        python wordpress_publisher.py test

    Publish draft post:
        python wordpress_publisher.py publish --title "My Post" --content "<p>Hello World</p>" --status draft

    Publish with categories and tags:
        python wordpress_publisher.py publish --title "AI Update" --content "<p>Content here</p>" \\
            --categories "AI" "Technology" --tags "machine-learning" "claude"

    Upload media:
        python wordpress_publisher.py upload-media --file /path/to/image.jpg --alt "Image description"

    List posts:
        python wordpress_publisher.py list-posts --limit 5

    Publish from file:
        python wordpress_publisher.py publish --title "My Post" --content-file post.html --status publish
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test API connection")

    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish a blog post")
    publish_parser.add_argument("--title", required=True, help="Post title")
    publish_parser.add_argument("--content", help="Post content (HTML)")
    publish_parser.add_argument("--content-file", help="Read content from file")
    publish_parser.add_argument("--status", default="draft",
                               choices=["draft", "publish", "pending", "private"],
                               help="Post status (default: draft)")
    publish_parser.add_argument("--excerpt", help="Post excerpt/summary")
    publish_parser.add_argument("--featured-image", type=int, help="Featured image media ID")
    publish_parser.add_argument("--categories", nargs="+", help="Category names or IDs")
    publish_parser.add_argument("--tags", nargs="+", help="Tag names (will be created if needed)")
    publish_parser.add_argument("--slug", help="URL slug")

    # Upload media command
    media_parser = subparsers.add_parser("upload-media", help="Upload media file")
    media_parser.add_argument("--file", required=True, help="Path to media file")
    media_parser.add_argument("--alt", default="", help="Alt text")
    media_parser.add_argument("--caption", default="", help="Caption")

    # List posts command
    list_posts_parser = subparsers.add_parser("list-posts", help="List recent posts")
    list_posts_parser.add_argument("--limit", type=int, default=10, help="Number of posts")
    list_posts_parser.add_argument("--status", default="any", help="Filter by status")

    # List categories command
    subparsers.add_parser("list-categories", help="List all categories")

    # List tags command
    subparsers.add_parser("list-tags", help="List all tags")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        with WordPressPublisher() as wp:
            if args.command == "test":
                print("Testing WordPress API connection...")
                result = wp.test_connection()
                if result["success"]:
                    print(f"SUCCESS: {result['message']}")
                    user = result.get("user_info", {})
                    if user:
                        print(f"  User ID: {user.get('id')}")
                        print(f"  Roles: {', '.join(user.get('roles', []))}")
                        print(f"  URL: {user.get('url')}")
                else:
                    print(f"FAILED: {result['message']}")
                    sys.exit(1)

            elif args.command == "publish":
                # Get content from file or argument
                if args.content_file:
                    content_path = Path(args.content_file)
                    if not content_path.exists():
                        print(f"Error: Content file not found: {args.content_file}")
                        sys.exit(1)
                    content = content_path.read_text()
                elif args.content:
                    content = args.content
                else:
                    print("Error: Must provide --content or --content-file")
                    sys.exit(1)

                print(f"Publishing post: {args.title}")
                result = wp.publish_post(
                    title=args.title,
                    content=content,
                    status=args.status,
                    excerpt=args.excerpt or "",
                    featured_image_id=args.featured_image,
                    categories=args.categories,
                    tags=args.tags,
                    slug=args.slug
                )

                if result["success"]:
                    print(f"SUCCESS: Post published!")
                    print(f"  Post ID: {result['post_id']}")
                    print(f"  Status: {result['status']}")
                    print(f"  URL: {result['url']}")
                else:
                    print(f"FAILED: {result['error']}")
                    sys.exit(1)

            elif args.command == "upload-media":
                print(f"Uploading: {args.file}")
                result = wp.upload_media(args.file, args.alt, args.caption)

                if result["success"]:
                    print(f"SUCCESS: Media uploaded!")
                    print(f"  Media ID: {result['media_id']}")
                    print(f"  URL: {result['url']}")
                else:
                    print(f"FAILED: {result['error']}")
                    sys.exit(1)

            elif args.command == "list-posts":
                posts = wp.list_posts(limit=args.limit, status=args.status)
                if posts:
                    print(f"Recent posts ({len(posts)}):")
                    for post in posts:
                        print(f"  [{post['id']}] {post['status']:8} | {post['title'][:50]}")
                        print(f"          {post['url']}")
                else:
                    print("No posts found.")

            elif args.command == "list-categories":
                categories = wp.list_categories()
                if categories:
                    print(f"Categories ({len(categories)}):")
                    for cat in categories:
                        print(f"  [{cat['id']:3}] {cat['name']} ({cat['count']} posts)")
                else:
                    print("No categories found.")

            elif args.command == "list-tags":
                tags = wp.list_tags()
                if tags:
                    print(f"Tags ({len(tags)}):")
                    for tag in tags:
                        print(f"  [{tag['id']:3}] {tag['name']} ({tag['count']} posts)")
                else:
                    print("No tags found.")

    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
