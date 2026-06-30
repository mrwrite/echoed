# Pilot Verification Checklist

This checklist is the bounded go/no-go flow for preparing EchoEd for a small pilot walkthrough.

Related runbooks:

- [Demo Readiness Runbook](./demo-readiness.md)
- [Demo Smoke Validation](./demo-smoke-validation.md)

## Before You Start

- confirm backend dependencies are installed
- confirm frontend dependencies and Playwright are installed
- confirm the backend and frontend will run against the intended local environment

## Reset and Startup

1. Apply backend migrations.
2. Run `backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py`.
3. Start the backend locally.
4. Start the frontend locally.
5. Open `http://127.0.0.1:4200/login` and confirm the login page renders.

## Automated Verification

Run these in order:

```powershell
cd backend
pytest -q
```

```powershell
cd frontend
cmd /c .\node_modules\.bin\ng.cmd test --watch=false --browsers=ChromeHeadless
```

```powershell
cd frontend
cmd /c .\node_modules\.bin\playwright.cmd test tests/demo/student-flagship-smoke.spec.ts
```

Treat any failure here as a pilot-readiness failure until explained.

## Manual Student Checks

- sign in as `normalstudent`
- confirm the active flagship course card is visible
- confirm `Continue lesson` enters the governed lesson path
- confirm the lesson page loads with the governed viewer
- confirm the student can exit the lesson and return to the dashboard safely

## Manual Teacher Checks

- sign in as `teacher`
- confirm the dashboard loads without broken or empty shell states
- confirm the flagship course context is visible enough for a live walkthrough
- confirm learner/runtime context is visible enough to explain the archetype story

These teacher checks remain intentionally manual in Phase 1.

## Manual Admin/Governance Checks

Only run these if the walkthrough needs governance visibility:

- sign in as `orgadmin`
- confirm the flagship course remains present
- confirm staff-only governance reads remain staff-only
- confirm the environment does not require manual repair to expose the flagship governance story

## Troubleshooting

- If login fails after reseed, rerun the reseed before changing any data manually.
- If the smoke test stays on `/login`, check that the frontend and backend are pointed at the same local environment.
- If PowerShell blocks `npm`, use the direct `cmd /c` binary commands.
- If `npm` fails because of local cache or disk pressure, clear space and rerun the direct commands.
- If the student dashboard loads but the flagship course is missing, stop and treat the demo environment as invalid.

## What This Checklist Proves

- the deterministic demo can be restored without manual cleanup
- the backend and frontend regression suites are green
- the bounded student browser story still works
- the teacher dashboard is manually demonstrable

## What This Checklist Does Not Prove

- exhaustive teacher browser coverage
- full end-to-end resilience across every route
- deployment health outside the local pilot-prep environment
- broader operational monitoring or production SRE readiness
