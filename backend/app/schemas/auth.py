from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    role: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class RefreshToken(BaseModel):
    refresh_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict
    
    
class LogoutResponse(BaseModel):
    message: str = "Successfully logged out"


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetResponse(BaseModel):
    message: str = "Password reset email sent"


class TwoFactorAuthSetup(BaseModel):
    secret_key: str
    qr_code_url: str
    backup_codes: list


class TwoFactorAuthVerify(BaseModel):
    token: str
    backup_code: Optional[str] = None


class SessionInfo(BaseModel):
    user_id: int
    session_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool