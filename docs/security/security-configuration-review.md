# Security Configuration and Dependency Review

| Area | Evidence / decision |
| --- | --- |
| Authentication | bcrypt plus `python-jose` HS256; mandatory `JWT_SECRET`; 120-minute bearer; no refresh/revocation/MFA (deferred) |
| Passwords | bcrypt direct API; no plaintext/token logging; 72-byte bcrypt behavior remains documented |
| Multipart/uploads | existing `python-multipart`; no new dependency; bounded raster structural validation |
| Rate limiting | standard-library locked memory; environment-configurable; no commercial/new package; single-process limitation documented |
| Proxy | forwarding headers ignored; direct peer only; no implicit trust of spoofable headers |
| CORS/hosts | explicit configured origins; all methods/headers with credentials retained for client compatibility; TrustedHost middleware not configured |
| Headers | `nosniff`, `DENY` frame policy, `no-referrer`, request ID; HSTS/CSP remain serving-edge work |
| Cookies/session | bearer Authorization token, not auth cookie; CSRF risk changes if cookies are introduced |
| Environment | `JWT_SECRET` fails fast; rate-limit numeric overrides fail on invalid/non-positive values when evaluated; local CORS defaults must not be production defaults |
| Debug/OpenAPI | FastAPI debug is not enabled by code; OpenAPI remains exposed for current developer/evaluation use |
| Test bypasses | dependency overrides and test JWT secret stay in test code; shared demo credentials are explicitly non-production |
| Logging | privacy-safe request/security events; no durable audit store |
| Dependencies | no backend dependency added/removed/upgraded; Angular runtime/compiler packages moved narrowly from 20.3.25 to 20.3.27 to remediate the production dependency advisories found during verification; the lockfile was regenerated/normalized |

Production must supply a strong rotated secret, explicit `FRONTEND_URL`, single API process until shared rate limiting exists, TLS/HSTS at the edge, restricted deployment access, and non-demo credentials/data. A future deployment-hardening change should validate production-mode defaults, trusted hosts/proxies, OpenAPI policy, CSP/HSTS, secret rotation, backups, and distributed rate limiting.

`npm audit --omit=dev` reports zero production vulnerabilities after the Angular patch. The full audit still reports 31 development-tool findings (3 low, 7 moderate, 19 high, 2 critical), primarily through Angular CLI/build-server, Karma, archive, proxy, and bundler dependencies. They are not shipped in the production browser bundle, but local/CI tools must not process untrusted projects or expose development servers. Remediation is deferred to a bounded toolchain dependency change because the available fixes update a broad transitive build tree and are outside this focused runtime-boundary phase.
