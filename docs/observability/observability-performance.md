# Observability Performance

Date: 2026-08-07

## Method

Local measurements use the in-process FastAPI test client after warm-up. Five batches of 200 liveness requests compared metrics enabled with metrics disabled while request-completion output was suppressed in both cases. Seven batches of 2,000 Course Studio operational-event calls measured the bounded event/counter boundary with the logger disabled, isolating metric overhead. Two small batches of two missing-account login attempts measured the deliberately expensive constant-work authentication failure path; a larger initial sample exceeded the 120-second local command budget and was discarded. The existing Course Studio representative large-graph backend test remains the autosave regression guard.

## Results

| Scenario | Instrumentation enabled | Comparison | Observation |
| --- | ---: | ---: | --- |
| `GET /health/live`, median batch time per request | 3.525 ms | 5.092 ms with metrics disabled | Difference is within local TestClient/host noise; no measured regression |
| Course Studio event/counter, median per call | 0.03169 ms | 0.02526 ms with metrics disabled | Approximately 0.00643 ms incremental local cost |
| Missing-account login, median per request | 4102.850 ms | 4059.793 ms with metrics disabled | 43.057 ms / about 1.06%; sample is too small and password verification dominates |

Structured completion-log sink cost was intentionally excluded because it depends on the deployment’s stdout collector. Database readiness remains covered by full-suite functional tests, but a stable local A/B latency result was not claimed for it. No production-scale latency or throughput claim is made.

The instrumentation is constant work per request: context-variable set/reset, monotonic timing, lock-protected bounded counter updates, and one completion event when request logging is enabled. It does not serialize bodies or course graphs. Prometheus rendering takes the registry lock only when the protected endpoint is scraped.

These measurements are regression signals, not production-scale guarantees. SQLite, TestClient, developer logging, host load, and the process-local registry differ from production PostgreSQL and deployment collectors. Multi-process scrape aggregation and sustained concurrency require deployment-specific validation.
