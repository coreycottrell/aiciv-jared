const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function testImageVisibility() {
  const outputDir = '/home/jared/projects/AI-CIV/aether/exports/qa-image-fix';

  // Create output directory if it doesn't exist
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Set viewport to desktop size
  await page.setViewportSize({ width: 1440, height: 900 });

  console.log('Navigating to purebrain.ai/your-ai-tim-cook/...');
  await page.goto('https://purebrain.ai/your-ai-tim-cook/', {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  // Wait for page to settle
  await page.waitForTimeout(2000);

  console.log('Taking initial screenshot...');
  let screenshot = await page.screenshot({ path: path.join(outputDir, '001-hero-section.png') });
  console.log('Screenshot saved: 001-hero-section.png');

  // Scroll down to find amplify-founder image (should be between Hero and "The Problem" section)
  console.log('\nScrolling to amplify-founder image location...');
  await page.evaluate(() => {
    // Scroll to approximately where the image should be
    window.scrollBy(0, 600);
  });

  await page.waitForTimeout(2000); // Wait for scroll animation and IntersectionObserver

  screenshot = await page.screenshot({ path: path.join(outputDir, '002-amplify-founder-image.png') });
  console.log('Screenshot saved: 002-amplify-founder-image.png');

  // Continue scrolling to vc-fomo image
  console.log('\nScrolling to vc-fomo image location...');
  await page.evaluate(() => {
    window.scrollBy(0, 800);
  });

  await page.waitForTimeout(2000); // Wait for scroll animation

  screenshot = await page.screenshot({ path: path.join(outputDir, '003-vc-fomo-image.png') });
  console.log('Screenshot saved: 003-vc-fomo-image.png');

  // Scroll down more to verify bottom section
  console.log('\nScrolling to closing CTA section...');
  await page.evaluate(() => {
    window.scrollBy(0, 800);
  });

  await page.waitForTimeout(2000);

  screenshot = await page.screenshot({ path: path.join(outputDir, '004-closing-cta.png') });
  console.log('Screenshot saved: 004-closing-cta.png');

  // Check image opacity values via JavaScript
  console.log('\nChecking image opacity values...');
  const imageData = await page.evaluate(() => {
    const images = Array.from(document.querySelectorAll('img[src*="amplify"], img[src*="vc-fomo"], img[class*="reveal"]'));
    return images.map(img => ({
      src: img.src,
      style: img.getAttribute('style'),
      computedOpacity: window.getComputedStyle(img).opacity,
      isVisible: window.getComputedStyle(img).opacity !== '0'
    }));
  });

  console.log('\nImage opacity check results:');
  imageData.forEach((img, idx) => {
    console.log(`\nImage ${idx + 1}:`);
    console.log(`  Src: ${img.src.substring(img.src.lastIndexOf('/'))}`);
    console.log(`  Inline style: ${img.style || 'none'}`);
    console.log(`  Computed opacity: ${img.computedOpacity}`);
    console.log(`  Visible: ${img.isVisible ? 'YES' : 'NO'}`);
  });

  await browser.close();

  console.log(`\nAll screenshots saved to: ${outputDir}`);
}

testImageVisibility().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
