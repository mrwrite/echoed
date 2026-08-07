# Background Work Observability

EchoEd currently has no Celery, RQ, scheduler, message broker, executing generation worker, or application-managed retry queue. `GenerationRun` rows with a `queued` status are product metadata, not evidence of an active worker architecture. Phase 10 therefore does not invent a queue or report queue depth.

Any future worker must emit stable start/success/failure/duration/retry/permanent-failure events, use bounded operation/resource-type metric labels, propagate a sanitized correlation ID from the initiating request where available, generate its own execution ID, and exclude payload bodies, generated content, learner data, secrets, and filenames. Worker lifecycle persistence is distinct from the durable security audit ledger.
