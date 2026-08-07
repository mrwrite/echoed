# Object-Level Authorization Audit

| Resource family | Required checks / Phase 8 disposition | Evidence or residual work |
| --- | --- | --- |
| Users | platform role, target hierarchy, self/final-admin, explicit fields | hardened; admin/security tests |
| Organizations/memberships/invites | active membership, header/path match, grant allowlist | hardened high-risk paths; org tests |
| Sections | active educator org membership; section organization; course version belongs to org or global catalog | hardened; two-org tests |
| Assignments/lesson sessions | scoped section, unit/lesson belongs to section course version, learner enrollment for submission | hardened parent mismatches; tests cover session paths |
| Courses/programs | existing course-authoring/V2 organization policy; public/published reads deliberate | retained; prior course permission/authoring suites |
| Units/lessons/activities | resolve child to owning course and re-check authoring capability for every mutation, including moves | hardened mutations; content-admin cross-org test |
| Assessments/attempts | student attempt identity is server-owned; staff creation remains legacy global staff scope | existing assessment phase suites; full org-local assessment model deferred |
| Learner progress | resolve unit/segment to student course; learner owns record; teacher must own/be enrolled in section; admin deliberate | hardened direct ID; learner IDOR test |
| Badges/certificates | student own records or explicit admin/super admin; student certifications use `/me` | explicit role cleanup; existing suites |
| Forum | authenticated server-owned author; owner/moderator; immutable parent/owner | hardened; forum suite |
| Uploads | role-gated create only; no client object ID, replacement, or deletion | hardened binary boundary; ownership model deferred |
| V2 workspaces/projects/products/reviews/access grants | existing organization/workspace resolvers and creator/reviewer policies | audited and retained; V2 wrapper tests |
| Reports/analytics | existing scoped section helper for org summary; global analytics roles remain deliberate legacy contract | section cross-org tests; unified reporting scope remains future work |

Policy: cross-organization or parent-mismatch lookups return 404 to conceal the protected object. A known object denied only by actor capability returns 403. Invalid identifiers use 400/422; absent resources use 404. A valid UUID never substitutes for authorization.

Not every legacy read is private: published course, program, certification, forum, and catalog reads retain product visibility. Phase 8 focuses protected records and mutations rather than redesigning catalog publication.
