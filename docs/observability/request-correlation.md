# Request Correlation

Every response carries `X-Request-ID`. The API accepts an existing request ID only when it is 1–128 characters from the safe identifier alphabet; otherwise it generates a UUID. This preserves safe upstream correlation without trusting arbitrary caller text.

`X-Correlation-ID` is separate and configurable with `CORRELATION_HEADER`. A supplied value is accepted only when bounded to 64 safe characters. It is a diagnostic hint, not authentication, authorization, or a distributed trace ID. Both values are stored on request state and context variables, included in structured events, returned in response headers when present, and reset after the request.

The repository has no internal HTTP client or executing request-spawned worker today. A future client or worker should explicitly copy correlation context, generate its own operation/request ID, and avoid placing IDs in metric labels. Support staff may ask users for a displayed request reference; they must never ask for tokens, cookies, passwords, or course/learner content.
