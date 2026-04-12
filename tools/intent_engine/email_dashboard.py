"""
Email Dashboard Generator for Experiential Intent Engine
Sends daily digest of hot prospects to purebrain@puremarketing.ai
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
from .config import EMAIL_RECIPIENT

# Email config from .env
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def generate_dashboard_html(
    ready_prospects: List[Dict],
    warm_prospects: List[Dict],
    recent_signals: List[Dict],
    counts: Dict[str, int],
) -> str:
    """
    Generate HTML email for daily dashboard.

    Args:
        ready_prospects: Top prospects with READY status
        warm_prospects: Top prospects with WARM status
        recent_signals: Recent signals (last 24h)
        counts: Count of prospects by status

    Returns:
        HTML string for email body
    """
    date_str = datetime.now().strftime("%A, %B %d, %Y")

    # Generate prospect rows
    prospect_rows = ""
    for p in ready_prospects[:10]:
        fields = p.get("fields", {})
        prospect_rows += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px;">
                <strong>{fields.get('Name', 'Unknown')}</strong><br>
                <span style="color: #6b7280; font-size: 12px;">
                    {fields.get('Title', '')}
                </span>
            </td>
            <td style="padding: 12px; text-align: center;">
                <span style="background: #10b981; color: white; padding: 4px 10px; border-radius: 20px; font-size: 12px;">
                    {fields.get('Rolling Intent Score (formula)', 0)}
                </span>
            </td>
            <td style="padding: 12px;">
                <a href="{fields.get('LinkedIn URL', '#')}" style="color: #2563eb; text-decoration: none;">
                    View →
                </a>
            </td>
        </tr>"""

    # Generate signal rows
    signal_rows = ""
    for s in recent_signals[:10]:
        fields = s.get("fields", {})
        signal_rows += f"""
        <tr style="border-bottom: 1px solid #f3f4f6;">
            <td style="padding: 8px;">
                <span style="background: #e0e7ff; color: #3730a3; padding: 2px 8px; border-radius: 4px; font-size: 10px; text-transform: uppercase;">
                    {fields.get('Signal Type', 'unknown')}
                </span>
            </td>
            <td style="padding: 8px;">
                {fields.get('LinkedIn URL', '')[:40]}...
            </td>
            <td style="padding: 8px; color: #6b7280; font-size: 12px;">
                Strength: {fields.get('Signal Strength', 0)}
            </td>
        </tr>"""

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Experiential Intent Dashboard</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; margin: 0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">🎯 Experiential Intent Dashboard</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">{date_str}</p>
        </div>

        <!-- Stats -->
        <div style="display: flex; justify-content: space-around; padding: 20px; background: #f9fafb; border-bottom: 1px solid #e5e7eb;">
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: #10b981;">{counts.get('ready', 0)}</div>
                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase;">Ready</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: #f59e0b;">{counts.get('warm', 0)}</div>
                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase;">Warm</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 28px; font-weight: bold; color: #2563eb;">{len(recent_signals)}</div>
                <div style="font-size: 12px; color: #6b7280; text-transform: uppercase;">New Signals</div>
            </div>
        </div>

        <!-- Hot Prospects -->
        <div style="padding: 20px; border-bottom: 1px solid #e5e7eb;">
            <h2 style="font-size: 16px; font-weight: 600; color: #111827; margin: 0 0 15px 0;">
                🔥 Today's Hot Prospects
            </h2>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f9fafb;">
                        <th style="padding: 8px; text-align: left; font-size: 12px; color: #6b7280;">Person</th>
                        <th style="padding: 8px; text-align: center; font-size: 12px; color: #6b7280;">Score</th>
                        <th style="padding: 8px; text-align: left; font-size: 12px; color: #6b7280;">Link</th>
                    </tr>
                </thead>
                <tbody>
                    {prospect_rows if prospect_rows else '<tr><td colspan="3" style="padding: 20px; text-align: center; color: #6b7280;">No ready prospects yet</td></tr>'}
                </tbody>
            </table>
        </div>

        <!-- Recent Signals -->
        <div style="padding: 20px; border-bottom: 1px solid #e5e7eb;">
            <h2 style="font-size: 16px; font-weight: 600; color: #111827; margin: 0 0 15px 0;">
                📡 Recent Signals (24h)
            </h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tbody>
                    {signal_rows if signal_rows else '<tr><td colspan="3" style="padding: 20px; text-align: center; color: #6b7280;">No new signals in last 24h</td></tr>'}
                </tbody>
            </table>
        </div>

        <!-- CTA -->
        <a href="https://airtable.com/app3PhIudYCZ8VCCF" style="display: block; background: #2563eb; color: white; text-align: center; padding: 14px 20px; text-decoration: none; margin: 20px; border-radius: 8px; font-weight: 600;">
            Open Full Dashboard in Airtable →
        </a>

        <!-- Footer -->
        <div style="text-align: center; padding: 20px; color: #9ca3af; font-size: 12px;">
            Experiential Intent Engine • Pure Marketing Group<br>
            Automated daily at 8 AM EST
        </div>
    </div>
</body>
</html>
"""
    return html


def send_dashboard_email(
    ready_prospects: List[Dict],
    warm_prospects: List[Dict],
    recent_signals: List[Dict],
    counts: Dict[str, int],
    gmail_user: str = None,
    gmail_password: str = None,
) -> bool:
    """
    Send the daily dashboard email.

    Args:
        ready_prospects: Top READY prospects
        warm_prospects: Top WARM prospects
        recent_signals: Recent signals
        counts: Status counts
        gmail_user: Gmail username (or from env)
        gmail_password: Gmail app password (or from env)

    Returns:
        True if sent successfully
    """
    # Get credentials from env if not provided
    if not gmail_user:
        gmail_user = os.getenv("GMAIL_USERNAME")
    if not gmail_password:
        gmail_password = os.getenv("GOOGLE_APP_PASSWORD")

    if not gmail_user or not gmail_password:
        print("Error: Gmail credentials not provided")
        print("Set GMAIL_USERNAME and GOOGLE_APP_PASSWORD in .env")
        return False

    # Generate HTML
    html = generate_dashboard_html(
        ready_prospects, warm_prospects, recent_signals, counts
    )

    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎯 Intent Dashboard - {datetime.now().strftime('%b %d')}"
    msg["From"] = gmail_user
    msg["To"] = EMAIL_RECIPIENT

    # Attach HTML
    msg.attach(MIMEText(html, "html"))

    # Send via Gmail SMTP
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
            print(f"✅ Dashboard email sent to {EMAIL_RECIPIENT}")
            return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def preview_dashboard(output_file: str = None):
    """
    Generate a preview of the dashboard without sending.

    Args:
        output_file: Where to save the HTML preview
    """
    from . import airtable_client
    import os

    if output_file is None:
        output_file = os.path.expanduser("~/dashboard_preview.html")

    print("Generating dashboard preview...")

    # Fetch data
    ready = airtable_client.get_ready_prospects(10)
    warm = airtable_client.get_warm_prospects(10)
    signals = airtable_client.get_recent_signals(24)
    counts = airtable_client.count_by_status()

    # Generate HTML
    html = generate_dashboard_html(ready, warm, signals, counts)

    # Save to file
    with open(output_file, "w") as f:
        f.write(html)

    print(f"✅ Preview saved to: {output_file}")
    print(f"   Open in browser: file://{output_file}")


if __name__ == "__main__":
    preview_dashboard()
