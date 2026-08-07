# Frontend Error Observability

Angular uses `DiagnosticService` as the privacy boundary for local diagnostics. It emits a stable event and sanitized operation plus numeric status and validated backend request ID. It never includes the raw error, URL/query, response body, headers, authorization state, forms, course graphs, learner data, filenames, or stack traces.

The HTTP diagnostic interceptor records unexpected transport/server failures. Existing authentication, permission, concealed-resource, validation, conflict, and rate-limit messages remain authoritative and accessible. A global `ErrorHandler` captures otherwise unhandled Angular failures. Lazy-chunk failures are classified before redirecting to the existing recovery page. A `WeakSet` prevents the same error object from being logged twice.

Unexpected `5xx` responses can append `Reference: <safe request ID>` to appropriate messages. Routine `401`, `403`, `404`, `409`, `422`, and `429` responses do not receive reference clutter. Course Studio preserves local work after autosave failure and shows the reference when available. No diagnostics are transmitted to a commercial vendor or new backend collection endpoint.
