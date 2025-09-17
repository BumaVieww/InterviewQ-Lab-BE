from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QuestionResponse(BaseModel):
    question_id: int
    registrant_id: int
    question: str
    category: str
    company_id: int
    tag: str
    question_at: datetime

    class Config:
        from_attributes = True

class QuestionCreateRequest(BaseModel):
    question: str
    category: str
    company_id: int
    tag: str

class QuestionUpdateRequest(BaseModel):
    question: str
    category: str
    tag: str