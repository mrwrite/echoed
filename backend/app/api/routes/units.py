from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Unit
from app.schemas import UnitResponse
from pydantic import BaseModel

class UnitCreate(BaseModel):
    course_id: UUID
    title: str
    content: str | None = None
    order: int | None = None

class UnitUpdate(UnitCreate):
    pass

router = APIRouter()

@router.post('/units', response_model=UnitResponse)
def create_unit(unit: UnitCreate, db: Session = Depends(get_db)):
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

@router.get('/units', response_model=list[UnitResponse])
def list_units(db: Session = Depends(get_db)):
    return db.query(Unit).all()

@router.get('/units/{unit_id}', response_model=UnitResponse)
def get_unit(unit_id: UUID, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter_by(id=unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail='Unit not found')
    return unit

@router.put('/units/{unit_id}', response_model=UnitResponse)
def update_unit(unit_id: UUID, unit: UnitUpdate, db: Session = Depends(get_db)):
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
def delete_unit(unit_id: UUID, db: Session = Depends(get_db)):
    db_unit = db.query(Unit).filter_by(id=unit_id).first()
    if not db_unit:
        raise HTTPException(status_code=404, detail='Unit not found')
    db.delete(db_unit)
    db.commit()
    return {'message': 'Unit deleted'}
