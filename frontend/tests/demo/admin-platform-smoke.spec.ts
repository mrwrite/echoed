import { expect, test } from '@playwright/test';

const ADMIN_USERNAME = process.env['DEMO_ADMIN_USERNAME'] || 'orgadmin';
const ADMIN_PASSWORD = process.env['DEMO_ADMIN_PASSWORD'] || 'password';

async function signIn(page: import('@playwright/test').Page, username: string, password: string) {
  await page.goto('/login');
  await page.getByLabel('Email or Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
}

test.describe('seeded platform administrator smoke', () => {
  test('administrator can inspect supported Admin oversight without completing destructive actions', async ({ page }) => {
    await signIn(page, ADMIN_USERNAME, ADMIN_PASSWORD);
    await expect(page).toHaveURL(/\/admin$/);
    await expect(page.getByRole('heading', { name: 'Admin overview' })).toBeVisible();

    await page.getByRole('link', { name: 'Users', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Users', exact: true })).toBeVisible();
    await page.getByLabel('Search by name').fill('Eshe');
    await expect(page.getByText('1 user shown')).toBeVisible();
    await page.getByRole('link', { name: 'Review Eshe Steady' }).click();
    await expect(page.getByRole('heading', { name: 'Identity' })).toBeVisible();
    await expect(page.getByText('Organization memberships')).toBeVisible();
    const deleteButton = page.getByRole('button', { name: 'Delete user account' });
    if (await deleteButton.isEnabled()) {
      await deleteButton.click();
      await expect(page.getByRole('dialog', { name: 'Delete user account' })).toBeVisible();
      await expect(page.getByText(/cannot be undone/i)).toBeVisible();
      await page.getByRole('button', { name: 'Cancel' }).click();
    }

    await page.getByRole('link', { name: 'Organizations', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Organizations' })).toBeVisible();
    await expect(page.getByText('Scoped organization visibility')).toBeVisible();

    await page.getByRole('link', { name: 'Courses', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Course oversight' })).toBeVisible();
    await expect(page.getByText('Create course')).toHaveCount(0);

    await page.getByRole('link', { name: 'Badges', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Badge administration' })).toBeVisible();

    await page.setViewportSize({ width: 390, height: 844 });
    await expect(page.getByRole('heading', { name: 'Badge administration' })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
  });

  test('student deep link to Admin is rejected by the shared permission flow', async ({ page }) => {
    await signIn(page, process.env['DEMO_STUDENT_USERNAME'] || 'normalstudent', process.env['DEMO_STUDENT_PASSWORD'] || 'password');
    await expect(page).toHaveURL(/\/learn$/);
    await page.goto('/admin/users');
    await expect(page).toHaveURL(/\/access-denied$/);
    await expect(page.getByText(/permission|access/i).first()).toBeVisible();
  });
});
