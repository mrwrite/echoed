# Content Studio Production Implementation

Date: 2026-07-13

## Delivered

- Canonical, `content_admin`-guarded routes under `/studio` for overview, creation, projects, content, courses, programs and paths, sources, drafts, review, and publishing.
- Role-accurate Studio navigation and `/studio` as the content-admin login destination; existing `/workspace/**` routes remain available for deep-link compatibility.
- A content-focused overview using supported V2 workspace analytics, explicit partial-failure handling, recent work, concrete state counts, and editorial shortcuts.
- Searchable and filterable responsive libraries for projects, product wrappers, course/program wrapper types, sources, drafts, and publishing states.
- Project detail with supported project-scoped source and draft creation.
- Product-wrapper oversight with review state, audience visibility, source coverage, access context, confirmed public publishing, and no optimistic state mutation.
- Draft detail and preview using the stored Artifact body without enrollment, lesson sessions, or learner-progress requests.
- Review queue for the backend's reviewable wrapper states, with exact confirmation language and server-confirmed state changes.
- Shared loading, empty, error, confirmation, live-status, focus, and responsive patterns across the canonical Studio family.
- Seeded Playwright coverage for the supported content-admin workflow and unauthorized student deep links.

## Components Created

`StudioOverviewComponent`, `StudioLibraryComponent`, `StudioCreateComponent`, `StudioContentDetailComponent`, `StudioProjectDetailComponent`, `StudioDraftDetailComponent`, and `StudioReviewComponent`; shared Studio production layout styles in `frontend/src/styles/_studio-production.scss`.

## Components Migrated

Route configuration, shell navigation, canonical role destination, sidebar expectations, and shared confirmation/state usage were adapted for Studio. Legacy workspace components and routes were retained rather than broadly rewritten or deleted.

## APIs Used

- `GET /api/analytics/workspace`
- `GET /api/workspaces`
- `GET/POST /api/projects` and `GET /api/projects/{id}`
- `GET/POST /api/products`, `GET /api/products/{id}`, `PATCH /api/products/{id}/review-status`, and `PATCH /api/products/{id}/publish`
- `GET/POST /api/knowledge-sources` and project-scoped source reads
- `GET/POST /api/artifacts`, `GET /api/artifacts/{id}`, project-scoped artifact reads, and `PATCH /api/artifacts/{id}/review-status`
- `GET /api/review-center`

All authorization, organization scope, review state, visibility, and publishing results remain backend-authoritative.

## Supported Behavior Boundaries

The backend does not provide `content_admin` with a coherent, ownership-safe course/unit/lesson/activity/assessment CRUD surface. It also lacks a supported Studio asset/upload library, curriculum ordering contract, formal approval accountability, unpublish action, version history, review comments, reviewer assignment, and collaborative editing. Canonical Studio therefore presents the supported V2 content-operation wrappers and does not expose nonfunctional or authorization-inconsistent controls.

Program and Course views are filtered V2 product-wrapper libraries, not full learner curriculum editors. Source records expose only current wrapper metadata; the API does not contain bibliographic, rights, citation, or related-lesson fields. Preview renders the stored draft body only and never enters the student runtime.

## Backend Changes

None. No schema, migration, endpoint, seed, authentication, JWT, or authorization behavior changed in Phase 5.

## Verification

- Frontend unit tests: `256 SUCCESS` (baseline was `245 SUCCESS`).
- TypeScript application compile: passes.
- Production build: passes; existing Sass mixed-declaration warnings and the existing initial-bundle budget warning remain.
- Playwright discovery: 5 tests in 3 files.
- Seeded browser execution: a disposable model-created SQLite database was seeded because Docker/PostgreSQL were unavailable. Student, Admin, Studio, and unauthorized deep-link scenarios pass in Chromium. Result: `5 passed`.
- Studio browser checks cover project/source/content navigation, search, safe draft preview, a cancelled public-publish confirmation, review, keyboard focus, and 390px horizontal overflow.
- OpenSpec strict validation: `overhaul-role-based-ui-ux-experience` is valid.

## Known Limitations

- Manual screen-reader timing, 200% browser zoom, user override contrast, mobile virtual keyboards, and very long real citations remain review items.
- No safe asset upload, lesson/activity/assessment editor, accessible reorder control, approval audit trail, or reversible unpublish workflow is exposed because its required backend contract is absent.
- Legacy workspace routes retain older terminology and broader creator-role assumptions until their non-Studio consumers receive canonical replacements.

## Recommended Next Phase

Proceed to organization-admin self-service after separately specifying the critical scoped curriculum-authoring contract. Do not fold those backend gaps into the organization UI phase.
