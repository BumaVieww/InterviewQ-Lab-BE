from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base

class AnswerComment(Base):
    __tablename__ = "answer_comment"

    answer_comment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    answer_id = Column(Integer, ForeignKey("answer.answer_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    comment = Column(String(255), nullable=False)