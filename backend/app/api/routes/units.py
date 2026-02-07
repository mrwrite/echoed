from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.deps import require_roles
from app.models import Unit, CourseVersion
from app.schemas import UnitResponse
from pydantic import BaseModel

class UnitCreate(BaseModel):
    course_id: UUID
    title: str
    content: str | None = None
    order: int | None = None

class UnitUpdate(UnitCreate):
    pass


class VersionUnitCreate(BaseModel):
    title: str
    content: str | None = None
    order: int | None = None

router = APIRouter()

@router.post('/units', response_model=UnitResponse)
def create_unit(
    unit: UnitCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    new_unit = Unit(
        course_id=unit.course_id,
        title=unit.title,
        content=unit.content,
        order=unit.order,
    )
    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    return new_unit


@router.post('/course-versions/{version_id}/units', response_model=UnitResponse)
def create_unit_for_version(
    version_id: UUID,
    unit: VersionUnitCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    version = db.query(CourseVersion).filter_by(id=version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail='Course version not found')
    new_unit = Unit(
        course_id=version.course_id,
        course_version_id=version.id,
        title=unit.title,
        content=unit.content,
        order=unit.order,
    )
    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    return new_unit


@router.get('/course-versions/{version_id}/units', response_model=list[UnitResponse])
def list_units_for_version(
    version_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    return db.query(Unit).filter_by(course_version_id=version_id).all()

@router.get('/units', response_model=list[UnitResponse])
def list_units(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    return db.query(Unit).all()

@router.get('/units/{unit_id}', response_model=UnitResponse)
def get_unit(
    unit_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    unit = db.query(Unit).filter_by(id=unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail='Unit not found')
    return unit

@router.put('/units/{unit_id}', response_model=UnitResponse)
def update_unit(
    unit_id: UUID,
    unit: UnitUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    db_unit = db.query(Unit).filter_by(id=unit_id).first()
    if not db_unit:
        raise HTTPException(status_code=404, detail='Unit not found')
    db_unit.course_id = unit.course_id
    db_unit.title = unit.title
    db_unit.content = unit.content
    db_unit.order = unit.order
    db.commit()
    db.refresh(db_unit)
    return db_unit

@router.delete('/units/{unit_id}')
def delete_unit(
    unit_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    db_unit = db.query(Unit).filter_by(id=unit_id).first()
    if not db_unit:
        raise HTTPException(status_code=404, detail='Unit not found')
    db.delete(db_unit)
    db.commit()
    return {'message': 'Unit deleted'}
