"""
Tests for Inactive Contact Cleanup

This module tests the cleanup functionality that removes people who have not
been active in the last 90 days to reduce API costs and keep the prospect list fresh.

Business Rules:
1. "Active" = has at least 1 signal in the past 90 days
2. "Inactive" = zero signals in 90+ days
3. If someone was added recently (< 30 days ago) but has no signals yet, don't remove them
4. Dry run should report who would be removed without actually removing
5. Archiving is preferred over hard delete
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, call
from tools.intent_engine import airtable_client


class TestGetInactiveContacts:
    """Tests for identifying inactive contacts."""

    def test_person_with_recent_signal_is_active(self):
        """A person with a signal in the last 90 days should be considered active."""
        # Person created 100 days ago with signal 30 days ago = ACTIVE
        person = {
            "id": "rec123",
            "fields": {
                "Name": "Active Person",
                "LinkedIn URL": "https://linkedin.com/in/active",
            },
            "createdTime": (datetime.now(timezone.utc) - timedelta(days=100)).isoformat(),
        }

        signals = [
            {
                "id": "sig1",
                "fields": {
                    "Signal Timestamp": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                },
            }
        ]

        result = airtable_client.is_contact_inactive(person, signals, inactive_days=90)
        assert result is False, "Person with recent signal should not be inactive"

    def test_person_with_old_signal_is_inactive(self):
        """A person with no signals in 90+ days should be considered inactive."""
        # Person created 200 days ago with last signal 100 days ago = INACTIVE
        person = {
            "id": "rec456",
            "fields": {
                "Name": "Inactive Person",
                "LinkedIn URL": "https://linkedin.com/in/inactive",
            },
            "createdTime": (datetime.now(timezone.utc) - timedelta(days=200)).isoformat(),
        }

        signals = [
            {
                "id": "sig1",
                "fields": {
                    "Signal Timestamp": (datetime.now(timezone.utc) - timedelta(days=100)).isoformat(),
                },
            }
        ]

        result = airtable_client.is_contact_inactive(person, signals, inactive_days=90)
        assert result is True, "Person with only old signals should be inactive"

    def test_person_with_no_signals_but_recently_added_is_protected(self):
        """A person added in last 30 days with no signals should NOT be removed."""
        # Person created 15 days ago with no signals = PROTECTED (not inactive)
        person = {
            "id": "rec789",
            "fields": {
                "Name": "New Person",
                "LinkedIn URL": "https://linkedin.com/in/newperson",
            },
            "createdTime": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
        }

        signals = []  # No signals

        result = airtable_client.is_contact_inactive(
            person, signals, inactive_days=90, grace_period_days=30
        )
        assert result is False, "Recently added person should be protected"

    def test_person_with_no_signals_and_old_is_inactive(self):
        """A person added 90+ days ago with no signals should be inactive."""
        # Person created 120 days ago with no signals = INACTIVE
        person = {
            "id": "rec101",
            "fields": {
                "Name": "Old No-Signal Person",
                "LinkedIn URL": "https://linkedin.com/in/oldnosignal",
            },
            "createdTime": (datetime.now(timezone.utc) - timedelta(days=120)).isoformat(),
        }

        signals = []  # No signals

        result = airtable_client.is_contact_inactive(
            person, signals, inactive_days=90, grace_period_days=30
        )
        assert result is True, "Old person with no signals should be inactive"


class TestGetSignalsForPerson:
    """Tests for fetching signals linked to a person."""

    def test_get_signals_for_person(self):
        """Should fetch all signals linked to a person record."""
        person_record_id = "rec123"

        with patch('tools.intent_engine.airtable_client.requests.get') as mock_get:
            mock_get.return_value.raise_for_status = MagicMock()
            mock_get.return_value.json.return_value = {
                "records": [
                    {"id": "sig1", "fields": {"Signal Type": "posted_about_launch"}},
                    {"id": "sig2", "fields": {"Signal Type": "timing_trigger"}},
                ]
            }

            signals = airtable_client.get_signals_for_person(person_record_id)

            assert len(signals) == 2
            # Verify the filter formula was used
            call_args = mock_get.call_args
            assert "filterByFormula" in call_args[1]["params"]


class TestArchivePerson:
    """Tests for archiving (soft-deleting) inactive contacts."""

    def test_archive_person_sets_status(self):
        """Archiving should set a status field instead of hard deleting."""
        with patch('tools.intent_engine.airtable_client.requests.patch') as mock_patch:
            mock_patch.return_value.raise_for_status = MagicMock()
            mock_patch.return_value.json.return_value = {"id": "rec123"}

            result = airtable_client.archive_person("rec123", reason="inactive_90_days")

            call_args = mock_patch.call_args
            payload = call_args[1]["json"]

            # Should set Status to "Archived"
            assert payload["fields"]["Status"] == "Archived"
            assert "Archive Reason" in payload["fields"]
            assert "Archived At" in payload["fields"]


class TestDeletePerson:
    """Tests for hard deleting contacts (if needed)."""

    def test_delete_person_removes_record(self):
        """Delete should remove the person record from Airtable."""
        with patch('tools.intent_engine.airtable_client.requests.delete') as mock_delete:
            mock_delete.return_value.raise_for_status = MagicMock()
            mock_delete.return_value.json.return_value = {"deleted": True, "id": "rec123"}

            result = airtable_client.delete_person("rec123")

            assert result["deleted"] is True


class TestGetInactivePeople:
    """Tests for the main function to get all inactive people."""

    def test_get_inactive_people_returns_list(self):
        """Should return a list of people who are inactive."""
        # Mock get_all_people to return mixed active/inactive
        mock_people = [
            {
                "id": "rec1",
                "fields": {"Name": "Active"},
                "createdTime": (datetime.now(timezone.utc) - timedelta(days=100)).isoformat(),
            },
            {
                "id": "rec2",
                "fields": {"Name": "Inactive"},
                "createdTime": (datetime.now(timezone.utc) - timedelta(days=200)).isoformat(),
            },
        ]

        # Active person has recent signal
        signals_rec1 = [
            {"id": "s1", "fields": {"Signal Timestamp": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()}}
        ]
        # Inactive person has old signal
        signals_rec2 = [
            {"id": "s2", "fields": {"Signal Timestamp": (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()}}
        ]

        with patch.object(airtable_client, 'get_all_people', return_value=mock_people):
            with patch.object(airtable_client, 'get_signals_for_person') as mock_signals:
                mock_signals.side_effect = [signals_rec1, signals_rec2]

                inactive = airtable_client.get_inactive_people(inactive_days=90)

                assert len(inactive) == 1
                assert inactive[0]["id"] == "rec2"


class TestCleanupInactiveFunction:
    """Tests for the main cleanup orchestration function."""

    def test_cleanup_dry_run_does_not_delete(self):
        """Dry run should report but not delete/archive."""
        mock_inactive = [
            {"id": "rec1", "fields": {"Name": "Inactive 1"}},
            {"id": "rec2", "fields": {"Name": "Inactive 2"}},
        ]

        with patch.object(airtable_client, 'get_inactive_people', return_value=mock_inactive):
            with patch.object(airtable_client, 'archive_person') as mock_archive:
                result = airtable_client.cleanup_inactive(days=90, dry_run=True)

                # Should not call archive in dry run
                mock_archive.assert_not_called()

                # Should report what would be removed
                assert result["would_remove"] == 2
                assert result["removed"] == 0

    def test_cleanup_actually_archives(self):
        """When not dry run, should actually archive the contacts."""
        mock_inactive = [
            {"id": "rec1", "fields": {"Name": "Inactive 1"}},
            {"id": "rec2", "fields": {"Name": "Inactive 2"}},
        ]

        with patch.object(airtable_client, 'get_inactive_people', return_value=mock_inactive):
            with patch.object(airtable_client, 'archive_person') as mock_archive:
                mock_archive.return_value = {"id": "rec1"}

                result = airtable_client.cleanup_inactive(days=90, dry_run=False)

                # Should call archive for each inactive person
                assert mock_archive.call_count == 2
                assert result["removed"] == 2

    def test_cleanup_returns_summary(self):
        """Cleanup should return a summary of actions taken."""
        mock_inactive = [
            {"id": "rec1", "fields": {"Name": "Inactive 1"}},
        ]

        with patch.object(airtable_client, 'get_inactive_people', return_value=mock_inactive):
            with patch.object(airtable_client, 'archive_person') as mock_archive:
                mock_archive.return_value = {"id": "rec1"}

                result = airtable_client.cleanup_inactive(days=90, dry_run=False)

                assert "removed" in result
                assert "would_remove" in result
                assert "inactive_days" in result
                assert "people" in result  # List of who was removed
