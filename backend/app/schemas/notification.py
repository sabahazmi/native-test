from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.notification import NotificationType, NotificationPriority, NotificationChannel


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM


class NotificationCreate(NotificationBase):
    user_id: int
    channels: List[NotificationChannel]
    transaction_id: Optional[int] = None
    account_id: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    priority: Optional[NotificationPriority] = None
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class NotificationInDBBase(NotificationBase):
    id: int
    user_id: int
    channels: List[str]
    is_read: bool
    is_sent: bool
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    transaction_id: Optional[int] = None
    account_id: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class Notification(NotificationInDBBase):
    pass


class NotificationSummary(BaseModel):
    id: int
    title: str
    notification_type: NotificationType
    priority: NotificationPriority
    is_read: bool
    created_at: datetime
    action_url: Optional[str] = None
    
    class Config:
        orm_mode = True


class NotificationMarkRead(BaseModel):
    notification_ids: List[int]


class NotificationPreferences(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    transaction_notifications: bool = True
    security_notifications: bool = True
    account_notifications: bool = True
    system_notifications: bool = True
    marketing_notifications: bool = False


class NotificationStats(BaseModel):
    total_notifications: int
    unread_notifications: int
    notifications_by_type: Dict[str, int]
    notifications_by_priority: Dict[str, int]
    notifications_today: int
    notifications_this_week: int
    notifications_this_month: int
    
    class Config:
        orm_mode = True