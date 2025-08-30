const { chromium } = require('playwright');

async function takeScreenshotAndKeepOpen() {
  // Launch browser in headed mode so user can see it
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true 
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  
  const page = await context.newPage();
  
  try {
    console.log('Navigating to http://localhost:3005...');
    await page.goto('http://localhost:3005');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    console.log('Taking baseline screenshot...');
    await page.screenshot({ 
      path: 'current-state-baseline.png', 
      fullPage: true 
    });
    
    console.log('✅ Baseline screenshot saved as current-state-baseline.png');
    console.log('🌐 Browser is open and ready for live viewing at http://localhost:3005');
    console.log('📋 Keep this browser window open to see changes in real-time');
    
    // Keep the browser open - don't close it
    // This allows user to see live changes
    console.log('Press Ctrl+C to close when done...');
    
    // Keep the script running
    await new Promise(() => {}); // This will never resolve, keeping browser open
    
  } catch (error) {
    console.error('Error:', error);
    await browser.close();
  }
}

takeScreenshotAndKeepOpen();