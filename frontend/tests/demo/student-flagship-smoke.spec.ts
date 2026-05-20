import { expect, test } from '@playwright/test';

import {
  expectFlagshipCourseOnStudentDashboard,
  FLAGSHIP_COURSE_TITLE,
  loginAsDemoStudent,
} from './support/demo-smoke';

test.describe('demo student flagship smoke', () => {
  test('student can log in and open the flagship governed lesson path', async ({ page }) => {
    await loginAsDemoStudent(page);

    await expectFlagshipCourseOnStudentDashboard(page);
    await expect(page.getByText('Welcome back')).toBeVisible();
    await expect(page.getByTestId('student-active-course-title')).toHaveText(
      FLAGSHIP_COURSE_TITLE,
    );
    await page.getByTestId('student-continue-lesson').click();

    await expect(page).toHaveURL(/\/home\/lesson\//);
    await expect(page.getByLabel('Lesson experience')).toBeVisible();    
    await expect(
      page.getByRole('button', { name: 'Exit lesson and return to dashboard' }),
    ).toBeVisible();
  });
});
