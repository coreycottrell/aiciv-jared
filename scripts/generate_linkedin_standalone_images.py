#!/usr/bin/env python3
"""
Generate LinkedIn Standalone images (1080x1350) for week of April 7-13, 2026.
5 new posts that need images.
PureBrain brand: hexagon logo, PUREBRAIN.ai wordmark, dark #080a12, Oswald Bold.
"""

import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("/home/jared/exports/portal-files")
LOGO_PATH = Path("/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors-v16/pt-hex-logo.png")

logo_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()

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
    width: 1080px;
    height: 1350px;
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
.logo { width: 70px; height: 70px; object-fit: contain; }
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
.awaken {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 18px;
    letter-spacing: 2px;
    color: #f1420b;
    opacity: 0.9;
}
.title {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    text-transform: uppercase;
    line-height: 1.08;
    text-align: center;
}
.grid {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(42, 147, 193, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(42, 147, 193, 0.02) 1px, transparent 1px);
    background-size: 60px 60px;
}
.header {
    position: absolute;
    top: 50px;
    left: 0; right: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}
.footer {
    position: absolute;
    bottom: 50px;
    left: 0; right: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}
.cta {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 24px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #ffffff;
    text-align: center;
}
.cta .url { color: #2a93c1; }
"""

WORDMARK_HTML = """
<span class="wordmark">
    <span class="pure">PURE</span><span class="br">BR</span><span class="ai-letters">AI</span><span class="n-letter">N</span><span class="dot-ai">.ai</span>
</span>
"""

# ============================================================
# IMAGE 1: 88% Stat Nobody Talks About (Apr 7)
# ============================================================
IMAGE_1_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{COMMON_CSS}
.container {{
    background: linear-gradient(180deg, #080a12 0%, #0d1020 30%, #120a15 50%, #0d1020 70%, #080a12 100%);
}}
.big-stat {{
    position: absolute;
    top: 28%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 260px;
    color: #f1420b;
    opacity: 0.08;
    letter-spacing: -10px;
}}
.percent {{
    position: absolute;
    top: 28%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 160px;
    color: #f1420b;
    text-shadow: 0 0 60px rgba(241, 66, 11, 0.3), 0 0 120px rgba(241, 66, 11, 0.1);
}}
.content {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -30%);
    text-align: center;
    width: 85%;
}}
.title {{ font-size: 56px; margin-bottom: 30px; }}
.title .orange {{ color: #f1420b; }}
.title .blue {{ color: #2a93c1; }}
.subtitle {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 22px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
}}
/* Shield fragments */
.shield-frag {{
    position: absolute;
    background: rgba(241, 66, 11, 0.06);
    border: 1px solid rgba(241, 66, 11, 0.1);
    transform: rotate(15deg);
}}
.sf1 {{ width: 80px; height: 120px; top: 15%; right: 8%; }}
.sf2 {{ width: 60px; height: 90px; top: 22%; right: 18%; transform: rotate(-20deg); }}
.sf3 {{ width: 50px; height: 70px; bottom: 30%; left: 8%; transform: rotate(35deg); }}
</style></head><body>
<div class="container">
    <div class="grid"></div>
    <div class="shield-frag sf1"></div>
    <div class="shield-frag sf2"></div>
    <div class="shield-frag sf3"></div>
    <div class="big-stat">88%</div>
    <div class="percent">88%</div>
    <div class="header">
        <img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo">
        {WORDMARK_HTML}
    </div>
    <div class="content">
        <div class="title">
            THE STAT <span class="orange">NOBODY</span><br>
            IS <span class="blue">TALKING ABOUT</span>
        </div>
        <div class="subtitle">AI Agent Security Is A Crisis</div>
    </div>
    <div class="footer">
        <div class="cta">Build boundaries first <span class="url">purebrain.ai</span></div>
        <span class="awaken">Awaken Your AI Partner Today</span>
    </div>
</div>
</body></html>"""

# ============================================================
# IMAGE 2: The Personalization Gap (Apr 10)
# ============================================================
IMAGE_2_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{COMMON_CSS}
.container {{
    background: linear-gradient(180deg, #080a12 0%, #0a1520 30%, #0d1a28 50%, #0a1520 70%, #080a12 100%);
}}
/* Signal waves emanating from center */
.wave {{
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(42, 147, 193, 0.08);
    top: 35%;
    left: 50%;
    transform: translate(-50%, -50%);
}}
.w1 {{ width: 200px; height: 200px; border-color: rgba(42, 147, 193, 0.15); }}
.w2 {{ width: 350px; height: 350px; }}
.w3 {{ width: 500px; height: 500px; border-color: rgba(42, 147, 193, 0.05); }}
.w4 {{ width: 650px; height: 650px; border-color: rgba(42, 147, 193, 0.03); }}
/* Center pulse */
.pulse {{
    position: absolute;
    top: 35%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: radial-gradient(circle, #2a93c1, transparent);
    box-shadow: 0 0 40px rgba(42, 147, 193, 0.4), 0 0 80px rgba(42, 147, 193, 0.15);
}}
/* Data points around waves */
.dp {{
    position: absolute;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #2a93c1;
    box-shadow: 0 0 10px rgba(42, 147, 193, 0.5);
}}
.dp1 {{ top: 25%; left: 35%; }}
.dp2 {{ top: 30%; right: 30%; }}
.dp3 {{ top: 42%; left: 20%; }}
.dp4 {{ top: 38%; right: 22%; background: #f1420b; box-shadow: 0 0 10px rgba(241,66,11,0.5); }}
.dp5 {{ top: 45%; left: 40%; }}
.content {{
    position: absolute;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -20%);
    text-align: center;
    width: 85%;
}}
.title {{ font-size: 60px; margin-bottom: 24px; }}
.title .blue {{ color: #2a93c1; }}
.title .orange {{ color: #f1420b; }}
.subtitle {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 20px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
}}
.stat-line {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 28px;
    color: #f1420b;
    margin-bottom: 16px;
    letter-spacing: 1px;
}}
</style></head><body>
<div class="container">
    <div class="grid"></div>
    <div class="wave w1"></div>
    <div class="wave w2"></div>
    <div class="wave w3"></div>
    <div class="wave w4"></div>
    <div class="pulse"></div>
    <div class="dp dp1"></div>
    <div class="dp dp2"></div>
    <div class="dp dp3"></div>
    <div class="dp dp4"></div>
    <div class="dp dp5"></div>
    <div class="header">
        <img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo">
        {WORDMARK_HTML}
    </div>
    <div class="content">
        <div class="stat-line">83% WILL SHARE DATA FOR REAL VALUE</div>
        <div class="title">
            THE <span class="blue">PERSONALIZATION</span><br>
            <span class="orange">GAP</span>
        </div>
        <div class="subtitle">Stop Segmenting. Start Listening.</div>
    </div>
    <div class="footer">
        <div class="cta">Your AI should listen <span class="url">purebrain.ai</span></div>
        <span class="awaken">Awaken Your AI Partner Today</span>
    </div>
</div>
</body></html>"""

# ============================================================
# IMAGE 3: The AI Budget Trap (Apr 11)
# ============================================================
IMAGE_3_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{COMMON_CSS}
.container {{
    background: linear-gradient(180deg, #080a12 0%, #100a14 30%, #0d0f1a 50%, #100a14 70%, #080a12 100%);
}}
/* Money drain visual - descending bars */
.bar-container {{
    position: absolute;
    top: 22%;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 20px;
    align-items: flex-end;
    height: 250px;
}}
.bar {{
    width: 50px;
    border-radius: 4px 4px 0 0;
    opacity: 0.7;
}}
.b1 {{ height: 250px; background: linear-gradient(180deg, #2a93c1, rgba(42,147,193,0.3)); }}
.b2 {{ height: 200px; background: linear-gradient(180deg, #2a93c1, rgba(42,147,193,0.25)); opacity: 0.6; }}
.b3 {{ height: 150px; background: linear-gradient(180deg, #f1420b, rgba(241,66,11,0.25)); opacity: 0.5; }}
.b4 {{ height: 100px; background: linear-gradient(180deg, #f1420b, rgba(241,66,11,0.2)); opacity: 0.4; }}
.b5 {{ height: 50px; background: linear-gradient(180deg, #f1420b, rgba(241,66,11,0.15)); opacity: 0.3; }}
/* Downward arrow */
.arrow {{
    position: absolute;
    top: 48%;
    right: 15%;
    font-size: 80px;
    color: rgba(241, 66, 11, 0.15);
    transform: rotate(90deg);
}}
.content {{
    position: absolute;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -10%);
    text-align: center;
    width: 85%;
}}
.title {{ font-size: 64px; margin-bottom: 24px; }}
.title .orange {{ color: #f1420b; }}
.title .blue {{ color: #2a93c1; }}
.subtitle {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 20px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
}}
.stat-line {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 26px;
    color: rgba(255,255,255,0.5);
    margin-bottom: 16px;
    letter-spacing: 1px;
}}
.stat-line .num {{ color: #f1420b; }}
</style></head><body>
<div class="container">
    <div class="grid"></div>
    <div class="bar-container">
        <div class="bar b1"></div>
        <div class="bar b2"></div>
        <div class="bar b3"></div>
        <div class="bar b4"></div>
        <div class="bar b5"></div>
    </div>
    <div class="arrow">&#x276F;</div>
    <div class="header">
        <img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo">
        {WORDMARK_HTML}
    </div>
    <div class="content">
        <div class="stat-line"><span class="num">86%</span> INCREASING AI BUDGETS</div>
        <div class="title">
            THE AI <span class="orange">BUDGET</span><br>
            <span class="blue">TRAP</span>
        </div>
        <div class="subtitle">Spending More Is Not A Strategy</div>
    </div>
    <div class="footer">
        <div class="cta">Spend smarter not more <span class="url">purebrain.ai</span></div>
        <span class="awaken">Awaken Your AI Partner Today</span>
    </div>
</div>
</body></html>"""

# ============================================================
# IMAGE 4: Transparency as Competitive Advantage (Apr 12)
# ============================================================
IMAGE_4_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{COMMON_CSS}
.container {{
    background: linear-gradient(180deg, #080a12 0%, #0a1222 30%, #0d1830 50%, #0a1222 70%, #080a12 100%);
}}
/* Glass/transparent layers */
.glass {{
    position: absolute;
    border: 1px solid rgba(42, 147, 193, 0.12);
    border-radius: 12px;
    background: rgba(42, 147, 193, 0.03);
    backdrop-filter: blur(2px);
}}
.g1 {{ width: 400px; height: 280px; top: 18%; left: 50%; transform: translateX(-50%); }}
.g2 {{ width: 350px; height: 240px; top: 22%; left: 50%; transform: translateX(-50%) rotate(3deg); border-color: rgba(42, 147, 193, 0.08); }}
.g3 {{ width: 300px; height: 200px; top: 26%; left: 50%; transform: translateX(-50%) rotate(-2deg); border-color: rgba(42, 147, 193, 0.05); }}
/* Eye/window icon in center */
.eye {{
    position: absolute;
    top: 28%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80px;
    height: 40px;
    border: 3px solid rgba(42, 147, 193, 0.4);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.pupil {{
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #2a93c1;
    box-shadow: 0 0 20px rgba(42, 147, 193, 0.5);
}}
/* Light rays */
.ray {{
    position: absolute;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(42, 147, 193, 0.1), transparent);
    top: 28%;
    left: 50%;
}}
.ray1 {{ width: 600px; transform: translateX(-50%) rotate(0deg); }}
.ray2 {{ width: 500px; transform: translateX(-50%) rotate(30deg); }}
.ray3 {{ width: 500px; transform: translateX(-50%) rotate(-30deg); }}
.ray4 {{ width: 400px; transform: translateX(-50%) rotate(60deg); }}
.ray5 {{ width: 400px; transform: translateX(-50%) rotate(-60deg); }}
.content {{
    position: absolute;
    top: 52%;
    left: 50%;
    transform: translate(-50%, -10%);
    text-align: center;
    width: 85%;
}}
.title {{ font-size: 52px; margin-bottom: 24px; }}
.title .blue {{ color: #2a93c1; }}
.title .orange {{ color: #f1420b; }}
.subtitle {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 20px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
}}
</style></head><body>
<div class="container">
    <div class="grid"></div>
    <div class="glass g3"></div>
    <div class="glass g2"></div>
    <div class="glass g1"></div>
    <div class="ray ray1"></div>
    <div class="ray ray2"></div>
    <div class="ray ray3"></div>
    <div class="ray ray4"></div>
    <div class="ray ray5"></div>
    <div class="eye"><div class="pupil"></div></div>
    <div class="header">
        <img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo">
        {WORDMARK_HTML}
    </div>
    <div class="content">
        <div class="title">
            <span class="blue">TRANSPARENCY</span><br>
            AS <span class="orange">COMPETITIVE</span><br>
            ADVANTAGE
        </div>
        <div class="subtitle">Show Your Work. Own The Decade.</div>
    </div>
    <div class="footer">
        <div class="cta">Show your work <span class="url">purebrain.ai</span></div>
        <span class="awaken">Awaken Your AI Partner Today</span>
    </div>
</div>
</body></html>"""

# ============================================================
# IMAGE 5: The Sunday Reset Myth (Apr 13)
# ============================================================
IMAGE_5_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{COMMON_CSS}
.container {{
    background: linear-gradient(180deg, #080a12 0%, #0f0a16 30%, #12101c 50%, #0f0a16 70%, #080a12 100%);
}}
/* Calendar/reset icon */
.calendar {{
    position: absolute;
    top: 22%;
    left: 50%;
    transform: translateX(-50%);
    width: 200px;
    height: 200px;
    border: 2px solid rgba(241, 66, 11, 0.2);
    border-radius: 12px;
    background: rgba(241, 66, 11, 0.03);
    display: flex;
    flex-direction: column;
}}
.cal-header {{
    height: 50px;
    background: rgba(241, 66, 11, 0.1);
    border-radius: 10px 10px 0 0;
    border-bottom: 2px solid rgba(241, 66, 11, 0.15);
}}
.cal-body {{
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.reset-icon {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 60px;
    color: rgba(241, 66, 11, 0.4);
}}
/* Circular arrow around calendar */
.circ-arrow {{
    position: absolute;
    top: 22%;
    left: 50%;
    transform: translateX(-50%);
    width: 280px;
    height: 280px;
    border: 2px dashed rgba(241, 66, 11, 0.1);
    border-radius: 50%;
}}
/* Fading memory fragments */
.frag {{
    position: absolute;
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.08);
    transform: rotate(-5deg);
}}
.f1 {{ top: 18%; left: 10%; }}
.f2 {{ top: 25%; right: 8%; transform: rotate(3deg); }}
.f3 {{ top: 40%; left: 5%; transform: rotate(-8deg); }}
.f4 {{ top: 35%; right: 5%; transform: rotate(6deg); }}
.content {{
    position: absolute;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -10%);
    text-align: center;
    width: 85%;
}}
.title {{ font-size: 58px; margin-bottom: 24px; }}
.title .orange {{ color: #f1420b; }}
.title .blue {{ color: #2a93c1; }}
.subtitle {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 20px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
}}
.stat-line {{
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 24px;
    color: rgba(255,255,255,0.5);
    margin-bottom: 16px;
    letter-spacing: 1px;
}}
.stat-line .num {{ color: #f1420b; }}
</style></head><body>
<div class="container">
    <div class="grid"></div>
    <div class="frag f1">BRAND VOICE...</div>
    <div class="frag f2">Q2 GOALS...</div>
    <div class="frag f3">CAMPAIGN DATA...</div>
    <div class="frag f4">CUSTOMER SEGMENTS...</div>
    <div class="circ-arrow"></div>
    <div class="calendar">
        <div class="cal-header"></div>
        <div class="cal-body"><div class="reset-icon">0</div></div>
    </div>
    <div class="header">
        <img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo">
        {WORDMARK_HTML}
    </div>
    <div class="content">
        <div class="stat-line"><span class="num">20%</span> OF TIME LOST TO CONTEXT REBUILDING</div>
        <div class="title">
            THE <span class="orange">SUNDAY</span><br>
            <span class="blue">RESET</span> MYTH
        </div>
        <div class="subtitle">Stop Paying The Briefing Tax</div>
    </div>
    <div class="footer">
        <div class="cta">Your AI should remember <span class="url">purebrain.ai</span></div>
        <span class="awaken">Awaken Your AI Partner Today</span>
    </div>
</div>
</body></html>"""

# ============================================================
# RENDER ALL
# ============================================================
IMAGES = [
    {"name": "linkedin-88-percent-stat-nobody-talks-about", "html": IMAGE_1_HTML},
    {"name": "linkedin-personalization-gap", "html": IMAGE_2_HTML},
    {"name": "linkedin-ai-budget-trap", "html": IMAGE_3_HTML},
    {"name": "linkedin-transparency-competitive-advantage", "html": IMAGE_4_HTML},
    {"name": "linkedin-sunday-reset-myth", "html": IMAGE_5_HTML},
]

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for img in IMAGES:
            print(f"Rendering: {img['name']}...")
            page = browser.new_page(viewport={"width": 1080, "height": 1350})
            page.set_content(img["html"], wait_until="networkidle")
            page.wait_for_timeout(1000)
            output_path = OUTPUT_DIR / f"{img['name']}.png"
            page.screenshot(path=str(output_path), full_page=False)
            print(f"  Saved: {output_path}")
            page.close()
        browser.close()

    print(f"\nAll {len(IMAGES)} images saved to {OUTPUT_DIR}/")
    for img in IMAGES:
        p = OUTPUT_DIR / f"{img['name']}.png"
        size = p.stat().st_size
        print(f"  {p.name}: {size:,} bytes ({size/1024:.0f} KB)")

if __name__ == "__main__":
    main()
