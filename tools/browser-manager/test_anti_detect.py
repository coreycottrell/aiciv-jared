#!/usr/bin/env python3
"""
test_anti_detect.py - Test suite for browser fingerprint manager.

TDD: Written FIRST, then implementation built to pass these tests.
Tests fingerprint uniqueness, profile CRUD, session persistence,
proxy configuration, and automation API.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestFingerprintGeneration(unittest.TestCase):
    """Test that BrowserForge generates unique, realistic fingerprints."""

    def test_import_fingerprint_gen(self):
        """fingerprint_gen module should be importable."""
        from fingerprint_gen import generate_fingerprint
        self.assertTrue(callable(generate_fingerprint))

    def test_generate_fingerprint_returns_dict(self):
        """Generated fingerprint should be a serializable dict."""
        from fingerprint_gen import generate_fingerprint
        fp = generate_fingerprint()
        self.assertIsInstance(fp, dict)
        # Must be JSON-serializable for storage
        json_str = json.dumps(fp)
        self.assertIsInstance(json_str, str)

    def test_fingerprint_has_required_fields(self):
        """Fingerprint must contain all key spoofing categories."""
        from fingerprint_gen import generate_fingerprint
        fp = generate_fingerprint()
        required_keys = [
            'navigator',
            'screen',
            'videoCard',
            'fonts',
            'audioCodecs',
            'videoCodecs',
        ]
        for key in required_keys:
            self.assertIn(key, fp, f"Missing required fingerprint field: {key}")

    def test_fingerprints_are_unique(self):
        """Two generated fingerprints should differ (not identical)."""
        from fingerprint_gen import generate_fingerprint
        fp1 = generate_fingerprint()
        fp2 = generate_fingerprint()
        # At minimum, user agents or screen sizes should differ across runs
        # (statistically near-certain with randomization)
        fp1_json = json.dumps(fp1, sort_keys=True)
        fp2_json = json.dumps(fp2, sort_keys=True)
        self.assertNotEqual(fp1_json, fp2_json,
                            "Two fingerprints should not be identical")

    def test_navigator_has_user_agent(self):
        """Navigator fingerprint must include a user agent string."""
        from fingerprint_gen import generate_fingerprint
        fp = generate_fingerprint()
        nav = fp['navigator']
        self.assertIn('userAgent', nav)
        self.assertIsInstance(nav['userAgent'], str)
        self.assertGreater(len(nav['userAgent']), 20)

    def test_screen_has_dimensions(self):
        """Screen fingerprint must have width and height."""
        from fingerprint_gen import generate_fingerprint
        fp = generate_fingerprint()
        screen = fp['screen']
        self.assertIn('width', screen)
        self.assertIn('height', screen)
        self.assertGreater(screen['width'], 0)
        self.assertGreater(screen['height'], 0)

    def test_generate_multiple_fingerprints_batch(self):
        """Should be able to generate 10 fingerprints without error."""
        from fingerprint_gen import generate_fingerprint
        fingerprints = [generate_fingerprint() for _ in range(10)]
        self.assertEqual(len(fingerprints), 10)
        # Check they're not all the same
        unique_uas = set(fp['navigator']['userAgent'] for fp in fingerprints)
        self.assertGreater(len(unique_uas), 1,
                           "10 fingerprints should have at least 2 unique user agents")


class TestProfileManager(unittest.TestCase):
    """Test profile CRUD operations."""

    def setUp(self):
        """Create a temp directory for test profiles."""
        self.test_dir = tempfile.mkdtemp(prefix='browser_mgr_test_')
        self.profiles_dir = os.path.join(self.test_dir, 'profiles')
        os.makedirs(self.profiles_dir)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _get_manager(self):
        from browser_manager import ProfileManager
        return ProfileManager(profiles_dir=self.profiles_dir)

    def test_create_profile(self):
        """Should create a new profile with fingerprint and config."""
        mgr = self._get_manager()
        profile = mgr.create_profile(name="test-1")
        self.assertEqual(profile['name'], 'test-1')
        self.assertIn('fingerprint', profile)
        self.assertIn('created_at', profile)
        # Should persist to disk
        profile_path = os.path.join(self.profiles_dir, 'test-1', 'profile.json')
        self.assertTrue(os.path.exists(profile_path))

    def test_create_profile_with_proxy(self):
        """Should store proxy config in profile."""
        mgr = self._get_manager()
        profile = mgr.create_profile(
            name="proxied",
            proxy="socks5://user:pass@1.2.3.4:1080"
        )
        self.assertEqual(profile['proxy'], 'socks5://user:pass@1.2.3.4:1080')

    def test_create_duplicate_profile_raises(self):
        """Creating a profile with existing name should raise."""
        mgr = self._get_manager()
        mgr.create_profile(name="dupe")
        with self.assertRaises(ValueError):
            mgr.create_profile(name="dupe")

    def test_list_profiles(self):
        """Should list all created profiles."""
        mgr = self._get_manager()
        mgr.create_profile(name="alpha")
        mgr.create_profile(name="bravo")
        mgr.create_profile(name="charlie")
        profiles = mgr.list_profiles()
        names = [p['name'] for p in profiles]
        self.assertIn('alpha', names)
        self.assertIn('bravo', names)
        self.assertIn('charlie', names)
        self.assertEqual(len(profiles), 3)

    def test_list_empty(self):
        """Listing with no profiles should return empty list."""
        mgr = self._get_manager()
        profiles = mgr.list_profiles()
        self.assertEqual(profiles, [])

    def test_get_profile(self):
        """Should retrieve a specific profile by name."""
        mgr = self._get_manager()
        mgr.create_profile(name="fetch-me")
        profile = mgr.get_profile("fetch-me")
        self.assertEqual(profile['name'], 'fetch-me')

    def test_get_nonexistent_profile_raises(self):
        """Getting a non-existent profile should raise."""
        mgr = self._get_manager()
        with self.assertRaises(FileNotFoundError):
            mgr.get_profile("ghost")

    def test_delete_profile(self):
        """Should delete profile and its data directory."""
        mgr = self._get_manager()
        mgr.create_profile(name="delete-me")
        profile_dir = os.path.join(self.profiles_dir, 'delete-me')
        self.assertTrue(os.path.exists(profile_dir))
        mgr.delete_profile("delete-me")
        self.assertFalse(os.path.exists(profile_dir))

    def test_delete_nonexistent_profile_raises(self):
        """Deleting a non-existent profile should raise."""
        mgr = self._get_manager()
        with self.assertRaises(FileNotFoundError):
            mgr.delete_profile("nope")

    def test_profile_has_data_dir(self):
        """Each profile should have a user data directory for persistence."""
        mgr = self._get_manager()
        profile = mgr.create_profile(name="persistent")
        data_dir = os.path.join(self.profiles_dir, 'persistent', 'user_data')
        self.assertTrue(os.path.isdir(data_dir))

    def test_profile_fingerprint_persists(self):
        """Fingerprint should be identical when re-loaded."""
        mgr = self._get_manager()
        created = mgr.create_profile(name="persist-fp")
        loaded = mgr.get_profile("persist-fp")
        self.assertEqual(
            json.dumps(created['fingerprint'], sort_keys=True),
            json.dumps(loaded['fingerprint'], sort_keys=True)
        )


class TestProxyConfig(unittest.TestCase):
    """Test proxy URL parsing and configuration."""

    def test_parse_socks5_proxy(self):
        """Should parse SOCKS5 proxy URL correctly."""
        from browser_manager import parse_proxy_url
        result = parse_proxy_url("socks5://user:pass@1.2.3.4:1080")
        self.assertEqual(result['server'], 'socks5://1.2.3.4:1080')
        self.assertEqual(result['username'], 'user')
        self.assertEqual(result['password'], 'pass')

    def test_parse_http_proxy(self):
        """Should parse HTTP proxy URL correctly."""
        from browser_manager import parse_proxy_url
        result = parse_proxy_url("http://proxy.example.com:8080")
        self.assertEqual(result['server'], 'http://proxy.example.com:8080')
        self.assertIsNone(result.get('username'))

    def test_parse_none_proxy(self):
        """None proxy should return None."""
        from browser_manager import parse_proxy_url
        result = parse_proxy_url(None)
        self.assertIsNone(result)

    def test_parse_empty_proxy(self):
        """Empty string proxy should return None."""
        from browser_manager import parse_proxy_url
        result = parse_proxy_url("")
        self.assertIsNone(result)


class TestCamoufoxIntegration(unittest.TestCase):
    """Test Camoufox launch option generation (no actual browser launch)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix='browser_mgr_test_')
        self.profiles_dir = os.path.join(self.test_dir, 'profiles')
        os.makedirs(self.profiles_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_build_launch_options(self):
        """Should build Camoufox-compatible launch options from profile."""
        from browser_manager import ProfileManager
        mgr = ProfileManager(profiles_dir=self.profiles_dir)
        profile = mgr.create_profile(name="launch-test")
        opts = mgr.build_launch_options("launch-test")
        self.assertIsInstance(opts, dict)
        # Should have persistent context path
        self.assertIn('user_data_dir', opts)

    def test_launch_options_include_proxy(self):
        """Launch options should include proxy when profile has one."""
        from browser_manager import ProfileManager
        mgr = ProfileManager(profiles_dir=self.profiles_dir)
        mgr.create_profile(name="proxy-launch", proxy="socks5://1.2.3.4:1080")
        opts = mgr.build_launch_options("proxy-launch")
        self.assertIn('proxy', opts)

    def test_launch_options_no_proxy_when_none(self):
        """Launch options should not include proxy when profile has none."""
        from browser_manager import ProfileManager
        mgr = ProfileManager(profiles_dir=self.profiles_dir)
        mgr.create_profile(name="no-proxy-launch")
        opts = mgr.build_launch_options("no-proxy-launch")
        self.assertNotIn('proxy', opts)


class TestHumanization(unittest.TestCase):
    """Test human-like behavior pattern generation."""

    def test_random_delay_in_range(self):
        """Random delays should be within reasonable human range."""
        from browser_manager import human_delay
        for _ in range(50):
            delay = human_delay()
            self.assertGreaterEqual(delay, 0.05)
            self.assertLessEqual(delay, 3.0)

    def test_random_delay_custom_range(self):
        """Custom delay range should be respected."""
        from browser_manager import human_delay
        for _ in range(50):
            delay = human_delay(min_sec=1.0, max_sec=2.0)
            self.assertGreaterEqual(delay, 1.0)
            self.assertLessEqual(delay, 2.0)


class TestCLIInterface(unittest.TestCase):
    """Test the CLI argument parsing."""

    def test_create_command_parse(self):
        """CLI should parse create command."""
        from browser_manager import build_parser
        parser = build_parser()
        args = parser.parse_args(['create', '--name', 'test-profile'])
        self.assertEqual(args.command, 'create')
        self.assertEqual(args.name, 'test-profile')

    def test_create_with_proxy(self):
        """CLI should parse create with proxy."""
        from browser_manager import build_parser
        parser = build_parser()
        args = parser.parse_args([
            'create', '--name', 'test', '--proxy', 'socks5://1.2.3.4:1080'
        ])
        self.assertEqual(args.proxy, 'socks5://1.2.3.4:1080')

    def test_list_command_parse(self):
        """CLI should parse list command."""
        from browser_manager import build_parser
        parser = build_parser()
        args = parser.parse_args(['list'])
        self.assertEqual(args.command, 'list')

    def test_launch_command_parse(self):
        """CLI should parse launch command."""
        from browser_manager import build_parser
        parser = build_parser()
        args = parser.parse_args(['launch', '--name', 'my-profile'])
        self.assertEqual(args.command, 'launch')
        self.assertEqual(args.name, 'my-profile')

    def test_delete_command_parse(self):
        """CLI should parse delete command."""
        from browser_manager import build_parser
        parser = build_parser()
        args = parser.parse_args(['delete', '--name', 'old-profile'])
        self.assertEqual(args.command, 'delete')
        self.assertEqual(args.name, 'old-profile')

    def test_launch_headless_flag(self):
        """CLI should parse headless flag on launch."""
        from browser_manager import build_parser
        parser = build_parser()
        args = parser.parse_args(['launch', '--name', 'test', '--headless'])
        self.assertTrue(args.headless)

    def test_launch_default_not_headless(self):
        """CLI launch should default to not headless."""
        from browser_manager import build_parser
        parser = build_parser()
        args = parser.parse_args(['launch', '--name', 'test'])
        self.assertFalse(args.headless)


class TestPythonAPI(unittest.TestCase):
    """Test the Python API for automation integration."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix='browser_mgr_test_')
        self.profiles_dir = os.path.join(self.test_dir, 'profiles')
        os.makedirs(self.profiles_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_launch_profile_function_exists(self):
        """launch_profile should be importable from browser_manager."""
        from browser_manager import launch_profile
        self.assertTrue(callable(launch_profile))

    def test_profile_manager_context_manager(self):
        """ProfileManager should work as context manager."""
        from browser_manager import ProfileManager
        with ProfileManager(profiles_dir=self.profiles_dir) as mgr:
            profile = mgr.create_profile(name="ctx-test")
            self.assertEqual(profile['name'], 'ctx-test')


class TestFingerprintUniqueness(unittest.TestCase):
    """Deeper uniqueness tests - the core anti-detection value."""

    def test_50_fingerprints_all_unique_user_agents(self):
        """50 fingerprints should produce many unique user agents."""
        from fingerprint_gen import generate_fingerprint
        uas = set()
        for _ in range(50):
            fp = generate_fingerprint()
            uas.add(fp['navigator']['userAgent'])
        # With randomization, expect significant diversity
        # Allow some duplicates but majority should be unique
        self.assertGreater(len(uas), 5,
                           f"Expected >5 unique UAs from 50 fingerprints, got {len(uas)}")

    def test_fingerprints_have_diverse_screens(self):
        """Fingerprints should show diversity in screen resolutions."""
        from fingerprint_gen import generate_fingerprint
        resolutions = set()
        for _ in range(30):
            fp = generate_fingerprint()
            s = fp['screen']
            resolutions.add((s['width'], s['height']))
        self.assertGreater(len(resolutions), 3,
                           f"Expected >3 unique resolutions from 30 fingerprints, got {len(resolutions)}")

    def test_fingerprints_have_diverse_video_cards(self):
        """Fingerprints should show diversity in WebGL renderers."""
        from fingerprint_gen import generate_fingerprint
        renderers = set()
        for _ in range(30):
            fp = generate_fingerprint()
            vc = fp.get('videoCard', {})
            if isinstance(vc, dict):
                renderers.add(vc.get('renderer', ''))
            else:
                renderers.add(str(vc))
        self.assertGreater(len(renderers), 2,
                           f"Expected >2 unique renderers from 30 fingerprints, got {len(renderers)}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
