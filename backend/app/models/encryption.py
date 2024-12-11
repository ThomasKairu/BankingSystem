from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class EncryptionKey(Base):
    __tablename__ = "encryption_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String, unique=True, index=True)
    key_type = Column(String)  # symmetric, asymmetric_public, asymmetric_private
    key_data = Column(String)  # Encrypted key data
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    purpose = Column(String)  # data_encryption, file_encryption, key_wrapping
    version = Column(Integer)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    last_rotated_at = Column(DateTime)
    last_rotated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    rotator = relationship("User", foreign_keys=[last_rotated_by])

class KeyRotationHistory(Base):
    __tablename__ = "key_rotation_history"

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(String, ForeignKey("encryption_keys.key_id"))
    rotated_at = Column(DateTime, default=datetime.utcnow)
    rotated_by = Column(Integer, ForeignKey("users.id"))
    old_version = Column(Integer)
    new_version = Column(Integer)
    reason = Column(String)  # scheduled, emergency, policy_change
    
    # Relationships
    key = relationship("EncryptionKey")
    user = relationship("User")
