import os
import shutil
import uuid
from fastapi import APIRouter, Depends, File, Request, UploadFile

from app.deps import require_roles
from app.models import User

router = APIRouter()

STORYBOOK_PATH = os.getenv("STORYBOOK_PATH", "./storybook")
COLORINGS_PATH = os.getenv("COLORINGS_PATH", "./colorings")
BADGES_PATH = os.getenv("BADGES_PATH", "./badges")


@router.post("/upload/coloring")
def upload_coloring(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(COLORINGS_PATH, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_url = request.url_for("colorings", path=filename)
    return {"file_path": str(file_url)}


@router.post("/upload/storybook")
def upload_storybook_page(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(STORYBOOK_PATH, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_url = request.url_for("storybook", path=filename)
    return {"file_path": str(file_url)}


@router.post("/upload/badge")
def upload_badge_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin")),
):
    extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(BADGES_PATH, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_url = request.url_for("badges", path=filename)
    return {"file_path": str(file_url)}
