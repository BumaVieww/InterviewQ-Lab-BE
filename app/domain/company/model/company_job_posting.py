from sqlalchemy import Column, BigInteger, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .company import Company

class CompanyJobPosting(Base):
    __tablename__ = "company_job_posting"

    company_job_posting_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("company.company_id"), nullable=True)
    job_id = Column(Text, nullable=True)
    overview = Column(String(255), nullable=True)
    key_responsibilities = Column(String(255), nullable=True)
    preferred_qualifications = Column(String(255), nullable=True)
    benefits_and_perks = Column(String(255), nullable=True)
    hiring_process = Column(String(255), nullable=True)
    employment_type = Column(String(255), nullable=True)
    application_deadline = Column(Date, nullable=True)
    work_location = Column(String(255), nullable=True)

    # Relationships
    company = relationship("Company", backref="job_postings")
    tech_stacks = relationship("TechStack", backref="job_posting")
