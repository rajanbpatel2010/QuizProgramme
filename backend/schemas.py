from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime

VALID_ROLES = [
    "Fresher Software Developer",
    "Experienced Software Developer",
    "Advanced Software Developer",
    "Technical Lead",
    "Technical Architect",
    "Project Manager",
    "Program Manager",
]

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in VALID_ROLES:
            raise ValueError(f'Invalid role. Must be one of: {VALID_ROLES}')
        return v

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class AnswerResponse(BaseModel):
    id: int
    answer_text: str

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    practical_example: Optional[str] = None
    answers: list[AnswerResponse] = []

    class Config:
        from_attributes = True

class AssessmentStateResponse(BaseModel):
    questions: list[QuestionResponse]
    answered_map: dict[int, int] # Maps question_id -> selected_answer_id


class SubmitAnswer(BaseModel):
    question_id: int
    selected_answer_id: Optional[int] = None # None means time expired or skipped

class TestAttemptResponse(BaseModel):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[int] = None
    total: Optional[int] = None
    ai_summary: Optional[str] = None

    class Config:
        from_attributes = True
