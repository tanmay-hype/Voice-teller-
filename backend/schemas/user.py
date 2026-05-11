from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserRegisterRequest(UserBase):
    password: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserVerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    password: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserUpdate(BaseModel):
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserDeleteRequest(BaseModel):
    password: str

class UserProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_no: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture_url: Optional[str] = None

class UserProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    contact_no: str
    email: EmailStr

class UserInDBBase(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_no: Optional[str] = None
    profile_picture_url: Optional[str] = None
    status: str = "active"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str
