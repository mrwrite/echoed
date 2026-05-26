# Demo Smoke Validation

This runbook covers the bounded browser smoke flow for the seeded EchoEd demo environment. It is intentionally limited to one deterministic student flagship path in Phase 1.

Related runbooks:

- [Demo Readiness Runbook](./demo-readiness.md)
- [Pilot Verification Checklist](./pilot-verification-checklist.md)

## Purpose

Use this smoke flow to confirm that the seeded demo environment is usable in a real browser before a live demo. It is not a full end-to-end suite and it does not replace backend or component-level verification.

## Prerequisites

- Backend dependencies are installed and the API can start locally.
- Frontend dependencies are installed, including Playwright.
- The deterministic demo seed has been applied successfully.
- The frontend app is available at `http://127.0.0.1:4200` unless you override `PLAYWRIGHT_BASE_URL`.
- The backend API is reachable through the frontend proxy at `http://127.0.0.1:8000`.

## Recommended Preflight

Before running the smoke, confirm these conditions:

- `backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py` completes successfully.
- The backend is serving authenticated routes without migration errors.
- The frontend login page loads at `/login`.
- The demo credentials still work for `normalstudent` / `password`.
- You are not relying on a stale browser session from a previous run.

## Prepare the Demo Environment

### 1. Apply backend migrations

From the repo root:

```powershell
cd backend
venv\Scripts\python.exe -m alembic upgrade head
```

### 2. Reseed the deterministic demo

From the repo root:

```powershell
backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py
```

### 3. Start the backend

Make the API available locally at `http://127.0.0.1:8000`.

If you use the local FastAPI startup flow, start it from `backend` with your normal development command before launching the frontend.

### 4. Start the frontend

From `frontend`:

```powershell
npm start
```

The Angular dev server proxies `/api` requests to `http://127.0.0.1:8000` through `proxy.conf.json`.

## Install Playwright

From `frontend`:

```powershell
npm install
npx playwright install chromium
```

## Run the Student Smoke

From `frontend`:

```powershell
npm run smoke:demo:student
```

Windows fallback when `npm` is blocked by PowerShell execution policy or npm cache issues:

```powershell
cmd /c .\node_modules\.bin\playwright.cmd test tests/demo/student-flagship-smoke.spec.ts
```

Optional overrides:

```powershell
$env:PLAYWRIGHT_BASE_URL="http://127.0.0.1:4200"
$env:DEMO_STUDENT_USERNAME="normalstudent"
$env:DEMO_STUDENT_PASSWORD="password"
npm run smoke:demo:student
```

## What the Smoke Validates

- login works through the real browser auth flow
- the seeded student dashboard loads
- the seeded flagship `Introduction to Africa` course appears in the continuation card
- the student can continue into the governed lesson route
- the lesson experience, lesson state, lesson viewer, and progression indicator render

## Phase 1 Non-Goals

- no teacher or admin browser smoke coverage yet
- no assessment-completion or certification walkthrough
- no visual regression, screenshot capture, or performance measurement
- no backend mutation orchestration beyond the normal student continuation flow
- no CI pipeline redesign

## Pass / Fail Meaning

Pass means the seeded student flagship story is working at a browser level for demo confidence.

Fail means one of these is broken:

- the local app is not started correctly
- the demo seed is stale or missing
- the seeded student cannot authenticate
- the dashboard no longer exposes the flagship continuation path
- the governed lesson route is failing to load or render

This smoke flow is intentionally bounded. A pass does not imply exhaustive product coverage.

## Troubleshooting

If browser setup or execution fails:

1. If login fails and the browser remains on `/login`, rerun the deterministic reseed:

```powershell
backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py
```

2. Check that the frontend is pointing at the intended API and that the backend is actually running.
3. If `npm run smoke:demo:student` fails under PowerShell because script execution is disabled, run:

```powershell
cmd /c .\node_modules\.bin\playwright.cmd test tests/demo/student-flagship-smoke.spec.ts
```

4. Check free disk space and make sure there is enough room for Playwright browser binaries and frontend build artifacts.
5. Clear Angular cache if local build artifacts have accumulated:

```powershell
npx ng cache clean
```

6. Retry the browser install from `frontend`:

```powershell
npx playwright install chromium
```

7. Rerun the smoke:

```powershell
npm run smoke:demo:student
```

8. If the smoke still fails after reseed, treat that as a pilot-readiness failure until you can explain whether the issue is:

- auth/login
- dashboard continuation
- governed lesson restoration
- local startup/proxy drift
