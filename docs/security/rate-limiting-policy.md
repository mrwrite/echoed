# Rate-Limiting Policy

All limits use the central fixed-window implementation in `app.rate_limit`; values are configurable with `RATE_LIMIT_<GROUP>_LIMIT` and `RATE_LIMIT_<GROUP>_WINDOW_SECONDS`.

| Group / protected endpoints | Default | Key | Failure |
| --- | ---: | --- | --- |
| `auth_login` `/auth/token` | 10 / 60 s | direct peer + normalized account identifier | generic 429 + `Retry-After` |
| `auth_register` `/auth/register` | 5 / 3600 s | direct peer + normalized username | 429 + retry metadata |
| `invite_accept` `/invites/accept` | 10 / 300 s | authenticated user ID | generic invitation/rate response |
| `invite_manage` create invite | 10 / 60 s | authenticated user ID | 429 |
| `upload` all three image uploads | 20 / 60 s | authenticated user ID | 429 before file storage |
| `forum_mutation` thread/post writes | 30 / 60 s | authenticated user ID | 429 before mutation |
| `user_management` role/delete | 20 / 60 s | authenticated user ID | 429 before mutation |

The store is locked process memory. The checked-in deployment starts one Uvicorn process, so this is effective for that topology and resets on restart. It is not distributed across workers/hosts; a shared non-commercial store is mandatory before scaling. Limit evaluation for protected writes is fail-closed because configuration errors raise at evaluation rather than silently disabling the control.

Only the direct socket peer is used. `X-Forwarded-For` and similar headers are ignored because trusted proxies are not configured. Behind a reverse proxy, authenticated routes remain keyed per user; anonymous account+peer keys can group callers behind the proxy but resist spoofing. Configure trusted proxy handling and a shared store together in future deployment work.

Tests cover independent keys, exact 429, `Retry-After`, reset after a window, environment overrides, authentication abuse, and upload abuse. Playwright does not use timing-heavy limiter loops.
