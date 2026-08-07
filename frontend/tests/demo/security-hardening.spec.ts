import { expect, test } from '@playwright/test';

test.describe('platform security hardening', () => {
  test('anonymous forum mutation fails closed at the API boundary', async ({ request }) => {
    const response = await request.post('/api/forum/threads', {
      data: { title: 'Anonymous topic', content: 'This must not be accepted.' },
    });

    expect(response.status()).toBe(401);
  });

  test('rate limiting is announced accessibly without discarding credentials', async ({ page }) => {
    await page.route('**/api/auth/token', async route => {
      await route.fulfill({
        status: 429,
        headers: { 'Content-Type': 'application/json', 'Retry-After': '60' },
        body: JSON.stringify({ detail: 'Too many attempts. Try again later.' }),
      });
    });

    await page.goto('/login');
    await page.getByLabel('Email or Username').fill('demo-user');
    await page.getByLabel('Password').fill('not-a-real-password');
    await page.getByRole('button', { name: 'Sign in' }).click();

    const alert = page.getByRole('alert');
    await expect(alert).toContainText(/too many attempts/i);
    await expect(page.getByLabel('Email or Username')).toHaveValue('demo-user');
    await expect(page.getByLabel('Password')).toHaveValue('not-a-real-password');
  });

  test('unexpected server failure presents a safe support reference', async ({ page }) => {
    await page.route('**/api/auth/token', async route => {
      await route.fulfill({
        status: 500,
        headers: { 'Content-Type': 'application/json', 'X-Request-ID': 'req-e2e-support' },
        body: JSON.stringify({ detail: 'Internal implementation detail must stay hidden.' }),
      });
    });

    await page.goto('/login');
    await page.getByLabel('Email or Username').fill('demo-user');
    await page.getByLabel('Password').fill('not-a-real-password');
    await page.getByRole('button', { name: 'Sign in' }).click();

    const alert = page.getByRole('alert');
    await expect(alert).toContainText('Reference: req-e2e-support');
    await expect(alert).not.toContainText('implementation detail');
  });
});
