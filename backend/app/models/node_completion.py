"""
Node completion model for RabbitHole
Tracks which nodes in a saved graph are marked as completed
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from ..database import Base


class NodeCompletion(Base):
    __tablename__ = "node_completions"

    id = Column(Integer, primary_key=True, index=True)
    saved_graph_id = Column(Integer, ForeignKey("saved_graphs.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("saved_graph_id", "node_id", name="uq_graph_node"),
    )
