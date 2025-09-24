from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.domain.question.model.question import QuestionTag

class QuestionResponse(BaseModel):
    question_id: int
    company_id: int
    registrant_id: int
    question: str
    category: str
    tag: str
    question_at: date

    class Config:
        from_attributes = True

class QuestionCreateRequest(BaseModel):
    question: str
    category: str
    company_id: int
    tag: QuestionTag

class QuestionUpdateRequest(BaseModel):
    question: str
    category: str
    tag: QuestionTag