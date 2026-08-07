# Health and Graceful Shutdown

| Endpoint/signal | Use | Behavior |
| --- | --- | --- |
| `/health/live` | Process liveness/restart | Returns only `{"status":"live"}` and never probes PostgreSQL. |
| `/health/ready` | Traffic admission, deployment verification, dependency outage | Runs bounded `SELECT 1`; returns 503 and generic database unavailable state on failure. |
| `/internal/metrics` | Authorized monitoring | Disabled by default; token-protected when enabled. Never use as a public health check. |

Neither health response exposes hosts, database names, credentials, SQL, versions, or topology. During termination, Uvicorn stops accepting work and waits up to `GRACEFUL_SHUTDOWN_SECONDS`; the FastAPI lifespan emits bounded lifecycle events and disposes the SQLAlchemy engine. The orchestrator stop grace must exceed the Uvicorn bound (Compose uses 35 vs 30 seconds). If the process exceeds the bound, termination is forced and the event is an incident signal.

There is no worker/job framework to drain. Any future worker must define lease, retry, idempotency, and shutdown semantics separately.
