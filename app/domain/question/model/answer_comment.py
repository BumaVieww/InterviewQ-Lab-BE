from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class AnswerComment(Base):
    __tablename__ = "answer_comments"

    comment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    answer_id = Column(Integer, ForeignKey("answers.answer_id"), nullable=False)
    commenter_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    answer = relationship("Answer", back_populates="comments")
    commenter = relationship("User", back_populates="comments")