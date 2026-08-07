# Health, Liveness, and Readiness Policy

| Endpoint | Meaning | Dependency behavior | Exposure |
| --- | --- | --- | --- |
| `GET /health/live` | The API process can answer HTTP | Does not query the database | Minimal public machine-readable `{"status":"live"}` |
| `GET /health/ready` | The instance can safely serve database-backed traffic | Executes bounded `SELECT 1`; returns `503` on SQLAlchemy failure | Minimal dependency category/status; no host, database name, version, SQL, credentials, or exception |

Liveness must remain healthy during a temporary database outage so an orchestrator does not confuse dependency failure with a dead process. Readiness may remove an unhealthy instance from service. The query is constant-cost, does not scan application tables, and is bounded by `READINESS_TIMEOUT_SECONDS` (default 2 seconds). No hosting-specific health topology is assumed.

Required storage is local filesystem-backed for existing uploads and has no separately configured remote dependency to probe. No worker service exists. If either becomes mandatory infrastructure, readiness must add a bounded, non-disclosing check before claiming coverage.
