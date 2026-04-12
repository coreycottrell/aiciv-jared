"""
cc.purebrain.ai Tab Detail Audit - Read content text + check for data populated
"""
import asyncio
import json
import time
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/cc-diagnostic-20260228"

URL = "https://cc.purebrain.ai/auth/login"
EMAIL = "jared@puretechnology.nyc"
PASSWORD = "puretech2026"
NAME = "Jared Sanborn"

console_all = []
console_errors = []

def capture_console(msg):
    entry = {"type": msg.type, "text": msg.text, "time": time.strftime("%H:%M:%S")}
    console_all.append(entry)
    if msg.type == "error":
        console_errors.append(entry)
        print(f"[CONSOLE ERROR] {msg.text}")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        page.on("console", capture_console)

        # Login
        await page.goto(URL, wait_until="networkidle", timeout=30000)
        await page.fill('input[placeholder*="name" i]', NAME)
        await page.fill('input[name="email"]', EMAIL)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle", timeout=15000)
        await page.wait_for_timeout(3000)

        print(f"Post-login URL: {page.url}")

        # =========================
        # TASKS TAB - DEEP AUDIT
        # =========================
        print("\n=== TASKS TAB ===")
        await page.click('button:has-text("Tasks")')
        await page.wait_for_timeout(2000)

        # Get full task list text
        task_content = await page.evaluate("""() => {
            // Look for task rows/cards
            const rows = document.querySelectorAll('tr, .task-row, .task-card, [class*="task"]');
            const results = [];
            rows.forEach(r => {
                const text = r.textContent.trim().replace(/\\s+/g, ' ');
                if (text.length > 5 && text.length < 500) results.push(text);
            });
            return results.slice(0, 30);
        }""")
        print(f"Task rows found: {len(task_content)}")
        for t in task_content[:5]:
            print(f"  Task: {t[:120]}")

        # Check specific data elements
        task_meta = await page.evaluate("""() => {
            return {
                taskCount: document.querySelectorAll('tr:not(:first-child), .task-item, [data-task]').length,
                hasTable: !!document.querySelector('table'),
                tableRows: document.querySelectorAll('table tr').length,
                headerRow: document.querySelector('table thead tr')?.textContent?.trim()?.replace(/\\s+/g, ' ') || 'no header',
                firstDataRow: document.querySelector('table tbody tr')?.textContent?.trim()?.replace(/\\s+/g, ' ')?.substring(0, 200) || 'no data row',
                filterElements: Array.from(document.querySelectorAll('select, input[type="text"], .filter')).map(el => ({
                    tag: el.tagName, placeholder: el.placeholder, value: el.value
                })),
                statusBadges: Array.from(document.querySelectorAll('.badge, .status, [class*="status"]')).slice(0, 10).map(el => el.textContent.trim()),
                paginationInfo: document.querySelector('.pagination, .page-info, [class*="page"]')?.textContent?.trim() || 'no pagination'
            };
        }""")
        print(f"Task meta: {json.dumps(task_meta, indent=2)}")

        await page.screenshot(path=f"{SCREENSHOT_DIR}/010-tasks-detail.png", full_page=True)
        print(f"Screenshot: 010-tasks-detail.png")

        # =========================
        # TEAM TAB - DEEP AUDIT
        # =========================
        print("\n=== TEAM TAB ===")
        await page.click('button:has-text("Team")')
        await page.wait_for_timeout(2000)

        team_meta = await page.evaluate("""() => {
            return {
                hasTeamContent: document.querySelector('[class*="team"], .card, .member-card') !== null,
                cardCount: document.querySelectorAll('.card, [class*="card"], .member').length,
                visibleText: document.querySelector('#app')?.textContent?.trim()?.replace(/\\s+/g, ' ')?.substring(0, 500) || 'no content',
                hasLoading: !!document.querySelector('.loading, .spinner, .skeleton'),
                emptyStateText: document.querySelector('.empty, .empty-state, [class*="empty"]')?.textContent?.trim() || 'no empty state',
                hasNeuralCanvas: !!document.getElementById('neural-canvas'),
                appVisible: document.getElementById('app')?.classList?.contains('visible'),
                allDivIds: Array.from(document.querySelectorAll('#app > *')).map(el => ({
                    tag: el.tagName,
                    id: el.id,
                    class: el.className.substring(0, 60),
                    visible: el.style.display !== 'none' && el.offsetHeight > 0
                }))
            };
        }""")
        print(f"Team meta: {json.dumps(team_meta, indent=2)}")

        await page.screenshot(path=f"{SCREENSHOT_DIR}/011-team-detail.png", full_page=True)
        print(f"Screenshot: 011-team-detail.png")

        # =========================
        # CALENDAR TAB - DEEP AUDIT
        # =========================
        print("\n=== CALENDAR TAB ===")
        await page.click('button:has-text("Calendar")')
        await page.wait_for_timeout(2000)

        cal_meta = await page.evaluate("""() => {
            const calView = document.getElementById('calendar-view');
            return {
                calendarViewVisible: calView ? calView.style.display !== 'none' : false,
                calendarViewDisplay: calView ? calView.style.display : 'no element',
                calendarViewClass: calView ? calView.className : 'not found',
                calendarContent: calView ? calView.textContent.trim().replace(/\\s+/g, ' ').substring(0, 300) : 'not found',
                calendarChildren: calView ? Array.from(calView.children).map(c => ({
                    tag: c.tagName, id: c.id, class: c.className.substring(0, 60), display: c.style.display
                })) : [],
                hasFullCalendar: typeof FullCalendar !== 'undefined',
                calendarEvents: document.querySelectorAll('.fc-event, .calendar-event, [class*="event"]').length,
                calendarGrid: !!document.querySelector('.fc-daygrid, .fc-timegrid, .calendar-grid'),
            };
        }""")
        print(f"Calendar meta: {json.dumps(cal_meta, indent=2)}")

        await page.screenshot(path=f"{SCREENSHOT_DIR}/012-calendar-detail.png", full_page=True)
        print(f"Screenshot: 012-calendar-detail.png")

        # =========================
        # EMAIL TAB - DEEP AUDIT
        # =========================
        print("\n=== EMAIL TAB ===")
        await page.click('button:has-text("Email")')
        await page.wait_for_timeout(2000)

        email_meta = await page.evaluate("""() => {
            const emailView = document.getElementById('email-view');
            return {
                emailViewExists: !!emailView,
                emailViewContent: emailView ? emailView.textContent.trim().replace(/\\s+/g, ' ').substring(0, 500) : 'not found',
                emailViewChildren: emailView ? Array.from(emailView.children).map(c => ({
                    tag: c.tagName, id: c.id, class: c.className.substring(0, 60), display: c.style.display
                })) : [],
                noMessagesText: document.querySelector('.no-messages, .empty-inbox, [class*="empty"]')?.textContent?.trim() || 'not found',
                inboxLabel: document.querySelector('.inbox-label, .inbox-title, h2, h3')?.textContent?.trim() || 'not found',
                setupButtonExists: !!document.querySelector('[class*="setup"], button:has-text("Setup"), a:has-text("Connect")'),
                gmailConnectExists: !!document.querySelector('[class*="gmail"], button:has-text("Gmail"), a:has-text("Gmail")'),
                syncSetupExists: !!document.querySelector('[class*="sync"]'),
                accountLabel: document.querySelector('[class*="account"], .account-email')?.textContent?.trim() || 'not found'
            };
        }""")
        print(f"Email meta: {json.dumps(email_meta, indent=2)}")

        await page.screenshot(path=f"{SCREENSHOT_DIR}/013-email-detail.png", full_page=True)
        print(f"Screenshot: 013-email-detail.png")

        # =========================
        # NAV BAR DETAILED AUDIT
        # =========================
        print("\n=== NAV BAR AUDIT ===")
        nav_meta = await page.evaluate("""() => {
            const nav = document.querySelector('nav, header, .navbar, .topbar');
            return {
                navContent: nav ? nav.textContent.trim().replace(/\\s+/g, ' ') : 'no nav found',
                navButtons: Array.from(document.querySelectorAll('nav button, header button, .tab-btn')).map(b => ({
                    text: b.textContent.trim(),
                    active: b.classList.contains('active'),
                    class: b.className.substring(0, 60)
                })),
                userInfo: {
                    name: document.querySelector('.user-name, .username, [class*="user-name"]')?.textContent?.trim() || 'not found',
                    role: document.querySelector('.user-role, .role, [class*="role"]')?.textContent?.trim() || 'not found',
                },
                syncSetupBtn: !!document.querySelector('[class*="sync"], button:has-text("Sync Setup")'),
                cardViewBtn: !!document.querySelector('button:has-text("Card View")')
            };
        }""")
        print(f"Nav meta: {json.dumps(nav_meta, indent=2)}")

        # Final console summary
        print(f"\n=== CONSOLE SUMMARY ===")
        print(f"Total messages: {len(console_all)}")
        print(f"Errors: {len(console_errors)}")
        for e in console_errors:
            print(f"  [ERROR] {e['text'][:300]}")

        # Print all console messages for completeness
        if console_all:
            print("\nAll console messages:")
            for msg in console_all:
                print(f"  [{msg['time']}] [{msg['type']}] {msg['text'][:200]}")
        else:
            print("No console messages at all (clean)")

        await browser.close()

        return {
            "task_meta": task_meta,
            "team_meta": team_meta,
            "cal_meta": cal_meta,
            "email_meta": email_meta,
            "nav_meta": nav_meta,
            "console_errors": console_errors,
            "console_all": console_all
        }

if __name__ == "__main__":
    results = asyncio.run(run())
    out_path = "/home/jared/projects/AI-CIV/aether/exports/cc-tab-detail-20260228.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved: {out_path}")
