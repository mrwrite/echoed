from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import UserPreferences
from app.schemas import UserPreferencesDto

router = APIRouter()


@router.get("/me/preferences", response_model=UserPreferencesDto)
def get_preferences(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    prefs = (
        db.query(UserPreferences)
        .filter(UserPreferences.user_id == current_user.id)
        .first()
    )
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


@router.put("/me/preferences", response_model=UserPreferencesDto)
def update_preferences(
    payload: UserPreferencesDto,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    prefs = (
        db.query(UserPreferences)
        .filter(UserPreferences.user_id == current_user.id)
        .first()
    )
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)

    prefs.locale = payload.locale
    prefs.timezone = payload.timezone
    prefs.theme = payload.theme
    prefs.large_text = payload.large_text
    prefs.dyslexia_font = payload.dyslexia_font
    prefs.preferred_mode = payload.preferred_mode
    prefs.reading_level_mode = payload.reading_level_mode
    db.commit()
    db.refresh(prefs)
    return prefs
