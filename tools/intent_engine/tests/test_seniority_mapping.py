"""
Tests for Issue 2: Job Title -> Seniority Mapping

The seniority detection function must correctly map common job title variations
to the correct Seniority dropdown values.
"""
import pytest
from tools.intent_engine.employee_scraper import detect_seniority


class TestSeniorityMapping:
    """Test comprehensive job title to seniority mapping."""

    # C-Level variations
    @pytest.mark.parametrize("title,expected", [
        ("CEO", "C-Level"),
        ("Chief Executive Officer", "C-Level"),
        ("CFO", "C-Level"),
        ("Chief Financial Officer", "C-Level"),
        ("CMO", "C-Level"),
        ("Chief Marketing Officer", "C-Level"),
        ("CTO", "C-Level"),
        ("Chief Technology Officer", "C-Level"),
        ("CRO", "C-Level"),
        ("Chief Revenue Officer", "C-Level"),
        ("COO", "C-Level"),
        ("Chief Operating Officer", "C-Level"),
        ("Chief Brand Officer", "C-Level"),
        ("C-Suite Executive", "C-Level"),
    ])
    def test_c_level_titles(self, title, expected):
        """C-Level executives should map to C-Level."""
        assert detect_seniority(title) == expected

    # VP variations
    @pytest.mark.parametrize("title,expected", [
        ("VP Marketing", "VP+"),
        ("VP of Marketing", "VP+"),
        ("Vice President Marketing", "VP+"),
        ("Vice President of Brand", "VP+"),
        ("V.P. Marketing", "VP+"),
        ("V.P. of Marketing", "VP+"),
        ("SVP Marketing", "VP+"),
        ("Senior Vice President", "VP+"),
        ("EVP Marketing", "VP+"),
        ("Executive Vice President", "VP+"),
        ("AVP Marketing", "VP+"),  # Associate VP
        ("Group VP", "VP+"),
    ])
    def test_vp_titles(self, title, expected):
        """VP titles should map to VP+."""
        assert detect_seniority(title) == expected

    # Director variations
    @pytest.mark.parametrize("title,expected", [
        ("Director of Marketing", "Director"),
        ("Marketing Director", "Director"),
        ("Dir Marketing", "Director"),
        ("Dir. of Brand", "Director"),
        ("Sr Director", "Director"),
        ("Senior Director", "Director"),
        ("Sr. Director", "Director"),
        ("Associate Director", "Director"),
        ("Group Director", "Director"),
        ("Executive Director", "Director"),
        ("Managing Director", "Director"),  # Could be VP+ in some orgs
        ("Head of Marketing", "Director"),  # Head of often = Director
        ("Head of Brand", "Director"),
    ])
    def test_director_titles(self, title, expected):
        """Director titles should map to Director."""
        assert detect_seniority(title) == expected

    # Senior Manager variations
    @pytest.mark.parametrize("title,expected", [
        ("Senior Manager Marketing", "Senior Manager"),
        ("Sr Manager Marketing", "Senior Manager"),
        ("Sr. Manager Marketing", "Senior Manager"),
        ("Sen Manager Marketing", "Senior Manager"),
        ("Senior Marketing Manager", "Senior Manager"),
        ("Sr Marketing Manager", "Senior Manager"),
        ("Sr. Marketing Manager", "Senior Manager"),
        ("Senior Brand Manager", "Senior Manager"),
        ("Sr Brand Manager", "Senior Manager"),
        ("Senior Product Manager", "Senior Manager"),
        ("Sr Product Manager", "Senior Manager"),
    ])
    def test_senior_manager_titles(self, title, expected):
        """Senior Manager titles should map to Senior Manager."""
        assert detect_seniority(title) == expected

    # Manager variations
    @pytest.mark.parametrize("title,expected", [
        ("Manager", "Manager"),
        ("Marketing Manager", "Manager"),
        ("Brand Manager", "Manager"),
        ("Product Manager", "Manager"),
        ("Mgr Marketing", "Manager"),
        ("Mgr. Marketing", "Manager"),
        ("Team Lead Marketing", "Manager"),
        ("Lead Marketing Manager", "Manager"),
    ])
    def test_manager_titles(self, title, expected):
        """Manager titles should map to Manager."""
        assert detect_seniority(title) == expected

    # Associate/Individual Contributor
    @pytest.mark.parametrize("title,expected", [
        ("Associate Marketing Manager", "Associate"),
        ("Assoc Marketing Manager", "Associate"),
        ("Assoc. Marketing Manager", "Associate"),
        ("Marketing Associate", "Associate"),
    ])
    def test_associate_titles(self, title, expected):
        """Associate titles should map to Associate."""
        assert detect_seniority(title) == expected

    # Lead variations (should map to Manager or Lead)
    @pytest.mark.parametrize("title,expected", [
        ("Team Lead", "Manager"),
        ("Lead Brand Strategist", "Manager"),
        ("Marketing Lead", "Manager"),
    ])
    def test_lead_titles(self, title, expected):
        """Lead titles should map to Manager."""
        assert detect_seniority(title) == expected

    # Edge cases and mixed signals
    def test_case_insensitivity(self):
        """Seniority detection should be case-insensitive."""
        assert detect_seniority("vp marketing") == "VP+"
        assert detect_seniority("DIRECTOR OF BRAND") == "Director"
        assert detect_seniority("Sr. Marketing Manager") == "Senior Manager"

    def test_no_match_returns_ic(self):
        """Titles without seniority indicators should return IC."""
        assert detect_seniority("Marketing Specialist") == "IC"
        assert detect_seniority("Marketing Analyst") == "IC"
        assert detect_seniority("Coordinator") == "IC"
