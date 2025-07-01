const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Satellite Catalog & Crawler UI', () => {
  const fileUrl = 'file://' + path.resolve(__dirname, 'satellite_info_test.html');

  test('Crawler controls and satellite grid', async ({ page }) => {
    await page.goto(fileUrl);

    // Run Web Crawler
    await page.click('text=Run Web Crawler');
    await expect(page.locator('#crawler-status')).toBeVisible();
    await expect(page.locator('#crawler-message')).toContainText(/Starting web crawler|Crawler completed/i);

    // Update Catalog Data
    await page.click('text=Update Catalog Data');
    await expect(page.locator('#activity-log')).toContainText(/Update Catalog Data|update catalog/i);

    // Refresh Satellite List
    await page.click('text=Refresh Satellite List');
    await expect(page.locator('#activity-log')).toContainText(/Refresh Satellite List|refresh satellite/i);

    // Export Data
    await page.click('text=Export Data');
    await expect(page.locator('#activity-log')).toContainText(/Export Data|export data/i);

    // Interact with satellite cards
    const satelliteNames = ['Landsat 8', 'Sentinel-2', 'Sentinel-1', 'MODIS'];
    for (const name of satelliteNames) {
      // Click View Details
      await page.click(`button:has-text("View Details") >> xpath=ancestor::div[contains(., '${name}')]`);
      // Click Download
      await page.click(`button:has-text("Download") >> xpath=ancestor::div[contains(., '${name}')]`);
      // Click Info
      await page.click(`button:has-text("Info") >> xpath=ancestor::div[contains(., '${name}')]`);
      await expect(page.locator('#activity-log')).toContainText(new RegExp(name, 'i'));
    }

    // Test filter dropdown
    await page.selectOption('#satellite-category-filter', 'optical');
    await expect(page.locator('#activity-log')).toContainText(/optical/i);

    // Test advanced features
    await page.click('text=Test API');
    await page.click('text=Simulate Error');
    await page.click('text=Reset System');
    await page.click('text=Generate Report');
    await expect(page.locator('#activity-log')).toContainText(/API|Error|Reset|Report/i);
  });
}); 