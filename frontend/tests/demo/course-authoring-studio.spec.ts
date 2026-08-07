import { expect, test } from '@playwright/test';

const capabilities = {
  can_create: true, can_view_draft: true, can_edit: true, can_duplicate: true,
  can_preview: true, can_submit_review: true, can_review: false, can_publish: false,
};

test('course creator completes the canonical Studio journey at desktop and mobile sizes', async ({ page }) => {
  page.on('pageerror', error => console.error(`PAGE ERROR: ${error.message}`));
  let revision = 1;
  let latest: Record<string, unknown> = {};
  await page.addInitScript(() => {
    const payload = btoa(JSON.stringify({ sub: 'author-1', role: 'content_admin', exp: Math.floor(Date.now() / 1000) + 3600 })).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
    localStorage.setItem('auth_token', `header.${payload}.signature`);
    localStorage.setItem('active_org_id', 'org-1');
    localStorage.setItem('active_org_role', 'content_admin');
  });
  await page.route('**/api/**', async route => {
    const url = route.request().url();
    const method = route.request().method();
    const json = (body: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) });
    if (url.endsWith('/api/orgs')) return json([{ id: 'org-1', name: 'Pilot School', type: 'school', role: 'content_admin' }]);
    if (url.endsWith('/api/course-authoring/capabilities')) return json({ organization_id: 'org-1', capabilities });
    if (url.endsWith('/api/course-authoring/templates')) return json([]);
    if (url.endsWith('/api/courses/authoring') && method === 'POST') {
      latest = route.request().postDataJSON();
      return json({ ...latest, id: 'course-1', organization_id: 'org-1', created_by: 'author-1', revision_number: revision, revision_status: 'draft', revision_metadata: {}, updated_at: new Date().toISOString(), current_version_id: 'version-1', assessment_ids: [], capabilities });
    }
    if (url.endsWith('/api/courses/course-1/authoring-draft') && method === 'GET') {
      return json({ ...latest, id: 'course-1', organization_id: 'org-1', created_by: 'author-1', revision_number: revision, revision_status: 'draft', revision_metadata: {}, updated_at: new Date().toISOString(), current_version_id: 'version-1', assessment_ids: [], capabilities });
    }
    if (url.endsWith('/api/courses/course-1/authoring-draft') && method === 'PUT') {
      latest = route.request().postDataJSON(); revision += 1;
      return json({ ...latest, id: 'course-1', organization_id: 'org-1', created_by: 'author-1', revision_number: revision, revision_status: 'draft', revision_metadata: {}, updated_at: new Date().toISOString(), current_version_id: 'version-1', assessment_ids: [], capabilities });
    }
    if (url.endsWith('/api/courses/course-1/governance-summary')) return json({ course_id: 'course-1', course_title: 'Evidence Lab', publish_readiness: { blocking_issue_count: 0 }, safe_publish_validation: { blocking_issue_count: 0, blocking_issues: [], warnings: [] }, lineage_safety_visibility: {}, competency_evidence_integrity: {}, runtime_intervention_recommendations: [] });
    if (url.endsWith('/api/courses/course-1/authoring-preview')) return json({ ...latest, id: 'course-1', revision_number: revision, revision_status: 'draft', revision_metadata: {}, lineage_status: 'standalone', lineage_metadata: {}, skill_tags: [], standards_metadata: {} });
    if (url.endsWith('/api/courses/course-1/versions')) return json([{ id: 'version-1', course_id: 'course-1', version_number: 1, status: 'draft', created_at: new Date().toISOString() }]);
    return json([]);
  });

  await page.goto('/workspace/product-studio/courses/new');
  await expect(page.getByRole('heading', { name: 'Untitled course' })).toBeVisible();
  await expect(page.getByRole('tab', { name: 'Setup' })).toHaveAttribute('aria-selected', 'true');
  await page.getByLabel('Title', { exact: true }).fill('Evidence Lab');
  await page.getByLabel('Description', { exact: true }).fill('Practice evaluating primary sources.');
  await page.getByRole('button', { name: '+ Unit' }).click();
  await page.getByLabel('Unit title').fill('Source evaluation');
  await page.getByRole('button', { name: '+ Lesson' }).click();
  await page.getByLabel('Lesson title').fill('Claims and evidence');
  await page.getByRole('button', { name: '+ Activity' }).click();
  await page.getByLabel('Title', { exact: true }).last().fill('Compare two accounts');
  await page.getByLabel('Instructions / content').fill('Read both accounts and identify one supported claim.');
  await expect(page).toHaveURL(/\/courses\/course-1$/);
  await expect(page.getByRole('status').first()).toContainText('Idle');

  await page.getByRole('tab', { name: 'Quality' }).click();
  await expect(page.getByRole('heading', { name: 'Quality check' })).toBeVisible();
  await page.getByRole('tab', { name: 'Preview' }).click();
  await expect(page.getByRole('heading', { name: 'Learner preview' })).toBeVisible();
  await page.getByRole('tab', { name: 'Release' }).click();
  await expect(page.getByRole('heading', { name: 'Review and release' })).toBeVisible();

  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByRole('heading', { name: 'Review and release' })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
  await page.keyboard.press('Tab');
  await expect(page.locator(':focus')).toBeVisible();
});
