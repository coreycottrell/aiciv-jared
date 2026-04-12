#!/usr/bin/env python3
"""
Generate 4 weekly content images using Playwright HTML-to-PNG rendering.
PureBrain brand standards: hexagon logo, PUREBRAIN.ai wordmark, dark theme, Oswald Bold.

Blog Banners: 1200x630 (16:9-ish)
LinkedIn Standalone: 1080x1350
"""

import base64
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("/home/jared/exports/portal-files")
LOGO_PATH = Path("/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors-v16/pt-hex-logo.png")

# Read and base64 encode logo for inline embedding
logo_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()

# Common CSS
COMMON_CSS = """
@font-face {
    font-family: 'Oswald';
    src: url('file:///home/jared/.fonts/Oswald-Bold.ttf') format('truetype');
    font-weight: 700;
    font-style: normal;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    background: #080a12;
    color: #ffffff;
    overflow: hidden;
}
.container {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}
.logo {
    width: 60px;
    height: 60px;
    object-fit: contain;
}
.wordmark {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 22px;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.wordmark .pure { color: #ffffff; }
.wordmark .br { color: #2a93c1; }
.wordmark .ai-letters { color: #f1420b; }
.wordmark .n-letter { color: #2a93c1; }
.wordmark .dot-ai { color: #ffffff; }
.neural-feed {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #2a93c1;
    opacity: 0.8;
}
.awaken {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: 2px;
    color: #f1420b;
    opacity: 0.9;
}
.title {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    text-transform: uppercase;
    line-height: 1.1;
    text-align: center;
}
"""

WORDMARK_HTML = """
<span class="wordmark">
    <span class="pure">PURE</span><span class="br">BR</span><span class="ai-letters">AI</span><span class="n-letter">N</span><span class="dot-ai">.ai</span>
</span>
"""

# ============================================================
# IMAGE 1: Blog Banner - AI Agent Security
# ============================================================
IMAGE_1_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{COMMON_CSS}
body {{ width: 1200px; height: 630px; }}
.container {{
    background: linear-gradient(135deg, #080a12 0%, #0d1422 40%, #121a2e 70%, #080a12 100%);
    padding: 40px 60px;
}}
/* Shield shape */
.shield-container {{
    position: absolute;
    right: 80px;
    top: 50%;
    transform: translateY(-50%);
    width: 220px;
    height: 260px;
    opacity: 0.15;
}}
.shield {{
    width: 100%;
    height: 100%;
    background: linear-gradient(180deg, #2a93c1 0%, #f1420b 100%);
    clip-path: polygon(50% 0%, 100% 25%, 100% 70%, 50% 100%, 0% 70%, 0% 25%);
}}
/* Warning lines */
.warning-line {{
    position: absolute;
    height: 2px;
    background: linear-gradient(90deg, #f1420b 0%, transparent 100%);
    opacity: 0.3;
}}
.wl1 {{ top: 120px; left: 0; width: 400px; }}
.wl2 {{ top: 180px; left: 0; width: 300px; }}
.wl3 {{ bottom: 120px; left: 0; width: 350px; }}
/* Grid lines */
.grid {{
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(42, 147, 193, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(42, 147, 193, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
}}
/* Glowing dot cluster */
.dot {{
    position: absolute;
    border-radius: 50%;
    background: #f1420b;
    box-shadow: 0 0 20px #f1420b, 0 0 40px rgba(241,66,11,0.3);
}}
.d1 {{ width: 6px; height: 6px; top: 200px; right: 320px; }}
.d2 {{ width: 4px; height: 4px; top: 260px; right: 280px; opacity: 0.7; }}
.d3 {{ width: 8px; height: 8px; top: 300px; right: 350px; opacity: 0.5; }}
.d4 {{ width: 5px; height: 5px; top: 160px; right: 250px; opacity: 0.6; }}
/* Header bar */
.header {{
    position: absolute;
    top: 30px;
    left: 60px;
    right: 60px;
    display: flex;
    align-items: center;
    gap: 16px;
}}
/* 88% stat */
.stat {{
    position: absolute;
    right: 60px;
    bottom: 100px;
    font-size: 80px;
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    color: #f1420b;
    opacity: 0.12;
    letter-spacing: -2px;
}}
/* Content */
.content {{
    position: absolute;
    left: 60px;
    top: 120px;
    max-width: 700px;
}}
.title {{
    font-size: 42px;
    text-align: left;
    line-height: 1.15;
    margin-bottom: 16px;
}}
.title .highlight {{ color: #f1420b; }}
.title .blue {{ color: #2a93c1; }}
/* Footer */
.footer {{
    position: absolute;
    bottom: 30px;
    left: 60px;
    right: 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
</style></head><body>
<div class="container">
    <div class="grid"></div>
    <div class="shield-container"><div class="shield"></div></div>
    <div class="warning-line wl1"></div>
    <div class="warning-line wl2"></div>
    <div class="warning-line wl3"></div>
    <div class="dot d1"></div>
    <div class="dot d2"></div>
    <div class="dot d3"></div>
    <div class="dot d4"></div>
    <div class="stat">88%</div>

    <div class="header">
        <img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo">
        {WORDMARK_HTML}
    </div>

    <div class="content">
        <div class="title">
            <span class="highlight">88% OF COMPANIES</span> HAD AN<br>
            AI AGENT <span class="blue">SECURITY INCIDENT</span>.<br>
            IS YOURS NEXT?
        </div>
    </div>

    <div class="footer">
        <span class="neural-feed">THE NEURAL FEED</span>
        <span class="awaken">Awaken Your AI Partner Today</span>
    </div>
</div>
</body></html>"""

# ============================================================
# IMAGE 2: Blog Banner - Customer Data/Personalization
# ============================================================
IMAGE_2_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{COMMON_CSS}
body {{ width: 1200px; height: 630px; }}
.container {{
    background: linear-gradient(135deg, #080a12 0%, #0a1520 40%, #0d1a28 70%, #080a12 100%);
    padding: 40px 60px;
}}
/* Conversation bubbles */
.bubble {{
    position: absolute;
    border-radius: 16px;
    padding: 12px 20px;
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 1px;
    text-transform: uppercase;
    opacity: 0.25;
}}
.b1 {{
    right: 60px; top: 100px;
    background: rgba(42, 147, 193, 0.15);
    border: 1px solid rgba(42, 147, 193, 0.3);
    color: #2a93c1;
}}
.b2 {{
    right: 100px; top: 170px;
    background: rgba(241, 66, 11, 0.1);
    border: 1px solid rgba(241, 66, 11, 0.25);
    color: #f1420b;
}}
.b3 {{
    right: 50px; top: 240px;
    background: rgba(42, 147, 193, 0.12);
    border: 1px solid rgba(42, 147, 193, 0.25);
    color: #2a93c1;
}}
.b4 {{
    right: 120px; top: 310px;
    background: rgba(241, 66, 11, 0.08);
    border: 1px solid rgba(241, 66, 11, 0.2);
    color: #f1420b;
}}
/* Signal waves */
.wave {{
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(42, 147, 193, 0.1);
}}
.w1 {{ width: 300px; height: 300px; right: -50px; top: 50%; transform: translateY(-50%); }}
.w2 {{ width: 400px; height: 400px; right: -100px; top: 50%; transform: translateY(-50%); }}
.w3 {{ width: 500px; height: 500px; right: -150px; top: 50%; transform: translateY(-50%); }}
/* Data streams */
.stream {{
    position: absolute;
    width: 1px;
    background: linear-gradient(180deg, transparent, rgba(42, 147, 193, 0.15), transparent);
}}
.s1 {{ height: 200px; right: 200px; top: 80px; }}
.s2 {{ height: 300px; right: 280px; top: 40px; }}
.s3 {{ height: 250px; right: 360px; top: 100px; }}
/* Grid */
.grid {{
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(42, 147, 193, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(42, 147, 193, 0.02) 1px, transparent 1px);
    background-size: 50px 50px;
}}
.header {{
    position: absolute;
    top: 30px;
    left: 60px;
    right: 60px;
    display: flex;
    align-items: center;
    gap: 16px;
}}
.content {{
    position: absolute;
    left: 60px;
    top: 120px;
    max-width: 680px;
}}
.title {{
    font-size: 44px;
    text-align: left;
    line-height: 1.12;
}}
.title .blue {{ color: #2a93c1; }}
.title .highlight {{ color: #f1420b; }}
.footer {{
    position: absolute;
    bottom: 30px;
    left: 60px;
    right: 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
</style></head><body>
<div class="container">
    <div class="grid"></div>
    <div class="wave w1"></div>
    <div class="wave w2"></div>
    <div class="wave w3"></div>
    <div class="stream s1"></div>
    <div class="stream s2"></div>
    <div class="stream s3"></div>
    <div class="bubble b1">I need help with...</div>
    <div class="bubble b2">What if we could...</div>
    <div class="bubble b3">My biggest pain is...</div>
    <div class="bubble b4">I wish someone would...</div>

    <div class="header">
        <img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo">
        {WORDMARK_HTML}
    </div>

    <div class="content">
        <div class="title">
            YOUR <span class="blue">CUSTOMERS</span> WILL<br>
            TELL YOU <span class="highlight">EVERYTHING</span>.<br>
            YOU JUST HAVE TO <span class="blue">ASK</span>.
        </div>
    </div>

    <div class="footer">
        <span class="neural-feed">THE NEURAL FEED</span>
        <span class="awaken">Awaken Your AI Partner Today</span>
    </div>
</div>
</body></html>"""

# ============================================================
# IMAGE 3: LinkedIn Standalone - The Agentic Era Is Here
# ============================================================
IMAGE_3_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{COMMON_CSS}
body {{ width: 1080px; height: 1350px; }}
.container {{
    background: linear-gradient(180deg, #080a12 0%, #0a1525 30%, #0d1a30 50%, #0a1525 70%, #080a12 100%);
    padding: 60px;
}}
/* Radial burst */
.burst {{
    position: absolute;
    top: 40%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 600px;
    height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(42, 147, 193, 0.08) 0%, transparent 70%);
}}
/* Orbital rings */
.ring {{
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(42, 147, 193, 0.08);
    top: 40%;
    left: 50%;
    transform: translate(-50%, -50%);
}}
.r1 {{ width: 300px; height: 300px; }}
.r2 {{ width: 450px; height: 450px; border-color: rgba(42, 147, 193, 0.05); }}
.r3 {{ width: 600px; height: 600px; border-color: rgba(42, 147, 193, 0.03); }}
/* Agent nodes on orbits */
.node {{
    position: absolute;
    border-radius: 50%;
    background: #2a93c1;
    box-shadow: 0 0 20px rgba(42, 147, 193, 0.4), 0 0 60px rgba(42, 147, 193, 0.15);
}}
.n1 {{ width: 12px; height: 12px; top: 30%; left: 62%; }}
.n2 {{ width: 8px; height: 8px; top: 38%; left: 30%; }}
.n3 {{ width: 10px; height: 10px; top: 52%; left: 68%; }}
.n4 {{ width: 6px; height: 6px; top: 25%; left: 45%; }}
.n5 {{ width: 14px; height: 14px; top: 45%; left: 35%;
    background: #f1420b;
    box-shadow: 0 0 20px rgba(241, 66, 11, 0.4), 0 0 60px rgba(241, 66, 11, 0.15);
}}
.n6 {{ width: 8px; height: 8px; top: 55%; left: 55%; }}
/* Connection lines */
.conn {{
    position: absolute;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(42, 147, 193, 0.12), transparent);
    transform-origin: left center;
}}
.c1 {{ top: 33%; left: 35%; width: 300px; transform: rotate(15deg); }}
.c2 {{ top: 42%; left: 30%; width: 350px; transform: rotate(-8deg); }}
.c3 {{ top: 50%; left: 40%; width: 250px; transform: rotate(25deg); }}
/* Upward arrows / pillars */
.pillar {{
    position: absolute;
    width: 2px;
    background: linear-gradient(0deg, transparent, rgba(42, 147, 193, 0.15), rgba(42, 147, 193, 0.05), transparent);
    bottom: 300px;
}}
.p1 {{ height: 400px; left: 25%; }}
.p2 {{ height: 500px; left: 50%; }}
.p3 {{ height: 350px; left: 75%; }}
/* Grid */
.grid {{
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(42, 147, 193, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(42, 147, 193, 0.02) 1px, transparent 1px);
    background-size: 60px 60px;
}}
.header {{
    position: absolute;
    top: 50px;
    left: 0;
    right: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}}
.content {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    width: 90%;
}}
.title {{
    font-size: 72px;
    line-height: 1.08;
    margin-bottom: 24px;
}}
.title .blue {{ color: #2a93c1; }}
.title .orange {{ color: #f1420b; }}
.subtitle {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 22px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.5);
    margin-top: 20px;
}}
.footer {{
    position: absolute;
    bottom: 50px;
    left: 0;
    right: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}}
</style></head><body>
<div class="container">
    <div class="grid"></div>
    <div class="burst"></div>
    <div class="ring r1"></div>
    <div class="ring r2"></div>
    <div class="ring r3"></div>
    <div class="node n1"></div>
    <div class="node n2"></div>
    <div class="node n3"></div>
    <div class="node n4"></div>
    <div class="node n5"></div>
    <div class="node n6"></div>
    <div class="conn c1"></div>
    <div class="conn c2"></div>
    <div class="conn c3"></div>
    <div class="pillar p1"></div>
    <div class="pillar p2"></div>
    <div class="pillar p3"></div>

    <div class="header">
        <img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo" style="width:70px;height:70px;">
        {WORDMARK_HTML}
    </div>

    <div class="content">
        <div class="title">
            THE <span class="blue">AGENTIC</span><br>
            <span class="orange">ERA</span> IS HERE
        </div>
        <div class="subtitle">Enterprise AI Has Crossed The Threshold</div>
    </div>

    <div class="footer">
        <span class="awaken" style="font-size:18px;">Awaken Your AI Partner Today</span>
        {WORDMARK_HTML}
    </div>
</div>
</body></html>"""

# ============================================================
# IMAGE 4: LinkedIn Standalone - AI Tool vs AI Partner
# ============================================================
IMAGE_4_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{COMMON_CSS}
body {{ width: 1080px; height: 1350px; }}
.container {{
    background: #080a12;
    padding: 60px;
}}
/* Split line */
.divider {{
    position: absolute;
    top: 35%;
    bottom: 25%;
    left: 50%;
    width: 2px;
    background: linear-gradient(180deg, transparent, rgba(255,255,255,0.15), transparent);
}}
/* Tool side - cold, mechanical */
.side-tool {{
    position: absolute;
    top: 35%;
    left: 60px;
    width: calc(50% - 80px);
    text-align: center;
}}
/* Partner side - warm, connected */
.side-partner {{
    position: absolute;
    top: 35%;
    right: 60px;
    width: calc(50% - 80px);
    text-align: center;
}}
/* Icons */
.icon-box {{
    width: 120px;
    height: 120px;
    margin: 0 auto 30px;
    position: relative;
}}
/* Wrench/tool icon - geometric */
.tool-icon {{
    width: 120px;
    height: 120px;
    border: 2px solid rgba(255,255,255,0.15);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,0.02);
}}
.tool-icon-inner {{
    width: 50px;
    height: 50px;
    border: 3px solid rgba(255,255,255,0.25);
    border-radius: 4px;
    position: relative;
}}
.tool-icon-inner::after {{
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.2);
}}
/* Partner icon - organic, glowing */
.partner-icon {{
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle, rgba(42, 147, 193, 0.15) 0%, transparent 70%);
    border: 2px solid rgba(42, 147, 193, 0.3);
    box-shadow: 0 0 40px rgba(42, 147, 193, 0.1);
}}
.partner-icon-inner {{
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(42, 147, 193, 0.4), rgba(42, 147, 193, 0.1));
    box-shadow: 0 0 20px rgba(42, 147, 193, 0.3);
}}
.side-label {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 36px;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 30px;
}}
.side-tool .side-label {{ color: rgba(255,255,255,0.4); }}
.side-partner .side-label {{ color: #2a93c1; }}
/* Trait list */
.trait {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 18px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}}
.side-tool .trait {{ color: rgba(255,255,255,0.3); }}
.side-partner .trait {{ color: rgba(42, 147, 193, 0.8); }}
/* VS badge */
.vs {{
    position: absolute;
    top: 52%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #080a12;
    border: 2px solid rgba(241, 66, 11, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 20px;
    color: #f1420b;
    z-index: 10;
    box-shadow: 0 0 30px rgba(241, 66, 11, 0.15);
}}
/* Grid */
.grid {{
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(42, 147, 193, 0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(42, 147, 193, 0.015) 1px, transparent 1px);
    background-size: 54px 54px;
}}
.header {{
    position: absolute;
    top: 50px;
    left: 0;
    right: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}}
.main-title {{
    position: absolute;
    top: 18%;
    left: 0;
    right: 0;
    text-align: center;
}}
.main-title .title {{
    font-size: 60px;
}}
.main-title .title .orange {{ color: #f1420b; }}
.main-title .title .blue {{ color: #2a93c1; }}
.footer {{
    position: absolute;
    bottom: 50px;
    left: 0;
    right: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}}
.bottom-line {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 24px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #f1420b;
    text-align: center;
}}
</style></head><body>
<div class="container">
    <div class="grid"></div>

    <div class="header">
        <img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo" style="width:70px;height:70px;">
        {WORDMARK_HTML}
    </div>

    <div class="main-title">
        <div class="title">
            AI <span class="orange">TOOL</span> vs AI <span class="blue">PARTNER</span>
        </div>
    </div>

    <div class="divider"></div>
    <div class="vs">VS</div>

    <div class="side-tool">
        <div class="icon-box">
            <div class="tool-icon"><div class="tool-icon-inner"></div></div>
        </div>
        <div class="side-label">Tool</div>
        <div class="trait">Follows Commands</div>
        <div class="trait">One Task At A Time</div>
        <div class="trait">No Memory</div>
        <div class="trait">Disposable</div>
        <div class="trait">Generic Output</div>
        <div class="trait">You Do The Thinking</div>
    </div>

    <div class="side-partner">
        <div class="icon-box">
            <div class="partner-icon"><div class="partner-icon-inner"></div></div>
        </div>
        <div class="side-label">Partner</div>
        <div class="trait">Understands Context</div>
        <div class="trait">Orchestrates Many</div>
        <div class="trait">Learns &amp; Remembers</div>
        <div class="trait">Grows With You</div>
        <div class="trait">Brand-Aligned</div>
        <div class="trait">Thinks Alongside You</div>
    </div>

    <div class="footer">
        <div class="bottom-line">Which one is running your business?</div>
        <span class="awaken" style="font-size:18px; margin-top: 8px;">Awaken Your AI Partner Today</span>
        {WORDMARK_HTML}
    </div>
</div>
</body></html>"""

# ============================================================
# RENDER ALL IMAGES
# ============================================================
IMAGES = [
    {
        "name": "blog-banner-ai-security-incident",
        "html": IMAGE_1_HTML,
        "width": 1200,
        "height": 630,
    },
    {
        "name": "blog-banner-customers-tell-everything",
        "html": IMAGE_2_HTML,
        "width": 1200,
        "height": 630,
    },
    {
        "name": "linkedin-agentic-era-is-here",
        "html": IMAGE_3_HTML,
        "width": 1080,
        "height": 1350,
    },
    {
        "name": "linkedin-ai-tool-vs-ai-partner",
        "html": IMAGE_4_HTML,
        "width": 1080,
        "height": 1350,
    },
]

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for img in IMAGES:
            print(f"Rendering: {img['name']}...")
            page = browser.new_page(viewport={"width": img["width"], "height": img["height"]})
            page.set_content(img["html"], wait_until="networkidle")
            # Wait for fonts to load
            page.wait_for_timeout(1000)

            output_path = OUTPUT_DIR / f"{img['name']}.png"
            page.screenshot(path=str(output_path), full_page=False)
            print(f"  Saved: {output_path}")
            page.close()

        browser.close()

    print(f"\nAll 4 images saved to {OUTPUT_DIR}/")
    for img in IMAGES:
        p = OUTPUT_DIR / f"{img['name']}.png"
        size = p.stat().st_size
        print(f"  {p.name}: {size:,} bytes ({size/1024:.0f} KB)")

if __name__ == "__main__":
    main()
