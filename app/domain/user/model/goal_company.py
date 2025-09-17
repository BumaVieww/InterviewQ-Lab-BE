from sqlalchemy import Column, Integer, ForeignKey
from core.database import Base

class GoalCompany(Base):
    __tablename__ = "goal_company"

    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, primary_key=True)
    company_id = Column(Integer, ForeignKey("company.company_id"), nullable=False, primary_key=True)