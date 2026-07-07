from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from ..database import Base


class ResourceCache(Base):
    __tablename__ = "resource_cache"

    id = Column(Integer, primary_key=True, index=True)
    concept_name = Column(String(200), nullable=False, unique=True, index=True)
    youtube_json = Column(Text, nullable=True)
    courses_json = Column(Text, nullable=True)
    papers_json = Column(Text, nullable=True)
    github_json = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
