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
from schemas.user import UserCreate, User as UserSchema

router = APIRouter(prefix="/auth", tags=["auth"])


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
