# Security Policy

EchoEd is early and pre-community-launch. Please report security concerns responsibly and do not test against systems or data you do not own.

## Supported Scope

Security reports may cover:
- Authentication and session handling.
- Authorization or role access issues.
- Exposure of secrets, tokens, or sensitive configuration.
- Demo credential misuse risks.
- Unsafe file upload behavior.
- Cross-site scripting, injection, or data exposure concerns.
- Vulnerabilities in documented setup or deployment instructions.

## Current Baseline

The focused [Phase 7 security baseline](docs/platform-maturity/security-baseline.md) records the prior evidence. The [Phase 8 security baseline](docs/security/phase-8-security-baseline.md), [threat model](docs/security/phase-8-threat-model.md), and linked policies document backend-enforced forum ownership, privileged-user invariants, role allowlists, configurable rate limits, upload signature checks, minimized responses, and expanded object/organization tests. These are scoped hardening controls, not a penetration test or production-readiness certification.

Durable audit events, distributed rate-limit storage, private/scanned asset delivery, session revocation, production proxy/host/CSP/HSTS validation, and formal privacy/retention work remain explicit future work. Do not use the current demo with real learner or production data.

## Reporting a Vulnerability

Send security reports to:

```text
support@echoed.com
```

Please include:
- A clear description of the issue.
- Steps to reproduce if safe to share.
- The affected URL, route, file, or component.
- Impact and suggested severity.
- Whether any data may have been exposed.

Do not include real student, school, personal, or sensitive data in a report.

## Demo Credential Policy

EchoEd currently uses shared demo credentials for evaluation. These accounts are demo-only, resettable, and not intended for real use.

Do not:
- Enter personal, student, school, or production data into demo accounts.
- Treat demo accounts as private workspaces.
- Use demo access for destructive, abusive, or load-testing behavior.
- Attempt to access non-demo data.

If demo credentials appear to expose sensitive data, report it immediately through the security contact above.

## Maintainer Response

This is a no-budget early project, so response time may vary. The intended response process is:

1. Acknowledge the report when possible.
2. Triage severity and reproducibility.
3. Fix or mitigate the issue.
4. Credit the reporter if they want recognition and disclosure is appropriate.

## Public Disclosure

Please do not publicly disclose a suspected vulnerability until there has been a reasonable opportunity to investigate and mitigate it.

## Diagnostic References and Sensitive Evidence

Unexpected API failures may display a bounded request reference. It is safe to include that reference, the approximate time, the action, and a non-sensitive page name in a report. Do not provide passwords, tokens, cookies, authorization headers, invitation/reset links, uploaded files, learner records, assessment responses, or private course content. Backend operational logs and metrics are privacy-redacted diagnostics; they are not a durable or tamper-resistant audit record. See the [observability runbook](docs/operations/observability-runbook.md).

Production configuration fails closed and never loads dotenv. Allowed hosts are enforced, and forwarded client/protocol/host metadata is ignored unless the direct peer belongs to an explicitly configured CIDR. Operators must never attach secrets, database URLs, backup contents, or raw environment dumps to issues; share only setting categories, safe request references, release identifiers, timestamps, and pass/fail results. See the [production configuration contract](docs/operations/production-configuration.md).

## Out of Scope

The following are out of scope unless they demonstrate a concrete security impact:
- Generic scanner output without reproduction.
- Social engineering.
- Denial-of-service testing.
- Physical attacks.
- Reports against third-party services not controlled by EchoEd.
