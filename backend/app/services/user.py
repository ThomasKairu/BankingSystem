from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate

class UserService:
    @staticmethod
    def get(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_multi(
        db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=False,
            two_factor_enabled=False,
            preferences={},
            notification_settings={
                "email": True,
                "sms": False,
                "push": False
            }
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(
        db: Session, *, db_obj: User, obj_in: UserUpdate
    ) -> User:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, *, user_id: int) -> User:
        obj = db.query(User).get(user_id)
        db.delete(obj)
        db.commit()
        return obj

    @staticmethod
    def authenticate(
        db: Session, *, email: str, password: str
    ) -> Optional[User]:
        user = UserService.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def is_active(user: User) -> bool:
        return user.is_active

    @staticmethod
    def is_verified(user: User) -> bool:
        return user.is_verified

    @staticmethod
    def update_verification(
        db: Session, *, user_id: int, is_verified: bool
    ) -> User:
        user = UserService.get(db, user_id=user_id)
        user.is_verified = is_verified
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_2fa(
        db: Session, *, user_id: int, enabled: bool, secret: Optional[str] = None
    ) -> User:
        user = UserService.get(db, user_id=user_id)
        user.two_factor_enabled = enabled
        if secret:
            user.two_factor_secret = secret
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
