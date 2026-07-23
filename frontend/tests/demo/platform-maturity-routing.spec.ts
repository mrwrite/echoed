import { expect, test } from '@playwright/test';
import { loginAsDemoStudent } from './support/demo-smoke';

test.describe('platform maturity route loading', () => {
  test('public and authentication deep links load lazy route content and history', async ({ page }) => {
    await page.goto('/products');
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();

    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Welcome back to EchoEd' })).toBeVisible();
    await page.goBack();
    await expect(page).toHaveURL(/\/products$/);
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await page.goForward();
    await expect(page).toHaveURL(/\/login$/);
  });

  test('student deep links retain guards after lazy loading', async ({ page }) => {
    await loginAsDemoStudent(page);
    await page.goto('/admin/users');

    await expect(page).toHaveURL(/\/access-denied$/);
    await expect(page.getByRole('status', { name: 'Permission denied page' })).toContainText(
      'You do not have permission to view this page.',
    );
  });

  test('chunk-load recovery route is accessible and retryable', async ({ page }) => {
    await page.goto('/load-error');

    await expect(
      page.getByRole('heading', { name: 'This part of EchoEd could not load' }),
    ).toBeVisible();
    await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Return to EchoEd home' })).toBeVisible();
  });
});
