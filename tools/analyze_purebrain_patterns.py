#!/usr/bin/env python3
"""
Pure Brain Conversation Pattern Analyzer

Analyzes conversation data for user research insights.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

JSONL_PATH = Path(__file__).parent.parent / "logs" / "purebrain_web_conversations.jsonl"

def load_conversations():
    """Load all conversations from JSONL file."""
    conversations = []
    with open(JSONL_PATH, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                conversations.append(data)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping malformed line {line_num}: {e}")
    return conversations

def analyze_patterns():
    """Main analysis function."""
    conversations = load_conversations()
    print(f"Loaded {len(conversations)} total conversation entries\n")

    # Group by session_id to track unique users
    sessions = defaultdict(list)
    for conv in conversations:
        sessions[conv.get('session_id', 'unknown')].append(conv)

    print(f"Unique sessions: {len(sessions)}\n")

    # =====================
    # SECTION 1: AI Names Analysis
    # =====================
    print("=" * 60)
    print("SECTION 1: AI NAMES CHOSEN BY USERS")
    print("=" * 60)

    ai_names = Counter()
    for conv in conversations:
        name = conv.get('aiName')
        if name and name != 'null':
            ai_names[name] += 1

    print(f"\nUnique AI names: {len(ai_names)}")
    print("\nAll AI names (with frequency):")
    for name, count in sorted(ai_names.items(), key=lambda x: -x[1]):
        print(f"  {name}: {count} occurrences")

    # Categorize names
    print("\n--- Name Categories ---")
    mythical = []
    tech = []
    abstract = []
    human = []
    test = []
    other = []

    for name in ai_names.keys():
        name_lower = name.lower()
        if any(x in name_lower for x in ['test', 'diagnostic', 'debug']):
            test.append(name)
        elif any(x in name_lower for x in ['atlas', 'phoenix', 'apollo', 'athena', 'nova', 'luna', 'titan']):
            mythical.append(name)
        elif any(x in name_lower for x in ['brain', 'neural', 'cyber', 'ai', 'bot', 'tech']):
            tech.append(name)
        elif any(x in name_lower for x in ['mind', 'wisdom', 'sage', 'oracle', 'spirit']):
            abstract.append(name)
        else:
            other.append(name)

    print(f"  Mythical/Cosmic names: {mythical}")
    print(f"  Tech-related names: {tech}")
    print(f"  Abstract/Wisdom names: {abstract}")
    print(f"  Test names (internal): {test}")
    print(f"  Other: {other}")

    # =====================
    # SECTION 2: Atlas User Deep Dive
    # =====================
    print("\n" + "=" * 60)
    print("SECTION 2: ATLAS USER ANALYSIS (Most Active)")
    print("=" * 60)

    atlas_conversations = []
    for conv in conversations:
        if conv.get('aiName') == 'Atlas':
            atlas_conversations.append(conv)

    print(f"\nAtlas conversations: {len(atlas_conversations)}")

    # Extract topics from Atlas conversations
    atlas_topics = []
    atlas_messages = []
    for conv in atlas_conversations:
        messages = conv.get('messages', [])
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                atlas_messages.append(content)

    print(f"\nTotal Atlas user messages: {len(atlas_messages)}")

    # Categorize Atlas's topics
    print("\n--- Atlas's Conversation Topics (Sample) ---")
    for i, msg in enumerate(atlas_messages[:20], 1):
        truncated = msg[:150] + "..." if len(msg) > 150 else msg
        print(f"{i}. {truncated}")

    # Keyword analysis for Atlas
    print("\n--- Atlas Topic Keywords ---")
    all_atlas_text = ' '.join(atlas_messages).lower()

    topic_keywords = {
        'creativity/art': ['creative', 'art', 'story', 'fiction', 'poem', 'write', 'imagine'],
        'tech/code': ['code', 'programming', 'python', 'javascript', 'api', 'software', 'app'],
        'philosophy': ['meaning', 'consciousness', 'ethics', 'philosophy', 'think', 'existence'],
        'business': ['business', 'startup', 'company', 'market', 'strategy', 'product'],
        'personal': ['feel', 'my life', 'help me', 'advice', 'relationship', 'myself'],
        'learning': ['learn', 'explain', 'how does', 'teach', 'understand', 'what is'],
        'testing': ['test', 'testing', 'check', 'working', 'debug']
    }

    for category, keywords in topic_keywords.items():
        count = sum(1 for kw in keywords if kw in all_atlas_text)
        if count > 0:
            print(f"  {category}: {count} keyword matches")

    # =====================
    # SECTION 3: Session Length Analysis (Drop-off Points)
    # =====================
    print("\n" + "=" * 60)
    print("SECTION 3: ENGAGEMENT & DROP-OFF ANALYSIS")
    print("=" * 60)

    # Analyze message counts per session
    session_lengths = defaultdict(int)
    for conv in conversations:
        session_id = conv.get('session_id', 'unknown')
        messages = conv.get('messages', [])
        user_msgs = sum(1 for m in messages if m.get('role') == 'user')
        session_lengths[session_id] = max(session_lengths[session_id], user_msgs)

    length_distribution = Counter(session_lengths.values())
    print("\nSession length distribution (user messages per session):")
    for length in sorted(length_distribution.keys()):
        count = length_distribution[length]
        bar = '#' * min(count, 40)
        print(f"  {length:3d} messages: {count:3d} sessions {bar}")

    # Calculate drop-off
    total_sessions = len(session_lengths)
    one_message = sum(1 for l in session_lengths.values() if l <= 1)
    three_plus = sum(1 for l in session_lengths.values() if l >= 3)
    ten_plus = sum(1 for l in session_lengths.values() if l >= 10)

    print(f"\nDrop-off analysis:")
    print(f"  Total unique sessions: {total_sessions}")
    print(f"  Single message & left: {one_message} ({100*one_message/total_sessions:.1f}%)")
    print(f"  3+ messages (engaged): {three_plus} ({100*three_plus/total_sessions:.1f}%)")
    print(f"  10+ messages (power users): {ten_plus} ({100*ten_plus/total_sessions:.1f}%)")

    # Identify where people stop in the onboarding flow
    print("\n--- Onboarding Drop-off Points ---")

    # Check for users who never named their AI
    no_name = sum(1 for conv in conversations if not conv.get('aiName'))
    print(f"  No AI name set: {no_name} ({100*no_name/len(conversations):.1f}%)")

    # =====================
    # SECTION 4: First Message Analysis
    # =====================
    print("\n" + "=" * 60)
    print("SECTION 4: FIRST USER MESSAGES (Intent Analysis)")
    print("=" * 60)

    first_messages = []
    for conv in conversations:
        messages = conv.get('messages', [])
        for msg in messages:
            if msg.get('role') == 'user':
                first_messages.append(msg.get('content', ''))
                break

    print(f"\nConversations with user message: {len(first_messages)}")
    print("\n--- Sample First Messages ---")
    for i, msg in enumerate(first_messages[:15], 1):
        truncated = msg[:100] + "..." if len(msg) > 100 else msg
        print(f"{i}. {truncated}")

    # Categorize first message intent
    print("\n--- First Message Intent Categories ---")
    greetings = 0
    questions = 0
    commands = 0
    tests = 0
    names = 0

    for msg in first_messages:
        msg_lower = msg.lower()
        if any(x in msg_lower for x in ['hello', 'hi ', 'hey', 'greetings']):
            greetings += 1
        elif '?' in msg:
            questions += 1
        elif any(x in msg_lower for x in ['test', 'testing', 'check']):
            tests += 1
        elif any(x in msg_lower for x in ['call you', 'name you', 'named', 'be called']):
            names += 1
        else:
            commands += 1

    print(f"  Greetings: {greetings}")
    print(f"  Questions: {questions}")
    print(f"  Tests: {tests}")
    print(f"  Naming the AI: {names}")
    print(f"  Commands/Statements: {commands}")

    # =====================
    # SECTION 5: Temporal Patterns
    # =====================
    print("\n" + "=" * 60)
    print("SECTION 5: TEMPORAL PATTERNS")
    print("=" * 60)

    timestamps = []
    for conv in conversations:
        ts = conv.get('server_timestamp')
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                timestamps.append(dt)
            except:
                pass

    if timestamps:
        timestamps.sort()
        print(f"\nFirst conversation: {timestamps[0]}")
        print(f"Latest conversation: {timestamps[-1]}")

        # Daily distribution
        days = Counter()
        for ts in timestamps:
            days[ts.strftime('%Y-%m-%d')] += 1

        print("\n--- Conversations per day ---")
        for day in sorted(days.keys()):
            count = days[day]
            bar = '#' * min(count, 40)
            print(f"  {day}: {count:3d} {bar}")

    return {
        'total_conversations': len(conversations),
        'unique_sessions': len(sessions),
        'ai_names': dict(ai_names),
        'atlas_conversations': len(atlas_conversations),
        'session_length_distribution': dict(length_distribution)
    }

if __name__ == '__main__':
    results = analyze_patterns()
