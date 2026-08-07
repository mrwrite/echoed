## 1. Preconditions and audit evidence

- [x] 1.1 Verify Phase 7 completion, strict validity, archive status, branch/commit, and pre-existing worktree changes without modifying archived or unrelated work
- [x] 1.2 Record authentication, authorization, roles, organization scope, rate limiting, upload/forum/admin routes, existing tests, and verified test baselines in `docs/security/phase-8-security-baseline.md`
- [x] 1.3 Complete the trust-boundary threat model and endpoint/object/configuration audit documents with evidence and residual risks

## 2. Canonical authorization and forum boundary

- [x] 2.1 Add centralized explicit platform and organization role allowlists, hierarchy/ownership helpers, deny-by-default semantics, and privacy-safe security-event logging
- [x] 2.2 Secure thread create/update/delete with authentication, server-derived ownership, author-or-moderator checks, immutable ownership, and mutation rate limits
- [x] 2.3 Secure post create/update/delete with authenticated identity, parent existence, author-or-moderator checks, immutable ownership/parent scope, and mutation rate limits
- [x] 2.4 Preserve intended public forum reads, document unsupported reactions/reports/moderation/attachments as disabled, and add forum security regression tests

## 3. Privileged user and organization administration

- [x] 3.1 Add explicit minimized platform-user summary/detail and narrow role-update request schemas that forbid sensitive extra fields
- [x] 3.2 Enforce global actor/target role allowlists, role hierarchy, no self-role change/delete, no self-escalation, and platform-only role grants
- [x] 3.3 Protect the final usable super administrator transactionally across demotion and deletion, with multiple-admin success cases and actionable conflict responses
- [x] 3.4 Make public registration authority server-controlled and reject/ignore caller privilege assignment safely
- [x] 3.5 Harden organization membership/invitation role grants, active membership/switch scope, token response exposure, and cross-organization behavior
- [x] 3.6 Add privacy-safe structured events and rate limits for privileged account, role, invitation, and cross-organization decisions
- [x] 3.7 Add privileged-user, administrator-safety, mass-assignment, response-minimization, and organization-isolation backend tests

## 4. Rate limiting and uploads

- [x] 4.1 Implement environment-configurable centralized fixed-window policies, direct-peer/user/account keys, independent windows, reset behavior, 429 responses, and retry metadata
- [x] 4.2 Apply limits to login, registration, invite acceptance/creation, uploads, forum writes, and user-management mutations without account-existence disclosure
- [x] 4.3 Add image signature/dimension validation, server-controlled paths, explicit format/size rejection, and cleanup while retaining safe existing upload behavior
- [x] 4.4 Add rate-limit configuration/proxy/failure tests and upload signature, traversal, authorization, size, and format regression tests

## 5. Object authorization and frontend alignment

- [x] 5.1 Audit client-supplied object identifiers across users, organizations, memberships/invites, sections, content, progress, badges/certificates, forum, uploads, reviews, and reports; fix evidenced high-risk parent/organization gaps narrowly
- [x] 5.2 Add two-organization multi-role backend tests for members, invites, sections, learner data, assignments/resources, and direct-object/parent-child mismatches
- [x] 5.3 Standardize security-relevant 401, 403, concealed 404, 409, 422, and 429 responses without internal leakage
- [x] 5.4 Update Angular admin schemas/actions and accessible error handling for final-admin/self-lockout, reduced responses, uploads, and rate limits
- [x] 5.5 Add Angular tests for 401/403/404/429 handling, reduced schemas, inaccessible forum mutations, administrator validation, and accessible upload/security errors
- [x] 5.6 Add stable Playwright coverage for anonymous forum mutation rejection, organization isolation, lower-role platform denial, final-admin protection, accessible throttling, and direct protected routes where practical

## 6. Documentation and verification

- [x] 6.1 Complete all required Phase 8 security policy, audit, response, organization-isolation, event, upload, rate-limit, and administrator-control documents
- [x] 6.2 Update `SECURITY.md`, `ARCHITECTURE.md`, `README.md`, `ROADMAP.md`, and relevant platform-maturity/UX canonical documents with links and deferred work
- [x] 6.3 Run backend format/lint and the complete backend suite without collection regression
- [x] 6.4 Run frontend format/lint, complete Angular tests, production build, and supported dependency audit without collection regression
- [x] 6.5 Run the complete Playwright suite, clean temporary services/data/artifacts, and record stable results
- [x] 6.6 Run strict OpenSpec validation and `git diff --check`, confirm no secrets/temp QA data/unrelated feature work, and complete `docs/security/phase-8-security-verification.md`
