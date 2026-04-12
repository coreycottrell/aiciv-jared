#!/usr/bin/env python3
"""Portal Demo Recorder — captures screenshots of PureBrain portal at key navigation points.
Uses page.evaluate() for JS-based navigation to avoid element visibility issues."""

import os
import time
import subprocess
from pathlib import Path

# Playwright sync API
from playwright.sync_api import sync_playwright

PORTAL_HTML = "/home/jared/projects/AI-CIV/aether/docs/from-telegram/pure-brain-v8-aether-dashboard.html"
FRAMES_DIR = "/tmp/portal-demo-frames"
OUTPUT_VIDEO = "/tmp/portal-demo.mp4"

# Clean up old frames
os.makedirs(FRAMES_DIR, exist_ok=True)
for f in Path(FRAMES_DIR).glob("*.png"):
    f.unlink()

# Define the demo sequence: (action_js, wait_ms, filename, description)
DEMO_SEQUENCE = [
    # 1. Chat landing page
    (None, 1500, "frame_001_chat_landing", "Chat view - main landing"),

    # 2. Type a message in the chat input
    ("document.querySelector('#messageInput, .chat__input textarea, textarea').value = 'What is my AI adoption readiness score?'; document.querySelector('#messageInput, .chat__input textarea, textarea').dispatchEvent(new Event('input', {bubbles: true}))",
     1000, "frame_002_chat_typing", "Chat with typed message"),

    # 3. Show History view
    ("showHistory()", 1500, "frame_003_history", "History view"),

    # 4. Show Dashboard view
    ("showDashboard()", 2000, "frame_004_dashboard", "Dashboard / AI Command Center"),

    # 5. Back to Chat
    ("showChat()", 1000, "frame_005_chat_return", "Back to chat"),

    # 6. Open Create Brain modal
    ("openCreateBrainModal()", 1500, "frame_006_create_brain", "Create Brain modal"),

    # 7. Close Create Brain modal
    ("closeCreateBrainModal()", 800, "frame_007_brain_closed", "Brain modal closed"),

    # 8. Open Create Project modal
    ("openCreateProjectModal()", 1500, "frame_008_create_project", "Create Project modal"),

    # 9. Close Create Project modal
    ("closeCreateProjectModal()", 800, "frame_009_project_closed", "Project modal closed"),

    # 10. Open Create Task modal
    ("openCreateTaskModal()", 1500, "frame_010_create_task", "Create Task modal"),

    # 11. Close Create Task modal
    ("closeCreateTaskModal()", 800, "frame_011_task_closed", "Task modal closed"),

    # 12. Open Create Goal modal
    ("openCreateGoalModal()", 1500, "frame_012_create_goal", "Create Goal modal"),

    # 13. Close Create Goal modal
    ("closeCreateGoalModal()", 800, "frame_013_goal_closed", "Goal modal closed"),

    # 14. Open Settings modal
    ("openSettingsModal()", 1500, "frame_014_settings_appearance", "Settings - Appearance tab"),

    # 15. Settings - Personalization tab
    ("switchSettingsTab('personalization')", 1000, "frame_015_settings_personalization", "Settings - Personalization"),

    # 16. Settings - Memory tab
    ("switchSettingsTab('memory')", 1000, "frame_016_settings_memory", "Settings - Memory"),

    # 17. Settings - Model tab
    ("switchSettingsTab('model')", 1000, "frame_017_settings_model", "Settings - Model"),

    # 18. Settings - Data tab
    ("switchSettingsTab('data')", 1000, "frame_018_settings_data", "Settings - Data"),

    # 19. Settings - Shortcuts tab
    ("switchSettingsTab('shortcuts')", 1000, "frame_019_settings_shortcuts", "Settings - Shortcuts"),

    # 20. Settings - Upgrade tab
    ("switchSettingsTab('upgrade')", 1000, "frame_020_settings_upgrade", "Settings - Upgrade"),

    # 21. Close Settings
    ("closeSettingsModal()", 800, "frame_021_settings_closed", "Settings closed"),

    # 22. Open Referral overlay
    ("openReferralOverlay()", 1500, "frame_022_referral", "Referral overlay"),

    # 23. Close Referral overlay
    ("closeReferralOverlay()", 800, "frame_023_referral_closed", "Referral closed"),

    # 24. Toggle sidebar collapsed
    ("toggleSidebar()", 1000, "frame_024_sidebar_collapsed", "Sidebar collapsed"),

    # 25. Toggle sidebar back
    ("toggleSidebar()", 1000, "frame_025_sidebar_expanded", "Sidebar expanded"),

    # 26. Final dashboard view
    ("showDashboard()", 2000, "frame_026_final_dashboard", "Final dashboard view"),
]


def main():
    print(f"Portal Demo Recorder")
    print(f"HTML: {PORTAL_HTML}")
    print(f"Frames: {FRAMES_DIR}")
    print(f"Sequence: {len(DEMO_SEQUENCE)} steps")
    print("=" * 50)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,  # Retina quality
        )
        page = context.new_page()

        # Load the portal HTML
        file_url = f"file://{PORTAL_HTML}"
        print(f"Loading: {file_url}")
        page.goto(file_url, wait_until="networkidle")

        # Wait for any animations to settle
        page.wait_for_timeout(2000)

        # ---------------------------------------------------------------
        # DARK MODE: Enforce dark mode BEFORE any recording begins.
        # Jared requirement (2026-02-28): "make sure demo is in dark mode!
        # flip it on in the portal."
        #
        # How the portal's theme system works:
        #   - Dark is the DEFAULT state (no data-theme attribute = dark)
        #   - Light mode sets data-theme="light" on <html> element
        #   - setThemePreference('dark') persists to localStorage 'pb_theme'
        #     then calls applyTheme() which removes any data-theme attribute
        #   - applyTheme('dark') = document.documentElement.removeAttribute('data-theme')
        #   - applyTheme('light') = document.documentElement.setAttribute('data-theme', 'light')
        # ---------------------------------------------------------------
        print("  [DARK MODE] Enforcing dark mode before recording...")
        page.evaluate("""
            // Step 1: Set localStorage preference to 'dark'
            localStorage.setItem('pb_theme', 'dark');

            // Step 2: Call the portal's own setThemePreference if available
            // (this also updates the Settings picker UI to show Dark as active)
            if (typeof setThemePreference === 'function') {
                setThemePreference('dark');
            } else if (typeof applyTheme === 'function') {
                // Fallback: call applyTheme directly
                applyTheme('dark');
            } else {
                // Last resort: remove the light-mode attribute directly
                document.documentElement.removeAttribute('data-theme');
            }
        """)

        # Let CSS transitions settle after theme switch
        page.wait_for_timeout(600)

        # Verify dark mode is active — data-theme must NOT be 'light'
        theme_attr = page.evaluate("document.documentElement.getAttribute('data-theme')")
        if theme_attr == 'light':
            print(f"  [DARK MODE] WARNING: data-theme still 'light' after setThemePreference — forcing removal...")
            page.evaluate("document.documentElement.removeAttribute('data-theme')")
            page.wait_for_timeout(300)
            theme_attr = page.evaluate("document.documentElement.getAttribute('data-theme')")

        if theme_attr == 'light':
            print(f"  [DARK MODE] CRITICAL: Could not remove light mode. Proceeding but portal may appear light.")
        else:
            print(f"  [DARK MODE] Confirmed: data-theme='{theme_attr}' (null/absent = dark mode active)")

        frame_count = 0
        for action_js, wait_ms, filename, description in DEMO_SEQUENCE:
            print(f"  [{frame_count+1}/{len(DEMO_SEQUENCE)}] {description}...")

            # Execute JS action if provided
            if action_js:
                try:
                    page.evaluate(action_js)
                except Exception as e:
                    print(f"    WARNING: JS error: {e}")

            # Wait for animations/transitions
            page.wait_for_timeout(wait_ms)

            # Capture screenshot
            frame_path = os.path.join(FRAMES_DIR, f"{filename}.png")
            page.screenshot(path=frame_path, full_page=False)
            frame_count += 1
            print(f"    Captured: {filename}.png")

        browser.close()

    print(f"\n{'=' * 50}")
    print(f"Captured {frame_count} frames in {FRAMES_DIR}")

    # Stitch into video using FFmpeg
    # Each frame shows for 2 seconds, with smooth crossfade transitions
    print(f"\nStitching into video...")

    # Get sorted frame list
    frames = sorted(Path(FRAMES_DIR).glob("*.png"))

    if len(frames) < 2:
        print("Not enough frames for video")
        return

    # Create a concat file for FFmpeg with frame durations
    concat_file = os.path.join(FRAMES_DIR, "frames.txt")
    with open(concat_file, "w") as f:
        for frame in frames:
            f.write(f"file '{frame}'\n")
            f.write(f"duration 2\n")
        # Last frame needs to be listed again (FFmpeg quirk)
        f.write(f"file '{frames[-1]}'\n")

    # FFmpeg: concat demuxer -> smooth video
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
        "-vf", "scale=1440:900:flags=lanczos,format=yuv420p",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-r", "30",
        "-movflags", "+faststart",
        OUTPUT_VIDEO
    ]

    print(f"Running: {' '.join(cmd[:8])}...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode == 0:
        size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
        print(f"\nVideo created: {OUTPUT_VIDEO} ({size_mb:.1f} MB)")
        print(f"Duration: ~{len(frames) * 2} seconds")
    else:
        print(f"FFmpeg error: {result.stderr[-500:]}")


if __name__ == "__main__":
    main()
