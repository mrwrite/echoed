import { chromium } from '@playwright/test';

const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:4201';
const password = process.env.DEMO_PASSWORD || 'password';

const observerScript = () => {
  window.__echoedPerf = { cls: 0, lcp: 0, longTasks: [] };
  new PerformanceObserver((list) => {
    const entries = list.getEntries();
    window.__echoedPerf.lcp = entries.at(-1)?.startTime || window.__echoedPerf.lcp;
  }).observe({ type: 'largest-contentful-paint', buffered: true });
  new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      if (!entry.hadRecentInput) window.__echoedPerf.cls += entry.value;
    }
  }).observe({ type: 'layout-shift', buffered: true });
  new PerformanceObserver((list) => {
    window.__echoedPerf.longTasks.push(
      ...list.getEntries().map((entry) => ({
        startTime: Math.round(entry.startTime),
        duration: Math.round(entry.duration),
      })),
    );
  }).observe({ type: 'longtask', buffered: true });
};

async function login(page, username) {
  await page.goto(`${baseURL}/login`);
  await page.getByLabel('Email or Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL((url) => !url.pathname.endsWith('/login'));
  await page.waitForLoadState('networkidle');
}

async function measure(browser, definition) {
  const context = await browser.newContext();
  await context.addInitScript(observerScript);
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);
  await cdp.send('Network.enable');
  await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
  await cdp.send('Performance.enable');

  if (definition.username) {
    await login(page, definition.username);
  }

  const target = await definition.resolveTarget?.(page) ?? definition.path;
  const started = performance.now();
  await page.goto(`${baseURL}${target}`);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(250);
  const routeTransitionMs = performance.now() - started;

  const browserMetrics = await cdp.send('Performance.getMetrics');
  const metrics = Object.fromEntries(browserMetrics.metrics.map(({ name, value }) => [name, value]));
  const result = await page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0];
    const resources = performance.getEntriesByType('resource');
    const scripts = resources.filter((entry) =>
      entry.initiatorType === 'script' || /\.js(?:$|\?)/.test(entry.name),
    );
    const api = resources.filter((entry) =>
      entry.initiatorType === 'fetch' || entry.initiatorType === 'xmlhttprequest',
    );
    const apiCounts = api.reduce((counts, entry) => {
      const path = new URL(entry.name).pathname;
      counts[path] = (counts[path] || 0) + 1;
      return counts;
    }, {});

    return {
      path: location.pathname,
      transferredJavaScriptBytes: scripts.reduce((sum, entry) => sum + entry.transferSize, 0),
      decodedJavaScriptBytes: scripts.reduce((sum, entry) => sum + entry.decodedBodySize, 0),
      scriptRequests: scripts.length,
      apiRequests: api.length,
      repeatedApiRequests: Object.fromEntries(
        Object.entries(apiCounts).filter(([, count]) => count > 1),
      ),
      domNodes: document.getElementsByTagName('*').length,
      domContentLoadedMs: Math.round(navigation.domContentLoadedEventEnd),
      loadEventMs: Math.round(navigation.loadEventEnd),
      lcpMs: Math.round(window.__echoedPerf?.lcp || 0),
      cls: Number((window.__echoedPerf?.cls || 0).toFixed(4)),
      longTasks: window.__echoedPerf?.longTasks || [],
    };
  });

  await context.close();
  return {
    name: definition.name,
    ...result,
    routeTransitionMs: Math.round(routeTransitionMs),
    scriptExecutionMs: Math.round((metrics.ScriptDuration || 0) * 1000),
    taskDurationMs: Math.round((metrics.TaskDuration || 0) * 1000),
  };
}

const definitions = [
  { name: 'Public landing', path: '/' },
  { name: 'Login', path: '/login' },
  { name: 'Student Learn home', path: '/learn', username: 'normalstudent' },
  {
    name: 'Student course detail',
    username: 'normalstudent',
    resolveTarget: async (page) => {
      const courseId = await page.evaluate(async () => {
        const response = await fetch('/api/student-courses', {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        });
        const courses = await response.json();
        return courses[0]?.course?.id || courses[0]?.course_id || courses[0]?.id;
      });
      if (!courseId) throw new Error('Seeded student course was not available.');
      return `/learn/courses/${courseId}`;
    },
  },
  { name: 'Teacher Teach home', path: '/teach', username: 'teacher' },
  { name: 'Content Studio home', path: '/studio', username: 'contentadmin' },
  { name: 'Organization home', path: '/organization', username: 'orgadmin' },
  { name: 'Platform Admin home', path: '/admin', username: 'superadmin' },
];

const browser = await chromium.launch({ headless: true });
try {
  const results = [];
  for (const definition of definitions) {
    results.push(await measure(browser, definition));
  }
  process.stdout.write(`${JSON.stringify({ baseURL, results }, null, 2)}\n`);
} finally {
  await browser.close();
}
