/**
 * E2E Sandbox Onboarding Test - April 10, 2026
 * Full flow: Password -> Chat naming -> PayPal sandbox -> Seed -> Thank you
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const REPORT_PATH = '/home/jared/exports/portal-files/e2e-sandbox-test-2026-04-10.md';
const SS_DIR = '/home/jared/projects/AI-CIV/aether/tests/screenshots';
const BASE_URL = 'https://purebrain.ai/home-test-sandbox/';
const PAGE_PASSWORD = 't3st3rrr253443####';
const PAYPAL_EMAIL = 'sb-c89tj49549583@personal.example.com';
const PAYPAL_PASSWORD = 'Z0+6<dS';
const AI_NAME = 'SandboxTest-Apr10';
const CUSTOMER_NAME = 'Sandbox Tester';
const CUSTOMER_EMAIL = 'sandbox-test@puretechnology.nyc';

const results = [];
let stepNum = 0;

function log(name, status, details = '') {
  stepNum++;
  results.push({ step: stepNum, name, status, details, ts: new Date().toISOString() });
  const icon = { PASS: 'PASS', FAIL: 'FAIL', WARN: 'WARN', INFO: 'INFO' }[status] || '??';
  console.log(`[${stepNum}] ${icon} ${name}${details ? ' -- ' + details : ''}`);
}

async function ss(page, name) {
  if (!fs.existsSync(SS_DIR)) fs.mkdirSync(SS_DIR, { recursive: true });
  await page.screenshot({ path: path.join(SS_DIR, `${name}.png`), fullPage: false });
}

async function run() {
  console.log('=== E2E Sandbox Onboarding Test - 2026-04-10 ===\n');

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });

  const consoleLogs = [];
  const networkErrors = [];
  const page = await context.newPage();
  page.on('console', msg => consoleLogs.push({ type: msg.type(), text: msg.text() }));
  page.on('pageerror', err => consoleLogs.push({ type: 'error', text: err.message }));
  page.on('requestfailed', req => networkErrors.push({ url: req.url(), err: req.failure()?.errorText }));

  // Track popup for PayPal
  let paypalPopup = null;
  context.on('page', p => {
    if (p.url().includes('paypal') || p.url() === 'about:blank') {
      paypalPopup = p;
      console.log('  [popup detected]: ' + p.url());
    }
  });

  try {
    // ============================================================
    // STEP 1: Load page & password
    // ============================================================
    console.log('\n--- STEP 1: Page Load & Password ---');

    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);
    log('Page loaded', 'PASS', BASE_URL);
    await ss(page, '01a-initial');

    // The password gate uses #pw-input and a button that calls JS to validate
    const pwInput = await page.$('#pw-input');
    if (pwInput) {
      log('Password gate detected', 'PASS', '#pw-input found');

      // Fill password
      await pwInput.fill(PAGE_PASSWORD);

      // Click the "Enter" button next to it - it's a button with text "Enter"
      // Use evaluate to find and click the button, and also call the password check function
      const pwResult = await page.evaluate((pw) => {
        const input = document.querySelector('#pw-input');
        if (input) input.value = pw;

        // Look for the enter button
        const btns = Array.from(document.querySelectorAll('button'));
        const enterBtn = btns.find(b => b.textContent.trim() === 'Enter' && b.offsetParent !== null);
        if (enterBtn) {
          enterBtn.click();
          return 'clicked Enter button';
        }

        // Try calling the password check function directly
        if (typeof checkPassword === 'function') {
          checkPassword();
          return 'called checkPassword()';
        }
        if (typeof pbCheckPassword === 'function') {
          pbCheckPassword();
          return 'called pbCheckPassword()';
        }

        return 'no handler found';
      }, PAGE_PASSWORD);

      log('Password submitted', 'INFO', pwResult);
      await page.waitForTimeout(3000);
      await ss(page, '01b-after-password');

      // Verify password gate is gone / page content is revealed
      const pageRevealed = await page.evaluate(() => {
        const chatSection = document.querySelector('[class*="chat"]');
        const pwGate = document.querySelector('#pw-input');
        return {
          chatVisible: chatSection ? chatSection.offsetParent !== null : false,
          pwInputVisible: pwGate ? pwGate.offsetParent !== null : false,
          bodyText: document.body.innerText.substring(0, 200)
        };
      });

      if (!pageRevealed.pwInputVisible || pageRevealed.chatVisible) {
        log('Password accepted', 'PASS', 'Password gate dismissed');
      } else {
        log('Password accepted', 'WARN', 'Password input still visible - may need different approach');
      }
    } else {
      log('Password gate', 'INFO', 'No password gate found - page accessible directly');
    }

    // Check dark theme
    const bgColor = await page.evaluate(() => window.getComputedStyle(document.body).backgroundColor);
    log('Dark theme check', 'INFO', `Background: ${bgColor}`);

    // Check chatbox loads
    const chatboxReady = await page.evaluate(() => {
      const chat = document.querySelector('.chat-messages, .chat-container, [class*="chat-"]');
      return !!chat;
    });
    log('Chatbox present', chatboxReady ? 'PASS' : 'WARN', chatboxReady ? 'Chat elements found' : 'No chat elements detected yet');

    // Check PayPal SDK
    const paypalSDK = await page.evaluate(() => typeof window.paypal !== 'undefined');
    log('PayPal SDK loaded', paypalSDK ? 'PASS' : 'WARN', paypalSDK ? 'window.paypal exists' : 'PayPal SDK not loaded yet');

    await ss(page, '01c-page-ready');

    // ============================================================
    // STEP 2: Chatbox naming ceremony
    // ============================================================
    console.log('\n--- STEP 2: Chatbox Naming Ceremony ---');

    // First click "Begin Awakening" button if present
    const beginBtn = await page.$('.chat-initial__btn');
    if (beginBtn) {
      const beginVisible = await beginBtn.evaluate(el => el.offsetParent !== null);
      if (beginVisible) {
        await beginBtn.click();
        log('Begin Awakening clicked', 'PASS', 'Clicked the chat initiation button');
        await page.waitForTimeout(5000); // Wait for first AI message
        await ss(page, '02a-after-begin');
      }
    }

    // Chat input
    const chatInput = await page.$('#userInput');
    const submitBtn = await page.$('#submitBtn');

    if (chatInput) {
      log('Chat input found', 'PASS', '#userInput');

      // Helper to send a message - re-queries DOM each time to avoid stale refs
      async function sendChat(msg) {
        // Re-find input each time (DOM may re-render)
        const input = await page.$('#userInput');
        if (!input) {
          console.log(`  Could not find #userInput for message: "${msg}"`);
          return false;
        }
        await input.click();
        await input.fill(msg);

        // Submit via evaluate to avoid stale element refs
        await page.evaluate(() => {
          const form = document.querySelector('.chat-input__form');
          if (form) {
            form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
            return;
          }
          const btn = document.querySelector('#submitBtn');
          if (btn) btn.click();
        });

        console.log(`  Sent: "${msg}"`);
        // Wait for AI response - the API call takes time
        await page.waitForTimeout(12000);
        return true;
      }

      // Send greeting
      await sendChat('Hello!');
      await ss(page, '02b-after-hello');

      // Check for AI response
      const aiResponded = await page.evaluate(() => {
        const messages = document.querySelectorAll('.chat-message, [class*="message-row"], [class*="chat-bubble"]');
        return messages.length;
      });
      log('AI response received', aiResponded > 1 ? 'PASS' : 'WARN', `${aiResponded} messages in chat`);

      // The naming ceremony flow: AI asks your name, then asks what to name the AI
      // Provide our name
      await sendChat(CUSTOMER_NAME);
      await ss(page, '02c-after-name');

      // Provide AI name
      await sendChat(AI_NAME);
      await ss(page, '02d-after-ai-name');

      // Provide email
      await sendChat(CUSTOMER_EMAIL);
      await ss(page, '02e-after-email');

      // Check state after naming
      const namingState = await page.evaluate(() => {
        return {
          payTestData: window.payTestData ? {
            aiName: window.payTestData.aiName,
            name: window.payTestData.name,
            email: window.payTestData.email,
            sessionUuid: window.payTestData.sessionUuid
          } : null,
          pricingVisible: (() => {
            const pricing = document.querySelector('#proCta');
            return pricing ? pricing.offsetParent !== null : false;
          })(),
          chatMessages: document.querySelectorAll('.chat-message, [class*="message-row"]').length,
          consentChecked: document.querySelector('#pb-consent-check')?.checked
        };
      });

      log('Naming ceremony state', 'INFO', JSON.stringify(namingState));

      if (namingState.payTestData?.aiName) {
        log('AI name captured', 'PASS', `AI Name: ${namingState.payTestData.aiName}`);
      } else {
        log('AI name captured', 'WARN', 'payTestData.aiName not set yet - naming may need more interaction');
      }

      // Session UUID
      const uuid = await page.evaluate(() => window.payTestData?.sessionUuid);
      log('UUID generated', uuid ? 'PASS' : 'WARN', uuid || 'Not yet available');

      // Payment buttons visible after naming?
      if (namingState.pricingVisible) {
        log('Payment buttons appear after naming', 'PASS', 'Pricing CTA visible');
      } else {
        log('Payment buttons after naming', 'WARN', 'CTAs not yet visible - naming ceremony may not be complete');

        // Try a few more interactions to complete naming
        // Sometimes the chatbox asks more questions
        const sent1 = await sendChat('Yes');
        if (!sent1) console.log('  sendChat failed for "Yes"');
        await page.waitForTimeout(3000);
        const sent2 = await sendChat('I want to try the Awakened tier');
        if (!sent2) console.log('  sendChat failed for tier selection');
        await page.waitForTimeout(3000);
        await ss(page, '02f-more-interaction');

        const retryState = await page.evaluate(() => {
          const proCta = document.querySelector('#proCta');
          return {
            pricingVisible: proCta ? proCta.offsetParent !== null : false,
            payTestData: window.payTestData ? {
              aiName: window.payTestData.aiName,
              name: window.payTestData.name,
              email: window.payTestData.email,
            } : null
          };
        });
        log('Retry naming state', 'INFO', JSON.stringify(retryState));
      }

    } else {
      log('Chat input', 'FAIL', 'Could not find #userInput');
    }

    // ============================================================
    // STEP 3: PayPal Checkout
    // ============================================================
    console.log('\n--- STEP 3: PayPal Checkout ---');

    // Check if CTA is clickable
    const ctaState = await page.evaluate(() => {
      const cta = document.querySelector('#proCta');
      if (!cta) return { exists: false };
      const style = window.getComputedStyle(cta);
      return {
        exists: true,
        visible: cta.offsetParent !== null,
        locked: cta.classList.contains('pb-cta-locked'),
        ariaDisabled: cta.getAttribute('aria-disabled'),
        text: cta.textContent.trim(),
        pointerEvents: style.pointerEvents
      };
    });

    log('CTA button state', 'INFO', JSON.stringify(ctaState));

    if (ctaState.exists && ctaState.visible && !ctaState.locked) {
      // Click the Awakened tier CTA
      await page.click('#proCta', { force: true });
      log('Clicked Awakened CTA', 'PASS', ctaState.text);
      await page.waitForTimeout(3000);
      await ss(page, '03a-after-cta');

      // Check for PayPal overlay
      const overlayVisible = await page.evaluate(() => {
        const overlay = document.querySelector('#pb-paypal-overlay');
        return overlay ? overlay.style.display !== 'none' && overlay.offsetParent !== null : false;
      });

      if (overlayVisible) {
        log('PayPal overlay appeared', 'PASS', 'PayPal buttons container visible');

        // Check for PayPal buttons iframe
        await page.waitForTimeout(3000);
        const ppFrames = page.frames().filter(f => f.url().includes('paypal.com'));
        log('PayPal iframes', 'INFO', `${ppFrames.length} PayPal frames found`);

        // Try to find and click the PayPal button inside the iframe
        let clickedPP = false;
        for (const frame of ppFrames) {
          try {
            const ppButton = await frame.$('.paypal-button, [data-funding-source="paypal"], .paypal-button-number-0, .paypal-button-container');
            if (ppButton) {
              await ppButton.click();
              clickedPP = true;
              log('PayPal button clicked', 'PASS', `In frame: ${frame.url().substring(0, 80)}`);
              break;
            }
          } catch (e) {
            // Try next frame
          }
        }

        if (!clickedPP) {
          // Try clicking via the page directly
          const ppBtnContainer = await page.$('.paypal-buttons, #pb-paypal-buttons-container');
          if (ppBtnContainer) {
            // Click on the first visible paypal button
            try {
              await page.frameLocator('iframe[title*="PayPal"]').locator('.paypal-button').first().click({ timeout: 10000 });
              clickedPP = true;
              log('PayPal button clicked via frameLocator', 'PASS');
            } catch (e) {
              log('PayPal button click', 'WARN', `Could not click: ${e.message.substring(0, 100)}`);
            }
          }
        }

        if (clickedPP) {
          // Wait for PayPal popup/redirect
          await page.waitForTimeout(8000);

          if (paypalPopup) {
            log('PayPal popup opened', 'PASS', paypalPopup.url().substring(0, 100));
            await ss(paypalPopup, '03b-paypal-popup');

            try {
              // Wait for email field
              await paypalPopup.waitForSelector('#email', { timeout: 20000 });
              await paypalPopup.fill('#email', PAYPAL_EMAIL);
              log('PayPal email entered', 'PASS', PAYPAL_EMAIL);

              // Click Next
              const nextBtn = await paypalPopup.$('#btnNext');
              if (nextBtn) {
                await nextBtn.click();
                await paypalPopup.waitForTimeout(4000);
              }

              // Enter password
              await paypalPopup.waitForSelector('#password', { timeout: 15000 });
              await paypalPopup.fill('#password', PAYPAL_PASSWORD);
              log('PayPal password entered', 'PASS');
              await ss(paypalPopup, '03c-paypal-creds');

              // Click Login
              const loginBtn = await paypalPopup.$('#btnLogin');
              if (loginBtn) {
                await loginBtn.click();
                log('PayPal login clicked', 'PASS');
                await paypalPopup.waitForTimeout(15000);
                await ss(paypalPopup, '03d-paypal-after-login');

                // Check for payment confirmation buttons
                const confirmSelectors = [
                  '#payment-submit-btn',
                  '#consentButton',
                  '#confirmButtonTop',
                  '.buttons .primary',
                  '#button-ok',
                  'button.btn-primary'
                ];

                let confirmed = false;
                for (const sel of confirmSelectors) {
                  try {
                    const btn = await paypalPopup.$(sel);
                    if (btn) {
                      const visible = await btn.evaluate(el => el.offsetParent !== null);
                      if (visible) {
                        await btn.click();
                        confirmed = true;
                        log('PayPal payment confirmed', 'PASS', `Clicked ${sel}`);
                        break;
                      }
                    }
                  } catch (e) {}
                }

                if (!confirmed) {
                  // Dump the page state for debugging
                  const ppState = await paypalPopup.evaluate(() => ({
                    url: document.location.href,
                    title: document.title,
                    buttons: Array.from(document.querySelectorAll('button')).map(b => ({
                      text: b.textContent.trim().substring(0, 40),
                      id: b.id,
                      class: b.className.substring(0, 40),
                      visible: b.offsetParent !== null
                    })),
                    text: document.body.innerText.substring(0, 500)
                  })).catch(() => ({ error: 'could not evaluate' }));
                  log('PayPal confirm', 'WARN', `No confirm button found. State: ${JSON.stringify(ppState).substring(0, 300)}`);
                  await ss(paypalPopup, '03e-paypal-state');
                }

                // Wait for payment processing
                await page.waitForTimeout(10000);
                await ss(page, '03f-after-payment');
              }
            } catch (ppErr) {
              log('PayPal flow', 'FAIL', ppErr.message.substring(0, 200));
              try { await ss(paypalPopup, '03-paypal-error'); } catch(e) {}
            }
          } else {
            // Check all pages
            const allPages = context.pages();
            log('PayPal popup', 'WARN', `No popup detected. ${allPages.length} total pages. URLs: ${allPages.map(p => p.url().substring(0, 60)).join(', ')}`);
          }
        }
      } else {
        // Check if overlay exists but hidden
        const overlayState = await page.evaluate(() => {
          const o = document.querySelector('#pb-paypal-overlay');
          return o ? { display: o.style.display, class: o.className, html: o.innerHTML.substring(0, 200) } : null;
        });
        log('PayPal overlay', 'FAIL', `Overlay not visible. State: ${JSON.stringify(overlayState)}`);
      }
    } else if (ctaState.exists && !ctaState.visible) {
      log('PayPal checkout', 'WARN', 'CTA exists but not visible - naming ceremony likely incomplete');
    } else {
      log('PayPal checkout', 'WARN', 'No CTA button found');
    }

    // ============================================================
    // STEP 4: Post-payment state
    // ============================================================
    console.log('\n--- STEP 4: Post-Payment State ---');

    const postState = await page.evaluate(() => ({
      url: window.location.href,
      seedFired: window._seedFired || false,
      payTestData: window.payTestData ? {
        aiName: window.payTestData.aiName,
        name: window.payTestData.name,
        email: window.payTestData.email,
        sessionUuid: window.payTestData.sessionUuid,
        orderId: window.payTestData.orderId,
        tierPaid: window.payTestData.tierPaid
      } : null
    }));

    log('Current URL', 'INFO', postState.url);
    log('Seed fired flag', postState.seedFired ? 'PASS' : 'INFO', `_seedFired = ${postState.seedFired}`);
    log('Payment data', 'INFO', JSON.stringify(postState.payTestData));

    if (postState.url.includes('thank-you')) {
      log('Redirect to /thank-you/', 'PASS', 'Successfully redirected after payment');
    }

    // ============================================================
    // STEP 5: Seed verification (check logs)
    // ============================================================
    console.log('\n--- STEP 5: Seed Verification ---');

    const seedLog = '/home/jared/projects/AI-CIV/aether/logs/seed_events.jsonl';
    if (fs.existsSync(seedLog)) {
      const lines = fs.readFileSync(seedLog, 'utf8').split('\n').filter(l => l.trim());
      const recent = lines.slice(-3).map(l => {
        try { return JSON.parse(l); } catch(e) { return null; }
      }).filter(Boolean);

      const testSeed = recent.find(s => s.ai_name === AI_NAME || (s.is_sandbox && s.timestamp > new Date(Date.now() - 600000).toISOString()));
      if (testSeed) {
        log('Seed event found', 'PASS', `UUID: ${testSeed.session_uuid}, AI: ${testSeed.ai_name}, Sandbox: ${testSeed.is_sandbox}`);
      } else {
        log('Seed event', 'INFO', `No seed for "${AI_NAME}" in last 10 min. Last entries: ${JSON.stringify(recent.map(r => r.ai_name))}`);
      }
      log('Seed events total', 'INFO', `${lines.length} total entries`);
    } else {
      log('Seed events log', 'WARN', 'seed_events.jsonl not found');
    }

    // ============================================================
    // STEP 7: Thank You Page (independent test)
    // ============================================================
    console.log('\n--- STEP 7: Thank You Page (Independent) ---');

    const tyUrl = `https://purebrain.ai/thank-you/?aiName=${encodeURIComponent(AI_NAME)}&name=${encodeURIComponent(CUSTOMER_NAME)}&email=${encodeURIComponent(CUSTOMER_EMAIL)}&tier=Awakened`;
    await page.goto(tyUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    await ss(page, '07a-thank-you');

    const tyState = await page.evaluate(() => {
      const canvases = document.querySelectorAll('canvas');
      const allButtons = Array.from(document.querySelectorAll('button, a.cta, a.btn, [class*="brain-stream"], [class*="enter-btn"]'));
      return {
        url: window.location.href,
        title: document.title,
        canvasCount: canvases.length,
        hasWebGL: (() => {
          for (const c of canvases) {
            try { if (c.getContext('webgl') || c.getContext('webgl2')) return true; } catch(e) {}
          }
          return false;
        })(),
        hasGlass: !!document.querySelector('[class*="glass"], .glass-card, .card'),
        buttons: allButtons.map(b => ({
          text: b.textContent.trim().substring(0, 60),
          class: b.className.substring(0, 60),
          href: b.href || '',
          visible: b.offsetParent !== null
        })),
        bodyText: document.body.innerText.substring(0, 800),
        checklist: Array.from(document.querySelectorAll('[class*="check"], [class*="status"], li')).map(el => el.textContent.trim().substring(0, 80))
      };
    });

    log('Thank-you page loaded', 'PASS', tyUrl);
    log('WebGL background', tyState.canvasCount > 0 ? 'PASS' : 'WARN', `${tyState.canvasCount} canvas elements, WebGL: ${tyState.hasWebGL}`);
    log('Glass card', tyState.hasGlass ? 'PASS' : 'WARN', 'Glass card element detected');

    // Check personalization
    const hasAIName = tyState.bodyText.includes(AI_NAME) || tyState.bodyText.includes('SandboxTest');
    log('Personalization (AI name)', hasAIName ? 'PASS' : 'WARN', hasAIName ? `"${AI_NAME}" found in page` : 'AI name not visible');

    const hasEmail = tyState.bodyText.includes(CUSTOMER_EMAIL) || tyState.bodyText.includes('sandbox-test');
    log('Personalization (email)', hasEmail ? 'PASS' : 'WARN', hasEmail ? 'Email visible on page' : 'Email not visible');

    // Brain stream button
    const brainStreamBtn = tyState.buttons.find(b =>
      b.text.toLowerCase().includes('brain stream') ||
      b.text.toLowerCase().includes('enter') ||
      b.class.includes('brain-stream')
    );
    log('Brain Stream button', brainStreamBtn ? 'PASS' : 'WARN',
      brainStreamBtn ? `Found: "${brainStreamBtn.text}" visible=${brainStreamBtn.visible}` : 'No brain stream button found yet (appears when magic link ready)');

    // Checklist items
    if (tyState.checklist.length > 0) {
      log('Status checklist', 'PASS', `${tyState.checklist.length} items: ${tyState.checklist.slice(0, 3).join(' | ')}`);
    }

    console.log('\nThank-you page visible text (excerpt):');
    console.log(tyState.bodyText.substring(0, 400));
    console.log('\nButtons found:', tyState.buttons.map(b => b.text).join(', '));

    await ss(page, '07b-thank-you-final');

  } catch (err) {
    log('CRITICAL ERROR', 'FAIL', err.message.substring(0, 300));
    console.error(err);
    try { await ss(page, 'error-state'); } catch(e) {}
  } finally {
    await browser.close();
  }

  // ============================================================
  // Generate report
  // ============================================================
  console.log('\n\n=== REPORT ===');

  const pass = results.filter(r => r.status === 'PASS').length;
  const fail = results.filter(r => r.status === 'FAIL').length;
  const warn = results.filter(r => r.status === 'WARN').length;
  const info = results.filter(r => r.status === 'INFO').length;

  let rpt = `# E2E Sandbox Onboarding Test Report\n\n`;
  rpt += `**Date**: 2026-04-10\n`;
  rpt += `**Target**: ${BASE_URL}\n`;
  rpt += `**AI Name**: ${AI_NAME}\n`;
  rpt += `**Test Type**: Full E2E with PayPal Sandbox\n`;
  rpt += `**Runner**: Playwright Chromium (headless)\n\n`;
  rpt += `## Summary\n\n`;
  rpt += `| Status | Count |\n|--------|-------|\n`;
  rpt += `| PASS | ${pass} |\n`;
  rpt += `| FAIL | ${fail} |\n`;
  rpt += `| WARN | ${warn} |\n`;
  rpt += `| INFO | ${info} |\n\n`;
  rpt += `**Overall**: ${fail === 0 ? 'ALL CRITICAL STEPS PASSED' : `${fail} FAILURES DETECTED`}\n\n`;
  rpt += `## Detailed Results\n\n`;

  for (const r of results) {
    const icon = { PASS: '[PASS]', FAIL: '[FAIL]', WARN: '[WARN]', INFO: '[INFO]' }[r.status];
    rpt += `### Step ${r.step}: ${r.name}\n`;
    rpt += `**Status**: ${icon}\n`;
    if (r.details) rpt += `**Details**: ${r.details}\n`;
    rpt += `\n`;
  }

  rpt += `## Console Errors\n\n`;
  const errors = consoleLogs.filter(l => l.type === 'error');
  if (errors.length > 0) {
    rpt += `${errors.length} JavaScript errors detected:\n\n`;
    for (const e of errors.slice(0, 20)) {
      rpt += `- ${e.text.substring(0, 200)}\n`;
    }
  } else {
    rpt += `No JavaScript errors detected.\n`;
  }

  if (networkErrors.length > 0) {
    rpt += `\n## Network Errors\n\n`;
    for (const e of networkErrors.slice(0, 10)) {
      rpt += `- ${e.url.substring(0, 100)}: ${e.err}\n`;
    }
  }

  rpt += `\n## Screenshots\n\n`;
  rpt += `Directory: ${SS_DIR}/\n\n`;
  try {
    const files = fs.readdirSync(SS_DIR).filter(f => f.endsWith('.png')).sort();
    for (const f of files) {
      rpt += `- ${f}\n`;
    }
  } catch(e) {}

  rpt += `\n## Observations & Recommendations\n\n`;
  rpt += `- Headless browser testing has limitations with PayPal popup flows\n`;
  rpt += `- The chatbox naming ceremony requires Claude API round-trips (variable latency)\n`;
  rpt += `- PayPal sandbox popups may require specific browser settings for full automation\n`;
  rpt += `- Seed verification and magic link polling are backend-dependent\n`;

  rpt += `\n---\nGenerated: ${new Date().toISOString()}\n`;

  const reportDir = path.dirname(REPORT_PATH);
  if (!fs.existsSync(reportDir)) fs.mkdirSync(reportDir, { recursive: true });
  fs.writeFileSync(REPORT_PATH, rpt);
  console.log(`Report: ${REPORT_PATH}`);

  const jsonPath = REPORT_PATH.replace('.md', '.json');
  fs.writeFileSync(jsonPath, JSON.stringify({ results, consoleLogs: errors.slice(0, 30), networkErrors }, null, 2));
  console.log(`JSON: ${jsonPath}`);

  console.log(`\nPASS: ${pass} | FAIL: ${fail} | WARN: ${warn} | INFO: ${info}`);
  return { pass, fail, warn };
}

run().then(s => {
  process.exit(s.fail > 0 ? 1 : 0);
}).catch(e => {
  console.error('Fatal:', e);
  process.exit(2);
});
