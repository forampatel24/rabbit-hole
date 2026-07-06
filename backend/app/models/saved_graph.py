"""
Saved graph model for RabbitHole
Stores graph data as JSON for instant reopening
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from ..database import Base


class SavedGraph(Base):
    __tablename__ = "saved_graphs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(200), nullable=False)
    graph_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_opened_at = Column(DateTime, default=datetime.utcnow)
