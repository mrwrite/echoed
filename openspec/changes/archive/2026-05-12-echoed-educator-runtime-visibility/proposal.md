## Why

EchoEd now has bounded runtime remediation, enrichment, and confidence-support guidance for learners, but educators still lack a lightweight way to see which learners need review, which learners are ready for extension, and which learners are progressing normally. This change adds that visibility on top of existing governed delivery and assessment/mastery evidence without turning EchoEd into a heavy analytics or intervention workflow product.

## What Changes

- Add additive educator-visible runtime support summaries derived from existing continuation guidance, assessment evidence, and mastery signals.
- Surface learner runtime support state on existing teacher/admin dashboard and reporting surfaces using current premium UX primitives.
- Expose read-only educator attention context, pacing hints, remediation/enrichment references, and confidence-support signals for the flagship pathway.
- Preserve learner-safe field separation so educator-only hints do not leak into learner-facing contracts.
- Preserve governed progression, assessment scoring, certification behavior, and existing teacher/admin route boundaries.

## Capabilities

### New Capabilities
- `educator-runtime-support-visibility`: Lightweight educator visibility into learner remediation, enrichment, normal continuation, and confidence-support state.
- `educator-runtime-support-surface-integration`: Bounded integration of runtime support visibility into existing educator dashboard and reporting surfaces.
- `educator-read-only-intervention-awareness`: Read-only educator attention context, pacing hints, and support guidance without workflow automation.
- `flagship-runtime-support-visibility`: Initial educator runtime support visibility scoped to the flagship Introduction to Africa pathway and existing runtime support metadata.
- `educator-runtime-support-ux`: Premium UX state treatment for educator-facing runtime support summaries, including loading, empty, error, retry, and support-state rendering.
- `educator-runtime-support-technical-alignment`: Architectural constraints that keep educator runtime support additive to governed delivery, assessment/mastery, auth/session, and existing dashboard boundaries.
- `educator-runtime-support-verification`: Regression expectations for educator visibility, read-only behavior, learner-safe separation, and compatibility preservation.

### Modified Capabilities

- None.

## Impact

- Affected code will likely include existing analytics/reporting read models, teacher/admin dashboard components, frontend educator summary cards/tables, and focused backend/frontend tests.
- No new intervention workflow engine, grading workflow, parent portal, or route structure is required.
- No new progression or mastery system is introduced; educator runtime support remains read-only and derived from existing evidence.
