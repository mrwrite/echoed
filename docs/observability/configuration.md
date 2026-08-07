# Observability Configuration

Settings are provider-neutral environment variables loaded and validated at API startup.

| Variable | Default | Contract |
| --- | --- | --- |
| `APP_ENV` | `development` | Environment field on structured events |
| `LOG_LEVEL` | `INFO` | Standard Python level; invalid values fail startup |
| `LOG_FORMAT` | `developer` | `developer` or `json` |
| `REQUEST_LOGGING_ENABLED` | `true` | Emits one completion event per request |
| `METRICS_ENABLED` | `true` | Collects bounded process-local metrics |
| `METRICS_ENDPOINT_ENABLED` | `false` | Conceals export unless explicitly enabled |
| `METRICS_ACCESS_TOKEN` | unset | Required when metrics export is enabled; never logged |
| `SLOW_REQUEST_THRESHOLD_MS` | `1000` | Positive duration for `request.slow` |
| `READINESS_TIMEOUT_SECONDS` | `2` | Positive database readiness bound |
| `CORRELATION_HEADER` | `X-Correlation-ID` | Safe 1–64 character HTTP header name |

Boolean values accept true/false, 1/0, yes/no, or on/off. Invalid booleans, formats, levels, positive durations, header names, or an enabled metrics endpoint without a token fail visibly at startup. Production should use JSON logs and an operator-managed metrics token/endpoint boundary. Basic diagnostics do not depend on a secret, and no setting is tied to a hosting provider.
