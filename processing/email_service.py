"""
Email service — no Streamlit dependency.
Reads SMTP credentials from environment variables or a local .env file.
Set EMAIL_SENDER and EMAIL_PASSWORD in your environment (or .env) before running.
"""
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Hard-coded fallback credentials (override via environment for production)
_DEFAULT_SENDER   = "novaflixteam@gmail.com"
_DEFAULT_PASSWORD = "hjkp zuxh ixip bvoy"          # app-password


def generate_otp() -> str:
    """Generate a random 6-digit verification code."""
    return str(random.randint(100000, 999999))


def _get_credentials():
    """Return (sender_email, sender_password) from env or hardcoded defaults."""
    sender_email    = os.environ.get("EMAIL_SENDER",   _DEFAULT_SENDER)
    sender_password = os.environ.get("EMAIL_PASSWORD", _DEFAULT_PASSWORD)
    return sender_email, sender_password


def send_otp_email(receiver_email: str, otp: str):
    """
    Send a 6-digit OTP email via Gmail SMTP.
    Returns (True, message) on success, (False, reason) on failure.
    Returns (False, 'SMTP_NOT_CONFIGURED') when credentials are missing.
    """
    sender_email, sender_password = _get_credentials()

    # Always log for debugging / dev testing
    print(f"\n{'='*44}\n[OTP] {receiver_email}: {otp}\n{'='*44}\n")

    if not sender_email or not sender_password:
        return False, "SMTP_NOT_CONFIGURED"

    try:
        msg = MIMEMultipart()
        msg['From']    = sender_email
        msg['To']      = receiver_email
        msg['Subject'] = "NovaFlix — Your Verification Code"

        body = f"""Hello,

Your NovaFlix verification / reset code is:

    {otp}

This code expires in 5 minutes.
If you did not request this, please ignore this email.

— NovaFlix Team
"""
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True, "OTP sent successfully."
    except Exception as e:
        return False, str(e)
