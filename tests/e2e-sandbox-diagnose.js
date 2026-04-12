const { chromium } = require('playwright');
const fs = require('fs');

async function diagnose() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  console.log('Loading page...');
  await page.goto('https://purebrain.ai/home-test-sandbox/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);

  // Get full page HTML structure for the password form
  const formInfo = await page.evaluate(() => {
    const forms = Array.from(document.querySelectorAll('form'));
    const inputs = Array.from(document.querySelectorAll('input'));
    const buttons = Array.from(document.querySelectorAll('button, input[type="submit"]'));

    return {
      title: document.title,
      url: document.location.href,
      bodyClass: document.body.className,
      forms: forms.map(f => ({
        id: f.id,
        action: f.action,
        method: f.method,
        class: f.className,
        innerHTML: f.innerHTML.substring(0, 500)
      })),
      inputs: inputs.map(i => ({
        type: i.type,
        name: i.name,
        id: i.id,
        class: i.className,
        visible: i.offsetParent !== null,
        value: i.type !== 'password' ? i.value : '***',
        placeholder: i.placeholder
      })),
      buttons: buttons.map(b => ({
        tag: b.tagName,
        type: b.type,
        text: b.textContent?.trim()?.substring(0, 50),
        id: b.id,
        class: b.className,
        visible: b.offsetParent !== null,
        value: b.value
      })),
      bodyHTML: document.body.innerHTML.substring(0, 3000)
    };
  });

  console.log('\n=== PAGE STRUCTURE ===');
  console.log('Title:', formInfo.title);
  console.log('URL:', formInfo.url);
  console.log('Body class:', formInfo.bodyClass);

  console.log('\n=== FORMS ===');
  for (const f of formInfo.forms) {
    console.log(`Form: id="${f.id}" action="${f.action}" method="${f.method}" class="${f.class}"`);
    console.log('  HTML:', f.innerHTML.substring(0, 300));
  }

  console.log('\n=== INPUTS ===');
  for (const i of formInfo.inputs) {
    console.log(`Input: type="${i.type}" name="${i.name}" id="${i.id}" visible=${i.visible} class="${i.class}"`);
  }

  console.log('\n=== BUTTONS ===');
  for (const b of formInfo.buttons) {
    console.log(`${b.tag}: type="${b.type}" text="${b.text}" id="${b.id}" visible=${b.visible} value="${b.value}" class="${b.class}"`);
  }

  // Try to fill password and submit via JavaScript
  console.log('\n=== ATTEMPTING PASSWORD SUBMIT ===');

  // Fill the password
  const pwInput = await page.$('input[type="password"]');
  if (pwInput) {
    await pwInput.fill('t3st3rrr253443####');
    console.log('Password filled');

    // Try submitting the form via JS
    const submitted = await page.evaluate(() => {
      const form = document.querySelector('form');
      if (form) {
        form.submit();
        return 'form.submit() called';
      }
      return 'no form found';
    });
    console.log('Submit result:', submitted);

    await page.waitForTimeout(8000);
    await page.screenshot({ path: 'tests/screenshots/diag-after-submit.png' });

    // Check new page state
    const afterState = await page.evaluate(() => {
      return {
        url: document.location.href,
        title: document.title,
        hasChat: !!document.querySelector('[class*="chat"], [id*="chat"]'),
        hasPaypal: typeof window.paypal !== 'undefined',
        bodyLength: document.body.innerHTML.length,
        bodyText: document.body.innerText.substring(0, 500)
      };
    });
    console.log('\n=== AFTER SUBMIT ===');
    console.log('URL:', afterState.url);
    console.log('Title:', afterState.title);
    console.log('Has chat:', afterState.hasChat);
    console.log('Has PayPal:', afterState.hasPaypal);
    console.log('Body length:', afterState.bodyLength);
    console.log('Body text:', afterState.bodyText.substring(0, 300));
  }

  await browser.close();
}

diagnose().catch(e => { console.error(e); process.exit(1); });
