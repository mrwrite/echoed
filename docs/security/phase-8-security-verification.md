# Phase 8 Security Verification

Date: 2026-08-06

`harden-platform-security` is implemented and strictly valid. This evidence confirms the bounded controls in the change; it is not a penetration-test result or a claim that EchoEd is fully secure or production-ready.

## Preconditions and scope

- Phase 7 `establish-platform-maturity-foundation` remains complete (21/21 tasks) and strictly valid.
- Phase 7 is not archived; its active artifacts were not modified.
- Work began on branch `aqw-echoed-dev` at commit `c6336fa79458c08da75746954615a86522e766a8` with separate course-authoring work already dirty. Those user-authored files were preserved and the Phase 8 implementation was kept within security, compatibility, test, and documentation boundaries.
- No database migration was required. The actual account model has no active/disabled field, so a usable highest administrator means a persisted `super_admin`. Organization final-admin enforcement was deliberately not invented because EchoEd does not require every organization to retain an administrator.

## Control evidence

- Public forum reads remain. Thread/post create, update, and delete require authentication; ownership is server-derived and immutable; author-or-platform-moderator rules are enforced; unsupported reactions, votes, reports, pin/lock, hide/restore, attachments, and broader moderation remain absent/disabled.
- Central backend role allowlists distinguish platform, organization, teaching, content, learner, forum-owner, and moderator authority. Unknown/broad negated-role authorization was not introduced.
- Platform user list/detail/role/delete operations use explicit schemas and actor/target hierarchy. Admins cannot grant platform roles or modify platform administrators. Self-role changes, self-delete, self-escalation, mass assignment, and final-super-admin demotion/deletion fail with actionable conflicts.
- Active organization membership is required for organization operations. Invitation roles are organization-safe; invitation tokens are returned once on creation but removed from list responses. Cross-organization content, section, lesson-session, assignment, and progress identifiers are parent/scope checked and concealed where documented.
- Central fixed-window policies cover login, registration, invitation management/acceptance, uploads, forum writes, and platform user mutations. Limits are environment-configurable, return `429` plus `Retry-After`, use direct socket peer/account/user keys, and intentionally ignore forwarded client-IP headers.
- Existing uploads retain streamed 5 MiB limits, UUID storage names, atomic completion, and explicit format/MIME allowlists. Raster signatures and dimensions/pixel counts are now validated; SVG, traversal, signature mismatches, unauthorized actors, and excess request rates are rejected.
- Privacy-safe structured events cover authentication failures, privileged user/role/delete actions, final-admin blocks, invitation actions, upload rejection, rate-limit triggers, and forum moderation where existing logging has sufficient context.
- Angular maps safe `401`, `403`, concealed `404`, `409`, `422`, and `429` messages, logs out expired sessions, preserves throttled form content, restricts role options, handles reduced schemas, and announces errors accessibly.

## Verification results

| Check | Result |
| --- | --- |
| Phase 7 strict validation | Pass; complete 21/21 and strictly valid |
| Backend complete suite | Pass; **269 passed**, 4,169 existing deprecation warnings; Phase 7 baseline 233 |
| Backend syntax/dependency checks | Pass; `compileall` clean and `pip check` reports no broken requirements |
| Backend format/lint | No formatter or linter is configured/installed by the repository; no substitute dependency was added |
| Angular complete suite | Pass; **299 passed**; Phase 7 baseline 287 |
| Playwright complete suite | Pass; **22 passed**; Phase 7 baseline 19 |
| Production Angular build | Pass; initial 437.82 kB / estimated 118.83 kB, output `dist/echoed-frontend` |
| Production dependency audit | Pass; `npm audit --omit=dev` reports **0 vulnerabilities** |
| Full npm audit | Finding; 31 development-tool vulnerabilities (3 low, 7 moderate, 19 high, 2 critical), documented in the configuration review |
| Phase 8 strict validation | Pass; `openspec validate harden-platform-security --strict` |
| Whitespace validation | Pass; `git diff --check` with line-ending conversion warnings only |

The full Playwright run used a disposable seeded SQLite database and a temporary local static SPA/API-proxy harness because the drive exhausted free space and `ng serve` could not allocate its build heap. The production build itself passed before this harness was used. One existing focus check was made sequence-stable by advancing through at most five keyboard focus targets without sleeps. The final run passed 22/22. Ports 8000 and 4200 were stopped, and the database, harness, Playwright results, and generated caches were removed.

## Residual risk and deferred work

- Rate-limit state is process-local and resets on restart; multi-process/host deployment requires a shared store and an explicit trusted-proxy policy.
- JWTs remain long-lived bearer tokens without refresh, revocation, MFA, OAuth, or SSO. Those identity-architecture changes remain non-goals.
- Uploaded files remain publicly served from API static paths; malware scanning, metadata stripping, private object storage, signed delivery, and organization-bound asset ownership remain future work.
- Security events are ordinary logs, not a durable, queryable, tamper-resistant audit ledger.
- The domain model still lacks account activation/security-state fields; therefore deactivation/reset/impersonation routes remain unsupported rather than partially implemented.
- Some legacy resources (notably assessments, certificates, reports, and uploads) lack complete organization ownership metadata. Existing accessible operations are role/parent checked where the model permits; schema-backed end-to-end isolation requires later domain work.
- Trusted-host policy, HSTS/CSP, production OpenAPI policy, secret rotation, backup/restore proof, and production-mode configuration validation remain deployment-hardening work.
- Development-only npm findings remain; production dependencies audit clean. Local/CI toolchains must remain non-public and avoid untrusted project inputs until a bounded dependency remediation change lands.

The recommended next OpenSpec change remains `establish-platform-observability`, followed by `implement-platform-audit-events` once correlation and operational telemetry are established.
