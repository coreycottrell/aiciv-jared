"""
Pattern Extraction Engine
==========================

Takes a parsed migration_profile (from chatgpt_parser or claude_parser) and
extracts user patterns for the AI partner context.

This is the intelligence layer — it transforms raw conversation data into
structured signals that PureBrain uses to personalize first interactions.

MVP approach: keyword frequency analysis (no LLM calls required).
Phase 2 can replace/augment with LLM-based extraction.

Output: user_context_profile matching the spec's schema.
"""

import re
import logging
from collections import Counter
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stop words — filtered from topic extraction
# ---------------------------------------------------------------------------

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "through", "during",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "need", "dare", "ought", "used", "not", "no", "so",
    "if", "than", "then", "that", "this", "these", "those", "it", "its",
    "he", "she", "they", "we", "i", "you", "me", "him", "her", "us", "them",
    "what", "which", "who", "whom", "when", "where", "why", "how",
    "all", "both", "each", "few", "more", "most", "other", "some", "such",
    "also", "just", "any", "same", "as", "my", "your", "our", "their",
    "like", "use", "using", "want", "need", "know", "think", "get", "make",
    "way", "new", "time", "please", "help", "can", "write", "create",
    "would", "could", "want", "provide", "give", "show", "tell", "explain",
    "hi", "hello", "thanks", "thank", "sure", "ok", "okay", "yes", "no",
}

# ---------------------------------------------------------------------------
# Topic domain hints — used to label raw keywords
# ---------------------------------------------------------------------------

DOMAIN_HINTS = {
    "marketing": ["marketing", "campaign", "brand", "audience", "conversion", "funnel",
                  "seo", "ads", "copy", "copywriting", "email", "newsletter", "social media",
                  "content", "landing page", "cta", "engagement", "leads", "traffic"],
    "coding": ["code", "python", "javascript", "function", "bug", "error", "api",
               "database", "sql", "html", "css", "react", "node", "typescript",
               "class", "variable", "debug", "deploy", "git", "backend", "frontend",
               "algorithm", "data structure", "test", "testing"],
    "writing": ["write", "draft", "essay", "article", "blog", "report", "proposal",
                "email", "memo", "letter", "document", "edit", "revise", "proofread",
                "tone", "paragraph", "outline", "summary"],
    "research": ["research", "analyze", "analysis", "study", "data", "statistics",
                 "findings", "survey", "literature", "sources", "citation", "evidence"],
    "business": ["business", "strategy", "revenue", "profit", "market", "competitor",
                 "product", "customer", "sales", "growth", "startup", "company",
                 "team", "hiring", "management", "operations", "process", "kpi"],
    "finance": ["finance", "financial", "budget", "cost", "investment", "valuation",
                "accounting", "cash flow", "balance sheet", "roi", "p&l", "model"],
    "design": ["design", "ui", "ux", "layout", "color", "typography", "wireframe",
               "prototype", "visual", "brand", "logo", "figma", "canva"],
    "productivity": ["productivity", "workflow", "task", "project", "schedule",
                     "prioritize", "organize", "plan", "goal", "system", "routine"],
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_user_context_profile(migration_profile: dict) -> dict:
    """
    Produce the user_context_profile JSON from a migration_profile.

    Args:
        migration_profile: Output of parse_chatgpt_export() or parse_claude_export().

    Returns:
        user_context_profile dict:
            top_topics          — list of {"topic": str, "count": int, "domain": str}
            communication_style — human-readable style description
            preferred_answer_format — "bullet" | "prose" | "mixed"
            domain_vocabulary   — list of repeated technical terms
            custom_instructions_raw — original custom instructions string (or None)
            conversation_count  — int
            message_count       — int
            date_range          — {"start": ISO str, "end": ISO str}
            date_range_years    — float (e.g. 2.3)
            source              — "chatgpt" | "claude" | "generic"
    """
    conversations = migration_profile.get("conversations", [])
    all_user_text = _collect_user_text(conversations)
    custom_instructions = migration_profile.get("custom_instructions") or ""

    top_topics = extract_top_topics(all_user_text, n=10)
    style_desc, format_pref = detect_communication_style(
        all_user_text, custom_instructions
    )
    vocab = extract_domain_vocabulary(all_user_text, top_n=30)
    date_range = migration_profile.get("date_range", {})
    date_range_years = _compute_years(date_range)

    return {
        "top_topics": top_topics,
        "communication_style": style_desc,
        "preferred_answer_format": format_pref,
        "domain_vocabulary": vocab,
        "custom_instructions_raw": custom_instructions or None,
        "conversation_count": migration_profile.get("conversation_count", 0),
        "message_count": migration_profile.get("message_count", 0),
        "date_range": date_range,
        "date_range_years": date_range_years,
        "source": migration_profile.get("source", "unknown"),
    }


def extract_top_topics(text: str, n: int = 10) -> list:
    """
    Extract top N topics by word/phrase frequency.

    Returns a list of dicts:
        [{"topic": "market analysis", "count": 23, "domain": "business"}, ...]
    """
    # 1. Extract bigrams that look like meaningful phrases
    bigrams = _extract_bigrams(text)
    bigram_counts = Counter(bigrams)

    # 2. Extract single keywords (after filtering stop words)
    words = _tokenize(text)
    word_counts = Counter(w for w in words if w not in STOP_WORDS and len(w) > 3)

    # 3. Boost bigrams that contain high-frequency keywords
    # Merge: prefer bigrams over single words when bigram count >= 3
    combined: dict = {}
    for bigram, count in bigram_counts.items():
        if count >= 2:
            combined[bigram] = count

    for word, count in word_counts.items():
        if word not in " ".join(combined.keys()):
            combined[word] = count

    # 4. Sort by frequency, take top N
    top = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:n]

    result = []
    for topic, count in top:
        domain = _classify_domain(topic)
        result.append({"topic": topic, "count": count, "domain": domain})

    return result


def detect_communication_style(user_text: str, custom_instructions: str = "") -> tuple:
    """
    Detect communication style and preferred format.

    Returns:
        (style_description: str, format_preference: "bullet" | "prose" | "mixed")
    """
    combined = (user_text + " " + custom_instructions).lower()

    style_signals = []
    format_pref = "mixed"

    # Format signals
    bullet_keywords = ["bullet", "bullet point", "list", "numbered", "itemize",
                       "step by step", "steps", "breakdown", "outline"]
    prose_keywords = ["paragraph", "prose", "explain", "elaborate", "detailed",
                      "in depth", "thorough", "comprehensive", "full"]

    bullet_hits = sum(1 for k in bullet_keywords if k in combined)
    prose_hits = sum(1 for k in prose_keywords if k in combined)

    if bullet_hits > prose_hits and bullet_hits > 2:
        format_pref = "bullet"
        style_signals.append("prefers bulleted lists and structured output")
    elif prose_hits > bullet_hits and prose_hits > 2:
        format_pref = "prose"
        style_signals.append("prefers detailed prose explanations")
    else:
        style_signals.append("uses a mix of structured and narrative responses")

    # Brevity signals
    brevity_keywords = ["brief", "concise", "short", "tldr", "tl;dr", "quick",
                        "simple", "straightforward", "no preamble", "no fluff"]
    detail_keywords = ["detailed", "comprehensive", "thorough", "depth", "complete",
                       "exhaustive", "extensive", "full explanation"]

    brevity_hits = sum(1 for k in brevity_keywords if k in combined)
    detail_hits = sum(1 for k in detail_keywords if k in combined)

    if brevity_hits > detail_hits and brevity_hits > 1:
        style_signals.append("prefers concise, direct responses")
    elif detail_hits > brevity_hits and detail_hits > 1:
        style_signals.append("prefers thorough and detailed responses")

    # Tone signals
    if any(k in combined for k in ["professional", "formal", "business"]):
        style_signals.append("uses professional/formal tone")
    elif any(k in combined for k in ["casual", "conversational", "friendly", "informal"]):
        style_signals.append("prefers casual, conversational tone")

    # Expert level signals
    if any(k in combined for k in ["assume i know", "no basics", "skip explanation",
                                    "i'm a developer", "i'm an expert", "technical"]):
        style_signals.append("expert-level user, skip basics")

    description = "; ".join(style_signals) if style_signals else "general purpose style"
    return description, format_pref


def extract_domain_vocabulary(text: str, top_n: int = 30) -> list:
    """
    Extract repeated technical terms and domain-specific vocabulary.

    Filters for words that appear in known domain hint lists or
    appear frequently enough to be significant (>= 3 times).

    Returns a list of strings.
    """
    words = _tokenize(text)
    counts = Counter(w for w in words if w not in STOP_WORDS and len(w) > 3)

    # Known domain terms
    known_terms = set()
    for terms in DOMAIN_HINTS.values():
        known_terms.update(t.lower() for t in terms)

    vocab = []
    seen = set()

    # Priority: known domain terms that actually appear in text
    for term in known_terms:
        if term in text.lower() and term not in seen:
            vocab.append(term)
            seen.add(term)

    # High-frequency unknown terms (potentially domain-specific jargon)
    for word, count in counts.most_common(top_n * 2):
        if count >= 3 and word not in seen and word not in STOP_WORDS:
            vocab.append(word)
            seen.add(word)
            if len(vocab) >= top_n:
                break

    return vocab[:top_n]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _collect_user_text(conversations: list) -> str:
    """Concatenate all user message texts into one string for analysis."""
    parts = []
    for conv in conversations:
        for msg in conv.get("user_messages", []):
            text = msg.get("text", "")
            if text:
                parts.append(text)
    return " ".join(parts)


def _tokenize(text: str) -> list:
    """Simple word tokenizer — lowercase, strip punctuation."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    return [w.strip("-") for w in text.split() if w.strip("-")]


def _extract_bigrams(text: str) -> list:
    """Extract two-word sequences that could be meaningful topic phrases."""
    words = _tokenize(text)
    bigrams = []
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        # Only keep bigrams where both words are non-stop-words
        if w1 not in STOP_WORDS and w2 not in STOP_WORDS and len(w1) > 3 and len(w2) > 3:
            bigrams.append(f"{w1} {w2}")
    return bigrams


def _classify_domain(topic: str) -> str:
    """Return the best-matching domain label for a topic string."""
    topic_lower = topic.lower()
    for domain, hints in DOMAIN_HINTS.items():
        if any(hint in topic_lower or topic_lower in hint for hint in hints):
            return domain
    return "general"


def _compute_years(date_range: dict) -> float:
    """Compute the number of years between start and end in date_range."""
    start = date_range.get("start")
    end = date_range.get("end")
    if not start or not end:
        return 0.0
    try:
        def _parse(ts):
            ts = ts.replace("Z", "+00:00") if ts.endswith("Z") else ts
            return datetime.fromisoformat(ts)
        s = _parse(start)
        e = _parse(end)
        delta = e - s
        return round(delta.days / 365.25, 1)
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import json as _json
    import pprint

    if len(sys.argv) < 2:
        print("Usage: python pattern_extractor.py <path-to-migration_profile.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        profile = _json.load(f)

    result = extract_user_context_profile(profile)
    pprint.pprint(result)
