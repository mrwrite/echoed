# EchoEd V2 Platform Evolution

## Why

EchoEd has outgrown the shape of a course-first educational application. The platform already has mature runtime infrastructure: organizations, authentication, roles and permissions, courses, units, lessons, activities, programs, sections, learner progress, assessments, certifications, lesson governance, source-backed lesson readiness, and multi-tenant behavior. Those systems are valuable and SHALL remain the runtime foundation.

The next evolution is to organize EchoEd around the full knowledge-to-learning lifecycle:

```text
Knowledge
-> AI Understanding
-> Generation
-> Governance
-> Publishing
-> Learning
-> Analytics
-> Continuous Improvement
```

EchoEd V2 adds a platform layer above the current education engine so organizations can transform internal, technical, or expert knowledge into trusted learning products. This creates a clearer product architecture without replacing the existing education runtime.

## Why This Is Not A Rewrite

This change explicitly preserves:

- `Course`
- `Unit`
- `Lesson`
- `Activity`
- `Program`
- `Assessment`
- `Certification`
- progress tracking
- governance
- source-backed lesson readiness
- current auth, organization, and role infrastructure
- existing APIs wherever practical

V2 introduces wrapper and orchestration concepts above those systems:

```text
Workspace
-> Project
-> Knowledge Sources
-> AI Analysis
-> Generation Runs
-> Artifacts
-> Products
-> Existing Education Runtime
-> Learner Portal
-> Analytics
```

The guiding architectural rule is: wrap working systems, do not replace them.

## What Problem The V2 Platform Layer Solves

EchoEd currently has strong educational primitives but lacks a canonical platform model for:

- grouping knowledge work into workspaces and projects
- treating source material as durable, reusable knowledge assets
- tracking AI analysis and generation runs
- reviewing generated artifacts before they become published lessons or products
- packaging existing courses, programs, downloads, and future membership hubs as products
- granting learner/member access independently from payments
- organizing analytics around product, source, artifact, and learner outcomes

The V2 layer solves these gaps by introducing stable platform concepts above the existing course runtime.

## Product Positioning

EchoEd should become:

> The AI-native platform that transforms organizational knowledge into trusted learning products.

EchoEd should borrow structural organization patterns from Teachable, GitBook, Notion, Atlassian, GitHub, and OpenAI while preserving its own identity: AI-assisted learning, source-aware knowledge, guided content creation, governed publishing, and structured educational delivery.

EchoEd is not another LMS. It is the operating system for technical knowledge.

## Teachable-Inspired, Not Teachable-Cloned

Teachable is useful as a reference for packaging: products, creator dashboard, checkout readiness, student experience, analytics, certificates, memberships, admin controls, and product pages.

EchoEd should adapt those platform patterns for a more technical and AI-native workflow:

- source material enters through projects and knowledge sources
- AI analysis creates structured understanding
- generation runs produce artifacts and drafts
- review center protects trust and governance
- products package courses, paths, artifacts, and resources
- learners consume governed, source-backed learning experiences
- analytics drive continuous improvement

## Capabilities

### New Capabilities

- `workspace-platform-foundation`
- `project-knowledge-pipeline`
- `product-studio`
- `product-catalog`
- `artifact-registry`
- `review-center`
- `learner-portal-v2`
- `access-grants`
- `analytics-v2`

### Existing Capabilities Preserved

- course and lesson runtime
- governed learner delivery
- progress and course completion
- assessment and certification flows
- organization and role foundations
- source-backed lesson readiness

## Phase 1 Scope

Phase 1 SHALL be low-risk and non-destructive. It focuses only on:

- V2 navigation
- route aliases
- workspace shell
- product terminology
- mapping existing pages into the new platform structure
- placeholder routes for future concepts

Phase 1 SHALL NOT introduce database migrations, runtime rewrites, auth changes, progress changes, payment flows, or new AI generation behavior.

## Impact

### Backend

V2 eventually adds wrapper models and APIs for workspaces, projects, products, knowledge sources, artifacts, generation runs, access grants, and analytics. Existing course, lesson, progress, assessment, certification, auth, and organization APIs remain available.

### Frontend

The frontend evolves navigation and information architecture first. Existing pages are remapped into the new structure before new workflows are built.

### Data

Existing records are migrated forward through additive backfills:

- organizations can become workspaces
- courses can be wrapped as products
- programs can become learning paths or product bundles
- lesson sources can be linked into knowledge sources
- generated drafts can become artifacts

### Testing

Each phase SHALL include regression coverage for current runtime behavior plus targeted coverage for the new wrapper behavior introduced in that phase.

