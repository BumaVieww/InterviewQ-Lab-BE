from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from core.database import get_db
from core.pagination import paginate_cursor
from api.schemas.question import QuestionResponse, QuestionCreateRequest, QuestionUpdateRequest
from api.schemas.answer import AnswerResponse, AnswerCreateRequest
from api.schemas.base import BaseResponse, CursorPage
from app.domain.question.model.question import Question
from app.domain.question.model.answer import Answer
from typing import Optional

router = APIRouter(prefix="/questions", tags=["questions"])

@router.post("/", response_model=BaseResponse)
async def create_question(
    question_request: QuestionCreateRequest,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    db_question = Question(
        registrant_id=user_id,
        question=question_request.question,
        category=question_request.category,
        company_id=question_request.company_id,
        tag=question_request.tag
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return BaseResponse(message="Question created successfully", data=db_question.question_id)

@router.get("/", response_model=CursorPage[QuestionResponse])
async def get_questions(
    cursor_id: Optional[int] = None,
    size: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Question).order_by(Question.question_id)
    return paginate_cursor(query, cursor_id, size, Question.question_id)

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.patch("/{question_id}", response_model=BaseResponse)
async def update_question(
    question_id: int,
    question_request: QuestionUpdateRequest,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.registrant_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this question")

    question.question = question_request.question
    question.category = question_request.category
    question.tag = question_request.tag
    db.commit()
    return BaseResponse(message="Question updated successfully", data=None)

@router.delete("/{question_id}", response_model=BaseResponse)
async def delete_question(
    question_id: int,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.registrant_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this question")

    db.delete(question)
    db.commit()
    return BaseResponse(message="Question deleted successfully", data=None)

@router.post("/{question_id}/answers", response_model=BaseResponse)
async def create_answer(
    question_id: int,
    answer_request: AnswerCreateRequest,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    db_answer = Answer(
        question_id=question_id,
        respondent_id=user_id,
        answer=answer_request.answer
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return BaseResponse(message="Answer created successfully", data=db_answer.answer_id)

@router.get("/{question_id}/answers", response_model=CursorPage[AnswerResponse])
async def get_question_answers(
    question_id: int,
    cursor_id: Optional[int] = None,
    size: int = 20,
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    query = db.query(Answer).filter(Answer.question_id == question_id).order_by(Answer.answer_id)
    return paginate_cursor(query, cursor_id, size, Answer.answer_id)