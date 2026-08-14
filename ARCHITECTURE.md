# EchoEd Architecture

EchoEd is a full-stack education platform with a separate Angular frontend and FastAPI backend.

## System Overview

```text
frontend/ Angular app
    |
    | HTTP API calls, proxied locally through frontend/proxy.conf.json
    v
backend/ FastAPI app
    |
    | SQLAlchemy models and Alembic migrations
    v
PostgreSQL or local development database
```

The repository also includes:
- `docs/` for runbooks and public project guidance.
- `openspec/` for spec-driven planning and validation.
- `curriculum/` for curriculum source and seed material.
- `backend/scripts/reseed_demo.py` for deterministic demo data.

## Frontend

Location: `frontend/`

Primary technologies:
- Angular
- Tailwind CSS and SCSS
- Playwright for demo smoke testing
- Karma/Jasmine for Angular tests

Important paths:
- `frontend/src/app/pages/landing/` public landing page
- `frontend/src/app/pages/login/` login flow
- `frontend/src/app/pages/registration/` registration flow
- `frontend/src/app/pages/user-dashboard/` student, teacher, and admin surfaces
- `frontend/src/app/shared/lesson-viewer.*` shared lesson rendering
- `frontend/src/environments/` environment API settings
- `frontend/tests/demo/` browser smoke tests

Local frontend API calls use `frontend/proxy.conf.json` to reach the backend at `http://127.0.0.1:8000`.

Page components are loaded through explicit standalone `loadComponent` route boundaries. Public, authentication, onboarding, Learn, Teach, Studio, Organization, Admin, and legacy compatibility routes keep their existing guards and URLs while downloading feature code on demand. Recognized dynamic-import failures use the lazy `/load-error` recovery route.

## Backend

Location: `backend/`

Primary technologies:
- FastAPI
- SQLAlchemy
- Alembic
- pytest
- JWT-based authentication

Important paths:
- `backend/app/main.py` wires the API.
- `backend/app/models.py` contains SQLAlchemy models.
- `backend/app/schemas.py` contains request and response schemas.
- `backend/app/auth.py` contains authentication logic.
- `backend/app/database.py` configures database access.
- `backend/app/api/routes/` contains route modules.
- `backend/app/crud/` contains domain helper functions where present.
- `backend/alembic/versions/` contains database migrations.
- `backend/tests/` contains the backend test suite.

The application exposes process-only `/health/live` and database-backed `/health/ready`. HTTP responses include a privacy-safe request ID and optional bounded correlation ID. Backend middleware records normalized route, method, status family, and duration through the structured/redacted logging and in-process metrics foundation. Optional Prometheus text export at `/internal/metrics` is disabled by default and token protected when enabled. These are vendor-neutral operational foundations, not distributed tracing or a production hosting architecture; see [the observability policy](docs/observability/logging-policy.md) and [runbook](docs/operations/observability-runbook.md).

High-impact supported mutations additionally write a transaction-bound `audit_events` record with allowlisted metadata and minimized before/after state. Platform and organization review APIs apply explicit scopes; per-scope SHA-256 chains support integrity verification after backup/restore. This is application-level tamper evidence, not externally anchored tamper-proof storage. See [the audit-event policy](docs/audit/audit-event-policy.md).

Backend authorization uses explicit platform/organization role allowlists plus reusable organization, section, course-content, forum-ownership, and learner-progress scope checks. Sensitive routes use a configurable process-local fixed-window limiter; it is suitable only for the checked-in single-Uvicorn-process topology and must be replaced by shared storage before horizontal scaling. The canonical policy and limitations are in [docs/security/role-authorization-policy.md](docs/security/role-authorization-policy.md) and [docs/security/rate-limiting-policy.md](docs/security/rate-limiting-policy.md).

## Existing Domain Boundaries

Reuse existing systems before adding new ones:
- Authentication: `backend/app/auth.py`, `backend/app/api/routes/auth.py`
- Organizations: `backend/app/api/routes/orgs.py`
- Courses and lessons: `courses.py`, `units.py`, `lessons.py`, `activities.py`
- Progress and learning runtime: `progress.py`, `start_course.py`, `lesson_sessions.py`
- Sections and assignments: `sections.py`, `assignments.py`
- Forum-style discussion: `posts.py`, `threads.py`
- Uploads and assets: `uploads.py`
- V2 workspace/product wrappers: `v2_platform.py`

Do not create parallel auth, organization, progress, lesson, or onboarding systems.

## Demo Seed System

The deterministic demo is reset with:

```powershell
backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py
```

The operator runbook is [docs/demo-readiness.md](docs/demo-readiness.md). The public evaluation guide is [docs/public-demo.md](docs/public-demo.md).

## OpenSpec Workflow

OpenSpec changes live in `openspec/changes/`.

Useful commands:

```powershell
cmd /c openspec status --change "<change-name>" --json
cmd /c openspec validate <change-name> --strict
cmd /c openspec instructions apply --change "<change-name>" --json
```

In this repository, implementation is performed by working through the task file for a change and checking off completed tasks. There is no `openspec apply` CLI subcommand.

## Testing Strategy

Backend tests:

```powershell
cd backend
pytest
```

Frontend build:

```powershell
cd frontend
cmd /c npm run build
```

Frontend unit tests:

```powershell
cd frontend
cmd /c .\node_modules\.bin\ng.cmd test --watch=false --browsers=ChromeHeadless
```

Demo smoke:

```powershell
cd frontend
cmd /c .\node_modules\.bin\playwright.cmd test tests/demo/student-flagship-smoke.spec.ts
```

## Contribution Guidance

Changes should be small, scoped, and aligned with existing boundaries. Documentation-only changes do not need backend migrations or frontend tests, but they should still pass OpenSpec validation when tied to an OpenSpec change.

## Operational lifecycle

`app.operational_config` validates environment, database, secret, host/proxy, origin, release, storage, migration, and observability decisions before route/database initialization. `TrustedHostMiddleware` and peer-CIDR forwarding resolution define the application network boundary; Uvicorn implicit proxy processing is disabled. Schema migration is a one-shot pre-start operation, health separates process liveness from database readiness, and the FastAPI lifespan disposes the SQLAlchemy engine during bounded shutdown. See [deployment architecture and limits](docs/operations/deployment-runbook.md).
