# Demo Readiness Runbook

This runbook documents the bounded EchoEd pilot-demo startup flow for the deterministic flagship environment.

Related runbooks:

- [Demo Smoke Validation](./demo-smoke-validation.md)
- [Pilot Verification Checklist](./pilot-verification-checklist.md)
- [Demo UI Polish Checklist](./demo-ui-polish-checklist.md)

## Purpose

Use this flow before a live demo when you need to:

- apply schema migrations
- reseed the canonical demo organization, users, and flagship course
- restore deterministic learner/runtime states
- verify the bounded student and teacher walkthrough paths without manual database repair

## Canonical Demo Context

- Demo organization: `EchoEd Demo School`
- Flagship course: `Introduction to Africa`
- Demo section: `Grade 3 - Cohort A`
- Shared seeded password: `password`

## Canonical Demo Accounts

### Staff

- `orgadmin` / `password`
- `teacher` / `password`
- `contentadmin` / `password`

### Reference students

- `student1` / `password`
- `student2` / `password`

### Deterministic flagship archetypes

- `masteredstudent` -> expected runtime state `enrichment`
- `reteachstudent` -> expected runtime state `reteach`
- `reviewstudent` -> expected runtime state `review`
- `monitorstudent` -> expected runtime state `monitor`
- `normalstudent` -> expected runtime state `normal`

## Startup Flow

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

What this guarantees:

- canonical demo users are reset to their known usernames, emails, roles, and passwords
- duplicate demo identities are cleaned up before final upsert
- flagship learner progress, attempts, and intervention states return to deterministic demo defaults

### 3. Start the backend

Make the backend available locally at `http://127.0.0.1:8000` using your normal development startup command.

### 4. Start the frontend

From `frontend`:

```powershell
npm start
```

The frontend dev server is expected at `http://127.0.0.1:4200` and proxies `/api` calls to the backend.

## Automated Confidence Layer

Phase 1 treats these as the authoritative automated checks:

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

What they prove:

- backend runtime, progression, auth, and demo-seed regressions remain covered
- Angular component and route behavior remains covered
- one real-browser student flagship path still works: login, dashboard, continue lesson, governed lesson entry

What remains intentionally manual in Phase 1:

- teacher dashboard walkthrough quality and narration
- staff governance-summary storytelling
- broader platform resilience outside the bounded flagship smoke

## Recommended Demo Walkthrough

1. Run migrations.
2. Run `backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py`.
3. Sign in as `normalstudent` and confirm the active flagship course appears.
4. Continue into the governed lesson and confirm the lesson view loads.
5. Return safely to the dashboard.
6. Sign in as `teacher` and confirm the dashboard loads with stable flagship visibility.
7. Sign in as `orgadmin` only if you need the staff governance route checks.

## Expected Teacher/Admin Outcomes

After reseeding:

- the teacher dashboard should open without manual enrollment repair
- the flagship course should remain visible and stable
- the runtime intervention mix should remain deterministic across the archetype learners
- learner access should still be denied from staff governance endpoints

## Known Acceptable Demo Warning

One warning remains intentionally acceptable in the flagship demo:

- surface: `competency_evidence_integrity`
- warning code: `unaligned_assessment_mastery_evidence`
- assessment: `Introduction to Africa Ambiguous Evidence Check`
- demonstrated by: `monitorstudent`

This warning is acceptable because it is deterministic, non-blocking, and intentionally demonstrates bounded educator ambiguity rather than corrupted data.

## Troubleshooting Notes

Use these when demo prep fails:

- If a seeded student cannot log in, rerun `backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py` before changing rows manually.
- If the student smoke stays on `/login`, verify the frontend is pointed at the intended backend and that the reseed completed against the same database the backend is using.
- If `npm` is blocked by PowerShell execution policy or npm cache issues, use the direct `cmd /c` binary commands shown above.
- If the dashboard loads but the flagship course is missing, treat that as a failed demo state rather than a cosmetic issue.
- If the lesson route opens but governed lesson restoration fails, stop and verify backend runtime integrity before changing demo data manually.

## Recovery Steps

1. Reapply migrations.
2. Rerun the deterministic reseed.
3. Restart backend and frontend.
4. Re-run the automated confidence layer.
5. Recheck the student flagship walkthrough with `normalstudent`.
6. Recheck the teacher dashboard with `teacher`.
7. Treat any need for manual row cleanup, reenrollment, or attempt deletion as a demo-readiness failure.

## Guardrails

- no auth bypass is used
- no governed runtime protections are disabled
- no manual database repair is part of the expected startup path
- no broader CI or deployment automation changes are required for this runbook
