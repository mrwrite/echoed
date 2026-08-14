# Future OpenSpec Roadmap

Date: 2026-08-06

## Prioritization

Priority weighs release criticality, security/privacy risk, architectural dependency, user and educational value, migration/data-model risk, testability, operational cost, and whether a bounded change is suitable for contributors. Complexity is relative: S, M, L, or XL. “Beta blocker” means the capability or an explicit decision to disable its unsafe surface is required before a public beta.

## Recommended sequence

Completed foundation changes: `harden-platform-security` (Phase 8), `establish-platform-observability` (Phase 10), and repository-scoped `establish-operational-readiness` (Phase 11).

1. `establish-operational-readiness`
2. `implement-platform-audit-events` (implemented; archive after verification)
3. `implement-curriculum-authoring`
4. `implement-activity-and-assessment-authoring`
5. `implement-content-review-workflow`
6. `implement-content-publishing-lifecycle`
7. `implement-asset-library`
8. `implement-teacher-feedback-and-review`
9. `implement-content-version-history`
10. `implement-notification-infrastructure`
11. `implement-content-search`
12. `implement-community-collaboration`
13. `prepare-echoed-1-0-release`

## Candidate proposals

### `harden-platform-security`

Phase 8 implementation adds the scoped controls and evidence under `docs/security/`. Remaining distributed rate limiting, durable audit persistence, session revocation, and private/scanned assets stay assigned to later changes; passing this phase does not establish production readiness.

- **Problem/users/value:** Maintainers and every role need authenticated, object-scoped APIs and safe uploads; current forum CRUD is unauthenticated and several administrative/user contracts need minimization and lifecycle invariants.
- **Current limitation/support:** `auth.py`, `deps.py`, Phase 6 section scoping, and upload roles provide a base, but `posts.py`/`threads.py` trust caller IDs, rate limiting is absent, and user mutations are broad.
- **Required work:** Backend authorization matrix, object ownership/scope enforcement, safe user-role/status mutations, rate-limit strategy, upload verification, error policy; frontend handles explicit denial/limit states without simulated controls.
- **Authorization/migrations:** New forum scope and user lifecycle may require membership/section/report-state migrations; preserve final-admin invariants.
- **Dependencies/security/privacy:** First roadmap dependency; high student/community privacy and privilege-escalation impact.
- **Testing/complexity/priority:** Cross-org IDOR, role matrix, upload, brute-force, and destructive-action tests; **XL / P0 / beta blocker**. Contributor work should be split by endpoint family under one reviewed security design.

### `establish-platform-observability`

Phase 10 implements structured/redacted logs, request/correlation IDs, bounded process-local metrics with protected optional export, database readiness/failure signals, Course Studio events, safe Angular diagnostics, and operational guidance. It does not add distributed tracing infrastructure, alert routing, a commercial vendor, or durable audit persistence.

- **Problem/users/value:** Operators cannot reliably correlate failures or measure availability.
- **Current limitation/support:** The Phase 10 foundation is implemented; external aggregation/alerts, multi-process metric continuity, and distributed traces remain deployment work.
- **Required work:** Backend logging schema, auth/authorization outcome events, metrics interfaces, trace propagation, frontend error envelope/reporting hook, redaction tests, and runbooks. No commercial provider is assumed.
- **Authorization/migrations:** Metrics export is disabled by default and token protected; no database migration was required.
- **Dependencies/security/privacy:** Follows security threat classification; logs must exclude tokens, learner content, and unnecessary identifiers.
- **Testing/complexity/priority:** Middleware/health failure, redaction, metric cardinality, frontend reference, and domain-event tests provide the Phase 10 gate; **implemented M / P0 foundation**.

### `establish-operational-readiness`

Phase 11 adds fail-closed runtime configuration, explicit host/proxy trust, non-mutating startup, explicit migration/head gates, health/shutdown integration, initial SLO/alert policy, safe backup/restore tooling, storage/rotation ownership, and evidence-driven local drills. Provider-specific alert delivery, backup scheduling, PostgreSQL production recovery measurement, and object storage remain infrastructure dependencies.

- **Problem/users/value:** Maintainers need reproducible deployment, rollback, backup, restore, migration, and secret-rotation procedures.
- **Current limitation/support:** The repository-owned operational contract is implemented; hosting selection and externally scheduled/aggregated operations remain unresolved.
- **Required work:** Select deployment assumptions, validate production config, migration gate, backup/restore drill, static asset ownership, secret rotation, rollback and post-deploy verification.
- **Authorization/migrations:** No product authorization change; may add migration safety metadata or operator-only tooling.
- **Dependencies/security/privacy:** Depends on hosting decision and security secret policy; backups contain learner data.
- **Testing/complexity/priority:** Ephemeral environment deploy/rollback and restore rehearsal; **L / P0 / beta blocker**.

### `implement-platform-audit-events`

The active OpenSpec change implements transaction-bound, privacy-minimized records for the supported high-impact action catalog, per-scope integrity chains, scoped administrative review/export, retention tooling, and backup/restore verification. External anchoring, WORM storage, legal-retention guarantees, and general business activity analytics remain out of scope.

- **Problem/users/value:** Administrators, organization stewards, reviewers, and security responders need attributable high-impact action history.
- **Current limitation/support:** Request logs and assessment attempt events exist, but no durable actor/action/resource audit model covers role, access, publish, invite, moderation, or destructive actions.
- **Required work:** Append-only event model, service interface, minimized read API/UI, retention/export policy, and instrumentation of approved actions.
- **Authorization/migrations:** New audit-event table and indexes; platform/org-scoped reads with immutable writes.
- **Dependencies/security/privacy:** Depends on the implemented security event taxonomy and request correlation. It must define durable append-only persistence, atomic action/event semantics, actor/action/target/organization, minimized before/after state, retention, restricted operator search/export, privacy, and tamper resistance without treating ephemeral logs as evidence.
- **Testing/complexity/priority:** Atomic event/action tests, scope tests, tamper constraints, retention tests; **L / P0 / beta blocker for high-impact admin actions**.

### `implement-curriculum-authoring`

- **Problem/users/value:** Content administrators need a complete organization-scoped course/program/unit/lesson hierarchy workflow.
- **Current limitation/support:** Course, unit, lesson, activity, program, version, readiness, and lineage models/routes exist, but role ownership and transactional ordering are fragmented.
- **Required work:** Consolidated authoring service/API, ownership policy, program editing, transactional reorder, draft validation, stateless preview, and Studio editor flows.
- **Authorization/migrations:** Content-admin/org ownership checks; likely ordering/concurrency metadata migrations, no parallel curriculum model.
- **Dependencies/security/privacy:** Requires security hardening and audit events; unpublished content must not leak to learners.
- **Testing/complexity/priority:** CRUD/ownership, reorder concurrency, preview side-effect, deep hierarchy, visual editor tests; **XL / P1 / beta blocker only if authoring is promised in beta**.

### `implement-activity-and-assessment-authoring`

- **Problem/users/value:** Authors and educators need governed activity, question, rubric, and assessment editing.
- **Current limitation/support:** Activity CRUD and assessment/question creation/attempt models exist; schemas are generic and update/delete/reorder/manual-review behavior is incomplete.
- **Required work:** Typed activity contracts, assessment/question edit/delete/reorder, answer secrecy, draft validation, rubric/manual-review boundaries, and Studio forms.
- **Authorization/migrations:** Scoped author roles; likely activity payload/rubric/version migrations.
- **Dependencies/security/privacy:** Depends on curriculum authoring and audit events; correct answers and learner attempts are sensitive.
- **Testing/complexity/priority:** Type validation, answer redaction, lifecycle, scoring compatibility, migration, and UI tests; **XL / P1 / not a beta blocker unless authoring is in beta**.

### `implement-content-review-workflow`

- **Problem/users/value:** Reviewers and content admins need assigned, explainable, auditable decisions.
- **Current limitation/support:** V2 review center and artifact/product status patches exist, but no assignment, comment, rationale, separation-of-duty, or review history exists.
- **Required work:** Review assignment/comment/decision models, workflow service, notification hooks, scoped queues, and Studio review UI.
- **Authorization/migrations:** New review assignment/comment/event tables; reviewer and publisher permissions must be distinct where policy requires.
- **Dependencies/security/privacy:** Depends on audit events; comments may contain sensitive source or learner-adjacent material.
- **Testing/complexity/priority:** Transition matrix, assignment scope, concurrency, attribution, UI queue tests; **L / P1 / not a beta blocker if publishing remains maintainer-controlled**.

### `implement-content-publishing-lifecycle`

- **Problem/users/value:** Publishers and operators need safe publish, unpublish, archive, and emergency rollback.
- **Current limitation/support:** Course-version and product publish plus readiness validation exist; reversible transitions and dependency checks are absent.
- **Required work:** Explicit lifecycle state machine, dependency validation, scheduled/transactional transitions if approved, public cache behavior, and confirmed UI actions.
- **Authorization/migrations:** Publisher permission; lifecycle event/history fields or tables may require migration.
- **Dependencies/security/privacy:** Depends on authoring, review, and audit events; prevents unintended public disclosure.
- **Testing/complexity/priority:** Transition/property tests, rollback, public visibility, concurrent publish; **L / P1 / beta blocker for public publishing**.

### `implement-content-version-history`

- **Problem/users/value:** Authors and maintainers need understandable diffs and safe restoration after edits.
- **Current limitation/support:** CourseVersion and revision/lineage metadata exist; broad immutable snapshots, diffs, history reads, and restore do not.
- **Required work:** Version ownership/snapshot policy, diff service, restore-as-new-version semantics, history UI, and storage/retention limits.
- **Authorization/migrations:** New snapshots or generalized version tables likely; published and learner-history integrity must be preserved.
- **Dependencies/security/privacy:** Follows stable authoring/publishing contracts; history can retain deleted sensitive content.
- **Testing/complexity/priority:** Diff determinism, restore safety, historical learner interpretation, retention; **XL / P2 / not a beta blocker**.

### `implement-asset-library`

- **Problem/users/value:** Authors need reusable, accessible, rights-aware assets rather than isolated file URLs.
- **Current limitation/support:** Hardened image upload, `Media`, `Source`, and `KnowledgeSource` provide fragments; no governed asset record, usage graph, replacement, alt text, or rights policy exists.
- **Required work:** Scoped asset metadata/API, storage abstraction, malware/content verification integration point, rights/attribution/alt text, usage lookup, safe replace/delete, and Studio library.
- **Authorization/migrations:** New or expanded asset/source tables and reference migrations; org/project scope.
- **Dependencies/security/privacy:** Depends on security and operational storage decisions; uploads can contain copyrighted or personal data.
- **Testing/complexity/priority:** File/type/size, scope, rights validation, usage safety, storage failure, accessibility tests; **XL / P1 / beta blocker if user uploads are enabled broadly**.

### `implement-teacher-feedback-and-review`

- **Problem/users/value:** Teachers and learners need persistent, scoped feedback, manual assessment review, retry grants, and intervention history.
- **Current limitation/support:** Sections, submissions, attempts, answers, analytics, and intervention recommendations exist; teacher feedback/action models do not.
- **Required work:** Feedback/review/retry/intervention models and APIs, learner-visible states, teacher queues, and notification integration.
- **Authorization/migrations:** New scoped tables tied to section enrollment/attempt/submission; strict teacher-roster checks.
- **Dependencies/security/privacy:** Depends on audit events and preferably notifications; educational records require minimization and retention policy.
- **Testing/complexity/priority:** Roster isolation, review transitions, retry limits, learner visibility; **L / P1 / beta blocker for assessed instructor-led pilots**.

### `implement-notification-infrastructure`

- **Problem/users/value:** Learners, educators, reviewers, and operators need reliable in-app event delivery.
- **Current limitation/support:** User preferences exist but no notification, queue, delivery, retry, receipt, or template system exists.
- **Required work:** Event-to-notification contract, in-app store/API/UI, preference semantics, queue adapter, retries/idempotency; email or push requires separate approval.
- **Authorization/migrations:** Notification/delivery/preference tables; recipient-only reads and operator-safe diagnostics.
- **Dependencies/security/privacy:** Depends on source events (review, feedback, announcements, security) and operations; payload minimization is required.
- **Testing/complexity/priority:** Idempotency, preference, recipient scope, retry/failure tests; **L / P2 / not a core beta blocker**.

### `implement-content-search`

- **Problem/users/value:** Learners and authors need discoverability across a growing catalog.
- **Current limitation/support:** Direct list/filter queries and tags exist; there is no cross-domain query contract or index lifecycle.
- **Required work:** Search requirements, permission-filtered indexing/query service, relevance/facets, reindex operation, and Learn/Studio consumers.
- **Authorization/migrations:** Search documents/indexes; results must enforce source visibility and organization scope.
- **Dependencies/security/privacy:** Follows publishing lifecycle and operational hosting choice; indexing unpublished/private content is a disclosure risk.
- **Testing/complexity/priority:** Scope leakage, relevance fixtures, stale index, reindex, accessibility; **L / P2 / not a beta blocker**.

### `implement-community-collaboration`

- **Problem/users/value:** Learners and educators need safe discussion and moderation, not unauthenticated global forum CRUD.
- **Current limitation/support:** Thread/Post models and endpoints exist but lack authentication, scope, reports, moderation, and safe ownership.
- **Required work:** Decide community/section context, replace caller-supplied identity, moderation/report/lock/restore workflow, frontend community surfaces, and safety operations.
- **Authorization/migrations:** Thread/post scope, moderation/report/status/audit fields and migration of any retained demo content.
- **Dependencies/security/privacy:** Depends on security, audit events, observability, and moderation policy; highest safeguarding implications.
- **Testing/complexity/priority:** Ownership/IDOR, cross-org scope, abuse reports, moderation, deletion/restore; **XL / P1 / beta blocker if forum endpoints remain exposed**.

### `prepare-echoed-1-0-release`

- **Problem/users/value:** Maintainers and adopters need an evidence-based release gate; passing Phase 7 alone does not make EchoEd production-ready.
- **Current limitation/support:** Regression suites, OpenSpec, security policy, architecture, and Phase 7 baselines exist; production SLOs, hosting, privacy/legal, backup drills, and release acceptance remain unresolved.
- **Required work:** Freeze supported scope, resolve beta blockers, threat/privacy review, migration/restore rehearsal, accessibility/manual acceptance, performance targets, release notes, rollback and support process.
- **Authorization/migrations:** Reviews all production migrations and role matrices; no catch-all product implementation.
- **Dependencies/security/privacy:** Last in sequence after security, observability, operations, and selected product blockers.
- **Testing/complexity/priority:** Full release matrix and rehearsals; **L / P0 at release time / definitionally blocks 1.0**.
