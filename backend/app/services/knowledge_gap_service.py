import logging
import os
from typing import List
from .groq_service import GroqService
from ..models.schemas import KnowledgeGapResponse

logger = logging.getLogger(__name__)


class KnowledgeGapService:
    def __init__(self):
        self.groq = GroqService()
        self.prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'knowledge_gap_prompt.txt')

    def analyze_gap(self, known_concepts: List[str], target_topic: str) -> KnowledgeGapResponse:
        logger.info(f"Analyzing knowledge gap for target: {target_topic}")

        prompt = self._build_prompt(known_concepts, target_topic)
        response_data = self.groq.generate(prompt)

        return self._process_response(response_data, known_concepts, target_topic)

    def _build_prompt(self, known_concepts: List[str], target_topic: str) -> str:
        logger.debug("Building knowledge gap prompt")

        try:
            with open(self.prompt_path, 'r') as f:
                template = f.read()
        except FileNotFoundError:
            logger.warning(f"Prompt file not found at {self.prompt_path}, using default template")
            template = self._get_default_prompt_template()

        known_str = ", ".join(known_concepts) if known_concepts else "none"
        prompt = template.replace("{target_topic}", target_topic)
        prompt = prompt.replace("{known_concepts}", known_str)
        logger.debug(f"Knowledge gap prompt built, length: {len(prompt)}")
        return prompt

    def _get_default_prompt_template(self) -> str:
        return """Analyze the knowledge gap between known concepts and a target topic.

Target topic: {target_topic}
Known concepts: [{known_concepts}]

Identify which known concepts are relevant prerequisites for the target topic, what concepts are missing, and generate a recommended learning path.

Return ONLY valid JSON with no markdown, no explanations, no additional text:

{
  "known": ["concept1", "concept2"],
  "missing": ["missing_concept1", "missing_concept2"],
  "learning_path": ["step1", "step2", "step3"]
}

CRITICAL REQUIREMENTS:
1. known: concepts from the input that are relevant prerequisites for the target
2. missing: concepts needed to go from known to target (ordered by dependency)
3. learning_path: ordered list from first missing concept to target topic
4. All fields must be arrays of strings
5. Return ONLY the JSON object
"""

    def _process_response(self, response_data: dict, known_concepts: List[str], target_topic: str) -> KnowledgeGapResponse:
        logger.info("Processing knowledge gap response")

        try:
            known = response_data.get("known", [])
            missing = response_data.get("missing", [])
            learning_path = response_data.get("learning_path", [])

            if not isinstance(known, list):
                known = []
            if not isinstance(missing, list):
                missing = []
            if not isinstance(learning_path, list):
                learning_path = []

            if not known and not missing and not learning_path:
                logger.warning("Knowledge gap response returned empty arrays")

            logger.info(f"Knowledge gap analysis: {len(known)} known, {len(missing)} missing, {len(learning_path)} path steps")
            return KnowledgeGapResponse(
                known=known,
                missing=missing,
                learning_path=learning_path
            )

        except Exception as e:
            logger.error(f"Error processing knowledge gap response: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to process knowledge gap response: {str(e)}")
