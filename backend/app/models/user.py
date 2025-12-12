from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from datetime import datetime
import uuid
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    TUTOR = "tutor"
    ADMIN = "admin"


class Language(str, enum.Enum):
    """Supported languages"""
    ENGLISH = "en"
    YORUBA = "yo"
    HAUSA = "ha"
    IGBO = "ig"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    preferred_language = Column(SQLEnum(Language), default=Language.ENGLISH, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    phone_number = Column(String(20), nullable=True)
    school_name = Column(String(255), nullable=True)
    grade_level = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"