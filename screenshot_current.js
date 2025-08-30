const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();
  
  try {
    await page.goto('http://localhost:3005', { waitUntil: 'networkidle' });
    await page.screenshot({ 
      path: 'current_site_screenshot.png', 
      fullPage: true 
    });
    console.log('Screenshot saved as current_site_screenshot.png');
  } catch (error) {
    console.error('Error taking screenshot:', error);
  } finally {
    await browser.close();
  }
})();