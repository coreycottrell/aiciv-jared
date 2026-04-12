#!/usr/bin/env python3
"""
Knowledge Base Sync Tool for AI-CIV Agents

Processes files from Google Drive folders and generates knowledge bases
for specialist agents.

Usage:
    python3 tools/sync_knowledge.py                    # Sync all agents
    python3 tools/sync_knowledge.py linkedin-specialist # Sync specific agent
    python3 tools/sync_knowledge.py --list             # List mappings
    python3 tools/sync_knowledge.py --status           # Show sync status
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import hashlib

# Optional imports for file processing
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class KnowledgeSync:
    def __init__(self, config_path: str = None):
        self.base_dir = Path("/home/jared/projects/AI-CIV/aether")
        self.config_path = config_path or self.base_dir / "config" / "agent_knowledge_mapping.json"
        self.config = self._load_config()
        self.gdrive_base = Path(self.config["gdrive_base"])
        self.output_dir = Path(self.config["knowledge_base_output"])
        self.state_file = self.base_dir / ".gdrive_sync_state.json"
        self.state = self._load_state()

    def _load_config(self) -> dict:
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _load_state(self) -> dict:
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {"last_sync": {}, "file_hashes": {}}

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)

    def _file_hash(self, filepath: Path) -> str:
        """Get MD5 hash of file for change detection."""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _should_process(self, filepath: Path) -> bool:
        """Check if file should be processed based on extension."""
        suffix = filepath.suffix.lower()
        if suffix in self.config["file_processors"]:
            return True
        for pattern in self.config["ignore_patterns"]:
            if filepath.match(pattern):
                return False
        return False

    def _extract_text_pdf(self, filepath: Path) -> str:
        """Extract text from PDF."""
        if not HAS_PYPDF2:
            return f"[PDF file - install PyPDF2 to extract: {filepath.name}]"

        try:
            text_parts = []
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return "\n\n".join(text_parts) if text_parts else f"[PDF with no extractable text: {filepath.name}]"
        except Exception as e:
            return f"[Error reading PDF {filepath.name}: {str(e)}]"

    def _extract_text_docx(self, filepath: Path) -> str:
        """Extract text from DOCX."""
        if not HAS_DOCX:
            return f"[DOCX file - install python-docx to extract: {filepath.name}]"

        try:
            doc = Document(filepath)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs) if paragraphs else f"[DOCX with no text: {filepath.name}]"
        except Exception as e:
            return f"[Error reading DOCX {filepath.name}: {str(e)}]"

    def _extract_text_xlsx(self, filepath: Path) -> str:
        """Extract text from Excel."""
        if not HAS_PANDAS:
            return f"[Excel file - install pandas to extract: {filepath.name}]"

        try:
            df = pd.read_excel(filepath, sheet_name=None)
            parts = []
            for sheet_name, sheet_df in df.items():
                parts.append(f"## Sheet: {sheet_name}\n")
                parts.append(sheet_df.to_string())
            return "\n\n".join(parts)
        except Exception as e:
            return f"[Error reading Excel {filepath.name}: {str(e)}]"

    def _extract_text_html(self, filepath: Path) -> str:
        """Extract text from HTML."""
        if not HAS_BS4:
            return f"[HTML file - install beautifulsoup4 to extract: {filepath.name}]"

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                return soup.get_text(separator='\n', strip=True)
        except Exception as e:
            return f"[Error reading HTML {filepath.name}: {str(e)}]"

    def _extract_text_plain(self, filepath: Path) -> str:
        """Read plain text file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"[Error reading {filepath.name}: {str(e)}]"

    def _extract_text(self, filepath: Path) -> str:
        """Extract text based on file type."""
        suffix = filepath.suffix.lower()

        if suffix == '.pdf':
            return self._extract_text_pdf(filepath)
        elif suffix == '.docx':
            return self._extract_text_docx(filepath)
        elif suffix == '.doc':
            return f"[DOC file - convert to DOCX for extraction: {filepath.name}]"
        elif suffix in ['.xlsx', '.xls']:
            return self._extract_text_xlsx(filepath)
        elif suffix == '.html':
            return self._extract_text_html(filepath)
        elif suffix == '.csv':
            if HAS_PANDAS:
                try:
                    df = pd.read_csv(filepath)
                    return df.to_string()
                except:
                    return self._extract_text_plain(filepath)
            return self._extract_text_plain(filepath)
        else:
            return self._extract_text_plain(filepath)

    def _summarize_content(self, content: str, max_chars: int = 50000) -> str:
        """Truncate content if too long, preserving structure."""
        if len(content) <= max_chars:
            return content

        # Try to cut at a sensible point
        truncated = content[:max_chars]
        last_para = truncated.rfind('\n\n')
        if last_para > max_chars * 0.8:
            truncated = truncated[:last_para]

        return truncated + f"\n\n[... Content truncated at {max_chars} characters ...]"

    def process_folder(self, mapping: dict) -> dict:
        """Process all files in a folder and return knowledge content."""
        folder_path = self.gdrive_base / mapping["folder"]
        agent = mapping["agent"]

        if not folder_path.exists():
            return {
                "agent": agent,
                "folder": mapping["folder"],
                "status": "folder_not_found",
                "files_processed": 0,
                "content": ""
            }

        files_processed = []
        content_parts = []

        # Walk through folder recursively
        for filepath in sorted(folder_path.rglob("*")):
            if not filepath.is_file():
                continue

            if not self._should_process(filepath):
                continue

            # Check if file has changed
            file_key = str(filepath.relative_to(self.gdrive_base))
            current_hash = self._file_hash(filepath)

            # Extract content
            relative_path = filepath.relative_to(folder_path)
            content = self._extract_text(filepath)

            if content and not content.startswith("["):
                content_parts.append(f"### File: {relative_path}\n\n{content}")
                files_processed.append(str(relative_path))

                # Update hash
                self.state["file_hashes"][file_key] = current_hash

        return {
            "agent": agent,
            "folder": mapping["folder"],
            "status": "success",
            "files_processed": len(files_processed),
            "files": files_processed,
            "content": "\n\n---\n\n".join(content_parts)
        }

    def generate_knowledge_base(self, agent: str, results: list) -> str:
        """Generate markdown knowledge base for an agent."""
        timestamp = datetime.now().isoformat()

        kb_content = f"""# Knowledge Base: {agent}

**Generated**: {timestamp}
**Source Folders**: {len(results)}
**Auto-sync**: Every {self.config['sync_interval_hours']} hours

---

## Overview

This knowledge base is automatically generated from Google Drive training folders.
It contains processed content from documents, PDFs, and other text sources.

**To manually update**: `python3 tools/sync_knowledge.py {agent}`

---

"""

        total_files = 0
        for result in results:
            if result["status"] == "success" and result["content"]:
                total_files += result["files_processed"]
                kb_content += f"""## Source: {result['folder']}

**Files Processed**: {result['files_processed']}

{result['content']}

---

"""

        kb_content += f"""
## Sync Metadata

- **Total Files**: {total_files}
- **Last Sync**: {timestamp}
- **Next Scheduled**: Every {self.config['sync_interval_hours']} hours
"""

        return self._summarize_content(kb_content, max_chars=100000)

    def sync_agent(self, agent_name: str) -> dict:
        """Sync knowledge base for a specific agent."""
        # Find all mappings for this agent
        mappings = [m for m in self.config["mappings"] if m["agent"] == agent_name]

        if not mappings:
            return {"status": "error", "message": f"No mappings found for agent: {agent_name}"}

        results = []
        for mapping in mappings:
            print(f"  Processing: {mapping['folder']}")
            result = self.process_folder(mapping)
            results.append(result)

        # Generate knowledge base
        kb_content = self.generate_knowledge_base(agent_name, results)

        # Write to file
        kb_file = self.output_dir / f"{agent_name}-kb.md"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(kb_file, 'w', encoding='utf-8') as f:
            f.write(kb_content)

        # Update state
        self.state["last_sync"][agent_name] = datetime.now().isoformat()
        self._save_state()

        total_files = sum(r["files_processed"] for r in results)
        return {
            "status": "success",
            "agent": agent_name,
            "files_processed": total_files,
            "output_file": str(kb_file)
        }

    def sync_all(self) -> list:
        """Sync all agents."""
        # Get unique agents
        agents = list(set(m["agent"] for m in self.config["mappings"]))

        results = []
        for agent in agents:
            print(f"\nSyncing {agent}...")
            result = self.sync_agent(agent)
            results.append(result)
            print(f"  -> {result['files_processed']} files processed")

        return results

    def list_mappings(self):
        """Display all folder-to-agent mappings."""
        print("\n=== Agent Knowledge Mappings ===\n")
        for m in self.config["mappings"]:
            status = "EXISTS" if (self.gdrive_base / m["folder"]).exists() else "MISSING"
            last_sync = self.state["last_sync"].get(m["agent"], "Never")
            print(f"Agent: {m['agent']}")
            print(f"  Folder: {m['folder']}")
            print(f"  Description: {m['description']}")
            print(f"  Priority: {m['priority']}")
            print(f"  Status: {status}")
            print(f"  Last Sync: {last_sync}")
            print()

    def show_status(self):
        """Show sync status for all agents."""
        print("\n=== Knowledge Base Sync Status ===\n")
        print(f"Sync Interval: Every {self.config['sync_interval_hours']} hours\n")

        agents = list(set(m["agent"] for m in self.config["mappings"]))
        for agent in sorted(agents):
            kb_file = self.output_dir / f"{agent}-kb.md"
            exists = kb_file.exists()
            size = kb_file.stat().st_size if exists else 0
            last_sync = self.state["last_sync"].get(agent, "Never")

            print(f"{agent}:")
            print(f"  Knowledge Base: {'EXISTS' if exists else 'NOT GENERATED'}")
            if exists:
                print(f"  Size: {size / 1024:.1f} KB")
            print(f"  Last Sync: {last_sync}")
            print()


def main():
    args = sys.argv[1:]

    sync = KnowledgeSync()

    if not args:
        # Sync all agents
        print("=== Knowledge Base Sync - All Agents ===")
        results = sync.sync_all()
        print("\n=== Summary ===")
        for r in results:
            print(f"  {r['agent']}: {r['files_processed']} files -> {r.get('output_file', 'N/A')}")

    elif args[0] == "--list":
        sync.list_mappings()

    elif args[0] == "--status":
        sync.show_status()

    elif args[0] == "--help":
        print(__doc__)

    else:
        # Sync specific agent
        agent_name = args[0]
        print(f"=== Syncing Knowledge Base: {agent_name} ===")
        result = sync.sync_agent(agent_name)
        if result["status"] == "success":
            print(f"\nSuccess! {result['files_processed']} files processed")
            print(f"Output: {result['output_file']}")
        else:
            print(f"\nError: {result['message']}")


if __name__ == "__main__":
    main()
