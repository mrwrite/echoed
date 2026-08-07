## Why

EchoEd now has mature security boundaries and a major Course Studio workflow, but operators still lack consistent structured diagnostics, vendor-neutral metrics, safe frontend/backend correlation, and actionable runbooks. This focused change establishes privacy-conscious platform observability without substituting for authorization, inventing production infrastructure, or building the separate durable audit-event product.

## What Changes

- Standardize environment-configurable structured backend logging with stable event names, centralized redaction, request/correlation context, and safe exception categories.
- Instrument HTTP traffic, authentication, authorization, rate limiting, uploads, database failures, and supported Course Studio lifecycle operations without logging bodies, secrets, learner content, or high-cardinality metric labels.
- Preserve server-generated request IDs, safely accept bounded correlation hints, return diagnostic identifiers, and make unexpected frontend errors referenceable without exposing exception details.
- Clarify bounded liveness, readiness, and dependency checks and introduce a protected vendor-neutral metrics export.
- Add safe Angular diagnostic handling for HTTP failures, lazy chunks, Course Studio autosave/publish errors, and backend reference IDs while preserving accessible user messaging.
- Document current architecture, logging/redaction/metrics policies, database and Course Studio signals, background-work reality, measured local overhead, operator workflows, incident guidance, and the explicit boundary for `implement-platform-audit-events`.
- Preserve existing supported learner, teacher, Studio, organization, platform-administration, public, authentication, onboarding, and Phase 8 security behavior.

## Capabilities

### New Capabilities

- `platform-observability`: Structured logging, request correlation, HTTP/error/database instrumentation, health/readiness, vendor-neutral metrics, frontend diagnostic correlation, privacy controls, and operational guidance.

### Modified Capabilities

- `auth-org-session-authority`: Authentication, authorization, and rate-limit outcomes gain privacy-safe operational signals while existing authority and organization-scope behavior remains unchanged.

## Impact

- Backend: FastAPI middleware/exception handling, logging, metrics, health/readiness, database session diagnostics, Phase 8 security events, uploads, authentication, authorization dependencies, and Course Studio routes/services.
- Frontend: Angular HTTP interception, global error handling, lazy-load diagnostics, safe reference-ID presentation, and Course Studio failure diagnostics.
- Operations/docs/tests: new observability and incident documentation plus backend, Angular, and stable Playwright regressions.
- Dependencies: no commercial monitoring vendor; prefer standard-library/vendor-neutral implementation and add no dependency unless repository constraints prove it necessary.
- Non-goals: durable audit persistence, SIEM, distributed tracing infrastructure, new cloud architecture, business/learner analytics, distributed rate limiting, authentication replacement, and unrelated product capability work.
