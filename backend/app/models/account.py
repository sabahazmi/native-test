from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum
import uuid


class AccountType(str, enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    BUSINESS = "business"
    INVESTMENT = "investment"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    CLOSED = "closed"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True, nullable=False)
    account_type = Column(Enum(AccountType), default=AccountType.CHECKING, nullable=False)
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False)
    
    # Owner
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Balance and limits
    balance = Column(Float, default=0.0, nullable=False)
    available_balance = Column(Float, default=0.0, nullable=False)  # Balance minus pending transactions
    daily_limit = Column(Float, default=5000.0, nullable=False)
    monthly_limit = Column(Float, default=50000.0, nullable=False)
    
    # Account details
    name = Column(String, nullable=False)  # Account nickname
    description = Column(Text, nullable=True)
    currency = Column(String, default="USD", nullable=False)
    
    # Interest (for savings accounts)
    interest_rate = Column(Float, default=0.0, nullable=False)
    last_interest_calculated = Column(DateTime, nullable=True)
    
    # Security
    is_primary = Column(Boolean, default=False, nullable=False)
    requires_approval_above = Column(Float, default=1000.0, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_activity = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="accounts")
    transactions_from = relationship("Transaction", foreign_keys="Transaction.from_account_id", back_populates="from_account")
    transactions_to = relationship("Transaction", foreign_keys="Transaction.to_account_id", back_populates="to_account")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.account_number:
            self.account_number = self.generate_account_number()
    
    @staticmethod
    def generate_account_number() -> str:
        """Generate unique account number"""
        import random
        return f"ACC{random.randint(1000000000, 9999999999)}"
    
    @property
    def is_active(self) -> bool:
        return self.status == AccountStatus.ACTIVE
    
    @property
    def can_transact(self) -> bool:
        return self.status in [AccountStatus.ACTIVE]
    
    def update_balance(self, amount: float, transaction_type: str = "credit"):
        """Update account balance"""
        if transaction_type == "credit":
            self.balance += amount
            self.available_balance += amount
        elif transaction_type == "debit":
            self.balance -= amount
            self.available_balance -= amount
        
        self.last_activity = func.now()
    
    def has_sufficient_funds(self, amount: float) -> bool:
        """Check if account has sufficient funds"""
        return self.available_balance >= amount
    
    def __repr__(self):
        return f"<Account(id={self.id}, number='{self.account_number}', balance={self.balance})>"