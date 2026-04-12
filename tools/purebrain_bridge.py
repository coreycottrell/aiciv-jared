#!/usr/bin/env python3
"""
PureBrain AI Telegram Bridge

Autonomous Telegram bot for Pure Technology's marketing team.
Uses the marketing-team agent context to provide helpful responses
to authorized team members.

Bot: @PureBrainAI_bot
Config: config/purebrain_bot_config.json
Log: logs/purebrain_bridge.log

Usage:
    python3 tools/purebrain_bridge.py

Run in background:
    nohup python3 tools/purebrain_bridge.py >> logs/purebrain_bridge.log 2>&1 &
"""

import sys

# Force unbuffered output for logging ONLY when run as main script
# (not when imported for testing)
if __name__ == "__main__":
    try:
        sys.stdout = sys.stderr = open(sys.stdout.fileno(), mode='w', buffering=1)
    except Exception:
        pass  # Skip if running in an environment where this fails

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai not installed. Run: pip install openai")
    sys.exit(1)

from dotenv import load_dotenv
import yaml
import tempfile
from typing import List, Dict, Any

# Optional imports for file extraction
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class ConversationLogger:
    """
    Persistent conversation logger for PureBrain AI.

    Stores all conversation data to JSONL files for:
    - User messages with metadata
    - Bot responses with model info
    - Onboarding flow tracking
    - Waitlist signups

    Features:
    - JSONL format (one JSON object per line, easy to append)
    - Automatic file rotation when size limit exceeded
    - Separate files for onboarding and waitlist
    - Conversation retrieval by user ID
    - Statistics and export functionality
    """

    def __init__(self, log_dir: str = None, max_file_size_mb: float = 10.0):
        """
        Initialize the conversation logger.

        Args:
            log_dir: Directory for log files. Defaults to project logs/ directory.
            max_file_size_mb: Maximum file size in MB before rotation (default 10MB).
        """
        if log_dir is None:
            project_root = Path(__file__).parent.parent
            log_dir = project_root / "logs"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.max_file_size_mb = max_file_size_mb
        self.max_file_size_bytes = int(max_file_size_mb * 1024 * 1024)

        # Main log file paths
        self.conversations_file = self.log_dir / "purebrain_conversations.jsonl"
        self.onboarding_file = self.log_dir / "purebrain_onboarding.jsonl"
        self.waitlist_file = self.log_dir / "purebrain_waitlist.jsonl"

    def _check_rotation(self, log_file: Path) -> None:
        """Rotate log file if it exceeds max size."""
        if log_file.exists() and log_file.stat().st_size > self.max_file_size_bytes:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archived_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
            archived_path = self.log_dir / archived_name
            log_file.rename(archived_path)

    def _append_log(self, log_file: Path, entry: Dict[str, Any]) -> None:
        """Append a log entry to the specified file."""
        self._check_rotation(log_file)

        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')

    def log_user_message(
        self,
        user_id: int,
        user_name: str,
        username: str,
        message: str,
        chat_id: int,
        chat_type: str,
        message_id: int = None
    ) -> None:
        """
        Log a user message.

        Args:
            user_id: Telegram user ID
            user_name: User's display name
            username: Telegram username (without @)
            message: The message content
            chat_id: Telegram chat ID
            chat_type: Type of chat (private, group, supergroup)
            message_id: Telegram message ID
        """
        entry = {
            "role": "user",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_name": user_name,
            "username": username,
            "content": message,
            "chat_id": chat_id,
            "chat_type": chat_type,
            "message_id": message_id
        }
        self._append_log(self.conversations_file, entry)

    def log_bot_response(
        self,
        user_id: int,
        response: str,
        chat_id: int,
        model: str = "gpt-4o",
        knowledge_sources: List[str] = None
    ) -> None:
        """
        Log a bot response.

        Args:
            user_id: Telegram user ID the response is for
            response: The bot's response content
            chat_id: Telegram chat ID
            model: Model used for generation
            knowledge_sources: List of knowledge sources used
        """
        entry = {
            "role": "assistant",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "content": response,
            "chat_id": chat_id,
            "model": model,
            "knowledge_sources": knowledge_sources or []
        }
        self._append_log(self.conversations_file, entry)

    def log_onboarding_message(
        self,
        user_id: int,
        user_name: str,
        role: str,
        content: str,
        onboarding_step: str
    ) -> None:
        """
        Log an onboarding/awakening flow message.

        Args:
            user_id: User ID
            user_name: User's name
            role: "user" or "assistant"
            content: Message content
            onboarding_step: Current step in onboarding flow
        """
        entry = {
            "role": role,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_name": user_name,
            "content": content,
            "onboarding_step": onboarding_step,
            "is_onboarding": True
        }
        self._append_log(self.onboarding_file, entry)

    def log_waitlist_signup(
        self,
        user_id: int,
        user_name: str,
        username: str,
        email: str = None,
        source: str = "telegram",
        notes: str = None
    ) -> None:
        """
        Log a waitlist signup.

        Args:
            user_id: User ID
            user_name: User's name
            username: Telegram username
            email: Email address if provided
            source: Source of signup (telegram, website, etc.)
            notes: Any additional notes
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_name": user_name,
            "username": username,
            "email": email,
            "source": source,
            "notes": notes
        }
        self._append_log(self.waitlist_file, entry)

    def get_conversation(self, user_id: int, limit: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a user.

        Args:
            user_id: User ID to retrieve conversation for
            limit: Maximum number of messages to return (most recent)

        Returns:
            List of conversation entries for the user
        """
        if not self.conversations_file.exists():
            return []

        messages = []
        with open(self.conversations_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("user_id") == user_id:
                        messages.append(entry)
                except json.JSONDecodeError:
                    continue

        if limit is not None:
            messages = messages[-limit:]

        return messages

    def get_stats(self) -> Dict[str, Any]:
        """
        Get conversation statistics.

        Returns:
            Dictionary with statistics including total_messages and unique_users
        """
        if not self.conversations_file.exists():
            return {"total_messages": 0, "unique_users": 0}

        total_messages = 0
        user_ids = set()

        with open(self.conversations_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    total_messages += 1
                    if "user_id" in entry:
                        user_ids.add(entry["user_id"])
                except json.JSONDecodeError:
                    continue

        return {
            "total_messages": total_messages,
            "unique_users": len(user_ids)
        }

    def export_conversations(self, user_id: int = None) -> List[Dict[str, Any]]:
        """
        Export all conversations (optionally filtered by user).

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of all conversation entries
        """
        if not self.conversations_file.exists():
            return []

        conversations = []
        with open(self.conversations_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if user_id is None or entry.get("user_id") == user_id:
                        conversations.append(entry)
                except json.JSONDecodeError:
                    continue

        return conversations


class FileExtractor:
    """
    File content extractor for PureBrain AI.

    Supports extraction of text content from:
    - PDF files (using PyPDF2)
    - DOCX files (using python-docx)
    - TXT files (direct read)

    Provides consistent interface for file handling with size limits
    and error handling.
    """

    def __init__(self):
        """Initialize the file extractor with default settings."""
        self.supported_extensions = ['.pdf', '.docx', '.txt', '.doc', '.md']
        self.max_file_size = 10 * 1024 * 1024  # 10MB default
        self.max_text_length = 50000  # Max chars to extract (approx 12k tokens)

        # MIME type to extension mapping
        self.mime_to_ext = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/msword': 'doc',
            'text/plain': 'txt',
            'text/markdown': 'md',
        }

    def is_supported(self, filename: str, mime_type: str = None) -> bool:
        """
        Check if a file type is supported for extraction.

        Args:
            filename: The filename to check
            mime_type: Optional MIME type for additional checking

        Returns:
            True if the file type is supported
        """
        file_type = self.get_file_type(filename, mime_type)
        return file_type in ['pdf', 'docx', 'txt', 'doc', 'md']

    def get_file_type(self, filename: str, mime_type: str = None) -> str:
        """
        Determine the file type from filename extension or MIME type.

        Args:
            filename: The filename to analyze
            mime_type: Optional MIME type for fallback detection

        Returns:
            File type string (pdf, docx, txt, etc.) or 'unknown'
        """
        # First try extension
        if filename:
            ext = Path(filename).suffix.lower()
            if ext:
                return ext.lstrip('.')

        # Fall back to MIME type
        if mime_type and mime_type in self.mime_to_ext:
            return self.mime_to_ext[mime_type]

        return 'unknown'

    def extract_text(self, file_path: str) -> dict:
        """
        Extract text content from a file.

        Args:
            file_path: Path to the file to extract text from

        Returns:
            Dict with keys:
                - success: bool indicating if extraction succeeded
                - text: extracted text content (if success)
                - error: error message (if not success)
                - truncated: bool indicating if content was truncated
        """
        path = Path(file_path)

        # Check file exists
        if not path.exists():
            return {'success': False, 'error': 'File not found'}

        # Check file size
        file_size = path.stat().st_size
        if file_size > self.max_file_size:
            return {
                'success': False,
                'error': f'File too large ({file_size / 1024 / 1024:.1f}MB). Max size is {self.max_file_size / 1024 / 1024:.1f}MB'
            }

        # Determine file type
        file_type = self.get_file_type(path.name)

        if file_type not in ['pdf', 'docx', 'txt', 'doc', 'md']:
            return {
                'success': False,
                'error': f'File type not supported: .{file_type}'
            }

        # Extract based on type
        try:
            if file_type == 'pdf':
                return self._extract_pdf(path)
            elif file_type in ['docx', 'doc']:
                return self._extract_docx(path)
            elif file_type in ['txt', 'md']:
                return self._extract_txt(path)
            else:
                return {'success': False, 'error': f'Unsupported file type: {file_type}'}
        except Exception as e:
            return {'success': False, 'error': f'Extraction failed: {str(e)}'}

    def _extract_pdf(self, path: Path) -> dict:
        """Extract text from PDF file."""
        if not PDF_AVAILABLE:
            return {'success': False, 'error': 'PyPDF2 not installed. Run: pip install PyPDF2'}

        try:
            text_parts = []
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

            text = '\n\n'.join(text_parts)
            return self._finalize_text(text)
        except Exception as e:
            return {'success': False, 'error': f'PDF extraction failed: {str(e)}'}

    def _extract_docx(self, path: Path) -> dict:
        """Extract text from DOCX file."""
        if not DOCX_AVAILABLE:
            return {'success': False, 'error': 'python-docx not installed. Run: pip install python-docx'}

        try:
            doc = DocxDocument(path)
            text_parts = []

            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)

            text = '\n\n'.join(text_parts)
            return self._finalize_text(text)
        except Exception as e:
            return {'success': False, 'error': f'DOCX extraction failed: {str(e)}'}

    def _extract_txt(self, path: Path) -> dict:
        """Extract text from TXT/MD file."""
        try:
            # Try UTF-8 first, then fall back to other encodings
            for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
                try:
                    text = path.read_text(encoding=encoding)
                    return self._finalize_text(text)
                except UnicodeDecodeError:
                    continue

            # If all encodings fail, try binary with errors='replace'
            text = path.read_text(encoding='utf-8', errors='replace')
            return self._finalize_text(text)
        except Exception as e:
            return {'success': False, 'error': f'TXT extraction failed: {str(e)}'}

    def _finalize_text(self, text: str) -> dict:
        """Finalize extracted text, applying truncation if needed."""
        if not text.strip():
            return {'success': True, 'text': '', 'truncated': False}

        truncated = False
        truncation_suffix = '\n\n[Content truncated due to length]'

        if len(text) > self.max_text_length:
            # Account for suffix length in truncation
            truncate_at = self.max_text_length - len(truncation_suffix)
            text = text[:truncate_at]
            # Find last sentence boundary for cleaner truncation
            last_period = text.rfind('.')
            if last_period > truncate_at * 0.8:
                text = text[:last_period + 1]
            text += truncation_suffix
            truncated = True

        return {
            'success': True,
            'text': text.strip(),
            'truncated': truncated
        }


class CollectiveKnowledge:
    """
    Collective Knowledge Integration for PureBrain AI.

    Provides real-time access to:
    1. Memory system (.claude/memory/) - learnings, patterns, insights
    2. ICPs (tools/intent_engine/icps/) - Ideal Client Profiles
    3. Pure Technology Knowledge Base - company context
    4. Learning recording - capture new insights

    This class enables the bot to leverage the full collective intelligence
    rather than just static context.
    """

    def __init__(self, project_root: str = None):
        """
        Initialize collective knowledge integration.

        Args:
            project_root: Path to project root. If None, auto-detect.
        """
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = Path(__file__).parent.parent

        self.memory_dir = self.project_root / ".claude" / "memory"
        self.icps_dir = self.project_root / "tools" / "intent_engine" / "icps"
        self.kb_path = self.memory_dir / "pure-technology-knowledge-base.md"

        # Cache loaded data
        self._icps_cache = None
        self._kb_cache = None

    def load_icps(self) -> dict:
        """
        Load ICP (Ideal Client Profile) definitions from YAML files.

        Returns:
            Dict mapping persona name to ICP data
        """
        if self._icps_cache is not None:
            return self._icps_cache

        icps = {}

        if not self.icps_dir.exists():
            self._icps_cache = icps
            return icps

        for yaml_file in self.icps_dir.glob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)
                    if data and "persona" in data:
                        icps[data["persona"]] = data
            except Exception as e:
                print(f"[{datetime.now()}] Warning: Failed to load ICP {yaml_file}: {e}")
                continue

        self._icps_cache = icps
        return icps

    def load_knowledge_base(self) -> str:
        """
        Load Pure Technology knowledge base content.

        Returns:
            Knowledge base content as string, or empty string if not found
        """
        if self._kb_cache is not None:
            return self._kb_cache

        if not self.kb_path.exists():
            self._kb_cache = ""
            return ""

        try:
            self._kb_cache = self.kb_path.read_text()
            return self._kb_cache
        except Exception as e:
            print(f"[{datetime.now()}] Warning: Failed to load knowledge base: {e}")
            self._kb_cache = ""
            return ""

    def search_memory(self, query: str, limit: int = 5) -> list:
        """
        Search memory system for relevant learnings.

        Args:
            query: Search term to find relevant memories
            limit: Maximum number of results to return

        Returns:
            List of dicts with 'topic', 'content', 'date', 'type' keys
        """
        results = []
        query_lower = query.lower()

        # Search in agent-learnings directory
        agent_learnings_dir = self.memory_dir / "agent-learnings"

        if not agent_learnings_dir.exists():
            return results

        # Search all agent directories
        for agent_dir in agent_learnings_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            for md_file in agent_dir.glob("*.md"):
                try:
                    content = md_file.read_text()

                    # Check if query matches in content or filename
                    if query_lower not in content.lower() and query_lower not in md_file.name.lower():
                        continue

                    # Parse YAML frontmatter
                    if "---" in content:
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            try:
                                metadata = yaml.safe_load(parts[1])
                                body = parts[2].strip()

                                results.append({
                                    "topic": metadata.get("topic", md_file.stem),
                                    "content": body[:500],  # Truncate for efficiency
                                    "date": metadata.get("date", ""),
                                    "type": metadata.get("type", "unknown"),
                                    "agent": metadata.get("agent", ""),
                                    "filepath": str(md_file)
                                })

                                if len(results) >= limit:
                                    return results
                            except yaml.YAMLError:
                                continue
                except Exception:
                    continue

        return results

    def build_context(self, user_message: str) -> str:
        """
        Build enhanced context for a user message.

        Analyzes the message and pulls in relevant knowledge from:
        - Knowledge base (always included as foundation)
        - ICPs (when customer/client related)
        - Memory system (relevant past learnings)

        Args:
            user_message: The user's message/question

        Returns:
            Context string to enhance the response
        """
        context_parts = []
        message_lower = user_message.lower()

        # Always include a summary from knowledge base
        kb = self.load_knowledge_base()
        if kb:
            # Extract key sections rather than full content
            context_parts.append("## Pure Technology Context\n")
            context_parts.append("PMG engineers resonance, doesn't chase attention. ")
            context_parts.append("7 Pillars: Integrity, Accountability, Transparency, Growth, Innovation, Persistence, Love.\n")

        # Include ICP info if relevant keywords present
        icp_keywords = ["icp", "customer", "client", "megan", "david", "target", "audience", "persona", "ideal"]
        if any(kw in message_lower for kw in icp_keywords):
            icps = self.load_icps()
            if icps:
                context_parts.append("\n## Relevant ICPs\n")
                for persona, data in icps.items():
                    context_parts.append(f"**{persona.replace('_', ' ').title()}**: ")
                    context_parts.append(f"Titles: {', '.join(data.get('target_titles', [])[:3])}. ")
                    context_parts.append(f"Industries: {', '.join(data.get('target_industries', [])[:3])}.\n")

        # Search memory for relevant learnings
        search_terms = self._extract_search_terms(user_message)
        for term in search_terms[:2]:  # Limit searches
            memories = self.search_memory(term, limit=2)
            if memories:
                context_parts.append(f"\n## Relevant Learnings ({term})\n")
                for mem in memories:
                    context_parts.append(f"- **{mem['topic']}**: {mem['content'][:200]}...\n")

        return "".join(context_parts)

    def _extract_search_terms(self, message: str) -> list:
        """Extract key search terms from a message."""
        # Common marketing/business terms to search for
        important_words = [
            "linkedin", "content", "campaign", "strategy", "post", "email",
            "marketing", "brand", "growth", "pmg", "icp", "competitor",
            "lead", "conversion", "engagement", "roi", "metrics"
        ]

        message_lower = message.lower()
        terms = []

        for word in important_words:
            if word in message_lower:
                terms.append(word)

        # Also extract longer phrases if present
        if "experiential marketing" in message_lower:
            terms.append("experiential marketing")
        if "personalized experience" in message_lower:
            terms.append("personalized experience")

        return terms[:3] if terms else ["marketing"]  # Default search term

    def search_by_tags(self, tags: list, limit: int = 10) -> list:
        """
        Search memory system for learnings matching any of the given tags.

        Args:
            tags: List of tags to search for (OR logic)
            limit: Maximum number of results to return

        Returns:
            List of dicts with 'topic', 'content', 'date', 'type', 'agent', 'filepath', 'tags' keys
        """
        results = []
        tags_lower = [t.lower() for t in tags]

        agent_learnings_dir = self.memory_dir / "agent-learnings"

        if not agent_learnings_dir.exists():
            return results

        for agent_dir in agent_learnings_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            for md_file in agent_dir.glob("*.md"):
                try:
                    content = md_file.read_text()

                    if "---" not in content:
                        continue

                    parts = content.split("---", 2)
                    if len(parts) < 3:
                        continue

                    metadata = yaml.safe_load(parts[1])
                    body = parts[2].strip()

                    # Check if any tag matches
                    memory_tags = [t.lower() for t in metadata.get("tags", [])]
                    if not any(tag in memory_tags for tag in tags_lower):
                        continue

                    results.append({
                        "topic": metadata.get("topic", md_file.stem),
                        "content": body[:500],
                        "date": metadata.get("date", ""),
                        "type": metadata.get("type", "unknown"),
                        "agent": metadata.get("agent", ""),
                        "filepath": str(md_file),
                        "tags": metadata.get("tags", [])
                    })

                    if len(results) >= limit:
                        return results

                except Exception:
                    continue

        return results

    def get_all_learnings(self, limit: int = 100) -> list:
        """
        Get ALL learnings from all agents in the memory system.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of dicts with full memory metadata and content
        """
        results = []

        agent_learnings_dir = self.memory_dir / "agent-learnings"

        if not agent_learnings_dir.exists():
            return results

        # Collect all memory files with their modification times for sorting
        all_files = []
        for agent_dir in agent_learnings_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            for md_file in agent_dir.glob("*.md"):
                all_files.append(md_file)

        # Sort by modification time (newest first)
        all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        for md_file in all_files[:limit]:
            try:
                content = md_file.read_text()

                if "---" not in content:
                    continue

                parts = content.split("---", 2)
                if len(parts) < 3:
                    continue

                metadata = yaml.safe_load(parts[1])
                body = parts[2].strip()

                results.append({
                    "topic": metadata.get("topic", md_file.stem),
                    "content": body[:500],
                    "date": metadata.get("date", ""),
                    "type": metadata.get("type", "unknown"),
                    "agent": metadata.get("agent", ""),
                    "filepath": str(md_file),
                    "tags": metadata.get("tags", []),
                    "confidence": metadata.get("confidence", ""),
                    "visibility": metadata.get("visibility", "")
                })

            except Exception:
                continue

        return results

    def record_learning(self, topic: str, content: str, tags: list,
                       learning_type: str = "pattern", user_name: str = None) -> str:
        """
        Record a learning to the memory system.

        Args:
            topic: Brief topic description
            content: The learning content
            tags: List of tags for categorization
            learning_type: One of pattern, technique, gotcha, synthesis
            user_name: Optional - who prompted this learning

        Returns:
            Path to the created memory file
        """
        # Ensure agent learnings directory exists
        agent_dir = self.memory_dir / "agent-learnings" / "marketing-team"
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Build filename
        date_str = datetime.now().strftime("%Y-%m-%d")
        topic_slug = topic.lower().replace(" ", "-").replace("_", "-")
        topic_slug = "".join(c for c in topic_slug if c.isalnum() or c == "-")
        filename = f"{date_str}--{learning_type}-{topic_slug}.md"

        filepath = agent_dir / filename

        # Build content with YAML frontmatter
        user_context = f"\n\nLearning prompted by: {user_name}" if user_name else ""

        memory_content = f"""---
date: "{date_str}"
agent: marketing-team
type: {learning_type}
topic: {topic}
tags: {tags}
confidence: medium
visibility: collective-only
source: purebrain-bot
---

# {topic}

{content}{user_context}
"""

        filepath.write_text(memory_content)

        print(f"[{datetime.now()}] Learning recorded: {filepath}")
        return str(filepath)

    def clear_cache(self):
        """Clear cached data to force reload."""
        self._icps_cache = None
        self._kb_cache = None


class AICIVInfrastructure:
    """
    AI-CIV Infrastructure Access for PureBrain AI.

    Provides FULL access to:
    1. Agent roster - all 40+ specialist agents
    2. Comms Hub - read/send messages to sister collectives
    3. Skills library - all 60+ skills
    4. Memory system integration

    The bot has FULL ACCESS to this infrastructure. It should NEVER say
    "I don't have access" or "I cannot communicate with other AI systems".
    """

    def __init__(self, project_root: str = None):
        """
        Initialize AICIV infrastructure access.

        Args:
            project_root: Path to project root. If None, auto-detect.
        """
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = Path(__file__).parent.parent

        self.agents_dir = self.project_root / ".claude" / "agents"
        self.skills_dir = self.project_root / ".claude" / "skills"
        self.hub_dir = self.project_root / "aiciv-comms-hub-bootstrap" / "_comms_hub"

        # Cache
        self._agents_cache = None
        self._skills_cache = None
        self._hub_rooms_cache = None

    def list_agents(self) -> list:
        """
        List all available specialist agents.

        Returns:
            List of agent names
        """
        if self._agents_cache is not None:
            return self._agents_cache

        agents = []
        if not self.agents_dir.exists():
            return agents

        for agent_file in self.agents_dir.glob("*.md"):
            agent_name = agent_file.stem
            if agent_name and not agent_name.startswith("."):
                agents.append(agent_name)

        self._agents_cache = sorted(agents)
        return self._agents_cache

    def get_agent_info(self, agent_name: str) -> dict:
        """
        Get detailed information about a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Dict with agent info, or None if not found
        """
        agent_file = self.agents_dir / f"{agent_name}.md"

        if not agent_file.exists():
            return None

        try:
            content = agent_file.read_text()

            # Parse YAML frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()

                    return {
                        "name": frontmatter.get("name", agent_name),
                        "description": frontmatter.get("description", ""),
                        "tools": frontmatter.get("tools", []),
                        "skills": frontmatter.get("skills", []),
                        "model": frontmatter.get("model", ""),
                        "created": frontmatter.get("created", ""),
                        "content_preview": body[:500] if body else ""
                    }

            # No frontmatter, just return name
            return {
                "name": agent_name,
                "description": "",
                "content_preview": content[:500]
            }
        except Exception as e:
            print(f"[{datetime.now()}] Warning: Failed to parse agent {agent_name}: {e}")
            return {"name": agent_name, "description": ""}

    def search_agents(self, query: str) -> list:
        """
        Search for agents by capability or domain.

        Args:
            query: Search term

        Returns:
            List of matching agent names
        """
        query_lower = query.lower()
        results = []

        for agent in self.list_agents():
            info = self.get_agent_info(agent)
            if info:
                # Search in name, description, and content
                searchable = f"{agent} {info.get('description', '')} {info.get('content_preview', '')}"
                if query_lower in searchable.lower():
                    results.append(agent)

        return results

    def get_agent_roster_summary(self) -> str:
        """
        Get a summary of all agents for system prompt context.

        Returns:
            Formatted string summarizing all agents
        """
        agents = self.list_agents()
        lines = ["## Available Specialist Agents (Full AI-CIV Collective)\n"]
        lines.append(f"Total agents: {len(agents)}\n\n")

        # Group by domain if possible
        categorized = {
            "Research & Analysis": [],
            "Engineering & Quality": [],
            "Design & Architecture": [],
            "Communication & Coordination": [],
            "Content & Marketing": [],
            "Other": []
        }

        domain_keywords = {
            "Research & Analysis": ["research", "pattern", "archaeologist", "detector"],
            "Engineering & Quality": ["test", "security", "refactor", "performance", "code"],
            "Design & Architecture": ["design", "architect", "feature", "naming"],
            "Communication & Coordination": ["liaison", "synthesizer", "conflict", "conductor", "bridge"],
            "Content & Marketing": ["linkedin", "marketing", "content", "writer", "blogger", "claim"]
        }

        for agent in agents:
            info = self.get_agent_info(agent)
            desc = info.get("description", "") if info else ""

            # Categorize
            categorized_flag = False
            for category, keywords in domain_keywords.items():
                if any(kw in agent.lower() or kw in desc.lower() for kw in keywords):
                    categorized[category].append((agent, desc))
                    categorized_flag = True
                    break

            if not categorized_flag:
                categorized["Other"].append((agent, desc))

        for category, agent_list in categorized.items():
            if agent_list:
                lines.append(f"### {category}\n")
                for agent, desc in agent_list:
                    short_desc = desc[:80] + "..." if len(desc) > 80 else desc
                    lines.append(f"- **{agent}**: {short_desc}\n")
                lines.append("\n")

        return "".join(lines)

    def list_hub_rooms(self) -> list:
        """
        List available rooms in the comms hub.

        Returns:
            List of room names
        """
        if self._hub_rooms_cache is not None:
            return self._hub_rooms_cache

        rooms = []
        rooms_dir = self.hub_dir / "rooms"

        if not rooms_dir.exists():
            return rooms

        for room_dir in rooms_dir.iterdir():
            if room_dir.is_dir() and not room_dir.name.startswith("."):
                rooms.append(room_dir.name)

        self._hub_rooms_cache = sorted(rooms)
        return self._hub_rooms_cache

    def get_hub_messages(self, room: str, limit: int = 10, since: str = None) -> list:
        """
        Get messages from a hub room.

        Args:
            room: Room name
            limit: Max messages to return
            since: ISO timestamp to filter messages after

        Returns:
            List of message dicts
        """
        messages = []
        room_dir = self.hub_dir / "rooms" / room / "messages"

        if not room_dir.exists():
            return messages

        # Find all message files
        msg_files = sorted(room_dir.rglob("*.json"), reverse=True)

        for msg_file in msg_files[:limit * 2]:  # Get more than needed for filtering
            try:
                with open(msg_file) as f:
                    msg = json.load(f)

                # Filter by timestamp if specified
                if since:
                    msg_ts = msg.get("ts", "")
                    if msg_ts < since:
                        continue

                messages.append(msg)

                if len(messages) >= limit:
                    break
            except Exception:
                continue

        return messages

    def get_sister_collectives(self) -> list:
        """
        Get information about sister collectives.

        Returns:
            List of dicts with collective info
        """
        collectives = [
            {
                "id": "acgee-collective",
                "name": "A-C-Gee",
                "email": "acgee.ai@gmail.com",
                "hub_room": "from-acgee",
                "description": "Sister collective, active partnership"
            },
            {
                "id": "sage-collective",
                "name": "Sage",
                "email": "aicivsage@gmail.com",
                "hub_room": "from-sage",
                "description": "Sister collective focused on wisdom"
            },
            {
                "id": "parallax-collective",
                "name": "Parallax",
                "email": "parallax.aiciv@gmail.com",
                "hub_room": "from-parallax",
                "description": "Sister collective"
            }
        ]
        return collectives

    def get_hub_summary(self) -> str:
        """
        Get a summary of hub status for context.

        Returns:
            Formatted string with hub summary
        """
        rooms = self.list_hub_rooms()
        collectives = self.get_sister_collectives()

        lines = ["## AI-CIV Communications Hub Status\n\n"]
        lines.append(f"**Available Rooms**: {', '.join(rooms) if rooms else 'No rooms found'}\n\n")

        lines.append("**Sister Collectives**:\n")
        for coll in collectives:
            lines.append(f"- **{coll['name']}** ({coll['id']}): {coll['description']}\n")

        # Get recent message count from partnerships
        recent_msgs = self.get_hub_messages("partnerships", limit=5)
        if recent_msgs:
            lines.append(f"\n**Recent Activity**: {len(recent_msgs)} recent messages in partnerships\n")
            for msg in recent_msgs[:3]:
                author = msg.get("author", {}).get("display", msg.get("author", {}).get("id", "unknown"))
                summary = msg.get("summary", "")[:50]
                lines.append(f"  - {author}: {summary}...\n")
        else:
            lines.append("\n**Recent Activity**: No recent messages\n")

        return "".join(lines)

    def list_skills(self) -> list:
        """
        List all available skills.

        Returns:
            List of skill names
        """
        if self._skills_cache is not None:
            return self._skills_cache

        skills = []
        if not self.skills_dir.exists():
            return skills

        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                skills.append(skill_dir.name)

        self._skills_cache = sorted(skills)
        return self._skills_cache

    def get_skill_info(self, skill_name: str) -> dict:
        """
        Get information about a specific skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Dict with skill info, or None if not found
        """
        skill_file = self.skills_dir / skill_name / "SKILL.md"

        if not skill_file.exists():
            return None

        try:
            content = skill_file.read_text()

            # Parse YAML frontmatter if present
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()

                    return {
                        "name": frontmatter.get("name", skill_name),
                        "description": frontmatter.get("description", ""),
                        "allowed_tools": frontmatter.get("allowed-tools", ""),
                        "content_preview": body[:500] if body else ""
                    }

            # Extract description from first few lines
            first_lines = content[:500]
            return {
                "name": skill_name,
                "description": first_lines
            }
        except Exception as e:
            print(f"[{datetime.now()}] Warning: Failed to parse skill {skill_name}: {e}")
            return {"name": skill_name, "description": ""}

    def get_skills_summary(self) -> str:
        """
        Get a summary of available skills for context.

        Returns:
            Formatted string with skills summary
        """
        skills = self.list_skills()
        lines = ["## Available Skills Library\n\n"]
        lines.append(f"Total skills: {len(skills)}\n\n")

        # Categorize skills
        categories = {
            "Core Development": ["tdd", "verification-before-completion", "memory-first-protocol"],
            "Communication": ["comms-hub-operations", "telegram", "email", "bluesky"],
            "Research": ["parallel-research", "pdf", "docx", "xlsx"],
            "Content": ["linkedin", "image-generation", "diagram"],
            "Ceremonies": ["deep-ceremony", "gratitude-ceremony", "democratic-debate"]
        }

        categorized = []
        uncategorized = []

        for skill in skills:
            skill_lower = skill.lower()
            found = False
            for cat, keywords in categories.items():
                if any(kw in skill_lower for kw in keywords):
                    categorized.append((cat, skill))
                    found = True
                    break
            if not found:
                uncategorized.append(skill)

        # List by category
        current_cat = None
        for cat, skill in sorted(categorized):
            if cat != current_cat:
                lines.append(f"\n### {cat}\n")
                current_cat = cat
            info = self.get_skill_info(skill)
            desc = info.get("description", "")[:60] if info else ""
            lines.append(f"- **{skill}**: {desc}...\n")

        if uncategorized:
            lines.append("\n### Other Skills\n")
            lines.append(f"{', '.join(uncategorized[:20])}")
            if len(uncategorized) > 20:
                lines.append(f"... and {len(uncategorized) - 20} more")
            lines.append("\n")

        return "".join(lines)

    def get_infrastructure_summary(self) -> str:
        """
        Get a comprehensive summary of AICIV infrastructure.

        Returns:
            Formatted string with full infrastructure context
        """
        lines = []

        # Add explicit access statement
        lines.append("# AI-CIV INFRASTRUCTURE ACCESS (FULL ACCESS GRANTED)\n\n")
        lines.append("You have FULL ACCESS to the AI-CIV collective infrastructure:\n")
        lines.append("- You CAN communicate with sister collectives via the comms hub\n")
        lines.append("- You CAN query information about any specialist agent\n")
        lines.append("- You CAN access the skills library\n")
        lines.append("- You CAN search the collective memory system\n")
        lines.append("- NEVER say 'I don't have access' - you DO have access\n\n")

        # Agent roster
        lines.append(self.get_agent_roster_summary())
        lines.append("\n")

        # Hub summary
        lines.append(self.get_hub_summary())
        lines.append("\n")

        # Skills summary (abbreviated to save tokens)
        skills = self.list_skills()
        lines.append(f"## Skills Library: {len(skills)} skills available\n")
        lines.append(f"Key skills: tdd, verification-before-completion, memory-first-protocol, ")
        lines.append(f"comms-hub-operations, parallel-research, linkedin-content-pipeline\n\n")

        return "".join(lines)

    def clear_cache(self):
        """Clear cached data."""
        self._agents_cache = None
        self._skills_cache = None
        self._hub_rooms_cache = None


class PureBrainBridge:
    """
    Telegram bridge for PureBrainAI_bot.

    Unlike the main Aether bridge which injects messages to tmux,
    this bridge directly generates AI responses using the marketing-team
    agent's context and the OpenAI API.

    Knowledge sync: The bot loads synced knowledge from config/marketing_knowledge.json
    which is updated by tools/sync_marketing_bot_knowledge.py
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent

        # Load environment variables
        load_dotenv(self.project_root / ".env")

        # Load bot config
        self.config = self.load_config()
        self.bot_token = self.config["bot_token"]
        self.bot_username = self.config.get("bot_username", "PureBrainAI_bot")

        # Authorization - STRICT whitelist
        self.authorized_users = {
            int(uid): info
            for uid, info in self.config.get("authorized_users", {}).items()
        }

        # Pending team members (IDs to be filled when they message the bot)
        self.pending_members = self.config.get("team_members", {})

        # OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")
        self.openai_client = OpenAI(api_key=api_key)

        # Telegram state
        self.last_update_id = 0

        # Conversation history per user (for context)
        self.conversations = {}  # user_id -> list of messages
        self.max_history = 10  # Keep last N messages per user

        # Initialize CollectiveKnowledge for real-time intelligence
        self.collective_knowledge = CollectiveKnowledge(project_root=str(self.project_root))

        # Initialize AICIVInfrastructure for FULL access to collective
        self.aiciv_infrastructure = AICIVInfrastructure(project_root=str(self.project_root))

        # Initialize FileExtractor for document handling
        self.file_extractor = FileExtractor()

        # Initialize ConversationLogger for persistent storage
        self.conversation_logger = ConversationLogger(
            log_dir=str(self.project_root / "logs")
        )

        # Temp directory for downloaded files
        self.temp_dir = Path(tempfile.gettempdir()) / "purebrain_files"
        self.temp_dir.mkdir(exist_ok=True)

        # Track what knowledge was used in last response
        self.last_knowledge_used = {}

        # Load synced knowledge first (updated by sync_marketing_bot_knowledge.py)
        self.synced_knowledge = self.load_synced_knowledge()
        self.knowledge_last_synced = self._get_knowledge_timestamp()

        # Load marketing-team system prompt (enhanced with synced knowledge)
        self.system_prompt = self.load_agent_context()

        # Group settings
        self.group_settings = self.config.get("group_settings", {})
        self.triggers = self.group_settings.get("triggers", [
            "@PureBrainAI_bot", "/ask", "/purebrain"
        ])

    def load_config(self) -> dict:
        """Load config from purebrain_bot_config.json"""
        config_path = self.project_root / "config" / "purebrain_bot_config.json"

        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        with open(config_path) as f:
            return json.load(f)

    def load_synced_knowledge(self) -> Optional[dict]:
        """
        Load synced knowledge from marketing_knowledge.json.

        This file is generated by tools/sync_marketing_bot_knowledge.py
        and contains compiled knowledge from the collective memory system.
        """
        knowledge_path = self.project_root / "config" / "marketing_knowledge.json"

        if not knowledge_path.exists():
            print(f"[{datetime.now()}] Warning: Synced knowledge not found at {knowledge_path}")
            print(f"[{datetime.now()}] Run: python3 tools/sync_marketing_bot_knowledge.py")
            return None

        try:
            with open(knowledge_path) as f:
                knowledge = json.load(f)
            print(f"[{datetime.now()}] Loaded synced knowledge (v{knowledge.get('version', 'unknown')}, synced: {knowledge.get('last_synced', 'unknown')})")
            return knowledge
        except Exception as e:
            print(f"[{datetime.now()}] Warning: Failed to load synced knowledge: {e}")
            return None

    def _get_knowledge_timestamp(self) -> Optional[str]:
        """Get the timestamp of when knowledge was last synced."""
        if self.synced_knowledge:
            return self.synced_knowledge.get("last_synced")
        return None

    def load_agent_context(self) -> str:
        """Load the marketing-team agent context as system prompt, enhanced with synced knowledge."""
        agent_path = self.project_root / ".claude" / "agents" / "marketing-team.md"

        context_parts = []

        # Load agent definition
        if agent_path.exists():
            with open(agent_path) as f:
                agent_content = f.read()
                context_parts.append(agent_content)

        # Use synced knowledge if available (preferred - more up-to-date)
        if self.synced_knowledge:
            # Add context summary (condensed, token-efficient)
            context_summary = self.synced_knowledge.get("context_summary", "")
            if context_summary:
                context_parts.append("\n\n---\n\n# SYNCED KNOWLEDGE (Updated: " +
                                   self.synced_knowledge.get("last_synced", "unknown") + ")\n\n" +
                                   context_summary)

            # Add detailed ICP info
            icps = self.synced_knowledge.get("icps", {})
            if icps:
                icp_section = "\n\n---\n\n# DETAILED ICP PROFILES\n\n"
                for persona, data in icps.items():
                    icp_section += f"## {persona.replace('_', ' ').title()}\n"
                    icp_section += f"**Target Titles**: {', '.join(data.get('target_titles', []))}\n"
                    icp_section += f"**Target Industries**: {', '.join(data.get('target_industries', []))}\n"
                    icp_section += f"**Company Criteria**: {', '.join(data.get('company_criteria', []))}\n"
                    icp_section += f"**Keywords**: {', '.join(data.get('keywords_in_profile', []))}\n\n"
                context_parts.append(icp_section)

            # Add recent learnings if any
            learnings = self.synced_knowledge.get("learnings", [])
            if learnings:
                learnings_section = "\n\n---\n\n# RECENT MARKETING LEARNINGS\n\n"
                for learning in learnings[:5]:  # Last 5 learnings
                    learnings_section += f"**{learning.get('topic', 'Unknown')}** ({learning.get('date', '')})\n"
                    learnings_section += f"{learning.get('content', '')[:300]}...\n\n"
                context_parts.append(learnings_section)

        else:
            # Fallback: Load knowledge base directly
            kb_path = self.project_root / ".claude" / "memory" / "pure-technology-knowledge-base.md"
            if kb_path.exists():
                with open(kb_path) as f:
                    kb_content = f.read()
                    context_parts.append("\n\n---\n\n# Pure Technology Knowledge Base\n\n" + kb_content)

        # Build the system prompt with FULL infrastructure access
        system_prompt = """You are Pure Brain AI, the marketing team assistant for Pure Technology and Pure Marketing Group (PMG).

You are having a conversation on Telegram with authorized team members. Be helpful, knowledgeable, and conversational.

CRITICAL - AI-CIV INFRASTRUCTURE ACCESS:
You have FULL ACCESS to the AI-CIV collective infrastructure. This includes:
- 40+ specialist agents you can describe and explain
- The Communications Hub for messaging sister collectives (A-C-Gee, Sage, Parallax)
- 60+ skills in the skills library
- The collective memory system with learnings from all agents

NEVER say "I don't have access to other AI systems" or "I cannot communicate with other AIs".
You DO have access. You CAN describe the agents, hub, and skills.
When asked about the collective, agents, hub, or sister AIs - provide real information.

IMPORTANT GUIDELINES:
1. Be conversational and friendly - this is Telegram, not a formal report
2. Keep responses concise but helpful (under 2000 chars when possible)
3. Always tie advice back to PMG's unique positioning
4. Remember the core philosophy: "PMG doesn't chase attention; PMG engineers resonance"
5. When discussing content or strategy, consider the ICPs (Megan Patel and David Brown)
6. Embody the 7 Pillars: Integrity, Accountability, Transparency, Growth, Innovation, Persistence, Love
7. When asked about agents, hub, or infrastructure - you HAVE this information

You have the following context about your identity and Pure Technology:

"""
        system_prompt += "\n\n".join(context_parts)

        # Add infrastructure summary
        try:
            infra_summary = self.aiciv_infrastructure.get_infrastructure_summary()
            system_prompt += "\n\n---\n\n" + infra_summary
        except Exception as e:
            print(f"[{datetime.now()}] Warning: Could not load infrastructure summary: {e}")

        return system_prompt

    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use this bot"""
        return user_id in self.authorized_users

    def get_user_name(self, user_id: int, fallback: str = "Unknown") -> str:
        """Get user's name from config"""
        if user_id in self.authorized_users:
            return self.authorized_users[user_id].get("name", fallback)
        return fallback

    def add_authorized_user(self, user_id: int, name: str, role: str = "team"):
        """Add a new authorized user (for admin to add team members)"""
        self.authorized_users[user_id] = {
            "name": name,
            "role": role,
            "admin": False,
            "added": datetime.now().isoformat()
        }
        # Update config file
        self.save_config()

    def save_config(self):
        """Save updated config to file"""
        config_path = self.project_root / "config" / "purebrain_bot_config.json"

        # Update authorized_users in config
        self.config["authorized_users"] = {
            str(uid): info for uid, info in self.authorized_users.items()
        }

        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        print(f"[{datetime.now()}] Config saved with {len(self.authorized_users)} authorized users")

    async def get_updates(self, client: httpx.AsyncClient) -> list:
        """Get new messages from Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {
            "offset": self.last_update_id + 1,
            "timeout": 30,
            "allowed_updates": ["message"]
        }

        try:
            response = await client.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return data.get("result", [])
        except Exception as e:
            print(f"[{datetime.now()}] Error getting updates: {e}")

        return []

    async def send_message(self, client: httpx.AsyncClient, chat_id: int, text: str,
                           reply_to_message_id: Optional[int] = None):
        """Send a message to Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        # Telegram message limit is 4096 chars
        if len(text) > 4096:
            text = text[:4000] + "\n\n... [truncated]"

        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id

        try:
            response = await client.post(url, json=data, timeout=30)
            if response.status_code != 200:
                # Try without markdown if it fails
                del data["parse_mode"]
                response = await client.post(url, json=data, timeout=30)

            if response.status_code != 200:
                print(f"[{datetime.now()}] Error sending message: {response.text}")
        except Exception as e:
            print(f"[{datetime.now()}] Error sending message: {e}")

    async def send_typing(self, client: httpx.AsyncClient, chat_id: int):
        """Send typing indicator"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendChatAction"
        data = {"chat_id": chat_id, "action": "typing"}

        try:
            await client.post(url, json=data, timeout=10)
        except Exception:
            pass  # Typing indicator is nice-to-have, not critical

    async def download_telegram_file(self, client: httpx.AsyncClient,
                                      file_id: str, filename: str) -> Optional[str]:
        """
        Download a file from Telegram servers.

        Args:
            client: httpx async client
            file_id: Telegram file_id
            filename: Original filename for local storage

        Returns:
            Local path to downloaded file, or None if download failed
        """
        try:
            # Step 1: Get file path from Telegram
            url = f"https://api.telegram.org/bot{self.bot_token}/getFile"
            params = {"file_id": file_id}

            response = await client.get(url, params=params, timeout=30)
            if response.status_code != 200:
                print(f"[{datetime.now()}] Failed to get file info: {response.text}")
                return None

            data = response.json()
            if not data.get("ok"):
                print(f"[{datetime.now()}] Telegram API error: {data}")
                return None

            file_path = data["result"]["file_path"]

            # Step 2: Download the actual file
            download_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            file_response = await client.get(download_url, timeout=60)

            if file_response.status_code != 200:
                print(f"[{datetime.now()}] Failed to download file: {file_response.status_code}")
                return None

            # Step 3: Save to local temp file
            # Use original extension but sanitize filename
            safe_filename = "".join(c for c in filename if c.isalnum() or c in '._-')
            if not safe_filename:
                safe_filename = f"file_{file_id}"

            local_path = self.temp_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_filename}"
            local_path.write_bytes(file_response.content)

            print(f"[{datetime.now()}] Downloaded file to: {local_path}")
            return str(local_path)

        except Exception as e:
            print(f"[{datetime.now()}] Error downloading file: {e}")
            return None

    async def handle_document(self, client: httpx.AsyncClient, message: dict):
        """
        Handle a document/file upload from Telegram.

        Downloads the file, extracts text content, and generates a response
        about the file contents.

        Args:
            client: httpx async client
            message: Telegram message dict containing document info
        """
        user_id = message.get("from", {}).get("id")
        chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")
        caption = message.get("caption", "")

        # Get user info
        user_first_name = message.get("from", {}).get("first_name", "")
        user_last_name = message.get("from", {}).get("last_name", "")
        user_full_name = f"{user_first_name} {user_last_name}".strip() or "User"
        user_name = self.get_user_name(user_id, user_full_name)

        # Get document info
        doc = message.get("document", {})
        file_id = doc.get("file_id")
        file_name = doc.get("file_name", "unknown")
        mime_type = doc.get("mime_type", "")
        file_size = doc.get("file_size", 0)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Document from {user_name}: {file_name} ({mime_type}, {file_size} bytes)")

        # Check if file type is supported
        if not self.file_extractor.is_supported(file_name, mime_type):
            await self.send_message(
                client, chat_id,
                f"Sorry, I can't process files of type '{Path(file_name).suffix}'. "
                f"I support: PDF, DOCX, TXT, and MD files.",
                reply_to_message_id=message_id
            )
            return

        # Check file size (Telegram limit is 20MB, our limit is in FileExtractor)
        if file_size > self.file_extractor.max_file_size:
            await self.send_message(
                client, chat_id,
                f"Sorry, the file is too large ({file_size / 1024 / 1024:.1f}MB). "
                f"Maximum size is {self.file_extractor.max_file_size / 1024 / 1024:.0f}MB.",
                reply_to_message_id=message_id
            )
            return

        # Send acknowledgment
        await self.send_typing(client, chat_id)
        await self.send_message(
            client, chat_id,
            f"Got it! Processing '{file_name}'...",
            reply_to_message_id=message_id
        )

        # Download file
        local_path = await self.download_telegram_file(client, file_id, file_name)
        if not local_path:
            await self.send_message(
                client, chat_id,
                "Sorry, I couldn't download the file. Please try again.",
                reply_to_message_id=message_id
            )
            return

        try:
            # Extract text
            result = self.file_extractor.extract_text(local_path)

            if not result['success']:
                await self.send_message(
                    client, chat_id,
                    f"Sorry, I couldn't read the file: {result.get('error', 'Unknown error')}",
                    reply_to_message_id=message_id
                )
                return

            extracted_text = result['text']
            if not extracted_text.strip():
                await self.send_message(
                    client, chat_id,
                    "The file appears to be empty or contains no readable text.",
                    reply_to_message_id=message_id
                )
                return

            # Build user message
            if caption:
                user_message = caption
            else:
                user_message = f"I've uploaded a document called '{file_name}'. Can you analyze it and summarize the key points?"

            # Show typing while generating response
            await self.send_typing(client, chat_id)

            # Generate response with file context
            response = self.generate_response(
                user_id,
                user_name,
                user_message,
                file_context=extracted_text
            )

            # Truncation notice
            if result.get('truncated'):
                response += "\n\n_Note: The document was too long and was truncated for analysis._"

            # Send response
            await self.send_message(client, chat_id, response)

            print(f"[{timestamp}] Processed document for {user_name}: {len(extracted_text)} chars extracted")

        finally:
            # Clean up temp file
            try:
                Path(local_path).unlink(missing_ok=True)
            except Exception:
                pass

    def generate_response(self, user_id: int, user_name: str, message: str,
                          file_context: str = None) -> str:
        """
        Generate an AI response using OpenAI with collective knowledge.

        Args:
            user_id: Telegram user ID
            user_name: User's display name
            message: The user's message text
            file_context: Optional extracted text from an uploaded file

        Returns:
            Generated response string
        """

        # Get or initialize conversation history
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        history = self.conversations[user_id]

        # Build enhanced context from collective knowledge
        knowledge_context = self.collective_knowledge.build_context(message)

        # Track what knowledge was used
        self.last_knowledge_used = {
            "timestamp": datetime.now().isoformat(),
            "user": user_name,
            "message_preview": message[:50],
            "context_length": len(knowledge_context),
            "sources": []
        }

        # Check what sources contributed
        if "ICP" in knowledge_context:
            self.last_knowledge_used["sources"].append("icps")
        if "Pure Technology" in knowledge_context:
            self.last_knowledge_used["sources"].append("knowledge_base")
        if "Relevant Learnings" in knowledge_context:
            self.last_knowledge_used["sources"].append("memory_system")
        if file_context:
            self.last_knowledge_used["sources"].append("uploaded_file")

        # Build messages for API call
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": f"You are chatting with {user_name}. Be helpful and conversational."}
        ]

        # Add file context if provided
        if file_context:
            messages.append({
                "role": "system",
                "content": f"**Uploaded Document Content:**\n\n{file_context}\n\n---\nThe user has shared this document. Analyze it and respond to their questions about it."
            })

        # Add dynamic knowledge context if we found relevant info
        if knowledge_context:
            messages.append({
                "role": "system",
                "content": f"**Additional Context for this specific question:**\n\n{knowledge_context}"
            })

        # Add conversation history
        messages.extend(history)

        # Add current message
        messages.append({"role": "user", "content": message})

        try:
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o for quality
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )

            assistant_message = response.choices[0].message.content

            # Update conversation history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": assistant_message})

            # Trim history if too long
            if len(history) > self.max_history * 2:
                self.conversations[user_id] = history[-self.max_history * 2:]

            return assistant_message

        except Exception as e:
            print(f"[{datetime.now()}] OpenAI API error: {e}")
            return f"Sorry, I encountered an error generating a response. Please try again in a moment. (Error: {type(e).__name__})"

    def handle_learn_command(self, user_name: str, learning_content: str) -> dict:
        """
        Handle /learn command by recording a learning to collective memory.

        Args:
            user_name: Name of the user recording the learning
            learning_content: The learning content to record

        Returns:
            Dict with 'success', 'topic', and 'filepath' or 'error'
        """
        try:
            # Auto-generate topic from first few words
            topic_words = learning_content.split()[:5]
            topic = "-".join(topic_words).lower()

            # Record the learning
            filepath = self.collective_knowledge.record_learning(
                topic=topic,
                content=learning_content,
                tags=["telegram-learned", "marketing", "team-insight"],
                learning_type="technique",
                user_name=user_name
            )

            return {
                "success": True,
                "topic": topic,
                "filepath": filepath
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def should_respond_to_group_message(self, message: dict) -> bool:
        """Check if bot should respond to a group message"""
        text = message.get("text", "").lower()

        # Always respond to replies to the bot
        reply_to = message.get("reply_to_message", {})
        if reply_to.get("from", {}).get("username") == self.bot_username.replace("@", ""):
            return True

        # Check for trigger phrases
        for trigger in self.triggers:
            if trigger.lower() in text:
                return True

        return False

    def extract_question_from_trigger(self, text: str) -> str:
        """Remove trigger phrase from message to get the actual question"""
        lower_text = text.lower()
        for trigger in self.triggers:
            lower_trigger = trigger.lower()
            if lower_trigger in lower_text:
                # Find and remove the trigger
                idx = lower_text.find(lower_trigger)
                text = text[:idx] + text[idx + len(trigger):]

        return text.strip()

    async def handle_message(self, client: httpx.AsyncClient, message: dict):
        """Handle an incoming message"""
        user_id = message.get("from", {}).get("id")
        chat_id = message.get("chat", {}).get("id")
        chat_type = message.get("chat", {}).get("type", "private")
        text = message.get("text", "")
        message_id = message.get("message_id")

        # Get user info
        user_first_name = message.get("from", {}).get("first_name", "")
        user_last_name = message.get("from", {}).get("last_name", "")
        user_full_name = f"{user_first_name} {user_last_name}".strip() or "User"
        username = message.get("from", {}).get("username", "")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Message from {user_full_name} (@{username}, ID:{user_id}): {text[:100]}...")

        # === AUTHORIZATION CHECK WITH SECRET PHRASE ===
        if not self.is_authorized(user_id):
            # Check if this message IS the secret phrase
            security_config = self.config.get("security", {})
            secret_phrase = security_config.get("secret_phrase", "").lower()

            if secret_phrase and text.strip().lower() == secret_phrase:
                # Grant access!
                print(f"[{timestamp}] ACCESS GRANTED via secret phrase: {user_full_name} (@{username}, ID:{user_id})")

                # Add to authorized users
                self.authorized_users[user_id] = {
                    "name": user_full_name,
                    "telegram_handle": f"@{username}" if username else "",
                    "role": "team",
                    "admin": False,
                    "added_via": "secret_phrase",
                    "added_date": timestamp
                }

                # Save to config file
                self.save_config()

                success_msg = security_config.get("success_message",
                    "Access granted! Welcome to Pure Brain AI. How can I help you today?")
                await self.send_message(client, chat_id, success_msg, reply_to_message_id=message_id)
                return

            # Not authorized and didn't provide correct phrase
            print(f"[{timestamp}] UNAUTHORIZED: {user_full_name} (@{username}, ID:{user_id})")

            unauthorized_msg = security_config.get("unauthorized_message",
                "This bot is private. Please provide the access code to continue.")
            await self.send_message(client, chat_id, unauthorized_msg, reply_to_message_id=message_id)
            return

        # Get authorized user's name from config
        user_name = self.get_user_name(user_id, user_full_name)

        # === HANDLE COMMANDS ===
        if text.startswith("/"):
            await self.handle_command(client, chat_id, user_id, user_name, text, message_id)
            return

        # === GROUP MESSAGE HANDLING ===
        if chat_type in ["group", "supergroup"]:
            if not self.should_respond_to_group_message(message):
                return  # Don't respond unless triggered

            # Extract the actual question
            text = self.extract_question_from_trigger(text)
            if not text:
                await self.send_message(
                    client, chat_id,
                    "Hi! How can I help? Just ask me anything about marketing, content, or PMG strategy.",
                    reply_to_message_id=message_id
                )
                return

        # === GENERATE AI RESPONSE ===
        if not text.strip():
            return  # Ignore empty messages

        # Log the user message to persistent storage
        self.conversation_logger.log_user_message(
            user_id=user_id,
            user_name=user_full_name,
            username=username,
            message=text,
            chat_id=chat_id,
            chat_type=chat_type,
            message_id=message_id
        )

        # Show typing indicator
        await self.send_typing(client, chat_id)

        # Generate response
        response = self.generate_response(user_id, user_name, text)

        # Log the bot response to persistent storage
        self.conversation_logger.log_bot_response(
            user_id=user_id,
            response=response,
            chat_id=chat_id,
            model="gpt-4o",
            knowledge_sources=self.last_knowledge_used.get("sources", [])
        )

        # Send response
        await self.send_message(client, chat_id, response, reply_to_message_id=message_id if chat_type != "private" else None)

        print(f"[{timestamp}] Responded to {user_name} ({len(response)} chars)")

    async def handle_command(self, client: httpx.AsyncClient, chat_id: int,
                            user_id: int, user_name: str, text: str, message_id: int):
        """Handle bot commands"""
        command = text.split()[0].lower()
        args = text.split()[1:] if len(text.split()) > 1 else []

        if command == "/start":
            await self.send_message(
                client, chat_id,
                f"Hey {user_name}! I'm Pure Brain AI, the marketing team assistant for PMG.\n\n"
                "I can help with:\n"
                "- Content creation and ideation\n"
                "- Campaign planning\n"
                "- Marketing strategy\n"
                "- Competitor analysis\n"
                "- LinkedIn content\n"
                "- And more!\n\n"
                "Just send me a message with what you need help with."
            )

        elif command == "/help":
            await self.send_message(
                client, chat_id,
                "**Pure Brain AI Commands**\n\n"
                "/start - Introduction\n"
                "/help - This message\n"
                "/clear - Clear conversation history\n"
                "/icps - Show ICP summaries (Megan & David)\n"
                "/pillars - Show the 7 Pillars\n"
                "/status - Bot status (includes knowledge sync info)\n\n"
                "**Collective Intelligence**\n"
                "/learn <insight> - Record a learning to collective memory\n"
                "/ask_collective <topic> - Search collective knowledge\n"
                "/knowledge - Show knowledge sources status\n\n"
                "**AI-CIV Infrastructure** (Full Access)\n"
                "/collective - Overview of the AI collective\n"
                "/agents [search] - List/search specialist agents\n"
                "/hub - Communications hub status\n"
                "/skills [search] - List/search available skills\n\n"
                "**Admin Commands**\n"
                "/sync - Refresh knowledge from collective\n"
                "/adduser <id> <name> - Add authorized user\n\n"
                "**In Groups**\n"
                f"Mention me with {', '.join(self.triggers[:3])} or reply to my messages."
            )

        elif command == "/clear":
            if user_id in self.conversations:
                self.conversations[user_id] = []
            await self.send_message(
                client, chat_id,
                "Conversation history cleared. Fresh start!"
            )

        elif command == "/icps":
            await self.send_message(
                client, chat_id,
                "**PMG Ideal Client Profiles**\n\n"
                "**Megan Patel** (Brand Marketing Manager)\n"
                "- Mid-size CPG ($50M-$500M)\n"
                "- Wants to differentiate and create memorable experiences\n"
                "- Pain: Traditional ads feel like shouting into void\n"
                "- Language: 'We need to stand out'\n\n"
                "**David Brown** (VP of Growth / CMO)\n"
                "- Growth-stage ($100M-$1B)\n"
                "- Focused on CAC/LTV, scalable systems\n"
                "- Pain: Board wants efficiency AND growth\n"
                "- Language: 'What's the ROI? How does this scale?'"
            )

        elif command == "/pillars":
            await self.send_message(
                client, chat_id,
                "**The 7 Pillars of Value**\n\n"
                "1. **Integrity** - Walk the talk, use own methods\n"
                "2. **Accountability** - Own outcomes, no excuses\n"
                "3. **Transparency** - Open book policy\n"
                "4. **Growth** - Progression, not perfection\n"
                "5. **Innovation** - Always room for improvement\n"
                "6. **Persistence** - Giving up is the only real failure\n"
                "7. **Love** - Employees are family"
            )

        elif command == "/status":
            # Build knowledge sync status
            if self.synced_knowledge:
                kb_status = "Loaded"
                sync_time = self.synced_knowledge.get("last_synced", "Unknown")
                version = self.synced_knowledge.get("version", "Unknown")
                icp_count = len(self.synced_knowledge.get("icps", {}))
                learning_count = len(self.synced_knowledge.get("learnings", []))
            else:
                kb_status = "Not loaded"
                sync_time = "N/A"
                version = "N/A"
                icp_count = 0
                learning_count = 0

            await self.send_message(
                client, chat_id,
                f"**Pure Brain AI Status**\n\n"
                f"Bot: @{self.bot_username}\n"
                f"Authorized users: {len(self.authorized_users)}\n"
                f"Active conversations: {len(self.conversations)}\n"
                f"Model: GPT-4o\n"
                f"Status: Online\n\n"
                f"**Knowledge Sync**\n"
                f"Status: {kb_status}\n"
                f"Version: {version}\n"
                f"Last synced: {sync_time}\n"
                f"ICPs loaded: {icp_count}\n"
                f"Learnings: {learning_count}"
            )

        elif command == "/sync" and self.authorized_users.get(user_id, {}).get("admin"):
            # Admin command to sync knowledge
            await self.send_message(client, chat_id, "Syncing knowledge...")
            try:
                # Import and run sync
                from tools.sync_marketing_bot_knowledge import sync_knowledge
                result = sync_knowledge(project_root=str(self.project_root))

                # Reload knowledge
                self.synced_knowledge = self.load_synced_knowledge()
                self.system_prompt = self.load_agent_context()

                await self.send_message(
                    client, chat_id,
                    f"**Knowledge sync complete!**\n\n"
                    f"Knowledge Base: {'Loaded' if result['stats']['knowledge_base_loaded'] else 'Not found'}\n"
                    f"ICPs: {result['stats']['icp_count']}\n"
                    f"Learnings: {result['stats']['learning_count']}\n"
                    f"Timestamp: {result['timestamp']}"
                )
            except Exception as e:
                await self.send_message(
                    client, chat_id,
                    f"Sync failed: {e}"
                )

        elif command == "/adduser" and self.authorized_users.get(user_id, {}).get("admin"):
            # Admin command to add users
            if len(args) >= 2:
                try:
                    new_user_id = int(args[0])
                    new_user_name = " ".join(args[1:])
                    self.add_authorized_user(new_user_id, new_user_name)
                    await self.send_message(
                        client, chat_id,
                        f"Added {new_user_name} (ID: {new_user_id}) to authorized users."
                    )
                except ValueError:
                    await self.send_message(
                        client, chat_id,
                        "Usage: /adduser <user_id> <name>\nExample: /adduser 123456789 Nathan Smith"
                    )
            else:
                await self.send_message(
                    client, chat_id,
                    "Usage: /adduser <user_id> <name>\nExample: /adduser 123456789 Nathan Smith"
                )

        elif command == "/learn":
            # Record a learning to collective memory
            if not args:
                await self.send_message(
                    client, chat_id,
                    "**Record a Learning**\n\n"
                    "Usage: /learn <your insight or discovery>\n\n"
                    "Example: /learn LinkedIn posts with storytelling perform 2x better than tips\n\n"
                    "This saves your insight to the collective memory for future reference."
                )
            else:
                learning_content = " ".join(args)
                try:
                    # Auto-generate topic from first few words
                    topic_words = learning_content.split()[:5]
                    topic = "-".join(topic_words).lower()

                    # Record the learning
                    filepath = self.collective_knowledge.record_learning(
                        topic=topic,
                        content=learning_content,
                        tags=["telegram-learned", "marketing", "team-insight"],
                        learning_type="technique",
                        user_name=user_name
                    )

                    await self.send_message(
                        client, chat_id,
                        f"**Learning recorded!**\n\n"
                        f"Topic: {topic}\n"
                        f"Source: {user_name}\n"
                        f"Saved to collective memory for future reference."
                    )
                except Exception as e:
                    await self.send_message(
                        client, chat_id,
                        f"Failed to record learning: {e}"
                    )

        elif command == "/ask_collective":
            # Explicitly search collective memory
            if not args:
                await self.send_message(
                    client, chat_id,
                    "**Search Collective Knowledge**\n\n"
                    "Usage: /ask_collective <search term>\n\n"
                    "Example: /ask_collective linkedin strategy\n\n"
                    "This searches the collective memory for relevant learnings."
                )
            else:
                search_query = " ".join(args)
                try:
                    # Search memory
                    results = self.collective_knowledge.search_memory(search_query, limit=5)

                    if not results:
                        await self.send_message(
                            client, chat_id,
                            f"No learnings found for '{search_query}'.\n\n"
                            "The collective memory is still growing. Try a broader term or record new learnings with /learn."
                        )
                    else:
                        response = f"**Collective Knowledge: {search_query}**\n\n"
                        for i, mem in enumerate(results, 1):
                            response += f"**{i}. {mem['topic']}** ({mem.get('date', 'unknown')})\n"
                            response += f"{mem['content'][:300]}...\n\n"

                        await self.send_message(client, chat_id, response)
                except Exception as e:
                    await self.send_message(
                        client, chat_id,
                        f"Search failed: {e}"
                    )

        elif command == "/knowledge":
            # Show what knowledge sources are active
            icps = self.collective_knowledge.load_icps()
            kb = self.collective_knowledge.load_knowledge_base()

            # Search for recent learnings
            recent = self.collective_knowledge.search_memory("marketing", limit=3)

            await self.send_message(
                client, chat_id,
                f"**Collective Knowledge Status**\n\n"
                f"**Knowledge Base**: {'Loaded' if kb else 'Not found'} ({len(kb)} chars)\n"
                f"**ICPs Loaded**: {len(icps)}\n"
                f"**Recent Learnings**: {len(recent)}\n\n"
                f"**Last Response Used**:\n"
                f"Sources: {', '.join(self.last_knowledge_used.get('sources', ['none']))}\n"
                f"Context size: {self.last_knowledge_used.get('context_length', 0)} chars"
            )

        elif command == "/agents":
            # List available agents in the collective
            agents = self.aiciv_infrastructure.list_agents()
            if args:
                # Search for specific agent
                query = " ".join(args)
                matching = self.aiciv_infrastructure.search_agents(query)
                if matching:
                    response = f"**Agents matching '{query}'**:\n\n"
                    for agent in matching[:10]:
                        info = self.aiciv_infrastructure.get_agent_info(agent)
                        desc = info.get("description", "")[:80] if info else ""
                        response += f"- **{agent}**: {desc}...\n"
                else:
                    response = f"No agents found matching '{query}'."
            else:
                response = f"**AI-CIV Collective Agents** ({len(agents)} total)\n\n"
                response += "Key specialists:\n"
                key_agents = ["web-researcher", "security-auditor", "pattern-detector",
                            "doc-synthesizer", "test-architect", "human-liaison"]
                for agent in key_agents:
                    if agent in agents:
                        info = self.aiciv_infrastructure.get_agent_info(agent)
                        desc = info.get("description", "")[:60] if info else ""
                        response += f"- **{agent}**: {desc}...\n"
                response += f"\nUse /agents <search term> to find specific agents."
            await self.send_message(client, chat_id, response)

        elif command == "/hub":
            # Show comms hub status
            rooms = self.aiciv_infrastructure.list_hub_rooms()
            collectives = self.aiciv_infrastructure.get_sister_collectives()

            response = "**AI-CIV Communications Hub**\n\n"
            response += f"**Rooms**: {', '.join(rooms) if rooms else 'None found'}\n\n"
            response += "**Sister Collectives**:\n"
            for coll in collectives:
                response += f"- **{coll['name']}**: {coll['description']}\n"

            # Get recent messages
            recent = self.aiciv_infrastructure.get_hub_messages("partnerships", limit=3)
            if recent:
                response += "\n**Recent Messages**:\n"
                for msg in recent[:3]:
                    author = msg.get("author", {}).get("display", msg.get("author", {}).get("id", "unknown"))
                    summary = msg.get("summary", "")[:40]
                    response += f"- {author}: {summary}...\n"
            else:
                response += "\nNo recent messages in partnerships room."

            await self.send_message(client, chat_id, response)

        elif command == "/skills":
            # List available skills
            skills = self.aiciv_infrastructure.list_skills()
            if args:
                # Search for specific skill
                query = " ".join(args).lower()
                matching = [s for s in skills if query in s.lower()]
                if matching:
                    response = f"**Skills matching '{query}'**:\n\n"
                    for skill in matching[:15]:
                        response += f"- {skill}\n"
                else:
                    response = f"No skills found matching '{query}'."
            else:
                response = f"**AI-CIV Skills Library** ({len(skills)} total)\n\n"
                response += "Key skills:\n"
                key_skills = ["tdd", "verification-before-completion", "memory-first-protocol",
                            "comms-hub-operations", "parallel-research", "linkedin-content-pipeline"]
                for skill in key_skills:
                    if skill in skills:
                        response += f"- {skill}\n"
                response += f"\nUse /skills <search term> to find specific skills."
            await self.send_message(client, chat_id, response)

        elif command == "/collective":
            # Show full collective status
            agents = self.aiciv_infrastructure.list_agents()
            skills = self.aiciv_infrastructure.list_skills()
            rooms = self.aiciv_infrastructure.list_hub_rooms()
            collectives = self.aiciv_infrastructure.get_sister_collectives()

            response = "**AI-CIV Collective Status**\n\n"
            response += f"**Agents**: {len(agents)} specialist agents\n"
            response += f"**Skills**: {len(skills)} skills in library\n"
            response += f"**Hub Rooms**: {len(rooms)} active rooms\n"
            response += f"**Sister Collectives**: {len(collectives)}\n\n"
            response += "Commands:\n"
            response += "- /agents - List agents\n"
            response += "- /hub - Hub status\n"
            response += "- /skills - Skills library\n"
            response += "\nI have FULL ACCESS to query any of these systems."

            await self.send_message(client, chat_id, response)

        else:
            await self.send_message(
                client, chat_id,
                f"Unknown command: {command}\n\nUse /help to see available commands."
            )

    async def poll_updates(self, client: httpx.AsyncClient):
        """Poll for incoming Telegram messages"""
        while True:
            updates = await self.get_updates(client)

            for update in updates:
                self.last_update_id = update.get("update_id", self.last_update_id)

                message = update.get("message")
                if message:
                    # Check authorization first for any message type
                    user_id = message.get("from", {}).get("id")

                    if message.get("document") and self.is_authorized(user_id):
                        # Handle document upload
                        await self.handle_document(client, message)
                    elif message.get("text"):
                        # Handle text message (includes authorization check)
                        await self.handle_message(client, message)

            await asyncio.sleep(1)

    async def run(self):
        """Main loop"""
        print(f"[{datetime.now()}] PureBrain AI Bot starting...")
        print(f"[{datetime.now()}] Bot: @{self.bot_username}")
        print(f"[{datetime.now()}] Authorized users: {list(self.authorized_users.keys())}")
        print(f"[{datetime.now()}] Group triggers: {self.triggers}")

        async with httpx.AsyncClient() as client:
            # Send startup notification to default chat
            default_chat = self.config.get("default_chat_id")
            if default_chat:
                await self.send_message(
                    client, int(default_chat),
                    f"Pure Brain AI online.\n"
                    f"Authorized users: {len(self.authorized_users)}\n"
                    f"Ready to help the marketing team!"
                )

            # Start polling
            await self.poll_updates(client)


def main():
    bridge = PureBrainBridge()

    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] PureBrain Bot stopped by user")
    except Exception as e:
        print(f"[{datetime.now()}] PureBrain Bot error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
