import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage

from core.config import settings

logger = logging.getLogger(__name__)


def _build_otp_message(email: str, otp: str, website_name: str) -> EmailMessage:
    sender_email = settings.EMAIL_SENDER.strip()
    message = EmailMessage()
    message["Subject"] = f"Verify your email for {website_name}"
    message["From"] = sender_email
    message["To"] = email

    plain_text = (
        f"Hello,\n\n"
        f"Your verification code for {website_name} is: {otp}\n\n"
        f"This code expires in {settings.OTP_EXPIRY_MINUTES} minutes.\n"
        "If you did not request this, you can ignore this email.\n"
    )

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #1f2937; background: #f8fafc; padding: 24px;">
        <div style="max-width: 640px; margin: 0 auto; background: #ffffff; border-radius: 18px; padding: 32px; border: 1px solid #e5e7eb;">
          <h1 style="margin: 0 0 16px; font-size: 28px; color: #111827;">Verify your email</h1>
          <p style="margin: 0 0 20px;">Thanks for registering with {website_name}. Use the one-time code below to complete your sign-up.</p>
          <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 16px; padding: 20px; text-align: center; margin: 24px 0;">
            <div style="font-size: 14px; color: #1d4ed8; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.12em;">One-time password</div>
            <div style="font-size: 36px; font-weight: 700; letter-spacing: 0.35em; color: #0f172a;">{otp}</div>
          </div>
          <p style="margin: 0; color: #4b5563;">This code expires in {settings.OTP_EXPIRY_MINUTES} minutes.</p>
          <p style="margin: 12px 0 0; color: #4b5563;">If you did not request this, you can ignore this email.</p>
        </div>
      </body>
    </html>
    """

    message.set_content(plain_text)
    message.add_alternative(html_content, subtype="html")
    return message


def _send_otp_email_sync(email: str, otp: str, website_name: str) -> None:
    smtp_server = settings.SMTP_SERVER.strip()
    smtp_port = int(settings.SMTP_PORT)
    sender_email = settings.EMAIL_SENDER.strip()
    sender_password = settings.EMAIL_PASSWORD.strip()

    if not smtp_server or not sender_email:
        raise RuntimeError("SMTP server and sender email are required")

    message = _build_otp_message(email, otp, website_name)
    is_local_smtp = smtp_server in {"localhost", "127.0.0.1"}
    use_starttls = smtp_port in {587, 25} and not is_local_smtp

    if not is_local_smtp and not sender_password:
      raise RuntimeError("SMTP password is required for non-local delivery")

    with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as server:
        server.ehlo()
        if use_starttls:
            server.starttls(context=ssl.create_default_context())
            server.ehlo()

        if sender_password and not is_local_smtp:
            server.login(sender_email, sender_password)

        server.send_message(message)


async def send_otp_email(email: str, otp: str, website_name: str = "Voice Teller") -> bool:
    """Send a verification OTP email using SMTP."""
    try:
        logger.info("Sending OTP email to %s via %s:%s", email, settings.SMTP_SERVER, settings.SMTP_PORT)
        await asyncio.to_thread(_send_otp_email_sync, email, otp, website_name)
        logger.info("OTP email sent successfully to %s", email)
        return True
    except Exception:
        logger.exception("Failed to send OTP email to %s", email)
        return False


# Backward-compatible alias for any legacy imports.
send_welcome_email = send_otp_email
