import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import settings
from core.database import get_db
from core.security import verify_password, create_access_token, get_password_hash
from models.user import User
from schemas.user import UserRegisterRequest, UserVerifyOTPRequest
from services.email_svc import send_otp_email
from services.otp_svc import (
    clear_registration_state,
    clear_login_failures,
    login_attempt_state,
    generate_otp,
    get_pending_registration,
    mark_otp_send_cooldown,
    otp_send_cooldown_remaining,
    record_login_failure,
    store_otp,
    store_pending_registration,
    verify_otp as verify_stored_otp,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


async def _start_otp_registration(user_in: UserRegisterRequest, db: AsyncSession):
    email = user_in.email.strip().lower()
    logger.info("Register request received for %s", email)

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalars().first()

    if existing_user and existing_user.is_verified and getattr(existing_user, "status", "active") != "deleted":
        raise HTTPException(status_code=400, detail="The email is already registered and verified.")

    cooldown_remaining = await otp_send_cooldown_remaining(email)
    if cooldown_remaining > 0:
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {cooldown_remaining} seconds before requesting another OTP.",
        )

    otp = generate_otp()
    hashed_password = get_password_hash(user_in.password)

    registration_payload = {
        "hashed_password": hashed_password,
        "latitude": user_in.latitude,
        "longitude": user_in.longitude,
    }

    otp_stored = await store_otp(email, otp)
    registration_stored = await store_pending_registration(email, registration_payload)
    cooldown_stored = await mark_otp_send_cooldown(email)

    if not otp_stored or not registration_stored or not cooldown_stored:
        await clear_registration_state(email)
        raise HTTPException(status_code=500, detail="Failed to prepare OTP registration. Please try again.")

    email_sent = await send_otp_email(email, otp)
    if not email_sent:
        await clear_registration_state(email)
        raise HTTPException(status_code=500, detail="Unable to send verification email. Please try again.")

    return {"message": "OTP sent to your email. Verify it to complete registration."}


@router.post("/register")
async def register(user_in: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Start OTP registration by sending a verification code to the user."""
    return await _start_otp_registration(user_in, db)


@router.post("/send-otp")
async def send_otp(user_in: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Explicit OTP send endpoint with resend cooldown protection."""
    return await _start_otp_registration(user_in, db)


@router.post("/verify-otp")
async def verify_otp(payload: UserVerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """Verify the OTP and create or reactivate the user account."""
    email = payload.email.strip().lower()
    logger.info("OTP verification request received for %s", email)

    if not await verify_stored_otp(email, payload.otp.strip()):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    pending_registration = await get_pending_registration(email)
    if not pending_registration:
        raise HTTPException(status_code=400, detail="Registration request expired. Please register again.")

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalars().first()

    if existing_user:
        if existing_user.is_verified and getattr(existing_user, "status", "active") != "deleted":
            await clear_registration_state(email)
            raise HTTPException(status_code=400, detail="This email is already verified. Please log in.")

        existing_user.hashed_password = pending_registration["hashed_password"]
        existing_user.is_active = True
        existing_user.is_verified = True
        existing_user.status = "active"
        existing_user.latitude = pending_registration.get("latitude")
        existing_user.longitude = pending_registration.get("longitude")
        user = existing_user
    else:
        user = User(
            email=email,
            hashed_password=pending_registration["hashed_password"],
            is_active=True,
            is_verified=True,
            status="active",
            latitude=pending_registration.get("latitude"),
            longitude=pending_registration.get("longitude"),
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)
    await clear_registration_state(email)

    return {"message": "Email verified successfully. You can now log in."}

@router.post("/login")
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Request
):
    """
    Login endpoint that accepts username, password, and optional location (latitude/longitude)
    """
    try:
        form_data = await request.form()
        email = form_data.get('username')
        password = form_data.get('password')
        latitude = form_data.get('latitude')
        longitude = form_data.get('longitude')
        client_id = request.client.host if request.client else "unknown"

        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")

        login_state = await login_attempt_state(email, client_id)
        if login_state["locked"]:
            raise HTTPException(
                status_code=429,
                detail=f"Too many login attempts. Try again in {login_state['lock_remaining']} seconds.",
            )

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user or not verify_password(password, user.hashed_password):
            lock_state = await record_login_failure(email, client_id)
            if lock_state["locked"]:
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many login attempts. Try again in {lock_state['lock_remaining']} seconds.",
                )
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        elif not user.is_active or getattr(user, "status", "active") == "deleted":
            raise HTTPException(status_code=400, detail="Inactive user")
        elif not user.is_verified:
            raise HTTPException(status_code=403, detail="Please verify your email before logging in")

        await clear_login_failures(email, client_id)
        
        # Update user location if provided
        if latitude and longitude:
            try:
                user.latitude = float(latitude)
                user.longitude = float(longitude)
                db.add(user)
                await db.commit()
                logger.info("Location updated for user %s: (%s, %s)", user.email, user.latitude, user.longitude)
            except (ValueError, TypeError):
                logger.warning("Invalid latitude/longitude values for %s", user.email)
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Login error")
        raise HTTPException(status_code=500, detail="An error occurred during login")
