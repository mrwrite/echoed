# Database Observability

Database session providers catch `SQLAlchemyError`, roll back the active transaction, increment a bounded operation/failure counter, and emit `database.operation_failed`. Readiness records success/failure and elapsed time. Unexpected database exceptions still reach the request-level safe exception boundary with the same request ID.

The policy deliberately excludes SQL statements, bound parameters, connection URLs, database names, credentials, and model serialization. SQLAlchemy echo remains disabled. Current coverage identifies session, authorization-session, authentication-session, and readiness boundaries; it does not provide per-query tracing, pool-exhaustion gauges, deadlock classification, or migration-state inspection because the current stack does not expose those safely through an existing instrumentation layer.

Operators should correlate `database.operation_failed` with readiness `503` responses and request references. A future production topology may add driver/pool metrics through a vendor-neutral adapter, but must retain the no-values/no-personal-data contract.
