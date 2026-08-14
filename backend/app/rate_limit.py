from __future__ import annotations

from dataclasses import dataclass
import os
from threading import Lock
import time
from typing import Final

from fastapi import HTTPException, Request, status

from app.security import security_event
from app.observability import metrics


@dataclass(frozen=True)
class RateLimitPolicy:
    limit: int
    window_seconds: int


_DEFAULTS: Final[dict[str, RateLimitPolicy]] = {
    "auth_login": RateLimitPolicy(10, 60),
    "auth_register": RateLimitPolicy(5, 3600),
    "invite_accept": RateLimitPolicy(10, 300),
    "invite_manage": RateLimitPolicy(10, 60),
    "upload": RateLimitPolicy(20, 60),
    "forum_mutation": RateLimitPolicy(30, 60),
    "user_management": RateLimitPolicy(20, 60),
    "audit_export": RateLimitPolicy(5, 300),
}


def _positive_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a positive integer") from exc
    if value <= 0:
        raise RuntimeError(f"{name} must be a positive integer")
    return value


def get_policy(group: str) -> RateLimitPolicy:
    default = _DEFAULTS.get(group)
    if default is None:
        raise RuntimeError(f"Unknown rate-limit group: {group}")
    env_prefix = f"RATE_LIMIT_{group.upper()}"
    return RateLimitPolicy(
        limit=_positive_env(f"{env_prefix}_LIMIT", default.limit),
        window_seconds=_positive_env(f"{env_prefix}_WINDOW_SECONDS", default.window_seconds),
    )


class FixedWindowRateLimiter:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], tuple[int, int]] = {}
        self._lock = Lock()

    def check(self, group: str, key: str, *, now: float | None = None) -> int | None:
        policy = get_policy(group)
        current = int(time.time() if now is None else now)
        window_start = current - (current % policy.window_seconds)
        storage_key = (group, key)
        with self._lock:
            stored_window, count = self._entries.get(storage_key, (window_start, 0))
            if stored_window != window_start:
                stored_window, count = window_start, 0
            if count >= policy.limit:
                return max(1, stored_window + policy.window_seconds - current)
            self._entries[storage_key] = (stored_window, count + 1)
        return None

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


limiter = FixedWindowRateLimiter()


def direct_peer_key(request: Request) -> str:
    # Forwarded headers are deliberately ignored until trusted proxies are configured.
    return getattr(request.state, "client_ip", None) or (request.client.host if request.client else "unknown-peer")


def enforce_rate_limit(
    request: Request,
    group: str,
    *,
    actor_id: object | None = None,
    account_identifier: str | None = None,
) -> None:
    peer = direct_peer_key(request)
    if actor_id is not None:
        key = f"user:{actor_id}"
    elif account_identifier:
        key = f"peer:{peer}:account:{account_identifier.strip().lower()}"
    else:
        key = f"peer:{peer}"
    retry_after = limiter.check(group, key)
    if retry_after is None:
        return
    metrics.increment("echoed_rate_limit_triggers_total", group=group)
    security_event(
        action="rate_limit",
        result="denied",
        actor_id=actor_id,
        target_type="endpoint_group",
        target_id=group,
        reason="limit_exceeded",
        request_id=getattr(request.state, "request_id", None),
    )
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many requests. Please try again later.",
        headers={"Retry-After": str(retry_after)},
    )
