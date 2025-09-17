from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class Position(Base):
    __tablename__ = "positions"

    position_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    position_name = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user_positions = relationship("UserPosition", back_populates="position")