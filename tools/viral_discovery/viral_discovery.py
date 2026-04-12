#!/usr/bin/env python3
"""
Viral Content Discovery Engine

Finds viral/trending content across platforms related to Jared's ICPs and niches.
Uses Apify actors for scraping without needing platform API credentials.

Platforms:
- LinkedIn (post search)
- Twitter/X (keyword search)
- Reddit (subreddit posts)
- TikTok (hashtag videos)
- Instagram (hashtag posts)
- Google Trends (rising topics)

Set APIFY_API_KEY in .env file.
"""

import os
import sys
import json
import time
import yaml
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from intent_engine.config import APIFY_API_KEY
except ImportError:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
    APIFY_API_KEY = os.getenv("APIFY_API_KEY")

# ============================================================================
# APIFY ACTOR CONFIGURATION
# ============================================================================

# Recommended actors from research (cost-effective, reliable)
ACTORS = {
    # LinkedIn - post search by keywords (no login required)
    "linkedin": "harvestapi~linkedin-post-search",  # $2/1k posts, no cookies

    # Twitter/X - keyword search
    "twitter": "apidojo/tweet-scraper",  # Reliable, cost-effective

    # Reddit - subreddit scraper
    "reddit": "trudax/reddit-scraper",  # Good community support

    # TikTok - hashtag/keyword search
    "tiktok": "clockworks/tiktok-scraper",  # Most popular, full-featured

    # Instagram - hashtag scraper
    "instagram": "apify/instagram-hashtag-scraper",  # Official, $2.60/1k

    # Google Trends - trending topics
    "google_trends": "apify/google-trends-scraper",  # Official, well-maintained
}

# Alternative actors (fallbacks)
ALT_ACTORS = {
    "linkedin": "curious_coder/linkedin-post-search-scraper",
    "twitter": "quacker/twitter-scraper",
    "reddit": "crawlerbros/reddit-scraper",
    "tiktok": "apidojo/tiktok-scraper",
    "instagram": "instaprism/instagram-hashtag-scraper",
}

# Cache settings
CACHE_DIR = Path(__file__).parent.parent.parent / ".cache" / "viral_discovery"
CACHE_HOURS = 12  # Re-scrape after 12 hours

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ViralContent:
    """Represents a piece of viral/trending content."""
    platform: str
    content_type: str  # post, video, thread, etc.
    title: str
    text: str
    url: str
    author: str
    author_url: str
    engagement: Dict[str, int]  # likes, comments, shares, views, etc.
    timestamp: str
    relevance_score: float  # 0-100
    categories: List[str]
    keywords_matched: List[str]
    raw_data: Dict  # Original scraped data


# ============================================================================
# MAIN CLASS
# ============================================================================

class ViralContentDiscovery:
    """
    Discovers viral content across platforms for trend riding and engagement.

    Usage:
        discovery = ViralContentDiscovery()

        # Discover across all platforms
        results = discovery.discover_all()

        # Platform-specific discovery
        linkedin = discovery.discover_linkedin_viral(min_engagement=100)
        twitter = discovery.discover_twitter_trending(min_retweets=50)
        reddit = discovery.discover_reddit_discussions(min_upvotes=100)
        tiktok = discovery.discover_tiktok_trends(min_views=10000)
        instagram = discovery.discover_instagram_activations(min_likes=500)
        trends = discovery.get_trending_topics()

        # Generate actionable digest
        digest = discovery.generate_daily_digest()
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize discovery engine with niche configuration."""
        self.api_key = APIFY_API_KEY
        if not self.api_key:
            print("WARNING: APIFY_API_KEY not set. Viral discovery disabled.")

        # Load niche config
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = Path(__file__).parent / "niche_config.yaml"

        if config_file.exists():
            with open(config_file) as f:
                self.config = yaml.safe_load(f)
        else:
            print(f"WARNING: Config not found at {config_file}")
            self.config = self._default_config()

        # Ensure cache directory exists
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Results storage
        self.results: Dict[str, List[ViralContent]] = {}

    def _default_config(self) -> Dict:
        """Return minimal default config."""
        return {
            "keywords": {
                "primary": ["experiential marketing", "brand activation", "CPG marketing"],
                "secondary": ["marketing ROI", "brand building"]
            },
            "hashtags": {
                "linkedin": ["marketing", "brandmarketing"],
                "twitter": ["MarketingTwitter"],
                "tiktok": ["marketingtips"],
                "instagram": ["brandactivation"]
            },
            "subreddits": {"primary": ["marketing", "Entrepreneur"]},
            "engagement_thresholds": {
                "linkedin": {"reactions": 100},
                "twitter": {"retweets": 50},
                "reddit": {"upvotes": 100},
                "tiktok": {"views": 10000},
                "instagram": {"likes": 500}
            },
            "exclude_keywords": ["hiring", "job posting"]
        }

    # ========================================================================
    # APIFY HELPERS
    # ========================================================================

    def _run_actor(self, actor_id: str, payload: Dict, timeout: int = 600) -> List[Dict]:
        """Run an Apify actor and return results."""
        if not self.api_key:
            print(f"  Skipping {actor_id} - no API key")
            return []

        # Start run
        url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={self.api_key}"
        try:
            print(f"  Starting actor: {actor_id}")
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            run_id = resp.json()["data"]["id"]
            print(f"    Run ID: {run_id}")

            return self._wait_for_run(run_id, timeout)
        except requests.exceptions.RequestException as e:
            print(f"  Error starting {actor_id}: {e}")
            return []

    def _wait_for_run(self, run_id: str, timeout: int = 600, poll: int = 10) -> List[Dict]:
        """Wait for Apify run to complete and return results."""
        start = time.time()

        while time.time() - start < timeout:
            url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.api_key}"
            resp = requests.get(url)
            resp.raise_for_status()
            status = resp.json()["data"]

            state = status.get("status")
            if state == "SUCCEEDED":
                dataset_id = status.get("defaultDatasetId")
                if dataset_id:
                    items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={self.api_key}"
                    items_resp = requests.get(items_url)
                    items_resp.raise_for_status()
                    return items_resp.json()
                return []
            elif state in ["FAILED", "ABORTED", "TIMED-OUT"]:
                print(f"    Run failed: {state}")
                return []

            print(f"    Status: {state}...")
            time.sleep(poll)

        print(f"    Timeout after {timeout}s")
        return []

    def _get_cache_key(self, platform: str, params: Dict) -> str:
        """Generate cache key for a query."""
        params_str = json.dumps(params, sort_keys=True)
        hash_val = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{platform}_{hash_val}"

    def _load_cache(self, cache_key: str) -> Optional[List[Dict]]:
        """Load cached results if fresh."""
        cache_file = CACHE_DIR / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                cached_time = datetime.fromisoformat(data.get("timestamp", ""))
                if datetime.now() - cached_time < timedelta(hours=CACHE_HOURS):
                    print(f"  Using cached data ({cache_key})")
                    return data.get("results", [])
            except Exception:
                pass
        return None

    def _save_cache(self, cache_key: str, results: List[Dict]):
        """Save results to cache."""
        cache_file = CACHE_DIR / f"{cache_key}.json"
        with open(cache_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results
            }, f, indent=2, default=str)

    # ========================================================================
    # PLATFORM-SPECIFIC DISCOVERY
    # ========================================================================

    def discover_linkedin_viral(self,
                                 keywords: Optional[List[str]] = None,
                                 min_engagement: int = 100,
                                 max_posts: int = 100,
                                 use_cache: bool = True) -> List[ViralContent]:
        """
        Find viral LinkedIn posts in our niches.

        Args:
            keywords: Search keywords (default: from config)
            min_engagement: Minimum reactions to include
            max_posts: Maximum posts per keyword
            use_cache: Use cached results if available

        Returns:
            List of ViralContent objects
        """
        print("\n[LinkedIn] Discovering viral posts...")

        keywords = keywords or self.config["keywords"]["primary"][:5]  # Top 5

        all_results = []
        for keyword in keywords:
            params = {"keyword": keyword, "maxPosts": max_posts}
            cache_key = self._get_cache_key("linkedin", params)

            if use_cache:
                cached = self._load_cache(cache_key)
                if cached:
                    all_results.extend(cached)
                    continue

            # Build search URL (LinkedIn public search)
            payload = {
                "searchUrl": f"https://www.linkedin.com/search/results/content/?keywords={keyword.replace(' ', '%20')}&sortBy=%22relevance%22",
                "maxPosts": max_posts,
            }

            raw_posts = self._run_actor(ACTORS["linkedin"], payload)
            self._save_cache(cache_key, raw_posts)
            all_results.extend(raw_posts)

        # Parse and filter
        viral_content = []
        for post in all_results:
            reactions = post.get("reactions", post.get("likeCount", 0))
            if reactions < min_engagement:
                continue

            if self._is_excluded(post.get("text", "")):
                continue

            content = ViralContent(
                platform="linkedin",
                content_type="post",
                title="",  # LinkedIn posts don't have titles
                text=post.get("text", "")[:500],
                url=post.get("postUrl", post.get("url", "")),
                author=post.get("authorName", post.get("author", {}).get("name", "Unknown")),
                author_url=post.get("authorUrl", ""),
                engagement={
                    "reactions": reactions,
                    "comments": post.get("comments", post.get("commentCount", 0)),
                    "shares": post.get("shares", post.get("shareCount", 0)),
                },
                timestamp=post.get("postedAt", post.get("timestamp", "")),
                relevance_score=self._score_relevance(post.get("text", ""), "linkedin"),
                categories=self._categorize_content(post.get("text", "")),
                keywords_matched=self._find_matched_keywords(post.get("text", "")),
                raw_data=post
            )
            viral_content.append(content)

        # Sort by engagement
        viral_content.sort(key=lambda x: x.engagement.get("reactions", 0), reverse=True)

        print(f"  Found {len(viral_content)} viral LinkedIn posts")
        self.results["linkedin"] = viral_content
        return viral_content

    def discover_twitter_trending(self,
                                   keywords: Optional[List[str]] = None,
                                   min_retweets: int = 50,
                                   max_tweets: int = 100,
                                   use_cache: bool = True) -> List[ViralContent]:
        """
        Find trending tweets we can engage with.

        Args:
            keywords: Search keywords (default: from config)
            min_retweets: Minimum retweets to include
            max_tweets: Maximum tweets per keyword
            use_cache: Use cached results if available

        Returns:
            List of ViralContent objects
        """
        print("\n[Twitter] Discovering trending tweets...")

        keywords = keywords or self.config["keywords"]["primary"][:5]

        all_results = []
        for keyword in keywords:
            params = {"keyword": keyword, "maxTweets": max_tweets}
            cache_key = self._get_cache_key("twitter", params)

            if use_cache:
                cached = self._load_cache(cache_key)
                if cached:
                    all_results.extend(cached)
                    continue

            payload = {
                "searchTerms": [keyword],
                "maxTweets": max_tweets,
                "includeReplies": False,
            }

            raw_tweets = self._run_actor(ACTORS["twitter"], payload)
            self._save_cache(cache_key, raw_tweets)
            all_results.extend(raw_tweets)

        # Parse and filter
        viral_content = []
        for tweet in all_results:
            retweets = tweet.get("retweet_count", tweet.get("retweetCount", 0))
            if retweets < min_retweets:
                continue

            text = tweet.get("full_text", tweet.get("text", ""))
            if self._is_excluded(text):
                continue

            user = tweet.get("user", {})
            content = ViralContent(
                platform="twitter",
                content_type="tweet",
                title="",
                text=text[:500],
                url=tweet.get("url", f"https://twitter.com/{user.get('screen_name', '')}/status/{tweet.get('id_str', '')}"),
                author=user.get("name", tweet.get("author", "Unknown")),
                author_url=f"https://twitter.com/{user.get('screen_name', '')}",
                engagement={
                    "retweets": retweets,
                    "likes": tweet.get("favorite_count", tweet.get("likeCount", 0)),
                    "replies": tweet.get("reply_count", tweet.get("replyCount", 0)),
                },
                timestamp=tweet.get("created_at", tweet.get("timestamp", "")),
                relevance_score=self._score_relevance(text, "twitter"),
                categories=self._categorize_content(text),
                keywords_matched=self._find_matched_keywords(text),
                raw_data=tweet
            )
            viral_content.append(content)

        viral_content.sort(key=lambda x: x.engagement.get("retweets", 0), reverse=True)

        print(f"  Found {len(viral_content)} trending tweets")
        self.results["twitter"] = viral_content
        return viral_content

    def discover_reddit_discussions(self,
                                     subreddits: Optional[List[str]] = None,
                                     min_upvotes: int = 100,
                                     max_posts: int = 50,
                                     use_cache: bool = True) -> List[ViralContent]:
        """
        Find hot Reddit discussions to join or reference.

        Args:
            subreddits: Subreddits to search (default: from config)
            min_upvotes: Minimum upvotes to include
            max_posts: Maximum posts per subreddit
            use_cache: Use cached results if available

        Returns:
            List of ViralContent objects
        """
        print("\n[Reddit] Discovering hot discussions...")

        subreddits = subreddits or self.config["subreddits"].get("primary", ["marketing"])

        all_results = []
        for subreddit in subreddits:
            params = {"subreddit": subreddit, "maxPosts": max_posts}
            cache_key = self._get_cache_key("reddit", params)

            if use_cache:
                cached = self._load_cache(cache_key)
                if cached:
                    all_results.extend(cached)
                    continue

            payload = {
                "startUrls": [f"https://www.reddit.com/r/{subreddit}/hot/"],
                "maxPosts": max_posts,
                "sort": "hot",
            }

            raw_posts = self._run_actor(ACTORS["reddit"], payload)
            self._save_cache(cache_key, raw_posts)
            all_results.extend(raw_posts)

        # Parse and filter
        viral_content = []
        for post in all_results:
            upvotes = post.get("score", post.get("ups", post.get("upvotes", 0)))
            if upvotes < min_upvotes:
                continue

            title = post.get("title", "")
            text = post.get("selftext", post.get("body", ""))
            if self._is_excluded(title + " " + text):
                continue

            content = ViralContent(
                platform="reddit",
                content_type="post",
                title=title,
                text=text[:500],
                url=post.get("url", post.get("permalink", "")),
                author=post.get("author", "Unknown"),
                author_url=f"https://reddit.com/user/{post.get('author', '')}",
                engagement={
                    "upvotes": upvotes,
                    "comments": post.get("num_comments", post.get("commentCount", 0)),
                    "ratio": post.get("upvote_ratio", 0),
                },
                timestamp=post.get("created_utc", post.get("timestamp", "")),
                relevance_score=self._score_relevance(title + " " + text, "reddit"),
                categories=self._categorize_content(title + " " + text),
                keywords_matched=self._find_matched_keywords(title + " " + text),
                raw_data=post
            )
            viral_content.append(content)

        viral_content.sort(key=lambda x: x.engagement.get("upvotes", 0), reverse=True)

        print(f"  Found {len(viral_content)} hot Reddit discussions")
        self.results["reddit"] = viral_content
        return viral_content

    def discover_tiktok_trends(self,
                                hashtags: Optional[List[str]] = None,
                                min_views: int = 10000,
                                max_videos: int = 50,
                                use_cache: bool = True) -> List[ViralContent]:
        """
        Find viral TikTok content in our space.

        Args:
            hashtags: Hashtags to search (default: from config)
            min_views: Minimum views to include
            max_videos: Maximum videos per hashtag
            use_cache: Use cached results if available

        Returns:
            List of ViralContent objects
        """
        print("\n[TikTok] Discovering viral videos...")

        hashtags = hashtags or self.config["hashtags"].get("tiktok", ["marketingtips"])[:5]

        all_results = []
        for hashtag in hashtags:
            params = {"hashtag": hashtag, "maxVideos": max_videos}
            cache_key = self._get_cache_key("tiktok", params)

            if use_cache:
                cached = self._load_cache(cache_key)
                if cached:
                    all_results.extend(cached)
                    continue

            payload = {
                "hashtags": [hashtag],
                "resultsPerPage": max_videos,
            }

            raw_videos = self._run_actor(ACTORS["tiktok"], payload)
            self._save_cache(cache_key, raw_videos)
            all_results.extend(raw_videos)

        # Parse and filter
        viral_content = []
        for video in all_results:
            views = video.get("playCount", video.get("views", 0))
            if views < min_views:
                continue

            text = video.get("text", video.get("desc", ""))
            if self._is_excluded(text):
                continue

            author_data = video.get("author", video.get("authorMeta", {}))
            content = ViralContent(
                platform="tiktok",
                content_type="video",
                title="",
                text=text[:500],
                url=video.get("webVideoUrl", video.get("url", "")),
                author=author_data.get("nickname", author_data.get("name", "Unknown")),
                author_url=f"https://tiktok.com/@{author_data.get('uniqueId', author_data.get('id', ''))}",
                engagement={
                    "views": views,
                    "likes": video.get("diggCount", video.get("likes", 0)),
                    "comments": video.get("commentCount", video.get("comments", 0)),
                    "shares": video.get("shareCount", video.get("shares", 0)),
                },
                timestamp=video.get("createTime", video.get("timestamp", "")),
                relevance_score=self._score_relevance(text, "tiktok"),
                categories=self._categorize_content(text),
                keywords_matched=self._find_matched_keywords(text),
                raw_data=video
            )
            viral_content.append(content)

        viral_content.sort(key=lambda x: x.engagement.get("views", 0), reverse=True)

        print(f"  Found {len(viral_content)} viral TikTok videos")
        self.results["tiktok"] = viral_content
        return viral_content

    def discover_instagram_activations(self,
                                        hashtags: Optional[List[str]] = None,
                                        min_likes: int = 500,
                                        max_posts: int = 50,
                                        use_cache: bool = True) -> List[ViralContent]:
        """
        Find brand activations and experiential content on Instagram.

        Args:
            hashtags: Hashtags to search (default: from config)
            min_likes: Minimum likes to include
            max_posts: Maximum posts per hashtag
            use_cache: Use cached results if available

        Returns:
            List of ViralContent objects
        """
        print("\n[Instagram] Discovering brand activations...")

        hashtags = hashtags or self.config["hashtags"].get("instagram", ["brandactivation"])[:5]

        all_results = []
        for hashtag in hashtags:
            params = {"hashtag": hashtag, "maxPosts": max_posts}
            cache_key = self._get_cache_key("instagram", params)

            if use_cache:
                cached = self._load_cache(cache_key)
                if cached:
                    all_results.extend(cached)
                    continue

            payload = {
                "hashtags": [hashtag],
                "resultsLimit": max_posts,
            }

            raw_posts = self._run_actor(ACTORS["instagram"], payload)
            self._save_cache(cache_key, raw_posts)
            all_results.extend(raw_posts)

        # Parse and filter
        viral_content = []
        for post in all_results:
            likes = post.get("likesCount", post.get("likes", 0))
            if likes < min_likes:
                continue

            text = post.get("caption", post.get("text", ""))
            if self._is_excluded(text):
                continue

            owner = post.get("ownerUsername", post.get("owner", {}).get("username", ""))
            content = ViralContent(
                platform="instagram",
                content_type="post",
                title="",
                text=text[:500],
                url=post.get("url", post.get("shortCode", "")),
                author=owner,
                author_url=f"https://instagram.com/{owner}",
                engagement={
                    "likes": likes,
                    "comments": post.get("commentsCount", post.get("comments", 0)),
                },
                timestamp=post.get("timestamp", post.get("takenAt", "")),
                relevance_score=self._score_relevance(text, "instagram"),
                categories=self._categorize_content(text),
                keywords_matched=self._find_matched_keywords(text),
                raw_data=post
            )
            viral_content.append(content)

        viral_content.sort(key=lambda x: x.engagement.get("likes", 0), reverse=True)

        print(f"  Found {len(viral_content)} Instagram activations")
        self.results["instagram"] = viral_content
        return viral_content

    def get_trending_topics(self,
                            keywords: Optional[List[str]] = None,
                            geo: str = "US",
                            use_cache: bool = True) -> List[Dict]:
        """
        Get trending topics from Google Trends.

        Args:
            keywords: Keywords to track (default: from config)
            geo: Geographic region (default: US)
            use_cache: Use cached results if available

        Returns:
            List of trending topic dicts
        """
        print("\n[Google Trends] Getting trending topics...")

        keywords = keywords or self.config["keywords"]["primary"][:10]

        params = {"keywords": keywords, "geo": geo}
        cache_key = self._get_cache_key("trends", params)

        if use_cache:
            cached = self._load_cache(cache_key)
            if cached:
                return cached

        payload = {
            "searchTerms": keywords,
            "geo": geo,
            "timeRange": "now 7-d",  # Last 7 days
            "isPublic": True,
        }

        results = self._run_actor(ACTORS["google_trends"], payload)
        self._save_cache(cache_key, results)

        # Process results
        trending = []
        for item in results:
            trending.append({
                "keyword": item.get("keyword", item.get("term", "")),
                "interest": item.get("interest", item.get("value", 0)),
                "rising": item.get("rising", []),
                "related_queries": item.get("relatedQueries", []),
                "related_topics": item.get("relatedTopics", []),
            })

        print(f"  Got trends for {len(trending)} keywords")
        return trending

    # ========================================================================
    # SCORING AND FILTERING
    # ========================================================================

    def _score_relevance(self, text: str, platform: str) -> float:
        """
        Score content relevance to our ICPs (0-100).

        Higher score = more relevant to Jared's niches.
        """
        if not text:
            return 0.0

        text_lower = text.lower()
        score = 0.0

        # Primary keyword match (high weight)
        primary_keywords = self.config["keywords"].get("primary", [])
        for kw in primary_keywords:
            if kw.lower() in text_lower:
                score += 15.0

        # Secondary keyword match (medium weight)
        secondary_keywords = self.config["keywords"].get("secondary", [])
        for kw in secondary_keywords:
            if kw.lower() in text_lower:
                score += 7.0

        # Hashtag match (platform-specific)
        platform_hashtags = self.config["hashtags"].get(platform, [])
        for tag in platform_hashtags:
            if f"#{tag.lower()}" in text_lower or tag.lower() in text_lower:
                score += 5.0

        # Brand mention bonus
        brands = self.config.get("brands_to_watch", {})
        for brand_list in brands.values():
            for brand in brand_list:
                if brand.lower() in text_lower:
                    score += 10.0
                    break

        # Cap at 100
        return min(score, 100.0)

    def _categorize_content(self, text: str) -> List[str]:
        """Assign categories to content based on text analysis."""
        if not text:
            return []

        text_lower = text.lower()
        categories = []

        category_keywords = {
            "product_launch": ["launch", "new product", "introducing", "announcing"],
            "brand_activation": ["activation", "experiential", "pop-up", "popup"],
            "sampling_giveaway": ["sample", "giveaway", "sweepstakes", "free", "contest"],
            "influencer_collab": ["influencer", "creator", "collab", "partnership"],
            "retail_partnership": ["retail", "target", "walmart", "kroger", "store"],
            "industry_trend": ["trend", "future", "prediction", "what's next"],
            "thought_leadership": ["insight", "strategy", "lesson", "learned"],
            "case_study": ["case study", "results", "roi", "success story"],
        }

        for category, keywords in category_keywords.items():
            if any(kw in text_lower for kw in keywords):
                categories.append(category)

        return categories or ["general"]

    def _find_matched_keywords(self, text: str) -> List[str]:
        """Find which of our target keywords matched in the text."""
        if not text:
            return []

        text_lower = text.lower()
        matched = []

        all_keywords = (
            self.config["keywords"].get("primary", []) +
            self.config["keywords"].get("secondary", [])
        )

        for kw in all_keywords:
            if kw.lower() in text_lower:
                matched.append(kw)

        return matched

    def _is_excluded(self, text: str) -> bool:
        """Check if content should be excluded based on negative keywords."""
        if not text:
            return False

        text_lower = text.lower()
        exclude = self.config.get("exclude_keywords", [])

        return any(kw.lower() in text_lower for kw in exclude)

    # ========================================================================
    # AGGREGATION
    # ========================================================================

    def discover_all(self,
                     platforms: Optional[List[str]] = None,
                     use_cache: bool = True) -> Dict[str, List[ViralContent]]:
        """
        Run discovery across all platforms.

        Args:
            platforms: List of platforms to search (default: all)
            use_cache: Use cached results if available

        Returns:
            Dict mapping platform -> list of ViralContent
        """
        platforms = platforms or ["linkedin", "twitter", "reddit", "tiktok", "instagram"]

        print(f"\n{'='*60}")
        print(f"VIRAL CONTENT DISCOVERY - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}")

        results = {}

        if "linkedin" in platforms:
            results["linkedin"] = self.discover_linkedin_viral(use_cache=use_cache)

        if "twitter" in platforms:
            results["twitter"] = self.discover_twitter_trending(use_cache=use_cache)

        if "reddit" in platforms:
            results["reddit"] = self.discover_reddit_discussions(use_cache=use_cache)

        if "tiktok" in platforms:
            results["tiktok"] = self.discover_tiktok_trends(use_cache=use_cache)

        if "instagram" in platforms:
            results["instagram"] = self.discover_instagram_activations(use_cache=use_cache)

        self.results = results

        # Summary
        print(f"\n{'='*60}")
        print("DISCOVERY COMPLETE")
        for platform, content in results.items():
            print(f"  {platform}: {len(content)} items")
        print(f"{'='*60}")

        return results

    def get_top_content(self, limit: int = 10) -> List[ViralContent]:
        """
        Get top content across all platforms by relevance.

        Args:
            limit: Maximum items to return

        Returns:
            List of ViralContent sorted by relevance_score
        """
        all_content = []
        for platform_content in self.results.values():
            all_content.extend(platform_content)

        # Sort by relevance score, then engagement
        all_content.sort(
            key=lambda x: (x.relevance_score, sum(x.engagement.values())),
            reverse=True
        )

        return all_content[:limit]

    def export_results(self, filepath: str, format: str = "json"):
        """
        Export results to file.

        Args:
            filepath: Output file path
            format: Output format (json or csv)
        """
        if format == "json":
            output = {}
            for platform, content in self.results.items():
                output[platform] = [asdict(c) for c in content]

            with open(filepath, "w") as f:
                json.dump(output, f, indent=2, default=str)

        elif format == "csv":
            import csv

            rows = []
            for platform, content in self.results.items():
                for c in content:
                    rows.append({
                        "platform": c.platform,
                        "type": c.content_type,
                        "title": c.title,
                        "text": c.text[:200],
                        "url": c.url,
                        "author": c.author,
                        "relevance_score": c.relevance_score,
                        "categories": ", ".join(c.categories),
                        **c.engagement
                    })

            if rows:
                with open(filepath, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)

        print(f"Exported to {filepath}")


# ============================================================================
# CLI
# ============================================================================

def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Viral Content Discovery")
    parser.add_argument("command", choices=["discover", "linkedin", "twitter", "reddit", "tiktok", "instagram", "trends"],
                        help="Discovery command")
    parser.add_argument("--all", action="store_true", help="Run all platforms")
    parser.add_argument("--platform", type=str, help="Specific platform to search")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache")
    parser.add_argument("--export", type=str, help="Export results to file")

    args = parser.parse_args()

    discovery = ViralContentDiscovery()

    if args.command == "discover" or args.all:
        results = discovery.discover_all(use_cache=not args.no_cache)
    elif args.command == "linkedin":
        discovery.discover_linkedin_viral(use_cache=not args.no_cache)
    elif args.command == "twitter":
        discovery.discover_twitter_trending(use_cache=not args.no_cache)
    elif args.command == "reddit":
        discovery.discover_reddit_discussions(use_cache=not args.no_cache)
    elif args.command == "tiktok":
        discovery.discover_tiktok_trends(use_cache=not args.no_cache)
    elif args.command == "instagram":
        discovery.discover_instagram_activations(use_cache=not args.no_cache)
    elif args.command == "trends":
        trends = discovery.get_trending_topics(use_cache=not args.no_cache)
        for t in trends:
            print(f"  {t['keyword']}: interest={t['interest']}")

    if args.export:
        fmt = "csv" if args.export.endswith(".csv") else "json"
        discovery.export_results(args.export, format=fmt)


if __name__ == "__main__":
    main()
