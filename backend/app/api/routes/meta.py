from fastapi import APIRouter
from app.enum import OrganizationRole, OrganizationType

router = APIRouter(prefix="/meta", tags=["meta"])


def _enum_value(v):
    # Handles normal Enums, and also any weird tuple-style items
    if isinstance(v, tuple):
        v = v[0]  # pick first element if enum value is stored as tuple
    return str(v)


def _label_from_value(value: str) -> str:
    return value.replace("_", " ").title()


@router.get("/enums")
def get_enums():
    roles = []
    for r in OrganizationRole:
        value = _enum_value(getattr(r, "value", r))
        key = getattr(r, "name", value)
        roles.append({"key": key, "value": value, "label": _label_from_value(value)})

    org_types = []
    for t in OrganizationType:
        value = _enum_value(getattr(t, "value", t))
        key = getattr(t, "name", value)
        org_types.append({"key": key, "value": value, "label": _label_from_value(value)})

    return {"organizationRoles": roles, "organizationTypes": org_types}
