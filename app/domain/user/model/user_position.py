from sqlalchemy import Column, Integer, ForeignKey
from core.database import Base

class UserPosition(Base):
    __tablename__ = "user_position"

    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, primary_key=True)
    position_id = Column(Integer, ForeignKey("position.position_id"), nullable=False, primary_key=True)