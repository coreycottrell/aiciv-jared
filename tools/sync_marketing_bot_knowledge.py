#!/usr/bin/env python3
"""
Marketing Bot Knowledge Sync

Syncs knowledge from the Aether collective memory system to the
@PureBrainAI_bot Telegram bot, keeping it updated with:
- Pure Technology knowledge base
- Latest ICP configurations (Megan Patel, David Brown)
- Marketing team learnings
- Campaign insights and strategies

Usage:
    # Manual sync
    python3 tools/sync_marketing_bot_knowledge.py

    # Can be added to cron for daily sync:
    # 0 6 * * * cd /home/jared/projects/AI-CIV/aether && python3 tools/sync_marketing_bot_knowledge.py

Author: refactoring-specialist
Version: 1.0.0
Date: 2026-02-04
"""

import json
import yaml
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


def get_project_root() -> str:
    """Get the project root directory."""
    return str(Path(__file__).parent.parent)


class KnowledgeCompiler:
    """
    Compiles knowledge from various sources in the Aether collective
    into a synced knowledge file for the marketing bot.
    """

    VERSION = "1.0.0"

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the knowledge compiler.

        Args:
            project_root: Path to project root (defaults to auto-detect)
        """
        if project_root is None:
            project_root = get_project_root()

        self.project_root = Path(project_root)
        self.memory_dir = self.project_root / ".claude" / "memory"
        self.icp_dir = self.project_root / "tools" / "intent_engine" / "icps"
        self.config_dir = self.project_root / "config"

        # Ensure directories exist
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.icp_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_knowledge_base(self) -> Optional[str]:
        """
        Load the pure-technology-knowledge-base.md file.

        Returns:
            Content of knowledge base or None if not found.
        """
        kb_path = self.memory_dir / "pure-technology-knowledge-base.md"

        if not kb_path.exists():
            return None

        return kb_path.read_text(encoding="utf-8")

    def load_icps(self) -> Dict[str, Dict]:
        """
        Load all ICP (Ideal Customer Profile) YAML files.

        Returns:
            Dictionary mapping persona name to ICP configuration.
        """
        icps = {}

        if not self.icp_dir.exists():
            return icps

        for yaml_file in self.icp_dir.glob("*.yaml"):
            try:
                content = yaml_file.read_text(encoding="utf-8")
                data = yaml.safe_load(content)

                if data and "persona" in data:
                    persona_name = data["persona"]
                    icps[persona_name] = data
            except Exception as e:
                print(f"Warning: Failed to load ICP {yaml_file}: {e}")

        return icps

    def load_marketing_learnings(self) -> List[Dict[str, Any]]:
        """
        Load marketing-team agent learnings from memory.

        Returns:
            List of learning entries with metadata and content.
        """
        learnings = []
        learnings_dir = self.memory_dir / "agent-learnings" / "marketing-team"

        if not learnings_dir.exists():
            return learnings

        for md_file in learnings_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")

                # Parse YAML frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        metadata = yaml.safe_load(parts[1])
                        body = parts[2].strip()

                        if metadata:
                            # Convert date to string if it's a date object
                            date_val = metadata.get("date", "")
                            if hasattr(date_val, 'isoformat'):
                                date_val = date_val.isoformat()
                            elif date_val and not isinstance(date_val, str):
                                date_val = str(date_val)

                            learning = {
                                "topic": metadata.get("topic", ""),
                                "type": metadata.get("type", ""),
                                "date": date_val,
                                "tags": metadata.get("tags", []),
                                "confidence": metadata.get("confidence", ""),
                                "content": body,
                                "file": md_file.name
                            }
                            learnings.append(learning)
            except Exception as e:
                print(f"Warning: Failed to load learning {md_file}: {e}")

        # Sort by date (newest first)
        learnings.sort(key=lambda x: x.get("date", ""), reverse=True)

        return learnings

    def load_additional_learnings(self) -> List[Dict[str, Any]]:
        """
        Load relevant learnings from other agents that relate to marketing.

        Returns:
            List of learning entries with marketing relevance.
        """
        learnings = []
        agent_learnings_dir = self.memory_dir / "agent-learnings"

        if not agent_learnings_dir.exists():
            return learnings

        # Agents that might have marketing-relevant learnings
        relevant_agents = ["web-researcher", "linkedin-researcher", "linkedin-writer"]
        marketing_tags = ["marketing", "pmg", "content", "campaign", "linkedin", "icp"]

        for agent_dir in agent_learnings_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            if agent_dir.name == "marketing-team":
                continue  # Already loaded separately

            for md_file in agent_dir.glob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")

                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            metadata = yaml.safe_load(parts[1])
                            body = parts[2].strip()

                            if metadata:
                                tags = metadata.get("tags", [])
                                # Check if marketing-relevant
                                if any(tag in marketing_tags for tag in tags):
                                    # Convert date to string if it's a date object
                                    date_val = metadata.get("date", "")
                                    if hasattr(date_val, 'isoformat'):
                                        date_val = date_val.isoformat()
                                    elif date_val and not isinstance(date_val, str):
                                        date_val = str(date_val)

                                    learning = {
                                        "topic": metadata.get("topic", ""),
                                        "type": metadata.get("type", ""),
                                        "date": date_val,
                                        "tags": tags,
                                        "confidence": metadata.get("confidence", ""),
                                        "content": body,
                                        "file": md_file.name,
                                        "agent": agent_dir.name
                                    }
                                    learnings.append(learning)
                except Exception:
                    continue

        return learnings

    def generate_context_summary(self) -> str:
        """
        Generate a condensed context summary for efficient token usage in prompts.

        Returns:
            A summary string suitable for inclusion in system prompts.
        """
        sections = []

        # Load knowledge base
        kb = self.load_knowledge_base()
        if kb:
            # Extract key sections
            sections.append("## KNOWLEDGE BASE SUMMARY")
            sections.append(kb[:3000] if len(kb) > 3000 else kb)

        # Load ICPs
        icps = self.load_icps()
        if icps:
            sections.append("\n## ICP SUMMARY")
            for persona, data in icps.items():
                titles = data.get("target_titles", [])[:3]
                industries = data.get("target_industries", [])[:3]
                sections.append(f"**{persona}**: Titles: {', '.join(titles)}. Industries: {', '.join(industries)}")

        # Load recent learnings (last 5)
        learnings = self.load_marketing_learnings()[:5]
        if learnings:
            sections.append("\n## RECENT MARKETING LEARNINGS")
            for learning in learnings:
                sections.append(f"- **{learning['topic']}** ({learning['date']}): {learning['content'][:200]}...")

        return "\n".join(sections)

    def compile(self, output_path: Optional[str] = None) -> str:
        """
        Compile all knowledge into a single JSON file.

        Args:
            output_path: Custom output path (defaults to config/marketing_knowledge.json)

        Returns:
            Path to the compiled knowledge file.
        """
        if output_path is None:
            output_path = str(self.config_dir / "marketing_knowledge.json")

        # Gather all knowledge
        knowledge = {
            "version": self.VERSION,
            "last_synced": datetime.now().isoformat(),
            "knowledge_base": self.load_knowledge_base(),
            "icps": self.load_icps(),
            "learnings": self.load_marketing_learnings(),
            "additional_learnings": self.load_additional_learnings(),
            "strategies": self._extract_strategies(),
            "context_summary": self.generate_context_summary()
        }

        # Write to file
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)

        return str(output)

    def _extract_strategies(self) -> Dict[str, Any]:
        """
        Extract strategy-related content from learnings.

        Returns:
            Dictionary of strategy insights.
        """
        strategies = {
            "content_strategies": [],
            "campaign_insights": [],
            "icp_insights": []
        }

        for learning in self.load_marketing_learnings():
            tags = learning.get("tags", [])

            if "content" in tags or "strategy" in tags:
                strategies["content_strategies"].append({
                    "topic": learning["topic"],
                    "date": learning["date"],
                    "summary": learning["content"][:500]
                })

            if "campaign" in tags:
                strategies["campaign_insights"].append({
                    "topic": learning["topic"],
                    "date": learning["date"],
                    "summary": learning["content"][:500]
                })

            if "icp" in tags:
                strategies["icp_insights"].append({
                    "topic": learning["topic"],
                    "date": learning["date"],
                    "summary": learning["content"][:500]
                })

        return strategies


def sync_knowledge(project_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Main sync function - compiles and saves knowledge.

    Args:
        project_root: Optional project root path

    Returns:
        Dictionary with sync results and statistics.
    """
    compiler = KnowledgeCompiler(project_root=project_root)
    output_path = compiler.compile()

    # Gather stats
    kb = compiler.load_knowledge_base()
    icps = compiler.load_icps()
    learnings = compiler.load_marketing_learnings()

    stats = {
        "knowledge_base_loaded": kb is not None,
        "knowledge_base_size": len(kb) if kb else 0,
        "icp_count": len(icps),
        "icp_names": list(icps.keys()),
        "learning_count": len(learnings),
        "additional_learning_count": len(compiler.load_additional_learnings())
    }

    return {
        "path": output_path,
        "timestamp": datetime.now().isoformat(),
        "stats": stats
    }


def main():
    """CLI entry point."""
    print("Marketing Bot Knowledge Sync")
    print("=" * 40)

    try:
        result = sync_knowledge()

        print(f"\nSync completed successfully!")
        print(f"Output: {result['path']}")
        print(f"\nStatistics:")
        print(f"  - Knowledge Base: {'Loaded' if result['stats']['knowledge_base_loaded'] else 'Not Found'}")
        print(f"  - ICPs: {result['stats']['icp_count']} ({', '.join(result['stats']['icp_names'])})")
        print(f"  - Marketing Learnings: {result['stats']['learning_count']}")
        print(f"  - Additional Learnings: {result['stats']['additional_learning_count']}")
        print(f"\nTimestamp: {result['timestamp']}")

    except Exception as e:
        print(f"\nError during sync: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
