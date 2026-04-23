# Design: Certified Platform Foundation

## Context

EchoEd already includes:
- Course → Unit → Lesson → Activity structure
- Progress tracking (`StudentCourse`, `StudentUnitProgress`, `SegmentProgress`)
- Organization and role-based access
- Lesson sessions and start-course flows
- Badge system

However, it lacks:
- Program-level structure
- Assessment and scoring system
- Certification logic
- Standards-based curriculum alignment
- Consistent UX for onboarding and trust

---

## Goals

- Enable structured learning paths (Programs)
- Enable measurable outcomes through assessments
- Award certifications based on completion and performance
- Align curriculum with objectives and standards
- Improve UX for clarity, trust, and accessibility

---

## Non-Goals

- Rewriting existing auth or org systems
- Replacing current curriculum structure
- Building external accreditation integrations (future phase)

---

## Architecture Overview

### Programs Layer

Add:
- `Program`
- `ProgramCourse`
- `StudentProgramProgress`

Programs group courses into certification tracks.

---

### Assessment Layer

Add:
- `Assessment`
- `Question`
- `StudentAssessmentAttempt`

Assessments can be tied to:
- lessons
- courses
- programs

---

### Certification Layer

Add:
- `Certification`
- `CertificationRequirement`
- `StudentCertification`

Certification is granted when:
- required courses are completed
- required assessments are passed

---

### Curriculum Alignment

Extend existing models to include:
- learning objectives
- skill tags
- standard alignment metadata

---

## Backend Design

### Must Reuse Existing Systems

Use:
- `models.py`
- `schemas.py`
- `progress.py`
- `start_course.py`
- `lesson_sessions.py`

Do NOT:
- duplicate progress tracking
- duplicate lesson flow logic
- create parallel curriculum models

---

## Frontend Design

### New Views
- Program dashboard
- Assessment interface
- Certification results page

### Reuse
- existing dashboard
- existing lesson flow
- existing shell/layout

---

## UX Design Principles

- Clear progression (Program → Course → Lesson → Assessment)
- Strong readability (no low-contrast text)
- Stable layout (no sidenav overlap)
- Cultural identity reflected in design system

---

## Repo Constraints

Frontend:
- `frontend/src`

Backend:
- `backend/app`

Existing routes:
- `auth.py`
- `orgs.py`
- `courses.py`
- `lessons.py`
- `progress.py`
- `start_course.py`
- `lesson_sessions.py`

Do NOT create duplicate systems.

---

## Risks

- Overlapping with existing progress logic
- UI complexity increase
- Curriculum inconsistency

---

## Mitigation

- Extend existing models, do not duplicate
- Introduce features incrementally
- Validate curriculum structure before scaling