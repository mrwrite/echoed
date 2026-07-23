import { expect, test } from '@playwright/test';

const ORG_ADMIN_USERNAME = process.env['DEMO_ORG_ADMIN_USERNAME'] || 'orgadmin';
const ORG_ADMIN_PASSWORD = process.env['DEMO_ORG_ADMIN_PASSWORD'] || 'password';

async function signIn(page: import('@playwright/test').Page, username: string, password: string) {
  await page.goto('/login');
  await page.getByLabel('Email or Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
}

async function activateDemoOrganization(page: import('@playwright/test').Page) {
  const organizationSwitcher = page.getByLabel('Switch organization');
  await expect(organizationSwitcher).toBeVisible();
  await organizationSwitcher.selectOption({ label: 'EchoEd Demo School' });
  await expect(page.getByText('Confirmed organization')).toBeVisible();
}

test.describe('seeded organization administrator smoke', () => {
  test('organization administrator can inspect scoped people, classes, content, and settings', async ({ page }) => {
    await signIn(page, ORG_ADMIN_USERNAME, ORG_ADMIN_PASSWORD);
    await activateDemoOrganization(page);
    await page.goto('/organization');
    await expect(page).toHaveURL(/\/organization$/);
    await expect(page.getByRole('heading', { name: 'EchoEd Demo School' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Organization summary' })).toBeVisible();

    await page.getByRole('link', { name: 'Members', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Members', exact: true })).toBeVisible();
    await page.getByRole('searchbox', { name: 'Search', exact: true }).fill('Tariq');
    await expect(page.getByText(/members shown/)).toBeVisible();
    await expect(page.getByText(/@demo\.com/)).toHaveCount(0);

    await page.getByRole('link', { name: 'Teachers', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Teachers', exact: true })).toBeVisible();
    await expect(page.getByText('Tariq Teacher')).toBeVisible();

    await page.getByRole('link', { name: 'Students', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Students', exact: true })).toBeVisible();

    await page.getByRole('link', { name: 'Invitations', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Invitations', exact: true })).toBeVisible();
    await expect(page.getByText(/Token:/i)).toHaveCount(0);
    await page.getByLabel('Email address').fill('future-admin@example.com');
    await page.getByLabel('Organization role').selectOption('org_admin');
    await page.getByRole('button', { name: 'Create invitation' }).click();
    await expect(page.getByRole('dialog', { name: 'Create a privileged organization invitation?' })).toBeVisible();
    await page.getByRole('button', { name: 'Cancel' }).click();

    await page.getByRole('link', { name: 'Classes', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Classes', exact: true })).toBeVisible();
    const reviewClass = page.getByRole('link', { name: /^Review / }).first();
    if (await reviewClass.count()) {
      await reviewClass.click();
      await expect(page.getByRole('heading', { name: 'Class membership' })).toBeVisible();
      await page.getByRole('link', { name: 'Return to classes' }).click();
    }

    await page.getByRole('link', { name: 'Course Availability', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Course availability' })).toBeVisible();
    await expect(page.getByText('Edit content')).toHaveCount(0);

    await page.getByRole('link', { name: 'Settings', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Organization settings' })).toBeVisible();
    await expect(page.getByLabel('Organization name')).toHaveValue('EchoEd Demo School');

    await page.setViewportSize({ width: 390, height: 844 });
    await expect(page.getByRole('heading', { name: 'Organization settings' })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
  });

  test('student deep link to Organization is rejected by the shared permission flow', async ({ page }) => {
    await signIn(page, process.env['DEMO_STUDENT_USERNAME'] || 'normalstudent', process.env['DEMO_STUDENT_PASSWORD'] || 'password');
    await expect(page).toHaveURL(/\/learn$/);
    await page.goto('/organization/members');
    await expect(page).toHaveURL(/\/access-denied$/);
    await expect(page.getByText(/permission|access/i).first()).toBeVisible();
  });
});
