from typing import Optional, List
from pydantic import BaseSettings, validator
import secrets


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Digital Banking Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:8080",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/banking_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TRANSACTION_TOPIC: str = "transactions"
    KAFKA_NOTIFICATION_TOPIC: str = "notifications"
    KAFKA_CONSUMER_GROUP: str = "banking-consumers"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # Email (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    
    # Superuser
    FIRST_SUPERUSER: str = "admin@banking.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    
    # Transaction limits
    DAILY_TRANSFER_LIMIT: float = 10000.0
    SINGLE_TRANSFER_LIMIT: float = 5000.0
    LARGE_TRANSACTION_THRESHOLD: float = 1000.0
    
    # Security settings
    PASSWORD_MIN_LENGTH: int = 8
    FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION: int = 300  # 5 minutes
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()