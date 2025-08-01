from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum
import uuid


class TransactionType(str, enum.Enum):
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    INTEREST = "interest"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    reference_number = Column(String, unique=True, index=True, nullable=False)
    
    # Transaction details
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    
    # Accounts and users
    from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # External account details (for external transfers)
    external_account_number = Column(String, nullable=True)
    external_bank_name = Column(String, nullable=True)
    external_routing_number = Column(String, nullable=True)
    
    # Transaction metadata
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Fees and charges
    fee_amount = Column(Float, default=0.0, nullable=False)
    exchange_rate = Column(Float, default=1.0, nullable=False)
    
    # Security and compliance
    requires_approval = Column(Boolean, default=False, nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    fraud_score = Column(Float, default=0.0, nullable=False)
    is_flagged = Column(Boolean, default=False, nullable=False)
    
    # Processing details
    processed_at = Column(DateTime, nullable=True)
    failed_reason = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Scheduling (for recurring transactions)
    is_scheduled = Column(Boolean, default=False, nullable=False)
    scheduled_for = Column(DateTime, nullable=True)
    recurring_pattern = Column(String, nullable=True)  # daily, weekly, monthly, etc.
    parent_transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    from_account = relationship("Account", foreign_keys=[from_account_id], back_populates="transactions_from")
    to_account = relationship("Account", foreign_keys=[to_account_id], back_populates="transactions_to")
    sender = relationship("User", foreign_keys=[from_user_id], back_populates="transactions_sent")
    receiver = relationship("User", foreign_keys=[to_user_id], back_populates="transactions_received")
    approver = relationship("User", foreign_keys=[approved_by])
    parent_transaction = relationship("Transaction", remote_side=[id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
    
    @staticmethod
    def generate_transaction_id() -> str:
        """Generate unique transaction ID"""
        return f"TXN{uuid.uuid4().hex[:12].upper()}"
    
    @staticmethod
    def generate_reference_number() -> str:
        """Generate unique reference number"""
        import random
        return f"REF{random.randint(100000000000, 999999999999)}"
    
    @property
    def is_pending(self) -> bool:
        return self.status == TransactionStatus.PENDING
    
    @property
    def is_completed(self) -> bool:
        return self.status == TransactionStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        return self.status in [TransactionStatus.FAILED, TransactionStatus.CANCELLED, TransactionStatus.REJECTED]
    
    @property
    def total_amount(self) -> float:
        """Total amount including fees"""
        return self.amount + self.fee_amount
    
    @property
    def is_internal_transfer(self) -> bool:
        """Check if this is an internal transfer between accounts"""
        return self.from_account_id is not None and self.to_account_id is not None
    
    @property
    def is_external_transfer(self) -> bool:
        """Check if this is an external transfer"""
        return self.external_account_number is not None
    
    def mark_as_completed(self):
        """Mark transaction as completed"""
        self.status = TransactionStatus.COMPLETED
        self.processed_at = func.now()
    
    def mark_as_failed(self, reason: str):
        """Mark transaction as failed"""
        self.status = TransactionStatus.FAILED
        self.failed_reason = reason
        self.processed_at = func.now()
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.transaction_type}', amount={self.amount}, status='{self.status}')>"