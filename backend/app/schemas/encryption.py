from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EncryptionKeyBase(BaseModel):
    key_type: str
    purpose: str
    version: int
    is_active: bool = True

class EncryptionKeyCreate(EncryptionKeyBase):
    expiry_days: Optional[int] = None

class EncryptionKeyUpdate(BaseModel):
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class EncryptionKey(EncryptionKeyBase):
    id: int
    key_id: str
    created_at: datetime
    expires_at: Optional[datetime]
    created_by: int
    last_rotated_at: Optional[datetime]
    last_rotated_by: Optional[int]

    class Config:
        from_attributes = True

class KeyRotationHistoryBase(BaseModel):
    key_id: str
    old_version: int
    new_version: int
    reason: str

class KeyRotationHistoryCreate(KeyRotationHistoryBase):
    pass

class KeyRotationHistory(KeyRotationHistoryBase):
    id: int
    rotated_at: datetime
    rotated_by: int

    class Config:
        from_attributes = True
