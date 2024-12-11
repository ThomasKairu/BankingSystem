from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from app.core.security import encryption_utils
from app.models.encryption import EncryptionKey, KeyRotationHistory
from app.core.config import settings

class KeyManagementService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_key(
        self,
        key_type: str,
        purpose: str,
        created_by: int,
        expiry_days: Optional[int] = None
    ) -> EncryptionKey:
        """Create a new encryption key."""
        key_id = encryption_utils.secure_random_string()
        
        # Generate key based on type
        if key_type == "symmetric":
            key_data = encryption_utils.secure_random_string(32)
        elif key_type in ["asymmetric_public", "asymmetric_private"]:
            key_pair = encryption_utils.generate_key_pair()
            key_data = key_pair["private_key"] if key_type == "asymmetric_private" else key_pair["public_key"]
        else:
            raise ValueError(f"Invalid key type: {key_type}")
        
        # Encrypt key data using master key
        encrypted_key_data = encryption_utils.encrypt_sensitive_data({"key": key_data})
        
        # Calculate expiry date
        expires_at = None
        if expiry_days:
            expires_at = datetime.utcnow() + timedelta(days=expiry_days)
        
        # Create key record
        key = EncryptionKey(
            key_id=key_id,
            key_type=key_type,
            key_data=encrypted_key_data,
            created_by=created_by,
            purpose=purpose,
            version=1,
            expires_at=expires_at
        )
        
        self.db.add(key)
        self.db.commit()
        self.db.refresh(key)
        
        return key
    
    def rotate_key(
        self,
        key_id: str,
        rotated_by: int,
        reason: str = "scheduled"
    ) -> EncryptionKey:
        """Rotate an existing encryption key."""
        key = self.db.query(EncryptionKey).filter(EncryptionKey.key_id == key_id).first()
        if not key:
            raise ValueError(f"Key not found: {key_id}")
        
        # Generate new key data
        if key.key_type == "symmetric":
            new_key_data = encryption_utils.secure_random_string(32)
        elif key.key_type in ["asymmetric_public", "asymmetric_private"]:
            key_pair = encryption_utils.generate_key_pair()
            new_key_data = key_pair["private_key"] if key.key_type == "asymmetric_private" else key_pair["public_key"]
        
        # Encrypt new key data
        encrypted_key_data = encryption_utils.encrypt_sensitive_data({"key": new_key_data})
        
        # Create rotation history record
        rotation = KeyRotationHistory(
            key_id=key_id,
            rotated_by=rotated_by,
            old_version=key.version,
            new_version=key.version + 1,
            reason=reason
        )
        
        # Update key record
        key.key_data = encrypted_key_data
        key.version += 1
        key.last_rotated_at = datetime.utcnow()
        key.last_rotated_by = rotated_by
        
        self.db.add(rotation)
        self.db.commit()
        self.db.refresh(key)
        
        return key
    
    def get_active_key(self, purpose: str, key_type: str) -> Optional[EncryptionKey]:
        """Get the active key for a specific purpose and type."""
        return (
            self.db.query(EncryptionKey)
            .filter(
                EncryptionKey.purpose == purpose,
                EncryptionKey.key_type == key_type,
                EncryptionKey.is_active == True,
                (
                    (EncryptionKey.expires_at > datetime.utcnow()) |
                    (EncryptionKey.expires_at.is_(None))
                )
            )
            .first()
        )
    
    def get_key_data(self, key: EncryptionKey) -> str:
        """Decrypt and return the key data."""
        encrypted_data = key.key_data
        decrypted_data = encryption_utils.decrypt_sensitive_data(encrypted_data)
        return decrypted_data["key"]
    
    def check_keys_for_rotation(self) -> List[EncryptionKey]:
        """Check for keys that need rotation based on age."""
        rotation_threshold = datetime.utcnow() - timedelta(
            days=settings.ENCRYPTION_KEY_ROTATION_DAYS
        )
        
        keys_to_rotate = (
            self.db.query(EncryptionKey)
            .filter(
                EncryptionKey.is_active == True,
                (
                    (EncryptionKey.last_rotated_at < rotation_threshold) |
                    (
                        (EncryptionKey.last_rotated_at.is_(None)) &
                        (EncryptionKey.created_at < rotation_threshold)
                    )
                )
            )
            .all()
        )
        
        return keys_to_rotate
    
    def disable_key(self, key_id: str) -> None:
        """Disable a key."""
        key = self.db.query(EncryptionKey).filter(EncryptionKey.key_id == key_id).first()
        if key:
            key.is_active = False
            self.db.commit()
    
    def get_rotation_history(self, key_id: str) -> List[KeyRotationHistory]:
        """Get rotation history for a key."""
        return (
            self.db.query(KeyRotationHistory)
            .filter(KeyRotationHistory.key_id == key_id)
            .order_by(KeyRotationHistory.rotated_at.desc())
            .all()
        )
