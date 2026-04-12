#!/usr/bin/env python3
"""FIX 5: Add fingerprint persistence per profile.

After first launch, save Camoufox fingerprint config alongside profile data.
On subsequent launches, pass saved fingerprint back so each profile looks like
the same device every time.
"""
import sys

filepath = '/opt/baas/profile_manager.py'

with open(filepath, 'r') as f:
    content = f.read()

# Replace the entire file with updated version that includes fingerprint persistence
new_content = '''"""Layer 6: Multi-Account Profile Isolation — Per-profile fingerprint, proxy, timezone, schedule.

Maps named profiles to their proxy provider, fingerprint seed, schedule window,
and Camoufox launch kwargs for consistent identity across sessions.

FIX 5 (2026-04-06): Added fingerprint persistence — saves/loads Camoufox fingerprint
config per profile so each profile looks like the same device every time.
"""
import hashlib, json, logging, os, random
from datetime import datetime
from zoneinfo import ZoneInfo

log = logging.getLogger('baas.profile_manager')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE = os.path.join(BASE_DIR, 'keys.json')
PROFILES_CONFIG_FILE = os.path.join(BASE_DIR, 'managed_profiles.json')
FINGERPRINTS_DIR = os.path.join(BASE_DIR, 'fingerprints')

# Ensure fingerprints directory exists
os.makedirs(FINGERPRINTS_DIR, exist_ok=True)


def _load_proxy_providers() -> dict:
    try:
        with open(KEYS_FILE) as f:
            return json.load(f).get('proxy_providers', {})
    except Exception:
        return {}


def _fingerprint_path(profile_name: str) -> str:
    """Get path to saved fingerprint for a profile."""
    safe_name = profile_name.replace('/', '_').replace('..', '_')
    return os.path.join(FINGERPRINTS_DIR, f'{safe_name}_fingerprint.json')


class ProfileManager:
    """Manages per-profile isolation: fingerprint + proxy + timezone + cookies."""

    # Default profile definitions — can be extended via managed_profiles.json
    BUILTIN_PROFILES = {
        'jared-linkedin': {
            'proxy_provider': 'floppydata-jared',
            'timezone': 'America/New_York',
            'locale': 'en-US',
            'screen': {'width': 1920, 'height': 1080},
            'os': 'windows',
            'fingerprint_seed': 'jared-linkedin-v1',
            'schedule': {
                'start': '08:30',
                'end': '18:30',
                'timezone': 'America/New_York',
            },
        },
        'nathan-linkedin': {
            'proxy_provider': 'floppydata-nathan',
            'timezone': 'America/New_York',
            'locale': 'en-US',
            'screen': {'width': 1440, 'height': 900},
            'os': 'macos',
            'fingerprint_seed': 'nathan-linkedin-v1',
            'schedule': {
                'start': '09:00',
                'end': '17:00',
                'timezone': 'America/New_York',
            },
        },
    }

    def __init__(self):
        self.profiles = dict(self.BUILTIN_PROFILES)
        self._load_extra_profiles()

    def _load_extra_profiles(self):
        """Merge any profiles from managed_profiles.json."""
        if os.path.exists(PROFILES_CONFIG_FILE):
            try:
                with open(PROFILES_CONFIG_FILE) as f:
                    extras = json.load(f)
                self.profiles.update(extras)
                log.info(f'Loaded {len(extras)} extra managed profiles')
            except Exception as e:
                log.warning(f'Failed to load managed profiles: {e}')

    def is_managed(self, profile_name: str) -> bool:
        """Check if this profile has a managed configuration."""
        return profile_name in self.profiles

    def get_profile(self, profile_name: str) -> dict:
        """Get profile config or None."""
        return self.profiles.get(profile_name)

    def get_proxy_url(self, profile_name: str) -> str:
        """Resolve proxy from keys.json provider for this profile."""
        profile = self.profiles.get(profile_name)
        if not profile or not profile.get('proxy_provider'):
            return None
        provider_name = profile['proxy_provider']
        providers = _load_proxy_providers()
        p = providers.get(provider_name)
        if not p:
            log.warning(f'Proxy provider {provider_name} not found for profile {profile_name}')
            return None
        if not p.get('username') or not p.get('password'):
            log.warning(f'Proxy provider {provider_name} not configured')
            return None
        proto = p.get('protocol', 'http')
        return f"{proto}://{p['username']}:{p['password']}@{p['host']}:{p['port']}"

    def can_run_now(self, profile_name: str) -> bool:
        """Check if profile is within its schedule window."""
        profile = self.profiles.get(profile_name)
        if not profile or not profile.get('schedule'):
            return True  # No schedule = always allowed
        sched = profile['schedule']
        tz = ZoneInfo(sched.get("timezone", "America/New_York"))
        now = datetime.now(tz)
        start_parts = sched['start'].split(':')
        end_parts = sched['end'].split(':')
        start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
        end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])
        current_minutes = now.hour * 60 + now.minute
        return start_minutes <= current_minutes <= end_minutes

    def get_fingerprint_config(self, profile_name: str) -> dict:
        """Get persistent fingerprint for this profile.

        FIX 5: First checks for a saved fingerprint file. If found, uses it
        for consistency. If not, generates one from seed and saves it.
        Same profile = same fingerprint every time.
        """
        profile = self.profiles.get(profile_name)
        if not profile:
            return {}

        # Check for saved fingerprint first
        fp_path = _fingerprint_path(profile_name)
        if os.path.exists(fp_path):
            try:
                with open(fp_path, 'r') as f:
                    saved_fp = json.load(f)
                log.info(f'Loaded saved fingerprint for profile {profile_name}')
                return saved_fp
            except Exception as e:
                log.warning(f'Failed to load saved fingerprint for {profile_name}: {e}, regenerating...')

        # Generate deterministic fingerprint from seed
        seed = profile.get('fingerprint_seed', profile_name)
        h = hashlib.sha256(seed.encode()).hexdigest()
        rng = random.Random(int(h[:16], 16))
        screen_cfg = profile.get('screen', {'width': 1920, 'height': 1080})
        # Small jitter on screen (within +-10px so it looks natural but stays consistent per seed)
        w = screen_cfg['width'] + rng.randint(-5, 5) * 2  # even numbers
        h_val = screen_cfg['height'] + rng.randint(-5, 5) * 2

        fp_config = {
            'os': profile.get('os', 'windows'),
            'screen_width': w,
            'screen_height': h_val,
            'locale': profile.get('locale', 'en-US'),
            'timezone': profile.get('timezone', 'America/New_York'),
        }

        # Save for future use
        self.save_fingerprint(profile_name, fp_config)
        return fp_config

    def save_fingerprint(self, profile_name: str, fp_config: dict):
        """Save fingerprint config for a profile (FIX 5: persistence).

        Called after first launch or when Camoufox generates a fingerprint.
        Subsequent launches will use this saved config.
        """
        fp_path = _fingerprint_path(profile_name)
        try:
            with open(fp_path, 'w') as f:
                json.dump(fp_config, f, indent=2)
            log.info(f'Saved fingerprint for profile {profile_name} to {fp_path}')
        except Exception as e:
            log.warning(f'Failed to save fingerprint for {profile_name}: {e}')

    def save_fingerprint_from_browser(self, profile_name: str, browser_fingerprint: dict):
        """Save Camoufox-generated fingerprint data after first browser launch.

        This captures the actual fingerprint Camoufox generated (UA, fonts, etc.)
        and saves it so the same values are used on subsequent launches.
        """
        fp_path = _fingerprint_path(profile_name)
        existing = {}
        if os.path.exists(fp_path):
            try:
                with open(fp_path, 'r') as f:
                    existing = json.load(f)
            except:
                pass

        # Merge browser fingerprint into existing config
        existing.update(browser_fingerprint)

        try:
            with open(fp_path, 'w') as f:
                json.dump(existing, f, indent=2)
            log.info(f'Saved browser fingerprint for profile {profile_name}: {list(browser_fingerprint.keys())}')
        except Exception as e:
            log.warning(f'Failed to save browser fingerprint for {profile_name}: {e}')

    def get_launch_config(self, profile_name: str) -> dict:
        """Get full launch config including proxy, fingerprint, timezone.

        Returns dict compatible with Camoufox AsyncNewBrowser kwargs.
        """
        profile = self.profiles.get(profile_name)
        if not profile:
            return {}

        fp = self.get_fingerprint_config(profile_name)
        proxy_url = self.get_proxy_url(profile_name)

        config = {
            'os': fp.get('os', 'windows'),
            'humanize': True,
            'block_webrtc': True,
        }

        # Screen — use Camoufox Screen object params
        config['screen_min_width'] = fp['screen_width']
        config['screen_max_width'] = fp['screen_width']
        config['screen_min_height'] = fp['screen_height']
        config['screen_max_height'] = fp['screen_height']

        # Locale
        config['locale'] = fp.get('locale', 'en-US')

        # Proxy
        if proxy_url:
            config['proxy_url'] = proxy_url

        return config

    def list_profiles(self) -> dict:
        """List all managed profiles and their current status."""
        result = {}
        for name, cfg in self.profiles.items():
            fp_path = _fingerprint_path(name)
            result[name] = {
                'proxy_provider': cfg.get('proxy_provider'),
                'timezone': cfg.get('timezone'),
                'os': cfg.get('os'),
                'screen': cfg.get('screen'),
                'schedule': cfg.get('schedule'),
                'can_run_now': self.can_run_now(name),
                'has_saved_fingerprint': os.path.exists(fp_path),
            }
        return result


# Module-level singleton
profile_manager = ProfileManager()
'''

with open(filepath, 'w') as f:
    f.write(new_content)

print("FIX 5: COMPLETE — Fingerprint persistence added to profile_manager.py")
print(f"  - Fingerprints saved to: {FINGERPRINTS_DIR}")
print("  - Loaded on subsequent launches for consistent device identity")
print("  - save_fingerprint_from_browser() available for Camoufox-generated data")
