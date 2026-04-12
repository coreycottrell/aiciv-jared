"""
ICP (Ideal Customer Profile) Configuration Management

Loads and manages ICP configurations from YAML files.
Supports multiple ICPs with different target criteria.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml


# Path to ICP configuration directory
ICP_DIR = Path(__file__).parent / "icps"


def load_icp_config(icp_name: str) -> Dict:
    """
    Load ICP configuration from YAML file.

    Args:
        icp_name: Name of the ICP (e.g., "megan_patel", "david_brown")

    Returns:
        Dict containing ICP configuration

    Raises:
        ValueError: If ICP not found
    """
    icp_file = ICP_DIR / f"{icp_name}.yaml"

    if not icp_file.exists():
        available = list_icps()
        raise ValueError(
            f"ICP '{icp_name}' not found. Available ICPs: {available}"
        )

    with open(icp_file, "r") as f:
        config = yaml.safe_load(f)

    return config


def list_icps() -> List[str]:
    """
    List all available ICP configurations.

    Returns:
        List of ICP names (without .yaml extension)
    """
    if not ICP_DIR.exists():
        return []

    icps = []
    for f in ICP_DIR.glob("*.yaml"):
        icps.append(f.stem)

    return sorted(icps)


def get_all_icps() -> Dict[str, Dict]:
    """
    Load all ICP configurations.

    Returns:
        Dict mapping ICP name to config
    """
    all_icps = {}
    for icp_name in list_icps():
        all_icps[icp_name] = load_icp_config(icp_name)
    return all_icps


def get_icp_display_name(icp_name: str) -> str:
    """
    Get human-readable display name for ICP.

    Args:
        icp_name: Internal ICP name (e.g., "megan_patel")

    Returns:
        Display name (e.g., "Megan Patel")
    """
    return icp_name.replace("_", " ").title()


def save_icp_config(icp_name: str, config: Dict) -> None:
    """
    Save ICP configuration to YAML file.

    Args:
        icp_name: Name of the ICP
        config: Configuration dict to save
    """
    ICP_DIR.mkdir(parents=True, exist_ok=True)
    icp_file = ICP_DIR / f"{icp_name}.yaml"

    with open(icp_file, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)


def update_icp_exclusions(icp_name: str, exclusions: Dict) -> None:
    """
    Update exclusions in ICP config based on learnings.

    Args:
        icp_name: Name of the ICP
        exclusions: Dict with "titles", "industries", "keywords" lists
    """
    config = load_icp_config(icp_name)

    # Merge exclusions (avoid duplicates)
    if "exclusions" not in config:
        config["exclusions"] = {"titles": [], "industries": [], "keywords": []}

    for key in ["titles", "industries", "keywords"]:
        if key in exclusions:
            existing = set(config["exclusions"].get(key, []))
            new_items = set(exclusions.get(key, []))
            config["exclusions"][key] = sorted(list(existing | new_items))

    save_icp_config(icp_name, config)


if __name__ == "__main__":
    # Test loading
    print("Available ICPs:", list_icps())

    for icp_name in list_icps():
        print(f"\n{get_icp_display_name(icp_name)}:")
        config = load_icp_config(icp_name)
        print(f"  Titles: {len(config.get('target_titles', []))}")
        print(f"  Industries: {len(config.get('target_industries', []))}")
        print(f"  Keywords: {len(config.get('keywords_in_profile', []))}")
