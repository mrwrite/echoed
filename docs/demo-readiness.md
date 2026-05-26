# Demo Readiness Runbook

This runbook documents the deterministic EchoEd demo environment used for the flagship `Introduction to Africa` walkthrough.

Related planning document:

- [Demo UI Polish Checklist](./demo-ui-polish-checklist.md)

## Purpose

Use this flow before a live demo when you need to:

- apply schema migrations
- rebuild the canonical demo organization and users
- reset flagship learner progress and evidence into known states
- verify the expected teacher and admin story without manual repair

## Demo Setup

### 1. Apply backend migrations

From the repo root:

```powershell
cd backend
venv\Scripts\python.exe -m alembic upgrade head
```

If you are using an activated virtual environment, `python -m alembic upgrade head` is equivalent.

### 2. Reseed the deterministic demo

From the repo root:

```powershell
backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py
```

What this does:

- reuses the real `app.seed_demo.run()` entrypoint
- refreshes the canonical demo organization and memberships
- refreshes the flagship `Introduction to Africa` course structure
- reseeds the canonical section, enrollments, student-course rows, progress rows, attempts, answers, and attempt events
- restores the demo archetypes to stable runtime states

The command is safe to rerun for repeat demo preparation. It is intentionally bounded to the demo-scoped seed identities and flagship course state.

## Canonical Demo Context

- Demo organization: `EchoEd Demo School`
- Flagship course: `Introduction to Africa`
- Demo section: `Grade 3 - Cohort A`
- Shared password for seeded accounts: `password`

## Demo Accounts

### Staff accounts

- Org admin: `orgadmin` / `password`
- Teacher: `teacher` / `password`
- Content admin: `contentadmin` / `password`

### Reference student accounts

- `student1` / `password`
- `student2` / `password`

These two learners stay available as clean student accounts for baseline learner-flow demos and regression coverage.

## Flagship Learner Archetypes

The seeded archetypes are the canonical learners for the deterministic teacher/admin demo story.

- Enrichment/mastered: `masteredstudent` / `password`
  - Expected runtime recommendation: `enrichment`
  - Expected state: completed flagship course with completed unit and segment progress
- Reteach/struggling: `reteachstudent` / `password`
  - Expected runtime recommendation: `reteach`
  - Expected state: active flagship course with weak real assessment evidence
- Review/moderate: `reviewstudent` / `password`
  - Expected runtime recommendation: `review`
  - Expected state: active flagship course with mixed but coherent evidence
- Monitor/ambiguous: `monitorstudent` / `password`
  - Expected runtime recommendation: `monitor`
  - Expected state: active flagship course with ambiguous competency evidence
- Normal progression: `normalstudent` / `password`
  - Expected runtime recommendation: `normal`
  - Expected state: active flagship course with governed progress and no special intervention signal

## Expected Teacher/Admin Outcomes

After reseeding, staff-facing reads should be predictable:

- The flagship teacher runtime support view should surface a stable mix of intervention needs across the archetypes.
- The mastered learner should present as enrichment-ready.
- The reteach learner should present as needing targeted reteach support.
- The review learner should present as needing short review before continuing.
- The monitor learner should present as needing educator monitoring because the evidence is intentionally ambiguous.
- The normal learner should present as governed normal continuation.

## Staff Governance Demo Checks

Use these checks when you want to prove the flagship demo course is staff-ready from a governance perspective.

### 1. Publish readiness

- Inspect: `GET /api/courses/{course_id}/publish-readiness` or the staff publish-readiness section.
- Expected outcome: the flagship course is ready to publish.
- Expected details:
  - `is_ready = true`
  - no blocking issues
  - no warnings
- Demo users: `orgadmin`, `teacher`, or `contentadmin`
- Expected vs unexpected:
  - expected: no publish-readiness warnings
  - unexpected: missing readiness fields, draft review status, or ordering issues

### 2. Safe publish validation

- Inspect: `GET /api/courses/{course_id}/safe-publish-validation` or the staff safe-publish section.
- Expected outcome: the flagship course is safe to publish.
- Expected details:
  - `is_safe = true`
  - no blocking issues
  - no warnings
- Demo users: `orgadmin`, `teacher`, or `contentadmin`
- Expected vs unexpected:
  - expected: no safe-publish warnings
  - unexpected: blocked revision state, unsafe historical evidence, or deprecated learner-facing curriculum state

### 3. Governance summary

- Inspect: `GET /api/courses/{course_id}/governance-summary`
- Expected outcome: one staff-readable payload with all governance sections present.
- UI alignment: if you are showing the staff governance dashboard, this route is the backend summary payload that should back the existing governance sections without changing their wording.
- Expected sections:
  - `publish_readiness`
  - `safe_publish_validation`
  - `lineage_safety_visibility`
  - `competency_evidence_integrity`
  - `runtime_intervention_recommendations`
- Demo users: `orgadmin` is the simplest demo account for this check
- Expected vs unexpected:
  - expected: lineage/safety shows coherent and safe
  - unexpected: missing sections, learner access, or route-level mismatches between summary and individual reads

### 4. Competency evidence integrity

- Inspect: `GET /api/courses/{course_id}/competency-evidence-integrity`
- Expected outcome: valid but intentionally not fully explainable.
- Expected details:
  - `is_valid = true`
  - `is_explainable = false`
  - one warning on `Introduction to Africa Ambiguous Evidence Check`
  - warning code: `unaligned_assessment_mastery_evidence`
- Demo user/archetype proving the warning: `monitorstudent` / Dayo Monitor
- Expected vs unexpected:
  - expected: exactly the ambiguity warning tied to the ambiguous evidence check
  - unexpected: blocking issues, unsafe historical evidence, or unexplained warnings on the flagship aligned checks

### 5. Runtime intervention recommendations

- Inspect: `GET /api/courses/{course_id}/runtime-intervention-recommendations` or the staff runtime/intervention section.
- Expected outcome: all five learner stories are present.
- Expected learner mapping:
  - `masteredstudent` / Amara Mastery -> `enrichment`
  - `reteachstudent` / Binta Reteach -> `reteach`
  - `reviewstudent` / Chidi Review -> `review`
  - `monitorstudent` / Dayo Monitor -> `monitor`
  - `normalstudent` / Eshe Steady -> `normal`
- Expected vs unexpected:
  - expected: `monitorstudent` includes `ambiguous_competency_evidence`
  - expected: `monitorstudent` and `normalstudent` include `limited_mastery_evidence`
  - unexpected: all learners collapsing to one state, or the ambiguous evidence warning leaking onto the aligned archetypes

### 6. Learner denial

- Inspect: attempt the same governance endpoints while authenticated as `student1` or `student2`
- Expected outcome: learners are denied from staff governance reads.
- Expected details:
  - `403` for publish readiness
  - `403` for safe publish validation
  - `403` for competency evidence integrity
  - `403` for governance summary
  - `403` for runtime intervention recommendations

## Recommended Live Demo Path

1. Run migrations.
2. Run `backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py`.
3. Sign in as `teacher` and open the flagship course.
4. Show the learner mix through the deterministic runtime/intervention story:
   - `masteredstudent`
   - `reteachstudent`
   - `reviewstudent`
   - `monitorstudent`
   - `normalstudent`
5. Sign in as `orgadmin` if you need the staff/admin view of the same flagship environment.
6. Use `student1` or `student2` for a clean learner-flow walkthrough when you do not want preseeded attempt history.

## Verification Checklist

Use this as a quick operator check after reseeding:

- The command exits successfully.
- The output references `EchoEd Demo School`.
- The output lists `orgadmin`, `teacher`, and the five archetype learners.
- The flagship course remains `Introduction to Africa`.
- The teacher dashboard can discover the archetype learners without manual enrollment repair.
- The governance summary route returns all expected sections for the flagship course.
- Publish readiness and safe publish validation are clean for the flagship course.
- Runtime intervention recommendations show enrichment, reteach, review, monitor, and normal at the same time.
- Competency evidence integrity shows the expected ambiguous warning for `monitorstudent` and no blocking issues.

## Final Operator Validation Checklist

Use this when you need a stricter go or no-go check immediately before a live demo.

- Run migrations and rerun `backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py` without manual database cleanup.
- Confirm the reseed output completes successfully and still names `EchoEd Demo School` and `Introduction to Africa`.
- Sign in as `normalstudent` and confirm the flagship course starts on a governed lesson with normal continuation guidance.
- Sign in as `teacher` and confirm the runtime intervention recommendation mix includes:
  - `Amara Mastery` -> `enrichment`
  - `Binta Reteach` -> `reteach`
  - `Chidi Review` -> `review`
  - `Dayo Monitor` -> `monitor`
  - `Eshe Steady` -> `normal`
- Sign in as `teacher` and confirm the educator runtime support view remains stable:
  - `Amara Mastery` shows `completed` support with `celebrate-and-reflect`
  - `Binta Reteach` shows `remediation` support with `review-and-continue`
  - `Chidi Review` shows `remediation` support with `review-and-continue`
  - `Dayo Monitor` and `Eshe Steady` remain in normal continuation support
- Sign in as `orgadmin` and confirm `GET /api/courses/{course_id}/governance-summary` returns:
  - `publish_readiness`
  - `safe_publish_validation`
  - `lineage_safety_visibility`
  - `competency_evidence_integrity`
  - `runtime_intervention_recommendations`
- Confirm publish readiness is clean, safe publish validation is clean, and lineage safety remains coherent and safe.
- Confirm learner access is still denied from the staff governance endpoints.
- Treat any need for manual row cleanup, manual reenrollment, or manual attempt deletion as a demo-readiness failure.

## Known Acceptable Demo Warnings

One governance warning is intentionally acceptable in the flagship demo:

- Surface: `competency_evidence_integrity`
- Warning code: `unaligned_assessment_mastery_evidence`
- Assessment: `Introduction to Africa Ambiguous Evidence Check`
- Demonstrated by: `monitorstudent` / Dayo Monitor
- Why it is acceptable:
  - the course remains valid and safe
  - the warning is deterministic across reseeds
  - it demonstrates realistic staff governance ambiguity rather than data corruption
  - it should appear without any blocking issues

Unexpected warnings for the flagship demo include:

- additional competency evidence integrity warnings
- any blocking governance issue
- publish readiness warnings
- safe publish warnings
- lineage safety warnings

## Recovery Steps If Reseed Validation Fails

1. Rerun migrations from `backend` with `venv\Scripts\python.exe -m alembic upgrade head`.
2. Rerun `backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py`.
3. Confirm the reseed summary still names `EchoEd Demo School`, `Introduction to Africa`, `orgadmin`, `teacher`, and the five archetype learners.
4. Recheck the flagship student flow with `normalstudent`.
5. Recheck the teacher runtime recommendation mix and the `orgadmin` governance summary.
6. If learner access is no longer denied, or if the acceptable ambiguity warning becomes blocking, stop the demo prep and treat the environment as invalid.
7. If stale auth or session data appears to be masking the expected state, sign out, start a new session, and repeat the validation checks before changing any data manually.

## Guardrails

- No frontend UI changes are required for demo preparation.
- No auth bypass is used.
- No fake scoring is used.
- No special-case runtime logic is required in the demo path.
- No workflow expansion is part of this setup path.
