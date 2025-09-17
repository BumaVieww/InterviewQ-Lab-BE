from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Text
from core.database import Base
import enum

class QuestionTag(str, enum.Enum):
    TENACITY = "tenacity"
    TECHNOLOGY = "technology"

class Question(Base):
    __tablename__ = "question"

    question_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("company.company_id"), nullable=False)
    registrant_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    question = Column(Text, nullable=False)
    category = Column(String(100))
    tag = Column(Enum(QuestionTag), nullable=False)
    question_at = Column(Date, nullable=False)