import { expect, Page, test } from '@playwright/test';
import { loginAsDemoStudent } from './support/demo-smoke';

async function signIn(page: Page, username: string) {
  await page.goto('/login');
  await page.getByLabel('Email or Username').fill(username);
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).not.toHaveURL(/\/login$/);
}

test.describe('representative role visuals', () => {
  test('public landing at desktop and mobile', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'EchoEd' })).toBeVisible();
    await expect(page).toHaveScreenshot('public-landing-desktop.png');
    await page.setViewportSize({ width: 390, height: 844 });
    await expect(page).toHaveScreenshot('public-landing-mobile.png');
  });

  test('authentication at mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Secure sign in' })).toBeVisible();
    await expect(page).toHaveScreenshot('login-mobile.png');
  });

  test('student lesson at mobile', async ({ page }) => {
    await loginAsDemoStudent(page);
    await page.getByRole('button', { name: /start lesson|resume lesson/i }).first().click();
    await page.setViewportSize({ width: 390, height: 844 });
    await expect(page.getByLabel('Lesson experience')).toBeVisible();
    await page.evaluate(() => {
      window.scrollTo(0, 0);
      document.querySelectorAll('*').forEach(element => {
        if (element.scrollTop) element.scrollTop = 0;
        if (element.scrollLeft) element.scrollLeft = 0;
      });
    });
    await expect(page).toHaveScreenshot('student-lesson-mobile.png');
  });

  test('teacher classes at desktop', async ({ page }) => {
    await signIn(page, 'teacher');
    await page.goto('/teach/classes');
    await expect(page.getByRole('heading', { name: 'My classes', exact: true })).toBeVisible();
    await expect(page).toHaveScreenshot('teacher-classes-desktop.png');
  });

  test('admin users at desktop', async ({ page }) => {
    await signIn(page, 'orgadmin');
    await page.goto('/admin/users');
    await expect(page.getByRole('heading', { name: 'Users', exact: true })).toBeVisible();
    await expect(page).toHaveScreenshot('admin-users-desktop.png');
  });
});
