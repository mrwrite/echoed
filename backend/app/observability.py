from __future__ import annotations

from collections import defaultdict
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
import os
import re
from threading import Lock
import traceback
from typing import Any, Mapping


REDACTED = "[REDACTED]"
_SENSITIVE_KEY_PARTS = (
    "authorization",
    "cookie",
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "credential",
)
_BEARER_PATTERN = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+\-/]+=*")
_JWT_PATTERN = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_context: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def _boolean(name: str, default: bool, environ: Mapping[str, str]) -> bool:
    raw = environ.get(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be true or false")


def _positive_float(name: str, default: float, environ: Mapping[str, str]) -> float:
    raw = environ.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a positive number") from exc
    if value <= 0:
        raise RuntimeError(f"{name} must be a positive number")
    return value


@dataclass(frozen=True)
class ObservabilitySettings:
    environment: str
    log_level: str
    log_format: str
    request_logging: bool
    metrics_enabled: bool
    metrics_endpoint_enabled: bool
    metrics_access_token: str | None
    slow_request_threshold_ms: float
    correlation_header: str
    readiness_timeout_seconds: float


def load_settings(environ: Mapping[str, str] | None = None) -> ObservabilitySettings:
    values = os.environ if environ is None else environ
    level = values.get("LOG_LEVEL", "INFO").strip().upper()
    if level not in logging._nameToLevel or level == "NOTSET":
        raise RuntimeError("LOG_LEVEL must be a supported logging level")
    log_format = values.get("LOG_FORMAT", "developer").strip().lower()
    if log_format not in {"developer", "json"}:
        raise RuntimeError("LOG_FORMAT must be 'developer' or 'json'")
    endpoint_enabled = _boolean("METRICS_ENDPOINT_ENABLED", False, values)
    access_token = values.get("METRICS_ACCESS_TOKEN") or None
    if endpoint_enabled and not access_token:
        raise RuntimeError("METRICS_ACCESS_TOKEN is required when metrics export is enabled")
    header = values.get("CORRELATION_HEADER", "X-Correlation-ID").strip()
    if not re.fullmatch(r"[A-Za-z0-9-]{1,64}", header):
        raise RuntimeError("CORRELATION_HEADER must be a safe HTTP header name")
    return ObservabilitySettings(
        environment=values.get("APP_ENV", "development").strip() or "development",
        log_level=level,
        log_format=log_format,
        request_logging=_boolean("REQUEST_LOGGING_ENABLED", True, values),
        metrics_enabled=_boolean("METRICS_ENABLED", True, values),
        metrics_endpoint_enabled=endpoint_enabled,
        metrics_access_token=access_token,
        slow_request_threshold_ms=_positive_float("SLOW_REQUEST_THRESHOLD_MS", 1000.0, values),
        correlation_header=header,
        readiness_timeout_seconds=_positive_float("READINESS_TIMEOUT_SECONDS", 2.0, values),
    )


settings = load_settings()


def _sensitive_key(key: object) -> bool:
    normalized = str(key).strip().lower().replace("-", "_")
    return any(part in normalized for part in _SENSITIVE_KEY_PARTS)


def redact(value: Any, *, key: object | None = None) -> Any:
    if key is not None and _sensitive_key(key):
        return REDACTED
    if isinstance(value, Mapping):
        return {str(item_key): redact(item_value, key=item_key) for item_key, item_value in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [redact(item) for item in value]
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"
    if isinstance(value, str):
        return _JWT_PATTERN.sub(REDACTED, _BEARER_PATTERN.sub(REDACTED, value))[:1024]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:256]


class StructuredFormatter(logging.Formatter):
    def __init__(self, *, json_output: bool) -> None:
        super().__init__()
        self.json_output = json_output

    def format(self, record: logging.LogRecord) -> str:
        fields = redact(getattr(record, "event_fields", {}))
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": record.levelname.lower(),
            "event": getattr(record, "event_name", record.getMessage()),
            "message": redact(record.getMessage()),
            "service": "echoed-api",
            "component": getattr(record, "component", "application"),
            "environment": settings.environment,
            "request_id": request_id_context.get(),
            "correlation_id": correlation_id_context.get(),
            **fields,
        }
        if record.exc_info:
            exception_type = record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            payload["exception_type"] = exception_type
            payload["stack"] = [
                {"file": frame.filename[-160:], "line": frame.lineno, "function": frame.name[:80]}
                for frame in traceback.extract_tb(record.exc_info[2])[-12:]
            ]
        payload = {key: value for key, value in payload.items() if value is not None}
        if self.json_output:
            return json.dumps(payload, separators=(",", ":"), sort_keys=True)
        context = " ".join(f"{key}={value}" for key, value in payload.items() if key not in {"timestamp", "severity", "message"})
        return f"{payload['timestamp']} {payload['severity'].upper()} {payload['message']} {context}".rstrip()


def configure_logging() -> logging.Logger:
    application_logger = logging.getLogger("echoed")
    application_logger.setLevel(settings.log_level)
    if not any(getattr(handler, "_echoed_observability", False) for handler in application_logger.handlers):
        handler = logging.StreamHandler()
        handler._echoed_observability = True  # type: ignore[attr-defined]
        handler.setFormatter(StructuredFormatter(json_output=settings.log_format == "json"))
        application_logger.addHandler(handler)
    application_logger.propagate = True
    return application_logger


logger = configure_logging()


def emit_event(
    event_name: str,
    *,
    level: int = logging.INFO,
    message: str | None = None,
    component: str = "application",
    exc_info: bool | BaseException | tuple | None = None,
    **fields: Any,
) -> None:
    logger.log(
        level,
        message or event_name,
        extra={"event_name": event_name, "event_fields": redact(fields), "component": component},
        exc_info=exc_info,
    )


def _label_text(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")[:160]


class MetricRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: dict[tuple[str, tuple[tuple[str, str], ...]], float] = defaultdict(float)
        self._gauges: dict[tuple[str, tuple[tuple[str, str], ...]], float] = defaultdict(float)
        self._histograms: dict[tuple[str, tuple[tuple[str, str], ...]], tuple[int, float]] = {}

    @staticmethod
    def _key(name: str, labels: Mapping[str, object]) -> tuple[str, tuple[tuple[str, str], ...]]:
        if not re.fullmatch(r"[a-z][a-z0-9_:]*", name):
            raise ValueError("Metric names must be stable snake_case identifiers")
        forbidden = {"user_id", "course_id", "organization_id", "email", "filename", "username", "request_id"}
        if forbidden.intersection(labels):
            raise ValueError("Metric labels must not contain personal or high-cardinality identifiers")
        return name, tuple(sorted((str(key), str(value)[:160]) for key, value in labels.items()))

    def increment(self, name: str, amount: float = 1, **labels: object) -> None:
        if not settings.metrics_enabled:
            return
        key = self._key(name, labels)
        with self._lock:
            self._counters[key] += amount

    def gauge_add(self, name: str, amount: float, **labels: object) -> None:
        if not settings.metrics_enabled:
            return
        key = self._key(name, labels)
        with self._lock:
            self._gauges[key] += amount

    def observe(self, name: str, value: float, **labels: object) -> None:
        if not settings.metrics_enabled:
            return
        key = self._key(name, labels)
        with self._lock:
            count, total = self._histograms.get(key, (0, 0.0))
            self._histograms[key] = (count + 1, total + value)

    def clear(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()

    @staticmethod
    def _line(name: str, labels: tuple[tuple[str, str], ...], value: float | int) -> str:
        rendered = ",".join(f'{key}="{_label_text(label)}"' for key, label in labels)
        suffix = f"{{{rendered}}}" if rendered else ""
        return f"{name}{suffix} {value}"

    def render(self) -> str:
        with self._lock:
            lines = [self._line(name, labels, value) for (name, labels), value in sorted(self._counters.items())]
            lines.extend(self._line(name, labels, value) for (name, labels), value in sorted(self._gauges.items()))
            for (name, labels), (count, total) in sorted(self._histograms.items()):
                lines.append(self._line(f"{name}_count", labels, count))
                lines.append(self._line(f"{name}_sum", labels, round(total, 6)))
        return "\n".join(lines) + ("\n" if lines else "")


metrics = MetricRegistry()


def record_outcome(domain: str, operation: str, result: str) -> None:
    metrics.increment(f"echoed_{domain}_total", operation=operation, result=result)
