#!/usr/bin/env python3
"""
browser_manager.py - GoLogin alternative using Camoufox + BrowserForge.

Profile management CLI and Python API for fingerprinted browser sessions.
Each profile gets a unique fingerprint, optional proxy, and persistent storage.

CLI Usage:
    ./browser_manager.py create --name "campaign-1" --proxy socks5://user:pass@host:port
    ./browser_manager.py list
    ./browser_manager.py launch --name "campaign-1" [--headless]
    ./browser_manager.py delete --name "campaign-1"

Python API:
    from browser_manager import ProfileManager, launch_profile
    mgr = ProfileManager()
    mgr.create_profile("campaign-1", proxy="socks5://...")
    browser, page = launch_profile("campaign-1")
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, Union
from urllib.parse import urlparse

# Default profiles directory (sibling to this script)
DEFAULT_PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles')


def parse_proxy_url(proxy_url: Optional[str]) -> Optional[dict]:
    """
    Parse a proxy URL into Playwright-compatible proxy config.

    Args:
        proxy_url: URL like "socks5://user:pass@host:port" or "http://host:port"

    Returns:
        dict with 'server', 'username', 'password' or None
    """
    if not proxy_url:
        return None

    parsed = urlparse(proxy_url)

    if not parsed.hostname:
        return None

    # Build server URL without credentials
    port_part = f":{parsed.port}" if parsed.port else ""
    server = f"{parsed.scheme}://{parsed.hostname}{port_part}"

    result = {'server': server}

    if parsed.username:
        result['username'] = parsed.username
    if parsed.password:
        result['password'] = parsed.password

    return result


def human_delay(min_sec: float = 0.05, max_sec: float = 3.0) -> float:
    """
    Generate a random human-like delay duration.

    Uses a log-normal-ish distribution to simulate human timing:
    most actions are quick, some are slower (thinking pauses).

    Args:
        min_sec: Minimum delay in seconds
        max_sec: Maximum delay in seconds

    Returns:
        float: Delay duration in seconds
    """
    # Weighted toward shorter delays with occasional longer pauses
    base = random.random() ** 2  # Skewed toward 0
    delay = min_sec + base * (max_sec - min_sec)
    return round(delay, 3)


class ProfileManager:
    """
    Manage browser profiles with unique fingerprints and persistent storage.

    Each profile is stored as a directory under profiles_dir:
        profiles/{name}/profile.json   - Profile config + fingerprint
        profiles/{name}/user_data/     - Persistent browser data (cookies, etc.)
    """

    def __init__(self, profiles_dir: Optional[str] = None):
        self.profiles_dir = profiles_dir or DEFAULT_PROFILES_DIR
        os.makedirs(self.profiles_dir, exist_ok=True)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def create_profile(
        self,
        name: str,
        proxy: Optional[str] = None,
        timezone: Optional[str] = None,
        locale: Optional[str] = None,
    ) -> dict:
        """
        Create a new browser profile with a unique fingerprint.

        Args:
            name: Unique profile name (used as directory name)
            proxy: Optional proxy URL (socks5://..., http://...)
            timezone: Optional timezone override (e.g., "America/New_York")
            locale: Optional locale override (e.g., "en-US")

        Returns:
            dict: The created profile config

        Raises:
            ValueError: If profile name already exists
        """
        profile_dir = os.path.join(self.profiles_dir, name)
        if os.path.exists(profile_dir):
            raise ValueError(f"Profile '{name}' already exists")

        # Create directory structure
        os.makedirs(profile_dir)
        user_data_dir = os.path.join(profile_dir, 'user_data')
        os.makedirs(user_data_dir)

        # Generate unique fingerprint
        from fingerprint_gen import generate_fingerprint
        fingerprint = generate_fingerprint()

        # Build profile config
        profile = {
            'name': name,
            'fingerprint': fingerprint,
            'proxy': proxy,
            'timezone': timezone,
            'locale': locale,
            'user_data_dir': user_data_dir,
            'created_at': datetime.now(timezone if hasattr(timezone, 'utcoffset') else None
                                        or __import__('datetime').timezone.utc).isoformat(),
            'last_launched': None,
        }

        # Save to disk
        profile_path = os.path.join(profile_dir, 'profile.json')
        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=2, default=str)

        return profile

    def list_profiles(self) -> list:
        """
        List all saved profiles.

        Returns:
            list[dict]: List of profile configs sorted by name
        """
        profiles = []
        if not os.path.exists(self.profiles_dir):
            return profiles

        for entry in sorted(os.listdir(self.profiles_dir)):
            profile_path = os.path.join(self.profiles_dir, entry, 'profile.json')
            if os.path.isfile(profile_path):
                with open(profile_path) as f:
                    profiles.append(json.load(f))

        return profiles

    def get_profile(self, name: str) -> dict:
        """
        Get a specific profile by name.

        Args:
            name: Profile name

        Returns:
            dict: Profile config

        Raises:
            FileNotFoundError: If profile doesn't exist
        """
        profile_path = os.path.join(self.profiles_dir, name, 'profile.json')
        if not os.path.isfile(profile_path):
            raise FileNotFoundError(f"Profile '{name}' not found")

        with open(profile_path) as f:
            return json.load(f)

    def delete_profile(self, name: str) -> None:
        """
        Delete a profile and all its data.

        Args:
            name: Profile name

        Raises:
            FileNotFoundError: If profile doesn't exist
        """
        profile_dir = os.path.join(self.profiles_dir, name)
        if not os.path.exists(profile_dir):
            raise FileNotFoundError(f"Profile '{name}' not found")

        import shutil
        shutil.rmtree(profile_dir)

    def build_launch_options(self, name: str, headless: bool = False) -> dict:
        """
        Build Camoufox-compatible launch options from a profile.

        Args:
            name: Profile name
            headless: Whether to run headless

        Returns:
            dict: Launch options for Camoufox
        """
        profile = self.get_profile(name)
        fp = profile['fingerprint']

        opts = {
            'user_data_dir': os.path.join(self.profiles_dir, name, 'user_data'),
            'headless': headless,
        }

        # Fingerprint config for Camoufox
        if fp.get('screen'):
            opts['screen'] = {
                'width': fp['screen'].get('width', 1920),
                'height': fp['screen'].get('height', 1080),
            }

        # WebGL config
        if fp.get('videoCard'):
            opts['webgl_config'] = {
                'renderer': fp['videoCard'].get('renderer', ''),
                'vendor': fp['videoCard'].get('vendor', ''),
            }
            # Detect OS from user agent
            ua = fp.get('navigator', {}).get('userAgent', '')
            if 'Mac' in ua:
                opts['os'] = 'macos'
            elif 'Windows' in ua:
                opts['os'] = 'windows'
            else:
                opts['os'] = 'linux'

        # Fonts
        if fp.get('fonts'):
            opts['fonts'] = fp['fonts']

        # Navigator overrides
        if fp.get('navigator'):
            nav = fp['navigator']
            if nav.get('language'):
                opts['locale'] = nav['language']

        # Timezone override from profile (if set)
        if profile.get('timezone'):
            opts['locale'] = profile['timezone']

        # Locale override from profile
        if profile.get('locale'):
            opts['locale'] = profile['locale']

        # WebRTC blocking (anti-leak)
        opts['block_webrtc'] = True

        # Human-like behavior
        opts['humanize'] = True

        # Proxy
        if profile.get('proxy'):
            proxy_config = parse_proxy_url(profile['proxy'])
            if proxy_config:
                opts['proxy'] = proxy_config

        return opts

    def update_last_launched(self, name: str) -> None:
        """Update the last_launched timestamp for a profile."""
        profile = self.get_profile(name)
        profile['last_launched'] = datetime.now(
            __import__('datetime').timezone.utc
        ).isoformat()
        profile_path = os.path.join(self.profiles_dir, name, 'profile.json')
        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=2, default=str)


def launch_profile(
    name: str,
    profiles_dir: Optional[str] = None,
    headless: bool = False,
) -> Tuple:
    """
    Launch a Camoufox browser with a saved profile's fingerprint.

    This is the primary Python API for automation integration.

    Args:
        name: Profile name to launch
        profiles_dir: Custom profiles directory (default: ./profiles/)
        headless: Run headless (default: False for visual debugging)

    Returns:
        tuple: (browser_or_context, page) ready for automation

    Usage:
        from browser_manager import launch_profile
        browser, page = launch_profile("campaign-1")
        page.goto("https://example.com")
    """
    from playwright.sync_api import sync_playwright
    from camoufox import NewBrowser

    mgr = ProfileManager(profiles_dir=profiles_dir)
    opts = mgr.build_launch_options(name, headless=headless)

    # Extract options Camoufox understands
    user_data_dir = opts.pop('user_data_dir')
    is_headless = opts.pop('headless', False)

    pw = sync_playwright().start()

    # Launch with persistent context for session persistence
    context = NewBrowser(
        pw,
        headless='virtual' if is_headless else False,
        persistent_context=True,
        user_data_dir=user_data_dir,
        **{k: v for k, v in opts.items() if k not in ('user_data_dir',)},
    )

    # For persistent context, context IS the browser context
    page = context.new_page()

    # Update last launched
    mgr.update_last_launched(name)

    return context, page


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog='browser-manager',
        description='Browser fingerprint profile manager (GoLogin alternative)',
    )
    parser.add_argument(
        '--profiles-dir',
        default=DEFAULT_PROFILES_DIR,
        help='Custom profiles directory'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # create
    create_p = subparsers.add_parser('create', help='Create a new browser profile')
    create_p.add_argument('--name', required=True, help='Profile name')
    create_p.add_argument('--proxy', default=None, help='Proxy URL (socks5://... or http://...)')
    create_p.add_argument('--timezone', default=None, help='Timezone (e.g., America/New_York)')
    create_p.add_argument('--locale', default=None, help='Locale (e.g., en-US)')

    # list
    subparsers.add_parser('list', help='List all profiles')

    # launch
    launch_p = subparsers.add_parser('launch', help='Launch a browser with profile')
    launch_p.add_argument('--name', required=True, help='Profile name to launch')
    launch_p.add_argument('--headless', action='store_true', help='Run in headless mode')
    launch_p.add_argument('--url', default=None, help='URL to open on launch')

    # delete
    delete_p = subparsers.add_parser('delete', help='Delete a profile')
    delete_p.add_argument('--name', required=True, help='Profile name to delete')

    # info
    info_p = subparsers.add_parser('info', help='Show detailed profile info')
    info_p.add_argument('--name', required=True, help='Profile name')

    return parser


def cli_create(args):
    """Handle create command."""
    mgr = ProfileManager(profiles_dir=args.profiles_dir)
    try:
        profile = mgr.create_profile(
            name=args.name,
            proxy=args.proxy,
            timezone=args.timezone,
            locale=args.locale,
        )
        ua = profile['fingerprint'].get('navigator', {}).get('userAgent', 'N/A')
        screen = profile['fingerprint'].get('screen', {})
        res = f"{screen.get('width', '?')}x{screen.get('height', '?')}"
        print(f"[+] Profile '{args.name}' created")
        print(f"    User-Agent: {ua[:80]}...")
        print(f"    Screen: {res}")
        print(f"    Proxy: {args.proxy or 'none'}")
        print(f"    Data dir: {profile['user_data_dir']}")
    except ValueError as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


def cli_list(args):
    """Handle list command."""
    mgr = ProfileManager(profiles_dir=args.profiles_dir)
    profiles = mgr.list_profiles()
    if not profiles:
        print("[i] No profiles found.")
        return

    print(f"{'Name':<25} {'User-Agent':<50} {'Proxy':<30} {'Last Launch'}")
    print("-" * 135)
    for p in profiles:
        ua = p.get('fingerprint', {}).get('navigator', {}).get('userAgent', 'N/A')
        ua_short = ua[:47] + '...' if len(ua) > 50 else ua
        proxy = p.get('proxy', 'none') or 'none'
        proxy_short = proxy[:27] + '...' if len(proxy) > 30 else proxy
        last = p.get('last_launched', 'never') or 'never'
        if last != 'never':
            last = last[:19]  # Trim to datetime
        print(f"{p['name']:<25} {ua_short:<50} {proxy_short:<30} {last}")


def cli_launch(args):
    """Handle launch command."""
    print(f"[*] Launching profile '{args.name}'...")
    try:
        context, page = launch_profile(
            name=args.name,
            profiles_dir=args.profiles_dir,
            headless=args.headless,
        )
        if args.url:
            page.goto(args.url)
            print(f"[+] Navigated to {args.url}")

        print(f"[+] Browser launched. Press Ctrl+C to close.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Closing browser...")
            context.close()
    except FileNotFoundError as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[!] Launch error: {e}", file=sys.stderr)
        sys.exit(1)


def cli_delete(args):
    """Handle delete command."""
    mgr = ProfileManager(profiles_dir=args.profiles_dir)
    try:
        mgr.delete_profile(args.name)
        print(f"[+] Profile '{args.name}' deleted")
    except FileNotFoundError as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


def cli_info(args):
    """Handle info command."""
    mgr = ProfileManager(profiles_dir=args.profiles_dir)
    try:
        profile = mgr.get_profile(args.name)
        print(json.dumps(profile, indent=2, default=str))
    except FileNotFoundError as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        'create': cli_create,
        'list': cli_list,
        'launch': cli_launch,
        'delete': cli_delete,
        'info': cli_info,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
