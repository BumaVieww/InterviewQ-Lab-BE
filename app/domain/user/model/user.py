from sqlalchemy import Column, BigInteger, String, Boolean
from core.database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True)
    nickname = Column(String(100))
    email = Column(String(255))
    role = Column(String(30))
    is_onboarding = Column(Boolean)