# Security Event Logging

Phase 8 security events now flow through the Phase 10 structured, recursively redacted application logger. `security_event` writes request/correlation ID, actor ID (or anonymous), action, target type/ID when authorized, result, and safe reason code; bounded action/result counters provide aggregate operational visibility.

Implemented events include authentication failure, limiter triggers, platform role changes, user deletion, final-super-admin protection failures, organization invitation creation, upload rejection, and moderator forum deletion. Existing request logs also record cross-organization denial status/path correlation without response bodies.

Never log passwords, bearer/invitation/reset tokens, uploaded bytes, filenames supplied by users, learner content, decoded JWT payloads, or unnecessary email/profile data. IDs are operational identifiers, not permission to expose associated records.

These logs are diagnostic, potentially ephemeral, and intended for monitoring and incident response. They are not a durable/tamper-evident audit ledger; no retention guarantee, restricted search/export API, before/after state model, or administrative review UI exists. `implement-platform-audit-events` must separately define append-only persistence, atomic event/action behavior, actor/action/target/organization/correlation, minimized before/after state, retention, access control, privacy, export, and tamper resistance.
