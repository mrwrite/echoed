## Why

EchoEd now has historical curriculum lineage metadata and read-only safety validation, but authorized staff still lack a bounded way to inspect those results operationally. This change is needed now so staff/admin users can review lineage coherence, learner-progress safety, and assessment-evidence safety in the same governance surfaces they already use, without exposing historical warnings to learners or expanding into workflow orchestration.

## What Changes

- Add a staff-only, read-only backend contract that exposes course-level lineage and safety status using existing lineage coherence, learner-progress safety, assessment-evidence safety, and safe-publish validation helpers.
- Expose structured blocking issues and warnings for affected entities, including entity type, identifier, title, and assessment-evidence or learner-progress risk context.
- Add bounded staff-facing UI visibility for lineage and safety results beside existing publish-readiness and safe-publish sections.
- Keep learner/student serialization and governed delivery unchanged, with no staff lineage warnings or historical controls shown in learner-facing surfaces.
- Preserve the existing `Course`/`Unit`/`Lesson`/`Assessment` model family, safe-publish validators, auth/session patterns, governed delivery behavior, and assessment/mastery architecture.
- Add focused regression coverage for staff access, learner denial, read-only behavior, staff UI rendering, learner non-exposure, and compatibility with current reporting, certification, and governed delivery behavior.

## Capabilities

### New Capabilities
- `staff-lineage-safety-surface-integration`: Bounded staff-facing UI expectations for lineage and safety visibility beside existing governance sections.

### Modified Capabilities
- `staff-lineage-safety-visibility`: Extend read-only staff lineage visibility into an explicit aggregated backend contract with structured issues and safety summaries.
- `historical-lineage-technical-alignment`: Extend historical-lineage technical constraints to cover staff-only backend contracts and governance UI integration without route redesign or workflow expansion.
- `historical-lineage-safety-verification`: Extend regression requirements to cover staff access, learner denial, read-only behavior, staff rendering, and learner non-exposure.
- `versioning-ux-and-governance-boundaries`: Extend bounded governance UX expectations so lineage and historical-safety warnings appear alongside publish-readiness and safe-publish concerns without becoming a full authoring suite.

## Impact

Affected areas include backend staff/admin read-only governance endpoints, frontend staff governance/course-management UI, role-based access checks, lineage and safety validation aggregation, and focused regression coverage for learner-safe separation, reporting compatibility, assessment evidence interpretation, and governed learner delivery stability.
