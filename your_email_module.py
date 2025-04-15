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

    subject = "Your SKINIQ Verification OTP"
    body = f"""
    Hi there 👋,

    Your OTP for email verification is: **{otp}**

    Please enter this in the app to verify your email.

    Cheers,
    SKINIQ Team
    """

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Reply-To"] = sender_email
    message.attach(MIMEText(body, "plain", "utf-8"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.set_debuglevel(1)  # 🔍 See email debug in Render logs
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print(f"✅ Verification email sent to {receiver_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# ✅ Wrapper function for use in FastAPI
def send_email_otp(email: str):
    print(f"📩 Sending OTP to: {email}")
    otp = random.randint(100000, 999999)
    send_verification_email(email, str(otp))
    # You can store OTP in DB here if needed
