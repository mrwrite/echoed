from dataclasses import replace
import json
import logging
import uuid

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.exc import OperationalError

from app import main
from app.api.routes import courses
from app.main import app
from app.observability import (
    MetricRegistry,
    StructuredFormatter,
    load_settings,
    metrics,
    redact,
)


client = TestClient(app, raise_server_exceptions=False)


def test_observability_settings_validate_environment_configuration():
    configured = load_settings(
        {
            "APP_ENV": "production",
            "LOG_LEVEL": "WARNING",
            "LOG_FORMAT": "json",
            "METRICS_ENABLED": "true",
            "METRICS_ENDPOINT_ENABLED": "true",
            "METRICS_ACCESS_TOKEN": "operator-secret",
            "SLOW_REQUEST_THRESHOLD_MS": "250",
            "CORRELATION_HEADER": "X-EchoEd-Correlation",
            "READINESS_TIMEOUT_SECONDS": "1.5",
        }
    )

    assert configured.environment == "production"
    assert configured.log_format == "json"
    assert configured.metrics_endpoint_enabled is True
    assert configured.correlation_header == "X-EchoEd-Correlation"
    assert configured.readiness_timeout_seconds == 1.5

    with pytest.raises(RuntimeError):
        load_settings({"LOG_LEVEL": "LOUD"})
    with pytest.raises(RuntimeError):
        load_settings({"METRICS_ENDPOINT_ENABLED": "true"})
    with pytest.raises(RuntimeError):
        load_settings({"REQUEST_LOGGING_ENABLED": "sometimes"})


def test_log_redaction_handles_nested_headers_tokens_and_binary_content():
    jwt_value = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJzdHVkZW50In0.signature"
    result = redact(
        {
            "authorization": f"Bearer {jwt_value}",
            "nested": {"password": "secret", "safe": f"prefix {jwt_value}"},
            "content": b"private upload bytes",
        }
    )

    assert result["authorization"] == "[REDACTED]"
    assert result["nested"]["password"] == "[REDACTED]"
    assert jwt_value not in result["nested"]["safe"]
    assert result["content"].startswith("<bytes:")


def test_json_formatter_emits_structured_fields_without_secret_values():
    record = logging.LogRecord("echoed", logging.INFO, __file__, 1, "auth.login.failed", (), None)
    record.event_name = "auth.login.failed"
    record.component = "authentication"
    record.event_fields = {"result": "denied", "token": "top-secret"}

    payload = json.loads(StructuredFormatter(json_output=True).format(record))

    assert payload["event"] == "auth.login.failed"
    assert payload["component"] == "authentication"
    assert payload["result"] == "denied"
    assert payload["token"] == "[REDACTED]"


def test_request_id_and_separate_correlation_header_are_returned_and_sanitized():
    response = client.get(
        "/health/live",
        headers={"X-Request-ID": "support-request", "X-Correlation-ID": "support-case-42"},
    )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "support-request"
    assert response.headers["x-correlation-id"] == "support-case-42"

    invalid = client.get("/health/live", headers={"X-Request-ID": "bad value", "X-Correlation-ID": "x" * 200})
    uuid.UUID(invalid.headers["x-request-id"])
    assert "x-correlation-id" not in invalid.headers


def test_http_metrics_use_normalized_routes_and_forbid_personal_labels():
    metrics.clear()
    response = client.get(f"/api/users/{uuid.uuid4()}")

    assert response.status_code == 401
    exported = metrics.render()
    assert '/api/users/{user_id}' in exported
    assert str(response.request.url).split("/")[-1] not in exported

    registry = MetricRegistry()
    with pytest.raises(ValueError):
        registry.increment("echoed_bad_metric_total", user_id="user-1")


def test_route_template_preserves_nested_router_prefix_across_starlette_versions():
    from types import SimpleNamespace

    from fastapi import Request

    request = Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": "/api/users/example",
            "raw_path": b"/api/users/example",
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "root_path": "/api",
            "route": SimpleNamespace(path="/users/{user_id}"),
        }
    )

    assert main._route_template(request) == "/api/users/{user_id}"


def test_route_template_recovers_prefix_when_nested_root_path_is_empty():
    from types import SimpleNamespace

    from fastapi import Request

    user_id = uuid.uuid4()
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": f"/api/users/{user_id}",
            "raw_path": f"/api/users/{user_id}".encode(),
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
            "root_path": "",
            "path_params": {"user_id": user_id},
            "route": SimpleNamespace(path="/users/{user_id}"),
        }
    )

    template = main._route_template(request)
    assert template == "/api/users/{user_id}"
    assert str(user_id) not in template


def test_metrics_endpoint_is_concealed_then_token_protected(monkeypatch):
    metrics.clear()
    metrics.increment("echoed_test_total", result="success")

    assert client.get("/internal/metrics").status_code == 404

    monkeypatch.setattr(
        main,
        "settings",
        replace(main.settings, metrics_endpoint_enabled=True, metrics_access_token="metrics-secret"),
    )
    assert client.get("/internal/metrics").status_code == 403
    response = client.get("/internal/metrics", headers={"X-Metrics-Token": "metrics-secret"})
    assert response.status_code == 200
    assert "echoed_test_total" in response.text
    assert "metrics-secret" not in response.text


def test_liveness_does_not_depend_on_database_and_readiness_failure_is_safe(monkeypatch):
    class BrokenEngine:
        def connect(self):
            raise OperationalError("SELECT secret", {"password": "private"}, Exception("database host"))

    monkeypatch.setattr(main, "engine", BrokenEngine())

    live = client.get("/health/live")
    ready = client.get("/health/ready")

    assert live.status_code == 200
    assert live.json() == {"status": "live"}
    assert ready.status_code == 503
    assert ready.json() == {"status": "not_ready", "dependencies": {"database": "unavailable"}}
    assert "secret" not in ready.text
    assert "host" not in ready.text


def test_unhandled_exception_returns_safe_support_reference():
    path = f"/api/testing/unhandled-{uuid.uuid4().hex}"

    def fail():
        raise RuntimeError("internal database password=do-not-return")

    app.add_api_route(path, fail, methods=["GET"])
    response = client.get(path)

    assert response.status_code == 500
    assert response.json()["detail"] == "Something went wrong."
    assert response.json()["request_id"] == response.headers["x-request-id"]
    assert "password" not in response.text


def test_authentication_and_course_studio_metrics_have_bounded_labels(caplog):
    metrics.clear()
    response = client.post("/api/auth/token", data={"username": "missing-user", "password": "private"})
    assert response.status_code == 401

    actor = type("Actor", (), {"id": uuid.uuid4(), "role": "content_admin"})()
    course_id = uuid.uuid4()
    with caplog.at_level(logging.INFO, logger="echoed"):
        courses._course_studio_event("draft_save", "conflict", actor=actor, course_id=course_id, reason="revision_conflict")

    exported = metrics.render()
    assert 'operation="login"' in exported
    assert 'operation="draft_save"' in exported
    assert str(course_id) not in exported
    assert "private" not in caplog.text
