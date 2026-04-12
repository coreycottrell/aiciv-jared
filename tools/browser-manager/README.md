# Browser Fingerprint Manager

Internal GoLogin alternative using **Camoufox** (Firefox fork with fingerprint spoofing) + **BrowserForge** (realistic fingerprint generation).

Zero cost. Full control. Each profile looks like a unique real person.

## Quick Start

### Install Dependencies

```bash
pip install camoufox browserforge playwright
python -m playwright install firefox
```

### Create a Profile

```bash
./browser_manager.py create --name "campaign-1"
./browser_manager.py create --name "campaign-2" --proxy socks5://user:pass@1.2.3.4:1080
./browser_manager.py create --name "campaign-eu" --proxy http://proxy.eu:8080 --locale de-DE
```

### List Profiles

```bash
./browser_manager.py list
```

### Launch a Browser

```bash
# Interactive (opens visible browser)
./browser_manager.py launch --name "campaign-1"

# Open a URL immediately
./browser_manager.py launch --name "campaign-1" --url https://example.com

# Headless mode (no visible window)
./browser_manager.py launch --name "campaign-1" --headless
```

### View Profile Details

```bash
./browser_manager.py info --name "campaign-1"
```

### Delete a Profile

```bash
./browser_manager.py delete --name "campaign-1"
```

## Python API (Automation Integration)

```python
from browser_manager import ProfileManager, launch_profile

# Create and manage profiles
mgr = ProfileManager()
mgr.create_profile("auto-1", proxy="socks5://1.2.3.4:1080")

# Launch a browser with the profile's fingerprint
browser, page = launch_profile("auto-1")
page.goto("https://example.com")

# Do your automation work...
page.fill("#email", "test@example.com")
page.click("button[type=submit]")

# Session data (cookies, localStorage) persists automatically
browser.close()

# Next launch will have the same fingerprint + saved session
browser2, page2 = launch_profile("auto-1")
# Cookies and login state are still there
```

### Context Manager Pattern

```python
from browser_manager import ProfileManager

with ProfileManager() as mgr:
    mgr.create_profile("session-1")
    profiles = mgr.list_profiles()
```

### Human-Like Delays

```python
from browser_manager import human_delay
import time

# Add realistic delays between actions
page.click("#button")
time.sleep(human_delay())        # 0.05 - 3.0 seconds
page.fill("#input", "text")
time.sleep(human_delay(0.5, 1.5))  # Custom range
```

## What Each Profile Gets

| Feature | Description |
|---------|-------------|
| Unique fingerprint | Canvas, WebGL, audio, fonts, screen, navigator, timezone, language |
| Persistent storage | Cookies, localStorage, sessionStorage survive restarts |
| Proxy config | Per-profile HTTP/SOCKS5 proxy routing |
| WebRTC blocking | Prevents IP leaks through WebRTC |
| Human-like behavior | Camoufox humanize mode for natural mouse/timing patterns |

## Anti-Detection Stack

1. **Camoufox** handles core anti-detection: 53+ browser parameters spoofed at the engine level (not JS injection)
2. **BrowserForge** generates statistically realistic fingerprint combinations
3. **Persistent profiles** maintain consistent identity across sessions
4. **WebRTC blocking** prevents real IP exposure
5. **Human-like delays** available for automation scripts

## Directory Structure

```
browser-manager/
  browser_manager.py      # Main CLI + Python API
  fingerprint_gen.py      # BrowserForge fingerprint generation
  test_anti_detect.py     # Test suite (39 tests)
  profiles/               # Profile storage
    campaign-1/
      profile.json        # Fingerprint + config
      user_data/          # Persistent browser data
    campaign-2/
      ...
```

## Running Tests

```bash
python -m unittest test_anti_detect -v
```

39 tests covering: fingerprint generation, uniqueness, profile CRUD, proxy parsing, CLI parsing, humanization, and integration.

## Phase 2 Ideas

- Web UI for profile management
- Proxy rotation pools
- Fingerprint scheduling (rotate every N days)
- Team sharing (export/import profiles)
- Integration with campaign automation platform
