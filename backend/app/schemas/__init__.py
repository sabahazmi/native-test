from .user import (
    User, UserCreate, UserUpdate, UserLogin, UserRegister, 
    UserPasswordChange, UserPublic, UserAdmin, UserStats,
    PasswordReset, PasswordResetConfirm, TwoFactorSetup, TwoFactorVerify
)
from .account import (
    Account, AccountCreate, AccountUpdate, AccountSummary, 
    AccountDetails, AccountBalance, AccountLimits, AccountStats
)
from .transaction import (
    Transaction, TransactionCreate, TransactionUpdate, TransactionApproval,
    TransactionSummary, TransactionDetails, TransferRequest, 
    DepositRequest, WithdrawalRequest, TransactionFilter, TransactionStats
)
from .notification import (
    Notification, NotificationCreate, NotificationUpdate, NotificationSummary,
    NotificationMarkRead, NotificationPreferences, NotificationStats
)
from .auth import (
    Token, TokenData, RefreshToken, LoginResponse, LogoutResponse,
    PasswordResetRequest, PasswordResetResponse, TwoFactorAuthSetup,
    TwoFactorAuthVerify, SessionInfo
)

# Common response schemas
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class APIResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: Optional[List[str]] = None
    error_code: Optional[str] = None


__all__ = [
    # User schemas
    "User", "UserCreate", "UserUpdate", "UserLogin", "UserRegister",
    "UserPasswordChange", "UserPublic", "UserAdmin", "UserStats",
    "PasswordReset", "PasswordResetConfirm", "TwoFactorSetup", "TwoFactorVerify",
    
    # Account schemas
    "Account", "AccountCreate", "AccountUpdate", "AccountSummary",
    "AccountDetails", "AccountBalance", "AccountLimits", "AccountStats",
    
    # Transaction schemas
    "Transaction", "TransactionCreate", "TransactionUpdate", "TransactionApproval",
    "TransactionSummary", "TransactionDetails", "TransferRequest",
    "DepositRequest", "WithdrawalRequest", "TransactionFilter", "TransactionStats",
    
    # Notification schemas
    "Notification", "NotificationCreate", "NotificationUpdate", "NotificationSummary",
    "NotificationMarkRead", "NotificationPreferences", "NotificationStats",
    
    # Auth schemas
    "Token", "TokenData", "RefreshToken", "LoginResponse", "LogoutResponse",
    "PasswordResetRequest", "PasswordResetResponse", "TwoFactorAuthSetup",
    "TwoFactorAuthVerify", "SessionInfo",
    
    # Common schemas
    "APIResponse", "PaginatedResponse", "ErrorResponse",
]