from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import get_current_user
from core.pagination import paginate_cursor
from api.schemas.answer import (
    AnswerResponse, AnswerUpdateRequest, AnswerCommentResponse,
    AnswerCommentCreateRequest, AnswerCommentUpdateRequest
)
from api.schemas.base import BaseResponse, CursorPage
from app.domain.question.model.answer import Answer
from app.domain.question.model.answer_comment import AnswerComment
from app.domain.user.model.user import User
from typing import Optional

router = APIRouter(prefix="/answers", tags=["answers"])

@router.get("/{answer_id}", response_model=AnswerResponse)
async def get_answer(answer_id: int, db: Session = Depends(get_db)):
    answer = db.query(Answer).filter(Answer.answer_id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    return answer

@router.patch("/{answer_id}", response_model=BaseResponse)
async def update_answer(
    answer_id: int,
    answer_request: AnswerUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    answer = db.query(Answer).filter(Answer.answer_id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    if answer.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this answer")

    answer.answer = answer_request.answer
    db.commit()
    return BaseResponse(message="Answer updated successfully", data=None)

@router.delete("/{answer_id}", response_model=BaseResponse)
async def delete_answer(
    answer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    answer = db.query(Answer).filter(Answer.answer_id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    if answer.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this answer")

    db.delete(answer)
    db.commit()
    return BaseResponse(message="Answer deleted successfully", data=None)

@router.post("/{answer_id}/comments", response_model=BaseResponse)
async def create_answer_comment(
    answer_id: int,
    comment_request: AnswerCommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    answer = db.query(Answer).filter(Answer.answer_id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    db_comment = AnswerComment(
        answer_id=answer_id,
        user_id=current_user.user_id,
        comment=comment_request.comment
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return BaseResponse(message="Comment created successfully", data=db_comment.answer_comment_id)

@router.get("/{answer_id}/comments", response_model=CursorPage[AnswerCommentResponse])
async def get_answer_comments(
    answer_id: int,
    cursor_id: Optional[int] = None,
    size: int = 20,
    db: Session = Depends(get_db)
):
    answer = db.query(Answer).filter(Answer.answer_id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    query = db.query(AnswerComment).filter(AnswerComment.answer_id == answer_id).order_by(AnswerComment.answer_comment_id)
    return paginate_cursor(query, cursor_id, size, AnswerComment.answer_comment_id)

@router.patch("/comments/{comment_id}", response_model=BaseResponse)
async def update_answer_comment(
    comment_id: int,
    comment_request: AnswerCommentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment = db.query(AnswerComment).filter(AnswerComment.answer_comment_id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    comment.comment = comment_request.comment
    db.commit()
    return BaseResponse(message="Comment updated successfully", data=None)

@router.delete("/comments/{comment_id}", response_model=BaseResponse)
async def delete_answer_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment = db.query(AnswerComment).filter(AnswerComment.answer_comment_id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()
    return BaseResponse(message="Comment deleted successfully", data=None)