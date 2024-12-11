from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.api import deps
from app.services.key_management_service import KeyManagementService

router = APIRouter()

@router.post("/keys/", response_model=schemas.EncryptionKey)
def create_key(
    *,
    db: Session = Depends(deps.get_db),
    key_in: schemas.EncryptionKeyCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.EncryptionKey:
    """Create a new encryption key."""
    key_service = KeyManagementService(db)
    key = key_service.create_key(
        key_type=key_in.key_type,
        purpose=key_in.purpose,
        created_by=current_user.id,
        expiry_days=key_in.expiry_days
    )
    return key

@router.post("/keys/{key_id}/rotate", response_model=schemas.EncryptionKey)
def rotate_key(
    *,
    db: Session = Depends(deps.get_db),
    key_id: str,
    reason: str = "scheduled",
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.EncryptionKey:
    """Rotate an existing encryption key."""
    key_service = KeyManagementService(db)
    try:
        key = key_service.rotate_key(
            key_id=key_id,
            rotated_by=current_user.id,
            reason=reason
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return key

@router.get("/keys/", response_model=List[schemas.EncryptionKey])
def get_keys(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    purpose: Optional[str] = None,
    key_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> List[models.EncryptionKey]:
    """Retrieve encryption keys."""
    query = db.query(models.EncryptionKey)
    
    if purpose:
        query = query.filter(models.EncryptionKey.purpose == purpose)
    if key_type:
        query = query.filter(models.EncryptionKey.key_type == key_type)
    if is_active is not None:
        query = query.filter(models.EncryptionKey.is_active == is_active)
    
    keys = query.offset(skip).limit(limit).all()
    return keys

@router.get("/keys/{key_id}", response_model=schemas.EncryptionKey)
def get_key(
    *,
    db: Session = Depends(deps.get_db),
    key_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> models.EncryptionKey:
    """Get a specific encryption key."""
    key = db.query(models.EncryptionKey).filter(
        models.EncryptionKey.key_id == key_id
    ).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    return key

@router.get("/keys/{key_id}/history", response_model=List[schemas.KeyRotationHistory])
def get_key_rotation_history(
    *,
    db: Session = Depends(deps.get_db),
    key_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> List[models.KeyRotationHistory]:
    """Get rotation history for a specific key."""
    key_service = KeyManagementService(db)
    history = key_service.get_rotation_history(key_id)
    return history

@router.post("/keys/{key_id}/disable")
def disable_key(
    *,
    db: Session = Depends(deps.get_db),
    key_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> dict:
    """Disable an encryption key."""
    key_service = KeyManagementService(db)
    key_service.disable_key(key_id)
    return {"message": "Key disabled successfully"}

@router.get("/keys/rotation-check", response_model=List[schemas.EncryptionKey])
def check_keys_for_rotation(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> List[models.EncryptionKey]:
    """Check for keys that need rotation."""
    key_service = KeyManagementService(db)
    keys = key_service.check_keys_for_rotation()
    return keys
