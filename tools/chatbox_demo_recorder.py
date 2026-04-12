#!/usr/bin/env python3
"""Chatbox Demo Recorder — captures the PureBrain chatbox experience on pay-test-sandbox-2.
Enters password gate, interacts with the chatbox, captures the conversation flow."""

import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
FRAMES_DIR = "/tmp/chatbox-demo-frames"
OUTPUT_VIDEO = "/tmp/chatbox-demo.mp4"

os.makedirs(FRAMES_DIR, exist_ok=True)
for f in Path(FRAMES_DIR).glob("*.png"):
    f.unlink()


def main():
    print("Chatbox Demo Recorder")
    print(f"URL: {PAGE_URL}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        page = context.new_page()

        # Navigate to page
        print("Loading page...")
        page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        frame_num = 0

        # Enter password
        print("Entering password...")
        pwd_input = page.query_selector('input[type="password"], input[name="post_password"]')
        if pwd_input:
            pwd_input.fill(PAGE_PASSWORD)
            page.wait_for_timeout(500)

            # Click Enter/Submit button
            submit_btn = page.query_selector('input[type="submit"], button[type="submit"], button:has-text("Enter")')
            if submit_btn:
                submit_btn.click()
                print("  Password submitted, waiting for page load...")
                page.wait_for_timeout(8000)  # Wait for full page with chatbox to load
            else:
                # Try pressing Enter
                pwd_input.press("Enter")
                page.wait_for_timeout(8000)
        else:
            print("  No password input found, page may be open")
            page.wait_for_timeout(3000)

        # Capture the loaded page
        frame_num += 1
        frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_num:03d}_page_loaded.png")
        page.screenshot(path=frame_path, full_page=False, timeout=60000)
        print(f"  [{frame_num}] Page loaded after password")

        # Dump page HTML structure to find chatbox elements
        print("\nSearching for chatbox elements...")
        elements_info = page.evaluate("""
        () => {
            const results = [];
            // Look for chatbox-related elements
            const selectors = [
                '#pb-chatbox', '.pb-chatbox', '#purebrain-chat', '.purebrain-chatbox',
                '#awakening', '.awakening', '.chatbox', '#chatbox',
                '.begin-awakening', '.begin-btn', '.chat-widget',
                'iframe', '[data-chatbox]', '.tawk-min-container',
                '#pb-chat-container', '.pb-chat', '[id*="chat"]', '[class*="chat"]',
                '[id*="awaken"]', '[class*="awaken"]', '[id*="begin"]', '[class*="begin"]',
                '.elementor-widget-html', '.elementor-html'
            ];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    const rect = el.getBoundingClientRect();
                    results.push({
                        selector: sel,
                        tag: el.tagName,
                        id: el.id,
                        classes: el.className.toString().substring(0, 100),
                        visible: rect.width > 0 && rect.height > 0,
                        rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height },
                        text: el.innerText?.substring(0, 80) || ''
                    });
                });
            });
            return results;
        }
        """)

        for el in elements_info:
            if el['visible']:
                print(f"  VISIBLE: {el['selector']} #{el['id']} .{el['classes'][:50]} - '{el['text'][:40]}'")

        # Scroll through page and capture at each point
        total_height = page.evaluate("document.body.scrollHeight")
        viewport_height = 900
        scroll_points = [0, 0.25, 0.5, 0.75, 1.0]

        for pct in scroll_points:
            scroll_y = int(total_height * pct)
            page.evaluate(f"window.scrollTo(0, {scroll_y})")
            page.wait_for_timeout(1500)

            frame_num += 1
            frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_num:03d}_scroll_{int(pct*100)}.png")
            page.screenshot(path=frame_path, full_page=False, timeout=60000)
            print(f"  [{frame_num}] Scroll {int(pct*100)}% captured")

        # Look for any buttons with interesting text
        buttons_info = page.evaluate("""
        () => {
            const results = [];
            document.querySelectorAll('a, button, input[type="submit"], [role="button"]').forEach(el => {
                const text = el.innerText?.trim() || el.value || '';
                if (text.length > 0 && text.length < 100) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        results.push({
                            tag: el.tagName,
                            text: text,
                            href: el.href || '',
                            rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height }
                        });
                    }
                }
            });
            return results;
        }
        """)

        print(f"\nFound {len(buttons_info)} visible buttons/links:")
        for btn in buttons_info[:20]:
            print(f"  {btn['tag']}: '{btn['text'][:50]}' @ y={btn['rect']['top']:.0f}")

        # Full page screenshot
        frame_num += 1
        frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_num:03d}_fullpage.png")
        page.screenshot(path=frame_path, full_page=True, timeout=60000)
        print(f"  [{frame_num}] Full page captured")

        browser.close()

    print(f"\n{'=' * 60}")
    print(f"Captured {frame_num} frames")

    # Stitch non-fullpage frames into video
    frames = sorted(Path(FRAMES_DIR).glob("frame_*.png"))
    frames = [f for f in frames if 'fullpage' not in f.name]

    if len(frames) >= 2:
        concat_file = os.path.join(FRAMES_DIR, "frames.txt")
        with open(concat_file, "w") as f:
            for frame in frames:
                f.write(f"file '{frame}'\n")
                f.write(f"duration 2.5\n")
            f.write(f"file '{frames[-1]}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_file,
            "-vf", "scale=1440:900:flags=lanczos,format=yuv420p",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-r", "30", "-movflags", "+faststart",
            OUTPUT_VIDEO
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
            print(f"Video: {OUTPUT_VIDEO} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
