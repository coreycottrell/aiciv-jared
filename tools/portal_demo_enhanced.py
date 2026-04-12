#!/usr/bin/env python3
"""Enhanced Portal Demo Recorder — simulates real chat interactions + captures all features.
Injects messages directly into DOM to simulate a realistic conversation."""

import os
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

PORTAL_HTML = "/home/jared/projects/AI-CIV/aether/docs/from-telegram/pure-brain-v8-aether-dashboard.html"
FRAMES_DIR = "/tmp/portal-demo-enhanced"
OUTPUT_VIDEO = "/tmp/portal-demo-enhanced.mp4"

os.makedirs(FRAMES_DIR, exist_ok=True)
for f in Path(FRAMES_DIR).glob("*.png"):
    f.unlink()

# Simulated conversation messages
CHAT_CONVERSATION = [
    ("user", "What's my AI adoption readiness score based on our current setup?"),
    ("assistant", """Based on your current setup, I'd place your organization at a **7.2/10** AI Adoption Readiness Score. Here's the breakdown:

**Strengths (scoring high):**
- ✅ Active AI integration across 3+ departments
- ✅ Persistent memory system in place (your sessions compound)
- ✅ Executive sponsorship — you're personally driving adoption

**Growth areas:**
- ⚠️ Team-wide AI literacy varies significantly
- ⚠️ No formal AI governance framework yet
- ⚠️ Data pipeline automation at ~40% capacity

**Recommendation:** Focus on closing the competence gap in your mid-tier performers. Your top people are already compounding — the risk is in the middle layer coasting on surface-level AI usage.

Want me to build a detailed action plan for the next 90 days?"""),
    ("user", "Yes, build the 90-day plan. Also, what's the ROI projection if we close that gap?"),
    ("assistant", """**90-Day AI Acceleration Plan**

**Days 1-30: Foundation**
- Deploy AI usage analytics across all teams
- Identify your top 5 "AI power users" and your bottom 5
- Establish weekly AI strategy reviews (not just tool usage metrics)

**Days 31-60: Intervention**
- Pair top performers with mid-tier in AI mentorship pods
- Implement "question quality" evaluation in performance reviews
- Launch persistent AI relationships for each department head

**Days 61-90: Compound**
- Measure strategic output improvement (not just speed)
- Build department-specific AI playbooks from power user patterns
- ROI checkpoint and recalibration

**Projected ROI:**
Conservative estimate: **23-31% productivity gain** in strategic output by Day 90, with the competence gap narrowing by ~40%. The real multiplier comes in months 4-6 when the compounding effect kicks in.

Shall I create a goal to track this plan?"""),
]

# Demo sequence: (action_type, action_data, wait_ms, filename, description)
DEMO_SEQUENCE = [
    # === CHAT INTERACTION SEQUENCE ===
    ("wait", None, 1500, "frame_001_landing", "Clean chat landing"),

    # Type first message
    ("type_message", CHAT_CONVERSATION[0][1], 800, "frame_002_typing", "User typing question"),
    ("send_and_reply", CHAT_CONVERSATION[1][1], 2500, "frame_003_ai_response_1", "AI responds with readiness score"),
    ("scroll_down", None, 1000, "frame_004_ai_response_1_full", "Full AI response visible"),

    # Type second message
    ("type_message", CHAT_CONVERSATION[2][1], 800, "frame_005_typing_2", "User asks for 90-day plan"),
    ("send_and_reply", CHAT_CONVERSATION[3][1], 2500, "frame_006_ai_response_2", "AI delivers 90-day plan"),
    ("scroll_down", None, 1000, "frame_007_ai_response_2_full", "Full plan + ROI visible"),

    # === NAVIGATION SEQUENCE ===
    ("js", "showHistory()", 1500, "frame_008_history", "History view with conversations"),
    ("js", "showDashboard()", 2000, "frame_009_dashboard", "AI Command Center"),

    # === MODAL SEQUENCE ===
    ("js", "showChat()", 800, None, None),  # Return to chat (no capture)
    ("js", "openCreateBrainModal()", 1500, "frame_010_create_brain", "Create Brain modal"),
    ("js", "closeCreateBrainModal()", 500, None, None),

    ("js", "openCreateProjectModal()", 1500, "frame_011_create_project", "Create Project modal"),
    ("js", "closeCreateProjectModal()", 500, None, None),

    ("js", "openCreateTaskModal()", 1500, "frame_012_create_task", "Create Task modal"),
    ("js", "closeCreateTaskModal()", 500, None, None),

    ("js", "openCreateGoalModal()", 1500, "frame_013_create_goal", "Create Goal modal"),
    ("js", "closeCreateGoalModal()", 500, None, None),

    # === SETTINGS SEQUENCE ===
    ("js", "openSettingsModal()", 1200, "frame_014_settings", "Settings - Appearance"),
    ("js", "switchSettingsTab('personalization')", 800, "frame_015_personalization", "Settings - Personalization"),
    ("js", "switchSettingsTab('memory')", 800, "frame_016_memory", "Settings - Memory"),
    ("js", "switchSettingsTab('model')", 800, "frame_017_model", "Settings - Model"),
    ("js", "switchSettingsTab('data')", 800, "frame_018_data", "Settings - Data Controls"),
    ("js", "switchSettingsTab('shortcuts')", 800, "frame_019_shortcuts", "Settings - Shortcuts"),
    ("js", "switchSettingsTab('upgrade')", 800, "frame_020_upgrade", "Settings - Upgrade Plan"),
    ("js", "closeSettingsModal()", 500, None, None),

    # === REFERRAL + SIDEBAR ===
    ("js", "openReferralOverlay()", 1500, "frame_021_referral", "Refer & Earn overlay"),
    ("js", "closeReferralOverlay()", 500, None, None),

    ("js", "toggleSidebar()", 1000, "frame_022_collapsed", "Sidebar collapsed view"),
    ("js", "toggleSidebar()", 800, None, None),

    # === FINAL SHOT ===
    ("js", "showDashboard()", 2000, "frame_023_final_dashboard", "Final dashboard shot"),
]


def inject_user_message(page, text):
    """Inject a user message into the chat DOM."""
    page.evaluate(f"""
    (() => {{
        // Remove welcome hero if present
        const hero = document.getElementById('welcomeHero');
        if (hero) hero.remove();

        const msgHtml = `
        <div class="message message--user" style="animation: messageSlideIn 0.3s ease-out;">
            <div class="message__content">
                <div class="message__bubble message__bubble--user">
                    <div class="message__text">{text}</div>
                </div>
                <div class="message__time">${{new Date().toLocaleTimeString([], {{hour:'2-digit', minute:'2-digit'}})}}</div>
            </div>
            <div class="message__avatar message__avatar--user">
                <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;font-size:12px;color:#fff;font-weight:600;">JS</div>
            </div>
        </div>`;

        const container = document.getElementById('chatMessages') || document.querySelector('.chat__messages');
        if (container) {{
            container.insertAdjacentHTML('beforeend', msgHtml);
            container.scrollTop = container.scrollHeight;
        }}
    }})()
    """)


def inject_ai_message(page, text):
    """Inject an AI response into the chat DOM with markdown-like formatting."""
    # Escape backticks and convert markdown bold to HTML
    safe_text = text.replace('`', '\\`').replace('\n', '<br>')
    safe_text = safe_text.replace('**', '<strong>', 1)
    # Convert all remaining ** pairs
    import re
    def bold_replace(match):
        return f'<strong>{match.group(1)}</strong>'
    safe_text = re.sub(r'\*\*(.+?)\*\*', bold_replace, text.replace('\n', '<br>'))

    page.evaluate(f"""
    (() => {{
        const msgHtml = `
        <div class="message message--assistant" style="animation: messageSlideIn 0.3s ease-out;">
            <div class="message__avatar">
                <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#2a93c1,#f1420b);display:flex;align-items:center;justify-content:center;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l2 2"/></svg>
                </div>
            </div>
            <div class="message__content">
                <div class="message__bubble message__bubble--assistant">
                    <div class="message__text">{safe_text}</div>
                </div>
                <div class="message__time">${{new Date().toLocaleTimeString([], {{hour:'2-digit', minute:'2-digit'}})}}</div>
            </div>
        </div>`;

        const container = document.getElementById('chatMessages') || document.querySelector('.chat__messages');
        if (container) {{
            container.insertAdjacentHTML('beforeend', msgHtml);
            container.scrollTop = container.scrollHeight;
        }}
    }})()
    """)


def main():
    print(f"Enhanced Portal Demo Recorder")
    print(f"HTML: {PORTAL_HTML}")
    print(f"Frames: {FRAMES_DIR}")
    print(f"Steps: {len(DEMO_SEQUENCE)}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        page = context.new_page()

        file_url = f"file://{PORTAL_HTML}"
        print(f"Loading: {file_url}")
        page.goto(file_url, wait_until="networkidle")
        page.wait_for_timeout(2000)

        frame_count = 0
        for action_type, action_data, wait_ms, filename, description in DEMO_SEQUENCE:
            if description:
                print(f"  [{frame_count+1}] {description}...")

            if action_type == "wait":
                pass  # Just wait and capture

            elif action_type == "type_message":
                # Show text appearing in the input field
                page.evaluate(f"""
                    document.getElementById('messageInput').value = `{action_data}`;
                    document.getElementById('messageInput').dispatchEvent(new Event('input', {{bubbles: true}}));
                """)

            elif action_type == "send_and_reply":
                # First, "send" the previous typed message (move it to chat)
                typed = page.evaluate("document.getElementById('messageInput').value")
                if typed:
                    inject_user_message(page, typed)
                    page.evaluate("document.getElementById('messageInput').value = '';")
                    page.wait_for_timeout(500)

                    # Show thinking indicator briefly
                    page.evaluate("""
                        const status = document.getElementById('aiStatus');
                        if (status) status.textContent = 'Thinking...';
                    """)
                    page.wait_for_timeout(1200)

                    # Inject AI response
                    page.evaluate("""
                        const status = document.getElementById('aiStatus');
                        if (status) status.textContent = 'Online · Ready to assist';
                    """)

                inject_ai_message(page, action_data)

            elif action_type == "scroll_down":
                page.evaluate("""
                    const container = document.getElementById('chatMessages') || document.querySelector('.chat__messages');
                    if (container) container.scrollTop = container.scrollHeight;
                """)

            elif action_type == "js":
                try:
                    page.evaluate(action_data)
                except Exception as e:
                    print(f"    WARNING: JS error: {e}")

            page.wait_for_timeout(wait_ms)

            # Capture screenshot if filename provided
            if filename:
                frame_path = os.path.join(FRAMES_DIR, f"{filename}.png")
                page.screenshot(path=frame_path, full_page=False)
                frame_count += 1
                print(f"    Captured: {filename}.png")

        browser.close()

    print(f"\n{'=' * 60}")
    print(f"Captured {frame_count} frames")

    # Stitch into video
    print(f"\nStitching video...")
    frames = sorted(Path(FRAMES_DIR).glob("*.png"))

    if len(frames) < 2:
        print("Not enough frames")
        return

    # Create concat file — chat frames get longer display, nav frames shorter
    concat_file = os.path.join(FRAMES_DIR, "frames.txt")
    with open(concat_file, "w") as f:
        for frame in frames:
            fname = frame.name
            # Chat interaction frames get 3 seconds, nav frames get 1.5 seconds
            if "response" in fname or "typing" in fname or "landing" in fname or "full" in fname:
                duration = 3.0
            elif "dashboard" in fname or "referral" in fname or "brain" in fname:
                duration = 2.0
            else:
                duration = 1.5
            f.write(f"file '{frame}'\n")
            f.write(f"duration {duration}\n")
        f.write(f"file '{frames[-1]}'\n")

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

    print(f"Running FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode == 0:
        size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
        total_duration = sum(3.0 if "response" in f.name or "typing" in f.name or "landing" in f.name or "full" in f.name
                           else 2.0 if "dashboard" in f.name or "referral" in f.name or "brain" in f.name
                           else 1.5 for f in frames)
        print(f"\nVideo: {OUTPUT_VIDEO} ({size_mb:.1f} MB, ~{total_duration:.0f}s)")
    else:
        print(f"FFmpeg error: {result.stderr[-500:]}")


if __name__ == "__main__":
    main()
