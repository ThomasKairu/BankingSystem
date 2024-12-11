from datetime import datetime, timedelta
from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.schemas.token import Token, RefreshToken
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.models.user import User as UserModel

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    request: Request
) -> Any:
    """
    Register new user.
    """
    device_info = {
        "device_id": request.headers.get("X-Device-ID"),
        "device_name": request.headers.get("X-Device-Name"),
        "device_type": request.headers.get("X-Device-Type"),
        "fingerprint": request.headers.get("X-Device-Fingerprint"),
        "ip_address": request.client.host,
        "user_agent": request.headers.get("User-Agent")
    }

    auth_service = AuthService(db)
    return await auth_service.register_user(
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
        date_of_birth=user_in.date_of_birth,
        device_info=device_info
    )

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request
) -> Any:
    """
    OAuth2 compatible token login.
    """
    device_info = {
        "device_id": request.headers.get("X-Device-ID"),
        "device_name": request.headers.get("X-Device-Name"),
        "device_type": request.headers.get("X-Device-Type"),
        "fingerprint": request.headers.get("X-Device-Fingerprint"),
        "ip_address": request.client.host,
        "user_agent": request.headers.get("User-Agent")
    }

    auth_service = AuthService(db)
    return await auth_service.authenticate_user(
        email=form_data.username,
        password=form_data.password,
        device_info=device_info
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    *,
    db: Session = Depends(get_db),
    refresh_token: RefreshToken = Body(...),
    request: Request
) -> Any:
    """
    Refresh token.
    """
    device_info = {
        "device_id": request.headers.get("X-Device-ID"),
        "device_name": request.headers.get("X-Device-Name"),
        "device_type": request.headers.get("X-Device-Type"),
        "fingerprint": request.headers.get("X-Device-Fingerprint"),
        "ip_address": request.client.host,
        "user_agent": request.headers.get("User-Agent")
    }

    auth_service = AuthService(db)
    return await auth_service.refresh_token(
        refresh_token=refresh_token.refresh_token,
        device_info=device_info
    )

@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Verify user's email address.
    """
    auth_service = AuthService(db)
    return await auth_service.verify_email(token)

@router.post("/forgot-password")
async def forgot_password(
    email: str = Body(..., embed=True),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Password recovery email.
    """
    auth_service = AuthService(db)
    return await auth_service.forgot_password(email)

@router.post("/reset-password/{token}")
async def reset_password(
    token: str,
    new_password: str = Body(..., embed=True),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Reset password with token.
    """
    auth_service = AuthService(db)
    return await auth_service.reset_password(token, new_password)

@router.post("/verify-mfa", response_model=Token)
async def verify_mfa(
    *,
    db: Session = Depends(get_db),
    mfa_token: str = Body(...),
    mfa_code: str = Body(...),
    request: Request
) -> Any:
    """
    Verify MFA code and complete login.
    """
    device_info = {
        "device_id": request.headers.get("X-Device-ID"),
        "device_name": request.headers.get("X-Device-Name"),
        "device_type": request.headers.get("X-Device-Type"),
        "fingerprint": request.headers.get("X-Device-Fingerprint"),
        "ip_address": request.client.host,
        "user_agent": request.headers.get("User-Agent")
    }

    auth_service = AuthService(db)
    return await auth_service.verify_mfa(
        mfa_token=mfa_token,
        mfa_code=mfa_code,
        device_info=device_info
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
) -> Any:
    """
    Get current user information.
    """
    return current_user

@router.post("/logout")
async def logout(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Logout current user.
    """
    auth_service = AuthService(db)
    return await auth_service.logout(current_user.id)

@router.post("/logout-all-devices")
async def logout_all_devices(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Logout from all devices.
    """
    auth_service = AuthService(db)
    return await auth_service.logout_all_devices(current_user.id)
