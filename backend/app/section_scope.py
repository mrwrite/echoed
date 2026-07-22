from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import OrganizationMembership, Section


def require_scoped_section(
    db: Session,
    membership: OrganizationMembership,
    section_id: str | UUID,
) -> Section:
    try:
        normalized_id = section_id if isinstance(section_id, UUID) else UUID(section_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid section id") from exc

    section = (
        db.query(Section)
        .filter(
            Section.id == normalized_id,
            Section.organization_id == membership.organization_id,
        )
        .first()
    )
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return section
