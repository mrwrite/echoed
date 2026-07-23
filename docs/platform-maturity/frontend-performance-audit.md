# Frontend Performance Audit

Date: 2026-07-23
Baseline commit: `21c07367d664fcfdd128a7ca19e2f7e2f97b4b42`

## Method

The baseline was built with:

```text
npm run build -- --stats-json
```

Angular's emitted `stats.json` was inspected by output and by `bytesInOutput`; dependency conclusions below come from that file, route imports, `package.json`, the installed dependency tree, and source searches. Generated filenames are evidence for this build only and are not treated as stable contracts.

## Before measurement

| Initial output | Raw bytes |
| --- | ---: |
| `main-IIHDY2XJ.js` | 1,166,868 |
| Unnamed shared chunk | 161,494 |
| Global CSS | 57,946 |
| Polyfills | 34,585 |
| **Angular initial total** | **1.42 MB** |
| **Estimated initial transfer** | **253.55 kB** |

The build exceeded the 1.25 MB warning budget by 170.89 kB. Only the async animation browser implementation (64,184 bytes) was emitted as a lazy chunk.

## Largest initial JavaScript contributors

The following `bytesInOutput` values came from the baseline main output:

| Input | Bytes in baseline main |
| --- | ---: |
| Angular Router | 66,825 |
| Angular CDK drag/drop | 56,592 |
| Angular Forms | 48,027 |
| Student dashboard | 39,478 |
| Angular Common module | 31,367 |
| Learner home | 29,892 |
| Teacher dashboard | 24,497 |
| Shared lesson viewer | 23,609 |
| Product Studio | 23,512 |
| Section detail | 22,041 |
| Studio project detail | 20,860 |
| Registration | 18,494 |
| Studio create | 18,322 |
| Landing | 18,157 |
| Admin courses | 17,346 |

The evidence shows that the dominant avoidable cost was not a single third-party utility: `app.routes.ts` statically imported 61 independently navigable page components. That made student, teacher, Studio, Organization, Admin, course-authoring, and CDK drag/drop code part of every initial visit.

## CSS and assets

- Global CSS was 57,946 bytes. `src/styles.scss` contributed 52,662 bytes, design-token CSS 3,903 bytes, and CDK overlay CSS 1,380 bytes.
- No component stylesheet exceeded the configured 10 kB warning.
- Production assets are a 15,086-byte favicon; a 101,592-byte Cal Sans TTF plus its license; two small map SVGs; two icon SVGs; and a 1,032-byte event JSON file.
- `index.html` loads Inter, Poppins, and Playfair Display from Google Fonts. The local Cal Sans file is copied but no `@font-face` declaration loads it. Changing typography would risk Phase 6 visual regression, so Phase 7 records this rather than silently replacing fonts.
- No application images are large enough to explain the JavaScript warning.

## Build configuration

- Builder: `@angular-devkit/build-angular:application`.
- Production optimization, build optimizer behavior, minification, and tree shaking use Angular production defaults.
- Output hashing is enabled.
- Production source maps are not enabled; development source maps are enabled.
- No global scripts are configured.
- The production build emitted no CommonJS warning.
- `provideAnimationsAsync()` already defers the animation browser implementation.

## Dependencies and duplication

- Runtime dependencies are Angular packages, Angular CDK, and Zone.js; there is no broad utility library in the initial dependency set.
- CDK drag/drop is used only by the course-wizard review step but was eager solely because the route component was eager.
- `uuid` is imported by course-wizard steps without being declared as a direct runtime dependency; it is present only transitively while `@types/uuid` is declared. This is a reproducibility defect and a candidate for replacement with the browser-native UUID API.
- Loader packages and Storybook-related build tooling are development-only and do not appear in production output.
- The installed tree contains normal build-tool transitive version duplication; no duplicate application runtime framework was emitted in the baseline main bundle.

## Route-loading structure before optimization

Public, authentication, onboarding, Learn, Teach, Studio, Organization, Platform Admin, legacy `/home`, and legacy `/workspace` page components all used eager `component` route entries. Guards existed but protected feature code was already present in the initial bundle.

## Evidence-backed optimization

Convert standalone route components to explicit `loadComponent` functions while retaining `canActivate`, data, children, redirects, and path shapes. This directly removes the measured page and feature dependencies from the initial graph and makes unauthorized feature code avoidable until navigation passes the applicable route boundary.

## Risks to verify

- Direct deep links and refreshes must resolve through the server fallback and lazy route.
- Route guards must remain on the same route records.
- Shared shell and nested empty-path routes must still compose correctly.
- A larger number of chunks can add request overhead on feature entry.
- Lazy import failures need a recoverable accessible state.
- Navigation history, mobile navigation, and visual output must remain unchanged.
- No exact generated filename should be asserted because optimizer partitioning is unstable.
