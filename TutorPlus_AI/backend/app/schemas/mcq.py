from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional, List


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MCQOptionBase(BaseModel):
    option_text: str
    option_letter: str


class MCQOptionCreate(MCQOptionBase):
    is_correct: bool


class MCQOptionResponse(MCQOptionBase):
    id: UUID
    is_correct: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MCQBase(BaseModel):
    question: str
    subject: str
    topic: str
    difficulty: Difficulty = Difficulty.MEDIUM
    explanation: Optional[str] = None
    language: str = "en"


class MCQCreate(MCQBase):
    options: List[MCQOptionCreate]


class MCQResponse(MCQBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    options: List[MCQOptionResponse] = []
    
    class Config:
        from_attributes = True


class MCQAttemptBase(BaseModel):
    selected_option_id: Optional[UUID] = None
    time_spent_seconds: int = 0


class MCQAttemptCreate(MCQAttemptBase):
    mcq_id: UUID


class MCQAttemptResponse(MCQAttemptBase):
    id: UUID
    user_id: UUID
    mcq_id: UUID
    is_correct: bool
    attempted_at: datetime
    
    class Config:
        from_attributes = True