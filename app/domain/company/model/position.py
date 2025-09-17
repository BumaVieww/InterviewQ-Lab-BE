from sqlalchemy import Column, Integer, String
from core.database import Base

class Position(Base):
    __tablename__ = "position"

    position_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    position_name = Column(String(50), nullable=False)