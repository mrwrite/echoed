# Log Redaction Policy

Redaction is defense in depth. Call sites must omit sensitive data, and the shared formatter recursively protects nested mappings and collections. Keys containing authorization, cookie, password/passwd, secret, token, API key, or credential markers become `[REDACTED]`. Bearer/JWT-like strings are replaced, binary values become a byte-count marker, strings are bounded, and unknown objects are converted to bounded text.

Protected material includes authorization headers, cookies, JWTs, passwords and hashes, invitation/reset/verification tokens, API keys, raw query secrets, request bodies, uploaded binaries, caller filenames, assessment responses, learner records, and course/import content. Exception objects are not serialized into event fields. Server stack traces may be emitted only through controlled server logging and must never be returned to clients.

Regression tests cover nested secrets, token-like strings, binary values, safe JSON formatting, client error-body exclusion, and forbidden metric labels. New events must use stable categorical reason codes instead of free-form exception text.
