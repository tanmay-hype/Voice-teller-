import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.deps import get_current_active_user
from core.database import get_db
from core.security import verify_password
from models.user import User
from schemas.user import User as UserSchema, UserDeleteRequest

router = APIRouter(prefix="/users", tags=["users"])

PROFILE_UPLOAD_DIR = Path("media/profile_pictures")
PROFILE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _user_to_schema(user: User) -> UserSchema:
    return UserSchema.model_validate(user)


@router.get("/me", response_model=UserSchema)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    contact_no: str = Form(...),
    email: str = Form(...),
    profile_picture: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(User).where(User.email == email, User.id != current_user.id))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists.")

    current_user.first_name = first_name.strip()
    current_user.last_name = last_name.strip()
    current_user.contact_no = contact_no.strip()
    current_user.email = email.strip()

    if profile_picture and profile_picture.filename:
        file_ext = os.path.splitext(profile_picture.filename)[1] or ".png"
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = PROFILE_UPLOAD_DIR / unique_filename
        file_bytes = await profile_picture.read()

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty profile picture uploaded")

        with open(file_path, "wb") as file_handle:
            file_handle.write(file_bytes)

        current_user.profile_picture_url = f"/media/profile_pictures/{unique_filename}"

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me")
async def delete_current_user(
    payload: UserDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    current_user.status = "deleted"
    current_user.is_active = False
    db.add(current_user)
    await db.commit()

    return {"message": "Account deleted successfully"}
