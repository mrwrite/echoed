import asyncio
from contextlib import asynccontextmanager
import os
import re
import secrets
import time
import uuid

from app.operational_config import load_operational_settings

operational_settings = load_operational_settings()

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import (
    activities,
    analytics,
    assessments,
    assignments,
    auth,
    badges,
    certifications,
    courses,
    enroll,
    invites,
    lesson_sessions,
    lessons,
    orgs,
    posts,
    preferences,
    programs,
    progress,
    sections,
    start_course,
    threads,
    units,
    uploads,
    users,
    meta,
    v2_platform,
)
from app.database import engine
from app.network_trust import resolve_network_context
from app.observability import (
    correlation_id_context,
    emit_event,
    metrics,
    request_id_context,
    settings,
)

@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.accepting_requests = True
    emit_event(
        "application.started",
        component="lifecycle",
        environment=operational_settings.environment,
        release_version=operational_settings.release_version,
        deployment_id=operational_settings.deployment_id,
        result="success",
    )
    try:
        yield
    finally:
        application.state.accepting_requests = False
        emit_event("application.shutdown.started", component="lifecycle", result="started")
        await run_in_threadpool(engine.dispose)
        emit_event("application.shutdown.completed", component="lifecycle", result="success")


app = FastAPI(lifespan=lifespan)

STORYBOOK_PATH = str(operational_settings.storybook_path)
COLORINGS_PATH = str(operational_settings.colorings_path)
BADGES_PATH = str(operational_settings.badges_path)

os.makedirs(STORYBOOK_PATH, exist_ok=True)
os.makedirs(COLORINGS_PATH, exist_ok=True)
os.makedirs(BADGES_PATH, exist_ok=True)

app.mount("/storybook", StaticFiles(directory=STORYBOOK_PATH), name="storybook")
app.mount("/colorings", StaticFiles(directory=COLORINGS_PATH), name="colorings")
app.mount("/badges", StaticFiles(directory=BADGES_PATH), name="badges")


def _parse_allowed_origins(raw_origins: str) -> list[str]:
    return [
        origin.strip().rstrip("/")
        for origin in raw_origins.split(",")
        if origin.strip()
    ]


allowed_origins = list(operational_settings.allowed_origins)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(operational_settings.allowed_hosts))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
CORRELATION_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")


def _safe_incoming(value: str, pattern: re.Pattern[str]) -> str | None:
    return value if pattern.fullmatch(value) else None


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else "unmatched"


@app.middleware("http")
async def add_operational_context(request: Request, call_next):
    incoming_request_id = request.headers.get("X-Request-ID", "")
    request_id = _safe_incoming(incoming_request_id, REQUEST_ID_PATTERN) or str(uuid.uuid4())
    incoming_correlation_id = request.headers.get(settings.correlation_header, "")
    correlation_id = _safe_incoming(incoming_correlation_id, CORRELATION_ID_PATTERN)
    started_at = time.perf_counter()
    request.state.request_id = request_id
    request.state.correlation_id = correlation_id
    request.state.actor_class = "anonymous"
    network_context = resolve_network_context(request, operational_settings)
    request.state.client_ip = network_context.client_ip
    request.state.authoritative_scheme = network_context.scheme
    request.state.authoritative_host = network_context.host
    request.state.proxy_trusted = network_context.proxy_trusted
    request_token = request_id_context.set(request_id)
    correlation_token = correlation_id_context.set(correlation_id)
    metrics.gauge_add("echoed_http_active_requests", 1)

    try:
        response = await call_next(request)
    except Exception as exc:
        emit_event(
            "request.unhandled_exception",
            level=40,
            component="http",
            message="Unexpected request failure",
            exc_info=exc,
            method=request.method,
            route=_route_template(request),
            result="error",
        )
        metrics.increment("echoed_request_failures_total", category="unhandled_exception")
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Something went wrong.", "request_id": request_id},
        )
    finally:
        metrics.gauge_add("echoed_http_active_requests", -1)

    try:
        duration_ms = (time.perf_counter() - started_at) * 1000
        route = _route_template(request)
        status_family = f"{response.status_code // 100}xx"
        metrics.increment("echoed_http_requests_total", method=request.method, route=route, status_family=status_family)
        metrics.observe("echoed_http_request_duration_ms", duration_ms, method=request.method, route=route)
        if response.status_code in {401, 403}:
            category = "authentication" if response.status_code == 401 else "authorization"
            metrics.increment("echoed_request_denials_total", category=category, route=route)
            emit_event(
                "authorization.denied" if response.status_code == 403 else "authentication.required",
                component="http",
                method=request.method,
                route=route,
                status=response.status_code,
                actor_class=request.state.actor_class,
                result="denied",
            )
        elif response.status_code == 422:
            metrics.increment("echoed_request_failures_total", category="validation")
            emit_event("request.validation_failed", component="http", method=request.method, route=route, result="denied")
        if settings.request_logging:
            emit_event(
                "request.completed",
                component="http",
                method=request.method,
                route=route,
                status=response.status_code,
                duration_ms=round(duration_ms, 2),
                actor_class=request.state.actor_class,
                organization_context=bool(request.headers.get("X-Org-Id")),
                result="success" if response.status_code < 400 else "failure",
            )
        if duration_ms >= settings.slow_request_threshold_ms:
            emit_event(
                "request.slow",
                level=30,
                component="http",
                method=request.method,
                route=route,
                duration_ms=round(duration_ms, 2),
            )
        response.headers["X-Request-ID"] = request_id
        if correlation_id:
            response.headers[settings.correlation_header] = correlation_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response
    finally:
        request_id_context.reset(request_token)
        correlation_id_context.reset(correlation_token)

app.include_router(progress.router, prefix="/api", tags=["Progress"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(enroll.router, prefix="/api", tags=["Enrollment"])
app.include_router(start_course.router, prefix="/api", tags=["Start Course"])
app.include_router(badges.router, prefix="/api", tags=["Badges"])
app.include_router(units.router, prefix="/api", tags=["Units"])
app.include_router(lessons.router, prefix="/api", tags=["Lessons"])
app.include_router(activities.router, prefix="/api", tags=["Activities"])
app.include_router(programs.router, prefix="/api", tags=["Programs"])
app.include_router(assessments.router, prefix="/api", tags=["Assessments"])
app.include_router(certifications.router, prefix="/api", tags=["Certifications"])
app.include_router(threads.router, prefix="/api/forum", tags=["Threads"])
app.include_router(posts.router, prefix="/api/forum", tags=["Posts"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(courses.router, prefix="/api", tags=["Courses"])
app.include_router(orgs.router, prefix="/api", tags=["Organizations"])
app.include_router(invites.router, prefix="/api", tags=["Invites"])
app.include_router(preferences.router, prefix="/api", tags=["Preferences"])
app.include_router(sections.router, prefix="/api", tags=["Sections"])
app.include_router(lesson_sessions.router, prefix="/api", tags=["Lesson Sessions"])
app.include_router(assignments.router, prefix="/api", tags=["Assignments"])
app.include_router(uploads.router, prefix="/api", tags=["Uploads"])
app.include_router(meta.router, prefix="/api", tags=["Meta"])
app.include_router(v2_platform.router, prefix="/api", tags=["V2 Platform"])


@app.get("/api")
def read_root():
    return {"message": "Echoed API is running"}


@app.get("/health/live", include_in_schema=False)
def liveness():
    return {"status": "live"}


def _database_ready() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


@app.get("/health/ready", include_in_schema=False)
async def readiness():
    started_at = time.perf_counter()
    try:
        await asyncio.wait_for(run_in_threadpool(_database_ready), timeout=settings.readiness_timeout_seconds)
    except (SQLAlchemyError, TimeoutError):
        duration_ms = (time.perf_counter() - started_at) * 1000
        metrics.increment("echoed_database_operations_total", operation="readiness", result="failure")
        metrics.observe("echoed_database_operation_duration_ms", duration_ms, operation="readiness")
        emit_event("database.connection.failed", level=40, component="database", operation="readiness", result="failure")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "dependencies": {"database": "unavailable"}},
        )
    duration_ms = (time.perf_counter() - started_at) * 1000
    metrics.increment("echoed_database_operations_total", operation="readiness", result="success")
    metrics.observe("echoed_database_operation_duration_ms", duration_ms, operation="readiness")
    return {"status": "ready", "dependencies": {"database": "available"}}


@app.get("/internal/metrics", include_in_schema=False, response_class=PlainTextResponse)
def operational_metrics(x_metrics_token: str | None = Header(default=None, alias="X-Metrics-Token")):
    if not settings.metrics_endpoint_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if not x_metrics_token or not settings.metrics_access_token or not secrets.compare_digest(
        x_metrics_token, settings.metrics_access_token
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Metrics access denied")
    return PlainTextResponse(metrics.render(), media_type="text/plain; version=0.0.4; charset=utf-8")
