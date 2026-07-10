import { expect, Page } from '@playwright/test';

export const DEMO_STUDENT_USERNAME =
  process.env['DEMO_STUDENT_USERNAME'] || 'normalstudent';
export const DEMO_STUDENT_PASSWORD =
  process.env['DEMO_STUDENT_PASSWORD'] || 'password';
export const FLAGSHIP_COURSE_TITLE =
  process.env['DEMO_FLAGSHIP_COURSE_TITLE'] || 'Introduction to Africa';

export async function loginAsDemoStudent(page: Page): Promise<void> {
  await page.goto('/login');

  await expect(page.getByRole('heading', { name: 'Welcome back to EchoEd' })).toBeVisible();
  await page.getByLabel('Email or Username').fill(DEMO_STUDENT_USERNAME);
  await page.getByLabel('Password').fill(DEMO_STUDENT_PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page).toHaveURL(/\/learn$/);
  await expect(page.getByRole('heading', { name: 'Your products and learning paths' })).toBeVisible();
}

export async function expectFlagshipCourseOnStudentDashboard(page: Page): Promise<void> {
  await expect(page.getByText(FLAGSHIP_COURSE_TITLE)).toBeVisible();
}
