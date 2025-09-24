from sqlalchemy import Column, Integer, ForeignKey, Text
from core.database import Base

class KeywordsByPosition(Base):
    __tablename__ = "keywords_by_position"

    keywords_by_position_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    position_id = Column(Integer, ForeignKey("position.position_id"), nullable=False)
    keywords = Column(Text)