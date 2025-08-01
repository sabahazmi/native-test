from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from ..core.database import get_db
from ..core.security import verify_token
from ..models.user import User, UserRole
from ..schemas.auth import TokenData
import redis
from ..core.config import settings


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        user_id = verify_token(token)
        if user_id is None:
            raise credentials_exception
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise credentials_exception
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
            
        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is locked"
            )
            
        return user
        
    except Exception:
        raise credentials_exception


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_manager_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current manager or admin user"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    if credentials is None:
        return None
        
    try:
        token = credentials.credentials
        user_id = verify_token(token)
        if user_id is None:
            return None
            
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None or not user.is_active or user.is_locked:
            return None
            
        return user
        
    except Exception:
        return None


def get_redis_client():
    """Get Redis client"""
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
        
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent string"""
    return request.headers.get("User-Agent", "unknown")


def require_verification(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be verified"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user


def check_rate_limit(
    request: Request,
    redis_client=Depends(get_redis_client),
    limit: int = 60,
    window: int = 60
) -> bool:
    """Check rate limit for requests"""
    client_ip = get_client_ip(request)
    key = f"rate_limit:{client_ip}"
    
    try:
        current = redis_client.get(key)
        if current is None:
            redis_client.setex(key, window, 1)
            return True
        
        if int(current) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        redis_client.incr(key)
        return True
        
    except redis.RedisError:
        # If Redis is down, allow the request
        return True