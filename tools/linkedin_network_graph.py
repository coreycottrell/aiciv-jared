#!/usr/bin/env python3
"""
LinkedIn Network Graph Visualizer
==================================
Takes a LinkedIn connections CSV export and generates an interactive
HTML network graph using NetworkX + pyvis.

Usage:
    python tools/linkedin_network_graph.py path/to/Connections.csv
    python tools/linkedin_network_graph.py exports/sample_connections.csv

Output:
    exports/linkedin-network-graph.html  (self-contained, interactive)

Author: full-stack-developer agent
Date: 2026-02-19
"""

import sys
import os
import json
import math
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Dependency check with helpful error messages
# ---------------------------------------------------------------------------
try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not installed. Run: venv/bin/pip install pandas")
    sys.exit(1)

try:
    import networkx as nx
except ImportError:
    print("ERROR: networkx not installed. Run: venv/bin/pip install networkx")
    sys.exit(1)

try:
    from pyvis.network import Network
except ImportError:
    print("ERROR: pyvis not installed. Run: venv/bin/pip install pyvis")
    sys.exit(1)

try:
    import community as community_louvain
    LOUVAIN_AVAILABLE = True
except ImportError:
    LOUVAIN_AVAILABLE = False
    print("WARNING: python-louvain not available; falling back to greedy modularity.")

# ---------------------------------------------------------------------------
# Constants — PureBrain brand palette
# ---------------------------------------------------------------------------
BRAND_BLUE   = "#2a93c1"
BRAND_ORANGE = "#f1420b"
BRAND_WHITE  = "#e8f4f8"
DARK_BG      = "#0d1117"

# Colour palette for company clusters (cycles through)
CLUSTER_PALETTE = [
    "#2a93c1",  # brand blue
    "#f1420b",  # brand orange
    "#00d4aa",  # teal
    "#a855f7",  # purple
    "#f59e0b",  # amber
    "#34d399",  # emerald
    "#f472b6",  # pink
    "#60a5fa",  # sky blue
    "#fb923c",  # light orange
    "#a3e635",  # lime
    "#38bdf8",  # light blue
    "#e879f9",  # fuchsia
]

CENTER_NODE_COLOR = "#ffffff"
SOLO_NODE_COLOR   = "#4a5568"  # grey for unconnected individuals


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------

def load_connections(csv_path: str) -> pd.DataFrame:
    """
    Load a LinkedIn connections CSV.

    LinkedIn exports include a preamble of several lines before the header row.
    We detect the header by searching for 'First Name' in each row.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Detect header row offset — LinkedIn sometimes prepends 2–3 comment lines
    header_row = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        for i, line in enumerate(f):
            if "First Name" in line:
                header_row = i
                break

    df = pd.read_csv(path, skiprows=header_row, encoding="utf-8-sig")

    # Normalise column names (strip whitespace, lower for lookup)
    df.columns = [c.strip() for c in df.columns]

    required = {"First Name", "Last Name", "Company", "Position", "Connected On"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV is missing expected columns: {missing}\n"
            f"Found columns: {list(df.columns)}"
        )

    # Fill NaN
    df["Company"]   = df["Company"].fillna("").str.strip()
    df["Position"]  = df["Position"].fillna("").str.strip()
    df["First Name"] = df["First Name"].fillna("").str.strip()
    df["Last Name"]  = df["Last Name"].fillna("").str.strip()

    # Derived: full name
    df["full_name"] = (df["First Name"] + " " + df["Last Name"]).str.strip()

    # Remove the self-row if present (Jared Sanborn / Pure Technology)
    # We'll add the center node manually
    df = df[df["full_name"].str.lower() != "jared sanborn"].copy()
    df = df[df["Company"].str.lower() != "pure technology"].copy()

    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_graph(df: pd.DataFrame, center_name: str = "Jared Sanborn") -> nx.Graph:
    """
    Build a NetworkX graph:
    - Center node = Jared
    - One node per connection
    - Edge: every connection → Jared (direct LinkedIn connection)
    - Edge: connections who share a company → connected to each other
    """
    G = nx.Graph()

    # Add center node
    G.add_node(
        center_name,
        label=center_name,
        company="Pure Technology",
        position="Founder & CEO",
        node_type="center",
        size=60,
    )

    # Add connection nodes
    for _, row in df.iterrows():
        name = row["full_name"]
        if not name:
            continue
        G.add_node(
            name,
            label=name,
            company=row["Company"],
            position=row["Position"],
            connected_on=row.get("Connected On", ""),
            node_type="connection",
            size=20,
        )
        # Edge to center (direct LinkedIn connection)
        G.add_edge(center_name, name, weight=2, edge_type="linkedin")

    # Add company co-membership edges (proxy connections)
    company_members = defaultdict(list)
    for _, row in df.iterrows():
        name = row["full_name"]
        company = row["Company"]
        if name and company:
            company_members[company].append(name)

    for company, members in company_members.items():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                n1, n2 = members[i], members[j]
                if G.has_node(n1) and G.has_node(n2):
                    if not G.has_edge(n1, n2):
                        G.add_edge(n1, n2, weight=1, edge_type="shared_company",
                                   company=company)

    return G


# ---------------------------------------------------------------------------
# Community detection
# ---------------------------------------------------------------------------

def detect_communities(G: nx.Graph, center_name: str) -> dict:
    """
    Detect communities using Louvain (python-louvain) if available,
    otherwise fall back to greedy modularity.

    Returns dict: node_name -> community_id (int)
    """
    # Work on an undirected copy without the center so it doesn't dominate
    sub = G.copy()

    if LOUVAIN_AVAILABLE:
        partition = community_louvain.best_partition(sub, random_state=42)
    else:
        # Greedy modularity
        communities = nx.community.greedy_modularity_communities(sub)
        partition = {}
        for cid, community in enumerate(communities):
            for node in community:
                partition[node] = cid

    # Center node gets its own community id (-1 for visual distinction)
    partition[center_name] = -1
    return partition


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def compute_stats(df: pd.DataFrame, G: nx.Graph, partition: dict) -> dict:
    total_connections = len(df)
    companies = [c for c in df["Company"].tolist() if c]
    company_counts = Counter(companies)
    top_companies = company_counts.most_common(10)
    unique_companies = len(company_counts)
    num_clusters = len(set(v for k, v in partition.items() if v != -1))
    solo_nodes = [n for n, d in G.nodes(data=True)
                  if d.get("node_type") == "connection"
                  and not d.get("company")]

    return {
        "total_connections": total_connections,
        "unique_companies": unique_companies,
        "top_companies": top_companies,
        "num_clusters": num_clusters,
        "solo_count": len(solo_nodes),
        "total_edges": G.number_of_edges(),
    }


# ---------------------------------------------------------------------------
# Pyvis visualisation
# ---------------------------------------------------------------------------

def build_pyvis_network(
    G: nx.Graph,
    partition: dict,
    stats: dict,
    center_name: str = "Jared Sanborn",
    output_path: str = "exports/linkedin-network-graph.html",
) -> str:
    """
    Render the graph as an interactive pyvis HTML file.
    """
    net = Network(
        height="100vh",
        width="100%",
        bgcolor=DARK_BG,
        font_color=BRAND_WHITE,
        directed=False,
        notebook=False,
        cdn_resources="in_line",
    )

    # Physics: force-directed with repulsion (Barnes-Hut)
    net.force_atlas_2based(
        gravity=-80,
        central_gravity=0.01,
        spring_length=150,
        spring_strength=0.05,
        damping=0.4,
        overlap=0.2,
    )
    net.set_options(json.dumps({
        "physics": {
            "enabled": True,
            "forceAtlas2Based": {
                "gravitationalConstant": -80,
                "centralGravity": 0.01,
                "springLength": 150,
                "springConstant": 0.05,
                "damping": 0.4,
                "avoidOverlap": 0.2
            },
            "solver": "forceAtlas2Based",
            "stabilization": {
                "enabled": True,
                "iterations": 200,
                "updateInterval": 25
            }
        },
        "interaction": {
            "hover": True,
            "tooltipDelay": 100,
            "navigationButtons": True,
            "keyboard": True,
            "zoomView": True
        },
        "edges": {
            "smooth": {
                "type": "continuous",
                "roundness": 0.2
            },
            "color": {
                "inherit": False
            }
        },
        "nodes": {
            "font": {
                "color": "#e8f4f8",
                "size": 13,
                "face": "Inter, Arial, sans-serif"
            }
        }
    }))

    # Map community id -> colour
    unique_communities = sorted(set(v for v in partition.values() if v != -1))
    community_color_map = {}
    for i, cid in enumerate(unique_communities):
        community_color_map[cid] = CLUSTER_PALETTE[i % len(CLUSTER_PALETTE)]

    # Add nodes
    for node, data in G.nodes(data=True):
        is_center = (node == center_name)
        cid = partition.get(node, 0)
        company = data.get("company", "")
        position = data.get("position", "")

        if is_center:
            color = {
                "background": CENTER_NODE_COLOR,
                "border": BRAND_ORANGE,
                "highlight": {"background": "#fff", "border": BRAND_ORANGE},
                "hover": {"background": "#fff", "border": BRAND_ORANGE},
            }
            size = 55
            shape = "star"
            title = (
                f"<div style='background:#1a2332;padding:10px;border-radius:8px;"
                f"border:1px solid {BRAND_ORANGE};color:#e8f4f8;font-family:Arial'>"
                f"<b style='font-size:15px'>{node}</b><br>"
                f"<span style='color:{BRAND_ORANGE}'>Pure Technology</span><br>"
                f"Founder & CEO<br><br>"
                f"<b>Network stats:</b><br>"
                f"Total connections: {stats['total_connections']}<br>"
                f"Companies: {stats['unique_companies']}<br>"
                f"Communities: {stats['num_clusters']}"
                f"</div>"
            )
            border_width = 3
        elif not company:
            color = {
                "background": SOLO_NODE_COLOR,
                "border": "#718096",
                "highlight": {"background": "#636e7e", "border": "#a0aec0"},
                "hover": {"background": "#636e7e", "border": "#a0aec0"},
            }
            size = 16
            shape = "dot"
            title = (
                f"<div style='background:#1a2332;padding:8px;border-radius:6px;"
                f"border:1px solid #718096;color:#e8f4f8;font-family:Arial'>"
                f"<b>{node}</b><br>"
                f"<span style='color:#a0aec0'>{position or 'Independent'}</span>"
                f"</div>"
            )
            border_width = 1
        else:
            base_color = community_color_map.get(cid, BRAND_BLUE)
            # Slightly lighter for hover
            color = {
                "background": base_color,
                "border": base_color,
                "highlight": {"background": base_color, "border": "#ffffff"},
                "hover": {"background": base_color, "border": "#ffffff"},
            }
            # Size by degree (more connections = larger)
            degree = G.degree(node)
            size = 18 + min(degree * 3, 20)
            shape = "dot"
            title = (
                f"<div style='background:#1a2332;padding:8px;border-radius:6px;"
                f"border:1px solid {base_color};color:#e8f4f8;font-family:Arial'>"
                f"<b style='color:{base_color}'>{node}</b><br>"
                f"<span style='color:#a0aec0'>{position}</span><br>"
                f"<span style='font-size:11px;color:#718096'>{company}</span>"
                f"</div>"
            )
            border_width = 2

        net.add_node(
            node,
            label=node,
            title=title,
            color=color,
            size=size,
            shape=shape,
            borderWidth=border_width,
            shadow=True,
        )

    # Add edges
    for u, v, data in G.edges(data=True):
        edge_type = data.get("edge_type", "linkedin")
        if edge_type == "linkedin":
            color = {"color": "#2a3f52", "highlight": BRAND_BLUE, "hover": BRAND_BLUE}
            width = 1.5
            dashes = False
        else:
            # Shared company — glowing coloured line
            company = data.get("company", "")
            # Derive edge colour from one of the nodes' community
            cid = partition.get(u, 0)
            base = community_color_map.get(cid, BRAND_BLUE)
            color = {"color": base + "66", "highlight": base, "hover": base}
            width = 2.5
            dashes = False

        net.add_edge(u, v, color=color, width=width, dashes=dashes)

    # Generate HTML
    net.save_graph(output_path)

    # Post-process: inject custom header panel + enhanced CSS
    _inject_stats_panel(output_path, stats, center_name)

    return output_path


# ---------------------------------------------------------------------------
# HTML post-processing: inject stats panel + dark glow CSS
# ---------------------------------------------------------------------------

def _inject_stats_panel(html_path: str, stats: dict, center_name: str) -> None:
    """Inject a stats panel overlay and additional CSS into the pyvis HTML."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    top_companies_html = "".join(
        f'<div class="company-row">'
        f'<span class="company-name">{c}</span>'
        f'<span class="company-count">{n}</span>'
        f'</div>'
        for c, n in stats["top_companies"][:8]
    )

    overlay_html = f"""
<!-- LinkedIn Network Graph Stats Panel -->
<div id="stats-panel">
  <div class="stats-header">
    <div class="logo-mark">&#9650;</div>
    <div>
      <div class="stats-title">LinkedIn Network</div>
      <div class="stats-subtitle">Interactive Graph</div>
    </div>
  </div>
  <div class="stat-grid">
    <div class="stat-card">
      <div class="stat-number" style="color:{BRAND_BLUE}">{stats['total_connections']}</div>
      <div class="stat-label">Connections</div>
    </div>
    <div class="stat-card">
      <div class="stat-number" style="color:{BRAND_ORANGE}">{stats['unique_companies']}</div>
      <div class="stat-label">Companies</div>
    </div>
    <div class="stat-card">
      <div class="stat-number" style="color:#00d4aa">{stats['num_clusters']}</div>
      <div class="stat-label">Communities</div>
    </div>
    <div class="stat-card">
      <div class="stat-number" style="color:#a855f7">{stats['total_edges']}</div>
      <div class="stat-label">Connections</div>
    </div>
  </div>
  <div class="companies-section">
    <div class="section-title">Top Companies</div>
    {top_companies_html}
  </div>
  <div class="legend">
    <div class="legend-item"><span class="legend-dot" style="background:#fff;border:2px solid {BRAND_ORANGE}"></span>You (Center)</div>
    <div class="legend-item"><span class="legend-dot" style="background:{BRAND_BLUE}"></span>Company cluster</div>
    <div class="legend-item"><span class="legend-dot" style="background:#4a5568"></span>Independent</div>
  </div>
  <div class="controls-hint">Scroll to zoom &bull; Drag to pan &bull; Click nodes</div>
</div>

<style>
  /* ===== Global dark canvas ===== */
  body, html {{
    background: {DARK_BG} !important;
    margin: 0;
    padding: 0;
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    overflow: hidden;
  }}
  #mynetwork {{
    background: {DARK_BG} !important;
    border: none !important;
  }}

  /* ===== Stats panel ===== */
  #stats-panel {{
    position: fixed;
    top: 20px;
    left: 20px;
    width: 240px;
    background: rgba(13,17,23,0.92);
    border: 1px solid rgba(42,147,193,0.35);
    border-radius: 12px;
    padding: 18px;
    z-index: 1000;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 30px rgba(42,147,193,0.15), 0 8px 32px rgba(0,0,0,0.5);
    color: #e8f4f8;
  }}

  .stats-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(42,147,193,0.2);
  }}
  .logo-mark {{
    font-size: 22px;
    color: {BRAND_BLUE};
    text-shadow: 0 0 12px {BRAND_BLUE};
  }}
  .stats-title {{
    font-size: 14px;
    font-weight: 700;
    color: {BRAND_WHITE};
    letter-spacing: 0.5px;
  }}
  .stats-subtitle {{
    font-size: 11px;
    color: #6b8ea8;
  }}

  .stat-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 16px;
  }}
  .stat-card {{
    background: rgba(42,147,193,0.07);
    border: 1px solid rgba(42,147,193,0.15);
    border-radius: 8px;
    padding: 10px 8px;
    text-align: center;
  }}
  .stat-number {{
    font-size: 22px;
    font-weight: 800;
    line-height: 1;
    text-shadow: 0 0 8px currentColor;
  }}
  .stat-label {{
    font-size: 10px;
    color: #6b8ea8;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .companies-section {{
    margin-bottom: 14px;
  }}
  .section-title {{
    font-size: 11px;
    color: #6b8ea8;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
  }}
  .company-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 12px;
  }}
  .company-name {{
    color: #a8c4d4;
    max-width: 160px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .company-count {{
    color: {BRAND_BLUE};
    font-weight: 700;
    font-size: 12px;
    background: rgba(42,147,193,0.12);
    padding: 1px 7px;
    border-radius: 10px;
  }}

  .legend {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(42,147,193,0.2);
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    color: #8ba8bc;
  }}
  .legend-dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }}

  .controls-hint {{
    font-size: 10px;
    color: #3d5a6e;
    text-align: center;
    padding-top: 10px;
    border-top: 1px solid rgba(42,147,193,0.1);
    letter-spacing: 0.3px;
  }}

  /* ===== Title badge top-right ===== */
  #title-badge {{
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(13,17,23,0.88);
    border: 1px solid rgba(241,66,11,0.35);
    border-radius: 8px;
    padding: 10px 16px;
    z-index: 1000;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 20px rgba(241,66,11,0.1);
    color: {BRAND_WHITE};
    font-size: 13px;
    text-align: center;
  }}
  #title-badge strong {{
    color: {BRAND_ORANGE};
    font-size: 15px;
    display: block;
    text-shadow: 0 0 8px {BRAND_ORANGE};
  }}

  /* ===== Canvas glow ===== */
  canvas {{
    filter: brightness(1.05);
  }}
</style>

<div id="title-badge">
  <strong>{center_name}</strong>
  LinkedIn Network Graph
</div>
"""

    # Inject before </body>
    html = html.replace("</body>", overlay_html + "\n</body>")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_network_graph(
    csv_path: str,
    output_path: str = "exports/linkedin-network-graph.html",
    center_name: str = "Jared Sanborn",
) -> str:
    """
    Full pipeline: CSV -> Graph -> Visualisation -> HTML.

    Parameters
    ----------
    csv_path    : Path to LinkedIn Connections CSV export
    output_path : Where to write the output HTML
    center_name : Name of the person at the centre of the graph

    Returns
    -------
    Absolute path to the generated HTML file
    """
    print(f"\nLinkedIn Network Graph Generator")
    print(f"=================================")
    print(f"Input  : {csv_path}")
    print(f"Output : {output_path}")
    print()

    # Step 1 — Load data
    print("Loading connections CSV...")
    df = load_connections(csv_path)
    print(f"  Loaded {len(df)} connections")

    # Step 2 — Build graph
    print("Building graph...")
    G = build_graph(df, center_name=center_name)
    print(f"  Nodes : {G.number_of_nodes()}")
    print(f"  Edges : {G.number_of_edges()}")

    # Step 3 — Community detection
    print("Detecting communities...")
    partition = detect_communities(G, center_name=center_name)
    num_communities = len(set(v for v in partition.values() if v != -1))
    print(f"  Communities found: {num_communities}")

    # Step 4 — Stats
    stats = compute_stats(df, G, partition)
    print("\nNetwork Statistics:")
    print(f"  Total connections : {stats['total_connections']}")
    print(f"  Unique companies  : {stats['unique_companies']}")
    print(f"  Communities       : {stats['num_clusters']}")
    print(f"  Top companies:")
    for company, count in stats["top_companies"][:5]:
        print(f"    {company:<30} {count}")

    # Step 5 — Render
    print(f"\nRendering interactive HTML...")
    os.makedirs(Path(output_path).parent, exist_ok=True)
    final_path = build_pyvis_network(
        G, partition, stats,
        center_name=center_name,
        output_path=output_path,
    )
    size_kb = Path(final_path).stat().st_size / 1024
    print(f"  Done! {size_kb:.0f} KB written to: {final_path}")
    print(f"\nOpen in browser: file://{Path(final_path).resolve()}")
    return final_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive LinkedIn network graph from a connections CSV export.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/linkedin_network_graph.py exports/sample_connections.csv
  python tools/linkedin_network_graph.py ~/Downloads/Connections.csv
  python tools/linkedin_network_graph.py Connections.csv --output my-graph.html --center "Jane Doe"
        """,
    )
    parser.add_argument(
        "csv_path",
        help="Path to LinkedIn connections CSV export",
    )
    parser.add_argument(
        "--output", "-o",
        default="exports/linkedin-network-graph.html",
        help="Output HTML file path (default: exports/linkedin-network-graph.html)",
    )
    parser.add_argument(
        "--center", "-c",
        default="Jared Sanborn",
        help='Name for the center node (default: "Jared Sanborn")',
    )

    args = parser.parse_args()
    generate_network_graph(args.csv_path, args.output, args.center)


if __name__ == "__main__":
    main()
