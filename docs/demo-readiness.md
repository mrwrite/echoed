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
- V2 workspace: `EchoEd Demo Workspace`
- V2 project: `EchoEd V2 Platform Evolution Dogfood`
- V2 guide route: `/workspace/demo-readiness`
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
- V2 dogfooding wrapper records are present for workspace, project, knowledge sources, artifacts, products, access grants, review queues, learner visibility, and analytics
- no Course, Unit, Lesson, progress, enrollment, or governance behavior is changed by the V2 wrapper layer

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
3. Sign in as `contentadmin` and open `/workspace/demo-readiness`.
4. Walk `/workspace` -> `/workspace/product-studio` -> `/workspace/projects` -> `/workspace/artifacts` -> `/workspace/review-center` -> `/workspace/analytics`.
5. Sign in as `normalstudent` and open `/learn` to confirm the published V2 product appears through an active access grant.
6. Continue into the existing flagship governed course only through the existing learner course runtime.
7. Sign in as `teacher` and confirm the existing dashboard loads with stable flagship visibility.
8. Sign in as `orgadmin` only if you need the staff governance route checks.

## Five-Minute Walkthrough Script

Use this script when a new viewer needs the V2 value proposition quickly.

### 0:00 - Open with Workspace

Say: "EchoEd is not another LMS. It is a governed product studio for turning organizational knowledge into trusted learning products."

Show `/workspace`. Point to the lifecycle: Knowledge Sources, Artifacts, Products, Review Center, Learners, Access, and Analytics.

### 0:45 - Show Product Studio

Say: "Creators start by defining the product wrapper, then connect source knowledge and existing runtime delivery when it is ready."

Show `/workspace/product-studio`. Call out that AI generation is intentionally disabled/coming soon in this phase.

### 1:30 - Show Knowledge In

Say: "Projects are where source knowledge becomes structured product work."

Open `/workspace/projects`, then the seeded EchoEd project if available. Explain that sources are durable, reusable records.

### 2:10 - Show AI Understanding and Artifacts

Say: "Generated outputs become reviewable artifacts first, not learner-visible lessons."

Open `/workspace/artifacts`. Show approved, in-review, and needs-changes states.

### 2:50 - Show Review and Governance

Say: "Trust is the workflow. Artifact approval does not publish a lesson, and product approval does not override runtime governance."

Open `/workspace/review-center`. Point to pending artifacts, draft/in-review products, and lesson governance messaging.

### 3:35 - Show Learner Delivery

Say: "Products organize access. The existing course and lesson runtime still controls governed delivery."

Sign in as `normalstudent` and open `/learn`. Show the active product grant, then only continue into lessons through the existing governed course path.

### 4:25 - Close with Analytics

Say: "Operators can see product health, knowledge pipeline health, learner engagement, access, and review signal without adding complex tracking yet."

Open `/workspace/analytics` and close on read-only dashboard metrics.

## Known V2 Demo Limitations

- AI generation execution is not implemented; generation runs are seeded metadata only.
- Payments, checkout, subscriptions, memberships, marketplace, and public product pages are intentionally absent.
- Product wrapper status does not publish runtime Course, Unit, Lesson, or Activity records.
- AccessGrant visibility does not create StudentCourse enrollment.
- Review request and review decision audit records are still a later task.
- Analytics V2 uses current wrapper and runtime data; complex event tracking is not implemented.

## V2 Dogfooding Demo Data

Phase 8.6 adds wrapper-only demo records after the canonical course seed:

- Workspace: `EchoEd Demo Workspace`
- Project: `EchoEd V2 Platform Evolution Dogfood`
- Knowledge sources: OpenSpec phase plan, governed runtime preservation notes, Learner Portal access walkthrough
- Products: published `EchoEd V2 Operator Walkthrough`, in-review `EchoEd Governance Review Pack`, and course-backed `Introduction to Africa Governed Course Product`
- Artifacts: approved workspace storyboard, in-review review checklist, needs-changes learner access explainer
- Access grant: active manual product grant for `normalstudent`
- Generation run: metadata-only demo placeholder marked with `execution: not_run`

These records are intended to populate Product Studio, Projects, Artifact Registry, Review Center, Learner Portal, and Analytics without creating runtime lessons or changing publication behavior.

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
