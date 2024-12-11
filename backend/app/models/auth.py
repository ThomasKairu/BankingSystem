from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.user import User

class AuthDevice(Base):
    __tablename__ = "auth_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(String, unique=True, index=True)
    device_name = Column(String)
    device_type = Column(String)
    fingerprint = Column(String)
    is_trusted = Column(Boolean, default=False)
    last_used = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Integer, default=0)
    metadata = Column(JSON)

    user = relationship("User", back_populates="auth_devices")

class MFAMethod(Base):
    __tablename__ = "mfa_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    method_type = Column(String)  # email, phone, authenticator, biometric
    identifier = Column(String)  # email address, phone number, etc.
    is_primary = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)
    last_used = Column(DateTime)
    metadata = Column(JSON)

    user = relationship("User", back_populates="mfa_methods")

class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(String, ForeignKey("auth_devices.device_id"))
    session_token = Column(String, unique=True, index=True)
    refresh_token = Column(String, unique=True)
    ip_address = Column(String)
    user_agent = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_valid = Column(Boolean, default=True)

    user = relationship("User", back_populates="auth_sessions")
    device = relationship("AuthDevice")

class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String)  # google, facebook, apple, etc.
    provider_user_id = Column(String)
    email = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="social_accounts")

class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    consent_type = Column(String)  # privacy_policy, terms_of_service, marketing, etc.
    version = Column(String)
    granted_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    user_agent = Column(String)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON)

    user = relationship("User", back_populates="consent_records")
