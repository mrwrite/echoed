# Audit Event Privacy and Access

Durable events use identifiers only where attribution and correlation require them. Names, emails, IP addresses, organization names, course/lesson text, assessment responses, invitation tokens, credentials, uploaded content, and raw request payloads are prohibited. Central action-specific allowlists accept only primitive bounded state values and fail the associated transaction if unsafe data is supplied.

Platform audit reads require explicit `admin` or `super_admin`. Organization reads require an active matching `org_admin` membership, except the deliberate `super_admin` scope path. The frontend is a convenience surface; it is not an authorization boundary. Audit export follows the same backend policy and must be handled as sensitive administrative data.

Database operators can alter database state and therefore remain outside the application tamper-evidence boundary. Restrict production database credentials, preserve encrypted backups, verify chains after restore, and investigate any verification failure without rewriting evidence.
