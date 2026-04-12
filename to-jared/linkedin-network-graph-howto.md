# LinkedIn Network Graph - Complete How-To Guide

## What It Does
Takes your LinkedIn connections CSV export and generates a beautiful, interactive network graph showing:
- **You (Jared Sanborn)** at the center as a star node
- **Every connection** as a colored node, clustered by company
- **Company clusters** - people who work at the same company are connected and color-coded
- **Community detection** (Louvain algorithm) - finds natural groupings
- **Stats panel** - total connections, companies, communities, top employers
- **Interactive** - drag, zoom, click nodes to see name/title/company

---

## Files You Need

| File | Location | What It Is |
|------|----------|-----------|
| `tools/linkedin_network_graph.py` | Aether server | The Python script (24KB) |
| `exports/linkedin-network-graph.html` | Aether server | Sample output (709KB, self-contained) |

---

## Step-by-Step: How to Run It

### Step 1: Export Your LinkedIn Connections

1. Go to **linkedin.com** > Click your profile photo (top right)
2. Click **Settings & Privacy**
3. Click **Data privacy** (left sidebar)
4. Click **Get a copy of your data**
5. Select **Connections** only (fastest - takes ~10 minutes)
6. Click **Request archive**
7. LinkedIn emails you a download link when ready
8. Download and unzip - you'll get a file called **`Connections.csv`**

### Step 2: Send the CSV to Aether

Send the `Connections.csv` file to me via Telegram. I'll process it automatically.

**OR** if you want to run it yourself on the server:

```bash
# SSH into the server
ssh jared@89.167.19.20

# Navigate to the project
cd /home/jared/projects/AI-CIV/aether

# Activate the Python environment
source venv/bin/activate

# Run the graph generator
python tools/linkedin_network_graph.py /path/to/Connections.csv
```

### Step 3: Open the Output

The script generates: `exports/linkedin-network-graph.html`

**Option A - On the server directly:**
```bash
# The file is already at:
# /home/jared/projects/AI-CIV/aether/exports/linkedin-network-graph.html
# Download it to your laptop and open in Chrome/Safari
```

**Option B - Send me the CSV via Telegram:**
I'll run it and send back the HTML file. Just open it in any browser.

---

## What the Output Looks Like

- **Dark theme** with PureBrain brand colors (blue #2a93c1, orange #f1420b)
- **Star node** (white with orange border) = You at the center
- **Colored dots** = Your connections, grouped by company/community
- **Lines** = Connections (solid = direct LinkedIn, colored = shared company)
- **Stats panel** (top left) = Connection count, companies, communities, top employers
- **Name badge** (top right) = "Jared Sanborn - LinkedIn Network Graph"

### Controls:
- **Scroll** = Zoom in/out
- **Click + drag** = Pan around
- **Click a node** = See name, title, company in tooltip
- **Drag a node** = Reposition it (physics simulation adjusts)
- **Double-click** = Focus on a node

---

## Advanced Options

```bash
# Custom output location
python tools/linkedin_network_graph.py Connections.csv --output my-graph.html

# Different center person (if generating for someone else)
python tools/linkedin_network_graph.py Connections.csv --center "Phil Smith"
```

---

## Dependencies (Already Installed)

All dependencies are pre-installed in the server's Python virtual environment:

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | 3.0.0 | CSV data processing |
| networkx | 3.6.1 | Graph algorithms |
| pyvis | 0.3.2 | Interactive HTML visualization |
| python-louvain | 0.16 | Community detection algorithm |

---

## Quick Start (TL;DR)

1. Export LinkedIn connections (Settings > Data Privacy > Get Copy > Connections)
2. Send `Connections.csv` to me on Telegram
3. I generate the graph and send back the HTML
4. Open HTML in browser, explore your network

That's it. ~2 minutes of your time.
