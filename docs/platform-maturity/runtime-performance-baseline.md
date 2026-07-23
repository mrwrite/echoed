# Runtime Performance Baseline

Date: 2026-07-23

## Method

Measurements were collected with `frontend/scripts/measure-runtime.mjs`, Playwright Chromium, Chrome DevTools Protocol network/performance metrics, and browser `PerformanceObserver` entries. The disposable seeded Phase 7 database and local FastAPI service were used. The Angular development server at `http://127.0.0.1:4200` was measured because the checked-in production environment targets the deployed Railway API and cannot be redirected to the disposable local backend without changing deployment configuration.

These development-server JavaScript byte counts include unminified development modules and are not production bundle measurements. Production bytes are recorded in the bundle audit and implementation documents. The timings are local-machine baselines, not Lighthouse scores or claims about production users.

## Collected measurements

| Route | JS transferred | JS executed | LCP | CLS | Long tasks | Route wall time | API requests | Repeated API paths | DOM nodes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| Public landing `/` | 2,540,989 B | 40 ms | 228 ms | 0.0012 | 0 | 991 ms | 0 | None | 144 |
| Login `/login` | 2,775,349 B | 34 ms | 192 ms | 0.0007 | 0 | 960 ms | 0 | None | 59 |
| Student Learn `/learn` | 3,395,437 B | 129 ms | 220 ms | 0.0679 | 0 | 1,070 ms | 11 | `/api/orgs` twice | 244 |
| Course detail `/learn/courses/:id` | 3,322,775 B | 116 ms | 264 ms | 0.0684 | 0 | 1,084 ms | 7 | `/api/orgs` twice; `/api/progress/segment` twice | 314 |
| Teacher Teach `/teach` | 3,829,989 B | 122 ms | 204 ms | 0.0681 | 0 | 1,151 ms | 8 | `/api/orgs` twice | 260 |
| Content Studio `/studio` | 3,236,874 B | 102 ms | 188 ms | 0.0679 | 0 | 977 ms | 5 | `/api/orgs` twice | 222 |
| Organization `/organization` | 3,233,031 B | 106 ms | 172 ms | 0.0679 | 0 | 1,004 ms | 8 | `/api/orgs` three times | 247 |
| Platform Admin `/admin` | 3,246,523 B | 92 ms | 172 ms | 0.0934 | 0 | 948 ms | 5 | `/api/orgs` three times | 157 |

“JS executed” is Chrome `ScriptDuration`, not decoded bytes. All eight runs captured DOMContentLoaded, load, LCP, CLS, long-task, script, task, network, API-waterfall, and DOM-node evidence. No run produced a greater-than-50-ms browser long-task entry.

## Findings from collected evidence

- The authenticated shell repeats `/api/orgs` two or three times on every representative role landing. Consolidating active-organization bootstrap reads is a measured follow-up opportunity.
- Course detail repeats `/api/progress/segment`; its resolver/component ownership should be examined before changing behavior.
- Platform Admin had the largest observed layout shift at 0.0934, still below the commonly used 0.1 “good” boundary but close enough to monitor.
- The sampled pages had modest DOM sizes (59–314 nodes) and no observed long tasks on the local machine.
- The bundle split is visible in development script-request counts: routes request only their shell and selected lazy graphs, not every page component.

## Measurements not collected

- No Lighthouse score, field Core Web Vitals, low-end mobile CPU result, constrained-network trace, production CDN/cache result, or real-user measurement was collected.
- Authenticated production-configuration runs were blocked by the hard-coded deployed API URL in `environment.prod.ts`; changing that deployment setting was outside this baseline.
- Interaction to Next Paint was not available from the automated route loads because no representative post-load interaction taxonomy exists.
- Route-transition costs here include the fixed post-navigation observation window and should be used comparatively, not interpreted as user-perceived navigation latency.

## Code-inspection recommendations

Deduplicate organization bootstrap requests behind the existing session/organization state service; confirm progress-segment request ownership; parameterize the production API endpoint at deployment time; retain route-level dynamic imports; and add production-like, throttled CI measurements only after an ephemeral production configuration is defined. These are recommendations, not measured improvements.
