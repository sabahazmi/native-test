from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from ..models.account import AccountType, AccountStatus


class AccountBase(BaseModel):
    name: str
    account_type: AccountType = AccountType.CHECKING
    description: Optional[str] = None
    currency: str = "USD"


class AccountCreate(AccountBase):
    daily_limit: Optional[float] = 5000.0
    monthly_limit: Optional[float] = 50000.0
    
    @validator('daily_limit', 'monthly_limit')
    def validate_limits(cls, v):
        if v is not None and v < 0:
            raise ValueError('Limits must be non-negative')
        return v


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    daily_limit: Optional[float] = None
    monthly_limit: Optional[float] = None
    requires_approval_above: Optional[float] = None
    
    @validator('daily_limit', 'monthly_limit', 'requires_approval_above')
    def validate_limits(cls, v):
        if v is not None and v < 0:
            raise ValueError('Limits must be non-negative')
        return v


class AccountInDBBase(AccountBase):
    id: int
    account_number: str
    status: AccountStatus
    user_id: int
    balance: float
    available_balance: float
    daily_limit: float
    monthly_limit: float
    interest_rate: float
    is_primary: bool
    requires_approval_above: float
    created_at: datetime
    updated_at: datetime
    last_activity: datetime
    last_interest_calculated: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class Account(AccountInDBBase):
    pass


class AccountSummary(BaseModel):
    id: int
    account_number: str
    name: str
    account_type: AccountType
    balance: float
    available_balance: float
    currency: str
    is_primary: bool
    
    class Config:
        orm_mode = True


class AccountDetails(AccountInDBBase):
    transaction_count: Optional[int] = 0
    monthly_spending: Optional[float] = 0.0
    monthly_income: Optional[float] = 0.0


class AccountBalance(BaseModel):
    account_id: int
    balance: float
    available_balance: float
    currency: str
    last_updated: datetime
    
    class Config:
        orm_mode = True


class AccountLimits(BaseModel):
    daily_limit: float
    monthly_limit: float
    daily_used: float
    monthly_used: float
    daily_remaining: float
    monthly_remaining: float


class AccountStats(BaseModel):
    total_accounts: int
    active_accounts: int
    total_balance: float
    average_balance: float
    accounts_by_type: dict
    new_accounts_today: int
    new_accounts_this_week: int
    new_accounts_this_month: int
    
    class Config:
        orm_mode = True