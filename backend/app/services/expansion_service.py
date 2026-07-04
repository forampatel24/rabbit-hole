import logging
import os
from typing import Dict, Any
from .groq_service import GroqService
from ..models.schemas import Node, Edge, ExpandNodeResponse

logger = logging.getLogger(__name__)


class ExpansionService:
    def __init__(self):
        self.groq = GroqService()
        self.prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'expand_prompt.txt')

    def expand_node(self, node_id: str, current_depth: int, existing_node_ids: list) -> ExpandNodeResponse:
        logger.info(f"Expanding node: {node_id} at depth {current_depth}")

        prompt = self._build_prompt(node_id, current_depth, existing_node_ids)
        response_data = self.groq.generate(prompt)

        return self._process_response(response_data, node_id)

    def _build_prompt(self, node_id: str, current_depth: int, existing_node_ids: list) -> str:
        logger.debug(f"Building expand prompt for node: {node_id}")

        try:
            with open(self.prompt_path, 'r') as f:
                template = f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found at {self.prompt_path}, using default template")
            template = self._get_default_prompt_template()

        existing_ids_str = ", ".join(existing_node_ids) if existing_node_ids else "none"
        prompt = template.replace("{node_id}", node_id)
        prompt = prompt.replace("{current_depth}", str(current_depth))
        prompt = prompt.replace("{existing_node_ids}", existing_ids_str)
        logger.debug(f"Expand prompt built, length: {len(prompt)}")
        return prompt

    def _get_default_prompt_template(self) -> str:
        return """Expand the concept "{node_id}" and discover related sub-concepts, prerequisites, applications, and deeper knowledge.

Current depth level: {current_depth}
Already existing node IDs (DO NOT recreate): [{existing_node_ids}]

Return ONLY valid JSON with no markdown, no explanations, no additional text. The JSON structure MUST be:

{
  "new_nodes": [
    {
      "id": "unique_lowercase_id",
      "name": "Concept Name",
      "type": "prerequisite|core_concept|advanced_concept|application|framework|tool|mathematical_foundation|related_concept",
      "description": "detailed explanation",
      "difficulty": "Beginner|Intermediate|Advanced",
      "importance_score": 8.5,
      "estimated_learning_time": "duration",
      "prerequisites": ["id1", "id2"],
      "unlocks": ["id3"],
      "applications": ["app1"],
      "why_it_matters": "importance explanation",
      "resources": {},
      "depth": DEPTH
    }
  ],
  "new_edges": [
    {
      "id": "edge_unique_id",
      "source": "source_id",
      "target": "target_id",
      "relationship": "prerequisite|related_concept|advanced_concept|application|framework|tool|mathematical_foundation"
    }
  ],
  "new_node_details": {}
}

CRITICAL REQUIREMENTS:
1. Generate 3-8 new nodes
2. Generate edges connecting new nodes to each other and to the expanded node
3. The expanded node ID is: {node_id}
4. Set depth of new nodes to {current_depth} + 1
5. All node IDs must be lowercase with underscores
6. All edges must reference existing nodes only (either the parent or newly created nodes)
7. Include diverse node types
8. Return ONLY the JSON object - no markdown fences, no explanations
9. Every node must have all required fields
10. Importance scores should be 0-10 scale
"""

    def _process_response(self, response_data: Dict[str, Any], node_id: str) -> ExpandNodeResponse:
        logger.info("Processing expansion response")

        try:
            new_nodes_data = response_data.get("new_nodes", [])
            new_nodes = []
            new_node_details = {}

            for node_data in new_nodes_data:
                try:
                    node = Node(
                        id=node_data.get("id", "").lower().replace(" ", "_"),
                        name=node_data.get("name", "Unknown"),
                        type=node_data.get("type", "related_concept"),
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
                    new_nodes.append(node)
                    new_node_details[node.id] = node
                except Exception as e:
                    logger.warning(f"Failed to process expanded node: {str(e)}", exc_info=True)
                    continue

            new_edges_data = response_data.get("new_edges", [])
            new_edges = []
            new_node_ids = {n.id for n in new_nodes}

            for edge_data in new_edges_data:
                try:
                    source = edge_data.get("source", "").lower().replace(" ", "_")
                    target = edge_data.get("target", "").lower().replace(" ", "_")

                    if source not in new_node_ids and source != node_id:
                        logger.debug(f"Skipping edge: source {source} not in new nodes or parent")
                        continue
                    if target not in new_node_ids and target != node_id:
                        logger.debug(f"Skipping edge: target {target} not in new nodes or parent")
                        continue

                    edge = Edge(
                        id=edge_data.get("id", f"{source}-{target}"),
                        source=source,
                        target=target,
                        relationship=edge_data.get("relationship", "related_concept")
                    )
                    new_edges.append(edge)
                except Exception as e:
                    logger.warning(f"Failed to process expansion edge: {str(e)}", exc_info=True)
                    continue

            logger.info(f"Expansion complete: {len(new_nodes)} new nodes, {len(new_edges)} new edges")
            return ExpandNodeResponse(
                new_nodes=new_nodes,
                new_edges=new_edges,
                new_node_details=new_node_details
            )

        except Exception as e:
            logger.error(f"Error processing expansion response: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to process expansion response: {str(e)}")
