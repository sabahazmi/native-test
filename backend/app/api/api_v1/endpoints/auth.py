from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Any

from ....core.database import get_db
from ....core.security import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, verify_token, generate_password_reset_token,
    verify_password_reset_token, validate_password_strength
)
from ....models.user import User, UserRole, UserStatus
from ....models.audit_log import AuditLog, AuditAction, AuditLevel
from ....schemas import (
    UserLogin, UserRegister, LoginResponse, Token, RefreshToken,
    PasswordResetRequest, PasswordResetResponse, PasswordResetConfirm,
    APIResponse, UserCreate, User as UserSchema
)
from ....utils.dependencies import (
    get_current_user, get_client_ip, get_user_agent, get_redis_client,
    check_rate_limit
)
from ....core.config import settings
import redis
import json

router = APIRouter()


@router.post("/register", response_model=APIResponse)
async def register(
    user_data: UserRegister,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    _: Any = Depends(check_rate_limit)
):
    """Register a new user"""
    
    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Validate password strength
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log the registration
    audit_log = AuditLog.create_log(
        action=AuditAction.LOGIN,
        description=f"User registered: {user_data.email}",
        user_id=db_user.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    db.add(audit_log)
    db.commit()
    
    # TODO: Send verification email in background task
    
    return APIResponse(
        success=True,
        message="User registered successfully. Please check your email for verification.",
        data={"user_id": db_user.id}
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    _: Any = Depends(check_rate_limit)
):
    """Authenticate user and return JWT tokens"""
    
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Get user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user:
        # Log failed login attempt
        audit_log = AuditLog.create_log(
            action=AuditAction.LOGIN_FAILED,
            description=f"Login failed: User not found for email {user_credentials.email}",
            level=AuditLevel.WARNING,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False
        )
        db.add(audit_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if account is locked
    if user.is_locked:
        audit_log = AuditLog.create_log(
            action=AuditAction.LOGIN_FAILED,
            description=f"Login failed: Account locked for user {user.email}",
            user_id=user.id,
            level=AuditLevel.WARNING,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False
        )
        db.add(audit_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is locked. Please contact support."
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user.hashed_password):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        
        # Lock account if too many failed attempts
        if user.failed_login_attempts >= settings.FAILED_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(
                seconds=settings.ACCOUNT_LOCKOUT_DURATION
            )
            user.status = UserStatus.LOCKED
        
        db.commit()
        
        # Log failed login attempt
        audit_log = AuditLog.create_log(
            action=AuditAction.LOGIN_FAILED,
            description=f"Login failed: Incorrect password for user {user.email}",
            user_id=user.id,
            level=AuditLevel.WARNING,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False
        )
        db.add(audit_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Reset failed login attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    if user.status == UserStatus.LOCKED:
        user.status = UserStatus.ACTIVE
    
    db.commit()
    
    # Create tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    # Store refresh token in Redis
    redis_client.setex(
        f"refresh_token:{user.id}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        refresh_token
    )
    
    # Log successful login
    audit_log = AuditLog.create_log(
        action=AuditAction.LOGIN,
        description=f"User logged in successfully: {user.email}",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_verified": user.is_verified
        }
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshToken,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """Refresh access token using refresh token"""
    
    # Verify refresh token
    user_id = verify_token(token_data.refresh_token, token_type="refresh")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if refresh token exists in Redis
    stored_token = redis_client.get(f"refresh_token:{user_id}")
    if not stored_token or stored_token != token_data.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    new_access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)
    
    # Update refresh token in Redis
    redis_client.setex(
        f"refresh_token:{user.id}",
        settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        new_refresh_token
    )
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        role=user.role
    )


@router.post("/logout", response_model=APIResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client),
    db: Session = Depends(get_db)
):
    """Logout user and invalidate tokens"""
    
    # Remove refresh token from Redis
    redis_client.delete(f"refresh_token:{current_user.id}")
    
    # Log logout
    audit_log = AuditLog.create_log(
        action=AuditAction.LOGOUT,
        description=f"User logged out: {current_user.email}",
        user_id=current_user.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    db.add(audit_log)
    db.commit()
    
    return APIResponse(
        success=True,
        message="Successfully logged out"
    )


@router.post("/password-reset", response_model=PasswordResetResponse)
async def password_reset_request(
    request_data: PasswordResetRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: Any = Depends(check_rate_limit)
):
    """Request password reset"""
    
    user = db.query(User).filter(User.email == request_data.email).first()
    
    # Always return success to prevent email enumeration
    if user:
        # Generate reset token
        reset_token = generate_password_reset_token(user.email)
        
        # TODO: Send password reset email in background task
        # background_tasks.add_task(send_password_reset_email, user.email, reset_token)
        
        # Log password reset request
        audit_log = AuditLog.create_log(
            action=AuditAction.PASSWORD_CHANGE,
            description=f"Password reset requested for user: {user.email}",
            user_id=user.id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        db.add(audit_log)
        db.commit()
    
    return PasswordResetResponse()


@router.post("/password-reset/confirm", response_model=APIResponse)
async def password_reset_confirm(
    reset_data: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token"""
    
    # Verify reset token
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate new password
    if not validate_password_strength(reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements"
        )
    
    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.password_changed_at = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None
    
    db.commit()
    
    # Log password change
    audit_log = AuditLog.create_log(
        action=AuditAction.PASSWORD_CHANGE,
        description=f"Password reset completed for user: {user.email}",
        user_id=user.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    db.add(audit_log)
    db.commit()
    
    return APIResponse(
        success=True,
        message="Password reset successfully"
    )


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user