# RabbitHole - System Architecture

## Overview

RabbitHole is an AI-powered knowledge exploration platform that transforms any topic into an interactive knowledge universe.

The system consists of:

* React Frontend
* FastAPI Backend
* Groq AI Layer
* React Flow Visualization Layer

The frontend is responsible for user interaction and visualization.

The backend is responsible for knowledge generation, validation, graph construction, and learning analysis.

The AI is responsible for generating structured knowledge.

---

# High-Level Architecture

```text
User
 │
 ▼
React Frontend
 │
 ▼
FastAPI Backend
 │
 ▼
Groq API
 │
 ▼
Structured JSON
 │
 ▼
React Flow Visualization
```

---

# Core Architecture Principle

The frontend never communicates directly with Groq.

All AI communication must pass through FastAPI.

```text
Frontend
    │
    ▼
FastAPI
    │
    ▼
Groq
```

This ensures:

* Validation
* Security
* Consistent schemas
* Better maintainability

---

# Frontend Architecture

Technology:

* React
* TailwindCSS
* React Flow
* Axios

Frontend responsibilities:

* Topic input
* Overview display
* Graph rendering
* Node interaction
* Side panel rendering
* Knowledge gap UI

The frontend should contain no AI logic.

---

# Frontend Folder Structure

```text
frontend/

src/

├── components/
│
├── pages/
│
├── services/
│
├── hooks/
│
├── utils/
│
├── assets/
│
└── App.jsx
```

---

# Components

## SearchBar

Purpose:

Accept user topic input.

Example:

Transformers

---

## TopicOverview

Displays:

* Difficulty
* Domain
* Applications
* Popularity
* Learning Time

---

## GraphView

Primary React Flow container.

Responsibilities:

* Render nodes
* Render edges
* Handle zoom
* Handle pan
* Handle node clicks

---

## NodePanel

Displays node details.

Displays:

* Description
* Difficulty
* Importance
* Prerequisites
* Unlocks
* Resources

---

## KnowledgeGapPanel

Displays:

* Known concepts
* Missing concepts
* Learning path

---

# Backend Architecture

Technology:

* FastAPI
* Pydantic
* Uvicorn

Backend responsibilities:

* Prompt generation
* AI communication
* Response validation
* Graph generation
* Learning path generation
* Knowledge gap analysis

---

# Backend Folder Structure

```text
backend/

backend/

app/

├── main.py

├── routes/
│   ├── graph.py
│   ├── expansion.py
│   └── knowledge_gap.py

├── services/
│   ├── groq_service.py
│   ├── graph_service.py
│   ├── expansion_service.py
│   └── knowledge_gap_service.py

├── models/
│   └── schemas.py

├── prompts/
│   ├── graph_prompt.txt
│   ├── expand_prompt.txt
│   └── knowledge_gap_prompt.txt

├── utils/

└── core/

---

# Routes Layer

Routes handle HTTP requests.

Example:

```text
POST /generate-graph

POST /expand-node

POST /knowledge-gap

GET /health
```

Routes should remain lightweight.

Business logic belongs in services.

---

# Services Layer

Services contain core application logic.

---

## Graph Service

Responsible for:

* Graph creation
* Node generation
* Edge generation

---

## Groq Service

Responsible for:

* API communication
* Prompt submission
* Response retrieval

---

## Knowledge Gap Service

Responsible for:

* Gap detection
* Path generation
* Missing prerequisite discovery

---

## Expansion Service

Responsible for:

* Node expansion
* Graph growth

---

# Models Layer

All data structures must be defined using Pydantic.

Examples:

* TopicOverview
* Node
* Edge
* GraphResponse
* KnowledgeGapResponse

No unvalidated data should reach the frontend.

---

# AI Architecture

The AI layer generates knowledge.

The AI does not render graphs.

The AI does not control UI behavior.

The AI only returns structured JSON.

---

# AI Workflow

```text
User Topic
      │
      ▼

Prompt Builder
      │
      ▼

Groq API
      │
      ▼

Raw JSON
      │
      ▼

Pydantic Validation
      │
      ▼

Graph Response
```

---

# Graph Generation Flow

The generated graph should include both graph structure and node metadata in a single response whenever possible.

Step 1

User enters:

Transformers

Step 2

Frontend sends:

```json
{
  "topic": "Transformers"
}
```

Step 3

Backend creates prompt.

Step 4

Groq generates:

* Topic Overview
* Nodes
* Edges
* Node Metadata

Step 5

Backend validates response.

Step 6

Frontend receives validated graph.

Step 7

React Flow renders graph.

---

# Node Expansion Flow

Step 1

User clicks:

GPT

Step 2

Frontend sends:

```json
{
  "node": "GPT"
}
```

Step 3

Backend generates expansion prompt.

Step 4

Groq returns:

* Related Concepts
* Subtopics
* Dependencies
* Applications

Step 5

Backend validates.

Step 6

Frontend appends new nodes and edges.

The entire graph must not be regenerated.

Only newly discovered concepts should be added.

---

# Knowledge Gap Detection Flow

The backend should reuse the generated knowledge graph whenever possible rather than generating a completely new graph for gap analysis.

Step 1

User provides:

Known:

* Python
* NumPy
* Pandas

Target:

Transformers

Step 2

Frontend sends request.

Step 3

Backend analyzes graph.

Step 4

Backend identifies:

* Known concepts
* Missing concepts
* Critical prerequisites

Step 5

Backend generates learning path.

Step 6

Frontend displays personalized path.

---

# Node Data Structure

Every node should contain:

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

# State Management

Initial implementation should use:

* React State
* React Context

Do not introduce Redux initially.

Use Redux only if complexity demands it later.

---

# Error Handling

Backend must handle:

* Invalid topics
* Empty responses
* Malformed JSON
* API failures
* Timeout errors

Frontend must display:

* Loading states
* Error states
* Retry options

---

# Security

API keys must never be exposed to the frontend.

Store all secrets in:

```text
.env
```

The frontend should never contain:

* API keys
* Secret tokens
* Direct Groq access

---

# Scalability Considerations

After MVP:

* Response caching
* Graph persistence
* Saved learning journeys
* User profiles
* Resource recommendation engine

These are future concerns.

Do not implement before MVP completion.

---

# Architectural Success Criteria

The architecture is successful when:

1. Any topic can generate a knowledge universe.
2. Nodes can be expanded indefinitely.
3. Knowledge gaps can be identified.
4. All AI responses are validated.
5. The graph remains interactive and responsive.
6. Frontend and backend remain loosely coupled.

The architecture should prioritize maintainability, scalability, and exploration-driven learning.
