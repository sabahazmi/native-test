from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.transaction import TransactionType, TransactionStatus


class TransactionBase(BaseModel):
    amount: float
    currency: str = "USD"
    description: Optional[str] = None
    notes: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)


class TransactionCreate(TransactionBase):
    transaction_type: TransactionType
    to_account_id: Optional[int] = None
    external_account_number: Optional[str] = None
    external_bank_name: Optional[str] = None
    external_routing_number: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    recurring_pattern: Optional[str] = None
    
    @validator('to_account_id', 'external_account_number')
    def validate_destination(cls, v, values):
        # Must have either internal account or external account details
        if 'to_account_id' in values and 'external_account_number' in values:
            if not values.get('to_account_id') and not values.get('external_account_number'):
                raise ValueError('Must specify either internal account or external account')
        return v


class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    notes: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class TransactionApproval(BaseModel):
    approved: bool
    notes: Optional[str] = None


class TransactionInDBBase(TransactionBase):
    id: int
    transaction_id: str
    reference_number: str
    transaction_type: TransactionType
    status: TransactionStatus
    from_account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    from_user_id: Optional[int] = None
    to_user_id: Optional[int] = None
    external_account_number: Optional[str] = None
    external_bank_name: Optional[str] = None
    external_routing_number: Optional[str] = None
    fee_amount: float
    exchange_rate: float
    requires_approval: bool
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    fraud_score: float
    is_flagged: bool
    processed_at: Optional[datetime] = None
    failed_reason: Optional[str] = None
    retry_count: int
    is_scheduled: bool
    scheduled_for: Optional[datetime] = None
    recurring_pattern: Optional[str] = None
    parent_transaction_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class Transaction(TransactionInDBBase):
    pass


class TransactionSummary(BaseModel):
    id: int
    transaction_id: str
    transaction_type: TransactionType
    status: TransactionStatus
    amount: float
    currency: str
    description: Optional[str] = None
    created_at: datetime
    from_account_number: Optional[str] = None
    to_account_number: Optional[str] = None
    
    class Config:
        orm_mode = True


class TransactionDetails(TransactionInDBBase):
    from_account_name: Optional[str] = None
    to_account_name: Optional[str] = None
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
    approver_name: Optional[str] = None


class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: Optional[int] = None
    external_account_number: Optional[str] = None
    external_bank_name: Optional[str] = None
    external_routing_number: Optional[str] = None
    amount: float
    description: Optional[str] = None
    notes: Optional[str] = None
    category: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)
    
    @validator('to_account_id', 'external_account_number')
    def validate_destination(cls, v, values):
        if 'to_account_id' in values and 'external_account_number' in values:
            if not values.get('to_account_id') and not values.get('external_account_number'):
                raise ValueError('Must specify either internal account or external account')
        return v


class DepositRequest(BaseModel):
    account_id: int
    amount: float
    description: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)


class WithdrawalRequest(BaseModel):
    account_id: int
    amount: float
    description: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)


class TransactionFilter(BaseModel):
    account_id: Optional[int] = None
    transaction_type: Optional[TransactionType] = None
    status: Optional[TransactionStatus] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    search: Optional[str] = None
    page: int = 1
    per_page: int = 20


class TransactionStats(BaseModel):
    total_transactions: int
    total_volume: float
    pending_transactions: int
    pending_volume: float
    completed_transactions: int
    completed_volume: float
    failed_transactions: int
    failed_volume: float
    transactions_by_type: Dict[str, int]
    volume_by_type: Dict[str, float]
    transactions_today: int
    volume_today: float
    transactions_this_week: int
    volume_this_week: float
    transactions_this_month: int
    volume_this_month: float
    
    class Config:
        orm_mode = True