import os
from ..models.schemas import ExpandNodeResponse, NodeSchema, EdgeSchema
from .groq_service import send_prompt

PROMPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'expand_prompt.txt')


async def expand_node(node_id: str, current_depth: int = 0) -> ExpandNodeResponse:
    with open(PROMPTS_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    prompt = template.format(node_id=node_id, current_depth=current_depth)
    raw = await send_prompt(prompt)
    new_nodes = raw.get('new_nodes', [])
    new_edges = raw.get('new_edges', [])
    new_node_details = raw.get('new_node_details', {})
    resp = ExpandNodeResponse(
        new_nodes=[NodeSchema(**n) for n in new_nodes],
        new_edges=[EdgeSchema(**e) for e in new_edges],
        new_node_details={k: NodeSchema(**v) for k, v in new_node_details.items()}
    )
    return resp
