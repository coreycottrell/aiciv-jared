"""
Tests for Issue 3: Company Table Account Multiplier

When updating Company table fields, the Account Multiplier value should change
when other fields update.
"""
import pytest
from unittest.mock import patch, MagicMock
from tools.intent_engine.employee_scraper import get_or_create_company


class TestCompanyAccountMultiplier:
    """Test that Account Multiplier is properly set/updated on company records."""

    def test_create_company_sets_account_multiplier(self):
        """When creating a new company, Account Multiplier should be set."""
        with patch('tools.intent_engine.employee_scraper.requests.get') as mock_get, \
             patch('tools.intent_engine.employee_scraper.requests.post') as mock_post:

            # No existing company found
            mock_get.return_value.json.return_value = {"records": []}

            # Mock successful creation
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"id": "rec123"}

            get_or_create_company("Test Corp", "https://linkedin.com/company/test-corp")

            # Check that Account Multiplier was included in creation
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert "Account Multiplier" in payload["fields"]

    def test_create_company_calculates_default_multiplier(self):
        """New companies should get a default Account Multiplier value."""
        with patch('tools.intent_engine.employee_scraper.requests.get') as mock_get, \
             patch('tools.intent_engine.employee_scraper.requests.post') as mock_post:

            mock_get.return_value.json.return_value = {"records": []}
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"id": "rec123"}

            get_or_create_company("Test Corp", "https://linkedin.com/company/test-corp")

            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            # Default multiplier should be a reasonable value (e.g., 1.0 or based on company size)
            assert payload["fields"]["Account Multiplier"] >= 1.0


class TestUpdateCompanyMultiplier:
    """Test updating company records with Account Multiplier."""

    def test_update_company_includes_multiplier(self):
        """update_company should be able to set Account Multiplier."""
        # This function may need to be created or modified
        from tools.intent_engine import airtable_client

        with patch('tools.intent_engine.airtable_client.requests.patch') as mock_patch:
            mock_patch.return_value.raise_for_status = MagicMock()
            mock_patch.return_value.json.return_value = {"id": "rec123"}

            airtable_client.update_company(
                company_record_id="rec123",
                fields={
                    "Company Name": "Test Corp Updated",
                    "Account Multiplier": 1.5,
                }
            )

            call_args = mock_patch.call_args
            payload = call_args[1]["json"]
            assert payload["fields"]["Account Multiplier"] == 1.5


class TestCompanyMultiplierCalculation:
    """Test Account Multiplier calculation logic."""

    def test_calculate_multiplier_based_on_employee_count(self):
        """Account Multiplier should be calculated based on factors like employee count."""
        from tools.intent_engine.employee_scraper import calculate_account_multiplier

        # Larger companies = higher multiplier (more potential value)
        assert calculate_account_multiplier(employee_count=10000) > \
               calculate_account_multiplier(employee_count=100)

    def test_calculate_multiplier_based_on_industry(self):
        """CPG companies should have higher multipliers (target industry)."""
        from tools.intent_engine.employee_scraper import calculate_account_multiplier

        cpg_multiplier = calculate_account_multiplier(industry="Consumer Goods")
        other_multiplier = calculate_account_multiplier(industry="Technology")

        # CPG is our target, should have higher multiplier
        assert cpg_multiplier >= other_multiplier

    def test_calculate_multiplier_defaults(self):
        """Multiplier should have sensible defaults when data is missing."""
        from tools.intent_engine.employee_scraper import calculate_account_multiplier

        # With no data, should return default multiplier
        multiplier = calculate_account_multiplier()
        assert multiplier == 1.0  # Default value
