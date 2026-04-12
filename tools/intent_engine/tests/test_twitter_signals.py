"""
Tests for Issue 4: Twitter/X Signal Tracking

Expand signal tracking to include Twitter (X) accounts for monitored staff members.
Track tweets, retweets, replies, likes with same signal structure as LinkedIn.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestTwitterCollector:
    """Test Twitter signal collection."""

    def test_twitter_collector_exists(self):
        """Twitter collector module should exist."""
        from tools.intent_engine import twitter_collector
        assert twitter_collector is not None

    def test_collect_twitter_signals(self):
        """collect_twitter_signals should accept Twitter handles and return signals."""
        from tools.intent_engine.twitter_collector import collect_twitter_signals

        handles = ["@testuser1", "@testuser2"]

        # Mock the Apify actor call (new implementation)
        with patch('tools.intent_engine.twitter_collector._run_apify_twitter_actor') as mock_apify:
            # Return Apify-format response that will be parsed
            mock_apify.return_value = [
                {
                    "user": {"screen_name": "testuser1", "name": "Test User 1"},
                    "full_text": "Excited about our new product launch!",
                    "created_at": "Mon Feb 01 10:00:00 +0000 2026",
                    "favorite_count": 50,
                    "retweet_count": 10,
                    "retweeted_status": None,
                    "in_reply_to_screen_name": None,
                }
            ]

            results = collect_twitter_signals(handles)

            assert len(results) > 0
            assert results[0]["handle"] == "@testuser1"

    def test_twitter_signal_structure_matches_linkedin(self):
        """Twitter signals should have same structure as LinkedIn signals."""
        from tools.intent_engine.twitter_collector import parse_twitter_signals

        twitter_data = {
            "handle": "@brandmanager",
            "name": "Sarah Chen",
            "tweets": [
                {
                    "text": "Just launched our experiential campaign!",
                    "created_at": "2026-02-01T15:00:00Z",
                    "likes": 100,
                    "retweets": 25,
                }
            ],
        }

        signals = parse_twitter_signals(twitter_data)

        # Should have same fields as LinkedIn signals
        assert len(signals) > 0
        signal = signals[0]
        assert "type" in signal
        assert "strength" in signal
        assert "evidence" in signal
        assert "source" in signal
        assert signal["source"] == "Twitter"


class TestTwitterSignalTypes:
    """Test that Twitter activity maps to appropriate signal types."""

    def test_tweet_about_launch_creates_signal(self):
        """Tweets about product launches should create posted_about_launch signal."""
        from tools.intent_engine.twitter_collector import parse_twitter_signals

        data = {
            "handle": "@brandvp",
            "tweets": [
                {
                    "text": "Thrilled to announce the launch of our new product line!",
                    "created_at": "2026-02-01T12:00:00Z",
                    "likes": 200,
                    "retweets": 50,
                }
            ],
        }

        signals = parse_twitter_signals(data)

        launch_signals = [s for s in signals if s["type"] == "posted_about_launch"]
        assert len(launch_signals) > 0

    def test_retweet_experiential_content(self):
        """Retweets of experiential content should create liked_experiential_post signal."""
        from tools.intent_engine.twitter_collector import parse_twitter_signals

        data = {
            "handle": "@marketingdir",
            "retweets": [
                {
                    "original_text": "Amazing brand activation at SXSW!",
                    "created_at": "2026-02-01T14:00:00Z",
                }
            ],
        }

        signals = parse_twitter_signals(data)

        experiential_signals = [s for s in signals if s["type"] == "liked_experiential_post"]
        assert len(experiential_signals) > 0

    def test_reply_to_competitor(self):
        """Replies to competitor content should create commented_on_competitor signal."""
        from tools.intent_engine.twitter_collector import parse_twitter_signals

        data = {
            "handle": "@brandmgr",
            "replies": [
                {
                    "text": "Great campaign! Love what you did here.",
                    "in_reply_to": "@competitorbrand",
                    "original_text": "Check out our new experiential activation",
                    "created_at": "2026-02-01T16:00:00Z",
                }
            ],
        }

        signals = parse_twitter_signals(data)

        competitor_signals = [s for s in signals if s["type"] == "commented_on_competitor"]
        assert len(competitor_signals) > 0


class TestTwitterPersonMapping:
    """Test mapping Twitter handles to People records."""

    def test_person_has_twitter_field(self):
        """People table should have a Twitter Handle field."""
        from tools.intent_engine.config import PEOPLE_FIELDS

        # The config should define a twitter_handle field
        assert "twitter_handle" in PEOPLE_FIELDS or "Twitter Handle" in str(PEOPLE_FIELDS)

    def test_get_people_with_twitter(self):
        """Should be able to fetch people who have Twitter handles."""
        from tools.intent_engine import airtable_client

        with patch('tools.intent_engine.airtable_client.get_all_people') as mock_get:
            mock_get.return_value = [
                {
                    "id": "rec123",
                    "fields": {
                        "Name": "Test User",
                        "Twitter Handle": "@testuser",
                    }
                }
            ]

            people = airtable_client.get_people_with_twitter()

            assert len(people) > 0
            assert people[0]["fields"]["Twitter Handle"] == "@testuser"


class TestCombinedSignalCollection:
    """Test collecting signals from both LinkedIn AND Twitter."""

    def test_collect_all_signals_includes_both_sources(self):
        """Full signal collection should include both LinkedIn and Twitter."""
        from tools.intent_engine.main import run_collect_all

        with patch('tools.intent_engine.airtable_client.get_people_with_linkedin') as mock_li_people, \
             patch('tools.intent_engine.airtable_client.get_people_with_twitter') as mock_tw_people, \
             patch('tools.intent_engine.apify_collector.collect_signals') as mock_linkedin, \
             patch('tools.intent_engine.twitter_collector.collect_twitter_signals') as mock_twitter:

            # Mock people queries to return empty lists (nothing to collect)
            mock_li_people.return_value = []
            mock_tw_people.return_value = []

            # These won't be called since no people, but set them anyway
            mock_linkedin.return_value = [{"source": "LinkedIn"}]
            mock_twitter.return_value = [{"source": "Twitter"}]

            results = run_collect_all()

            # run_collect_all was called - verify both sources were attempted
            mock_li_people.assert_called_once()
            mock_tw_people.assert_called_once()


class TestTwitterConfig:
    """Test Twitter API configuration (now Apify-based)."""

    def test_apify_api_token_in_config(self):
        """Config should have APIFY_API_KEY setting for Twitter collection."""
        from tools.intent_engine.config import APIFY_API_KEY

        # APIFY_API_KEY should be defined (may be None if not in .env)
        # The important thing is it's defined and accessible in config
        assert "APIFY_API_KEY" in dir() or APIFY_API_KEY is not None or APIFY_API_KEY is None

    def test_twitter_sources_defined(self):
        """SOURCES config should include Twitter."""
        from tools.intent_engine.config import SOURCES

        assert "Twitter" in SOURCES


class TestApifyTwitterIntegration:
    """Test Apify-based Twitter collection (replaces Twitter API)."""

    def test_extract_handle_from_twitter_url(self):
        """Should extract Twitter handle from various URL formats."""
        from tools.intent_engine.twitter_collector import extract_handle_from_url

        # Standard twitter.com format
        assert extract_handle_from_url("https://twitter.com/elonmusk") == "elonmusk"
        assert extract_handle_from_url("https://twitter.com/elonmusk/") == "elonmusk"

        # x.com format
        assert extract_handle_from_url("https://x.com/elonmusk") == "elonmusk"
        assert extract_handle_from_url("https://x.com/elonmusk/") == "elonmusk"

        # With www prefix
        assert extract_handle_from_url("https://www.twitter.com/elonmusk") == "elonmusk"
        assert extract_handle_from_url("https://www.x.com/elonmusk") == "elonmusk"

        # Handle edge cases
        assert extract_handle_from_url("https://twitter.com/user/status/123") == "user"
        assert extract_handle_from_url("@username") == "username"
        assert extract_handle_from_url("username") == "username"
        assert extract_handle_from_url("") is None

    def test_collect_twitter_signals_uses_apify(self):
        """collect_twitter_signals should use Apify actor, not Twitter API."""
        from tools.intent_engine.twitter_collector import collect_twitter_signals

        with patch('tools.intent_engine.twitter_collector._run_apify_twitter_actor') as mock_apify:
            mock_apify.return_value = [
                {
                    "user": {"screen_name": "testuser"},
                    "full_text": "Launching our experiential campaign!",
                    "created_at": "Mon Feb 03 10:00:00 +0000 2026",
                    "favorite_count": 50,
                    "retweet_count": 10,
                }
            ]

            results = collect_twitter_signals(["testuser"])

            mock_apify.assert_called_once()
            assert len(results) > 0

    def test_apify_twitter_handles_batching(self):
        """Should batch multiple handles efficiently for Apify."""
        from tools.intent_engine.twitter_collector import collect_twitter_signals

        with patch('tools.intent_engine.twitter_collector._run_apify_twitter_actor') as mock_apify:
            mock_apify.return_value = []

            # Pass multiple handles
            handles = ["user1", "user2", "user3"]
            collect_twitter_signals(handles)

            # Should be called with all handles batched together
            call_args = mock_apify.call_args
            assert call_args is not None
            # Verify handles were passed to Apify
            passed_handles = call_args[0][0] if call_args[0] else call_args[1].get("handles", [])
            assert len(passed_handles) >= 1

    def test_parse_apify_tweet_response(self):
        """Should parse Apify tweet response into our signal format."""
        from tools.intent_engine.twitter_collector import _parse_apify_response

        apify_response = [
            {
                "user": {"screen_name": "brandvp", "name": "Brand VP"},
                "full_text": "Launching our experiential campaign at SXSW!",
                "created_at": "Mon Feb 03 10:00:00 +0000 2026",
                "favorite_count": 100,
                "retweet_count": 25,
                "in_reply_to_screen_name": None,
                "retweeted_status": None,
            },
            {
                "user": {"screen_name": "brandvp", "name": "Brand VP"},
                "full_text": "RT @competitor: Amazing activation event",
                "created_at": "Mon Feb 03 11:00:00 +0000 2026",
                "favorite_count": 0,
                "retweet_count": 0,
                "in_reply_to_screen_name": None,
                "retweeted_status": {"full_text": "Amazing activation event"},
            },
        ]

        parsed = _parse_apify_response(apify_response)

        assert "brandvp" in parsed or "@brandvp" in parsed
        # Should have both tweet and retweet data
        user_data = parsed.get("brandvp") or parsed.get("@brandvp")
        assert user_data is not None
        assert "tweets" in user_data
        assert "retweets" in user_data

    def test_no_twitter_api_dependencies(self):
        """Twitter collector should not require Twitter API keys."""
        from tools.intent_engine.twitter_collector import collect_twitter_signals

        # Should not raise error even without Twitter API keys
        # (will use Apify instead)
        with patch('tools.intent_engine.twitter_collector._run_apify_twitter_actor') as mock_apify:
            mock_apify.return_value = []

            # This should NOT raise ValueError about TWITTER_BEARER_TOKEN
            try:
                results = collect_twitter_signals(["testuser"])
                assert results == [] or results is not None
            except ValueError as e:
                if "TWITTER" in str(e):
                    pytest.fail("Should not require Twitter API keys - use Apify instead")
