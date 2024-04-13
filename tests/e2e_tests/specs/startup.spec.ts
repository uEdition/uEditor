import { test, expect } from '@playwright/test';

test('Load configuration', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle('μEditor - Test Project');
});
