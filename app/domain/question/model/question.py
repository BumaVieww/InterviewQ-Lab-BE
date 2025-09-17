from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class QuestionCategory(str, enum.Enum):
    TECHNICAL = "TECHNICAL"
    BEHAVIORAL = "BEHAVIORAL"
    COMPANY = "COMPANY"

class QuestionTag(str, enum.Enum):
    TENACITY = "tenacity"
    TECHNOLOGY = "technology"

class Question(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    registrant_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    question = Column(String(1000), nullable=False)
    category = Column(Enum(QuestionCategory), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    tag = Column(Enum(QuestionTag), nullable=False)
    question_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    registrant = relationship("User", back_populates="questions")
    company = relationship("Company", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")