# EchoEd Academic Quality Foundation

## Why

EchoEd is becoming more than a content platform. To be respected by educators, schools, families, and organizations, its courses must be academically credible, instructionally structured, and backed by reliable sources.

The platform now has lesson-quality fields and content governance, but the broader academic-quality foundation still needs to define how courses, units, lessons, sources, reviews, and classroom-style instruction work together consistently.

## What Changes

- Standardize lesson structure around classroom-quality instructional design
- Ensure lessons include clear objectives, key concepts, instructional flow, teacher guidance, and sources
- Define how source-backed content should be represented across lessons and courses
- Establish expectations for reliable sources, citations, and review metadata
- Align course and lesson presentation with a legitimate classroom-style learning experience
- Preserve existing EchoEd course, unit, lesson, progress, and governance systems

## Capabilities

### New Capabilities
- `academic-lesson-structure`
- `source-backed-curriculum`
- `instructional-design-standards`
- `educator-guidance-layer`

### Modified Capabilities
- `lesson-delivery-and-activity-system`
- `course-and-lesson-api-contracts`
- `content-review-and-governance`

## Impact

- Backend:
  - Existing lesson, course, source, and governance models/APIs may need documentation, refinement, or validation alignment
  - No duplicate curriculum or lesson systems should be introduced

- Frontend:
  - Lesson viewer and course presentation should clearly expose academic-quality metadata where appropriate
  - Student-facing views should remain simple and focused
  - Teacher-facing views should expose instructional guidance

- Curriculum:
  - Courses and lessons should follow consistent academic-quality expectations
  - Sources and review metadata should support trust and legitimacy

- Testing:
  - Add or update tests only where behavior changes
  - Preserve existing lesson, course, progress, and governance behavior
