import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import requests
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class AlertService:
    """Service for sending alerts via email and SMS"""
    
    def __init__(self):
        self.email_enabled = settings.EMAIL_ENABLED
        self.sms_enabled = settings.SMS_ENABLED
        self.threshold = settings.ALERT_THRESHOLD
        self.time_window = settings.ALERT_TIME_WINDOW
    
    def send_alert(self, message: str, alert_type: str = "sentiment_spike"):
        """Send alert through configured channels"""
        logger.info(f"Alert triggered: {message}")
        
        if self.email_enabled:
            self._send_email_alert(message, alert_type)
        
        if self.sms_enabled:
            self._send_sms_alert(message)
    
    def _send_email_alert(self, message: str, alert_type: str):
        """Send email alert"""
        try:
            # Configure email settings
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "alerts@yourcompany.com"
            sender_password = "your-app-password"  # Use environment variable
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ", ".join(settings.notification_emails)
            msg['Subject'] = f"Sentiment Alert: {alert_type}"
            
            # Add body
            body = f"""
            <h2>Sentiment Alert Triggered</h2>
            <p><strong>Time:</strong> {datetime.utcnow()}</p>
            <p><strong>Type:</strong> {alert_type}</p>
            <p><strong>Message:</strong> {message}</p>
            <p><strong>Threshold:</strong> {self.threshold:.1%}</p>
            <p><strong>Time Window:</strong> {self.time_window} minutes</p>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            logger.info("Email alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_sms_alert(self, message: str):
        """Send SMS alert using Africa's Talking or similar service"""
        try:
            # Example using Africa's Talking API
            url = "https://api.africastalking.com/version1/messaging"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "apiKey": "your-api-key"  # Use environment variable
            }
            
            data = {
                "username": "sandbox",
                "to": ",".join(settings.phone_numbers),
                "message": f"Sentiment Alert: {message[:140]}"  # SMS length limit
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 201:
                logger.info("SMS alert sent successfully")
            else:
                logger.error(f"SMS sending failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {e}")