# Security Event Logging

Phase 8 security events now flow through the Phase 10 structured, recursively redacted application logger. `security_event` writes request/correlation ID, actor ID (or anonymous), action, target type/ID when authorized, result, and safe reason code; bounded action/result counters provide aggregate operational visibility.

Implemented events include authentication failure, limiter triggers, platform role changes, user deletion, final-super-admin protection failures, organization invitation creation, upload rejection, and moderator forum deletion. Existing request logs also record cross-organization denial status/path correlation without response bodies.

Never log passwords, bearer/invitation/reset tokens, uploaded bytes, filenames supplied by users, learner content, decoded JWT payloads, or unnecessary email/profile data. IDs are operational identifiers, not permission to expose associated records.

These logs are diagnostic, potentially ephemeral, and intended for monitoring and incident response. Supported high-impact mutations also write transaction-bound durable audit records through `app.audit`; those records have minimized before/after state, scoped review/export, retention tooling, and integrity verification. Operational logs remain distinct and may describe denied or failed attempts that correctly do not create successful durable records. See [the audit-event policy](../audit/audit-event-policy.md).
