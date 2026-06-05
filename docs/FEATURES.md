# RabbitHole - Features

## Overview

RabbitHole is an AI-powered knowledge exploration platform that transforms any topic into an interactive knowledge universe.

The platform helps users understand:

* What a topic is
* How concepts are connected
* What prerequisites are required
* What concepts are unlocked
* What knowledge gaps exist
* What to learn next

RabbitHole is designed around exploration rather than linear learning.

---

# MVP Features

The following features are required for Version 1.

---

## AI-Powered Topic Analysis

RabbitHole uses AI to:

- Identify concepts
- Discover relationships
- Estimate difficulty
- Estimate learning time
- Generate dependencies
- Build learning paths

AI is responsible for knowledge generation.

AI is not responsible for visualization.


## Topic Overview Dashboard

Provides:

- Difficulty
- Popularity
- Domain
- Importance Level
- Estimated Learning Time
- Applications

This acts as the entry point into the knowledge universe before graph exploration begins.

## Topic Search

Users can enter any topic and generate a knowledge universe.

Examples:

* Transformers
* Machine Learning
* Ancient Indian History
* Databases
* Probability
* Operating Systems

RabbitHole should support multiple domains.

---

## Topic Overview

Every topic generates an overview containing:

* Topic Name
* Domain
* Difficulty
* Popularity
* Estimated Learning Time
* Applications
* Summary
* Importance Level

Example:

```text
Topic:
Transformers

Domain:
Artificial Intelligence

Difficulty:
Advanced

Estimated Time:
3–6 Months

Applications:
ChatGPT
Claude
Gemini
```

Purpose:

Provide immediate context before exploration begins.

---

## Interactive Knowledge Graph

RabbitHole generates a visual knowledge graph.

The graph represents:

* Concepts
* Dependencies
* Relationships
* Learning connections

The graph is not a roadmap.

The graph is a knowledge universe.

---

## React Flow Visualization

Users can:

* Zoom
* Pan
* Drag Nodes
* Click Nodes
* Explore Relationships

The graph should remain interactive at all times.

---

## Rich Node Metadata

Every node contains:

* Name
* Description
* Difficulty
* Importance Score
* Estimated Learning Time
* Prerequisites
* Unlocks
* Applications
* Why It Matters
* Resources

Nodes are knowledge objects, not labels.

---

## Node Details Panel

Clicking a node opens a side panel.

The panel explains:

* What the concept is
* Why it matters
* What it unlocks
* What must be learned first

This is one of the core learning experiences of RabbitHole.

---

## Dynamic Node Expansion

Users can expand any node.

Example:

GPT

Expands into:

* GPT-2
* GPT-3
* GPT-4
* Agents
* Tool Use
* RAG

The graph grows dynamically.

Only new concepts should be added.

The entire graph should not be regenerated.

---

## Knowledge Gap Detection

Users can specify:

Known Concepts

Example:

* Python
* NumPy
* Pandas

Target Topic

Example:

Transformers

RabbitHole identifies:

* Known Concepts
* Missing Concepts
* Critical Prerequisites
* Recommended Learning Path

Example:

```text
Known

✓ Python

Missing

✗ Linear Algebra
✗ Probability
✗ Neural Networks
✗ Attention
```

Purpose:

Transform RabbitHole from a graph explorer into a personalized learning navigator.

---

## Personalized Learning Path

Based on knowledge gap analysis.

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

Users can see the shortest meaningful path to their target topic.

---

## Multi-Domain Support

RabbitHole should support:

Technology

* Machine Learning
* Databases
* Networking

Science

* Physics
* Chemistry
* Biology

Mathematics

* Algebra
* Calculus
* Probability

History

* Ancient India
* Roman Empire
* World War II

General Knowledge

* Philosophy
* Psychology
* Literature

The platform must remain domain-agnostic.

---

# Planned Features

These features are intended for future versions.

---

## Resource Recommendations

For every node:

* YouTube Videos
* Articles
* Documentation
* Books

Users can directly continue learning.

---

## Learning Time Estimation

Estimate:

* Time per concept
* Time per learning path
* Total journey duration

Example:

```text
Linear Algebra: 3 Weeks

Probability: 2 Weeks

Neural Networks: 2 Weeks

Attention: 4 Days
```

---

## Progress Tracking

Allow users to:

* Mark concepts complete
* Track learning progress
* Visualize completed paths

---

## Saved Knowledge Maps

Users can:

* Save generated graphs
* Return later
* Continue exploration

---

## Graph Export

Export graphs as:

* PNG
* PDF
* JSON

---

## Learning Journey History

Track:

* Topics explored
* Concepts expanded
* Learning paths generated

---

# Long-Term Vision

These features are outside the immediate roadmap but align with the future vision.

---

## User Profiles

Personalized exploration experiences.

---

## Community Knowledge Maps

Users can share:

* Knowledge universes
* Learning paths
* Exploration journeys

---

## Collaborative Exploration

Multiple users explore and build knowledge maps together.

---

## Recommendation Engine

Suggest:

* Related topics
* Next concepts
* Learning opportunities

Based on exploration behavior.

---

# Out of Scope

The following features are intentionally excluded from RabbitHole.

---

## Chatbot Interface

RabbitHole is not a chatbot.

Exploration should happen through graph interaction.

---

## Social Media Features

No:

* Posts
* Feeds
* Likes
* Followers

---

## Payments

No subscriptions or payment systems in MVP.

---

## Authentication

Authentication is not required for MVP.

---

## Gamification

No:

* XP
* Badges
* Streaks
* Leaderboards

---

## Generic Roadmap Generation

RabbitHole is not a roadmap generator.

Roadmaps are only a small component of the larger knowledge universe.

---

# Feature Prioritization

Priority 1

* Topic Search
* Topic Overview
* Knowledge Graph

Priority 2

* Node Details Panel
* Dynamic Node Expansion

Priority 3

* Knowledge Gap Detection
* Personalized Learning Path

Priority 4

* Resource Recommendations
* Progress Tracking

Priority 5

* Saved Graphs
* Export Features

---

# Success Metrics

RabbitHole succeeds when users can:

* Understand a topic quickly
* Discover missing knowledge
* Follow curiosity naturally
* Explore concept relationships visually
* Build personalized learning paths

The platform should make learning feel like exploring a connected universe of ideas rather than following a static checklist.
