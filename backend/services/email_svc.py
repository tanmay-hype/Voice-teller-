import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import settings
import logging

logger = logging.getLogger(__name__)


async def send_welcome_email(email: str, otp: str, website_name: str = "Voice Teller") -> bool:
    """
    Send welcome email with OTP to new user
    """
    try:
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Welcome to {website_name}! Verify Your Email"
        msg["From"] = settings.EMAIL_SENDER
        msg["To"] = email

        # HTML content
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
                        <h1 style="margin: 0; font-size: 28px;">Welcome to {website_name}! 🎉</h1>
                    </div>

                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                        <h2 style="color: #667eea;">Hello {email.split("@")[0]},</h2>
                        <p>Thank you for joining {website_name}! We're thrilled to have you on board.</p>
                        
                        <h3 style="color: #667eea; margin-top: 20px;">About {website_name}</h3>
                        <p>
                            {website_name} is an innovative platform that uses AI to transform your stories into 
                            engaging audio narratives. Whether you're a storyteller, content creator, or simply love 
                            stories, our platform empowers you to:
                        </p>
                        <ul style="line-height: 1.8;">
                            <li><strong>Generate Stories:</strong> Create unique stories using advanced AI</li>
                            <li><strong>Voice Narration:</strong> Convert stories to audio with natural-sounding voices</li>
                            <li><strong>Voice Cloning:</strong> Use your own voice or choose from multiple voices</li>
                            <li><strong>Share & Enjoy:</strong> Share your creations with the world</li>
                        </ul>
                    </div>

                    <div style="background: #fff3cd; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107; margin-bottom: 20px;">
                        <h3 style="color: #856404; margin-top: 0;">Your Email Verification Code</h3>
                        <p style="color: #856404; margin-bottom: 10px;">To complete your registration, please enter the following OTP on the registration page:</p>
                        <div style="background: #fff; padding: 15px; border-radius: 5px; text-align: center; margin: 15px 0;">
                            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #667eea;">{otp}</span>
                        </div>
                        <p style="color: #856404; font-size: 12px; margin: 10px 0;">⏱️ This code expires in 15 minutes</p>
                    </div>

                    <div style="background: #e7f3ff; padding: 15px; border-radius: 10px; border-left: 5px solid #0066cc; margin-bottom: 20px;">
                        <p style="margin: 0; color: #004499; font-size: 14px;">
                            <strong>Security Note:</strong> Never share this OTP with anyone. Our team will never ask for your OTP via email.
                        </p>
                    </div>

                    <div style="text-align: center; color: #666; font-size: 12px; padding-top: 20px; border-top: 1px solid #ddd;">
                        <p>If you didn't create this account, please ignore this email.</p>
                        <p>© 2024 {website_name}. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """

        # Attach HTML content
        msg.attach(MIMEText(html_content, "html"))

        # Send email
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
            server.send_message(msg)

        logger.info(f"Welcome email sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        return False
