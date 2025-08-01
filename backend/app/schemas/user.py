from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from ..models.user import UserRole, UserStatus


class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase, lowercase, digit, and special character
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character')
        
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None


class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character')
        
        return v


class UserInDBBase(UserBase):
    id: int
    role: UserRole
    status: UserStatus
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
    failed_login_attempts: int
    locked_until: Optional[datetime] = None
    password_changed_at: datetime
    two_factor_secret: Optional[str] = None
    backup_codes: Optional[str] = None


class UserPublic(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    
    class Config:
        orm_mode = True


class UserAdmin(UserInDBBase):
    failed_login_attempts: int
    locked_until: Optional[datetime] = None
    password_changed_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class UserRegister(UserCreate):
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class TwoFactorSetup(BaseModel):
    secret: str
    code: str


class TwoFactorVerify(BaseModel):
    code: str


class UserStats(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    locked_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    
    class Config:
        orm_mode = True