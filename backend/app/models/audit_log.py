from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class AuditAction(str, enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PROFILE_UPDATE = "profile_update"
    ACCOUNT_CREATE = "account_create"
    ACCOUNT_UPDATE = "account_update"
    TRANSACTION_CREATE = "transaction_create"
    TRANSACTION_APPROVE = "transaction_approve"
    TRANSACTION_REJECT = "transaction_reject"
    TRANSFER_INITIATE = "transfer_initiate"
    TRANSFER_COMPLETE = "transfer_complete"
    TRANSFER_FAIL = "transfer_fail"
    SETTINGS_CHANGE = "settings_change"
    TWO_FA_ENABLE = "two_fa_enable"
    TWO_FA_DISABLE = "two_fa_disable"
    API_ACCESS = "api_access"
    ADMIN_ACTION = "admin_action"
    SECURITY_ALERT = "security_alert"
    SYSTEM_ERROR = "system_error"


class AuditLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # User and session
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String, nullable=True)
    
    # Action details
    action = Column(Enum(AuditAction), nullable=False)
    level = Column(Enum(AuditLevel), default=AuditLevel.INFO, nullable=False)
    description = Column(Text, nullable=False)
    
    # Request details
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String, nullable=True)
    method = Column(String, nullable=True)
    
    # Related entities
    resource_type = Column(String, nullable=True)  # e.g., "account", "transaction"
    resource_id = Column(String, nullable=True)
    
    # Additional context
    metadata = Column(JSON, nullable=True)  # Additional data about the action
    old_values = Column(JSON, nullable=True)  # Previous values (for updates)
    new_values = Column(JSON, nullable=True)  # New values (for updates)
    
    # Status and result
    success = Column(String, nullable=False, default=True)  # Boolean as string for JSON compatibility
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    @property
    def is_security_event(self) -> bool:
        """Check if this is a security-related event"""
        security_actions = [
            AuditAction.LOGIN_FAILED,
            AuditAction.PASSWORD_CHANGE,
            AuditAction.TWO_FA_ENABLE,
            AuditAction.TWO_FA_DISABLE,
            AuditAction.SECURITY_ALERT
        ]
        return self.action in security_actions
    
    @property
    def is_critical(self) -> bool:
        """Check if this is a critical event"""
        return self.level == AuditLevel.CRITICAL
    
    @property
    def is_error(self) -> bool:
        """Check if this represents an error"""
        return self.level in [AuditLevel.ERROR, AuditLevel.CRITICAL]
    
    @classmethod
    def create_log(
        cls,
        action: AuditAction,
        description: str,
        user_id: int = None,
        level: AuditLevel = AuditLevel.INFO,
        ip_address: str = None,
        user_agent: str = None,
        endpoint: str = None,
        method: str = None,
        resource_type: str = None,
        resource_id: str = None,
        metadata: dict = None,
        success: bool = True,
        error_message: str = None
    ):
        """Create a new audit log entry"""
        return cls(
            action=action,
            description=description,
            user_id=user_id,
            level=level,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
            success=str(success),
            error_message=error_message
        )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"