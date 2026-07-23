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

The focused [Phase 7 security baseline](docs/platform-maturity/security-baseline.md) records repository evidence, severity, narrow remediations, and deferred security work. Phase 7 adds privacy-safe authentication logging, authenticated diagnostic access, active organization-membership enforcement, bounded image-upload validation, request correlation, baseline response headers, and patched Angular runtime packages. It is not a penetration test.

The unauthenticated forum mutation boundary, administrative response minimization, rate limiting, comprehensive audit events, and production security policy remain explicit future work. Do not use the current demo with real learner or production data.

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

## Out of Scope

The following are out of scope unless they demonstrate a concrete security impact:
- Generic scanner output without reproduction.
- Social engineering.
- Denial-of-service testing.
- Physical attacks.
- Reports against third-party services not controlled by EchoEd.
