# Course authoring operations guide

## Role policy

The backend capability response is the source of truth; the UI never grants an action from a claimed client role.

| Role and scope | Author | Review | Publish |
| --- | --- | --- | --- |
| Active organization content admin | Create, edit, duplicate, preview, submit | No | No |
| Active organization admin | Create, edit, duplicate, preview, submit | Yes, except own course | Yes, except own course |
| Active teacher or instructor | Duplicate approved/published content; edit and submit owned derivatives | No | No |
| Platform admin or super admin | Full cross-organization oversight | Yes | Yes |
| Learner or inactive/out-of-scope member | No authoring capabilities | No | No |

## Creator workflow

1. Open Product Studio → Courses and choose a blank course or internal template.
2. Complete Setup, then build the ordered unit, lesson, activity, and source outline in Build.
3. Watch the live save status. Quality combines immediate authoring prompts with the canonical governance summary.
4. Use Preview to request the learner-safe server projection. Preview does not change learner availability.
5. Fix blocking issues, save, and submit for review. A different authorized reviewer records approval or requests changes with feedback.
6. An authorized publisher publishes only an approved version that passes safe-publish validation. Later edits return the working copy to draft while the published snapshot remains recorded on the published version metadata.

## Save and recovery behavior

- Draft creation uses an idempotency key, so a safe retry cannot create two courses.
- Changes autosave after a short pause and writes are serialized. `Save now` uses the same path.
- The editor retains local input after offline or server failure and exposes Retry.
- Every update includes the last server revision. A stale revision produces a conflict without overwriting either copy; creators can reload the server copy or save local work as a recovered course.
- Browser close/reload warnings appear only while local changes are not durable. Saved drafts resume from their canonical URL.

## Accessibility and responsive verification checklist

Automation covers component rendering, status messages, debounce behavior, production compilation, and service contracts. Before general release, verify the following on desktop, tablet, and a 320-pixel mobile viewport:

- Complete Setup, Build, Quality, Preview, and Release using only the keyboard.
- Confirm heading order and landmark names in a screen-reader rotor.
- Confirm every input announces its label and supporting help, save and lifecycle changes announce once, and blocking issues move focus to the affected editor.
- Reorder units, lessons, and activities with Move up/Move down; confirm visual order and reading order agree.
- Confirm visible focus, 44-pixel primary targets, reflow without horizontal page scrolling, and no information conveyed by color alone.
- Trigger offline, failed save, and revision conflict states; confirm local text remains available and recovery actions are understandable.

## Interoperability limits

The first release exports the lossless `echoed-json-v1` aggregate and validates an EchoEd JSON document before any future import persistence. Adapter boundaries report every blocking or unsupported construct. Common Cartridge and QTI execution are intentionally deferred; do not represent those formats as supported in product copy.

## Rollout and rollback

Canonical navigation is controlled by `courseAuthoringStudioEnabled` in Angular environments. Pilot with authorized organization content admins and an independent org admin reviewer. Monitor failed saves, revision conflicts, validation failures, publish blocks, payload size, and save latency.

To roll back navigation, set the flag to `false` and redeploy the frontend. Existing legacy endpoints remain compatibility adapters over the canonical aggregate service, so durable drafts remain readable. Do not delete course/version data during rollback. Re-enable only after the defect is corrected and focused authorization, draft, learner-safety, frontend, build, and browser smoke checks pass.

## Pilot performance baseline

The local integration benchmark persists and revises a representative 20-unit graph with 100 lessons and 300 activities. The combined create/update test completed in 0.67 seconds on the development SQLite environment; each operation is bounded at 5 seconds and each aggregate response at 1.5 MB. Production rollout should capture p50/p95 network and database latency against the same shape before widening the flag.
