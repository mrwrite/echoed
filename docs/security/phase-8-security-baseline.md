# Phase 8 Security Baseline

Date: 2026-08-06

This snapshot was recorded before Phase 8 behavior changes. It is a repository review, not a penetration test and not a production-readiness claim.

## Repository state

- Branch: `aqw-echoed-dev`
- Commit: `c6336fa79458c08da75746954615a86522e766a8`
- Phase 7 change: `establish-platform-maturity-foundation` is complete (21/21 tasks) and passes `openspec validate establish-platform-maturity-foundation --strict`.
- Phase 7 archive status: not archived. It remains at `openspec/changes/establish-platform-maturity-foundation/`; no archived OpenSpec file will be modified by Phase 8.
- Working tree: dirty before Phase 8. Modified and untracked files belong to the separate completed `unify-course-authoring-experience` work and are preserved. The pre-existing paths are the course route/schema/governance and Angular Studio/environment files, the new course-authoring backend modules and tests, the new Course Studio frontend files/test, course-authoring documentation, and that OpenSpec change.

## Authentication and authorization

- Authentication uses bcrypt password hashes and signed HS256 JWT bearer access tokens. `JWT_SECRET` is mandatory at import/startup and tokens expire after 120 minutes. The database user is resolved again for every authenticated request. There is no refresh, revocation, session, MFA, OAuth, or SSO system.
- Registration and `/auth/token` are public. At baseline, registration trusts a caller-provided global role and login returns `400` for invalid credentials. Neither route is rate-limited.
- Backend authorization is primarily implemented through `require_roles(...)`, `require_org_roles(...)`, and route-local object checks. Checks are explicit in some mature organization/section/V2 routes but inconsistent across legacy routes. Angular guards and hidden controls are navigation aids only, not security boundaries.
- Supported global role strings found in runtime code and seed data are `student`, `teacher`, `content_admin`, `org_admin`, `admin`, `super_admin`, and the legacy-compatible `instructor` role. Organization roles are `org_admin`, `content_admin`, `teacher`, `parent`, `student`, `instructor`, `viewer`, and `super_admin`.
- Organization scoping uses an authenticated user membership plus `X-Org-Id`. `require_org_roles` requires an active membership. Several route families add parent-resource checks. A `super_admin` bypass exists, but its baseline implementation can return another user's membership and is not a sound canonical platform-scope primitive.

## Sensitive surfaces

- Rate limiting: none. There is no middleware, dependency, shared store, `429` contract, or trusted-proxy configuration.
- Uploads: `/api/upload/coloring` and `/api/upload/storybook` allow global `admin` or `teacher`; `/api/upload/badge` allows `admin`. The server uses UUID filenames, a 5 MiB streamed limit, an extension/content-type allowlist, atomic `.part` completion, and cleanup. It does not validate magic bytes, strip metadata, bind ownership/organization, or isolate served files from the application origin. Static upload directories are public.
- Forum access: thread/post reads and all thread/post mutations are public. Mutations trust caller-supplied `user_id`; updates can replace ownership. There are no organization, membership, owner, moderator, reaction, report, attachment, or moderation controls.
- Privileged user management: `GET /api/users`, `GET /api/users/{id}`, `PUT /api/users/{id}`, and `DELETE /api/users/{id}` require global `admin`. `GET /api/users/students` allows `admin` and `teacher`. List/detail endpoints return ORM objects without response schemas, exposing fields such as `hashed_password`; update accepts the registration DTO including password and arbitrary role. There are no explicit target hierarchy, self-action, mass-assignment, final-admin, organization, or audit controls.
- Organization user management: organization admins can list members and create/list invitations within the active organization. Invite responses expose acceptance tokens. Invite role construction is enum-bounded but includes `super_admin`; there is no narrowed organization-admin grant allowlist or rate limit.

## Existing security evidence and test baselines

- Existing focused tests cover authentication-required diagnostics, response headers/request IDs, upload MIME/size rejection, active organization membership, organization scope, direct user admin operations, and the current anonymous forum behavior.
- The verified Phase 7 baseline is 233 backend tests, 287 Angular tests, and 19 Playwright tests. Phase 7 itself cites the earlier minimums of 228, 284, and 16 respectively.
- The current dirty course-authoring work adds legitimate tests beyond Phase 7. Before Phase 8, its recorded verification was 294 passing Angular tests, 84 passing targeted backend tests, one passing Course Studio browser smoke, a passing production build, strict OpenSpec validation, and `git diff --check`. A complete current backend and Playwright baseline had not yet been re-established after those unrelated changes and must be measured during Phase 8 verification; no unexplained collection reduction is acceptable.

## Deployment and configuration baseline

- The checked-in deployment starts one Uvicorn process, so a process-local limiter can enforce limits for that topology. It will not coordinate across multiple API processes or hosts.
- Forwarded client-IP headers are not explicitly trusted or parsed by the application. The direct socket peer is the only safe anonymous key until an explicit trusted-proxy policy exists.
- CORS uses configured explicit origins but permits all methods and headers with credentials. API responses include request correlation, `nosniff`, frame denial, and `no-referrer`.
- No durable privileged-action audit ledger exists. Privacy-safe request logging is available and can carry structured security events as an interim control.
