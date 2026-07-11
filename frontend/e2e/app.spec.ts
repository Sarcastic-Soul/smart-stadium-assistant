import { test, expect } from '@playwright/test';

test.describe('Smart Stadium Assistant E2E', () => {
  test('asks for restroom and verifies route polyline appears', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Verify the app loads
    await expect(page.locator('h1')).toContainText('Smart Stadium Assistant');

    // Type a question in the chat input
    const chatInput = page.locator('#chat-input');
    await chatInput.fill('Where is the nearest restroom?');

    // Click send
    const sendBtn = page.locator('#chat-send-btn');
    await sendBtn.click();

    // Wait for the assistant reply with a route
    const routePolyline = page.locator('[data-testid="route-polyline"]');
    await expect(routePolyline).toBeVisible({ timeout: 10000 });

    // Verify waypoints are rendered
    const waypoints = page.locator('.waypoint');
    const count = await waypoints.count();
    expect(count).toBeGreaterThan(0);
  });

  test('switches language to Spanish', async ({ page }) => {
    await page.goto('http://localhost:5173');
    const langSelect = page.locator('#language-selector');
    await langSelect.selectOption('es');
    await expect(page.locator('h1')).toContainText('Asistente Inteligente');
  });

  test('navigates to dashboard tab', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.click('[id="tab-dashboard"]');
    await expect(page.locator('.dashboard-title')).toBeVisible();
  });

  test('navigates to map tab', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.click('[id="tab-map"]');
    await expect(page.locator('.stadium-svg')).toBeVisible();
  });
});
