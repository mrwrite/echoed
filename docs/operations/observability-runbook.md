# Observability Runbook

This vendor-neutral runbook uses process logs, health endpoints, and the optional protected metrics endpoint. Adapt collection commands to the approved deployment without exposing credentials.

## Routine checks

1. Call `GET /health/live`; expect `200` and `status=alive`.
2. Call `GET /health/ready`; expect `200` and the database category marked available. A `503` means the instance should not receive database-backed traffic.
3. If metrics export is enabled, access `GET /internal/metrics` through the operator boundary with `X-Metrics-Token`. Never paste that token into a ticket or command transcript.
4. Inspect process stdout or the configured log collector. Filter by stable `event`, then by request ID. Do not search by passwords, tokens, learner content, or full request bodies.

## Correlating user-visible failures

Ask the user for the displayed reference ID, approximate time, action, and non-sensitive page name. Find the matching `request_id`, inspect `request.unhandled_exception` or domain events, then compare normalized-route status/duration metrics. Do not request authorization headers, cookies, passwords, invitation/reset links, uploaded files, assessment answers, lesson content, or screenshots containing student data.

## Common diagnosis

- Authorization: inspect `authorization.denied`, `echoed_authorization_denials_total`, and `echoed_request_denials_total`; confirm role/org category without probing protected target data.
- Rate limiting: inspect `rate_limit.triggered` and trigger counts by limiter group; verify environment limits and process-local deployment behavior.
- Database: inspect `database.operation_failed`, readiness, and database outcome/duration metrics. Logs intentionally omit SQL and connection details.
- Course Studio: correlate draft save/conflict/preview/review/publish events with the request reference. Confirm local work remained dirty after autosave failure before asking the author to retry.
- Uploads: inspect upload category/outcome/duration and rejection reason code. Never collect the binary or caller filename solely for diagnostics.

## Changing verbosity safely

Change `LOG_LEVEL` to a supported level and, for production collection, prefer `LOG_FORMAT=json`. Restart/redeploy through the normal operator process because settings load at startup. Never enable SQL echo, raw-body logging, or secret-bearing headers. Record the time and reason, reproduce only as long as necessary, then restore the prior level and restart. Confirm health/readiness and that logs remain redacted.

Release, migration, shutdown, backup/restore, and recovery decisions are governed by the [Phase 11 deployment runbook](deployment-runbook.md) and [backup/restore procedure](backup-and-restore.md). Observability indicates state; it does not replace those operational gates.
