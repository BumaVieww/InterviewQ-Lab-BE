from pydantic import BaseModel, field_serializer
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

    @field_serializer('question_at')
    def serialize_question_at(self, value: date) -> str:
        """년도만 반환"""
        return str(value.year)

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