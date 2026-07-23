import { expect, Page, test } from '@playwright/test';
import { loginAsDemoStudent } from './support/demo-smoke';

async function signIn(page: Page, username: string, password = 'password') {
  await page.goto('/login');
  await page.getByLabel('Email or Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).not.toHaveURL(/\/login$/);
}

async function expectSinglePageHeading(page: Page) {
  await expect(page.locator('h1')).toHaveCount(1);
  await expect(page.locator('h1')).toBeVisible();
}

async function expectVisibleKeyboardFocus(page: Page) {
  await page.keyboard.press('Tab');
  const focused = page.locator(':focus');
  await expect(focused).toBeVisible();
  const hasFocusIndicator = await focused.evaluate(element => {
    const style = getComputedStyle(element);
    return style.outlineStyle !== 'none' || style.boxShadow !== 'none';
  });
  expect(hasFocusIndicator).toBe(true);
}

async function expectResponsiveDocument(page: Page) {
  for (const width of [390, 768, 1280, 1440]) {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
  }
}

async function expectNoUnnamedControls(page: Page) {
  const unnamed = await page.locator('button, a[href], input, select, textarea').evaluateAll(elements => elements.filter(element => {
    const html = element as HTMLElement;
    if (html.offsetParent === null) return false;
    const id = html.id;
    const labelled = id ? document.querySelector(`label[for="${CSS.escape(id)}"]`) : null;
    return !(html.getAttribute('aria-label') || html.getAttribute('aria-labelledby') || html.getAttribute('title') ||
      labelled?.textContent?.trim() || html.textContent?.trim() || html.getAttribute('placeholder'));
  }).length);
  expect(unnamed).toBe(0);
}

test.describe('critical WCAG role flows', () => {
  test('public and authentication pages expose ordered headings, labels, focus, and responsive bounds', async ({ page }) => {
    await page.goto('/');
    await expectSinglePageHeading(page);
    await expect(page.getByRole('navigation', { name: 'Primary navigation' })).toBeVisible();
    await expectVisibleKeyboardFocus(page);
    await expectResponsiveDocument(page);
    await expectNoUnnamedControls(page);

    await page.goto('/login');
    await expectSinglePageHeading(page);
    await expect(page.getByLabel('Email or Username')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
    await expectVisibleKeyboardFocus(page);
    await expectResponsiveDocument(page);
    await expectNoUnnamedControls(page);
  });

  test('student lesson keeps one page heading and keyboard-visible controls', async ({ page }) => {
    await loginAsDemoStudent(page);
    await page.getByRole('button', { name: /start lesson|resume lesson/i }).first().click();
    await expect(page).toHaveURL(/\/learn\/lesson\//);
    await expectSinglePageHeading(page);
    await expect(page.getByLabel('Lesson experience')).toBeVisible();
    await expectVisibleKeyboardFocus(page);
    await expectResponsiveDocument(page);
    await expectNoUnnamedControls(page);
  });

  test('teacher class detail preserves semantic structure and responsive keyboard actions', async ({ page }) => {
    await signIn(page, 'teacher');
    await page.goto('/teach/classes');
    await expect(page.getByRole('heading', { name: 'My classes', exact: true })).toBeVisible();
    await page.getByText('Open class overview', { exact: true }).first().click();
    await expect(page.locator('h1')).toBeVisible();
    await expectSinglePageHeading(page);
    await expectVisibleKeyboardFocus(page);
    await expectResponsiveDocument(page);
    await expectNoUnnamedControls(page);
  });

  test('admin user management preserves semantic structure and responsive keyboard actions', async ({ page }) => {
    await signIn(page, 'orgadmin');
    await page.goto('/admin/users');
    await expect(page.getByRole('heading', { name: 'Users', exact: true })).toBeVisible();
    await expectSinglePageHeading(page);
    await expect(page.getByLabel('Search by name')).toBeVisible();
    await expectVisibleKeyboardFocus(page);
    await expectResponsiveDocument(page);
    await expectNoUnnamedControls(page);
  });
});
