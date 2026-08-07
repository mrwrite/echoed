# Security Error Response Policy

- `401 Unauthorized`: missing, expired, invalid bearer token or invalid login credentials. Authentication messages are generic.
- `403 Forbidden`: authenticated actor is known but an explicit role/capability/ownership policy denies the action. Target detail is minimized.
- `404 Not Found`: absent resource or deliberate concealment of cross-organization, parent-mismatch, learner-record, or inactive-membership targets.
- `409 Conflict`: action is structurally valid but violates administrator safety or invitation lifecycle state.
- `422 Unprocessable Entity`: Pydantic validation, forbidden extra/mass-assignment fields, or unsupported role value.
- `429 Too Many Requests`: central limiter denial with integer `Retry-After` seconds and a generic safe message.

Denied operations never return success, stack traces, SQL, password hashes, tokens, or internal exception text. FastAPI validation details may identify rejected field names but not stored target data. Legitimate administrators receive actionable final-admin/self-action messages. Angular maps these statuses to safe accessible text; only deliberate 409/422 backend detail strings are displayed.
