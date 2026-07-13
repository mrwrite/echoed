# Admin Privacy Review

Date: 2026-07-13

## High-Risk Surfaces And Mitigations

| Surface | Risk | Production mitigation |
| --- | --- | --- |
| User directory | Broad disclosure of contact/security data | Shows display name, role, and creation date only. Email and username appear only after opening one protected record. Raw ID is not visible. |
| Backend user serialization | ORM response may include hashed password/internal fields | Typed frontend projection never renders unknown fields. Dedicated backend response schema remains a gap. |
| User detail | Mixing platform identity with learner progress | Shows identity and platform role only; no learner progress, demographics, tokens, password data, or global activity. |
| Organizations | Cross-organization disclosure | Uses membership-scoped `/api/orgs`; neutral unavailable state for unknown deep links; does not infer members/admins/classes/invites. |
| Courses | Learner and author identity exposure | Shows curriculum/governance metadata, not learner progress or teacher assignment data. Creator/organization UUIDs are not displayed. |
| Reporting | Misleading or identifying analytics | Uses aggregate documented counts only; no learner/organization ranking or individual activity. |
| Errors | Sensitive payload leakage | User-facing messages are neutral and do not echo backend payloads or identifiers. |
| Destructive operations | Hidden scope | Confirmations state known cascades and unaffected organizations/courses. |

Backend authorization remains authoritative for every API call and `RoleGuard` protects deep links after session bootstrap. The frontend does not log administrative payloads. Organization and learner contexts remain separate.
