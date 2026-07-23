from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    hash_password,
    resolve_active_organization,
)
from app.database import get_db
from app.models import (
    User,
    Organization,
    OrganizationMembership,
    UserPreferences,
)
from app.schemas import AuthTokenResponse, UserDto
from app.enum import OrganizationType, OrganizationRole

router = APIRouter()


@router.post("/auth/register")
def register_user(user: UserDto, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
        role=user.role.lower(),
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.flush()

    personal_org = Organization(
        name=f"{new_user.firstname}'s Personal Org",
        type=OrganizationType.PERSONAL,
        country=None,
        timezone=None,
    )
    db.add(personal_org)
    db.flush()

    membership = OrganizationMembership(
        organization_id=personal_org.id,
        user_id=new_user.id,
        role=OrganizationRole.ORG_ADMIN,
    )
    db.add(membership)
    db.add(UserPreferences(user_id=new_user.id))
    db.commit()

    return {"message": "User registered successfully", "organization_id": personal_org.id}


@router.post("/auth/token", response_model=AuthTokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    memberships = (
        db.query(OrganizationMembership)
        .join(Organization, Organization.id == OrganizationMembership.organization_id)
        .filter(OrganizationMembership.user_id == user.id)
        .all()
    )
    active_organization = resolve_active_organization(memberships)
    active_org_id = active_organization.organization_id if active_organization else None

    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": str(user.id),
            "fullname": f"{user.firstname} {user.lastname}",
            "role": user.role,
            "active_org_id": str(active_org_id) if active_org_id else None,
        },
        expires_delta=timedelta(minutes=120),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "organizations": [
            {
                "id": membership.organization_id,
                "role": membership.role.value,
            }
            for membership in memberships
        ],
        "active_org_id": str(active_org_id) if active_org_id else None,
        "active_org_role": active_organization.organization_role if active_organization else None,
        "active_organization": (
            {
                "id": active_organization.organization_id,
                "name": active_organization.organization_name,
                "type": active_organization.organization_type,
                "role": active_organization.organization_role,
            }
            if active_organization
            else None
        ),
    }


@router.get("/auth/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": "Authenticated"}
