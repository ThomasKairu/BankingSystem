from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.models.user import User
from app.models.auth import AuthDevice, MFAMethod, AuthSession, SocialAccount, ConsentRecord
from app.core.config import settings
from app.services.notification import NotificationService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.REFRESH_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def authenticate_user(
        self, 
        email: str, 
        password: str, 
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )

        # Check if MFA is required
        if user.two_factor_enabled:
            return await self.initiate_mfa(user, device_info)

        # Create session and tokens
        return await self.create_session(user, device_info)

    async def initiate_mfa(self, user: User, device_info: Dict[str, Any]) -> Dict[str, Any]:
        # Get primary MFA method
        mfa_method = self.db.query(MFAMethod).filter(
            MFAMethod.user_id == user.id,
            MFAMethod.is_primary == True,
            MFAMethod.is_enabled == True
        ).first()

        if not mfa_method:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No MFA method configured"
            )

        # Generate and send MFA code
        mfa_code = self._generate_mfa_code()
        
        if mfa_method.method_type == "email":
            await self.notification_service.send_mfa_code_email(
                user.email, 
                mfa_code
            )
        elif mfa_method.method_type == "phone":
            await self.notification_service.send_mfa_code_sms(
                user.phone_number, 
                mfa_code
            )

        # Store MFA session
        mfa_session = {
            "user_id": user.id,
            "mfa_code": mfa_code,
            "expires_at": datetime.utcnow() + timedelta(minutes=5)
        }

        return {
            "message": "MFA code sent",
            "mfa_required": True,
            "mfa_session": self.create_access_token(mfa_session, timedelta(minutes=5))
        }

    async def verify_mfa(
        self, 
        mfa_token: str, 
        mfa_code: str, 
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                mfa_token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="MFA session expired"
                )

            if payload["mfa_code"] != mfa_code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code"
                )

            user = self.db.query(User).filter(User.id == payload["user_id"]).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            return await self.create_session(user, device_info)

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA session"
            )

    async def create_session(
        self, 
        user: User, 
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Update or create device record
        device = self.db.query(AuthDevice).filter(
            AuthDevice.device_id == device_info["device_id"]
        ).first()

        if not device:
            device = AuthDevice(
                user_id=user.id,
                device_id=device_info["device_id"],
                device_name=device_info.get("device_name"),
                device_type=device_info.get("device_type"),
                fingerprint=device_info.get("fingerprint"),
                metadata=device_info
            )
            self.db.add(device)
        
        device.last_used = datetime.utcnow()
        
        # Create new session
        session = AuthSession(
            user_id=user.id,
            device_id=device.device_id,
            session_token=self._generate_session_token(),
            refresh_token=self._generate_refresh_token(),
            ip_address=device_info.get("ip_address"),
            user_agent=device_info.get("user_agent"),
            expires_at=datetime.utcnow() + timedelta(days=settings.SESSION_EXPIRE_DAYS)
        )
        self.db.add(session)
        
        # Update user's last login
        user.last_login = datetime.utcnow()
        
        self.db.commit()

        # Generate tokens
        access_token = self.create_access_token(
            data={"sub": user.email, "session": session.session_token}
        )
        refresh_token = self.create_refresh_token(
            data={"sub": user.email, "session": session.refresh_token}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_verified": user.is_verified
            }
        }

    async def refresh_token(
        self, 
        refresh_token: str, 
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                refresh_token, 
                settings.REFRESH_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            email = payload["sub"]
            session_token = payload["session"]

            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            session = self.db.query(AuthSession).filter(
                AuthSession.refresh_token == session_token,
                AuthSession.is_valid == True
            ).first()

            if not session or session.expires_at < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired session"
                )

            return await self.create_session(user, device_info)

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

    def _generate_mfa_code(self) -> str:
        """Generate a 6-digit MFA code"""
        import random
        return str(random.randint(100000, 999999))

    def _generate_session_token(self) -> str:
        """Generate a unique session token"""
        import uuid
        return str(uuid.uuid4())

    def _generate_refresh_token(self) -> str:
        """Generate a unique refresh token"""
        import uuid
        return str(uuid.uuid4())

    async def register_user(
        self, 
        email: str, 
        password: str, 
        full_name: str, 
        phone_number: str,
        date_of_birth: datetime,
        device_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Check if user already exists
        if self.db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        if self.db.query(User).filter(User.phone_number == phone_number).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

        # Create user
        user = User(
            email=email,
            hashed_password=self.get_password_hash(password),
            full_name=full_name,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            is_active=True,
            is_verified=False
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Send verification email
        await self.notification_service.send_verification_email(user.email)

        # Create initial session
        return await self.create_session(user, device_info)

    async def verify_email(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            email = payload["sub"]

            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            user.is_verified = True
            self.db.commit()

            return {"message": "Email verified successfully"}

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid verification token"
            )

    async def forgot_password(self, email: str) -> Dict[str, Any]:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            # Return success even if user doesn't exist for security
            return {"message": "Password reset instructions sent to email"}

        # Generate password reset token
        token = self.create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(hours=1)
        )

        # Send password reset email
        await self.notification_service.send_password_reset_email(user.email, token)

        return {"message": "Password reset instructions sent to email"}

    async def reset_password(
        self, 
        token: str, 
        new_password: str
    ) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            email = payload["sub"]

            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Update password
            user.hashed_password = self.get_password_hash(new_password)
            
            # Invalidate all existing sessions
            self.db.query(AuthSession).filter(
                AuthSession.user_id == user.id,
                AuthSession.is_valid == True
            ).update({"is_valid": False})

            self.db.commit()

            return {"message": "Password reset successfully"}

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid reset token"
            )
