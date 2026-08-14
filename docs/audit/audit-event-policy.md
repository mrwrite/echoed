# Durable Audit Event Policy

## Store boundary

Durable audit events are append-only application evidence for approved high-impact mutations. Structured security logs remain ephemeral diagnostics for monitoring and incident response. A successful durable mutation event is transactionally coupled to business state; an operational log is not.

The database row contains UUID/timestamp, stable action/category/outcome, actor UUID and role snapshot, target type/ID, optional organization UUID, request/correlation references, version, allowlisted primitive before/after summaries, reason code, and integrity-chain hashes. It contains no joined names, emails, content, credentials, tokens, request bodies, or files.

## Action catalog

| Stable action | Scope | State keys |
| --- | --- | --- |
| `platform.role.changed` | Platform | role |
| `platform.user.deleted` | Platform | role |
| `organization.invite.created` | Organization | role, status |
| `organization.invite.accepted` | Organization | role, status |
| `forum.post.moderated` | Platform | moderator override |
| `forum.thread.moderated` | Platform | moderator override |
| `course.review.changed` | Owning organization when present | review state |
| `course.version.published` | Owning organization when present | version status |
| `product.review.changed` | Workspace organization when present | review state |
| `product.published` | Workspace organization when present | status, visibility |
| `audit.exported` | Platform | row count |
| `audit.retention.performed` | Selected scope | deleted count, cutoff |

Denied or rolled-back mutations remain in privacy-safe operational security logs and do not become misleading durable success events.

## Access matrix

| Actor | Platform feed/detail/export | Organization feed |
| --- | --- | --- |
| `admin` | Allowed | Only through platform feed unless active organization policy grants org-admin authority |
| `super_admin` | Allowed | Allowed for explicitly selected active scope |
| active `org_admin` | Denied | Own active organization only |
| other authenticated roles | Denied | Denied |
| anonymous | 401 | 401 |

Backend authorization is authoritative. Cross-organization organization feeds are concealed with 404. Reads use explicit schemas, bounded cursor pagination, and allowlisted filters. CSV applies the same platform scope, caps output at 5,000 rows, neutralizes spreadsheet formulas, and records the export itself.

## Integrity boundary

Events form a SHA-256 chain per platform or organization scope over canonical, versioned event content and a unique sequence. PostgreSQL transaction advisory locking serializes even concurrent first writes within a scope. Verification detects ordinary modification and reordering within retained history, while ORM guards reject ordinary application updates/deletes and no mutation API exists. Because guarded retention may delete an old prefix, only an external anchor could prove deletion before the retained boundary.

This is tamper-evident application data, not proof against a fully privileged database operator who can rewrite rows and hashes. Independent anchoring, WORM storage, database credential separation, and external replication remain infrastructure work.

## Retention and preservation

The initial policy target is 365 days, subject to jurisdiction and operator policy. Security/operations owns execution; privacy/legal owners approve policy and preservation holds. The operator command defaults to dry-run. Production application requires explicit acknowledgement and a verified backup reference; `AUDIT_PRESERVATION_HOLD=true` blocks deletion. There is no public retention API.
