import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.deps import require_roles
from app.models import User

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
        temporary_path.replace(final_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    return filename


@router.post("/upload/coloring")
def upload_coloring(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    filename = _store_image_upload(file, COLORINGS_PATH)
    file_url = request.url_for("colorings", path=filename)
    return {"file_path": str(file_url)}


@router.post("/upload/storybook")
def upload_storybook_page(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    filename = _store_image_upload(file, STORYBOOK_PATH)
    file_url = request.url_for("storybook", path=filename)
    return {"file_path": str(file_url)}


@router.post("/upload/badge")
def upload_badge_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin")),
):
    filename = _store_image_upload(file, BADGES_PATH)
    file_url = request.url_for("badges", path=filename)
    return {"file_path": str(file_url)}
