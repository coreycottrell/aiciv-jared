"""
Tests for Cleanup CLI Integration

Tests that the cleanup command is properly integrated into main.py CLI.
"""
import pytest
from unittest.mock import patch, MagicMock
from tools.intent_engine import main


class TestCleanupCLI:
    """Tests for the cleanup command-line interface."""

    def test_run_cleanup_inactive_function_exists(self):
        """The run_cleanup_inactive function should exist in main module."""
        assert hasattr(main, 'run_cleanup_inactive')

    def test_run_cleanup_inactive_calls_airtable(self):
        """run_cleanup_inactive should call the airtable cleanup function."""
        from tools.intent_engine import airtable_client

        with patch.object(airtable_client, 'cleanup_inactive') as mock_cleanup:
            mock_cleanup.return_value = {
                "would_remove": 5,
                "removed": 0,
                "inactive_days": 90,
                "grace_period_days": 30,
                "people": [],
            }

            result = main.run_cleanup_inactive(days=90, dry_run=True)

            mock_cleanup.assert_called_once_with(
                days=90,
                grace_period_days=30,
                dry_run=True
            )

    def test_run_cleanup_inactive_dry_run_default(self):
        """Dry run should be True by default for safety."""
        from tools.intent_engine import airtable_client

        with patch.object(airtable_client, 'cleanup_inactive') as mock_cleanup:
            mock_cleanup.return_value = {
                "would_remove": 0,
                "removed": 0,
                "inactive_days": 90,
                "grace_period_days": 30,
                "people": [],
            }

            # Default call without dry_run specified
            result = main.run_cleanup_inactive()

            # Should default to dry_run=True
            call_args = mock_cleanup.call_args
            assert call_args[1]["dry_run"] is True

    def test_run_cleanup_inactive_returns_result(self):
        """run_cleanup_inactive should return the cleanup result."""
        from tools.intent_engine import airtable_client

        expected_result = {
            "would_remove": 3,
            "removed": 3,
            "inactive_days": 90,
            "grace_period_days": 30,
            "people": [
                {"id": "rec1", "name": "Person 1"},
                {"id": "rec2", "name": "Person 2"},
                {"id": "rec3", "name": "Person 3"},
            ],
        }

        with patch.object(airtable_client, 'cleanup_inactive', return_value=expected_result):
            result = main.run_cleanup_inactive(days=90, dry_run=False)

            assert result["would_remove"] == 3
            assert result["removed"] == 3
            assert len(result["people"]) == 3
