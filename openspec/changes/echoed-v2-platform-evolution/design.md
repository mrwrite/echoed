# Design: EchoEd V2 Platform Evolution

## Target Architecture

EchoEd V2 SHALL add a platform layer above the existing education runtime:

```text
Workspace
  -> Project
    -> Knowledge Sources
    -> Knowledge Graph
    -> AI Analysis
    -> Generation Runs
    -> Artifacts
    -> Products
      -> Existing Education Runtime
        -> Course
          -> Unit
            -> Lesson
              -> Activity
      -> Learner Portal
      -> Analytics
```

The existing education engine remains the delivery layer. New V2 concepts organize knowledge ingestion, generation, packaging, publishing, access, and continuous improvement.

## Current Architecture Preservation Strategy

EchoEd SHALL preserve:

- existing SQLAlchemy runtime models
- existing FastAPI route families
- existing progress semantics
- existing lesson governance and readiness rules
- existing assessment and certification behavior
- existing auth, role, and organization behavior

The V2 platform layer SHALL be additive. New objects reference current runtime objects instead of duplicating them.

### Why

The current runtime already solves hard education problems: governed delivery, progress, assessments, certifications, organizations, sections, and role-aware behavior. Replacing these systems would introduce unnecessary risk.

### Problem Solved

The current app lacks a unifying platform model for AI-generated technical knowledge products. Wrappers create that model without disturbing delivery.

### Existing Functionality Reused

Organizations, memberships, courses, programs, lessons, sources, progress, assessments, certifications, sections, and analytics.

### Migration Required

Add new tables and route aliases first. Backfill wrapper records later. Keep existing APIs live during migration.

### Future Capabilities Unlocked

Product packaging, source-aware generation, artifact review, memberships, checkout readiness, enterprise knowledge projects, and source coverage analytics.

## Navigation Migration

Target global navigation:

```text
Workspace
Projects
Product Studio
Products
Knowledge Sources
Artifacts
Review Center
Learners
Analytics
Settings
```

Existing page mapping:

| V2 Area | Existing Surface | Migration Strategy |
|---|---|---|
| Workspace | user dashboard, org context, preferences | Add workspace shell and route aliases |
| Projects | new placeholder | Add empty-state placeholder in Phase 1 |
| Product Studio | course wizard, studio courses | Rename and route existing authoring surface |
| Products | admin courses, available courses, programs | Product terminology first, wrapper model later |
| Knowledge Sources | lesson sources, uploads | Placeholder first, model in Phase 2 |
| Artifacts | generated outputs, media/uploads | Placeholder first, registry in Phase 2/4 |
| Review Center | lesson governance, readiness | Placeholder first, queue later |
| Learners | users, student courses, sections | Rename surfaces gradually |
| Analytics | current analytics | Add V2 dashboard later |
| Settings | preferences, org invites, admin users | Consolidate over time |

## Route Migration

Phase 1 route aliases:

```text
/workspace
/workspace/projects
/workspace/product-studio
/workspace/products
/workspace/knowledge-sources
/workspace/artifacts
/workspace/review-center
/workspace/learners
/workspace/analytics
/workspace/settings
/learn
/learn/products
/learn/paths
/learn/resources
/learn/certificates
```

Existing `/home` routes SHALL remain functional. Route aliases MAY render current components while labels and navigation move toward V2 terminology.

## Domain Model Evolution

New platform concepts:

- `Workspace`: top-level operating context, initially backed by existing organizations.
- `Project`: groups sources, analysis, artifacts, and products.
- `KnowledgeSource`: reusable source asset used for analysis, generation, and citations.
- `KnowledgeGraph`: structured representation of source relationships and concepts.
- `AIAnalysis`: persisted understanding of sources or projects.
- `GenerationRun`: auditable AI generation event.
- `Artifact`: generated or uploaded reviewable output.
- `Product`: package users can access, learn from, download, or eventually buy.
- `LearningPath`: productized sequence that may wrap existing programs.
- `Learner`: product-facing identity around existing users/students.
- `AccessGrant`: explicit permission to access a product or resource.
- `ReviewCenter`: workflow surface for lessons, artifacts, products, and generated drafts.

## Data Model Strategy

All model additions SHALL be additive.

Recommended migration order:

1. `workspaces`
2. `projects`
3. `products`
4. `knowledge_sources`
5. `artifacts`
6. `generation_runs`
7. `access_grants`
8. `review_requests`
9. `analytics_events`

Backfill strategy:

- create one workspace per organization
- create default projects for existing organizations or course collections
- create one product per existing course
- optionally create product wrappers for programs
- link existing lesson sources to knowledge sources without deleting original source rows

## Backend Impact

New route families MAY be added when no existing route owns the new domain:

```text
/api/workspaces
/api/projects
/api/products
/api/knowledge-sources
/api/artifacts
/api/generation-runs
/api/review-center
/api/access-grants
/api/analytics/v2
```

Existing route families SHALL remain authoritative for current runtime behavior:

```text
/api/courses
/api/units
/api/lessons
/api/activities
/api/programs
/api/progress
/api/start-course
/api/assessments
/api/certifications
/api/orgs
/api/auth
```

## Frontend Impact

The frontend SHALL evolve by composition:

- add V2 navigation labels
- add route aliases
- reuse current shell, guards, services, and pages
- embed existing Course Wizard inside Product Studio
- reframe student dashboard as Learner Portal over time
- reframe admin/teacher surfaces as Workspace and Product operations

Phase 1 SHALL not require backend model changes.

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Runtime regression | Keep Course/Unit/Lesson/progress APIs unchanged |
| Navigation confusion | Add aliases before removing old labels |
| Product abstraction too broad | Start with course-backed products only |
| AI trust issues | Generated outputs remain draft artifacts until reviewed |
| Source migration loses citations | Link/copy sources without deleting original rows |
| Payment scope creep | Build access grants before checkout |
| Overbuilt enterprise features | Defer advanced permissions and billing |

## Phase-Based Rollout

1. Workspace shell and navigation reframe
2. Wrapper models for Workspace, Project, Product, Artifact, KnowledgeSource, GenerationRun
3. Product Studio foundation
4. Knowledge pipeline and artifact registry
5. Review Center expansion
6. Learner Portal V2
7. Access grants
8. Analytics V2
9. Commercialization readiness

Each phase SHALL preserve the existing education runtime and include migration notes, tests, and operational validation.

