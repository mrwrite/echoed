## 1. Backend Governance Summary Composition

- [x] 1.1 Identify the existing publish-readiness, safe-publish, lineage-safety, competency-integrity, and runtime-intervention read helpers that will remain authoritative inputs to the unified summary.
- [x] 1.2 Add a shared backend read-model composition layer that assembles one staff-facing course governance summary payload from those existing validators without duplicating route-level orchestration.
- [x] 1.3 Define or update the staff-facing response schema so the payload exposes bounded sections, aggregate status, and structured issue context for each governance concern.
- [x] 1.4 Ensure the composition path stays deterministic and read-only, with no mutation to curriculum, publish state, progression, attempts, mastery, certification, or reporting records.
- [ ] 1.5 Add bounded batching or equivalent fan-out reduction support for multi-course staff reads and document deferred caching boundaries in the implementation notes.

## 2. Staff Dashboard Consumption

- [x] 2.1 Update the existing staff/admin/teacher governance surface to request one course governance summary payload per course instead of separate per-course governance requests where practical.
- [x] 2.2 Preserve the current publish-readiness, safe-publish, lineage, competency, and runtime sections while wiring them to the consolidated payload.
- [x] 2.3 Keep the consolidated UI read-only and avoid adding publish, rollback, grading, messaging, assignment, or intervention workflow controls.
- [x] 2.4 Confirm the frontend request pattern reflects reduced per-course governance fan-out without changing learner-facing surfaces.

## 3. Authorization and Learner-Safe Separation

- [x] 3.1 Reuse the existing staff/admin/content authorization boundary for the unified governance summary contract.
- [x] 3.2 Deny learner/student access to the unified governance summary and keep learner-facing serialization and governed delivery contracts unchanged.
- [x] 3.3 Verify the consolidated read model does not leak staff-only governance fields into learner, progress, assessment, certification, or reporting views.

## 4. Regression Verification

- [x] 4.1 Add focused backend tests for unified payload shape, section presence, staff access, learner denial, and read-only behavior.
- [x] 4.2 Add regression coverage proving summary evaluation does not mutate progression, attempts, mastery evidence, certification outputs, or reporting outputs.
- [x] 4.3 Add focused frontend or integration coverage proving existing staff governance sections render correctly from one aggregated payload.
- [x] 4.4 Verify existing individual validators still behave correctly when consumed through the shared composition layer.
- [x] 4.5 Verify request consolidation does not regress governed learner delivery, assessment compatibility, or other existing learner-safe behavior.

## Follow-Ups

- [ ] Add batching for multi-course governance summaries
- [ ] Add pagination/limits for runtime intervention recommendations inside governance summary
- [ ] Add optional lazy-loading for heavy governance sections
- [ ] Render lineage/safety visibility as its own staff UI section
- [ ] Add contract tests to protect the nested governance summary shape
- [ ] Tune backend query loading to avoid overfetch as governance sections grow