from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class NotificationType(str, enum.Enum):
    TRANSACTION = "transaction"
    SECURITY = "security"
    ACCOUNT = "account"
    SYSTEM = "system"
    MARKETING = "marketing"
    REMINDER = "reminder"


class NotificationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notification details
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM, nullable=False)
    
    # Delivery
    channels = Column(JSON, nullable=False)  # Array of channels
    is_read = Column(Boolean, default=False, nullable=False)
    is_sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Related entities
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    
    # Metadata
    data = Column(JSON, nullable=True)  # Additional data for the notification
    action_url = Column(String, nullable=True)  # URL for action button
    expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    transaction = relationship("Transaction")
    account = relationship("Account")
    
    @property
    def is_expired(self) -> bool:
        """Check if notification is expired"""
        if self.expires_at is None:
            return False
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_urgent(self) -> bool:
        """Check if notification is urgent"""
        return self.priority == NotificationPriority.URGENT
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = func.now()
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.is_sent = True
        self.sent_at = func.now()
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type}', title='{self.title}')>"