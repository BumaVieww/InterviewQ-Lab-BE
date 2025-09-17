from pydantic import BaseModel
from datetime import datetime

class AnswerResponse(BaseModel):
    answer_id: int
    question_id: int
    respondent_id: int
    answer: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AnswerCreateRequest(BaseModel):
    answer: str

class AnswerUpdateRequest(BaseModel):
    answer: str

class AnswerCommentResponse(BaseModel):
    comment_id: int
    answer_id: int
    commenter_id: int
    comment: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AnswerCommentCreateRequest(BaseModel):
    comment: str

class AnswerCommentUpdateRequest(BaseModel):
    comment: str