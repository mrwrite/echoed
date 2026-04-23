# EchoEd Project Context

## Overview
EchoEd is a full-stack educational platform with a separate Angular frontend and FastAPI backend.

Repository structure:
- `frontend/` = Angular application
- `backend/` = FastAPI application, SQLAlchemy models, Alembic migrations, and pytest suite
- `openspec/` = spec-driven change workflow

This is an evolving application with existing auth, organizations, curriculum, progress tracking, uploads, forum/community, analytics, and lesson session flows already in place. New work must integrate with these existing systems rather than creating replacements or parallel implementations.

---

## Repository Structure

### Frontend
Primary frontend source:
- `frontend/src`

Frontend dependencies and tooling indicate:
- Angular
- Tailwind CSS
- Storybook
- standalone-component-oriented Angular development

### Backend
Primary backend source:
- `backend/app`

Important backend areas:
- `backend/app/main.py`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/auth.py`
- `backend/app/database.py`
- `backend/app/deps.py`
- `backend/app/enum.py`
- `backend/app/crud/`
- `backend/app/api/routes/`

### Migrations
Database migrations:
- `backend/alembic/versions`

### Tests
Backend tests:
- `backend/tests`

---

## Confirmed Backend Capabilities

The backend already has route modules for:

- `auth.py`
- `orgs.py`
- `users.py`
- `courses.py`
- `units.py`
- `lessons.py`
- `activities.py`
- `progress.py`
- `start_course.py`
- `lesson_sessions.py`
- `assignments.py`
- `sections.py`
- `enroll.py`
- `invites.py`
- `preferences.py`
- `analytics.py`
- `uploads.py`
- `badges.py`
- `posts.py`
- `threads.py`
- `meta.py`

### Implication
Before adding any new endpoint, router, or service logic, always inspect these existing route modules first. In most cases, new behavior should extend one of these existing routes rather than introducing a new route family.

---

## Backend Architecture

### Core Files
- `backend/app/main.py` wires the API
- `backend/app/models.py` contains SQLAlchemy models
- `backend/app/schemas.py` contains request/response schemas
- `backend/app/auth.py` contains authentication logic
- `backend/app/enum.py` contains enums such as progress-related enums
- `backend/app/crud/progress.py` and `backend/app/crud/badges.py` indicate domain-specific CRUD helpers already exist

### Key Rule
Do not create new model files, schema systems, or auth systems when equivalent functionality already exists in these files.

### Persistence
The application uses:
- SQLAlchemy
- PostgreSQL
- Alembic migrations

Migration history already includes:
- users
- courses
- lessons
- activities
- orgs and course versions
- progress status enums
- student unit progress
- segment progress cascades
- student course model changes
- badges
- storybook pages

### Implication
Changes involving data structure should respect the existing migration lineage and current table ownership. Avoid duplicating concepts already represented in migrations.

---

## Confirmed Domain Model Expectations

Based on prior project context and migration history, EchoEd includes models and relationships around:
- `User`
- `Organization`
- `Course`
- `Unit`
- `Lesson`
- `Activity`
- `Media`
- `StudentCourse`
- `StudentUnitProgress`
- `SegmentProgress`

Progress-related enums live in:
- `backend/app/enum.py`

### Progress Tracking
Progress is already part of the product architecture. New work must build on the existing `StudentCourse`, `StudentUnitProgress`, and `SegmentProgress` model instead of introducing a parallel progress solution.

### Organizations
Organization support is already part of the app and is backed by:
- migrations
- `backend/app/api/routes/orgs.py`

Any organization onboarding work must extend the existing org model and org routes.

---

## Frontend Architecture

### Location
Primary frontend source lives under:
- `frontend/src`

### Confirmed Tooling/Patterns
The frontend is Angular-based and uses:
- Angular
- Tailwind CSS
- Storybook

From prior EchoEd context, the app is using:
- standalone Angular components
- Tailwind-based styling rather than Angular Material as the primary UI direction
- reusable component development via Storybook

### Frontend Rules
- Use standalone components only
- Reuse existing services, guards, and routes before creating new ones
- Prefer shared Tailwind utility patterns and shared UI components over page-specific hacks
- Fix shell/layout issues at the shared layout level when possible

---

## Existing Product Areas

### Authentication
Existing auth already exists in the backend and likely maps to an existing frontend auth flow. Do not create a second auth path. Extend the current login/register/token/onboarding flow instead.

Backend auth locations:
- `backend/app/auth.py`
- `backend/app/api/routes/auth.py`

### Organizations
Existing organization functionality already exists.

Backend organization location:
- `backend/app/api/routes/orgs.py`

Organization setup during onboarding must plug into the existing org route and data model.

### Curriculum
Curriculum-related functionality already exists.

Relevant backend routes:
- `courses.py`
- `units.py`
- `lessons.py`
- `activities.py`
- `sections.py`

### Progress / Start / Lesson Sessions
Existing student progression and learning-session behavior already exists.

Relevant backend routes:
- `progress.py`
- `start_course.py`
- `lesson_sessions.py`

Relevant backend CRUD:
- `backend/app/crud/progress.py`

Any work involving:
- start course
- continue course
- progress updates
- segment completion
- teacher-led lesson launch
must extend these existing systems.

### Community / Discussion
Forum-style behavior already exists.

Relevant backend routes:
- `posts.py`
- `threads.py`

### Uploads / Media / Storybook Assets
Uploads already exist.

Relevant backend routes:
- `uploads.py`

Migration and file structure also suggest support for storybook-related uploads/pages and badge assets.

---

## Testing Expectations

Backend tests already exist and cover multiple major product areas, including:
- org permissions
- course permissions
- enroll flow
- start course flow
- student course behavior
- student progress behavior
- forum endpoints
- delete endpoints
- unit/lesson/activity endpoints
- upload endpoints
- badges

Relevant test files include:
- `test_org_permissions.py`
- `test_course_permissions.py`
- `test_enroll_endpoint.py`
- `test_start_course_endpoint.py`
- `test_student_course.py`
- `test_student_progress.py`
- `test_forum_endpoints.py`
- `test_unit_lesson_activity_endpoints.py`

### Rule
If you change backend behavior in one of these domains, update or add tests in the existing pytest suite. Do not leave behavior changes untested.

---

## Current OpenSpec Guidance for EchoEd

When implementing an OpenSpec change, always inspect the following before generating code:

### For auth or onboarding changes
- `backend/app/auth.py`
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/orgs.py`
- relevant frontend auth service, auth guards, registration/login routes, and onboarding components in `frontend/src`

### For curriculum or progress changes
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/enum.py`
- `backend/app/crud/progress.py`
- `backend/app/api/routes/progress.py`
- `backend/app/api/routes/start_course.py`
- `backend/app/api/routes/lesson_sessions.py`
- related frontend dashboard, lesson, and progress UI under `frontend/src`

### For layout or accessibility changes
- shared shell/app layout files in `frontend/src`
- shared Tailwind/global style configuration
- existing Storybook-backed UI components if the issue is component-level

---

## Critical Constraints

### Reuse First
Before adding code, search for an existing implementation in:
- `frontend/src`
- `backend/app/api/routes`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/crud`
- `backend/tests`

### Do Not Duplicate
Do not create:
- a second auth service or auth flow
- a second org onboarding system
- duplicate course/progress/session endpoints
- duplicate models for existing domain concepts
- parallel layout systems
- frontend-only workarounds for backend-owned domain logic

### Extend Existing Systems
Prefer:
- extending `orgs.py` over creating new organization endpoints
- extending `auth.py` and existing registration/login flow over creating alternate onboarding auth logic
- extending `progress.py`, `start_course.py`, and `lesson_sessions.py` over inventing new progress/session flows
- updating existing schemas/models over adding disconnected structures

---

## Accessibility and UX Standards

EchoEd must remain readable and predictable for students, teachers, and admins.

Required standards:
- readable contrast on light and dark surfaces
- no washed-out text for primary content
- sidenav must not overlap main content
- responsive layout must remain usable on desktop and mobile
- onboarding and lesson flows must be simple and predictable
- shared shell issues should be fixed at the shared shell/layout layer

---

## Definition of a Good EchoEd Change

A good change:
- reuses existing backend routes and models
- reuses existing frontend app structure
- makes minimal, targeted changes
- updates tests where behavior changes
- avoids architectural drift
- improves product behavior without introducing duplicate systems

A bad change:
- adds new routers for existing domains
- adds new models for existing concepts
- creates a second onboarding or progress path
- patches UI symptoms without fixing shared layout/style causes
- ignores existing tests and migration history