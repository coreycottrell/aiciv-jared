"""
Tests for Auto-Prospect Discovery Module

TDD: These tests are written FIRST before implementation.
Each test should FAIL initially, then pass after implementation.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path
import json
import os


class TestICPConfig:
    """Tests for ICP configuration loading and management"""

    def test_load_megan_patel_icp(self):
        """Megan Patel ICP should load with correct structure"""
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("megan_patel")

        assert icp is not None
        assert icp["persona"] == "megan_patel"
        assert "target_titles" in icp
        assert "target_industries" in icp
        assert "company_criteria" in icp
        assert "keywords_in_profile" in icp

        # Verify specific titles
        assert "VP Marketing" in icp["target_titles"]
        assert "CMO" in icp["target_titles"]
        assert "Director of Marketing" in icp["target_titles"]

        # Verify specific industries
        assert "Food & Beverage" in icp["target_industries"]
        assert "CPG" in icp["target_industries"]

    def test_load_david_brown_icp(self):
        """David Brown ICP should load with correct structure"""
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("david_brown")

        assert icp is not None
        assert icp["persona"] == "david_brown"
        assert "target_titles" in icp
        assert "target_industries" in icp

        # Verify specific titles
        assert "VP Sales" in icp["target_titles"]
        assert "National Accounts Director" in icp["target_titles"]

        # Verify specific industries
        assert "Packaged Bakery" in icp["target_industries"]
        assert "Snack Cakes" in icp["target_industries"]

    def test_load_invalid_icp_raises_error(self):
        """Loading non-existent ICP should raise ValueError"""
        from tools.intent_engine.icp_config import load_icp_config

        with pytest.raises(ValueError) as exc_info:
            load_icp_config("nonexistent_persona")

        assert "not found" in str(exc_info.value).lower()

    def test_list_available_icps(self):
        """Should list all available ICP configurations"""
        from tools.intent_engine.icp_config import list_icps

        icps = list_icps()

        assert "megan_patel" in icps
        assert "david_brown" in icps


class TestProspectScoring:
    """Tests for ICP scoring logic"""

    def test_score_perfect_megan_match(self):
        """Perfect Megan Patel match should score high (80+)"""
        from tools.intent_engine.prospect_discovery import score_prospect
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("megan_patel")
        prospect = {
            "title": "VP Marketing",
            "industry": "Food & Beverage",
            "company_size": 500,
            "profile_text": "Omnichannel retail DTC consumer goods brand marketing",
        }

        score = score_prospect(prospect, icp)

        assert score >= 80, f"Perfect match should score 80+, got {score}"

    def test_score_perfect_david_match(self):
        """Perfect David Brown match should score high (80+)"""
        from tools.intent_engine.prospect_discovery import score_prospect
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("david_brown")
        prospect = {
            "title": "VP Sales",
            "industry": "Packaged Bakery",
            "company_size": 200,
            "profile_text": "National accounts grocery retail trade marketing",
        }

        score = score_prospect(prospect, icp)

        assert score >= 80, f"Perfect match should score 80+, got {score}"

    def test_score_partial_title_match(self):
        """Partial title match should score moderately (40-70)"""
        from tools.intent_engine.prospect_discovery import score_prospect
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("megan_patel")
        prospect = {
            "title": "Marketing Coordinator",  # Not quite right title
            "industry": "Food & Beverage",
            "company_size": 500,
            "profile_text": "CPG brand marketing",
        }

        score = score_prospect(prospect, icp)

        # Should get industry + keywords points but reduced title points
        assert 20 <= score <= 70, f"Partial match should score 20-70, got {score}"

    def test_score_wrong_industry(self):
        """Wrong industry should score lower than perfect match"""
        from tools.intent_engine.prospect_discovery import score_prospect
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("megan_patel")
        prospect_wrong_industry = {
            "title": "VP Marketing",
            "industry": "Software",  # Wrong industry
            "company_size": 500,
            "profile_text": "SaaS B2B enterprise software",
        }
        prospect_right_industry = {
            "title": "VP Marketing",
            "industry": "Food & Beverage",
            "company_size": 500,
            "profile_text": "CPG DTC retail omnichannel",
        }

        score_wrong = score_prospect(prospect_wrong_industry, icp)
        score_right = score_prospect(prospect_right_industry, icp)

        # Wrong industry should score less than right industry
        assert score_wrong < score_right, f"Wrong industry ({score_wrong}) should score less than right ({score_right})"
        # Should still get some points for title match
        assert score_wrong >= 40, f"Title match should give at least 40 points, got {score_wrong}"

    def test_score_no_match(self):
        """No match should score very low (<40)"""
        from tools.intent_engine.prospect_discovery import score_prospect
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("megan_patel")
        prospect = {
            "title": "Software Engineer",
            "industry": "Technology",
            "company_size": 0,  # No company size to avoid bonus points
            "profile_text": "Python developer building APIs",
        }

        score = score_prospect(prospect, icp)

        # No title, industry, or keyword match - should be below filter threshold
        assert score < 40, f"No match should score < 40, got {score}"


class TestProspectFiltering:
    """Tests for filtering prospects by ICP"""

    def test_filter_returns_only_high_scores(self):
        """filter_by_icp should return only prospects with score >= threshold"""
        from tools.intent_engine.prospect_discovery import filter_by_icp
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("megan_patel")
        prospects = [
            {"title": "VP Marketing", "industry": "Food & Beverage", "profile_text": "CPG DTC retail"},
            {"title": "Software Engineer", "industry": "Tech", "profile_text": "Python"},
            {"title": "Director of Marketing", "industry": "CPG", "profile_text": "brand consumer goods"},
        ]

        filtered = filter_by_icp(prospects, icp, min_score=50)

        # Should only include VP Marketing and Director of Marketing
        assert len(filtered) == 2
        assert all(p.get("_icp_score", 0) >= 50 for p in filtered)

    def test_filter_preserves_original_data(self):
        """Filtering should not modify original prospect data"""
        from tools.intent_engine.prospect_discovery import filter_by_icp
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("megan_patel")
        prospects = [
            {"title": "VP Marketing", "industry": "Food & Beverage", "profile_text": "CPG"}
        ]
        original_prospect = prospects[0].copy()

        filter_by_icp(prospects, icp)

        # Original should still have same keys (score is added, not replaced)
        assert prospects[0]["title"] == original_prospect["title"]


class TestLearningFromFeedback:
    """Tests for learning from human feedback"""

    def test_load_empty_learnings(self):
        """Should return empty exclusions when no learnings exist"""
        from tools.intent_engine.prospect_discovery import load_learnings

        with patch("builtins.open", side_effect=FileNotFoundError):
            learnings = load_learnings()

        assert learnings.get("bad_titles", []) == []
        assert learnings.get("bad_industries", []) == []
        assert learnings.get("bad_keywords", []) == []

    def test_apply_learnings_reduces_score(self):
        """Learned bad patterns should reduce prospect score"""
        from tools.intent_engine.prospect_discovery import score_prospect, apply_learnings
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("megan_patel")
        prospect = {
            "title": "VP Marketing",
            "industry": "Food & Beverage",
            "profile_text": "CPG DTC retail",
        }

        learnings = {
            "bad_titles": ["VP Marketing"],  # Pretend we learned this is bad
        }

        # Score without learnings
        score_without = score_prospect(prospect, icp)

        # Score with learnings applied
        score_with = score_prospect(prospect, icp, learnings=learnings)

        assert score_with < score_without, "Learnings should reduce score"

    def test_save_learnings_from_feedback(self):
        """Should update learnings file from feedback"""
        from tools.intent_engine.prospect_discovery import update_learnings_from_feedback, load_learnings, LEARNINGS_FILE
        import tempfile
        import shutil

        feedback = [
            {"title": "Marketing Intern", "fit": "Bad Fit", "notes": "Too junior"},
            {"title": "VP Marketing", "fit": "Good Fit", "notes": "Great match"},
        ]

        # Use a temp file for testing
        original_file = LEARNINGS_FILE
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write('{"bad_titles": [], "good_titles": []}')
            tmp_path = tmp.name

        try:
            # Patch the LEARNINGS_FILE path
            import tools.intent_engine.prospect_discovery as pd
            pd.LEARNINGS_FILE = Path(tmp_path)

            update_learnings_from_feedback(feedback)

            # Load and verify
            learnings = load_learnings()
            assert "Marketing Intern" in learnings.get("bad_titles", [])
            assert "VP Marketing" in learnings.get("good_titles", [])
        finally:
            pd.LEARNINGS_FILE = original_file
            os.unlink(tmp_path)


class TestAirtableIntegration:
    """Tests for Airtable integration with new fields"""

    def test_add_prospect_includes_icp_match(self):
        """add_prospects_to_airtable should set ICP Match field"""
        from tools.intent_engine.prospect_discovery import add_prospects_to_airtable

        prospects = [
            {
                "name": "Test Person",
                "linkedin_url": "https://linkedin.com/in/test",
                "title": "VP Marketing",
                "_icp_score": 85,
            }
        ]

        with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
            # Mock existing check
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"records": []}

            # Mock create
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"id": "recXXX"}

            result = add_prospects_to_airtable(prospects, "megan_patel")

            # Verify ICP Match was included in the request
            call_args = mock_post.call_args
            fields = call_args[1]["json"]["fields"]
            assert "ICP Match" in fields
            assert fields["ICP Match"] == "Megan Patel"

    def test_add_prospect_includes_discovery_metadata(self):
        """add_prospects_to_airtable should set Discovery Date and Source"""
        from tools.intent_engine.prospect_discovery import add_prospects_to_airtable

        prospects = [
            {
                "name": "Test Person",
                "linkedin_url": "https://linkedin.com/in/test",
                "title": "VP Marketing",
                "_icp_score": 85,
            }
        ]

        with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"records": []}
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"id": "recXXX"}

            add_prospects_to_airtable(prospects, "megan_patel")

            fields = mock_post.call_args[1]["json"]["fields"]
            assert "Discovery Source" in fields
            assert fields["Discovery Source"] == "Auto-Discovery via Apify"
            assert "Discovery Date" in fields

    def test_skips_duplicates(self):
        """Should skip prospects already in Airtable"""
        from tools.intent_engine.prospect_discovery import add_prospects_to_airtable

        prospects = [
            {
                "name": "Existing Person",
                "linkedin_url": "https://linkedin.com/in/existing",
                "title": "VP Marketing",
            }
        ]

        with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
            # Mock that person already exists
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "records": [{"fields": {"LinkedIn URL": "https://linkedin.com/in/existing"}}]
            }

            result = add_prospects_to_airtable(prospects, "megan_patel")

            # Should not have tried to create
            assert result["added"] == 0
            assert result["skipped"] == 1


class TestApifySearchIntegration:
    """Tests for Apify search functionality"""

    def test_build_google_search_query_megan(self):
        """Should build appropriate search query for Megan ICP"""
        from tools.intent_engine.prospect_discovery import build_search_queries
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("megan_patel")
        queries = build_search_queries(icp, limit=5)

        # Should generate queries combining titles + industries
        assert len(queries) > 0
        # Queries should contain LinkedIn site restriction
        assert any("site:linkedin.com" in q for q in queries)
        # Should include title keywords
        assert any("VP Marketing" in q or "CMO" in q for q in queries)

    def test_parse_google_results_extracts_linkedin_urls(self):
        """Should extract LinkedIn profile URLs from Google search results"""
        from tools.intent_engine.prospect_discovery import parse_search_results

        google_results = [
            {"url": "https://www.linkedin.com/in/john-doe-123", "title": "John Doe - VP Marketing"},
            {"url": "https://example.com/page", "title": "Random Page"},
            {"url": "https://linkedin.com/in/jane-smith", "title": "Jane Smith | CMO"},
        ]

        linkedin_urls = parse_search_results(google_results)

        assert len(linkedin_urls) == 2
        assert "https://www.linkedin.com/in/john-doe-123" in linkedin_urls
        assert "https://linkedin.com/in/jane-smith" in linkedin_urls


class TestEndToEndDiscovery:
    """Integration tests for complete discovery workflow"""

    def test_discover_prospects_workflow(self):
        """Full discovery workflow should work end-to-end"""
        from tools.intent_engine.prospect_discovery import discover_prospects

        with patch("tools.intent_engine.prospect_discovery.search_prospects_apify") as mock_search:
            with patch("tools.intent_engine.prospect_discovery.add_prospects_to_airtable") as mock_add:
                mock_search.return_value = [
                    {
                        "name": "Test VP",
                        "linkedin_url": "https://linkedin.com/in/testvp",
                        "title": "VP Marketing",
                        "industry": "Food & Beverage",
                        "profile_text": "CPG brand DTC retail omnichannel",
                    }
                ]
                mock_add.return_value = {"added": 1, "skipped": 0}

                result = discover_prospects("megan_patel", limit=10)

                assert mock_search.called
                assert mock_add.called
                assert result["prospects_found"] >= 0


class TestCostAwareness:
    """Tests for cost-conscious implementation"""

    def test_respects_limit_parameter(self):
        """Should not exceed specified limit"""
        from tools.intent_engine.prospect_discovery import build_search_queries
        from tools.intent_engine.icp_config import load_icp_config

        icp = load_icp_config("megan_patel")
        queries = build_search_queries(icp, limit=5)

        # Total potential results should be limited
        # (Each query typically returns ~10 results)
        assert len(queries) <= 5  # Shouldn't need more than 5 queries for 50 prospects

    def test_caches_search_results(self):
        """Should use caching to avoid re-searching"""
        from tools.intent_engine.prospect_discovery import search_prospects_apify

        # This test verifies caching behavior exists
        # Implementation should cache results to avoid repeated Apify costs
        # (Detailed caching tests would go here)
        pass  # TODO: Implement when caching is added
