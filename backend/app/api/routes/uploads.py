import os
import struct
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.deps import require_roles
from app.models import User
from app.rate_limit import enforce_rate_limit
from app.security import security_event
from app.observability import emit_event, metrics

router = APIRouter()

STORYBOOK_PATH = os.getenv("STORYBOOK_PATH", "./storybook")
COLORINGS_PATH = os.getenv("COLORINGS_PATH", "./colorings")
BADGES_PATH = os.getenv("BADGES_PATH", "./badges")
MAX_IMAGE_UPLOAD_BYTES = 5 * 1024 * 1024
IMAGE_CONTENT_TYPES = {
    ".gif": "image/gif",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
MAX_IMAGE_DIMENSION = 12_000
MAX_IMAGE_PIXELS = 40_000_000


def _validate_dimensions(width: int, height: int) -> None:
    if (
        width <= 0
        or height <= 0
        or width > MAX_IMAGE_DIMENSION
        or height > MAX_IMAGE_DIMENSION
        or width * height > MAX_IMAGE_PIXELS
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Image dimensions are invalid or exceed the supported limit.",
        )


def _jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    offset = 2
    sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset + 4 <= len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in {0xD8, 0xD9}:
            continue
        if offset + 2 > len(data):
            return None
        segment_length = int.from_bytes(data[offset : offset + 2], "big")
        if segment_length < 2 or offset + segment_length > len(data):
            return None
        if marker in sof_markers and segment_length >= 7:
            height = int.from_bytes(data[offset + 3 : offset + 5], "big")
            width = int.from_bytes(data[offset + 5 : offset + 7], "big")
            return width, height
        offset += segment_length
    return None


def _image_dimensions(extension: str, data: bytes) -> tuple[int, int] | None:
    if extension == ".png":
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
            return None
        return struct.unpack(">II", data[16:24])
    if extension == ".gif":
        if len(data) < 10 or data[:6] not in {b"GIF87a", b"GIF89a"}:
            return None
        return struct.unpack("<HH", data[6:10])
    if extension in {".jpg", ".jpeg"}:
        return _jpeg_dimensions(data)
    if extension == ".webp":
        if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
            return None
        chunk = data[12:16]
        if chunk == b"VP8X":
            return 1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little")
        if chunk == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
            return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
        if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
            bits = int.from_bytes(data[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return None


def _store_image_upload(file: UploadFile, destination: str) -> str:
    extension = Path(file.filename or "").suffix.lower()
    expected_content_type = IMAGE_CONTENT_TYPES.get(extension)
    if not expected_content_type or file.content_type != expected_content_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload must be a supported image with a matching content type.",
        )

    filename = f"{uuid.uuid4()}{extension}"
    final_path = Path(destination) / filename
    temporary_path = final_path.with_suffix(f"{extension}.part")
    total_bytes = 0

    try:
        with temporary_path.open("wb") as buffer:
            while chunk := file.file.read(64 * 1024):
                total_bytes += len(chunk)
                if total_bytes > MAX_IMAGE_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail="Image upload exceeds the 5 MB limit.",
                    )
                buffer.write(chunk)
        data = temporary_path.read_bytes()
        dimensions = _image_dimensions(extension, data)
        if dimensions is None:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Upload content does not match a supported image format.",
            )
        _validate_dimensions(*dimensions)
        temporary_path.replace(final_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    return filename


def _store_authorized_upload(
    file: UploadFile, destination: str, request: Request, current_user: User, category: str
) -> str:
    started_at = time.perf_counter()
    metrics.increment("echoed_uploads_total", category=category, result="attempt")
    try:
        stored = _store_image_upload(file, destination)
    except HTTPException as exc:
        metrics.increment("echoed_uploads_total", category=category, result="rejected")
        security_event(
            action="upload_rejection",
            result="denied",
            actor_id=current_user.id,
            target_type="image_upload",
            reason=f"http_{exc.status_code}",
            request_id=getattr(request.state, "request_id", None),
        )
        raise
    except Exception:
        metrics.increment("echoed_uploads_total", category=category, result="failure")
        emit_event("upload.failed", level=40, component="upload", category=category, result="failure")
        raise
    metrics.increment("echoed_uploads_total", category=category, result="success")
    metrics.observe("echoed_upload_duration_ms", (time.perf_counter() - started_at) * 1000, category=category)
    emit_event("upload.succeeded", component="upload", actor_id=current_user.id, category=category, result="success")
    return stored


@router.post("/upload/coloring")
def upload_coloring(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin", "super_admin", "teacher", "instructor", "content_admin")),
):
    enforce_rate_limit(request, "upload", actor_id=current_user.id)
    filename = _store_authorized_upload(file, COLORINGS_PATH, request, current_user, "coloring")
    file_url = request.url_for("colorings", path=filename)
    return {"file_path": str(file_url)}


@router.post("/upload/storybook")
def upload_storybook_page(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin", "super_admin", "teacher", "instructor", "content_admin")),
):
    enforce_rate_limit(request, "upload", actor_id=current_user.id)
    filename = _store_authorized_upload(file, STORYBOOK_PATH, request, current_user, "storybook")
    file_url = request.url_for("storybook", path=filename)
    return {"file_path": str(file_url)}


@router.post("/upload/badge")
def upload_badge_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin", "super_admin")),
):
    enforce_rate_limit(request, "upload", actor_id=current_user.id)
    filename = _store_authorized_upload(file, BADGES_PATH, request, current_user, "badge")
    file_url = request.url_for("badges", path=filename)
    return {"file_path": str(file_url)}
