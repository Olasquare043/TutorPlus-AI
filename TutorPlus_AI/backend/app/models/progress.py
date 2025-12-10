from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, Boolean, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid
import enum


class SubjectArea(str, enum.Enum):
    """Academic subject areas"""
    MATHEMATICS = "mathematics"
    ENGLISH = "english"
    BIOLOGY = "biology"
    CHEMISTRY = "chemistry"
    PHYSICS = "physics"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    LITERATURE = "literature"
    GOVERNMENT = "government"
    ECONOMICS = "economics"


class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(SQLEnum(SubjectArea), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    lessons_completed = Column(Integer, default=0, nullable=False)
    total_lessons = Column(Integer, default=0, nullable=False)
    quiz_score = Column(Float, default=0.0, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Progress(user_id={self.user_id}, subject={self.subject}, topic={self.topic})>"


class StudentProgress(Base):
    __tablename__ = "student_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(SQLEnum(SubjectArea), nullable=False, index=True)
    overall_score = Column(Float, default=0.0, nullable=False)
    total_questions_answered = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    learning_streak = Column(Integer, default=0, nullable=False)
    last_learning_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<StudentProgress(user_id={self.user_id}, subject={self.subject})>"