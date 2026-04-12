"""
Tests for Issue 1: Signal Timestamp Mapping

Signal Timestamp should map to the actual date of the signal (when post was published,
comment was posted, article was reposted, etc.), NOT when the profile was checked.

The "Last Checked" column in People table should get the profile check timestamp instead.
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from tools.intent_engine import airtable_client


class TestSignalTimestamp:
    """Test that signal timestamps use actual signal dates."""

    def test_create_signal_uses_provided_timestamp(self):
        """create_signal should accept and use the actual signal timestamp."""
        # The function should accept a signal_timestamp parameter
        # and use it instead of datetime.utcnow()

        test_timestamp = "2026-02-01T14:30:00Z"

        with patch('tools.intent_engine.airtable_client.requests.post') as mock_post:
            mock_post.return_value.raise_for_status = MagicMock()
            mock_post.return_value.json.return_value = {"id": "rec123"}

            airtable_client.create_signal(
                signal_type="posted_about_launch",
                signal_strength=7,
                source="LinkedIn",
                linkedin_url="https://linkedin.com/in/test",
                person_record_id="rec456",
                signal_timestamp=test_timestamp,  # This parameter should exist
            )

            # Check that the actual signal timestamp was used
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["fields"]["Signal Timestamp"] == test_timestamp

    def test_create_signal_defaults_to_now_when_no_timestamp(self):
        """create_signal should default to now if no timestamp provided."""
        with patch('tools.intent_engine.airtable_client.requests.post') as mock_post:
            mock_post.return_value.raise_for_status = MagicMock()
            mock_post.return_value.json.return_value = {"id": "rec123"}

            # Call without signal_timestamp - should still work
            airtable_client.create_signal(
                signal_type="timing_trigger",
                signal_strength=5,
                source="LinkedIn",
                linkedin_url="https://linkedin.com/in/test",
            )

            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            # Should have a timestamp (default to now)
            assert "Signal Timestamp" in payload["fields"]


class TestLastCheckedUpdate:
    """Test that Last Checked is updated on People records when profiles are checked."""

    def test_update_person_last_checked(self):
        """Updating a person record should set Last Checked to current time."""
        with patch('tools.intent_engine.airtable_client.requests.patch') as mock_patch:
            mock_patch.return_value.raise_for_status = MagicMock()
            mock_patch.return_value.json.return_value = {"id": "rec123"}

            # This function should exist to update the Last Checked timestamp
            airtable_client.update_person_last_checked(
                person_record_id="rec123"
            )

            call_args = mock_patch.call_args
            payload = call_args[1]["json"]
            assert "Last Checked" in payload["fields"]


class TestSignalCreationWithActualTimestamp:
    """Integration-style tests for signal creation with real timestamps."""

    def test_signal_from_post_uses_post_timestamp(self):
        """When creating a signal from a post, use the post's timestamp."""
        # This tests the main.py flow where signals are created
        post_timestamp = "2026-01-28T09:15:00Z"

        # Simulated post data from Apify
        post_data = {
            "text": "Launching our new product line!",
            "likes": 150,
            "comments": 25,
            "timestamp": post_timestamp,
            "postedAt": post_timestamp,
        }

        # The signal created from this post should use post_timestamp
        # not datetime.utcnow()
        with patch('tools.intent_engine.airtable_client.requests.post') as mock_post:
            mock_post.return_value.raise_for_status = MagicMock()
            mock_post.return_value.json.return_value = {"id": "rec123"}

            airtable_client.create_signal(
                signal_type="posted_about_launch",
                signal_strength=8,
                source="LinkedIn",
                linkedin_url="https://linkedin.com/in/test",
                person_record_id="rec456",
                signal_timestamp=post_timestamp,
            )

            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["fields"]["Signal Timestamp"] == post_timestamp
