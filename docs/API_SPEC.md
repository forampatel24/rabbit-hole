# RabbitHole - API Specification

## Overview
The backend should attempt to reuse previously generated graph data whenever possible.

Knowledge Gap Detection and Node Expansion should operate on existing graph structures rather than generating entirely new graphs whenever feasible.

RabbitHole uses a REST API architecture.

The frontend communicates exclusively with the FastAPI backend.

The backend communicates with Groq.

The frontend never communicates directly with Groq.

All requests and responses use JSON.

Base URL:

```text
/api/v1
```

---

# Authentication

Authentication is not part of MVP.

No authentication headers are required.

Future versions may introduce authentication.

---

# API Endpoints

## Health Check

### Endpoint

```http
GET /api/v1/health
```

### Purpose

Verify backend availability.

### Response

```json
{
  "status": "healthy",
  "service": "rabbit-hole-api"
}
```

### Status Codes

| Code | Meaning |
| ---- | ------- |
| 200  | Success |

---

# Generate Graph

## Endpoint

```http
POST /api/v1/generate-graph
```

## Purpose

Generate a topic overview and knowledge graph.

---

## Request

```json
{
  "topic": "Transformers"
}
```

---

## Request Schema

```json
{
  "topic": "string"
}
```

Required:

* topic

---

## Response

```json
{
  "overview": {
    "topic": "Transformers",
    "domain": "Artificial Intelligence",
    "difficulty": "Advanced",
    "estimated_learning_time": "3-6 months",
    "popularity": "Very High",
    "importance_level": "High",
    "applications": [
      "ChatGPT",
      "Claude",
      "Gemini"
    ],
    "summary": "Transformer-based architectures dominate modern AI systems."
  },

  "graph": {
    "nodes": [],
    "edges": []
  },

  "node_details": {}
}
```

---

# Overview Object

```json
{
  "topic": "",
  "domain": "",
  "difficulty": "",
  "estimated_learning_time": "",
  "popularity": "",
  "importance_level": "",
  "applications": [],
  "summary": ""
}
```

---

# Node Object

Every node must contain:

```json
{
  "id": "",
  "name": "",
  "type": "",
  "description": "",
  "difficulty": "",
  "importance_score": 0,
  "estimated_learning_time": "",
  "prerequisites": [],
  "unlocks": [],
  "applications": [],
  "why_it_matters": "",
  "resources": {},
  "depth": 0
}
```

---

# Edge Object

```json
{
  "id": "",
  "source": "",
  "target": "",
  "relationship": ""
}
```

Relationship types:

* prerequisite
* related_concept
* advanced_concept
* application
* framework
* tool
* mathematical_foundation

---

# Node Details Object

```json
{
  "attention": {
    "id": "attention",
    "name": "Attention",
    "description": "",
    "difficulty": "Intermediate",
    "importance_score": 9,
    "estimated_learning_time": "2-4 days",
    "prerequisites": [],
    "unlocks": [],
    "applications": [],
    "why_it_matters": "",
    "resources": {}
  }
}
```

The node_details object is keyed by node ID.

This allows instant side-panel rendering without additional API requests.

---

# Expand Node

## Endpoint

```http
POST /api/v1/expand-node
```

## Purpose

Expand a node and discover deeper concepts.

The entire graph must not be regenerated.

Only new nodes and edges should be returned.

---

## Request

```json
{
  "node_id": "gpt",
  "current_depth": 2
}
```

---

## Response

```json
{
  "new_nodes": [],
  "new_edges": [],
  "new_node_details": {}
}
```

---

# Expanded Node Response

## new_nodes

Newly discovered nodes.

```json
[
  {
    "id": "gpt4",
    "name": "GPT-4"
  }
]
```

---

## new_edges

Relationships between newly discovered concepts.

```json
[
  {
    "source": "gpt",
    "target": "gpt4",
    "relationship": "advanced_concept"
  }
]
```

---

## new_node_details

Metadata for newly generated nodes.

```json
{
  "gpt4": {}
}
```

---

# Knowledge Gap Detection

## Endpoint

```http
POST /api/v1/knowledge-gap
```

## Purpose

Identify missing concepts between current knowledge and target topic.

Generate a personalized learning path.

---

## Request

```json
{
  "known_concepts": [
    "Python",
    "NumPy",
    "Pandas"
  ],
  "target_topic": "Transformers"
}
```

---

## Response

```json
{
  "known": [
    "Python"
  ],

  "missing": [
    "Linear Algebra",
    "Probability",
    "Neural Networks",
    "Attention"
  ],

  "learning_path": [
    "Linear Algebra",
    "Probability",
    "Neural Networks",
    "Attention",
    "Transformers"
  ]
}
```

---

# Knowledge Gap Response Schema

```json
{
  "known": [],
  "missing": [],
  "learning_path": []
}
```

---

# Error Response

All endpoints must use a consistent error format.

Example:

```json
{
  "error": true,
  "message": "Invalid topic",
  "code": "INVALID_TOPIC"
}
```

---

# Validation Rules

The backend must validate:

* Missing topic names
* Empty requests
* Invalid JSON
* Missing node IDs
* Invalid knowledge gap requests

Invalid requests must never reach AI processing.

---

# AI Response Validation

All AI-generated responses must pass Pydantic validation.

Invalid responses must be rejected.

Malformed JSON must never be forwarded to the frontend.

---

# Performance Guidelines

MVP Requirements:

* Generate graph under 10 seconds
* Expand node under 5 seconds
* Knowledge gap analysis under 5 seconds

These are goals, not hard guarantees.

---

# API Design Principles

The API should:

* Be stateless
* Use JSON exclusively
* Return structured data
* Validate all inputs
* Validate all AI outputs

The frontend should never need to parse AI-generated text.

The backend must convert all AI output into structured schema-compliant JSON before returning responses.
