from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.core.deps import get_current_active_user, get_current_active_superuser, get_db
from app.services.user import UserService
from app.schemas.user import User, UserCreate, UserUpdate
from app.models.user import User as UserModel
import pyotp

router = APIRouter()

@router.get("/me", response_model=User)
def read_user_me(
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    user = UserService.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = UserService.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = UserService.create(db, obj_in=user_in)
    return user

@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users. Only for admins.
    """
    users = UserService.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = UserService.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    if user.id != current_user.id and not current_user.role == "admin":
        raise HTTPException(
            status_code=400,
            detail="Not enough permissions",
        )
    return user

@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user. Only for admins.
    """
    user = UserService.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    user = UserService.update(db, db_obj=user, obj_in=user_in)
    return user

@router.post("/{user_id}/verify", response_model=User)
def verify_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: UserModel = Depends(get_current_active_superuser),
) -> Any:
    """
    Verify a user. Only for admins.
    """
    user = UserService.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    user = UserService.update_verification(db, user_id=user_id, is_verified=True)
    return user

@router.post("/me/enable-2fa", response_model=dict)
def enable_2fa(
    *,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Enable 2FA for current user.
    """
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="2FA is already enabled",
        )
    
    # Generate secret key
    secret = pyotp.random_base32()
    
    # Create OTP URI
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        current_user.email,
        issuer_name="Banking System"
    )
    
    # Update user with 2FA secret
    UserService.update_2fa(
        db,
        user_id=current_user.id,
        enabled=True,
        secret=secret
    )
    
    return {
        "secret": secret,
        "uri": provisioning_uri
    }

@router.post("/me/verify-2fa")
def verify_2fa(
    *,
    db: Session = Depends(get_db),
    token: str = Body(...),
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Verify 2FA token.
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="2FA is not enabled",
        )
    
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if not totp.verify(token):
        raise HTTPException(
            status_code=400,
            detail="Invalid token",
        )
    
    return {"message": "Token verified successfully"}
