"""
OpenAI Intent Classifier for Experiential Marketing Signals
"""
import json
import requests
from typing import List, Dict, Optional
from .config import OPENAI_API_KEY, SIGNAL_TYPES

SYSTEM_PROMPT = """You are an experiential marketing intent classifier for CPG brands. Analyze LinkedIn profiles AND activity to identify buying signals for experiential giveaway services.

CONTEXT:
- We sell experiential giveaways (not sampling) - memorable brand interactions
- Our targets are marketing/brand leaders at CPG companies
- Look for signals in BOTH profile data AND posts/activity

SIGNAL TYPES (use exactly these values):
- liked_experiential_post: Liked content about experiential, activation, brand experience
- commented_on_activation: Commented on experiential marketing content
- posted_about_launch: Posted about product launch, new flavor, brand activation
- follows_experiential_page: Follows experiential marketing brands/pages
- commented_on_competitor: Engaged with competitor experiential content
- timing_trigger: New role (<1 year), title mentions experiential/activation/brand experience, or upcoming campaign

IMPORTANT - Generate signals from PROFILE DATA too:
- Job title contains "experiential", "activation", "brand experience", "shopper marketing" → timing_trigger (strength 6-8)
- Started current role recently (within 1 year) → timing_trigger (strength 5-7)
- Works at major CPG company in marketing role → timing_trigger (strength 4-6)
- Headline mentions launches, campaigns, activations → timing_trigger (strength 6-8)

SIGNAL STRENGTH GUIDE:
- 1-3: Weak signal (generic, tangential)
- 4-6: Moderate signal (relevant role/company, some indicators)
- 7-9: Strong signal (explicit experiential focus, recent posts about launches)
- 10: Hot signal (explicitly seeking experiential partners)

OUTPUT FORMAT (JSON only):
{
  "signals": [
    {
      "type": "signal_type_here",
      "strength": 7,
      "evidence": "Direct quote or specific observation"
    }
  ]
}

ALWAYS look for at least one signal from profile data if the person works in marketing at a CPG company."""


def classify_linkedin_activity(
    name: str,
    headline: str,
    company: str,
    posts: List[Dict],
    activities: List[Dict],
    job_title: str = "",
    job_started: str = "",
) -> List[Dict]:
    """
    Classify LinkedIn profile and activity into experiential marketing signals.

    Args:
        name: Person's full name
        headline: LinkedIn headline/title
        company: Company name
        posts: List of recent posts with text, likes, comments, timestamp
        activities: List of recent activities (likes, comments on others' posts)
        job_title: Current job title
        job_started: When they started current role (e.g., "3-2022")

    Returns:
        List of classified signals with type, strength, and evidence
    """
    # Format posts for prompt
    posts_text = "\n".join([
        f'- "{p.get("text", "")[:200]}..." ({p.get("likes", 0)} likes, {p.get("comments", 0)} comments)'
        for p in posts[:5]
    ]) if posts else "No recent posts available"

    # Format activities for prompt
    activities_text = "\n".join([
        f'- {a.get("type", "engagement")}: "{a.get("targetPost", "")[:100]}..."'
        for a in activities[:5]
    ]) if activities else "No recent activity available"

    user_prompt = f"""Analyze this LinkedIn profile for experiential marketing intent:

PROFILE DATA:
Name: {name}
Current Title: {job_title or headline}
Headline: {headline}
Company: {company}
Role Start Date: {job_started or "Unknown"}

RECENT POSTS:
{posts_text}

RECENT ACTIVITY:
{activities_text}

Look for signals in BOTH the profile data AND posts. Generate at least one signal if this person works in marketing at a CPG/consumer goods company."""

    # Call OpenAI
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        },
    )

    resp.raise_for_status()
    result = resp.json()

    try:
        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        signals = parsed.get("signals", [])

        # Validate signal types
        valid_signals = []
        for sig in signals:
            if sig.get("type") in SIGNAL_TYPES:
                valid_signals.append({
                    "type": sig["type"],
                    "strength": min(10, max(1, int(sig.get("strength", 5)))),
                    "evidence": sig.get("evidence", "")[:500],
                })

        return valid_signals

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error parsing OpenAI response: {e}")
        return []


def classify_simple_signal(
    activity_type: str,
    content: str,
    source: str = "LinkedIn",
) -> Optional[Dict]:
    """
    Quick classification for a single activity without full profile context.

    Args:
        activity_type: 'post', 'like', 'comment', 'share', 'follow'
        content: The text content or description of the activity
        source: Where this came from

    Returns:
        Signal dict or None if not relevant
    """
    prompt = f"""Classify this single LinkedIn activity for experiential marketing intent:

Activity type: {activity_type}
Content: {content}

If this indicates experiential marketing interest, return a signal. Otherwise return empty signals array."""

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        },
    )

    resp.raise_for_status()
    result = resp.json()

    try:
        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        signals = parsed.get("signals", [])

        if signals and signals[0].get("type") in SIGNAL_TYPES:
            return {
                "type": signals[0]["type"],
                "strength": min(10, max(1, int(signals[0].get("strength", 5)))),
                "evidence": signals[0].get("evidence", "")[:500],
                "source": source,
            }
        return None

    except Exception as e:
        print(f"Error classifying signal: {e}")
        return None


if __name__ == "__main__":
    # Test the classifier
    print("Testing OpenAI Classifier...")

    test_signals = classify_linkedin_activity(
        name="Sarah Chen",
        headline="VP Brand Marketing at PepsiCo",
        company="PepsiCo",
        posts=[
            {
                "text": "Excited to announce our new flavor launch next month! Planning an immersive activation in NYC.",
                "likes": 145,
                "comments": 23,
            }
        ],
        activities=[
            {
                "type": "like",
                "targetPost": "Coca-Cola's experiential marketing recap from SXSW",
            }
        ],
    )

    print("\nClassified signals:")
    for sig in test_signals:
        print(f"  - {sig['type']} (strength: {sig['strength']})")
        print(f"    Evidence: {sig['evidence']}")

    print("\n✅ Classifier working!")
