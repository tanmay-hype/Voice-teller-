import random
import string
import json
import logging
from typing import Any

from core.config import settings
import redis

logger = logging.getLogger(__name__)

# Initialize Redis connection for OTP storage
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

OTP_KEY_PREFIX = "otp:"
PENDING_REGISTRATION_KEY_PREFIX = "pending_registration:"
OTP_COOLDOWN_KEY_PREFIX = "otp_cooldown:"
LOGIN_FAIL_KEY_PREFIX = "login_fail:"
LOGIN_LOCK_KEY_PREFIX = "login_lock:"


def _email_key(prefix: str, email: str) -> str:
    return f"{prefix}{email.strip().lower()}"


def _login_key(prefix: str, email: str, client_id: str | None = None) -> str:
    normalized_email = email.strip().lower()
    if client_id:
        return f"{prefix}{normalized_email}:{client_id.strip().lower()}"
    return f"{prefix}{normalized_email}"


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


async def store_otp(email: str, otp: str) -> bool:
    """Store OTP in Redis with expiry"""
    try:
        expiry_seconds = settings.OTP_EXPIRY_MINUTES * 60
        redis_client.setex(
            _email_key(OTP_KEY_PREFIX, email),
            expiry_seconds,
            otp
        )
        logger.info("OTP stored for %s", email)
        return True
    except Exception as e:
        logger.exception("Failed to store OTP for %s", email)
        return False


async def otp_send_cooldown_remaining(email: str) -> int:
    try:
        ttl = redis_client.ttl(_email_key(OTP_COOLDOWN_KEY_PREFIX, email))
        return max(0, ttl)
    except Exception:
        logger.exception("Error getting OTP cooldown for %s", email)
        return 0


async def mark_otp_send_cooldown(email: str) -> bool:
    try:
        redis_client.setex(
            _email_key(OTP_COOLDOWN_KEY_PREFIX, email),
            settings.OTP_RESEND_COOLDOWN_SECONDS,
            "1",
        )
        return True
    except Exception:
        logger.exception("Failed to store OTP cooldown for %s", email)
        return False


async def clear_otp_send_cooldown(email: str) -> None:
    try:
        redis_client.delete(_email_key(OTP_COOLDOWN_KEY_PREFIX, email))
    except Exception:
        logger.exception("Failed to clear OTP cooldown for %s", email)


async def verify_otp(email: str, otp: str) -> bool:
    """Verify if the provided OTP matches the stored one"""
    try:
        otp_key = _email_key(OTP_KEY_PREFIX, email)
        ttl = redis_client.ttl(otp_key)
        if ttl <= 0:
            redis_client.delete(otp_key)
            logger.warning("OTP not found or expired for %s", email)
            return False

        stored_otp = redis_client.get(otp_key)
        if not stored_otp:
            logger.warning("OTP not found or expired for %s", email)
            return False
        
        if stored_otp == otp:
            # Delete OTP after successful verification
            redis_client.delete(otp_key)
            logger.info("OTP verified successfully for %s", email)
            return True
        
        logger.warning("Invalid OTP provided for %s", email)
        return False
    except Exception as e:
        logger.exception("Error verifying OTP for %s", email)
        return False


async def get_otp_remaining_time(email: str) -> int:
    """Get remaining time in seconds for OTP expiry"""
    try:
        ttl = redis_client.ttl(_email_key(OTP_KEY_PREFIX, email))
        return max(0, ttl)
    except Exception as e:
        logger.exception("Error getting OTP TTL for %s", email)
        return 0


async def store_pending_registration(email: str, payload: dict) -> bool:
    try:
        expiry_seconds = settings.OTP_EXPIRY_MINUTES * 60
        redis_client.setex(
            _email_key(PENDING_REGISTRATION_KEY_PREFIX, email),
            expiry_seconds,
            json.dumps(payload),
        )
        logger.info("Pending registration stored for %s", email)
        return True
    except Exception:
        logger.exception("Failed to store pending registration for %s", email)
        return False


async def get_pending_registration(email: str) -> dict | None:
    try:
        raw_value = redis_client.get(_email_key(PENDING_REGISTRATION_KEY_PREFIX, email))
        if not raw_value:
            return None
        return json.loads(raw_value)
    except Exception:
        logger.exception("Failed to load pending registration for %s", email)
        return None


async def clear_registration_state(email: str) -> None:
    try:
        redis_client.delete(_email_key(OTP_KEY_PREFIX, email))
        redis_client.delete(_email_key(PENDING_REGISTRATION_KEY_PREFIX, email))
        redis_client.delete(_email_key(OTP_COOLDOWN_KEY_PREFIX, email))
    except Exception:
        logger.exception("Failed to clear registration state for %s", email)


async def login_attempt_state(email: str, client_id: str | None = None) -> dict[str, Any]:
    try:
        lock_key = _login_key(LOGIN_LOCK_KEY_PREFIX, email, client_id)
        fail_key = _login_key(LOGIN_FAIL_KEY_PREFIX, email, client_id)
        lock_ttl = redis_client.ttl(lock_key)
        fail_count = redis_client.get(fail_key)
        return {
            "locked": lock_ttl > 0,
            "lock_remaining": max(0, lock_ttl),
            "fail_count": int(fail_count or 0),
        }
    except Exception:
        logger.exception("Failed to read login attempt state for %s", email)
        return {"locked": False, "lock_remaining": 0, "fail_count": 0}


async def record_login_failure(email: str, client_id: str | None = None) -> dict[str, Any]:
    try:
        fail_key = _login_key(LOGIN_FAIL_KEY_PREFIX, email, client_id)
        lock_key = _login_key(LOGIN_LOCK_KEY_PREFIX, email, client_id)
        current_failures = redis_client.incr(fail_key)
        redis_client.expire(fail_key, settings.LOGIN_LOCKOUT_SECONDS)

        if current_failures >= settings.LOGIN_MAX_ATTEMPTS:
            redis_client.setex(lock_key, settings.LOGIN_LOCKOUT_SECONDS, "1")
            redis_client.delete(fail_key)
            return {"locked": True, "lock_remaining": settings.LOGIN_LOCKOUT_SECONDS, "fail_count": current_failures}

        return {"locked": False, "lock_remaining": 0, "fail_count": current_failures}
    except Exception:
        logger.exception("Failed to record login failure for %s", email)
        return {"locked": False, "lock_remaining": 0, "fail_count": 0}


async def clear_login_failures(email: str, client_id: str | None = None) -> None:
    try:
        redis_client.delete(_login_key(LOGIN_FAIL_KEY_PREFIX, email, client_id))
        redis_client.delete(_login_key(LOGIN_LOCK_KEY_PREFIX, email, client_id))
    except Exception:
        logger.exception("Failed to clear login failures for %s", email)
