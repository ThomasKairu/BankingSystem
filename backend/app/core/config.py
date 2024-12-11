from pydantic_settings import BaseSettings
from typing import List, Optional, Union
import secrets
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Advanced Banking System"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    TRUSTED_IPS: List[str] = ["127.0.0.1/32"]
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "banking_system"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: List[str] = ["localhost:9092"]
    
    # Elasticsearch
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Encryption Settings
    ENCRYPTION_MASTER_KEY: str = secrets.token_urlsafe(32)
    ENCRYPTION_KEY_ROTATION_DAYS: int = 30
    ENCRYPTION_MIN_KEY_LENGTH: int = 32
    ENCRYPTION_ALGORITHM: str = "AES-256-GCM"
    RSA_KEY_SIZE: int = 2048
    HASH_ITERATIONS: int = 100000
    
    # SMS Settings (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None
    
    # Push Notifications (Firebase)
    FIREBASE_CREDENTIALS: Optional[str] = None
    
    # Security settings
    VERIFY_EMAIL: bool = True
    RESET_PASSWORD_TOKEN_EXPIRE_HOURS: int = 48
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT: tuple = (100, 60)  # 100 requests per minute
    RATE_LIMIT_AUTH: tuple = (5, 60)       # 5 login attempts per minute
    RATE_LIMIT_TRANSACTIONS: tuple = (20, 60)  # 20 transactions per minute
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Feature flags
    ENABLE_AI_FEATURES: bool = True
    ENABLE_BIOMETRIC_AUTH: bool = True
    
    # Monitoring
    ENABLE_PROMETHEUS: bool = True
    PROMETHEUS_MULTIPROC_DIR: str = "/tmp"
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Construct database URI
if not settings.SQLALCHEMY_DATABASE_URI:
    settings.SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/"
        f"{settings.POSTGRES_DB}"
    )
