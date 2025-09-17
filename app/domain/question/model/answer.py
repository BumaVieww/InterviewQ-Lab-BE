from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base

class Answer(Base):
    __tablename__ = "answer"

    answer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("question.question_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    answer = Column(String(255), nullable=False)