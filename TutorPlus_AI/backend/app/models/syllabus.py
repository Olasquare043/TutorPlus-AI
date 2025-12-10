from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from datetime import datetime
import uuid


class Syllabus(Base):
    __tablename__ = "syllabus"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(255), nullable=False, index=True)
    subtopic = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    keywords = Column(String(500), nullable=True)
    difficulty_level = Column(String(20), nullable=False)
    exam_board = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    embedding_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Syllabus(id={self.id}, subject={self.subject}, topic={self.topic})>"