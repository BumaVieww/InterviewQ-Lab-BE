from sqlalchemy import Column, BigInteger, String
from core.database import Base

class Company(Base):
    __tablename__ = "company"

    company_id = Column(BigInteger, primary_key=True)
    company_name = Column(String(255))