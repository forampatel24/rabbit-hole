"""
Graph note model for RabbitHole
Each saved graph has its own notes
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from ..database import Base


class GraphNote(Base):
    __tablename__ = "graph_notes"

    id = Column(Integer, primary_key=True, index=True)
    saved_graph_id = Column(Integer, ForeignKey("saved_graphs.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
