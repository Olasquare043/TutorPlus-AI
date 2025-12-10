from pydantic import BaseModel, Field
from typing import Optional


class TutorRequestBase(BaseModel):
    query: str = Field(..., min_length=5, max_length=2000)
    subject: Optional[str] = None
    topic: Optional[str] = None
    language: str = "en"


class TutorRequest(TutorRequestBase):
    pass


class TutorResponse(BaseModel):
    response_text: str
    response_audio_url: Optional[str] = None
    language: str
    sources: Optional[list] = None


class MCQGenerationRequest(BaseModel):
    subject: str = Field(..., min_length=3)
    topic: str = Field(..., min_length=3)
    number_of_questions: int = Field(default=5, ge=1, le=20)
    difficulty: Optional[str] = None
    language: str = "en"


class VoiceGenerationRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000)
    language: str = "en"


class VoiceGenerationResponse(BaseModel):
    audio_url: str
    language: str
    duration_seconds: float