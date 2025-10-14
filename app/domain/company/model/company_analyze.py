from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from core.database import Base

class CompanyAnalyze(Base):
    __tablename__ = "company_analyze"

    company_analyze_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("company.company_id"), nullable=False)
    result = Column(Text)
    analyzed_at = Column(DateTime)
    from_field = Column("from", Text)