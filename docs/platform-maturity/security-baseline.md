# Platform Security Baseline

Date: 2026-07-23

This is a focused repository review, not a penetration test. Severity reflects plausible impact in a production deployment; environment-specific exploitability still requires threat modeling.

## Findings

| Severity | Finding | Evidence | Phase 7 disposition |
| --- | --- | --- | --- |
| Critical | Forum CRUD has no authentication/object scope and trusts caller-supplied user IDs | `backend/app/api/routes/posts.py`, `threads.py`; routers mounted under `/api/forum` | Not safely patchable without product scope and migration. Route to `harden-platform-security` and `implement-community-collaboration`; do not present a production Community surface. |
| High | Installed Angular 20.3.21 runtime had six high and two moderate production advisories | `npm audit --omit=dev`; advisories covered Angular common/core/compiler and dependents | Patched the coordinated runtime/compiler set to 20.3.25; dependency tree is deduplicated and full tests/build are required. |
| High | Authentication debug logs disclosed raw bearer tokens and decoded claims | `backend/app/auth.py` logged token, payload, subject, expiration, and ORM user | Fixed: removed sensitive debug values and retained privacy-safe rejection reasons. |
| High | Image uploads accepted arbitrary extensions/content types and unbounded streams | `backend/app/api/routes/uploads.py` previously copied caller files directly | Fixed: safe UUID names, explicit PNG/JPEG/GIF/WebP type-extension match, 5 MB limit, and partial-file cleanup. Malware scanning/storage isolation remains future work. |
| High | Organization role dependency accepted inactive memberships | `backend/app/deps.py::require_org_roles` previously filtered organization/user/role only | Fixed: requires `MembershipStatus.ACTIVE`; focused regression added. |
| High | Admin user APIs expose broad ORM objects and accept full DTO role strings | `users.py` list/detail/update; `User` contains hashed password; Phase 6 register | Future `harden-platform-security`: minimized schemas, role allowlist, self/final-admin invariants, lifecycle. |
| High | No application rate limiting for login, registration, uploads, or mutations | No limiter middleware/dependency in `backend/app/main.py` or route tree | Future security proposal; policy and trusted proxy/deployment topology are prerequisites. |
| Medium | `/auth/protected` name implied protection but had no dependency | `backend/app/api/routes/auth.py` | Fixed by requiring the current authenticated user; regression added. |
| Medium | API lacked consistent basic response security headers | `backend/app/main.py` baseline | Fixed for API responses: `nosniff`, frame denial, and no-referrer. Frontend CSP/HSTS remain deployment concerns. |
| Medium | CORS permits all methods/headers with credentials for configured origins | `backend/app/main.py`; origins are explicit, not wildcard | Documented. Narrowing methods/headers needs a complete client contract; validate production `FRONTEND_URL`. |
| Medium | No durable audit record for privileged/destructive/publish actions | Models/routes contain no general audit event | Future `implement-platform-audit-events`; request logs are not an audit ledger. |
| Medium | Static upload directories are directly mounted | `main.py` mounts storybook/colorings/badges | Future asset/security design should address authorization, cache headers, malware scanning, and storage isolation. |
| Low | JWT is a 120-minute bearer token with no revocation/rotation/session record | `auth.py`; frontend stores current token client-side | Future security decision; shorten/refresh/revoke semantics require product and data-model work. |
| Low | API error details are generally explicit but do not expose stack traces by design | FastAPI HTTP exceptions across routes | Retain client-meaningful errors; production exception handling/log redaction needs observability work. |
| Informational | CSRF exposure is limited by bearer Authorization tokens rather than cookie auth | OAuth2 bearer flow and Angular interceptor | Reassess if authentication moves to cookies. |
| Informational | `JWT_SECRET` is fail-fast required | `backend/app/auth.py` raises when missing | Positive baseline; production rotation/secret manager process remains operational work. |

## Boundaries reviewed

- Authentication: bcrypt password verification, JWT signature/expiry/subject lookup, required signing secret.
- Role and organization checks: platform role dependencies, active organization header parsing, Phase 6 section resolver, active membership enforcement.
- Object authorization: strong in Phase 6 org/section and V2 workspace helpers; inconsistent in legacy forum and broad admin user APIs.
- Cross-organization/IDOR: targeted Phase 6 tests exist; future work must expand property/role matrices.
- Inputs and errors: Pydantic coverage is broad; uploads needed explicit binary policy; many string status/role fields need allowlists.
- Browser boundary: explicit CORS origins; baseline response headers added. HSTS and CSP belong at the frontend/edge deployment boundary.
- Secrets/logging: required JWT secret; raw-token logging removed. No secrets were copied into these documents.
- Administrative actions: frontend confirmations exist, but backend invariants and durable auditability are incomplete.

## Required next actions

Before beta, either secure or disable the forum routes, finish privileged user mutation constraints, establish rate limits appropriate to the deployment topology, retain patched production dependencies, and implement durable audit events for high-impact actions. Before general availability, complete session/revocation policy, asset scanning/storage isolation, CSP/HSTS at the serving edge, retention/privacy review, and a formal threat model.
