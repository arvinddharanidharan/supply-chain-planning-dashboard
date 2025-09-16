import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import io
import streamlit as st

# Configuration
SUPERVISOR_EMAIL = "jamalahmedkashmiri@gmail.com"  # Hardcoded supervisor email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_critical_alert_email(critical_count):
    """Send automatic critical alert notification"""
    try:
        # Use Gmail App Password or free email service
        sender_email = st.secrets.get("EMAIL_USER", "")
        sender_password = st.secrets.get("EMAIL_PASSWORD", "")
        
        print(f"Debug: Email user: {sender_email[:5]}...")
        print(f"Debug: Password configured: {bool(sender_password)}")
        
        if not sender_email or not sender_password:
            print("Debug: Missing email credentials")
            return False
            
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = SUPERVISOR_EMAIL
        msg['Subject'] = f"CRITICAL ALERT: {critical_count} Items at Critical Stock Levels"
        
        body = f"""
URGENT: Critical Stock Alert

{critical_count} items have reached critical stock levels and require immediate attention.

Please log into the Supply Chain Dashboard to review and take action.

This is an automated alert from the Supply Chain Planning Dashboard.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        print("Debug: Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        print("Debug: Logging in...")
        server.login(sender_email, sender_password)
        print("Debug: Sending message...")
        result = server.send_message(msg)
        server.quit()
        print(f"Debug: Email sent successfully to {SUPERVISOR_EMAIL}")
        print("Debug: Check spam/junk folder if not received")
        
        return True
    except Exception as e:
        print(f"Debug: Email error: {str(e)}")
        return False

def send_critical_items_report(critical_items_df):
    """Send critical items list as attachment"""
    try:
        sender_email = st.secrets.get("EMAIL_USER", "")
        sender_password = st.secrets.get("EMAIL_PASSWORD", "")
        
        if not sender_email or not sender_password:
            print("Debug: Missing email credentials for report")
            return False
            
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = SUPERVISOR_EMAIL
        msg['Subject'] = "Critical Items Report - Immediate Action Required"
        
        body = f"""
        Critical Items Report
        
        Please find attached the detailed list of {len(critical_items_df)} items at critical stock levels.
        
        Immediate action required to prevent stockouts.
        
        Supply Chain Planning Dashboard
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create CSV attachment
        csv_buffer = io.StringIO()
        critical_items_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue().encode()
        
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(csv_data)
        encoders.encode_base64(attachment)
        attachment.add_header(
            'Content-Disposition',
            'attachment; filename="critical_items_report.csv"'
        )
        msg.attach(attachment)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return True
    except:
        return False