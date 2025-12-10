from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid
import enum


class Difficulty(str, enum.Enum):
    """Question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MCQ(Base):
    __tablename__ = "mcq"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text, nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(100), nullable=False)
    difficulty = Column(SQLEnum(Difficulty), default=Difficulty.MEDIUM, nullable=False)
    explanation = Column(Text, nullable=True)
    language = Column(String(10), default="en", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MCQ(id={self.id}, subject={self.subject}, topic={self.topic})>"


class MCQOption(Base):
    __tablename__ = "mcq_options"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mcq_id = Column(UUID(as_uuid=True), ForeignKey("mcq.id"), nullable=False, index=True)
    option_text = Column(Text, nullable=False)
    option_letter = Column(String(5), nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MCQOption(mcq_id={self.mcq_id}, option_letter={self.option_letter})>"


class MCQAttempt(Base):
    __tablename__ = "mcq_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    mcq_id = Column(UUID(as_uuid=True), ForeignKey("mcq.id"), nullable=False, index=True)
    selected_option_id = Column(UUID(as_uuid=True), ForeignKey("mcq_options.id"), nullable=True)
    is_correct = Column(Boolean, default=False, nullable=False)
    time_spent_seconds = Column(Integer, default=0, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MCQAttempt(user_id={self.user_id}, mcq_id={self.mcq_id})>"