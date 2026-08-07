## Why

Phase 7 verified that EchoEd's legacy forum mutations, privileged user-management APIs, upload boundary, and sensitive endpoints lack several fail-closed controls required for responsible platform operation. This focused phase closes those evidenced gaps while preserving supported Student, Teacher, Studio, organization, platform-admin, public, authentication, and onboarding behavior.

## What Changes

- Require backend-authenticated, owner-scoped forum mutations and make every supported or unsupported community mutation policy explicit; public reads remain compatible.
- Replace broad privileged-user DTO/ORM behavior with explicit actor/target role allowlists, minimized response schemas, organization boundaries, self-action rules, and final-platform-administrator protection.
- Centralize small backend authorization primitives for platform roles, organization roles, ownership, and consistent concealment/error semantics.
- Add configurable rate limiting for authentication, uploads, invitations, forum writes, and privileged user mutations with `429` and retry metadata.
- Validate upload signatures and safe image properties in addition to existing size, name, MIME, and extension controls.
- Add privacy-safe structured security events using existing logging, while deferring a durable audit-log product.
- Align Angular errors and controls with `401`, `403`, `404`, `409`/`422`, and `429` backend outcomes, and expand backend, Angular, and stable browser authorization coverage.
- Document the threat model, endpoint decisions, role policy, residual risks, configuration assumptions, and verification evidence.
- Security-sensitive behavior may become more restrictive. Unauthenticated or unauthorized mutations fail closed; frontend guards and hidden controls are not security boundaries.

## Capabilities

### New Capabilities

- `platform-security-hardening`: Backend-enforced authorization, administrator safety, abuse throttling, secure uploads, minimized administrative responses, organization isolation, security errors/events, frontend alignment, and regression verification.

### Modified Capabilities

- `auth-org-session-authority`: Registration role assignment and organization authority become explicit, server-controlled, and deny-by-default.

## Impact

Affected areas include FastAPI authentication/dependencies, forum, user, organization/invitation, and upload routes; Pydantic schemas; request/security logging; Angular admin and HTTP error behavior; backend/Angular/Playwright tests; deployment configuration; security and architecture documentation. Existing libraries are preferred, larger identity-provider/session redesigns are excluded, and no unrelated database migration or product capability is introduced.
