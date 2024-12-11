from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

class SecurityUtils:
    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.JWTError:
            return None
    
    @staticmethod
    def create_refresh_token(
        subject: Union[str, Any], expires_delta: timedelta = None
    ) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def generate_password_reset_token(email: str) -> str:
        delta = timedelta(hours=settings.RESET_PASSWORD_TOKEN_EXPIRE_HOURS)
        now = datetime.utcnow()
        expires = now + delta
        exp = expires.timestamp()
        encoded_jwt = jwt.encode(
            {"exp": exp, "nbf": now, "sub": email},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return encoded_jwt
    
    @staticmethod
    def verify_password_reset_token(token: str) -> str:
        try:
            decoded_token = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return decoded_token["sub"]
        except jwt.JWTError:
            return None

# Advanced encryption capabilities
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
import json

class EncryptionUtils:
    def __init__(self):
        self.master_key = base64.b64decode(settings.ENCRYPTION_MASTER_KEY)
        self.fernet = Fernet(self.master_key)
    
    def encrypt_sensitive_data(self, data: dict) -> str:
        """Encrypt sensitive data using Fernet (symmetric encryption)."""
        json_data = json.dumps(data)
        encrypted_data = self.fernet.encrypt(json_data.encode())
        return base64.b64encode(encrypted_data).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> dict:
        """Decrypt sensitive data using Fernet."""
        try:
            decoded_data = base64.b64decode(encrypted_data)
            decrypted_data = self.fernet.decrypt(decoded_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")

    def hash_sensitive_data(self, data: str, salt: bytes = None) -> dict:
        """One-way hash sensitive data using PBKDF2."""
        if not salt:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        key = base64.b64encode(kdf.derive(data.encode())).decode()
        return {
            "hash": key,
            "salt": base64.b64encode(salt).decode()
        }

    def generate_key_pair(self) -> dict:
        """Generate RSA key pair for asymmetric encryption."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            "private_key": private_pem.decode(),
            "public_key": public_pem.decode()
        }

    def encrypt_file(self, file_data: bytes) -> tuple:
        """Encrypt file data using AES-256-GCM."""
        key = os.urandom(32)
        iv = os.urandom(12)
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
        )
        
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(file_data) + encryptor.finalize()
        
        return {
            "encrypted_data": base64.b64encode(encrypted_data).decode(),
            "iv": base64.b64encode(iv).decode(),
            "tag": base64.b64encode(encryptor.tag).decode(),
            "key": base64.b64encode(key).decode()
        }

    def decrypt_file(self, encrypted_data: str, iv: str, tag: str, key: str) -> bytes:
        """Decrypt file data using AES-256-GCM."""
        try:
            key_bytes = base64.b64decode(key)
            iv_bytes = base64.b64decode(iv)
            tag_bytes = base64.b64decode(tag)
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            cipher = Cipher(
                algorithms.AES(key_bytes),
                modes.GCM(iv_bytes, tag_bytes),
            )
            
            decryptor = cipher.decryptor()
            return decryptor.update(encrypted_bytes) + decryptor.finalize()
        except Exception as e:
            raise ValueError(f"Failed to decrypt file: {str(e)}")

    @staticmethod
    def secure_random_string(length: int = 32) -> str:
        """Generate a secure random string."""
        return base64.b64encode(os.urandom(length)).decode()[:length]

# Initialize encryption utils
encryption_utils = EncryptionUtils()
