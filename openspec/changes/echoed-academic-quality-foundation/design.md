# Design: EchoEd Academic Quality Foundation

## Context

EchoEd already has a working course, unit, lesson, activity, progress, source, and content-governance foundation. Recent work added academic lesson-quality fields, lesson sources, review metadata, readiness metadata, and governance rules for approved-ready student content.

This change defines the academic-quality standards that sit above those features so EchoEd courses feel legitimate, classroom-ready, and source-backed.

## Goals

- Standardize what a high-quality EchoEd lesson must contain
- Preserve the current Course → Unit → Lesson → Activity structure
- Ensure lessons support classroom-style instruction
- Make sources and citations part of the curriculum experience
- Keep student views focused and teacher views instructionally useful
- Avoid duplicating lesson, source, progress, or governance systems

## Non-Goals

- Creating a new curriculum engine
- Replacing existing lesson/progress/governance logic
- Building a reviewer workbench UI in this change
- Adding external accreditation integrations

## Academic Lesson Standard

A strong EchoEd lesson should include:

- learning objectives
- key concepts
- hook
- content
- guided practice
- independent practice
- assessment/check for understanding
- teacher notes
- discussion questions
- at least one reliable source
- review/readiness metadata

## Instructional Design Standard

Lessons should follow a classroom-style flow:

1. Engage the learner with a hook
2. Teach the core concept
3. Guide practice with support
4. Allow independent practice
5. Check understanding through assessment or reflection

## Source-Backed Curriculum Standard

Lesson content should be traceable to reliable sources.

Sources should support:
- citation text
- URL when available
- source type when available
- relationship to lesson content

Future work may classify sources by type, such as:
- primary source
- scholarly source
- museum/archive
- reputable educational publisher
- video/media

## Educator Guidance Standard

Teacher-facing lesson views should expose:
- teacher notes
- discussion questions
- readiness/review context where useful

Student-facing views should remain simple and should not expose teacher-only guidance.

## Backend Strategy

Reuse the existing backend files and systems:

- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/lesson_governance.py`
- `backend/app/api/routes/lessons.py`
- `backend/app/api/routes/courses.py`

Do not create duplicate lesson, source, progress, or governance systems.

## Frontend Strategy

Reuse the existing Angular lesson viewer and course/lesson flows.

Relevant frontend areas include:
- `frontend/src/app/models/lesson.ts`
- `frontend/src/app/shared/lesson-viewer.component.ts`
- `frontend/src/app/shared/lesson-viewer.component.html`

Student views should prioritize clarity and learning flow.
Teacher views should expose instructional supports.

## Risks / Trade-offs

- Existing lessons may not yet meet the full academic-quality standard
- Too much metadata in student views could make lessons feel cluttered
- Duplicating governance/readiness logic outside `lesson_governance.py` could cause drift
- Course-level quality may need a future change after lesson-level standards are stable

## Mitigations

- Treat this change as standardization and alignment, not a broad rewrite
- Reuse existing governance and readiness metadata
- Keep student presentation clean
- Keep teacher-only guidance role-gated
- Add tests only where behavior changes