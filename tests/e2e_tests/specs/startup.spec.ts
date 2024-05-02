import { test, expect } from '@playwright/test';

test.beforeEach(async ({ request }) => {
  const response = await request.post("/api/tests/fixtures/simple");
  expect(response.status()).toBe(204);
});

test.afterEach(async ({ request }) => {
  const response = await request.delete("/api/tests/fixtures/simple");
  expect(response.status()).toBe(204);
})

test('Load configuration', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle('μEditor - Simple Fixture');
});
