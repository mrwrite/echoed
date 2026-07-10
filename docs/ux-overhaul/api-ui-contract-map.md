# API to UI Contract Map

Evidence: `frontend/src/app/services/*.ts`, `backend/app/api/routes/*.py`.

## Auth and Session

| UI/service | API | Method | Backend file | Roles | UX contract |
| --- | --- | --- | --- | --- | --- |
| `AuthService.login()` | `/api/auth/token` | POST | `routes/auth.py` | Public | Returns JWT, user, org context. Login must wait for permission bootstrap before navigation. |
| `AuthService.register()` | `/api/auth/register` | POST | `routes/auth.py` | Public | Creates account. Registration must not create parallel org flow. |
| `OrganizationService.refreshOrganizations()` | `/api/orgs` | GET | `routes/orgs.py` | Auth | Drives active org switcher and onboarding requirement. |
| `OrganizationService.createOrganization()` | `/api/orgs` | POST | `routes/orgs.py` | Auth | Creates org and org_admin membership. |
| `OrganizationService.switchOrganization()` | `/api/orgs/{id}/switch` | POST | `routes/orgs.py` | Member | Returns refreshed token/org context. UI must not optimistically switch. |
| `MetaService.getEnums()` | `/api/enums` | GET | `routes/meta.py` | Public | Drives registration role/org options. |

## Learning Runtime

| UI/service | API | Method | Backend file | Roles | UX contract |
| --- | --- | --- | --- | --- | --- |
| `CoursesService.getCourses()` | `/api/courses` | GET | `routes/courses.py` | admin, teacher, student | Course catalog. Student view must hide staff-only fields via backend serializer. |
| `CoursesService.getCourseById()` | `/api/courses/{id}` | GET | `routes/courses.py` | admin, teacher, student | Course overview and lesson preview. |
| `CoursesService.getStudentCourses()` | `/api/student-courses` | GET | `routes/courses.py` | student | Enrolled learning list and continuation guidance. |
| `CoursesService.enrollInCourse()` | `/api/enroll` | POST | `routes/enroll.py` | student | Self-enrollment; use success/error toast and avoid duplicate enrollment confusion. |
| `CoursesService.assignCourseToStudent()` | `/api/assign-course` | POST | `routes/enroll.py` | admin, teacher | Teacher assignment workflow. |
| `CoursesService.startCourse()` | `/api/start-course` | POST | `routes/start_course.py` | student | Returns governed segment state; UI must handle unavailable/pending/completed. |
| `CoursesService.getCurrentSegment()` | `/api/progress/segment` | GET | `routes/progress.py` | admin, teacher, student | Restores current governed lesson. |
| `CoursesService.markSegmentCompleted()` | `/api/progress/segment/complete` | POST | `routes/progress.py` | admin, teacher, student | Advances progress; UI must preserve recovery from stale segment IDs. |
| `CoursesService.getLessonById()` | `/api/lessons/{id}` | GET | `routes/lessons.py` | admin, teacher, student | Student receives governed learner lesson; staff receive teacher notes. |

## Curriculum and Authoring

| UI/service | API | Method | Backend file | Roles | UX contract |
| --- | --- | --- | --- | --- | --- |
| Course wizard | `/api/courses` | POST/PUT/DELETE | `routes/courses.py` | admin, teacher | Course create/edit/delete. Add confirmation and governance visibility. |
| Studio courses | `/api/courses/authoring` | POST | `routes/courses.py` | org content roles | Course authoring shell. |
| Course versions | `/api/courses/{id}/versions`, `/api/course-versions/{id}` | POST/PUT | `routes/courses.py` | content_admin, org_admin | Version workflow. |
| Publish version | `/api/course-versions/{id}/publish` | POST | `routes/courses.py` | content_admin, org_admin | Requires readiness/safe-publish context. |
| Units | `/api/units`, `/api/course-versions/{id}/units` | CRUD | `routes/units.py` | admin, teacher | Course structure editing. |
| Lessons | `/api/lessons` | CRUD | `routes/lessons.py` | admin, teacher | Lesson editing; staff fields visible only staff. |
| Uploads | `/api/upload/coloring`, `/api/upload/storybook`, `/api/upload/badge` | POST | `routes/uploads.py` | admin/teacher/admin badge | Asset upload. Storybook image URLs must use backend public URL in deployed environments. |

## Assessment and Credentials

| UI/service | API | Method | Backend file | Roles | UX contract |
| --- | --- | --- | --- | --- | --- |
| `ProgramsService.getPrograms()` | `/api/programs` | GET | `routes/programs.py` | Auth roles | Pathway list with student-specific progress. |
| Program enroll | `/api/programs/{id}/enroll` | POST | `routes/programs.py` | student | Adds pathway/courses. |
| Assessment detail | `/api/assessments/{id}` | GET | `routes/assessments.py` | Auth | Student form or staff preview. |
| Submit attempt | `/api/assessments/{id}/attempts` | POST | `routes/assessments.py` | student | Needs submit pending/failure and completion state. |
| Certifications | `/api/certifications`, `/api/students/me/certifications` | GET/POST | `routes/certifications.py` | staff/student | Separate learner credential display from staff management. |

## Classroom and Organization

| UI/service | API | Method | Backend file | Roles | UX contract |
| --- | --- | --- | --- | --- | --- |
| `SectionsService.getSections()` | `/api/sections` | GET | `routes/sections.py` | teacher, org_admin, instructor | Teacher class list. |
| Section roster | `/api/sections/{id}/roster` | GET | `routes/sections.py` | teacher, org_admin, instructor | Class detail roster. |
| Add enrollment | `/api/sections/{id}/enrollments` | POST | `routes/sections.py` | teacher, org_admin, instructor | Enroll learner. |
| Assignments | `/api/sections/{id}/assignments` | GET/POST | `routes/assignments.py` | teacher/org roles | Assignment workflow. |
| Submit assignment | `/api/assignments/{id}/submit` | POST | `routes/assignments.py` | student | Student work submission; no complete UI found. |
| Invites | `/api/orgs/{id}/invites`, `/api/invites/accept` | GET/POST | `routes/invites.py` | org_admin/content_admin for invites | Invite management and acceptance. |

## Analytics and Governance

| UI/service | API | Method | Backend file | Roles | UX contract |
| --- | --- | --- | --- | --- | --- |
| Admin overview | `/api/analytics/overview` | GET | `routes/analytics.py` | staff/admin | Admin dashboard metrics. |
| Teacher summary | `/api/analytics/teacher-summary` | GET | `routes/analytics.py` | teacher/admin | Classroom progress table/list. |
| Student progress | `/api/analytics/student-progress` | GET | `routes/analytics.py` | student | Learner dashboard metrics. |
| Educator support | `/api/analytics/...` runtime support | GET | `routes/analytics.py` | educator roles | Reteach/review/enrichment recommendation visibility. |
| Governance summary | `/api/courses/{id}/governance-summary` | GET | `routes/courses.py` | staff | Aggregates publish readiness, safe-publish, competency integrity, runtime interventions. |

## V2 Workspace

| UI/service | API | Method | Backend file | Roles | UX contract |
| --- | --- | --- | --- | --- | --- |
| Workspaces | `/api/workspaces` | GET | `routes/v2_platform.py` | creator roles | Workspace selection/status. |
| Projects | `/api/projects` | GET/POST | `routes/v2_platform.py` | creator roles | Project shell creation/list/detail. |
| Products | `/api/products` | GET/POST/PATCH | `routes/v2_platform.py` | creator roles | Product wrapper over course/content. |
| Public products | `/api/public/products` | GET | `routes/v2_platform.py` | Public | Public catalog/detail. |
| Learner portal products | `/api/learner-portal/products` | GET | `routes/v2_platform.py` | student/auth | Learner product catalog. |
| Knowledge sources | `/api/knowledge-sources` | GET/POST | `routes/v2_platform.py` | creator roles | Source metadata shell. |
| Artifacts | `/api/artifacts` | GET/POST | `routes/v2_platform.py` | creator roles | Artifact metadata shell. |
| Review center | `/api/review-center` | GET | `routes/v2_platform.py` | creator roles | Review queue. |
| Review status | `/api/artifacts/{id}/review-status`, `/api/products/{id}/review-status` | PATCH | `routes/v2_platform.py` | creator roles | Content review state changes. |
| Access grants | `/api/access-grants` | GET/POST/PATCH revoke | `routes/v2_platform.py` | creator roles | Access management. Avoid payment/commercial assumptions. |

## Backend Change Classification

Required for design implementation: none verified during design phase.

Potential optional backend additions:

- Context-aware current-user route to return resolved roles, active org, and default landing target in one call. Optional because current token + `/api/orgs` supports it.
- Parent/family child-progress endpoints if parent portal is implemented. Required only for future parent role.
- Search endpoints for public products/courses if client-side filtering becomes insufficient. Optional initially.
