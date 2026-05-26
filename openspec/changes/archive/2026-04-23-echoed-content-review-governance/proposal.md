# EchoEd Content Review & Governance

## Why

EchoEd now supports academically structured lessons with objectives, instructional flow, sources, and review metadata. However, there are currently no enforced standards or governance rules to ensure that lessons meet a consistent level of quality, credibility, and instructional completeness before being delivered to learners.

Without governance, lessons may be incomplete, unreviewed, or inconsistent, which limits trust and reduces the platform’s legitimacy in educational settings.

## What Changes

- Define and enforce lesson readiness rules for academically complete lessons
- Introduce a clear review workflow using existing `review_status` and `reviewed_by` fields
- Restrict who can mark lessons as reviewed or approved based on user roles
- Ensure lesson visibility aligns with review status (draft vs reviewed vs approved)
- Establish minimum source requirements and support validation of lesson sources
- Clarify role-based visibility for teacher-only content (teacher_notes, discussion_questions)
- Ensure consistent behavior across lesson and course APIs regarding lesson readiness and visibility

## Capabilities

### New Capabilities
- `lesson-readiness-validation`
- `content-review-workflow`
- `role-based-content-visibility`
- `lesson-source-governance`

### Modified Capabilities
- `lesson-delivery-and-activity-system`
- `course-and-lesson-api-contracts`

## Impact

- Backend:
  - Extend validation and business rules in existing lesson routes (`backend/app/api/routes/lessons.py`)
  - Update schemas to reflect readiness and visibility rules (`backend/app/schemas.py`)
  - Potential updates to models for stricter constraints (`backend/app/models.py`)
- Frontend:
  - Adjust lesson rendering logic to respect role-based visibility (teacher vs student)
  - Handle draft/reviewed/approved lesson states appropriately in lesson viewer
- APIs:
  - Lesson and course endpoints may filter or flag lessons based on readiness/review status
- Testing:
  - Add tests for readiness validation, review permissions, and visibility behavior