# Frontend Performance Implementation

Date: 2026-07-23

## Summary

Phase 7 changed route loading architecture, not UI design. The existing bundle budgets remain unchanged.

| Measurement | Before | After |
| --- | ---: | ---: |
| Initial raw bundle | 1.42 MB | 436.81 kB |
| Estimated initial transfer | 253.55 kB | 118.47 kB |
| Main entry | 1,166,868 bytes | 24.90 kB |
| Warning-budget result | 170.89 kB over | approximately 813 kB under |

The final measurement includes the Angular 20.3.25 security patch and recoverable loading route. The measured initial reduction is approximately 984 kB raw (about 69%). The original warning is no longer emitted.

## Optimization: standalone route lazy loading

- **Previous behavior:** `app.routes.ts` statically imported 61 page components. Every visitor downloaded code for all role areas and legacy routes.
- **New behavior:** Routes use explicit `loadComponent` dynamic imports. Public, authentication, onboarding, Learn, Teach, Studio, Organization, Admin, `/home`, and `/workspace` paths preserve their existing records, guards, route data, children, and redirects.
- **Measured difference:** Initial total fell from 1.42 MB to 436.81 kB; main fell from 1,166,868 bytes to 24.90 kB.
- **User effect:** Initial visits transfer substantially less JavaScript. Feature code loads when its route is requested. No content, action, role, or route was removed.
- **Risk:** First entry into a feature now performs a chunk request; offline or interrupted requests can fail.
- **Coverage:** Route configuration tests resolve representative lazy exports and retain guard assertions. Full unit and role/deep-link browser suites are release gates.
- **Rollback:** Restore a route's static component import and `component` entry independently.

## Optimization: recoverable route-chunk failure

- **Previous behavior:** A failed dynamic import would surface as a router navigation error without a purpose-built recovery page.
- **New behavior:** Angular's navigation error handler identifies browser and bundler chunk-load signatures and redirects to an accessible recovery route with retry and home actions. Unrelated navigation errors are not swallowed.
- **Measured difference:** Negligible initial code relative to the route split; the recovery page is itself lazy.
- **User effect:** Interrupted deployments or networks produce a named, keyboard-operable recovery state instead of a blank route.
- **Risk:** Browser error wording can evolve.
- **Coverage:** Unit tests cover recognized dynamic-import/legacy chunk signatures and rejection of unrelated errors.
- **Rollback:** Remove the navigation error feature provider and recovery route.

## Optimization: native UUID generation

- **Previous behavior:** Course-wizard steps imported undeclared transitive `uuid` runtime code and declared only its type package.
- **New behavior:** Those imports are replaced with the standards-based browser `crypto.randomUUID()` API and the unused type-only package is removed.
- **Measured difference:** This affects the lazy course-wizard graph rather than the initial bundle; final chunk impact is recorded in Phase 7 verification.
- **User effect:** No intended behavior change; draft identifiers remain UUIDs.
- **Risk:** Requires the secure-context browser support already required by the supported modern Angular browser set.
- **Coverage:** Existing course-wizard unit tests and the production build.
- **Rollback:** Declare `uuid` as a direct runtime dependency and restore its imports.

## Dependency security correction

- **Previous behavior:** The coordinated Angular runtime/compiler set was 20.3.21 and `npm audit --omit=dev` reported six high and two moderate production advisories.
- **New behavior:** Angular runtime/compiler packages are pinned coherently to 20.3.25, the first patched line identified by the advisories.
- **Measured difference:** The final production-only audit reports zero vulnerabilities. The final initial bundle remains 436.81 kB.
- **User effect:** No intended visual or role behavior change.
- **Risk:** Patch releases can change framework behavior; the full unit, browser, and build gates cover the update.
- **Coverage:** 287 Angular tests, 19 Playwright tests, and production compilation pass.
- **Rollback:** Reverting would restore known production advisories and is not recommended; use a newer coordinated patched set if a regression is found.

## Deferred candidates

- Font self-hosting or typography consolidation needs design and licensing review because the current UI uses three Google Font families and a copied but unloaded Cal Sans file.
- Further CSS consolidation is not required for the budget and risks reopening the completed visual scope.
- Deferrable template views were not needed after route boundaries achieved substantial margin; adding placeholders would create extra behavioral and accessibility surface.
