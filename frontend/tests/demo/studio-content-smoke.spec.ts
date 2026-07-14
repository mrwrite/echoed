import { expect, test } from '@playwright/test';

const CONTENT_ADMIN_USERNAME = process.env['DEMO_CONTENT_ADMIN_USERNAME'] || 'contentadmin';
const CONTENT_ADMIN_PASSWORD = process.env['DEMO_CONTENT_ADMIN_PASSWORD'] || 'password';
const DRAFT_OFFERING_TITLE = process.env['DEMO_STUDIO_DRAFT_TITLE'] || 'EchoEd Governance Review Pack';

async function signIn(page: import('@playwright/test').Page, username: string, password: string) {
  await page.goto('/login');
  await page.getByLabel('Email or Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
}

test.describe('seeded Content Studio smoke', () => {
  test('content administrator can inspect supported Studio work without publishing', async ({ page }) => {
    await signIn(page, CONTENT_ADMIN_USERNAME, CONTENT_ADMIN_PASSWORD);
    await expect(page).toHaveURL(/\/studio$/);
    await expect(page.getByRole('heading', { name: 'Studio overview' })).toBeVisible();
    await expect(page.getByText('Current authoring scope')).toBeVisible();

    await page.getByRole('link', { name: 'Projects', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Projects', exact: true })).toBeVisible();
    await page.getByRole('searchbox', { name: 'Search', exact: true }).fill('EchoEd');
    await expect(page.getByText(/items? shown/)).toBeVisible();

    await page.getByRole('link', { name: 'Sources', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Source library' })).toBeVisible();

    let progressRequests = 0;
    page.on('request', request => { if (request.url().includes('/api/progress') || request.url().includes('/api/start-course')) progressRequests += 1; });
    await page.getByRole('link', { name: 'Content Drafts', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Content drafts' })).toBeVisible();
    const firstDraft = page.getByRole('link', { name: /^Review / }).first();
    if (await firstDraft.count()) {
      await firstDraft.click();
      await expect(page.getByText('This is a content-record preview.')).toBeVisible();
      expect(progressRequests).toBe(0);
    }

    await page.getByRole('link', { name: 'Content', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Content library' })).toBeVisible();
    await page.getByRole('searchbox', { name: 'Search', exact: true }).fill(DRAFT_OFFERING_TITLE);
    await page.getByRole('link', { name: `Review ${DRAFT_OFFERING_TITLE}` }).click();
    const publishButton = page.getByRole('button', { name: 'Publish publicly' });
    await expect(publishButton).toBeVisible();
    await publishButton.click();
    await expect(page.getByRole('dialog', { name: 'Publish this learning offering publicly?' })).toBeVisible();
    await expect(page.getByText(/does not publish course lessons/i)).toBeVisible();
    await page.getByRole('button', { name: 'Cancel' }).click();

    await page.getByRole('link', { name: 'Review', exact: true }).first().click();
    await expect(page.getByRole('heading', { name: 'Review content' })).toBeVisible();

    await page.setViewportSize({ width: 390, height: 844 });
    await expect(page.getByRole('heading', { name: 'Review content' })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);

    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
  });

  test('student deep link to Studio is rejected by the shared permission flow', async ({ page }) => {
    await signIn(page, process.env['DEMO_STUDENT_USERNAME'] || 'normalstudent', process.env['DEMO_STUDENT_PASSWORD'] || 'password');
    await expect(page).toHaveURL(/\/learn$/);
    await page.goto('/studio/review');
    await expect(page).toHaveURL(/\/access-denied$/);
    await expect(page.getByText(/permission|access/i).first()).toBeVisible();
  });
});
