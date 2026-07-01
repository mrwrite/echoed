# EchoEd V2 Release Candidate Notes

## Release Candidate Scope

EchoEd V2 is a platform layer above the existing education runtime. This release candidate includes workspace navigation, Product Studio, projects, knowledge sources, artifacts, Review Center, Learner Portal V2, Access Grants, Analytics V2, demo readiness, public product placeholders, and commercialization metadata.

This release candidate does not include payments, checkout execution, subscriptions, memberships, marketplace behavior, AI generation execution, or new learner runtime behavior.

## Runtime Preservation

The existing education runtime remains authoritative for learner-visible learning delivery:

- Course, Unit, Lesson, Activity, Program, Assessment, Certification, progress, enrollment, and governance behavior are unchanged.
- Product wrapper publishing does not publish runtime lessons.
- Artifact approval does not create learner-visible runtime content.
- AccessGrant records can expose Product-level access, but they do not create StudentCourse enrollments.
- Public product pages are presentation placeholders and do not execute checkout or enrollment.

## Release Candidate Validation

Run these checks from a clean working database state before demo or release handoff.

Local validation status on 2026-06-30:

- OpenSpec strict validation passed.
- Full backend tests passed after stabilizing the test harness.
- Full frontend build and tests passed.
- PostgreSQL fresh migration and live reseed could not be executed in this session because Docker Desktop did not expose a ready daemon and the local `postgresql-x64-17` service could not be started.
- SQLite is not a valid fresh-migration substitute for this Alembic history because older migrations use PostgreSQL-style `ALTER COLUMN` operations.

### Fresh Migration

```powershell
cd backend
$env:DATABASE_URL = "sqlite:///../phase10_fresh_migration.db"
python -m alembic upgrade head
```

Expected result: Alembic upgrades to head without errors.

### Demo Reseed

```powershell
$env:DATABASE_URL = "sqlite:///../phase10_fresh_migration.db"
python ..\backend\scripts\reseed_demo.py
```

Expected result: the script prints `EchoEd demo reseed completed successfully.` and lists the V2 workspace, demo guide route, and learner route.

If PostgreSQL is unavailable locally, use the backend demo seed tests as the bounded code-level confidence check:

```powershell
pytest backend\tests\test_v2_demo_seed_phase8_6.py backend\tests\test_demo_operator_docs_phase2.py -q
```

These tests verify deterministic V2 demo seed behavior, operator docs, and runtime non-regression, but they do not replace a live PostgreSQL migration/reseed check before release.

### OpenSpec

```powershell
openspec validate echoed-v2-platform-evolution --strict
```

Expected result: the change is valid.

### Backend Tests

```powershell
pytest backend\tests -q
```

Expected result: backend tests pass. The forum endpoint collection blocker has been removed by using the shared isolated SQLite fixture instead of relying on a collection-time `DATABASE_URL` mutation.

### Frontend Build And Tests

```powershell
cd frontend
cmd /c .\node_modules\.bin\ng.cmd build
cmd /c .\node_modules\.bin\ng.cmd test --watch=false --browsers=ChromeHeadless
```

Expected result: build and tests pass. Existing Angular budget, Sass deprecation, and template optional-chain warnings may still appear.

## Demo Flow

Use `/workspace/demo-readiness` as the operator script.

Recommended five-minute path:

1. `/workspace` for the V2 lifecycle overview.
2. `/workspace/product-studio` for product creation and future AI generation placeholders.
3. `/workspace/projects` for source-to-artifact pipeline context.
4. `/workspace/artifacts` for reviewable generated knowledge outputs.
5. `/workspace/review-center` for governance and readiness messaging.
6. `/workspace/analytics` for read-only health metrics.
7. `/workspace/access` for AccessGrant management.
8. `/products` and `/products/:slug` for public product placeholders.
9. `/learn` as `normalstudent` for learner portal visibility backed by existing runtime and V2 access.

## Known Limitations

- Review request and review decision audit records remain a later task.
- AI generation runs are metadata-only placeholders; no generation execution is implemented.
- Commercial dashboard revenue, conversion, ARR, billing, plans, domains, and AI usage are placeholders.
- Public product pages have disabled enroll/checkout actions.
- V2 analytics use existing wrapper/runtime data and do not add complex event tracking yet.
