#!/usr/bin/env python3
"""
Traveling Comments Execution - April 6, 2026
Uses existing BaaS session. Targets Tier 1 LinkedIn influencers.
3-part framework: Pattern + Missing Layer + Smart Question.

Usage:
  python3 scripts/execute-traveling-comments-apr6-v2.py --dry-run
  python3 scripts/execute-traveling-comments-apr6-v2.py
"""

import requests
import time
import json
import sys
from datetime import datetime

PURESURF = "http://157.180.69.225:8901"
API_KEY = "O_EnHpl-94xMLwvWZRNBIc6WGnfl5bkk9Ogk7eew_bg"
HEADERS = {"Content-Type": "application/json", "X-API-Key": API_KEY}
SESSION_ID = "54288016e3c6"
DRY_RUN = "--dry-run" in sys.argv

# Pure Technology team - NEVER comment on these people
BLACKLIST = [
    "john smith", "nathan olson", "phil bliss", "melanie salvador",
    "mike daser", "alex seant", "baruch santana", "robert orlowski",
    "harrison amit", "faris asmar"
]

# Tier 1 targets with LinkedIn handles
TARGETS = [
    {"handle": "emollick", "name": "Ethan Mollick", "tier": 1},
    {"handle": "pascalbornet", "name": "Pascal Bornet", "tier": 1},
    {"handle": "rubenhassid", "name": "Ruben Hassid", "tier": 1},
    {"handle": "alliekmiller", "name": "Allie K. Miller", "tier": 1},
    {"handle": "bernardmarr", "name": "Bernard Marr", "tier": 1},
    {"handle": "zaabornet", "name": "Zain Kahn", "tier": 1},
    {"handle": "linasbeliunas", "name": "Linas Beliunas", "tier": 1},
    {"handle": "mattshumer", "name": "Matt Shumer", "tier": 1},
]

# Reaction rotation (NEVER "Like")
REACTIONS = ["Support", "Celebrate", "Insightful", "Love"]

def evaluate(script):
    """Run JS in the browser session."""
    resp = requests.post(
        f"{PURESURF}/sessions/{SESSION_ID}/evaluate",
        headers=HEADERS,
        json={"script": script},
        timeout=60,
    )
    return resp.json()

def navigate(url, wait=8):
    """Navigate to URL."""
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

def get_page_text():
    """Get visible text from page."""
    result = evaluate("document.body?.innerText?.substring(0, 5000) || ''")
    return result.get("result", "") if isinstance(result, dict) else str(result)

def check_auth():
    """Verify LinkedIn auth is working."""
    print("Checking authentication...")
    result = navigate("https://www.linkedin.com/feed/", wait=10)

    title = result.get("title", "")
    http = result.get("http_status")

    if http == 429:
        print("BLOCKED: LinkedIn 429 rate limit still active. Abort.")
        return False

    if "Feed" in title or "LinkedIn" in title:
        print(f"Authenticated! Title: {title}")
        return True

    print(f"Auth unclear. Title: {title}, HTTP: {http}")
    # Try checking for feed content
    text = get_page_text()
    if "Start a post" in text or "News" in text:
        print("Feed content detected - authenticated.")
        return True

    print("NOT authenticated. Cannot proceed.")
    return False

def find_recent_post(handle, name):
    """Navigate to profile activity and find a recent post. Returns post text excerpt or None."""
    print(f"\n  Visiting {name} ({handle})...")
    result = navigate(f"https://www.linkedin.com/in/{handle}/recent-activity/all/", wait=10)

    if result.get("http_status") == 429:
        print(f"  429 on {name}'s profile. Skipping.")
        return None

    # Get page content to find posts
    text = get_page_text()

    if not text or len(text) < 100:
        print(f"  No content loaded for {name}")
        return None

    # Check for actual posts (not just profile header)
    if "No posts" in text or "hasn't posted" in text:
        print(f"  {name} has no recent posts")
        return None

    # Return first ~500 chars of page text for comment crafting context
    print(f"  Found activity page ({len(text)} chars)")
    return text[:2000]

def craft_comment(post_context, target_name):
    """
    Craft a traveling comment based on the post context.
    Returns a dict with comment text and reaction.

    Since we can't use an LLM here, we have pre-crafted comments
    matched to common AI thought leader topics.
    """
    ctx = post_context.lower()

    # Match comment to topic based on keywords in post
    if any(w in ctx for w in ["agent", "autonomous", "agentic", "multi-agent"]):
        return {
            "text": "The part that gets overlooked in every agent conversation: the agent isn't the product. The orchestration layer is. Most teams build impressive individual agents but treat coordination as an afterthought. The ones shipping real value figured out that agent-to-agent communication patterns matter more than any single agent's capability. Curious if you're seeing the same split between 'cool demo' agents and 'actually deployed' agents?",
            "reaction": "Insightful"
        }

    if any(w in ctx for w in ["regulation", "governance", "policy", "compliance", "law"]):
        return {
            "text": "The tension nobody names: regulation moves in quarters, AI moves in weeks. By the time a policy framework gets ratified, the technology it targets has already evolved twice. The real governance gap isn't policy, it's institutional clock speed. Companies that build internal governance faster than external regulation arrives are the ones avoiding headlines. What's the fastest you've seen an org adapt policy to match a model update?",
            "reaction": "Support"
        }

    if any(w in ctx for w in ["productivity", "efficiency", "workflow", "automat"]):
        return {
            "text": "Here's what most productivity conversations miss: the bottleneck was never speed. It was decision quality. AI can process faster but if you're automating bad decisions you just fail faster. The teams getting real ROI aren't asking 'how do we do this faster' but 'should we be doing this at all.' Removing unnecessary work beats accelerating existing work every time. What's the biggest 'we just stopped doing that entirely' win you've seen?",
            "reaction": "Celebrate"
        }

    if any(w in ctx for w in ["hiring", "talent", "recruit", "job", "career", "layoff"]):
        return {
            "text": "Most people read this as a hiring story. I read it as a skills gap story. The roles that disappear aren't the ones AI replaces directly, they're the ones that can't articulate what humans uniquely contribute. The professionals who thrive aren't fighting AI adoption, they're redefining their value around judgment, relationships, and context that no model captures. Have you seen specific roles reinvent themselves successfully rather than resist?",
            "reaction": "Insightful"
        }

    if any(w in ctx for w in ["open source", "model", "llm", "gpt", "claude", "gemini", "ai model"]):
        return {
            "text": "The model conversation is a distraction from the real unlock: what you build around the model. Switching from GPT to Claude to Gemini changes maybe 15% of the outcome. The orchestration, memory, tools, and human-in-the-loop design around it? That's 85% of the value. The teams obsessing over which model to use are optimizing the wrong variable. What's the most impactful 'wrapper' layer you've seen transform a mediocre model into a great product?",
            "reaction": "Love"
        }

    if any(w in ctx for w in ["startup", "founder", "build", "ship", "launch", "funding"]):
        return {
            "text": "Something I keep noticing with AI startups: the ones that survive aren't the ones with the best technology. They're the ones who picked a painfully specific problem and refused to generalize too early. Every dead AI startup I've studied tried to be a platform before they earned the right. The survivors? They owned one workflow completely before expanding. Is there a pattern in what separates the 'horizontal too early' failures from the 'vertical first' winners you've seen?",
            "reaction": "Celebrate"
        }

    if any(w in ctx for w in ["data", "privacy", "security", "breach", "leak"]):
        return {
            "text": "The real vulnerability isn't the breach itself, it's the gap between what companies say their AI can access and what it actually touches. Most security teams audit the front door while the AI has already been given keys to every room. The organizations getting this right treat AI access like a separate threat surface, not an extension of existing user permissions. What's the first thing you'd audit in a company that just deployed an AI agent with database access?",
            "reaction": "Insightful"
        }

    if any(w in ctx for w in ["leadership", "ceo", "management", "culture", "team"]):
        return {
            "text": "The leadership gap AI exposes isn't technical, it's philosophical. Leaders who see AI as a cost-cutting tool get cost cuts. Leaders who see it as a capability multiplier get compounding advantages. The difference shows up in how they deploy it: replacing humans vs amplifying them. Two years from now the gap between these two approaches will be enormous. Are you seeing leadership teams actually shift from the replacement mindset to the amplification one, or is it still mostly lip service?",
            "reaction": "Support"
        }

    # Default for general AI content
    return {
        "text": "This hits on something I keep thinking about: the gap between AI awareness and AI integration is where most organizations stall. Everyone knows AI matters. Very few have changed a single workflow because of it. The companies pulling ahead aren't the ones with the biggest AI budget, they're the ones who picked one process, rebuilt it around AI, and proved the ROI before scaling. What's the smallest possible AI win you've seen create the biggest organizational shift?",
        "reaction": "Celebrate"
    }

def post_comment_via_evaluate(comment_text):
    """Post a comment using evaluate + execCommand for natural text input."""
    if DRY_RUN:
        print(f"  [DRY RUN] Would post: {comment_text[:80]}...")
        return True

    # Step 1: Find and click the comment button on the first post
    click_result = evaluate("""
        (() => {
            // Find comment buttons
            const btns = document.querySelectorAll('button[aria-label*="Comment"], button[aria-label*="comment"]');
            if (btns.length > 0) {
                btns[0].click();
                return 'clicked comment button';
            }
            return 'no comment button found';
        })()
    """)
    print(f"  Comment button: {click_result}")
    time.sleep(3)

    # Step 2: Find the comment text box and focus it
    focus_result = evaluate("""
        (() => {
            // Try various selectors for the comment input
            const selectors = [
                '.ql-editor[data-placeholder]',
                '.comments-comment-texteditor .ql-editor',
                '[role="textbox"][contenteditable="true"]',
                '.editor-content[contenteditable="true"]',
                'div[contenteditable="true"][aria-label*="comment" i]',
                'div[contenteditable="true"][aria-label*="Add" i]',
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
    """)
    print(f"  Focus: {focus_result}")
    time.sleep(1)

    # Step 3: Type using execCommand('insertText') for natural input
    escaped_text = comment_text.replace("'", "\\'").replace("\n", "\\n")
    type_result = evaluate(f"""
        (() => {{
            document.execCommand('insertText', false, '{escaped_text}');
            return 'text inserted';
        }})()
    """)
    print(f"  Type: {type_result}")
    time.sleep(2)

    # Step 4: Click submit button
    submit_result = evaluate("""
        (() => {
            const btns = document.querySelectorAll('button.comments-comment-box__submit-button, button[type="submit"]');
            for (const btn of btns) {
                if (!btn.disabled) {
                    btn.click();
                    return 'submitted';
                }
            }
            // Try finding by text
            const allBtns = document.querySelectorAll('button');
            for (const btn of allBtns) {
                if (btn.textContent.trim() === 'Post' || btn.textContent.trim() === 'Comment') {
                    if (!btn.disabled) {
                        btn.click();
                        return 'submitted via text match';
                    }
                }
            }
            return 'no submit button found';
        })()
    """)
    print(f"  Submit: {submit_result}")

    if "submitted" in str(submit_result):
        time.sleep(3)
        return True

    return False

def add_reaction(reaction_type):
    """Add a non-Like reaction to the first post."""
    if DRY_RUN:
        print(f"  [DRY RUN] Would react: {reaction_type}")
        return True

    # Step 1: Hover/long-press the like button to show reaction menu
    hover_result = evaluate("""
        (() => {
            const likeBtn = document.querySelector('button[aria-label*="Like"], button[aria-label*="React"]');
            if (likeBtn) {
                // Dispatch mouseenter + pointerenter to trigger reaction popup
                likeBtn.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
                likeBtn.dispatchEvent(new PointerEvent('pointerenter', {bubbles: true}));
                return 'hovering like button';
            }
            return 'no like button found';
        })()
    """)
    print(f"  Hover: {hover_result}")
    time.sleep(2)

    # Step 2: Click the specific reaction
    react_result = evaluate(f"""
        (() => {{
            const reaction = document.querySelector('button[aria-label*="{reaction_type}"]');
            if (reaction) {{
                reaction.click();
                return 'reacted: {reaction_type}';
            }}
            return 'reaction button not found for {reaction_type}';
        }})()
    """)
    print(f"  React: {react_result}")
    time.sleep(1)

    return "reacted" in str(react_result)

def main():
    print(f"=== Traveling Comments {'[DRY RUN]' if DRY_RUN else '[LIVE]'} ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Session: {SESSION_ID}")
    print(f"Max comments: 8")
    print(f"Min spacing: 180 seconds")
    print()

    # Step 1: Verify auth
    if not check_auth():
        print("\nABORT: Authentication failed.")
        return

    comments_posted = 0
    max_comments = 8
    comment_log = []
    persons_commented = {}  # track per-person count

    reaction_idx = 0

    for target in TARGETS:
        if comments_posted >= max_comments:
            break

        name = target["name"]
        handle = target["handle"]

        # Check blacklist
        if name.lower() in BLACKLIST:
            print(f"\nSKIP: {name} is on blacklist")
            continue

        # Check per-person limit (max 2)
        if persons_commented.get(name, 0) >= 2:
            print(f"\nSKIP: Already commented on {name} 2x today")
            continue

        # Find recent post
        post_context = find_recent_post(handle, name)
        if not post_context:
            continue

        # Craft comment based on post context
        comment_data = craft_comment(post_context, name)
        reaction = REACTIONS[reaction_idx % len(REACTIONS)]
        reaction_idx += 1

        print(f"\n  --- Posting comment on {name}'s post ---")
        print(f"  Comment: {comment_data['text'][:100]}...")
        print(f"  Reaction: {reaction}")

        # Post the comment
        success = post_comment_via_evaluate(comment_data["text"])

        if success:
            # Add reaction
            add_reaction(reaction)

            comments_posted += 1
            persons_commented[name] = persons_commented.get(name, 0) + 1

            comment_log.append({
                "target": name,
                "handle": handle,
                "comment": comment_data["text"],
                "reaction": reaction,
                "timestamp": datetime.now().isoformat(),
            })

            print(f"\n  SUCCESS: Comment #{comments_posted} on {name}")
        else:
            print(f"\n  FAILED: Could not post comment on {name}")

        # Wait 3+ minutes between comments
        if comments_posted < max_comments and target != TARGETS[-1]:
            wait_seconds = 180 + (comments_posted * 10)  # Gradually increase spacing
            print(f"\n  Waiting {wait_seconds}s before next comment...")
            if not DRY_RUN:
                time.sleep(wait_seconds)

    # Final report
    print(f"\n{'='*60}")
    print(f"TRAVELING COMMENTS REPORT")
    print(f"{'='*60}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Comments posted: {comments_posted}/{max_comments}")
    print()

    for i, entry in enumerate(comment_log, 1):
        print(f"--- Comment {i} ---")
        print(f"Target: {entry['target']} (@{entry['handle']})")
        print(f"Reaction: {entry['reaction']}")
        print(f"Comment: {entry['comment']}")
        print(f"Time: {entry['timestamp']}")
        print()

    # Save log
    log_path = f"/home/jared/projects/AI-CIV/aether/exports/linkedin-pipeline/traveling-comments-{datetime.now().strftime('%Y-%m-%d-%H%M')}.json"
    with open(log_path, "w") as f:
        json.dump(comment_log, f, indent=2)
    print(f"Log saved: {log_path}")

if __name__ == "__main__":
    main()
