from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nickname = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    is_onboarding = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    questions = relationship("Question", back_populates="registrant")
    answers = relationship("Answer", back_populates="respondent")
    comments = relationship("AnswerComment", back_populates="commenter")
    goal_companies = relationship("GoalCompany", back_populates="user")
    user_positions = relationship("UserPosition", back_populates="user")