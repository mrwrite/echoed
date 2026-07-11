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
    await expect(page.getByText('Next learning')).toBeVisible();
    await page.getByRole('button', { name: /start lesson|resume lesson/i }).first().click();

    await expect(page).toHaveURL(/\/learn\/lesson\//);
    await expect(page.getByLabel('Lesson experience')).toBeVisible();    
    await expect(
      page.getByRole('button', { name: 'Exit lesson and return to Learn' }),
    ).toBeVisible();
  });
});
