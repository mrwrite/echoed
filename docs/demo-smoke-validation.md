# Demo Smoke Validation

This runbook covers the bounded browser smoke flow for the seeded EchoEd demo environment. It is intentionally limited to one deterministic student flagship path in Phase 1.

## Purpose

Use this smoke flow to confirm that the seeded demo environment is usable in a real browser before a live demo. It is not a full end-to-end suite and it does not replace backend or component-level verification.

## Prerequisites

- Backend dependencies are installed and the API can start locally.
- Frontend dependencies are installed, including Playwright.
- The deterministic demo seed has been applied successfully.
- The frontend app is available at `http://127.0.0.1:4200` unless you override `PLAYWRIGHT_BASE_URL`.

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

## Current Execution Status

Browser-level execution is environment-blocked in this workspace until Playwright Chromium can be installed successfully. The current blocker is local disk-space exhaustion during `npx playwright install chromium`.

## Troubleshooting

If browser setup or execution fails:

1. Check free disk space and make sure there is enough room for the Playwright Chromium download.
2. Clear Angular cache if local build artifacts have accumulated:

```powershell
npx ng cache clean
```

3. Retry the browser install from `frontend`:

```powershell
npx playwright install chromium
```

4. Rerun the smoke:

```powershell
npm run smoke:demo:student
```
