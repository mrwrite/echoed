# Structured Logging Policy

Backend application events use the `echoed` logger and `emit_event()` from `backend/app/observability.py`. Production can select JSON; development can use readable key/value output. Stable event names are the aggregation contract.

Common fields are timestamp, severity, event, message, service, component, environment, request ID, correlation ID, normalized route, method, status, duration, actor classification/role where appropriate, resource type, operation, and result. Actor or resource identifiers may be present only in restricted logs when operationally necessary; they are never metric labels.

Canonical categories include `request.completed`, `request.slow`, `request.validation_failed`, `request.unhandled_exception`, `database.operation_failed`, `auth.login.succeeded`, `auth.login.failed`, `authorization.denied`, `rate_limit.triggered`, `upload.rejected`, and `course_studio.<operation>.<result>`.

Never log credentials, authorization/cookie headers, JWTs, reset/invitation secrets, raw bodies, uploaded bytes or caller filenames, course graphs, lesson or assessment content, or unnecessary personal/student data. Do not enable SQL echo or bound-parameter logging in production. The formatter recursively redacts sensitive keys and token-like strings, and truncates unexpected values. Domain code should still omit sensitive data at the source.

One layer owns each event: middleware owns HTTP completion/unhandled failures, dependencies own authorization denials, route boundaries own domain outcomes, and database session boundaries own transaction failure. Operational logs are not durable audit evidence.

Environment controls and startup validation are canonical in [configuration.md](configuration.md).
