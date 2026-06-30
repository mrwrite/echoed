# Tasks

## Phase 1: Workspace Shell And Navigation Reframe

- [x] Audit existing shell, sidebar, route guards, dashboard pages, course wizard, admin course pages, studio pages, programs, sections, certifications, preferences, and analytics surfaces
- [x] Add V2 navigation labels while preserving current role and permission checks
- [x] Add route aliases for `/workspace`, `/workspace/product-studio`, `/workspace/products`, `/workspace/projects`, `/workspace/knowledge-sources`, `/workspace/artifacts`, `/workspace/review-center`, `/workspace/learners`, `/workspace/analytics`, and `/workspace/settings`
- [x] Map existing pages into the V2 navigation without removing old routes
- [x] Add placeholder pages or panels for future-only concepts where no current page exists
- [x] Reframe visible terminology from admin/student/course-only language toward workspace, product, learner, source, and artifact language where safe
- [x] Verify existing learner course start/continue flow still works
- [x] Verify existing teacher/admin course management still works
- [x] Run frontend tests and existing student smoke validation

## Phase 2: Wrapper Models For Workspace, Project, Product, Artifact, KnowledgeSource, GenerationRun

- [x] Design additive SQLAlchemy models and Alembic migrations for workspace, project, product, knowledge source, artifact, and generation run wrappers
- [x] Backfill workspace records from existing organizations
- [x] Backfill course-backed product records from existing courses
- [x] Add nullable or join-based links from new wrapper records to existing runtime records
- [x] Preserve existing course, program, lesson, progress, assessment, and certification schemas
- [x] Add backend tests for non-destructive backfill behavior
- [x] Add API read endpoints for wrapper records without replacing existing course APIs

## Phase 3: Product Studio Foundation

- [x] Reframe the existing course wizard as the first Product Studio workflow
- [x] Add product type selection with course-backed product as the initial supported type
- [x] Add project connection step that can be skipped for existing course creation
- [x] Preserve current course create/edit behavior
- [x] Add draft publishing checklist using existing lesson readiness and governance signals
- [x] Add tests for course creation through the Product Studio route alias

## Phase 4: Knowledge Pipeline And Artifact Registry

- [x] Add knowledge source management screens and APIs
- [x] Add artifact registry screens and APIs
- [x] Link artifacts to projects, products, knowledge sources, and existing course/lesson records where applicable
- [x] Represent current source-backed lesson data in the knowledge pipeline without deleting original source rows
- [x] Add generation run history for future AI-assisted workflows
- [x] Add tests for source and artifact linkage

## Phase 5: Review Center Expansion

- [ ] Create Review Center surfaces for lesson readiness and generated artifact review
- [ ] Reuse existing lesson governance and readiness checks
- [ ] Add review request and review decision records
- [ ] Ensure generated artifacts default to draft or review-required states
- [ ] Add tests proving unapproved generated outputs do not become learner-deliverable

## Phase 6: Learner Portal V2

- [ ] Reframe the student dashboard as Learner Portal
- [ ] Show assigned/enrolled products using existing course/program enrollments first
- [ ] Add learner views for learning paths, resources, downloads, progress, and certificates
- [ ] Preserve existing governed lesson runtime and progress tracking
- [ ] Add tests for learner portal route aliases and current progress visibility

## Phase 7: Access Grants

- [ ] Add access grant model for product, course, program, artifact, and membership-style access
- [ ] Backfill access grants from existing course and program enrollments where appropriate
- [ ] Use access grants as the authorization layer for future products without weakening current role/auth rules
- [ ] Add tests for explicit access and denied access behavior

## Phase 8: Analytics V2

- [ ] Define product, source, artifact, review, and learner analytics events
- [ ] Add analytics dashboards for product engagement, learner progress, source coverage, artifact activity, and review cycle time
- [ ] Reuse existing assessment, progress, certification, and runtime analytics
- [ ] Add tests for analytics read models where backend behavior changes

## Phase 9: Commercialization Readiness

- [ ] Design pricing, checkout, order, subscription, and entitlement concepts around access grants
- [ ] Add product page readiness states before payment integration
- [ ] Keep payment provider implementation out of earlier phases
- [ ] Prepare checkout and membership specifications without changing auth or learner runtime behavior
- [ ] Add acceptance tests once payment/access behavior is implemented
