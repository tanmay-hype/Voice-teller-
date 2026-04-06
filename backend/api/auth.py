from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
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
    print("\n========== REGISTER API HIT ==========")
    print("Incoming Email:", user_in.email)

    try:
        print("➡️ Checking if user already exists...")
        result = await db.execute(select(User).where(User.email == user_in.email))
        existing_user = result.scalars().first()
        print("➡️ Existing user:", existing_user)

        if existing_user:
            print("❌ User already exists")
            raise HTTPException(
                status_code=400,
                detail="The user already exists.",
            )

        print("➡️ Hashing password...")
        hashed_password = get_password_hash(user_in.password)
        print("➡️ Password hashed successfully")

        print("➡️ Creating user object...")
        user = User(
            email=user_in.email,
            hashed_password=hashed_password,
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
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
