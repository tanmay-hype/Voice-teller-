import random
import string
from datetime import datetime, timedelta
from core.config import settings
import redis
import json
import logging

logger = logging.getLogger(__name__)

# Initialize Redis connection for OTP storage
redis_client = redis.from_url(settings.REDIS_URL)


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


async def store_otp(email: str, otp: str) -> bool:
    """Store OTP in Redis with expiry"""
    try:
        expiry_seconds = settings.OTP_EXPIRY_MINUTES * 60
        redis_client.setex(
            f"otp:{email}",
            expiry_seconds,
            otp
        )
        logger.info(f"OTP stored for {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to store OTP for {email}: {str(e)}")
        return False


async def verify_otp(email: str, otp: str) -> bool:
    """Verify if the provided OTP matches the stored one"""
    try:
        stored_otp = redis_client.get(f"otp:{email}")
        if not stored_otp:
            logger.warning(f"OTP not found or expired for {email}")
            return False
        
        if stored_otp.decode() == otp:
            # Delete OTP after successful verification
            redis_client.delete(f"otp:{email}")
            logger.info(f"OTP verified successfully for {email}")
            return True
        
        logger.warning(f"Invalid OTP provided for {email}")
        return False
    except Exception as e:
        logger.error(f"Error verifying OTP for {email}: {str(e)}")
        return False


async def get_otp_remaining_time(email: str) -> int:
    """Get remaining time in seconds for OTP expiry"""
    try:
        ttl = redis_client.ttl(f"otp:{email}")
        return max(0, ttl)
    except Exception as e:
        logger.error(f"Error getting OTP TTL for {email}: {str(e)}")
        return 0
