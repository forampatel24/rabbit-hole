import os
from ..models.schemas import KnowledgeGapResponse
from .groq_service import send_prompt

PROMPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'knowledge_gap_prompt.txt')


async def analyze(known_concepts, target_topic) -> KnowledgeGapResponse:
    with open(PROMPTS_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    # known_concepts expected as list
    known_str = ", ".join(known_concepts) if isinstance(known_concepts, (list, tuple)) else str(known_concepts)
    prompt = template.format(target_topic=target_topic, known_concepts=known_str)
    raw = await send_prompt(prompt)
    # raw expected to contain known/missing/learning_path
    return KnowledgeGapResponse(known=raw.get('known', []), missing=raw.get('missing', []), learning_path=raw.get('learning_path', []))
