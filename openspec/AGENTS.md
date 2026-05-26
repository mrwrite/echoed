# EchoEd Agent Rules

## Repo Orientation
EchoEd is split into:
- `frontend/` for Angular
- `backend/` for FastAPI, SQLAlchemy, Alembic, and pytest

Always inspect the existing implementation before writing code.

---

## Mandatory Search Targets

Before changing auth or onboarding, inspect:
- `backend/app/auth.py`
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/orgs.py`
- relevant frontend auth and onboarding files in `frontend/src`

Before changing curriculum or progress, inspect:
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/enum.py`
- `backend/app/crud/progress.py`
- `backend/app/api/routes/progress.py`
- `backend/app/api/routes/start_course.py`
- `backend/app/api/routes/lesson_sessions.py`

Before changing organization behavior, inspect:
- `backend/app/api/routes/orgs.py`
- related models and schemas

Before changing layout/accessibility, inspect:
- shared layout and shell files in `frontend/src`
- global Tailwind and shared UI component files

---

## Hard Constraints
- DO NOT create duplicate routers for existing domains
- DO NOT create duplicate Angular services for auth, orgs, or layout
- DO NOT create duplicate progress tracking systems
- DO NOT create parallel onboarding flows
- DO NOT bypass existing models and schemas when equivalent structures already exist

---

## Frontend Rules
- Use Angular standalone component patterns
- Use Tailwind CSS
- Reuse existing components, guards, and services
- Fix shared shell/layout issues at the shared level when possible
- Prefer minimal targeted changes over broad rewrites

---

## Backend Rules
- Reuse existing route files under `backend/app/api/routes`
- Reuse `models.py`, `schemas.py`, and `enum.py`
- Reuse CRUD helpers where present
- Preserve current API shape unless the change explicitly requires updating it
- If API contracts change, update frontend integration in the same change

---

## Testing Rules
If behavior changes, update or add tests in `backend/tests`.

Prioritize existing test areas such as:
- org permissions
- course permissions
- enroll
- start course
- student course
- student progress
- forum endpoints
- uploads
- unit/lesson/activity endpoints

---

## Implementation Standard
For every change:
1. inspect existing code first
2. identify what can be reused
3. make the smallest change that satisfies the spec
4. update tests
5. avoid unnecessary abstractions

If uncertain, read more of the existing repo before generating new code.