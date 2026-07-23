import os
import re
import time
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

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
from app.log import logger

app = FastAPI()

STORYBOOK_PATH = os.getenv("STORYBOOK_PATH", "./storybook")
COLORINGS_PATH = os.getenv("COLORINGS_PATH", "./colorings")
BADGES_PATH = os.getenv("BADGES_PATH", "./badges")

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


allowed_origins = _parse_allowed_origins(
    os.getenv("FRONTEND_URL", "http://localhost:4200,http://127.0.0.1:4200")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


@app.middleware("http")
async def add_operational_context(request: Request, call_next):
    incoming_request_id = request.headers.get("X-Request-ID", "")
    request_id = (
        incoming_request_id
        if REQUEST_ID_PATTERN.fullmatch(incoming_request_id)
        else str(uuid.uuid4())
    )
    started_at = time.perf_counter()
    request.state.request_id = request_id

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "request_failed request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        raise

    duration_ms = (time.perf_counter() - started_at) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    logger.info(
        "request_complete request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response

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


@app.get("/health/ready", include_in_schema=False)
def readiness():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable.",
        ) from exc
    return {"status": "ready", "database": "available"}
