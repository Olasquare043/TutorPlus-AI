from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional


class SubjectArea(str, Enum):
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


class ProgressBase(BaseModel):
    subject: SubjectArea
    topic: str
    lessons_completed: int = 0
    total_lessons: int = 0
    quiz_score: float = 0.0


class ProgressCreate(ProgressBase):
    pass


class ProgressUpdate(BaseModel):
    lessons_completed: Optional[int] = None
    total_lessons: Optional[int] = None
    quiz_score: Optional[float] = None


class ProgressResponse(ProgressBase):
    id: UUID
    user_id: UUID
    last_accessed: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StudentProgressBase(BaseModel):
    subject: SubjectArea
    overall_score: float = 0.0
    total_questions_answered: int = 0
    correct_answers: int = 0
    learning_streak: int = 0


class StudentProgressUpdate(BaseModel):
    overall_score: Optional[float] = None
    total_questions_answered: Optional[int] = None
    correct_answers: Optional[int] = None
    learning_streak: Optional[int] = None


class StudentProgressResponse(StudentProgressBase):
    id: UUID
    user_id: UUID
    last_learning_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True