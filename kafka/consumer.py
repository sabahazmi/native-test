import json
import asyncio
import logging
from kafka import KafkaConsumer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://banking_user:banking_password@postgres:5432/banking_db')
REDIS_URL = os.getenv('REDIS_URL', 'redis://:redis_password@redis:6379')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis setup
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

class BankingKafkaConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            'transactions',
            'notifications',
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='banking-consumers',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None
        )
        
    def process_transaction_event(self, message):
        """Process transaction-related events"""
        try:
            data = message.value
            event_type = data.get('event_type')
            transaction_data = data.get('transaction')
            
            logger.info(f"Processing transaction event: {event_type}")
            
            if event_type == 'transaction_created':
                self.handle_transaction_created(transaction_data)
            elif event_type == 'transaction_completed':
                self.handle_transaction_completed(transaction_data)
            elif event_type == 'transaction_failed':
                self.handle_transaction_failed(transaction_data)
            elif event_type == 'large_transaction_detected':
                self.handle_large_transaction(transaction_data)
            elif event_type == 'suspicious_activity':
                self.handle_suspicious_activity(transaction_data)
                
        except Exception as e:
            logger.error(f"Error processing transaction event: {e}")
    
    def process_notification_event(self, message):
        """Process notification events"""
        try:
            data = message.value
            event_type = data.get('event_type')
            notification_data = data.get('notification')
            
            logger.info(f"Processing notification event: {event_type}")
            
            if event_type == 'send_notification':
                self.send_notification(notification_data)
            elif event_type == 'send_email':
                self.send_email_notification(notification_data)
            elif event_type == 'send_sms':
                self.send_sms_notification(notification_data)
                
        except Exception as e:
            logger.error(f"Error processing notification event: {e}")
    
    def handle_transaction_created(self, transaction_data):
        """Handle new transaction creation"""
        transaction_id = transaction_data.get('id')
        amount = transaction_data.get('amount')
        user_id = transaction_data.get('from_user_id')
        
        # Update account balances in cache
        from_account_id = transaction_data.get('from_account_id')
        to_account_id = transaction_data.get('to_account_id')
        
        if from_account_id:
            # Deduct from sender's account
            self.update_account_balance_cache(from_account_id, -amount)
        
        if to_account_id:
            # Add to receiver's account
            self.update_account_balance_cache(to_account_id, amount)
        
        # Send real-time notification to user
        self.send_realtime_notification(user_id, {
            'type': 'transaction_created',
            'message': f'Transaction of ${amount} has been initiated',
            'transaction_id': transaction_id
        })
        
        logger.info(f"Processed transaction creation: {transaction_id}")
    
    def handle_transaction_completed(self, transaction_data):
        """Handle transaction completion"""
        transaction_id = transaction_data.get('id')
        amount = transaction_data.get('amount')
        user_id = transaction_data.get('from_user_id')
        
        # Send completion notification
        self.send_realtime_notification(user_id, {
            'type': 'transaction_completed',
            'message': f'Transaction of ${amount} has been completed successfully',
            'transaction_id': transaction_id
        })
        
        # Update transaction status in cache
        redis_client.hset(f"transaction:{transaction_id}", "status", "completed")
        
        logger.info(f"Processed transaction completion: {transaction_id}")
    
    def handle_transaction_failed(self, transaction_data):
        """Handle transaction failure"""
        transaction_id = transaction_data.get('id')
        amount = transaction_data.get('amount')
        user_id = transaction_data.get('from_user_id')
        reason = transaction_data.get('failed_reason', 'Unknown error')
        
        # Reverse balance changes if needed
        from_account_id = transaction_data.get('from_account_id')
        if from_account_id:
            self.update_account_balance_cache(from_account_id, amount)  # Add back
        
        # Send failure notification
        self.send_realtime_notification(user_id, {
            'type': 'transaction_failed',
            'message': f'Transaction of ${amount} failed: {reason}',
            'transaction_id': transaction_id
        })
        
        logger.info(f"Processed transaction failure: {transaction_id}")
    
    def handle_large_transaction(self, transaction_data):
        """Handle large transaction that needs approval"""
        transaction_id = transaction_data.get('id')
        amount = transaction_data.get('amount')
        user_id = transaction_data.get('from_user_id')
        
        # Notify user about approval requirement
        self.send_realtime_notification(user_id, {
            'type': 'transaction_pending_approval',
            'message': f'Large transaction of ${amount} requires approval',
            'transaction_id': transaction_id
        })
        
        # Notify admins
        self.notify_admins_about_large_transaction(transaction_data)
        
        logger.info(f"Processed large transaction: {transaction_id}")
    
    def handle_suspicious_activity(self, transaction_data):
        """Handle suspicious activity detection"""
        transaction_id = transaction_data.get('id')
        user_id = transaction_data.get('from_user_id')
        fraud_score = transaction_data.get('fraud_score', 0)
        
        # Alert security team
        self.alert_security_team(transaction_data)
        
        # Notify user if needed
        if fraud_score > 0.7:  # High risk
            self.send_realtime_notification(user_id, {
                'type': 'security_alert',
                'message': 'Unusual activity detected on your account. Please verify your recent transactions.',
                'transaction_id': transaction_id,
                'priority': 'high'
            })
        
        logger.warning(f"Processed suspicious activity: {transaction_id}, fraud_score: {fraud_score}")
    
    def send_notification(self, notification_data):
        """Send in-app notification"""
        user_id = notification_data.get('user_id')
        title = notification_data.get('title')
        message = notification_data.get('message')
        
        # Store notification in database (would need to import models)
        # For now, just cache it
        notification_id = f"notification:{user_id}:{datetime.now().timestamp()}"
        redis_client.hset(notification_id, mapping={
            'user_id': user_id,
            'title': title,
            'message': message,
            'created_at': datetime.now().isoformat(),
            'is_read': False
        })
        
        # Send real-time notification
        self.send_realtime_notification(user_id, {
            'type': 'new_notification',
            'title': title,
            'message': message
        })
        
        logger.info(f"Sent notification to user {user_id}")
    
    def send_email_notification(self, notification_data):
        """Send email notification"""
        email = notification_data.get('email')
        subject = notification_data.get('subject')
        body = notification_data.get('body')
        
        # TODO: Implement actual email sending
        # For now, just log it
        logger.info(f"Would send email to {email}: {subject}")
    
    def send_sms_notification(self, notification_data):
        """Send SMS notification"""
        phone = notification_data.get('phone')
        message = notification_data.get('message')
        
        # TODO: Implement actual SMS sending
        # For now, just log it
        logger.info(f"Would send SMS to {phone}: {message}")
    
    def update_account_balance_cache(self, account_id, amount_change):
        """Update account balance in Redis cache"""
        try:
            current_balance = redis_client.hget(f"account:{account_id}", "balance")
            if current_balance:
                new_balance = float(current_balance) + amount_change
                redis_client.hset(f"account:{account_id}", "balance", new_balance)
                logger.info(f"Updated account {account_id} balance by {amount_change}")
        except Exception as e:
            logger.error(f"Error updating account balance cache: {e}")
    
    def send_realtime_notification(self, user_id, notification):
        """Send real-time notification via WebSocket (through Redis pub/sub)"""
        try:
            channel = f"user:{user_id}:notifications"
            redis_client.publish(channel, json.dumps(notification))
            logger.info(f"Sent real-time notification to user {user_id}")
        except Exception as e:
            logger.error(f"Error sending real-time notification: {e}")
    
    def notify_admins_about_large_transaction(self, transaction_data):
        """Notify administrators about large transactions"""
        # Get admin user IDs from cache or database
        admin_channel = "admins:notifications"
        notification = {
            'type': 'large_transaction_alert',
            'transaction_id': transaction_data.get('id'),
            'amount': transaction_data.get('amount'),
            'from_user_id': transaction_data.get('from_user_id'),
            'timestamp': datetime.now().isoformat()
        }
        redis_client.publish(admin_channel, json.dumps(notification))
        logger.info("Notified admins about large transaction")
    
    def alert_security_team(self, transaction_data):
        """Alert security team about suspicious activity"""
        security_channel = "security:alerts"
        alert = {
            'type': 'suspicious_activity',
            'transaction_id': transaction_data.get('id'),
            'fraud_score': transaction_data.get('fraud_score'),
            'user_id': transaction_data.get('from_user_id'),
            'timestamp': datetime.now().isoformat()
        }
        redis_client.publish(security_channel, json.dumps(alert))
        logger.warning("Alerted security team about suspicious activity")
    
    def run(self):
        """Run the Kafka consumer"""
        logger.info("Starting Kafka consumer...")
        
        try:
            for message in self.consumer:
                topic = message.topic
                
                if topic == 'transactions':
                    self.process_transaction_event(message)
                elif topic == 'notifications':
                    self.process_notification_event(message)
                else:
                    logger.warning(f"Unknown topic: {topic}")
                    
        except KeyboardInterrupt:
            logger.info("Shutting down consumer...")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            self.consumer.close()


if __name__ == "__main__":
    consumer = BankingKafkaConsumer()
    consumer.run()