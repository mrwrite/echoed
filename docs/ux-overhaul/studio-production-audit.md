# Content Studio Production Audit

Date: 2026-07-13

## Scope and conclusion

The verified `content_admin` production surface is the organization-scoped V2 content-operations model: workspaces, projects, product wrappers, knowledge-source wrappers, artifacts, review state, wrapper publishing, and read-only V2 analytics. The legacy curriculum CRUD surface is not a coherent `content_admin` capability: course list/detail, units, lessons, activities, assessments, and uploads authorize `admin` and/or `teacher`, while the isolated course-authoring/version endpoints use organization roles but do not provide a safe complete editor contract.

Phase 5 therefore migrates supported V2 content work into the visible **Studio** area and documents legacy curriculum authoring as a backend gap. It does not grant `content_admin` teacher or platform-admin capabilities.

## Role and authorization findings

| Finding | Code evidence | Production decision |
| --- | --- | --- |
| V2 records are scoped through visible workspace IDs derived from active organization membership. | `v2_platform.py::_visible_workspace_ids`, `_scope_platform_query` | Preserve backend scoping and do not infer broader visibility in the UI. |
| V2 create/review/publish mutations call workspace-management checks. | `_require_manage_workspace`, `_require_manage_platform_record` | Expose only these verified mutations with confirmed API states. |
| `/workspace/**` is broadly exposed to `admin`, `teacher`, `content_admin`, `org_admin`, and `instructor`. | `creatorRoles` in `app.routes.ts` | Keep legacy routes, but canonical `/studio/**` is guarded to `content_admin` only in this phase. |
| `/home/studio/courses` is guarded to `content_admin`/`org_admin`, but calls `GET /api/courses`, which rejects both roles. | `StudioCoursesComponent`; `courses.py::get_courses` | Do not migrate this broken screen into canonical Studio. |
| `/workspace/product-studio/courses/new` and edit are guarded to `admin`/`teacher`, not `content_admin`. | `app.routes.ts` | Treat as legacy teacher/admin course authoring, not Studio. |
| Course authoring/version endpoints accept organization content roles, but list/detail, nested CRUD, and ownership checks are inconsistent. | `/courses/authoring`, course-version endpoints, course/unit/lesson/activity routes | Document as incomplete and do not assemble a frontend-only authoring workflow. |
| Program creation, assessment creation, unit/lesson/activity CRUD, and coloring/storybook uploads reject `content_admin`. | `programs.py`, `assessments.py`, `units.py`, `lessons.py`, `activities.py`, `uploads.py` | No create/edit/upload controls in canonical Studio. |
| Review-center wrapper decisions and product publishing are real mutations. | V2 review-status and publish endpoints | Use accurate wrapper terminology and confirmation for high-impact state changes. |

## Route and screen audit

| Current route or screen | User goal | Authorized roles | APIs | Visible term / backend entity | Actions and capability | Review/publishing behavior | Main risks | Migration and ownership |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/workspace` | Understand content operations | Broad creator roles | `GET /api/analytics/workspace`, `GET /api/review-center` | Workspace command center / V2 workspace summaries | Read | Shows wrapper review/publishing counts | Generic product/AI language; all-or-nothing loading; oversized headings; weak mobile priority | Canonical `/studio`; belongs in Studio for `content_admin`. |
| `/workspace/projects` | Browse curriculum projects | Broad creator roles | `GET /api/projects` | Project knowledge pipeline / `Project` | Read | Project status only | Internal pipeline copy; generic collection states | Alias from `/studio/projects`; Studio. |
| `/workspace/projects/:projectId` | Organize sources and draft outputs | Broad creator roles | Project detail plus project products, sources, artifacts, generation runs; POST source/artifact | Knowledge pipeline / `Project`, `KnowledgeSource`, `Artifact` | Read/write source and artifact shells | New artifacts default to review-required | Raw relationship IDs; missing error/loading; shell terminology; no destructive actions | Canonical `/studio/projects/:projectId`; Studio. |
| `/workspace/product-studio` and `/create` | Create project and product wrappers | Broad creator roles | Workspaces, projects, products, `GET /api/courses`, POST project/product | Product Studio / V2 wrappers | Project/product create; attempted runtime-course link | Creates draft wrappers only | `GET /api/courses` fails for content admin; commercial/product language; unsupported AI emphasis; no failure state | Canonical `/studio/create`; remove unusable course selector for content admin; Studio. |
| `/workspace/product-studio/courses` | Manage courses | `content_admin`, `org_admin` in frontend | `GET/POST /api/courses` | Product drafts / `Course` | Screen claims list/create | No real state mapping | Both requests are backend-incompatible for these global roles; unlabeled inputs; fake Draft label | Do not migrate. Legacy broken route retained and documented. |
| `/workspace/product-studio/courses/new` and `/:courseId/edit` | Author full curriculum | `admin`, `teacher` | Legacy course CRUD with nested units/lessons/activities | Course wizard / `CourseDto` | Create/update full graph | Lesson governance resolved during save | Not available to content admin; destructive graph replacement on update; weak save recovery | Remains legacy teacher/admin authoring; not Studio. |
| `/workspace/products` | Browse packaged learning offerings | Broad creator roles | `GET /api/products` | Product catalog / `Product` wrapper | Read | Displays wrapper state | Commercial/internal terminology and generic collection component | Canonical `/studio/content`; visible terms depend on wrapper type; Studio. |
| `/workspace/products/:productId` | Inspect and publish a wrapper | Broad creator roles | GET product, PATCH publish | Product shell / `Product` | Read and publish public | Publish sets status `published`, may set review `approved`, and creates public visibility; does not publish lessons | No confirmation or error announcement; public consequence understated | Canonical `/studio/content/:productId`; Studio with confirmation. |
| `/workspace/knowledge-sources` | Browse source records | Broad creator roles | `GET /api/knowledge-sources` | Knowledge sources / `KnowledgeSource` wrapper | Read | Source status only | No search/filter/detail; generic collection; limited bibliographic fields | Canonical `/studio/sources`; Studio. Creation stays project-scoped. |
| `/workspace/artifacts` | Browse draft content outputs | Broad creator roles | `GET /api/artifacts` | Artifacts / `Artifact` | Read | Shows status and review state | “Artifact” is too generic; no state handling | Canonical `/studio/drafts`; visible “Content drafts”; Studio. |
| `/workspace/artifacts/:artifactId` | Inspect a draft output and traceability | Broad creator roles | `GET /api/artifacts/{id}` | Artifact registry / `Artifact` | Read | Read-only; decisions occur in review | Raw related IDs; no loading/error state; hover decoration | Canonical `/studio/drafts/:artifactId`; Studio. |
| `/workspace/review-center` | Review wrappers, drafts, and lesson readiness | Broad creator roles | GET review center; PATCH artifact/product review status | Review Center / composed queue | Read/write wrapper status | Supports artifact `draft`, `in_review`, `approved`, `rejected`, `needs_changes`; product `draft`, `in_review`, `approved`, `published`, `archived` | Immediate high-impact mutations; no confirmation, pending, success, or failure states; placeholder activity is not an audit log | Canonical `/studio/review`; Studio after safety migration. |
| `/workspace/product-studio/generation-runs*` | Inspect generation metadata | Broad creator roles | GET generation runs/detail | AI generation attempts / `GenerationRun` | Read only | None | No execution exists; prompts/errors may be sensitive; distracts from curriculum work | Keep legacy; omit canonical primary navigation. |
| `/workspace/access` | Manage learner access grants | Broad creator roles | Access-grant GET/POST/revoke | Access / `AccessGrant` | Read/write/revoke | Separate from content publishing | Belongs to Organization/access administration; personal identifiers; consequential revoke | Keep legacy; do not redesign in Studio. |
| `/workspace/analytics` | Inspect V2 operational metrics | Broad creator roles | Four V2 analytics endpoints | Product intelligence / aggregate wrappers/runtime | Read | Review/publishing counts | Includes learner engagement outside content-admin primary need; all-or-nothing loading | Keep legacy; Studio overview uses only content-operation summary fields. |
| `/workspace/commercial` | View community wrapper area | Broad creator roles | V2/public wrapper APIs | Community (route remains commercial) | Read | Varies | Not Content Studio | Community ownership; unchanged. |
| `/workspace/demo-readiness` | Run seeded demo walkthrough | Broad creator roles | Multiple demo APIs | Demo guide | Read/test actions | Demo-specific | Not production Studio IA | Keep legacy demo route. |
| `/workspace/settings`, `/settings/invites` | Preferences or org invitations | Broad creator / org roles | Preferences/invites | Settings/invitations | Read/write | None | Organization self-service, not Studio | Unchanged; Organization ownership. |
| `/workspace/learners/**` | Learner/class/access work | Broad creator plus nested guards | Course/program/section/user APIs | Learners | Mixed | None | Mixes Teacher, Admin, and Organization responsibilities | Unchanged and omitted from Studio. |
| `/workspace/lesson/:id` | Open learner lesson runtime | No child role guard beyond workspace | Lesson/progress APIs | Lesson view / runtime | Runtime behavior | Governed progress may be invoked | Preview could create or depend on learner progress; unauthorized content-admin API | Do not use for Studio preview. |

## Data sensitivity

- Workspace, project, product, source, and artifact queries must remain constrained by the backend’s active organization membership scope.
- Artifact bodies, source URIs/citations, generation prompts, and error messages can contain unpublished or sensitive content; lists should show only task-relevant summaries.
- Learner analytics and access grants are not required for primary Studio work and are omitted from canonical Studio navigation.
- Public publishing is consequential because it changes wrapper visibility. It does not override lesson governance, create enrollment, or publish runtime lessons.
- Review-center activity currently returns a placeholder message, not attributable audit history. The UI must not describe it as an audit log.

## Loading, empty, error, accessibility, and responsive audit

- Current inline V2 pages frequently use all-or-nothing `forkJoin`, omit retry, and provide no permission-specific state.
- Several screens use oversized headings, viewport-scaled type, negative letter spacing, rounded pill commands, hover lift, and dense two-column forms that conflict with the production design guidance.
- Review actions execute immediately and lack accessible confirmation, pending state, focus restoration, and live success/failure messaging.
- Collection screens do not provide responsive task-oriented records, search, or announced result counts.
- Project detail exposes backend IDs as the primary relationship label and lacks associated error text for failed forms.
- No supported content-admin ordering API exists, so no drag-only or keyboard reorder UI should be invented.

## Destructive and consequential actions

No V2 delete endpoints are present for projects, products, knowledge sources, or artifacts. The supported high-impact actions are wrapper review-state changes, public wrapper publishing, and access-grant revocation. Only review and publishing belong in Studio; both require precise confirmation and API-confirmed state.

## Duplicate and misplaced surfaces

- `StudioCoursesComponent` duplicates the legacy course wizard concept but is not authorized by its backend dependencies.
- The legacy course wizard belongs to the current admin/teacher authoring contract, not the verified `content_admin` surface.
- Access grants, invitations, learners, cohorts, and settings belong to Organization or Teach.
- Admin course oversight remains under `/admin` and must not gain Studio authoring controls.
- Generation-run metadata remains a technical legacy surface and is not promoted into the curriculum-focused Studio IA.

## Migration recommendation

Introduce guarded `/studio/**` routes for the supported V2 content surface and update `content_admin` navigation/default landing. Preserve `/workspace/**` deep links without broad deletion. Canonical Studio links should use education terms while requests continue to use the existing V2 models and endpoints. Unsupported course graph editing, programs, lessons, assessments, assets, and uploads remain documented gaps rather than nonfunctional screens.
