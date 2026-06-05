from pydantic import BaseModel, Field, AnyUrl
from typing import List, Dict, Optional
from enum import Enum

# Existing enums and schemas (kept for backward compatibility)
class NodeType(str, Enum):
    prerequisite = 'prerequisite'
    core_concept = 'core_concept'
    advanced_concept = 'advanced_concept'
    application = 'application'
    framework = 'framework'
    tool = 'tool'
    mathematical_foundation = 'mathematical_foundation'
    related_concept = 'related_concept'

class OverviewSchema(BaseModel):
    topic: str
    domain: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_learning_time: Optional[str] = None
    popularity: Optional[str] = None
    importance_level: Optional[str] = None
    applications: List[str] = []
    summary: Optional[str] = None

class ResourceSchema(BaseModel):
    title: Optional[str]
    url: Optional[AnyUrl]
    type: Optional[str]

class NodeSchema(BaseModel):
    id: str
    name: str
    type: NodeType
    description: Optional[str] = None
    difficulty: Optional[str] = None
    importance_score: float = 0.0
    estimated_learning_time: Optional[str] = None
    prerequisites: List[str] = []
    unlocks: List[str] = []
    applications: List[str] = []
    why_it_matters: Optional[str] = None
    resources: Dict[str, List[ResourceSchema]] = {}
    depth: int = 0

class EdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    relationship: str

class GraphSchema(BaseModel):
    nodes: List[NodeSchema] = []
    edges: List[EdgeSchema] = []

class GraphResponseSchema(BaseModel):
    overview: OverviewSchema
    graph: GraphSchema
    node_details: Dict[str, NodeSchema] = {}

class ExpandNodeRequest(BaseModel):
    node_id: str
    current_depth: Optional[int] = 0

class ExpandNodeResponse(BaseModel):
    new_nodes: List[NodeSchema] = []
    new_edges: List[EdgeSchema] = []
    new_node_details: Dict[str, NodeSchema] = {}

class KnowledgeGapRequest(BaseModel):
    known_concepts: List[str]
    target_topic: str

class KnowledgeGapResponse(BaseModel):
    known: List[str] = []
    missing: List[str] = []
    learning_path: List[str] = []

class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    code: str

class TopicRequest(BaseModel):
    topic: str

class HealthResponse(BaseModel):
    status: str
    service: str

# Aliases and required names per task (retain schema validation)
class TopicOverview(OverviewSchema):
    pass

class Node(NodeSchema):
    pass

class Edge(EdgeSchema):
    pass

class GraphResponse(GraphResponseSchema):
    pass

# ExpandNodeRequest, ExpandNodeResponse, KnowledgeGapRequest, KnowledgeGapResponse, ErrorResponse
# already exist with compatible names (ExpandNodeRequest, ExpandNodeResponse, KnowledgeGapRequest, KnowledgeGapResponse, ErrorResponse)
# Provide direct aliases for the exact names requested by the task where needed
ExpandNodeRequestAlias = ExpandNodeRequest
ExpandNodeResponseAlias = ExpandNodeResponse
KnowledgeGapRequestAlias = KnowledgeGapRequest
KnowledgeGapResponseAlias = KnowledgeGapResponse
ErrorResponseAlias = ErrorResponse

# For clarity, also expose the requested class names directly
ExpandNodeRequest = ExpandNodeRequest
ExpandNodeResponse = ExpandNodeResponse
KnowledgeGapRequest = KnowledgeGapRequest
KnowledgeGapResponse = KnowledgeGapResponse
ErrorResponse = ErrorResponse
