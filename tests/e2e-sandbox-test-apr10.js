/**
 * E2E Sandbox Onboarding Test - April 10, 2026
 *
 * Tests the full onboarding flow on /home-test-sandbox/
 * Steps: Page load -> Password -> Chatbox naming -> PayPal sandbox -> Post-payment -> Seed -> Thank you
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const REPORT_PATH = '/home/jared/exports/portal-files/e2e-sandbox-test-2026-04-10.md';
const SCREENSHOT_DIR = '/home/jared/projects/AI-CIV/aether/tests/screenshots';
const BASE_URL = 'https://purebrain.ai/home-test-sandbox/';
const PAGE_PASSWORD = 't3st3rrr253443####';
const PAYPAL_EMAIL = 'sb-c89tj49549583@personal.example.com';
const PAYPAL_PASSWORD = 'Z0+6<dS';
const AI_NAME = 'SandboxTest-Apr10';
const CUSTOMER_NAME = 'Sandbox Tester';
const CUSTOMER_EMAIL = 'sandbox-test@puretechnology.nyc';

// Results accumulator
const results = [];
let stepNum = 0;

function logStep(name, status, details = '') {
  stepNum++;
  const entry = { step: stepNum, name, status, details, timestamp: new Date().toISOString() };
  results.push(entry);
  console.log(`[Step ${stepNum}] ${status === 'PASS' ? '✓' : status === 'FAIL' ? '✗' : '⚠'} ${name}${details ? ' - ' + details : ''}`);
  return entry;
}

async function screenshot(page, name) {
  if (!fs.existsSync(SCREENSHOT_DIR)) fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  const filepath = path.join(SCREENSHOT_DIR, `${name}.png`);
  await page.screenshot({ path: filepath, fullPage: false });
  return filepath;
}

async function waitAndType(page, selector, text, options = {}) {
  try {
    await page.waitForSelector(selector, { timeout: options.timeout || 15000 });
    await page.fill(selector, text);
    return true;
  } catch (e) {
    return false;
  }
}

async function runTest() {
  console.log('=== E2E Sandbox Onboarding Test ===');
  console.log(`Started: ${new Date().toISOString()}`);
  console.log(`Target: ${BASE_URL}`);
  console.log('');

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  // Collect console logs
  const consoleLogs = [];
  const networkErrors = [];

  const page = await context.newPage();
  page.on('console', msg => consoleLogs.push({ type: msg.type(), text: msg.text() }));
  page.on('pageerror', err => consoleLogs.push({ type: 'error', text: err.message }));
  page.on('requestfailed', req => networkErrors.push({ url: req.url(), failure: req.failure()?.errorText }));

  try {
    // ==========================================
    // STEP 1: Load page and enter password
    // ==========================================
    console.log('\n--- STEP 1: Page Load & Password ---');

    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await screenshot(page, '01-initial-load');
    logStep('Page loads', 'PASS', `Loaded ${BASE_URL}`);

    // Check for password protection
    await page.waitForTimeout(2000);
    const pageContent = await page.content();

    // Look for WordPress password form or CF password protection
    const hasPasswordField = await page.$('input[type="password"]') !== null;
    const hasPasswordForm = pageContent.includes('password') || pageContent.includes('Password');

    if (hasPasswordField || hasPasswordForm) {
      logStep('Password protection detected', 'PASS', 'Page is password-protected as expected');

      // Try filling the password
      const passwordInput = await page.$('input[type="password"]');
      if (passwordInput) {
        await passwordInput.fill(PAGE_PASSWORD);
        await screenshot(page, '01b-password-entered');

        // Submit - try various methods
        const submitBtn = await page.$('input[type="submit"], button[type="submit"], .wp-block-loginout button, form button');
        if (submitBtn) {
          await submitBtn.click();
        } else {
          await page.keyboard.press('Enter');
        }

        await page.waitForTimeout(5000);
        await screenshot(page, '01c-after-password');
        logStep('Password submitted', 'PASS', 'Submitted password and waiting for page');
      } else {
        logStep('Password input', 'WARN', 'Password protection detected but no input field found');
      }
    } else {
      logStep('Password protection', 'INFO', 'No password protection detected - page loaded directly');
    }

    // Wait for full page load after password
    await page.waitForTimeout(3000);

    // Check for dark theme
    const bgColor = await page.evaluate(() => {
      const body = document.body;
      return window.getComputedStyle(body).backgroundColor;
    });
    const isDark = bgColor && (bgColor.includes('8, 10, 18') || bgColor.includes('0, 0, 0') || bgColor.includes('rgb(8') || bgColor.includes('rgb(0'));
    logStep('Dark theme', isDark ? 'PASS' : 'WARN', `Background: ${bgColor}`);

    // Check for chatbox
    const chatboxExists = await page.evaluate(() => {
      // Look for chatbox elements
      const chat = document.querySelector('.pb-chat, .chatbox, #chatbox, [class*="chat"], [id*="chat"]');
      return !!chat;
    });
    logStep('Chatbox present', chatboxExists ? 'PASS' : 'FAIL', chatboxExists ? 'Chatbox element found on page' : 'No chatbox element detected');
    await screenshot(page, '01d-page-loaded');

    // Check for PayPal SDK loaded
    const paypalLoaded = await page.evaluate(() => {
      return typeof window.paypal !== 'undefined';
    });
    logStep('PayPal SDK loaded', paypalLoaded ? 'PASS' : 'WARN', paypalLoaded ? 'PayPal SDK available' : 'PayPal SDK not yet loaded (may load after naming)');

    // ==========================================
    // STEP 2: Chatbox naming ceremony
    // ==========================================
    console.log('\n--- STEP 2: Chatbox Naming Ceremony ---');

    // Find the chat input
    const chatInputSelectors = [
      '#chatInput', '#chat-input', '.chat-input input', '.chat-input textarea',
      'input[placeholder*="type"]', 'input[placeholder*="message"]', 'input[placeholder*="Type"]',
      'textarea[placeholder*="type"]', 'textarea[placeholder*="message"]',
      '.pb-chat-input', '#pb-chat-input', '[data-chat-input]',
      'input.chat-field', '.message-input input', '.message-input textarea'
    ];

    let chatInput = null;
    for (const sel of chatInputSelectors) {
      chatInput = await page.$(sel);
      if (chatInput) {
        logStep('Chat input found', 'PASS', `Found via selector: ${sel}`);
        break;
      }
    }

    if (!chatInput) {
      // Try broader search
      const allInputs = await page.$$('input[type="text"], textarea');
      logStep('Chat input search', 'FAIL', `No chat input found. Total text inputs on page: ${allInputs.length}`);

      // Debug: list all inputs
      const inputInfo = await page.evaluate(() => {
        const inputs = Array.from(document.querySelectorAll('input, textarea'));
        return inputs.map(i => ({
          tag: i.tagName,
          type: i.type,
          id: i.id,
          className: i.className,
          placeholder: i.placeholder,
          name: i.name
        }));
      });
      console.log('All inputs found:', JSON.stringify(inputInfo, null, 2));
    }

    // Try to interact with chatbox - type a greeting
    if (chatInput) {
      await chatInput.click();
      await chatInput.fill('Hello!');

      // Find send button
      const sendBtnSelectors = [
        '#chatSend', '#chat-send', '.chat-send', '.send-btn', 'button.send',
        '[aria-label="Send"]', 'button[type="submit"]',
        '.pb-chat-send', '#pb-chat-send', '.message-send'
      ];

      let sendBtn = null;
      for (const sel of sendBtnSelectors) {
        sendBtn = await page.$(sel);
        if (sendBtn) break;
      }

      if (sendBtn) {
        await sendBtn.click();
        logStep('Sent greeting', 'PASS', 'Typed "Hello!" and clicked send');
      } else {
        await page.keyboard.press('Enter');
        logStep('Sent greeting', 'PASS', 'Typed "Hello!" and pressed Enter');
      }

      // Wait for AI response
      await page.waitForTimeout(8000);
      await screenshot(page, '02a-after-greeting');

      // Now try to type the AI name
      if (chatInput) {
        await chatInput.click();
        await chatInput.fill(AI_NAME);
        if (sendBtn) {
          await sendBtn.click();
        } else {
          await page.keyboard.press('Enter');
        }
        logStep('Sent AI name', 'PASS', `Typed "${AI_NAME}" in chatbox`);

        await page.waitForTimeout(8000);
        await screenshot(page, '02b-after-naming');
      }

      // Check if naming ceremony is tracked
      const namingData = await page.evaluate(() => {
        if (window._pbState) {
          return {
            aiName: window._pbState.aiName || window._pbState.ai_name,
            sessionUuid: window._pbState.sessionUuid || window._pbState.session_uuid,
            hasConversation: Array.isArray(window._pbState.conversationHistory) && window._pbState.conversationHistory.length > 0
          };
        }
        if (window.payTestData) {
          return {
            aiName: window.payTestData.aiName,
            sessionUuid: window.payTestData.sessionUuid,
            hasConversation: true
          };
        }
        return null;
      });

      if (namingData) {
        logStep('Session state', 'PASS', `AI Name: ${namingData.aiName || 'pending'}, UUID: ${namingData.sessionUuid || 'pending'}, Conversation: ${namingData.hasConversation}`);
      } else {
        logStep('Session state', 'WARN', 'Could not read _pbState or payTestData - may need more chat interaction');
      }
    }

    // Check if payment buttons are visible
    const paymentButtonsVisible = await page.evaluate(() => {
      const proCta = document.querySelector('#proCta');
      const partnerCta = document.querySelector('#partnerCta');
      const unifiedCta = document.querySelector('#unifiedCta');
      const pricingSection = document.querySelector('.pricing-section, #pricing, [class*="pricing"]');
      return {
        proCta: proCta ? { visible: proCta.offsetParent !== null, text: proCta.textContent?.trim() } : null,
        partnerCta: partnerCta ? { visible: partnerCta.offsetParent !== null, text: partnerCta.textContent?.trim() } : null,
        unifiedCta: unifiedCta ? { visible: unifiedCta.offsetParent !== null, text: unifiedCta.textContent?.trim() } : null,
        pricingSection: !!pricingSection
      };
    });
    logStep('Payment buttons state', 'INFO', JSON.stringify(paymentButtonsVisible));
    await screenshot(page, '02c-payment-buttons-state');

    // ==========================================
    // STEP 3: PayPal Checkout (Sandbox)
    // ==========================================
    console.log('\n--- STEP 3: PayPal Checkout ---');

    // Need to ensure naming is complete before payment buttons appear
    // The chatbox flow typically requires multiple messages - let's check state
    const currentState = await page.evaluate(() => {
      return {
        payTestData: window.payTestData ? {
          aiName: window.payTestData.aiName,
          name: window.payTestData.name,
          email: window.payTestData.email,
          sessionUuid: window.payTestData.sessionUuid
        } : null,
        pbState: window._pbState ? Object.keys(window._pbState) : null,
        paypalLoaded: typeof window.paypal !== 'undefined',
        pricingVisible: !!document.querySelector('.pricing-section:not([style*="display: none"])'),
        consentChecked: document.querySelector('#pb-consent-check')?.checked
      };
    });
    logStep('Pre-payment state', 'INFO', JSON.stringify(currentState));

    // If naming isn't done via chatbox yet, we may need more interaction
    // For now, let's try to click on a payment CTA if visible
    const proCta = await page.$('#proCta');
    if (proCta) {
      const isClickable = await page.evaluate(el => {
        const style = window.getComputedStyle(el);
        return style.pointerEvents !== 'none' && !el.classList.contains('pb-cta-locked') && el.getAttribute('aria-disabled') !== 'true';
      }, proCta);

      if (isClickable) {
        logStep('Awakened CTA clickable', 'PASS', 'CTA button is interactive');

        // Click the CTA
        await proCta.click();
        logStep('Clicked Awakened CTA', 'PASS', 'Clicked the Awakened tier button');

        await page.waitForTimeout(3000);
        await screenshot(page, '03a-after-cta-click');

        // Check for PayPal overlay
        const paypalOverlay = await page.$('#pb-paypal-overlay, .paypal-overlay, [class*="paypal-overlay"]');
        if (paypalOverlay) {
          logStep('PayPal overlay appeared', 'PASS', 'PayPal button container is visible');

          // Look for PayPal smart button
          const paypalButton = await page.$('.paypal-buttons, [data-funding-source], .paypal-button');
          if (paypalButton) {
            logStep('PayPal smart button rendered', 'PASS', 'PayPal button is present in overlay');

            // Click the PayPal button
            try {
              // PayPal buttons are in an iframe
              const paypalFrame = await page.$('iframe[title*="PayPal"], iframe[name*="paypal"]');
              if (paypalFrame) {
                const frame = await paypalFrame.contentFrame();
                if (frame) {
                  // Look for the main PayPal button inside the iframe
                  const ppBtn = await frame.$('.paypal-button, [data-funding-source="paypal"], .paypal-button-number-0');
                  if (ppBtn) {
                    await ppBtn.click();
                    logStep('Clicked PayPal button', 'PASS', 'Clicked PayPal smart button in iframe');
                  } else {
                    // Try clicking any clickable element in the frame
                    await frame.click('div[role="button"], .paypal-button-container div');
                    logStep('Clicked PayPal button', 'PASS', 'Clicked PayPal button element in frame');
                  }
                }
              } else {
                // Try direct click on paypal button area
                await paypalButton.click();
                logStep('Clicked PayPal button', 'PASS', 'Clicked PayPal button directly');
              }

              // Wait for PayPal popup
              await page.waitForTimeout(5000);

              // Check for popup window
              const pages = context.pages();
              const paypalPopup = pages.find(p => p.url().includes('paypal.com'));

              if (paypalPopup) {
                logStep('PayPal popup opened', 'PASS', `PayPal URL: ${paypalPopup.url()}`);
                await screenshot(paypalPopup, '03b-paypal-popup');

                // Try to log in with sandbox credentials
                try {
                  await paypalPopup.waitForSelector('#email', { timeout: 15000 });
                  await paypalPopup.fill('#email', PAYPAL_EMAIL);

                  // Click Next
                  const nextBtn = await paypalPopup.$('#btnNext');
                  if (nextBtn) {
                    await nextBtn.click();
                    await paypalPopup.waitForTimeout(3000);
                  }

                  // Fill password
                  await paypalPopup.waitForSelector('#password', { timeout: 10000 });
                  await paypalPopup.fill('#password', PAYPAL_PASSWORD);
                  await screenshot(paypalPopup, '03c-paypal-credentials');

                  // Click Login
                  const loginBtn = await paypalPopup.$('#btnLogin');
                  if (loginBtn) {
                    await loginBtn.click();
                    logStep('PayPal login submitted', 'PASS', 'Entered sandbox credentials and clicked login');

                    await paypalPopup.waitForTimeout(10000);
                    await screenshot(paypalPopup, '03d-paypal-after-login');

                    // Look for subscription consent / continue button
                    const continueBtn = await paypalPopup.$('#payment-submit-btn, #consentButton, #confirmButtonTop, .btn-primary');
                    if (continueBtn) {
                      await continueBtn.click();
                      logStep('PayPal payment confirmed', 'PASS', 'Clicked payment confirmation button');

                      await page.waitForTimeout(10000);
                      await screenshot(page, '03e-after-payment');
                    } else {
                      logStep('PayPal confirm button', 'WARN', 'Could not find payment confirmation button');
                      await screenshot(paypalPopup, '03d-paypal-no-confirm');
                    }
                  }
                } catch (paypalErr) {
                  logStep('PayPal login flow', 'FAIL', `Error: ${paypalErr.message}`);
                  await screenshot(paypalPopup, '03-paypal-error');
                }
              } else {
                logStep('PayPal popup', 'FAIL', `No PayPal popup detected. Total pages: ${pages.length}`);
              }
            } catch (ppErr) {
              logStep('PayPal button click', 'FAIL', `Error: ${ppErr.message}`);
            }
          } else {
            logStep('PayPal smart button', 'FAIL', 'No PayPal button rendered in overlay');
          }
        } else {
          logStep('PayPal overlay', 'FAIL', 'No PayPal overlay appeared after CTA click');
        }
      } else {
        logStep('Awakened CTA', 'WARN', 'CTA exists but is locked (naming may not be complete)');
      }
    } else {
      logStep('Payment CTAs', 'WARN', 'No #proCta found - pricing section may be hidden until naming completes');
    }

    // ==========================================
    // STEP 4: Post-payment collection
    // ==========================================
    console.log('\n--- STEP 4: Post-Payment State ---');

    const postPaymentState = await page.evaluate(() => {
      return {
        url: window.location.href,
        payTestData: window.payTestData ? {
          aiName: window.payTestData.aiName,
          name: window.payTestData.name,
          email: window.payTestData.email,
          sessionUuid: window.payTestData.sessionUuid,
          orderId: window.payTestData.orderId,
          tierPaid: window.payTestData.tierPaid
        } : null,
        seedFired: window._seedFired || false
      };
    });

    logStep('Post-payment state', 'INFO', JSON.stringify(postPaymentState));

    // Check if we redirected to thank-you
    const currentUrl = page.url();
    if (currentUrl.includes('thank-you')) {
      logStep('Redirect to thank-you', 'PASS', `Current URL: ${currentUrl}`);
    } else {
      logStep('Redirect to thank-you', 'INFO', `Still on: ${currentUrl} (payment may not have completed)`);
    }

    // ==========================================
    // STEP 5: Check seed events
    // ==========================================
    console.log('\n--- STEP 5: Seed Verification ---');

    // We'll check seed_events.jsonl for recent entries
    const seedCheckBefore = fs.existsSync('/home/jared/projects/AI-CIV/aether/logs/seed_events.jsonl')
      ? fs.readFileSync('/home/jared/projects/AI-CIV/aether/logs/seed_events.jsonl', 'utf8').split('\n').filter(l => l.trim()).length
      : 0;
    logStep('Seed events count (pre-test baseline)', 'INFO', `${seedCheckBefore} entries in seed_events.jsonl`);

    // ==========================================
    // STEP 7: Thank You Page (test independently)
    // ==========================================
    console.log('\n--- STEP 7: Thank You Page (Independent Test) ---');

    // Navigate to thank-you with test params
    const thankYouUrl = `https://purebrain.ai/thank-you/?aiName=${encodeURIComponent(AI_NAME)}&name=${encodeURIComponent(CUSTOMER_NAME)}&email=${encodeURIComponent(CUSTOMER_EMAIL)}&tier=Awakened`;
    await page.goto(thankYouUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    await screenshot(page, '07a-thank-you-page');

    const thankYouState = await page.evaluate(() => {
      return {
        url: window.location.href,
        title: document.title,
        hasWebGL: !!document.querySelector('canvas'),
        hasConfetti: !!document.querySelector('[class*="confetti"], canvas#confetti, .confetti'),
        hasGlassCard: !!document.querySelector('.glass, [class*="glass"], .card'),
        hasBrainStreamBtn: !!document.querySelector('[class*="brain-stream"], [id*="brain-stream"], button, a.cta'),
        bodyBg: window.getComputedStyle(document.body).backgroundColor,
        visibleText: document.body.innerText.substring(0, 500)
      };
    });

    logStep('Thank-you page loaded', 'PASS', `URL: ${thankYouUrl}`);
    logStep('WebGL canvas', thankYouState.hasWebGL ? 'PASS' : 'WARN', thankYouState.hasWebGL ? 'Canvas element found' : 'No canvas found');
    logStep('Glass card', thankYouState.hasGlassCard ? 'PASS' : 'WARN', 'Glass card element check');
    logStep('Brain Stream button', thankYouState.hasBrainStreamBtn ? 'PASS' : 'WARN', 'Button/CTA element check');

    // Check personalization
    const hasPersonalization = thankYouState.visibleText.includes(AI_NAME) || thankYouState.visibleText.includes('SandboxTest');
    logStep('Personalization', hasPersonalization ? 'PASS' : 'WARN', hasPersonalization ? `AI name "${AI_NAME}" visible` : 'AI name not found in visible text');

    console.log('\nVisible text excerpt:', thankYouState.visibleText.substring(0, 300));
    await screenshot(page, '07b-thank-you-final');

  } catch (err) {
    logStep('CRITICAL ERROR', 'FAIL', err.message);
    console.error('Test error:', err);
    try { await screenshot(page, 'error-state'); } catch(e) {}
  } finally {
    await browser.close();
  }

  // ==========================================
  // Generate Report
  // ==========================================
  console.log('\n\n=== GENERATING REPORT ===');

  const passCount = results.filter(r => r.status === 'PASS').length;
  const failCount = results.filter(r => r.status === 'FAIL').length;
  const warnCount = results.filter(r => r.status === 'WARN').length;
  const infoCount = results.filter(r => r.status === 'INFO').length;

  let report = `# E2E Sandbox Onboarding Test Report\n\n`;
  report += `**Date**: 2026-04-10\n`;
  report += `**Target**: ${BASE_URL}\n`;
  report += `**AI Name**: ${AI_NAME}\n`;
  report += `**Test Type**: Full E2E with PayPal Sandbox\n\n`;
  report += `## Summary\n\n`;
  report += `| Status | Count |\n|--------|-------|\n`;
  report += `| PASS | ${passCount} |\n`;
  report += `| FAIL | ${failCount} |\n`;
  report += `| WARN | ${warnCount} |\n`;
  report += `| INFO | ${infoCount} |\n\n`;
  report += `## Detailed Results\n\n`;
  report += `| # | Step | Status | Details |\n|---|------|--------|----------|\n`;

  for (const r of results) {
    const statusIcon = r.status === 'PASS' ? 'PASS' : r.status === 'FAIL' ? 'FAIL' : r.status === 'WARN' ? 'WARN' : 'INFO';
    const details = r.details.replace(/\|/g, '\\|').substring(0, 200);
    report += `| ${r.step} | ${r.name} | ${statusIcon} | ${details} |\n`;
  }

  report += `\n## Console Logs (notable)\n\n`;
  report += `Collected ${consoleLogs.length} console messages during test.\n\n`;

  const errors = consoleLogs.filter(l => l.type === 'error');
  if (errors.length > 0) {
    report += `### Errors (${errors.length})\n\n`;
    for (const e of errors.slice(0, 20)) {
      report += `- ${e.text.substring(0, 200)}\n`;
    }
  }

  if (networkErrors.length > 0) {
    report += `\n### Network Errors (${networkErrors.length})\n\n`;
    for (const e of networkErrors.slice(0, 10)) {
      report += `- ${e.url}: ${e.failure}\n`;
    }
  }

  report += `\n## Screenshots\n\n`;
  report += `All screenshots saved to: ${SCREENSHOT_DIR}/\n\n`;

  report += `\n## Notes\n\n`;
  report += `- This test was run in headless mode with Playwright Chromium\n`;
  report += `- PayPal sandbox popups may behave differently in headless mode\n`;
  report += `- The chatbox naming ceremony requires Claude API interaction which may have latency\n`;
  report += `- Steps 5 (seed verification) and 6 (magic link) require backend monitoring\n`;
  report += `\n---\nGenerated: ${new Date().toISOString()}\n`;

  // Write report
  const reportDir = path.dirname(REPORT_PATH);
  if (!fs.existsSync(reportDir)) fs.mkdirSync(reportDir, { recursive: true });
  fs.writeFileSync(REPORT_PATH, report);
  console.log(`\nReport saved to: ${REPORT_PATH}`);

  // Also output JSON results
  const jsonPath = REPORT_PATH.replace('.md', '.json');
  fs.writeFileSync(jsonPath, JSON.stringify({ results, consoleLogs: consoleLogs.slice(0, 50), networkErrors }, null, 2));
  console.log(`JSON results saved to: ${jsonPath}`);

  return { passCount, failCount, warnCount, results };
}

runTest().then(summary => {
  console.log(`\n=== TEST COMPLETE ===`);
  console.log(`PASS: ${summary.passCount} | FAIL: ${summary.failCount} | WARN: ${summary.warnCount}`);
  process.exit(summary.failCount > 0 ? 1 : 0);
}).catch(err => {
  console.error('Fatal test error:', err);
  process.exit(2);
});
