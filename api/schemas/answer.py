from pydantic import BaseModel
from datetime import datetime

class AnswerResponse(BaseModel):
    answer_id: int
    question_id: int
    user_id: int
    answer: str

    class Config:
        from_attributes = True

class AnswerCreateRequest(BaseModel):
    answer: str

class AnswerUpdateRequest(BaseModel):
    answer: str

class AnswerCommentResponse(BaseModel):
    answer_comment_id: int
    answer_id: int
    user_id: int
    comment: str

    class Config:
        from_attributes = True

class AnswerCommentCreateRequest(BaseModel):
    comment: str

class AnswerCommentUpdateRequest(BaseModel):
    comment: str