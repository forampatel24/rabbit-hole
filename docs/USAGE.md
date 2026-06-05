# RabbitHole - Usage Guide

## Overview

RabbitHole helps users explore knowledge through interactive concept graphs.

Users can:

* Generate knowledge universes
* Explore concept relationships
* Expand concepts
* Identify learning gaps
* Build personalized learning paths

---

# Generating a Knowledge Universe

Enter a topic.

Example:

```text
Transformers
```

Click:

```text
Generate Map
```

RabbitHole generates:

* Topic Overview
* Knowledge Graph
* Node Metadata

---

# Understanding Topic Overview

Example:

```text
Topic:
Transformers

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
```

The overview provides context before graph exploration begins.

---

# Exploring the Knowledge Graph

The graph visualizes:

* Concepts
* Dependencies
* Relationships

Users can:

* Zoom
* Pan
* Drag Nodes
* Click Nodes

Example:

```text
Python
   ↓
Linear Algebra
   ↓
Neural Networks
   ↓
Attention
   ↓
Transformers
```

---

# Viewing Node Details

Click any node.

Example:

```text
Attention
```

A side panel opens.

Displays:

* Description
* Difficulty
* Importance Score
* Estimated Learning Time
* Prerequisites
* Unlocks
* Applications
* Why It Matters
* Resources

Example:

```text
Attention

Difficulty:
Intermediate

Estimated Learning Time:
2-4 Days

Prerequisites:
Neural Networks

Unlocks:
Self Attention
Transformers
```

---

# Expanding Concepts

Expand any node to discover deeper knowledge.

Example:

Click:

```text
GPT
```

RabbitHole may generate:

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

The graph grows dynamically.

Only new concepts are added.

---

# Knowledge Gap Detection

Provide:

Known Concepts:

```text
Python
NumPy
Pandas
```

Target Topic:

```text
Transformers
```

RabbitHole analyzes the graph.

Output:

```text
Known

✓ Python

Missing

✗ Linear Algebra
✗ Probability
✗ Neural Networks
✗ Attention
```

---

# Personalized Learning Path

Based on identified gaps.

Example:

```text
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

This represents the recommended path toward the target topic.

---

# Example Topics

Technology

```text
Machine Learning
Operating Systems
Databases
Computer Networks
```

---

Mathematics

```text
Linear Algebra
Calculus
Probability
Statistics
```

---

Science

```text
Physics
Chemistry
Biology
```

---

History

```text
Ancient Indian History
Roman Empire
World War II
```

---

General Knowledge

```text
Psychology
Philosophy
Econom
```
