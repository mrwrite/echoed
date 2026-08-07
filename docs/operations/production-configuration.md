# Production Configuration Contract

Run from `backend` before migration or startup:

```text
python -m scripts.validate_operational_config
```

`APP_ENV=production` prevents dotenv loading and fails closed. Validation messages name categories, never values.

| Setting | Production contract |
| --- | --- |
| `APP_ENV` | Exactly `production` (other allowed identities: development, test, staging). |
| `DATABASE_URL` | Explicit PostgreSQL URL; placeholder/default credentials and SQLite are rejected. |
| `JWT_SECRET` | Explicit, at least 32 characters, and not a known development value. |
| `ALLOWED_HOSTS` | Explicit DNS/IP hosts; `*`, localhost, and malformed values are rejected. |
| `FRONTEND_URL` | One or more credential-free HTTPS origins. |
| `EXTERNAL_BASE_URL` | Credential-free HTTPS API origin. |
| `TRUST_PROXY_HEADERS` / `TRUSTED_PROXY_IPS` | Disabled by default. Enabling requires explicit peer IP/CIDR entries. Configuring peers without enabling trust is rejected. |
| `STORYBOOK_PATH`, `COLORINGS_PATH`, `BADGES_PATH` | Absolute, distinct persistent paths. |
| `PERSISTENT_STORAGE_ACKNOWLEDGED` | Must be `true`, confirming those paths outlive the process/container. |
| `AUTO_MIGRATE_ON_STARTUP` | Must be false. Migrations are a separate release step. |
| `RELEASE_VERSION`, `DEPLOYMENT_ID` | Explicit immutable artifact version and environment-specific deployment identity. |
| `LOG_FORMAT` | `json`. |
| `METRICS_ENABLED`, `REQUEST_LOGGING_ENABLED` | Both true. |
| `METRICS_ENDPOINT_ENABLED` / `METRICS_ACCESS_TOKEN` | Endpoint may remain disabled; enabling requires a secret token. |
| `GRACEFUL_SHUTDOWN_SECONDS` | Positive integer; default 30. |

Production must supply values through its secret/configuration mechanism. Do not copy `.env`; do not use Compose defaults. A configuration can pass syntax validation without proving DNS, certificates, storage durability, or database capacity, so deployment preflight still applies.

Trusted network topology: the direct listener receives traffic either directly, with proxy trust off, or from only the CIDRs in `TRUSTED_PROXY_IPS`. Uvicorn starts with `--no-proxy-headers`; application code considers the first valid forwarded client/protocol/host only when the direct peer is trusted. Host validation remains independent and always enforced. The selected reverse proxy must overwrite, not append untrusted inbound forwarding headers.
