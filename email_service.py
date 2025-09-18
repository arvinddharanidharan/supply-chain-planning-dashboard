import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import io
import streamlit as st
from datetime import datetime

# Configuration
SUPERVISOR_EMAIL = "arvinddharanidharan3@gmail.com"  # Hardcoded supervisor email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def is_morning_alert_time():
    """Check if current time is 6:00 AM for automatic alerts"""
    current_time = datetime.now()
    return current_time.hour == 6 and current_time.minute == 0

def send_critical_alert_email(critical_count):
    """Send automatic critical alert notification with rate limiting"""
    try:
        # Check if we've sent too many emails today
        today_key = f"email_count_{datetime.now().strftime('%Y%m%d')}"
        email_count = st.session_state.get(today_key, 0)
        
        if email_count >= 10:  # Limit to 10 emails per day
            print("Debug: Daily email limit reached (10/day)")
            return False
            
        sender_email = st.secrets.get("EMAIL_USER", "")
        sender_password = st.secrets.get("EMAIL_PASSWORD", "")
        
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
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        # Update email count
        st.session_state[today_key] = email_count + 1
        print(f"Debug: Email sent successfully ({email_count + 1}/10 today)")
        
        return True
    except smtplib.SMTPAuthenticationError:
        print("Debug: Gmail authentication failed - check App Password")
        return False
    except smtplib.SMTPRecipientsRefused:
        print("Debug: Recipient email rejected")
        return False
    except smtplib.SMTPSenderRefused:
        print("Debug: Sender blocked - likely hit daily limit (150+ emails)")
        return False
    except Exception as e:
        print(f"Debug: Email error: {str(e)}")
        if "quota" in str(e).lower() or "limit" in str(e).lower():
            print("Debug: Gmail daily sending limit exceeded")
        return False

def send_critical_items_report(critical_items_df):
    """Send critical items list as attachment with rate limiting"""
    try:
        # Check daily email limit
        today_key = f"email_count_{datetime.now().strftime('%Y%m%d')}"
        email_count = st.session_state.get(today_key, 0)
        
        if email_count >= 10:
            print("Debug: Daily email limit reached for reports")
            return False
            
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
        
        # Update email count
        st.session_state[today_key] = email_count + 1
        print(f"Debug: Report sent successfully ({email_count + 1}/10 today)")
        
        return True
    except smtplib.SMTPSenderRefused as e:
        print(f"Debug: Gmail blocked sender - likely hit daily limit: {str(e)}")
        return False
    except Exception as e:
        print(f"Debug: Report email error: {str(e)}")
        return False
