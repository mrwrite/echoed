## Context

EchoEd has a FastAPI/SQLAlchemy backend, Angular bearer-token client, explicit organization memberships, public legacy forum reads/writes, direct filesystem image uploads, and a single-process Uvicorn deployment. Phase 7 added baseline headers, privacy-safe request correlation, active-membership enforcement, and bounded upload streaming, then identified forum authorization, privileged-user schemas/invariants, and rate limiting as the next critical change. Phase 8 must harden those boundaries without replacing authentication, inventing a new organization model, or disturbing unrelated course-authoring work already present in the tree.

## Goals / Non-Goals

**Goals:**

- Make every forum write authenticated and owner-validated while preserving intended public reads.
- Express global and organization roles as canonical backend allowlists and deny unrecognized roles.
- Restrict platform user administration by actor scope, target hierarchy, allowed fields, self-action, and final-admin invariants.
- Rate-limit authentication, uploads, invitations, forum writes, and privileged mutations through documented endpoint groups.
- Validate actual uploaded image bytes and dimensions before atomic storage.
- Return explicit minimized administrative schemas and privacy-safe security events.
- Expand object/cross-organization tests and keep supported Angular workflows compatible.

**Non-Goals:**

- Replacing JWT/bcrypt or adding SSO, OAuth, MFA, session revocation, or a new identity provider.
- Building complete moderation, asset-management, notification, audit-log UI, or commercial security products.
- Creating a new organization hierarchy, broad schema migration, framework rewrite, or unrelated product capability.

## Decisions

1. **Small policy primitives, not a policy engine.** `app.security` will define canonical platform/organization role sets, hierarchy helpers, target-user rules, object concealment helpers, and privacy-safe event logging. Existing `require_roles` and `require_org_roles` remain compatible but validate against centralized sets. This avoids scattered negated checks without adding framework complexity.

2. **Global administration distinguishes `super_admin` and `admin`.** `super_admin` is the highest platform role; `admin` remains an existing platform administrator for compatibility. Both may read minimized platform user records. Only `super_admin` may grant/revoke `admin` or `super_admin` and modify another `super_admin`; ordinary admins may manage learner/teacher/content roles. A user may not change or delete their own administrative account through these endpoints. The final active `super_admin` cannot be demoted or deleted. Because `User` has no active/disabled field, Phase 8 does not invent deactivation and treats persisted users as usable. The database write transaction performs the last-admin count and mutation together; PostgreSQL target/admin rows are locked where supported. Organization-final-admin protection is not introduced because personal organizations and the current product allow membership lifecycle without a formal invariant.

3. **Registration is server-controlled.** Public registration creates `student` globally regardless of caller input and continues creating the personal organization/admin membership. This closes public self-escalation while retaining onboarding. The legacy role field can be accepted for request compatibility but cannot influence authority.

4. **Forum writes use authenticated identity and ownership.** Create payloads omit ownership; the server assigns `current_user.id`. Authenticated users can create threads/posts against existing parents, authors can edit/delete their own content, and platform forum moderators (`admin`, `super_admin`) can edit/delete any item. Updates change content/title only. Public list/detail reads remain available. Reactions, reports, pin/lock/hide/restore, attachments, and other moderation endpoints do not exist and therefore remain explicitly disabled (404), not partially implemented.

5. **A configurable fixed-window limiter is process-local.** The checked-in production command starts one Uvicorn process, so a locked in-memory store is immediately effective and introduces no dependency. Policies live in one configuration module and key by direct socket peer plus normalized account identifier for anonymous authentication, or authenticated user ID for uploads/mutations. Forwarded headers are ignored until trusted proxy configuration exists. Responses use 429 plus `Retry-After`; authentication failures remain generic. The limitation for multiple processes/hosts is documented as follow-up work for a distributed store. High-risk groups fail closed if limiter evaluation itself fails; public availability-sensitive reads are not limited.

6. **Image validation uses standard-library signature parsing.** PNG, JPEG, GIF, and WebP signatures/dimensions are checked from bounded bytes; the claimed extension and MIME must also agree. SVG and active formats remain rejected. Storage names stay server-generated and atomically completed. Public serving remains for product compatibility and is documented as residual same-origin/storage risk; uploads have no replacement/delete API to authorize.

7. **Response schemas are endpoint-specific.** Platform user list/detail return only id, name, username, email, role, and created timestamp required by Angular. Password hashes, update timestamps, ORM relationships, and future model fields cannot serialize. Student lookup omits email. Invitation list responses omit bearer invitation tokens; creation returns the token once because the current no-email distribution workflow requires it, and acceptance continues using a submitted token with generic failures.

8. **Error and concealment semantics are deliberate.** Missing/invalid credentials are 401; known authenticated policy denial is 403; cross-organization/object lookups are 404 where concealing existence is appropriate; lifecycle conflicts such as final-admin/self-lockout are 409; malformed payloads remain 422; limiter enforcement is 429. Angular maps safe error categories and preserves accessible live announcements.

9. **Existing logs carry interim security events.** Structured key/value events include request ID, actor ID, action, target type/ID when authorized, result, and reason code. Passwords, tokens, raw file content, and unnecessary profile data are excluded. A durable, queryable audit ledger remains deferred to `implement-platform-audit-events`.

## Risks / Trade-offs

- [Process-local rate limits do not coordinate across scaled workers] → document the one-process guarantee and require a shared store before scaling API replicas.
- [Direct peer IP may collapse many users behind a reverse proxy] → combine account identifier for auth and authenticated user ID elsewhere; do not trust spoofable forwarding headers.
- [Existing clients may send forum `user_id` or full user DTOs] → Pydantic forbids sensitive extras on hardened mutation schemas; update the Angular client and tests in the same change.
- [Public static uploads remain same-origin and globally readable] → reject active formats, send `nosniff`, generate opaque names, and record object storage/private delivery as deferred work.
- [Concurrent final-admin changes can race] → lock relevant PostgreSQL rows within the mutation transaction; SQLite tests verify invariant behavior but cannot model production row locking.
- [Broad legacy object authorization remains heterogeneous] → add focused multi-organization tests to highest-risk existing routes and document any lower-risk gaps rather than rewriting every domain.

## Migration Plan

No database migration is planned. Deploy configuration with documented rate-limit defaults, deploy backend and Angular together, monitor 401/403/409/429/security-event rates, and retain rollback through the previous application artifact. A rollback restores permissive forum/admin behavior and is therefore an emergency availability measure only. Clear the in-memory limiter by process restart if configuration is mis-sized.

## Open Questions

- A future deployment decision must select a non-commercial shared rate-limit store before multiple API processes or hosts are enabled.
- A later audit-event change must decide retention, access, tamper resistance, and operator UI requirements.
- A future community specification must define organization-scoped forums, moderation roles, reports, reactions, and attachments before those capabilities are enabled.
