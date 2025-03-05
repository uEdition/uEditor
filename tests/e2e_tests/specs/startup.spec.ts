import { test, expect } from "@playwright/test";

test.afterEach(async ({ request }) => {
  const response = await request.delete("/api/tests/fixtures");
  expect(response.status()).toBe(204);
});

test("Test loading default configuration", async ({ request, page }) => {
  let response = await request.post("/api/tests/fixtures/empty");
  expect(response.status()).toBe(204);
  response = await request.post("/api/auth/login");
  expect(response.status()).toBe(204);
  await page.goto("/");
  await expect(page).toHaveTitle("μEditor");
});

test("Load simple configuration", async ({ request, page }) => {
  let response = await request.post("/api/tests/fixtures/simple");
  expect(response.status()).toBe(204);
  response = await request.post("/api/auth/login");
  expect(response.status()).toBe(204);
  await page.goto("/");
  await expect(page).toHaveTitle("μEditor - Simple Fixture");
});
