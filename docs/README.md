# RabbitHole

> Explore knowledge. Discover dependencies. Follow curiosity.

RabbitHole is an AI-powered knowledge exploration platform that transforms any topic into an interactive knowledge universe.

Instead of providing static roadmaps or chatbot responses, RabbitHole visualizes how concepts connect, what prerequisites are required, what concepts become unlocked, and how knowledge expands through exploration.

The goal is to make learning feel like navigating a map rather than following a checklist.

---

## Why RabbitHole?

Most learning platforms answer:

> What should I learn next?

RabbitHole answers:

* Why should I learn this?
* What concepts depend on it?
* What am I missing?
* What does this unlock?
* How is everything connected?

Rather than presenting knowledge as a linear path, RabbitHole presents knowledge as an explorable universe.

---

## Example

### User Input

```text
Transformers
```

### RabbitHole Generates

#### Topic Overview

```text
Topic: Transformers

Domain:
Artificial Intelligence

Difficulty:
Advanced

Estimated Learning Time:
3-6 Months

Applications:
ChatGPT
Claude
Gemini
GitHub Copilot
```

#### Knowledge Graph

```text
Python
   ↓
Linear Algebra
   ↓
Probability
   ↓
Neural Networks
   ↓
Attention
   ↓
Transformers
```

#### Node Exploration

Click:

```text
Attention
```

View:

```text
Description
Difficulty
Importance Score
Prerequisites
Unlocks
Applications
Why It Matters
Estimated Learning Time
Resources
```

#### Knowledge Gap Detection

Input:

```text
Known:
Python
NumPy
Pandas

Goal:
Transformers
```

Output:

```text
Missing:
Linear Algebra
Probability
Neural Networks
Attention

Recommended Path:

Linear Algebra
↓
Probability
↓
Neural Networks
↓
Attention
↓
Transformers
```

---

## Core Features

### Topic Overview

Generate:

* Topic Name
* Domain
* Difficulty
* Popularity
* Importance Level
* Estimated Learning Time
* Applications
* Summary

---

### Interactive Knowledge Graph

Visualize:

* Concepts
* Dependencies
* Relationships
* Learning Connections

Built using React Flow.

---

### Rich Node Metadata

Every node includes:

* Description
* Difficulty
* Importance Score
* Estimated Learning Time
* Prerequisites
* Unlocks
* Applications
* Why It Matters
* Learning Resources

---

### Dynamic Node Expansion

Expand any concept to discover deeper knowledge.

Example:

```text
GPT
│
├── GPT-2
├── GPT-3
├── GPT-4
│
├── Agents
├── Tool Use
└── RAG
```

---

### Knowledge Gap Detection

Identify:

* Known Concepts
* Missing Concepts
* Critical Prerequisites
* Personalized Learning Paths

---

## Tech Stack

### Frontend

* React
* TailwindCSS
* React Flow
* Axios

### Backend

* FastAPI
* Pydantic
* Uvicorn

### AI

* Groq
* Llama 3.3 70B Versatile

### Data Format

* JSON

---

## Architecture

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

For detailed architecture:

See:

```text
docs/ARCHITECTURE.md
```

---

## Project Structure

```text
rabbit-hole/

├── frontend/
│
├── backend/
│
├── docs/
│   ├── README.md
│   ├── INSTALLATION.md
│   ├── USAGE.md
│   ├── ARCHITECTURE.md
│   ├── FEATURES.md
│   ├── ROADMAP.md
│   ├── PROJECT_SPEC.md
│   ├── API_SPEC.md
│   ├── UI_SPEC.md
│   └── AGENTS.md
│
└── LICENSE
```

---

## MVP Scope

Version 1 includes:

* Topic Search
* Topic Overview
* Interactive Knowledge Graph
* Node Details Panel
* Dynamic Node Expansion
* Knowledge Gap Detection
* Personalized Learning Paths

---

## Future Roadmap

Planned features include:

* Resource Recommendations
* Progress Tracking
* Saved Knowledge Maps
* Graph Export
* Personalized Recommendations
* Community Knowledge Universes

See:

```text
docs/ROADMAP.md
```

for full details.

---

## Installation

See:

```text
docs/INSTALLATION.md
```

---

## Usage

See:

```text
docs/USAGE.md
```

---

## Contributing

Contributions, ideas, and improvements are welcome.

Please review:

```text
docs/AGENTS.md
```

before contributing.

---

## License

This project is licensed under the MIT License.

---

## Vision

RabbitHole aims to become a universal knowledge exploration platform.

Instead of asking:

> What should I learn next?

Users should be able to see:

* Where they are
* What they know
* What they are missing
* How concepts connect
* What opportunities lie beyond

Learning should feel like exploring a universe of ideas.

---

Built with curiosity, graphs, and AI.
