import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_verification_email(email: str, otp: str):
    sender_email = os.getenv("EMAIL_HOST_USER")
    password = os.getenv("EMAIL_HOST_PASSWORD")
    receiver_email = email

    subject = "Email Verification"
    body = f"Your OTP for email verification is: {otp}"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"📨 Verification email sent to {receiver_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# ✅ Wrapper function for use in FastAPI route
def send_email_otp(email: str):
    print(f"📩 Sending OTP to: {email}")  # Debug log
    otp = random.randint(100000, 999999)
    send_verification_email(email, str(otp))
    # Optionally store the OTP in DB if you're verifying later
