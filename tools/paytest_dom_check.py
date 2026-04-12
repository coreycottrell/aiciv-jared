"""
Check the DOM state - specifically why chatMessages is undefined/null when showTyping runs.
The error is: 'Cannot read properties of undefined (reading appendChild)'
This means chatMessages = document.getElementById('chatMessages') returned null.
"""
import asyncio
from playwright.async_api import async_playwright

async def dom_check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        await page.goto("https://purebrain.ai/pay-test/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        dom_state = await page.evaluate("""() => {
            return {
                // Check what getElementById returns for all critical chat elements
                chatMessages: !!document.getElementById('chatMessages'),
                chatInitial: !!document.getElementById('chatInitial'),
                chatInput: !!document.getElementById('chatInput'),
                userInput: !!document.getElementById('userInput'),
                submitBtn: !!document.getElementById('submitBtn'),
                chatName: !!document.getElementById('chatName'),
                chatStatus: !!document.getElementById('chatStatus'),
                chatIndicator: !!document.getElementById('chatIndicator'),
                pricingSection: !!document.getElementById('pricing'),

                // Also check if the const variables at script level are accessible
                // If the script uses 'const' at module level, they may not be on window
                chatMessagesFromWindow: typeof window.chatMessages !== 'undefined',

                // How many chat-messages divs exist?
                chatMessagesDivCount: document.querySelectorAll('#chatMessages').length,
                chatMessagesByClass: document.querySelectorAll('.chat-messages').length,

                // What's in the #awakening section
                awakeningHTML: document.getElementById('awakening') ?
                    document.getElementById('awakening').innerHTML.substring(0, 500) : 'not found',

                // Check if scripts are in a closure (IIFE) vs global
                startConversationType: typeof startConversation,
                handleSubmitType: typeof handleSubmit,
                callClaudeType: typeof callClaude,
                stateType: typeof state,
            };
        }""")

        print("=== DOM STATE CHECK ===")
        for k, v in dom_state.items():
            if k != 'awakeningHTML':
                print(f"  {k}: {v}")

        print(f"\n  #awakening HTML preview:")
        print(dom_state.get('awakeningHTML', 'not found')[:500])

        # The key insight: chatMessages, chatInitial etc are declared as 'const' in the script.
        # If they resolve to null at declaration time, they'll be null forever.
        # BUT the script has TWO script sections - let's check which one defines these.

        # Get all script tags to understand scope
        scripts_info = await page.evaluate("""() => {
            const scripts = document.querySelectorAll('script:not([src])');
            return Array.from(scripts).map((s, i) => ({
                index: i,
                length: s.textContent.length,
                hasChat: s.textContent.includes('chatMessages'),
                hasDomElements: s.textContent.includes('getElementById'),
                hasClaude: s.textContent.includes('callClaude'),
                preview: s.textContent.substring(0, 200)
            }));
        }""")

        print("\n=== INLINE SCRIPTS ===")
        for s in scripts_info:
            print(f"  Script {s['index']}: len={s['length']} hasChat={s['hasChat']} hasDomEl={s['hasDomElements']} hasClaude={s['hasClaude']}")
            print(f"    Preview: {s['preview'][:100]}")
            print()

        # The real question: is the script deferred or waiting for DOMContentLoaded?
        # If the const chatMessages = getElementById('chatMessages') runs before DOM is ready,
        # it will be null.
        script_timing = await page.evaluate("""() => {
            const scripts = document.querySelectorAll('script:not([src])');
            const chatScript = Array.from(scripts).find(s => s.textContent.includes('chatMessages'));
            if (!chatScript) return {found: false};

            // Check if it has DOMContentLoaded wrapper
            const text = chatScript.textContent;
            return {
                found: true,
                hasDOMContentLoaded: text.includes('DOMContentLoaded'),
                hasWindowOnload: text.includes('window.onload'),
                hasDocumentReady: text.includes('document.ready') || text.includes('$(document)') || text.includes('$(function'),
                startsWithIIFE: text.trim().startsWith('(function') || text.trim().startsWith('(() =>'),
                length: text.length,
                // Get the actual opening of the script
                opening: text.trim().substring(0, 300)
            };
        }""")

        print("=== CHAT SCRIPT TIMING CHECK ===")
        for k, v in script_timing.items():
            if k != 'opening':
                print(f"  {k}: {v}")
        print(f"\n  Script opening:\n{script_timing.get('opening', 'not found')}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(dom_check())
