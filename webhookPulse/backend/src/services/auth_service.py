from fastapi import HTTPException, status

from src.models.tenant import create_tenant_document
from src.models.user import create_user_document
from src.repositories.tenant_repository import create_tenant
from src.repositories.user_repository import (
    create_user,
    get_user_by_email,
)
from src.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)


def register_user(
    email: str,
    password: str,
    company_name: str,
):

    existing_user = get_user_by_email(email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    tenant_document = create_tenant_document(company_name)
    tenant_id = create_tenant(tenant_document)

    password_hash = hash_password(password)

    user_document = create_user_document(
        email=email,
        password_hash=password_hash,
        tenant_id=tenant_id,
    )

    user_id = create_user(user_document)

    token = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        role="admin",
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


def login_user(
    email: str,
    password: str,
):

    user = get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user_id = str(user["_id"])
    tenant_id = user["tenant_id"]

    token = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        role=user["role"],
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }