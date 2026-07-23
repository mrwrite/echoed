# Organization Administration Privacy Review

Date: 2026-07-14

## High-risk surfaces and mitigations

| Surface | Risk | Mitigation |
| --- | --- | --- |
| Member directory | Broad account or contact disclosure | Dedicated organization-scoped response; no email, security fields, or unrelated memberships |
| Invitation list | Secret acceptance token or unnecessary contact exposure | Tokens omitted; email shown only for organization invitation administration |
| Class deep links | Cross-organization roster or progress disclosure | Backend filters section ID and active organization together; unknown/out-of-scope IDs return not found |
| Enrollment mutation | Adding an unrelated platform user | Existing endpoint now requires an active membership in the same organization |
| Assignment and analytics reads | Cross-organization identifier probing | Shared scoped-section dependency applied before read or write |
| Course availability | Unsafe access grants to arbitrary users | Canonical view is read-only; no grant mutation control |
| Errors and logs | Sensitive response payloads | UI uses general recovery copy and does not render raw backend bodies or tokens |

## Authorization conclusions

Canonical deep links use `HomeSessionGuard` and `RoleGuard`, but the API remains authoritative. Organization IDs are checked against the active membership, and nested section APIs verify the requested section belongs to that organization. The UI never uses platform-wide user endpoints for organization member discovery.

Remaining privacy work includes a member-safe access-grant mutation contract, organization-scoped audit events, and explicit retention/lifecycle behavior for invitations. Those gaps are recorded separately.
