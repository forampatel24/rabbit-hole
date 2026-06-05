import os
import asyncio
import time
from typing import Dict
from ..models.schemas import GraphResponseSchema
from ..models.schemas import OverviewSchema, GraphSchema, NodeSchema
from .groq_service import send_prompt
from pydantic import ValidationError

PROMPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'graph_prompt.txt')


def _format_title(topic: str) -> str:
    t_low = topic.lower()
    # Avoid naive singularization for -ics words (physics, statistics)
    if t_low.endswith('s') and not t_low.endswith('ics'):
        return f"{topic[:-1]} graph"
    return f"{topic} graph"


async def generate_graph(topic: str, retries: int = 3) -> GraphResponseSchema:

    print("GENERATE_GRAPH CALLED")
    print("TOPIC =", topic)
    print("PROMPT PATH =", PROMPTS_PATH)
    # Load prompt template
    with open(PROMPTS_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    title = _format_title(topic)
    prompt = (
    template
    .replace("{topic}", topic)
    .replace("{graph_title}", title)
    )

    last_err = None
    for attempt in range(1, retries + 1):
        print("BEFORE SEND_PROMPT")

        raw = await send_prompt(prompt)
        for node in raw.get("graph", {}).get("nodes", []):
            if "label" in node and "name" not in node:
                node["name"] = node.pop("label")

            if "type" not in node:
                node["type"] = "core_concept"

        for i, edge in enumerate(raw.get("graph", {}).get("edges", [])):
            if "label" in edge and "relationship" not in edge:
                edge["relationship"] = edge.pop("label")

            if "id" not in edge:
                edge["id"] = f"edge_{i}"

        for node_id, details in raw.get("node_details", {}).items():
            details.setdefault("id", node_id)
            details.setdefault("name", node_id)
            details.setdefault("type", "core_concept")
        print("AFTER SEND_PROMPT")
        print("\n" + "=" * 80)
        print("RAW RESPONSE")
        print("=" * 80)
        print(raw)
        print("=" * 80 + "\n")

        # Validate against schema
        try:
            resp = GraphResponseSchema.parse_obj(raw)

            # Enforce minimum sizes for visualization
            nodes_len = len(resp.graph.nodes or [])
            edges_len = len(resp.graph.edges or [])
            if nodes_len < 5:
                raise ValueError(f"Insufficient graph size: nodes={nodes_len}, edges={edges_len}")

            # Ensure topic appears in overview
            if getattr(resp.overview, 'topic', '').lower() != topic.lower():
                # allow some leeway: set it explicitly
                resp.overview.topic = topic

            return resp

        except (ValidationError, ValueError, KeyError) as e:
            print("\nVALIDATION FAILED")
            print(type(e).__name__)
            print(str(e))

            print("\nRAW DATA RECEIVED:")
            print(raw)
            print()

            last_err = e

            if attempt < retries:
                await asyncio.sleep(attempt)
                continue

            raise Exception(
                f"Failed to generate valid graph after {retries} attempts: {e}")

    raise Exception(f"Failed to generate graph: {last_err}")
