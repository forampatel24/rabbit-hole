from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class TopicRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200, description="The topic to generate a knowledge graph for")
    mode: str = Field(default="learn", description="Exploration mode: learn, interview, project, research, quick")


class Overview(BaseModel):
    topic: str
    domain: str
    difficulty: str
    estimated_learning_time: str
    popularity: str
    importance_level: str
    applications: List[str]
    summary: str


class Node(BaseModel):
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
    id: str
    source: str
    target: str
    relationship: str


class Graph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


class GraphResponse(BaseModel):
    overview: Overview
    graph: Graph
    node_details: Dict[str, Node]


class HealthResponse(BaseModel):
    status: str
    service: str


class ExpandNodeRequest(BaseModel):
    node_id: str = Field(..., min_length=1, description="The node ID to expand")
    current_depth: int = Field(default=1, ge=0, description="Current depth of the node")


class ExpandNodeResponse(BaseModel):
    new_nodes: List[Node]
    new_edges: List[Edge]
    new_node_details: Dict[str, Node]


class KnowledgeGapRequest(BaseModel):
    known_concepts: List[str] = Field(default_factory=list, description="Concepts the user already knows")
    target_topic: str = Field(..., min_length=1, description="The target topic to learn")


class KnowledgeGapResponse(BaseModel):
    known: List[str]
    missing: List[str]
    learning_path: List[str]


class YouTubeResource(BaseModel):
    title: str
    channel: str
    thumbnail: str
    url: str
    duration: str


class CourseResource(BaseModel):
    provider: str
    title: str
    url: str
    thumbnail: Optional[str] = None


class PaperResource(BaseModel):
    title: str
    authors: List[str]
    year: Optional[int] = None
    citation_count: Optional[int] = None
    doi: Optional[str] = None
    openalex_url: Optional[str] = None
    pdf_url: Optional[str] = None


class GitHubResource(BaseModel):
    repo_name: str
    description: Optional[str] = None
    stars: Optional[int] = None
    language: Optional[str] = None
    url: str


class LearningResourcesResponse(BaseModel):
    youtube: List[YouTubeResource] = Field(default_factory=list)
    courses: List[CourseResource] = Field(default_factory=list)
    papers: List[PaperResource] = Field(default_factory=list)
    github: List[GitHubResource] = Field(default_factory=list)


class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class CollectionRename(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class CollectionResponse(BaseModel):
    id: int
    name: str
    created_at: str
    graph_count: int = 0


class CollectionDetail(BaseModel):
    id: int
    name: str
    created_at: str
    graphs: List[Dict[str, Any]] = Field(default_factory=list)


class GraphMoveRequest(BaseModel):
    target_collection_id: Optional[int] = None


class GraphCopyRequest(BaseModel):
    target_collection_id: int


class SearchResult(BaseModel):
    id: int
    topic: str
    collection_name: Optional[str] = None
    collection_id: Optional[int] = None
    created_at: str
    completed_count: int = 0
    total_count: int = 0


class SearchResults(BaseModel):
    results: List[SearchResult] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: bool
    message: str
    code: str
