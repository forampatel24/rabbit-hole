import os
import json
import logging
import re
import asyncio
import random
from typing import Dict, Any

from dotenv import load_dotenv
try:
    from groq import Groq
except Exception:
    Groq = None  # allow local dev without package

load_dotenv()

logger = logging.getLogger("groq")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("API KEY FOUND:", bool(GROQ_API_KEY))

if GROQ_API_KEY:
    print("API KEY PREFIX:", GROQ_API_KEY[:10])

MODEL = "llama-3.3-70b-versatile"

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY and Groq is not None else None
MOCK_MODE = client is None


async def send_prompt(prompt: str, retries: int = 3, backoff: float = 1.0) -> Dict[str, Any]:
    """
    Sends prompt to Groq and returns parsed JSON. In absence of an API key, returns a mocked response.
    Retries JSON parse failures automatically.
    """

    # Mock mode: synthesize reasonable JSON based on prompt contents
    if MOCK_MODE:
        return _mock_response(prompt)

    for attempt in range(1, retries + 1):
        try:
            print("\n" + "=" * 80)
            print("SENDING TO GROQ")
            print("=" * 80)
            print(prompt[:1000])
            print("=" * 80)
            response = client.chat.completions.create(
                
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are RabbitHole's knowledge graph engine. Return VALID JSON ONLY. "
                            "No markdown. No explanations. No code fences."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=4000,

                
            )

            # groq client shape may vary; be defensive
            content = None
            try:
                content = response.choices[0].message.content.strip()
                print("\n" + "=" * 80)
                print("GROQ RAW RESPONSE")
                print("=" * 80)
                print(content[:5000])
                print("=" * 80)
            except Exception:
                try:
                    content = response.choices[0].text.strip()
                except Exception:
                    content = str(response)

            # strip markdown fences
            content = content.replace("```json", "").replace("```", "").strip()

            try:
                parsed = json.loads(content)
            except Exception as e:
                print("\nJSON PARSE FAILED")
                print(e)
                print("\nRAW CONTENT:")
                print(content)
                raise

            return parsed

        except json.JSONDecodeError as e:
            logger.warning(f"Attempt {attempt}: Groq returned invalid JSON: {e}")
            if attempt < retries:
                await asyncio.sleep(backoff * attempt)
                continue
            raise
        except Exception as e:
            

            logger.error(f"Groq request failed on attempt {attempt}: {e}")
            if attempt < retries:
                await asyncio.sleep(backoff * attempt)
                continue
            raise


def _extract_topic_from_prompt(prompt: str) -> str:
    # Try common patterns
    m = re.search(r"[Tt]opic[:\s]+([A-Za-z0-9 '\-()]+)", prompt)
    if m:
        return m.group(1).strip()
    m = re.search(r"for topic[:\s]+([A-Za-z0-9 '\-()]+)", prompt, re.I)
    if m:
        return m.group(1).strip()
    # fallback: first capitalized phrase
    m = re.search(r"([A-Z][a-zA-Z0-9 ]{3,50})", prompt)
    return m.group(1).strip() if m else "Unknown"


def _mock_response(prompt: str) -> Dict[str, Any]:
    """Create a deterministic mock response based on prompt content.
    Mock data will focus on the requested topic and will not inject unrelated topics like 'Transformers' unless the topic is Transformers.
    """
    lower = prompt.lower()
    if 'expand' in lower and 'node' in lower:
        # expansion mock
        node_id_match = re.search(r"node[:\s]+([A-Za-z0-9_\-]+)", prompt, re.I)
        node_id = node_id_match.group(1) if node_id_match else "node_1"
        new_nodes = []
        new_edges = []
        new_node_details = {}
        for i in range(3):
            nid = f"{node_id}_exp_{i}"
            new_nodes.append({"id": nid, "name": f"{node_id} child {i}", "type": "related_concept"})
            new_edges.append({"source": node_id, "target": nid, "relationship": "related_to"})
            new_node_details[nid] = {"id": nid, "name": f"{node_id} child {i}", "type": "related_concept", "description": "Mocked node"}
        return {"new_nodes": new_nodes, "new_edges": new_edges, "new_node_details": new_node_details}

    if 'knowledge gap' in lower or 'knowledge gap' in prompt.lower():
        target = _extract_topic_from_prompt(prompt)
        known_match = re.search(r"known[:\s]+\[(.*?)\]", prompt)
        known = []
        if known_match:
            known = [k.strip().strip('\"\'') for k in known_match.group(1).split(',') if k.strip()]
        # simple mock: assume half known, half missing
        missing = [f"{target} topic {i}" for i in range(3) if f"{target} topic {i}" not in known]
        learning_path = known + missing
        return {"known": known, "missing": missing, "learning_path": learning_path}

    # default: assume graph generation
    topic = _extract_topic_from_prompt(prompt)
    # simple singularization for plural "Databases" -> "Database" but avoid breaking -ics words
    t_low = topic.lower()
    if t_low.endswith('s') and not t_low.endswith('ics'):
        graph_title = f"{topic[:-1]} graph"
    else:
        graph_title = f"{topic} graph"

    # build mock nodes and edges
    base = re.sub(r"[^a-z0-9]+", "_", topic.lower())
    nodes = []
    node_details = {}
    num_nodes = 12
    for i in range(num_nodes):
        nid = f"{base}_n{i}"
        name = f"{topic} Concept {i+1}"
        ntype = random.choice(["core_concept", "prerequisite", "application", "related_concept"])
        node = {
            "id": nid,
            "name": name,
            "type": ntype,
            "description": f"Mock description for {name}",
            "importance_score": round(random.uniform(0.1, 1.0), 2),
            "depth": random.randint(0, 3),
        }
        nodes.append(node)
        node_details[nid] = node

    edges = []
    for i in range(1, num_nodes):
        source = nodes[random.randint(0, i-1)]['id']
        target = nodes[i]['id']
        edges.append({"id": f"e_{i}", "source": source, "target": target, "relationship": "prerequisite_of"})
    # add some random cross links
    for i in range(3):
        a = random.choice(nodes)['id']
        b = random.choice(nodes)['id']
        if a != b:
            edges.append({"id": f"cross_{i}", "source": a, "target": b, "relationship": "related_to"})

    overview = {
        "topic": topic,
        "domain": "General",
        "difficulty": "Intermediate",
        "estimated_learning_time": "20-30 hours",
        "popularity": "Medium",
        "importance_level": "High",
        "applications": [f"Application {i}" for i in range(3)],
        "summary": f"Mock overview for {topic}",
    }

    return {"overview": overview, "graph": {"nodes": nodes, "edges": edges}, "node_details": node_details}
