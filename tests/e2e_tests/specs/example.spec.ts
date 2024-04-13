import { test, expect } from '@playwright/test';

test('has μEditor title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/μEditor/);
});

/*
test('get started link', async ({ page }) => {
  await page.goto('https://playwright.dev/');

  // Click the get started link.
  await page.getByRole('link', { name: 'Get started' }).click();

  // Expects page to have a heading with the name of Installation.
  await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
});
*/
