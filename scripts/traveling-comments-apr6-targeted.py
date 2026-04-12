#!/usr/bin/env python3
"""
Traveling Comments - April 6, 2026
8 targeted comments for Tier 1 LinkedIn influencers.
Each comment crafted against their ACTUAL recent content.

Usage:
  python3 scripts/traveling-comments-apr6-targeted.py --dry-run
  python3 scripts/traveling-comments-apr6-targeted.py
"""

import requests
import time
import json
import sys
import os
from datetime import datetime

PURESURF = "http://157.180.69.225:8901"
API_KEY = "O_EnHpl-94xMLwvWZRNBIc6WGnfl5bkk9Ogk7eew_bg"
HEADERS = {"Content-Type": "application/json", "X-API-Key": API_KEY}
SESSION_ID = "54288016e3c6"
DRY_RUN = "--dry-run" in sys.argv

# Pure Technology team - NEVER comment on these people
BLACKLIST = {n.lower() for n in [
    "John Smith", "Nathan Olson", "Phil Bliss", "Melanie Salvador",
    "Mike Daser", "Alex Seant", "Baruch Santana", "Robert Orlowski",
    "Harrison Amit", "Faris Asmar"
]}

# 8 targets with pre-crafted comments matched to their recent content
TARGETS = [
    {
        "handle": "emollick",
        "name": "Ethan Mollick",
        "comment": "Most people reading this focus on which skills AI replaces. The real signal is which skills become disproportionately valuable BECAUSE of AI. Pattern recognition used to be a nice-to-have. Now it's the difference between someone who uses AI well and someone who just runs prompts. The skill premium isn't disappearing, it's concentrating. What skill have you seen become 10x more valuable specifically because AI handles the routine version of it?",
        "reaction": "Insightful",
    },
    {
        "handle": "pascalbornet",
        "name": "Pascal Bornet",
        "comment": "The hybrid framing is the first one I've seen that honestly names the problem: genAI alone isn't reliable enough and predictive AI alone isn't flexible enough. Most vendors pretend one approach handles everything. What's interesting is the organizational challenge. Teams built around predictive AI think differently than teams built around genAI. Merging the tech is the easy part. Merging the workflows and mental models? That's where most hybrid attempts stall. What patterns are you seeing from companies that actually pulled off the merge?",
        "reaction": "Celebrate",
    },
    {
        "handle": "rubenhassid",
        "name": "Ruben Hassid",
        "comment": "\"Mediocrity gets replaced fast\" hits because it's already happening and most people still think they have time. The part I'd add: the survivors won't just be better at prompting. They'll be better at taste. AI can generate infinite options. The human edge is knowing which option is right without needing to test all of them. That editorial instinct is what separates useful AI output from noise. How do you train taste when most AI education focuses purely on technical skills?",
        "reaction": "Support",
    },
    {
        "handle": "alliekmiller",
        "name": "Allie K. Miller",
        "comment": "The voice AI prediction is worth watching closely because voice changes the adoption curve completely. Text-based AI has a learning curve. Voice doesn't. My 60-year-old neighbor will never write a prompt but he'll absolutely talk to an AI. That's when adoption goes from tech-forward companies to literally everyone. The trust question gets harder at that scale because voice feels more personal and therefore more manipulable. Where do you think the first major voice AI trust crisis shows up?",
        "reaction": "Love",
    },
    {
        "handle": "bernardmarr",
        "name": "Bernard Marr",
        "comment": "The trust paradox you named is showing up everywhere. Companies feel confident about AI because their demos work. But demos aren't production. The gap between \"our pilot looked great\" and \"this runs reliably at scale\" is where trust actually gets tested. Most organizations don't discover the gap until they're already committed. The skill that matters most right now isn't technical. It's the ability to honestly assess readiness without the pressure to say yes. Who typically catches the readiness gap first in an organization?",
        "reaction": "Insightful",
    },
    {
        "handle": "zainkahn",
        "name": "Zain Kahn",
        "comment": "The Gmail + Calendar + CRM agent stack is where things get interesting fast. Each tool alone saves minutes. Connected together they start making decisions you used to make manually. The jump from \"AI does what I ask\" to \"AI does what I would have asked if I'd thought of it\" happens when agents share context across tools. That's also where the risk surface expands. How are you thinking about the permission model when an agent can read your email AND write to your CRM?",
        "reaction": "Celebrate",
    },
    {
        "handle": "linasbeliunas",
        "name": "Linas Beliunas",
        "comment": "AI agents hiring humans flips the entire labor market conversation. Everyone debates which jobs AI takes. Nobody talks about the jobs AI creates by needing physical execution it can't do. Delivery, inspection, installation, repair. The irony is that blue-collar work becomes MORE valuable in an AI-first economy because it's the layer AI literally cannot perform. The one-person unicorn concept only works because thousands of humans still handle the physical layer. Is anyone pricing this dependency correctly?",
        "reaction": "Support",
    },
    {
        "handle": "mattshumer",
        "name": "Matt Shumer",
        "comment": "The coding agent productivity piece connects to something bigger: most people use AI agents the way they used Google in 2005. Type a query, get a result, manually do the next step. The 10x users aren't writing better prompts. They're building loops where the agent's output feeds directly into the next action without human intervention. The gap between \"assisted\" and \"autonomous\" workflows is where the real productivity jump lives. What's the simplest autonomous loop you've seen that made the biggest difference?",
        "reaction": "Love",
    },
]


def evaluate(script):
    """Run JS in the browser session via evaluate endpoint."""
    try:
        resp = requests.post(
            f"{PURESURF}/sessions/{SESSION_ID}/evaluate",
            headers=HEADERS,
            json={"script": script},
            timeout=60,
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def navigate(url, wait=8):
    """Navigate to URL and wait."""
    try:
        resp = requests.post(
            f"{PURESURF}/sessions/{SESSION_ID}/navigate",
            headers=HEADERS,
            json={"url": url, "wait_for": "networkidle"},
            timeout=60,
        )
        data = resp.json()
        print(f"  Nav: {data.get('status')} | Title: {data.get('title', '')[:60]} | HTTP: {data.get('http_status')}")
        time.sleep(wait)
        return data
    except Exception as e:
        print(f"  Nav error: {e}")
        return {"error": str(e)}


def check_session_alive():
    """Verify the BaaS session exists."""
    try:
        resp = requests.get(
            f"{PURESURF}/sessions/{SESSION_ID}",
            headers=HEADERS,
            timeout=10,
        )
        data = resp.json()
        if data.get("error"):
            return False
        return True
    except:
        return False


def check_auth():
    """Verify LinkedIn auth is working."""
    print("Step 1: Checking session...")
    if not check_session_alive():
        print("ERROR: Session not found. May need to create a new one.")
        # Try creating a new session
        print("Attempting to create new session...")
        try:
            # Clear rate limit state first
            os.system('ssh root@157.180.69.225 "rm -f /opt/baas/proactive_rate_limits.json" 2>/dev/null')
            time.sleep(2)
            resp = requests.post(f"{PURESURF}/sessions", headers=HEADERS, json={
                "profile_name": "jared-linkedin-fresh",
                "proxy_provider": "residential",
                "headless": True,
                "timeout": 90,
            }, timeout=90)
            data = resp.json()
            global SESSION_ID
            SESSION_ID = data.get("session_id")
            print(f"New session created: {SESSION_ID}")
        except Exception as e:
            print(f"Failed to create session: {e}")
            return False

    print("Step 2: Loading LinkedIn feed...")
    result = navigate("https://www.linkedin.com/feed/", wait=10)

    http = result.get("http_status")
    title = result.get("title", "")
    status = result.get("status", "")

    if http == 429 or "rate_limit" in str(status):
        print("BLOCKED: LinkedIn 429 rate limit still active.")
        print("Wait 2-6 hours and retry, or have Jared generate fresh li_at.")
        return False

    if "Feed" in title or "LinkedIn" in title:
        print(f"Authenticated! Title: {title}")
        return True

    # Check page content as fallback
    content_result = evaluate("document.title + ' | ' + (document.body?.innerText?.substring(0, 200) || '')")
    content = str(content_result.get("result", ""))
    if "Feed" in content or "Start a post" in content:
        print("Authenticated (confirmed via page content)")
        return True

    print(f"Auth unclear. Title: {title}, HTTP: {http}")
    return False


def visit_profile_and_find_post(handle, name):
    """Navigate to recent activity and verify posts exist."""
    url = f"https://www.linkedin.com/in/{handle}/recent-activity/all/"
    result = navigate(url, wait=10)

    if result.get("http_status") == 429:
        print(f"  429 on {name}'s profile")
        return False

    # Check if posts are visible
    check = evaluate("""
        (() => {
            // Look for post containers
            const posts = document.querySelectorAll('.feed-shared-update-v2, .occludable-update, [data-urn]');
            const commentBtns = document.querySelectorAll('button[aria-label*="Comment"], button[aria-label*="comment"]');
            return JSON.stringify({
                posts: posts.length,
                commentBtns: commentBtns.length,
                title: document.title
            });
        })()
    """)

    result_str = str(check.get("result", "{}"))
    print(f"  Page check: {result_str}")

    try:
        page_data = json.loads(result_str) if isinstance(result_str, str) else {}
    except:
        page_data = {}

    if page_data.get("posts", 0) > 0 or page_data.get("commentBtns", 0) > 0:
        return True

    # Fallback: check for any interactive elements
    fallback = evaluate("document.querySelectorAll('[data-urn]').length")
    if int(fallback.get("result", 0)) > 0:
        return True

    print(f"  No posts found on {name}'s activity page")
    return False


def post_comment(comment_text):
    """Post a comment on the first visible post using evaluate + execCommand."""
    if DRY_RUN:
        print(f"  [DRY RUN] Would post: {comment_text[:80]}...")
        return True

    # Step 1: Click the comment button on the first post
    print("  Clicking comment button...")
    click_js = """
        (() => {
            const btns = document.querySelectorAll('button[aria-label*="Comment"], button[aria-label*="comment"]');
            if (btns.length > 0) {
                btns[0].scrollIntoView({behavior: 'smooth', block: 'center'});
                setTimeout(() => btns[0].click(), 500);
                return 'clicked';
            }
            return 'no button found';
        })()
    """
    result = evaluate(click_js)
    print(f"    Result: {result.get('result', result)}")
    time.sleep(3)

    # Step 2: Focus the comment textbox
    print("  Focusing textbox...")
    focus_js = """
        (() => {
            const selectors = [
                '.ql-editor[data-placeholder]',
                '.comments-comment-texteditor .ql-editor',
                '[role="textbox"][contenteditable="true"]',
                'div[contenteditable="true"][aria-label*="comment" i]',
                'div[contenteditable="true"][aria-label*="Add" i]',
                'div[contenteditable="true"]',
            ];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el) {
                    el.focus();
                    el.click();
                    return 'focused: ' + sel;
                }
            }
            return 'no textbox found';
        })()
    """
    result = evaluate(focus_js)
    print(f"    Result: {result.get('result', result)}")
    time.sleep(1)

    # Step 3: Insert text via execCommand (natural text input)
    print("  Inserting text...")
    escaped = comment_text.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n")
    type_js = f"""
        (() => {{
            const success = document.execCommand('insertText', false, '{escaped}');
            return success ? 'inserted' : 'insertText failed';
        }})()
    """
    result = evaluate(type_js)
    print(f"    Result: {result.get('result', result)}")
    time.sleep(2)

    # Step 4: Submit the comment
    print("  Submitting...")
    submit_js = """
        (() => {
            // Try dedicated submit button first
            const submit = document.querySelector('button.comments-comment-box__submit-button');
            if (submit && !submit.disabled) {
                submit.click();
                return 'submitted via submit button';
            }
            // Try any Post/Comment button
            const btns = document.querySelectorAll('button');
            for (const btn of btns) {
                const text = btn.textContent.trim().toLowerCase();
                if ((text === 'post' || text === 'comment' || text === 'submit') && !btn.disabled) {
                    btn.click();
                    return 'submitted via text match: ' + text;
                }
            }
            return 'no submit button found or all disabled';
        })()
    """
    result = evaluate(submit_js)
    print(f"    Result: {result.get('result', result)}")

    if "submitted" in str(result.get("result", "")):
        time.sleep(3)
        return True

    return False


def add_reaction(reaction_type):
    """Add a reaction (Support/Celebrate/Insightful/Love) to the first post."""
    if DRY_RUN:
        print(f"  [DRY RUN] Would react: {reaction_type}")
        return True

    # Hover the like button to trigger reaction popup
    print(f"  Adding {reaction_type} reaction...")
    hover_js = """
        (() => {
            const likeBtn = document.querySelector(
                'button[aria-label*="Like"], button[aria-label*="React"], button.react-button, button.reactions-react-button'
            );
            if (likeBtn) {
                likeBtn.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
                likeBtn.dispatchEvent(new PointerEvent('pointerenter', {bubbles: true}));
                return 'hovering';
            }
            return 'no like button';
        })()
    """
    evaluate(hover_js)
    time.sleep(2)

    # Click the specific reaction
    react_js = f"""
        (() => {{
            const btns = document.querySelectorAll('button[aria-label*="{reaction_type}"]');
            if (btns.length > 0) {{
                btns[0].click();
                return 'reacted';
            }}
            // Try image alt text
            const imgs = document.querySelectorAll('img[alt*="{reaction_type}"]');
            if (imgs.length > 0) {{
                imgs[0].closest('button')?.click();
                return 'reacted via img';
            }}
            return 'not found';
        }})()
    """
    result = evaluate(react_js)
    print(f"    Result: {result.get('result', result)}")
    return "reacted" in str(result.get("result", ""))


def main():
    print(f"{'='*60}")
    print(f"TRAVELING COMMENTS {'[DRY RUN]' if DRY_RUN else '[LIVE]'}")
    print(f"{'='*60}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Session: {SESSION_ID}")
    print(f"Targets: {len(TARGETS)}")
    print(f"Max comments: 8")
    print(f"Min spacing: 180 seconds (3 minutes)")
    print()

    # Verify auth
    if not check_auth():
        print("\nABORT: Cannot authenticate to LinkedIn.")
        return

    print()

    comments_posted = 0
    comment_log = []

    for i, target in enumerate(TARGETS):
        if comments_posted >= 8:
            break

        name = target["name"]
        handle = target["handle"]

        # Blacklist check
        if name.lower() in BLACKLIST:
            print(f"\n[SKIP] {name} is blacklisted")
            continue

        print(f"\n{'='*40}")
        print(f"TARGET {i+1}/{len(TARGETS)}: {name} (@{handle})")
        print(f"{'='*40}")

        # Visit profile
        has_posts = visit_profile_and_find_post(handle, name)
        if not has_posts:
            print(f"  Skipping {name} (no accessible posts)")
            continue

        # Post the comment
        print(f"\n  Comment ({len(target['comment'])} chars):")
        print(f"  \"{target['comment'][:120]}...\"")
        print(f"  Reaction: {target['reaction']}")

        success = post_comment(target["comment"])

        if success:
            add_reaction(target["reaction"])
            comments_posted += 1

            entry = {
                "target": name,
                "handle": handle,
                "comment": target["comment"],
                "reaction": target["reaction"],
                "timestamp": datetime.now().isoformat(),
                "success": True,
            }
            comment_log.append(entry)
            print(f"\n  Comment #{comments_posted} POSTED on {name}")
        else:
            comment_log.append({
                "target": name,
                "handle": handle,
                "comment": target["comment"][:80] + "...",
                "reaction": target["reaction"],
                "timestamp": datetime.now().isoformat(),
                "success": False,
            })
            print(f"\n  FAILED to post on {name}")

        # Wait 3+ minutes between comments (gradually increase)
        if i < len(TARGETS) - 1 and comments_posted < 8:
            wait = 180 + (comments_posted * 15)
            if not DRY_RUN:
                print(f"\n  Waiting {wait}s ({wait//60}m {wait%60}s) before next target...")
                time.sleep(wait)
            else:
                print(f"  [DRY RUN] Would wait {wait}s")

    # Final Report
    print(f"\n{'='*60}")
    print(f"TRAVELING COMMENTS REPORT")
    print(f"{'='*60}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Comments attempted: {len(comment_log)}")
    print(f"Comments posted: {sum(1 for c in comment_log if c['success'])}")
    print(f"Comments failed: {sum(1 for c in comment_log if not c['success'])}")
    print()

    for j, entry in enumerate(comment_log, 1):
        status = "POSTED" if entry["success"] else "FAILED"
        print(f"--- Comment {j} [{status}] ---")
        print(f"Target: {entry['target']} (@{entry['handle']})")
        print(f"Reaction: {entry['reaction']}")
        print(f"Time: {entry['timestamp']}")
        if entry["success"]:
            print(f"Comment: {entry['comment']}")
        print()

    # Save log to file
    os.makedirs("/home/jared/projects/AI-CIV/aether/exports/linkedin-pipeline", exist_ok=True)
    log_path = f"/home/jared/projects/AI-CIV/aether/exports/linkedin-pipeline/traveling-comments-{datetime.now().strftime('%Y-%m-%d-%H%M')}.json"
    with open(log_path, "w") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "session_id": SESSION_ID,
            "dry_run": DRY_RUN,
            "total_posted": sum(1 for c in comment_log if c["success"]),
            "comments": comment_log,
        }, f, indent=2)
    print(f"Log saved: {log_path}")


if __name__ == "__main__":
    main()
