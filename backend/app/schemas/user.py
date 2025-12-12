from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    TUTOR = "tutor"
    ADMIN = "admin"


class Language(str, Enum):
    ENGLISH = "en"
    YORUBA = "yo"
    HAUSA = "ha"
    IGBO = "ig"


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str | None = None
    preferred_language: Language = Language.ENGLISH
    phone_number: str | None = None
    school_name: str | None = None
    grade_level: str | None = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: str | None = None
    preferred_language: Language | None = None
    phone_number: str | None = None
    school_name: str | None = None
    grade_level: str | None = None


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    pass


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"