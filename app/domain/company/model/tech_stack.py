from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .company_job_posting import CompanyJobPosting

class TechStack(Base):
    __tablename__ = "tech_stack"

    tech_stack_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    company_job_position_id = Column(BigInteger, ForeignKey("company_job_posting.company_job_posting_id"), nullable=True)
    tech_name = Column(String(255), nullable=True)

    # Relationship (back_populates defined in CompanyJobPosting)
