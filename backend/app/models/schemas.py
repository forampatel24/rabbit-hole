"""
Pydantic schemas for RabbitHole API
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class TopicRequest(BaseModel):
    """Request schema for topic input"""
    topic: str = Field(..., min_length=1, max_length=200, description="The topic to generate a knowledge graph for")


class Overview(BaseModel):
    """Topic overview information"""
    topic: str
    domain: str
    difficulty: str
    estimated_learning_time: str
    popularity: str
    importance_level: str
    applications: List[str]
    summary: str


class Node(BaseModel):
    """Node in the knowledge graph"""
    id: str
    name: str
    type: str
    description: str
    difficulty: str
    importance_score: float
    estimated_learning_time: str
    prerequisites: List[str] = Field(default_factory=list)
    unlocks: List[str] = Field(default_factory=list)
    applications: List[str] = Field(default_factory=list)
    why_it_matters: str
    resources: Dict[str, Any] = Field(default_factory=dict)
    depth: int = 0


class Edge(BaseModel):
    """Edge between nodes in the knowledge graph"""
    id: str
    source: str
    target: str
    relationship: str


class Graph(BaseModel):
    """Knowledge graph structure"""
    nodes: List[Node]
    edges: List[Edge]


class GraphResponse(BaseModel):
    """Response for graph generation"""
    overview: Overview
    graph: Graph
    node_details: Dict[str, Node]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: bool
    message: str
    code: str

