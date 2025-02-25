import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

def send_support_email(subject: str, body: str) -> bool:
    """
    发送客服支持邮件
    
    @param subject: 邮件主题
    @param body: 邮件内容
    @return: 是否发送成功
    """
    try:
        sender_email = os.getenv("SENDER_EMAIL")
        receiver_email = os.getenv("RECEIVER_EMAIL")
        password = os.getenv("EMAIL_PASSWORD")
        
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email
        
        with smtplib.SMTP("smtp.example.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            
        return True
        
    except Exception as e:
        logger.error(f"发送邮件失败: {str(e)}")
        return False 