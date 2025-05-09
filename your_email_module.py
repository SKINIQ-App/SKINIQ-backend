import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_verification_email(email: str, otp: str, username: str):
    sender_email = os.getenv("EMAIL_HOST_USER")
    password = os.getenv("EMAIL_HOST_PASSWORD")
    receiver_email = email

    subject = "🌿 Your SKINIQ Verification Code is Here!"

    body = f"""
    <html>
      <body style="font-family: 'Segoe UI', sans-serif; background-color: #f2fdf9; color: #2f4f4f;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border-radius: 12px; border: 1px solid #b2dfdb; background: #ffffff;">
          
          <div style="text-align: center;">
            <img src="https://res.cloudinary.com/dieykiet2/image/upload/v1746696612/skincare_logo.png" alt="SKINIQ Logo" width="90" style="margin-bottom: 10px;" />
            <h1 style="color: #27ae60; margin: 0;">SKINIQ</h1>
            <p style="color: #219150; font-size: 14px; margin-top: 5px;"><em>Your Skin Our Care</em></p>
          </div>

          <h2 style="color: #27ae60;">Hi {username}! 🌿</h2>

          <p>We're absolutely thrilled to have you on board with <strong>SKINIQ</strong> – your new skincare BFF! 🍃</p>

          <p style="font-size: 18px; color: #333;">
            Your One-Time Password (OTP) is:  
            <span style="display: inline-block; background: #d4eee7; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 22px; color: #2c7a67;">
              {otp}
            </span>
          </p>

          <p>Enter this in the app to verify your email and start your glow journey today. ✨</p>

          <hr style="margin: 30px 0;" />

          <h4 style="color: #2c7a67;">Why verify your email?</h4>
          <ul>
            <li>Unlock your personalized skincare insights 🧴</li>
            <li>Store and compare your selfie analyses 📸</li>
            <li>Track progress across all your devices 📈</li>
            <li>Get exclusive SKINIQ glow tips 💡</li>
          </ul>

          <div style="text-align: center; margin: 30px 0;">
            <img src="https://res.cloudinary.com/dieykiet2/image/upload/v1746696668/email_gif.gif" alt="Cute skincare gif" width="250" style="border-radius: 12px;" />
          </div>

          <p>If you didn’t request this, no worries – simply ignore this email 💌</p>

          <p>With 💕 and SPF,<br/><strong>The SKINIQ Team</strong></p>

          <p style="font-size: 12px; color: #888; margin-top: 20px;">P.S. Remember to stay hydrated and reapply sunscreen! 💧🧴</p>
        </div>
      </body>
    </html>
    """

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Reply-To"] = sender_email
    message.attach(MIMEText(body, "html", "utf-8"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.set_debuglevel(1)  # For logs
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print(f"✅ Verification email sent to {receiver_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")


def send_password_reset_email(email: str, username: str, reset_link: str):
    sender_email = os.getenv("EMAIL_HOST_USER")
    password = os.getenv("EMAIL_HOST_PASSWORD")
    receiver_email = email

    subject = "🔐 Reset Your SKINIQ Password Securely"

    body = f"""
    <html>
      <body style="font-family: 'Segoe UI', sans-serif; background-color: #f2fdf9; color: #2f4f4f;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border-radius: 12px; border: 1px solid #b2dfdb; background: #ffffff;">
          
          <div style="text-align: center;">
            <img src="https://res.cloudinary.com/dieykiet2/image/upload/v1746696612/skincare_logo.png" alt="SKINIQ Logo" width="90" style="margin-bottom: 10px;" />
            <h1 style="color: #27ae60; margin: 0;">SKINIQ</h1>
            <p style="color: #219150; font-size: 14px; margin-top: 5px;"><em>Your Skin Our Care</em></p>
          </div>

          <h2 style="color: #27ae60;">Hi {username}! 🔐</h2>

          <p>Looks like you requested a password reset for your SKINIQ account.</p>

          <p>Click the button below to reset your password:</p>

          <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: #27ae60; color: #ffffff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
              Reset My Password
            </a>
          </div>

          <p>If the button doesn't work, you can also use this link:</p>
          <p style="word-break: break-all;"><a href="{reset_link}">{reset_link}</a></p>

          <p style="color: #888;">This link will expire in 30 minutes for your security.</p>

          <hr style="margin: 30px 0;" />

          <p>If you didn't request this, please ignore this email. Your password will remain unchanged.</p>

          <p>With 💕 and SPF,<br/><strong>The SKINIQ Team</strong></p>

          <p style="font-size: 12px; color: #888; margin-top: 20px;">P.S. Remember to stay hydrated and reapply sunscreen! 💧🧴</p>
        </div>
      </body>
    </html>
    """

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Reply-To"] = sender_email
    message.attach(MIMEText(body, "html", "utf-8"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.set_debuglevel(1)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print(f"✅ Password reset email sent to {receiver_email}")
    except Exception as e:
        print(f"❌ Error sending password reset email: {e}")
