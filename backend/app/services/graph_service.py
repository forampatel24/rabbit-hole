"""
Graph generation service for knowledge universe creation
"""

import logging
from typing import Dict, Any, List
from .groq_service import GroqService
from ..models.schemas import Node, Edge, Overview, Graph, GraphResponse
import os

logger = logging.getLogger(__name__)


class GraphService:
    """Service for generating knowledge graphs from topics"""

    def __init__(self):
        self.groq = GroqService()
        self.prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'graph_prompt.txt')

    def generate_graph(self, topic: str) -> GraphResponse:
        """
        Generate a complete knowledge graph for a topic

        Args:
            topic: The topic to generate a knowledge graph for

        Returns:
            GraphResponse containing overview, graph, and node_details
        """
        logger.info(f"Starting graph generation for topic: {topic}")

        # Read prompt template
        prompt = self._build_prompt(topic)
        logger.info("Prompt generated successfully")

        # Get response from Groq
        response_data = self.groq.generate(prompt)
        logger.info("Groq response received and parsed")

        # Process the response
        return self._process_response(response_data, topic)

    def _build_prompt(self, topic: str) -> str:
        """
        Build the prompt for Groq

        Args:
            topic: The topic to query

        Returns:
            Formatted prompt string
        """
        logger.debug("Building prompt for topic generation")

        try:
            with open(self.prompt_path, 'r') as f:
                template = f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found at {self.prompt_path}, using default template")
            template = self._get_default_prompt_template()

        # Replace topic placeholder
        prompt = template.replace("{TOPIC}", topic)
        logger.debug(f"Prompt built successfully, length: {len(prompt)}")
        return prompt

    def _get_default_prompt_template(self) -> str:
        """
        Get default prompt template if file is not found

        Returns:
            Default prompt template
        """
        return """Generate a comprehensive knowledge graph for the topic: {TOPIC}

Return ONLY valid JSON with no markdown, explanations, or additional text. The JSON must contain:

{
  "overview": {
    "topic": "{TOPIC}",
    "domain": "appropriate domain",
    "difficulty": "Beginner/Intermediate/Advanced",
    "estimated_learning_time": "estimated time",
    "popularity": "Low/Medium/High/Very High",
    "importance_level": "Low/Medium/High/Very High",
    "applications": ["application1", "application2"],
    "summary": "brief summary of the topic"
  },
  "nodes": [
    {
      "id": "unique_id",
      "name": "Node Name",
      "type": "prerequisite/core_concept/advanced_concept/application/framework/tool/mathematical_foundation/related_concept",
      "description": "detailed description",
      "difficulty": "Beginner/Intermediate/Advanced",
      "importance_score": 8.5,
      "estimated_learning_time": "time estimate",
      "prerequisites": [],
      "unlocks": [],
      "applications": [],
      "why_it_matters": "explanation of importance",
      "resources": {},
      "depth": 0
    }
  ],
  "edges": [
    {
      "id": "edge_id",
      "source": "source_id",
      "target": "target_id",
      "relationship": "prerequisite/related_concept/advanced_concept/application/framework/tool/mathematical_foundation"
    }
  ]
}

REQUIREMENTS:
- Generate at least 15 nodes
- Generate at least 14 edges
- Create a hierarchical structure from beginner to advanced
- Include prerequisite relationships
- All nodes must have unique IDs
- All edges must reference existing nodes
- Return ONLY the JSON object, nothing else
"""

    def _process_response(self, response_data: Dict[str, Any], topic: str) -> GraphResponse:
        """
        Process and validate the Groq response

        Args:
            response_data: Raw response from Groq
            topic: The original topic

        Returns:
            Validated GraphResponse
        """
        logger.info("Processing Groq response")

        try:
            # Extract overview
            overview_data = response_data.get("overview", {})
            overview = Overview(
                topic=overview_data.get("topic", topic),
                domain=overview_data.get("domain", "General"),
                difficulty=overview_data.get("difficulty", "Intermediate"),
                estimated_learning_time=overview_data.get("estimated_learning_time", "Unknown"),
                popularity=overview_data.get("popularity", "Medium"),
                importance_level=overview_data.get("importance_level", "High"),
                applications=overview_data.get("applications", []),
                summary=overview_data.get("summary", "")
            )
            logger.info(f"Overview processed: {overview.topic}")

            # Extract and process nodes
            nodes_data = response_data.get("nodes", [])
            nodes = []
            node_details = {}

            logger.info(f"Processing {len(nodes_data)} nodes")
            for node_data in nodes_data:
                try:
                    node = Node(
                        id=node_data.get("id", "").lower().replace(" ", "_"),
                        name=node_data.get("name", "Unknown"),
                        type=node_data.get("type", "core_concept"),
                        description=node_data.get("description", ""),
                        difficulty=node_data.get("difficulty", "Intermediate"),
                        importance_score=float(node_data.get("importance_score", 5.0)),
                        estimated_learning_time=node_data.get("estimated_learning_time", "Unknown"),
                        prerequisites=node_data.get("prerequisites", []),
                        unlocks=node_data.get("unlocks", []),
                        applications=node_data.get("applications", []),
                        why_it_matters=node_data.get("why_it_matters", ""),
                        resources=node_data.get("resources", {}),
                        depth=node_data.get("depth", 0)
                    )
                    nodes.append(node)
                    node_details[node.id] = node
                except Exception as e:
                    logger.warning(f"Failed to process node: {str(e)}", exc_info=True)
                    continue

            logger.info(f"Successfully processed {len(nodes)} nodes")

            # Extract and process edges
            edges_data = response_data.get("edges", [])
            edges = []
            node_ids = {n.id for n in nodes}

            logger.info(f"Processing {len(edges_data)} edges")
            for edge_data in edges_data:
                try:
                    source = edge_data.get("source", "").lower().replace(" ", "_")
                    target = edge_data.get("target", "").lower().replace(" ", "_")

                    # Only include edges where both nodes exist
                    if source not in node_ids or target not in node_ids:
                        logger.debug(f"Skipping edge: {source} -> {target} (nodes not found)")
                        continue

                    edge = Edge(
                        id=edge_data.get("id", f"{source}-{target}"),
                        source=source,
                        target=target,
                        relationship=edge_data.get("relationship", "related_concept")
                    )
                    edges.append(edge)
                except Exception as e:
                    logger.warning(f"Failed to process edge: {str(e)}", exc_info=True)
                    continue

            logger.info(f"Successfully processed {len(edges)} edges")

            # Create graph
            graph = Graph(nodes=nodes, edges=edges)

            # Validate minimum requirements
            if len(nodes) < 15:
                logger.warning(f"Generated only {len(nodes)} nodes, requirement is 15+")
            if len(edges) < 14:
                logger.warning(f"Generated only {len(edges)} edges, requirement is 14+")

            # Create response
            response = GraphResponse(
                overview=overview,
                graph=graph,
                node_details=node_details
            )

            logger.info(f"Graph generation complete: {len(nodes)} nodes, {len(edges)} edges")
            return response

        except Exception as e:
            logger.error(f"Error processing response: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to process graph response: {str(e)}")

