from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import settings
from core.database import get_db
from core.security import verify_password, create_access_token, get_password_hash
from models.user import User
from schemas.user import UserCreate, User as UserSchema, UserVerifyOTPRequest
from services.otp_svc import generate_otp, store_otp, verify_otp
from services.email_svc import send_welcome_email

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/request-otp", response_model=dict)
async def register_request_otp(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Step 1: Request OTP for registration
    User provides email, password, and location
    """
    print("\n========== REGISTER REQUEST OTP ==========")
    print("Incoming Email:", user_in.email)

    try:
        print("➡️ Checking if user already exists...")
        result = await db.execute(select(User).where(User.email == user_in.email))
        existing_user = result.scalars().first()

        if existing_user and getattr(existing_user, "status", "active") != "deleted":
            print("❌ User already exists and is active")
            raise HTTPException(
                status_code=400,
                detail="Email already registered. Please login or use a different email.",
            )
        elif existing_user and getattr(existing_user, "status", "active") == "deleted":
            # Allow OTP to be requested for a previously deleted account to enable reactivation
            print("ℹ️ Found previously deleted account — proceeding with OTP to allow reactivation")

        print("➡️ Generating OTP...")
        otp = generate_otp()
        
        print("➡️ Storing OTP in Redis...")
        await store_otp(user_in.email, otp)
        
        print("➡️ Sending welcome email with OTP...")
        email_sent = await send_welcome_email(user_in.email, otp)
        
        if not email_sent:
            print("⚠️ Email sending failed, but OTP was stored")
            raise HTTPException(
                status_code=500,
                detail="Failed to send verification email. Please try again later.",
            )

        print("✅ OTP SENT SUCCESSFULLY")
        print("=====================================\n")

        return {
            "message": "OTP sent to your email. Please verify within 15 minutes.",
            "email": user_in.email,
            "otp_expires_in_minutes": settings.OTP_EXPIRY_MINUTES
        }

    except HTTPException:
        raise
    except Exception as e:
        print("🔥 ERROR DURING OTP REQUEST:", str(e))
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.")


@router.post("/register/verify-otp", response_model=UserSchema)
async def register_verify_otp(verify_data: UserVerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Step 2: Verify OTP and create user account
    """
    print("\n========== REGISTER VERIFY OTP ==========")
    print("Verifying Email:", verify_data.email)

    try:
        print("➡️ Verifying OTP...")
        otp_valid = await verify_otp(verify_data.email, verify_data.otp)
        
        if not otp_valid:
            print("❌ Invalid or expired OTP")
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired OTP. Please request a new one.",
            )

        print("✅ OTP verified successfully")

        # Check if user already exists
        result = await db.execute(select(User).where(User.email == verify_data.email))
        existing_user = result.scalars().first()
        
        if existing_user and getattr(existing_user, "status", "active") != "deleted":
            raise HTTPException(
                status_code=400,
                detail="User already exists. Please login.",
            )

        print("➡️ Hashing password...")
        hashed_password = get_password_hash(verify_data.password)

        print("➡️ Creating or reactivating user account...")
        if existing_user and getattr(existing_user, "status", "active") == "deleted":
            # Reactivate the soft-deleted user
            existing_user.hashed_password = hashed_password
            existing_user.is_verified = True
            existing_user.is_active = True
            existing_user.status = "active"
            existing_user.latitude = verify_data.latitude
            existing_user.longitude = verify_data.longitude
            db.add(existing_user)
            await db.commit()
            await db.refresh(existing_user)
            user = existing_user
            print("✅ Reactivated existing user:", user.id)
        else:
            user = User(
                email=verify_data.email,
                hashed_password=hashed_password,
                is_verified=True,
                latitude=verify_data.latitude,
                longitude=verify_data.longitude,
            )
            print("➡️ Adding user to DB session...")
            db.add(user)
            print("➡️ Committing to database...")
            await db.commit()
            print("➡️ Refreshing user...")
            await db.refresh(user)

        print("✅ USER CREATED SUCCESSFULLY:", user.id)
        print("=====================================\n")

        return user

    except HTTPException:
        raise
    except Exception as e:
        print("🔥 ERROR DURING OTP VERIFICATION:", str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred during registration.")


@router.post("/register", response_model=UserSchema)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Legacy endpoint: Direct registration (can be deprecated after OTP flow is fully adopted)
    """
    print("\n========== REGISTER API HIT ==========")
    print("Incoming Email:", user_in.email)

    try:
        print("➡️ Checking if user already exists...")
        result = await db.execute(select(User).where(User.email == user_in.email))
        existing_user = result.scalars().first()
        print("➡️ Existing user:", existing_user)

        if existing_user and getattr(existing_user, "status", "active") != "deleted":
            print("❌ User already exists")
            raise HTTPException(
                status_code=400,
                detail="The user already exists.",
            )

        print("➡️ Hashing password...")
        hashed_password = get_password_hash(user_in.password)
        print("➡️ Password hashed successfully")

        if existing_user and getattr(existing_user, "status", "active") == "deleted":
            # Reactivate soft-deleted account
            print("➡️ Reactivating previously deleted account...")
            existing_user.hashed_password = hashed_password
            existing_user.is_active = True
            existing_user.is_verified = False
            existing_user.status = "active"
            existing_user.latitude = user_in.latitude
            existing_user.longitude = user_in.longitude
            db.add(existing_user)
            await db.commit()
            await db.refresh(existing_user)
            user = existing_user
            print("✅ REACTIVATED USER:", user.id)
        else:
            print("➡️ Creating user object...")
            user = User(
                email=user_in.email,
                hashed_password=hashed_password,
                latitude=user_in.latitude,
                longitude=user_in.longitude,
            )

            print("➡️ Adding user to DB session...")
            db.add(user)

            print("➡️ Committing to database...")
            await db.commit()

            print("➡️ Refreshing user...")
            await db.refresh(user)

        print("✅ USER CREATED SUCCESSFULLY:", user.id)
        print("=====================================\n")

        return user

    except Exception as e:
        print("🔥 ERROR DURING REGISTRATION:", str(e))
        raise

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

        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        elif not user.is_active or getattr(user, "status", "active") == "deleted":
            raise HTTPException(status_code=400, detail="Inactive user")
        
        # Update user location if provided
        if latitude and longitude:
            try:
                user.latitude = float(latitude)
                user.longitude = float(longitude)
                db.add(user)
                await db.commit()
                print(f"✅ Location updated for user {user.email}: ({user.latitude}, {user.longitude})")
            except (ValueError, TypeError) as e:
                print(f"⚠️ Invalid latitude/longitude values: {latitude}, {longitude} - {str(e)}")
        
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
        print(f"🔥 Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during login")
