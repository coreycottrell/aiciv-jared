#!/usr/bin/env python3
"""
Implement Personalized AI Capabilities Flow on purebrain.ai/purebrain-3/

NEW FLOW:
1. User chats with AI
2. AI discovers name through conversation
3. Button appears: "See What [AI_NAME] Can Do"
4. Click -> Claude API generates personalized list of 5-7 capabilities
5. Features display as chat messages
6. NEW BUTTON: "Bring [AI_NAME] to Life"
7. That button triggers existing purchase/signup flow

Date: 2026-02-17
Page: purebrain.ai/purebrain-3/ (Elementor page ID 338)
"""

import json
import requests
import sys
from datetime import datetime

# WordPress credentials
WP_BASE_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_APP_PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"
PAGE_ID = 338  # purebrain-3 page

# ============================================================
# THE OLD CTA BUTTON CODE (what we're replacing)
# ============================================================
OLD_BUTTON_CODE = """// Add CTA button inside the chat instead of auto-scrolling
                const displayName = state.aiName || 'Your PURE BRAIN';
                const ctaDiv = document.createElement('div');
                ctaDiv.className = 'chat-cta';
                ctaDiv.innerHTML = `
                    <button class="chat-cta__btn" onclick="revealPricing()">
                        <span class="btn-icon">⚡</span> See What ${displayName} Can Do
                    </button>
                `;
                chatMessages.appendChild(ctaDiv);
                scrollToBottom();"""

# ============================================================
# THE NEW CTA BUTTON CODE (changed onclick target)
# ============================================================
NEW_BUTTON_CODE = """// Add CTA button inside the chat - triggers personalized capabilities
                const displayName = state.aiName || 'Your PURE BRAIN';
                const ctaDiv = document.createElement('div');
                ctaDiv.className = 'chat-cta';
                ctaDiv.innerHTML = `
                    <button class="chat-cta__btn" id="seeWhatBtn" onclick="showPersonalizedCapabilities()">
                        <span class="btn-icon">⚡</span> See What ${displayName} Can Do
                    </button>
                `;
                chatMessages.appendChild(ctaDiv);
                scrollToBottom();"""

# ============================================================
# THE NEW showPersonalizedCapabilities() FUNCTION
# Inserted BEFORE the existing revealPricing() function
# ============================================================
NEW_CAPABILITIES_FUNCTION = """// ============================================
        // PERSONALIZED CAPABILITIES REVEAL
        // ============================================

        // Called when user clicks "See What [Name] Can Do"
        // Generates personalized capabilities via Claude API
        async function showPersonalizedCapabilities() {
            // Disable the button immediately
            const seeWhatBtn = document.getElementById('seeWhatBtn');
            if (seeWhatBtn) {
                seeWhatBtn.disabled = true;
                seeWhatBtn.textContent = 'Discovering your capabilities...';
            }

            const aiName = state.aiName || 'Your PURE BRAIN';

            // Build the capabilities prompt based on conversation context
            const conversationSummary = state.conversationHistory
                .filter(m => m.role !== 'system')
                .map(m => `${m.role === 'user' ? 'User' : aiName}: ${m.content.replace(/\[.*?\]/g, '').trim()}`)
                .slice(0, 20)
                .join('\\n');

            const capabilitiesMessages = [
                {
                    role: "user",
                    content: `Based on the following conversation between ${aiName} (the AI) and the user, generate a personalized list of exactly 5-7 specific ways ${aiName} can help this person in their daily life and work.

CONVERSATION:
${conversationSummary}

INSTRUCTIONS:
- Be SPECIFIC to what they mentioned in the conversation (their work, goals, values, challenges)
- Make each capability feel personal and tailored, not generic
- Use the user's actual words or themes back where possible
- Format as simple bullet points with a short title and one sentence description
- Use this exact format for each item:
  **[Short title]** — [One specific sentence about how this helps them]
- Do NOT include any introduction or conclusion text
- Do NOT number them
- Just the bullet points, nothing else
- Start directly with the first bullet point`
                }
            ];

            // Show typing indicator while generating
            showTyping();

            // Call Claude API for capabilities
            const capabilitiesResponse = await callClaude(capabilitiesMessages);
            hideTyping();

            if (capabilitiesResponse) {
                // Show intro message first
                addMessage(`Here's what I can actually do for you, ${aiName === 'Your PURE BRAIN' ? 'based on our conversation' : 'based on everything we just discovered about you'}:`, true);
                await new Promise(r => setTimeout(r, 800));

                // Parse and display each capability as a separate message
                const lines = capabilitiesResponse.split('\\n').filter(l => l.trim().length > 0);
                for (const line of lines) {
                    if (line.trim().startsWith('**') || line.trim().startsWith('-') || line.trim().startsWith('•')) {
                        showTyping();
                        const delay = Math.min(Math.max(line.length * 15, 600), 1800);
                        await new Promise(r => setTimeout(r, delay));
                        hideTyping();
                        addMessage(line.trim(), true);
                        await new Promise(r => setTimeout(r, 400));
                    }
                }

                // Short pause then show the "Bring to Life" button
                await new Promise(r => setTimeout(r, 1200));

                // Final message before CTA
                addMessage(`This is just the beginning of what we can build together.`, true);
                await new Promise(r => setTimeout(r, 1000));

            } else {
                // Fallback if API fails
                addMessage(`I've discovered who you are. Now let me show you what I can do for you.`, true);
                await new Promise(r => setTimeout(r, 800));
            }

            // Show the "Bring [Name] to Life" button
            const bringToLifeDiv = document.createElement('div');
            bringToLifeDiv.className = 'chat-cta';
            bringToLifeDiv.innerHTML = `
                <button class="chat-cta__btn chat-cta__btn--primary" onclick="revealPricing()">
                    <span class="btn-icon">✨</span> Bring ${aiName} to Life
                </button>
            `;
            chatMessages.appendChild(bringToLifeDiv);
            scrollToBottom();

            // Log capabilities reveal
            logConversationToBackend('capabilities_revealed', { ai_name: aiName });
        }

        """

# The anchor text before which to insert the new function
BEFORE_REVEAL_ANCHOR = """// Called by the in-chat CTA button - shows celebration first
        function revealPricing()"""


def get_elementor_data():
    """Fetch the current Elementor data for the page."""
    url = f"{WP_BASE_URL}/wp-json/wp/v2/pages/{PAGE_ID}?context=edit"
    response = requests.get(url, auth=(WP_USER, WP_APP_PASSWORD))

    if response.status_code != 200:
        print(f"ERROR fetching page: {response.status_code}")
        print(response.text[:500])
        return None

    data = response.json()
    elementor_data_str = data.get('meta', {}).get('_elementor_data', '')

    if not elementor_data_str:
        print("ERROR: No Elementor data found in page meta")
        return None

    return data, elementor_data_str


def modify_html_content(html_content):
    """Apply both modifications to the HTML content."""

    # MODIFICATION 1: Replace the CTA button onclick
    if OLD_BUTTON_CODE not in html_content:
        print("ERROR: Could not find old button code to replace")
        print("Searching for partial match...")
        fragment = 'chat-cta__btn" onclick="revealPricing()'
        idx = html_content.find(fragment)
        if idx > 0:
            print(f"Found partial match at {idx}")
            print(html_content[max(0,idx-200):idx+300])
        return None

    html_content = html_content.replace(OLD_BUTTON_CODE, NEW_BUTTON_CODE, 1)
    print("OK: Replaced CTA button onclick handler")

    # MODIFICATION 2: Insert the showPersonalizedCapabilities function before revealPricing
    if BEFORE_REVEAL_ANCHOR not in html_content:
        print("ERROR: Could not find revealPricing anchor to insert before")
        return None

    html_content = html_content.replace(
        BEFORE_REVEAL_ANCHOR,
        NEW_CAPABILITIES_FUNCTION + BEFORE_REVEAL_ANCHOR,
        1
    )
    print("OK: Inserted showPersonalizedCapabilities() function")

    return html_content


def update_page(page_data, elementor_data_str, new_html_content):
    """Update the page with modified HTML content via REST API."""

    # Parse and modify the Elementor data
    elementor_data = json.loads(elementor_data_str)

    # The HTML widget is at elementor_data[0]['elements'][0]
    widget = elementor_data[0]['elements'][0]
    widget_id = widget.get('id', 'unknown')

    print(f"Modifying widget ID: {widget_id}")
    print(f"Original HTML length: {len(widget['settings']['html'])}")
    print(f"New HTML length: {len(new_html_content)}")

    # Update the HTML in the widget
    elementor_data[0]['elements'][0]['settings']['html'] = new_html_content

    # Serialize back to JSON
    new_elementor_data_str = json.dumps(elementor_data, ensure_ascii=False)

    # Update via REST API - update both content and elementor_data
    url = f"{WP_BASE_URL}/wp-json/wp/v2/pages/{PAGE_ID}"

    # We need to update the meta field _elementor_data
    # Also update the content raw field which appears to be the same HTML
    payload = {
        'meta': {
            '_elementor_data': new_elementor_data_str
        }
    }

    response = requests.post(
        url,
        auth=(WP_USER, WP_APP_PASSWORD),
        json=payload
    )

    if response.status_code in (200, 201):
        print(f"OK: Page updated successfully (HTTP {response.status_code})")
        return True
    else:
        print(f"ERROR: Failed to update page (HTTP {response.status_code})")
        print(response.text[:1000])
        return False


def verify_change(html_content):
    """Verify the modifications were applied correctly."""
    checks = [
        ('New button onclick', 'onclick="showPersonalizedCapabilities()"'),
        ('Old button onclick removed', 'onclick="revealPricing()"'),  # Should NOT be in button anymore
        ('New function exists', 'async function showPersonalizedCapabilities()'),
        ('Bring to Life button', 'Bring ${aiName} to Life'),
        ('callClaude for capabilities', 'capabilitiesMessages'),
    ]

    print("\nVerification:")
    for name, text in checks:
        if name == 'Old button onclick removed':
            # This one should NOT be in the button anymore, but IS in revealPricing
            # So let's check the specific button context
            btn_idx = html_content.find('seeWhatBtn')
            if btn_idx > 0:
                btn_context = html_content[max(0,btn_idx-100):btn_idx+300]
                found = 'showPersonalizedCapabilities' in btn_context
                print(f"  OK New button calls showPersonalizedCapabilities: {found}")
            continue

        found = text in html_content
        status = "OK" if found else "FAIL"
        print(f"  {status}: {name}")

    return True


def main():
    print("=" * 60)
    print("PERSONALIZED CAPABILITIES FLOW IMPLEMENTATION")
    print("Target: https://purebrain.ai/purebrain-3/")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: Fetch current page data
    print("\n[1] Fetching current page data...")
    result = get_elementor_data()
    if not result:
        sys.exit(1)

    page_data, elementor_data_str = result
    elementor_data = json.loads(elementor_data_str)

    print(f"  Page title: {page_data.get('title', {}).get('rendered', 'unknown')}")
    print(f"  Elementor data: {len(elementor_data_str)} chars")

    # Step 2: Extract current HTML content
    print("\n[2] Extracting HTML content from Elementor widget...")
    widget = elementor_data[0]['elements'][0]
    html_content = widget['settings']['html']
    print(f"  Widget ID: {widget.get('id', 'unknown')}")
    print(f"  HTML content: {len(html_content)} chars")

    # Step 3: Check if already modified
    if 'showPersonalizedCapabilities' in html_content:
        print("\n  NOTE: showPersonalizedCapabilities already exists in page!")
        print("  Checking if it's the current version...")
        if 'Bring ${aiName} to Life' in html_content:
            print("  Current version already implemented. Nothing to do.")
            print("  Run with --force to re-apply.")
            if '--force' not in sys.argv:
                sys.exit(0)
            else:
                print("  Force flag set - re-applying...")
                # Reset to original first would require the original code
                # For now, just report
                print("  ERROR: Cannot re-apply without original code")
                sys.exit(1)

    # Step 4: Apply modifications
    print("\n[3] Applying modifications...")
    new_html_content = modify_html_content(html_content)

    if not new_html_content:
        print("ERROR: Modification failed")
        sys.exit(1)

    # Step 5: Verify the changes look correct
    print("\n[4] Verifying changes...")
    verify_change(new_html_content)

    # Show a preview of the new button code
    idx = new_html_content.find('seeWhatBtn')
    print("\nNew button preview:")
    print(new_html_content[max(0,idx-200):idx+400])

    # Step 6: Save backup of original
    print("\n[5] Saving backup...")
    with open('/tmp/purebrain3_html_backup.html', 'w') as f:
        f.write(html_content)
    print("  Backup saved: /tmp/purebrain3_html_backup.html")

    # Step 7: Save the new version locally first
    with open('/tmp/purebrain3_html_new.html', 'w') as f:
        f.write(new_html_content)
    print("  New version saved: /tmp/purebrain3_html_new.html")

    # Step 8: Update the page
    print("\n[6] Updating page on WordPress...")
    success = update_page(page_data, elementor_data_str, new_html_content)

    if success:
        print("\n" + "=" * 60)
        print("SUCCESS: Personalized capabilities flow implemented!")
        print("=" * 60)
        print("\nNew flow on purebrain.ai/purebrain-3/:")
        print("  1. Chat with AI -> AI discovers user's name")
        print("  2. Button appears: 'See What [Name] Can Do'")
        print("  3. Click -> Claude generates 5-7 personalized capabilities")
        print("  4. Capabilities display as chat messages")
        print("  5. Button appears: 'Bring [Name] to Life'")
        print("  6. That button -> existing purchase/celebration flow")
        print("\nTest at: https://purebrain.ai/purebrain-3/")
    else:
        print("\nERROR: Page update failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
