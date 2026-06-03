# RabbitHole - Project Specification

## Project Overview

RabbitHole is an AI-powered knowledge exploration platform that transforms any topic into an interactive learning universe.

Unlike traditional roadmap generators or chatbots, RabbitHole focuses on helping users understand how concepts are connected, what prerequisites are required, what advanced topics become accessible, and how knowledge expands through exploration.

The primary objective is to enable users to learn by following curiosity.

Users can explore topics visually through an interactive knowledge graph, inspect detailed concept information, identify learning gaps, and continuously expand concepts to discover deeper knowledge structures.

---

# Problem Statement

Current learning platforms typically provide:

* Static roadmaps
* Linear learning paths
* Search-based exploration
* Text-heavy explanations

These approaches often fail to answer:

* Why should I learn this?
* What does this concept unlock?
* How are concepts related?
* What am I missing before learning this?
* What can I explore next?

RabbitHole solves this problem by visualizing knowledge as an explorable network rather than a linear sequence.

---

# Vision

RabbitHole should function as a knowledge operating system.

Users should be able to:

* Explore any domain
* Discover prerequisites
* Understand dependencies
* Expand concepts dynamically
* Identify learning gaps
* Follow curiosity-driven learning paths

The graph is not the product.

The exploration experience is the product.

---

# Core Concept

User enters a topic.

Example:

Transformers

RabbitHole generates:

1. Topic Overview
2. Knowledge Graph
3. Concept Details
4. Learning Dependencies
5. Expandable Knowledge Network

The graph continuously grows as users explore concepts.

---

# Target Users

## Primary Users

* Students
* Self Learners
* Software Developers
* Researchers
* Educators

## Secondary Users

* Technical Interview Candidates
* Data Scientists
* AI Engineers
* Academic Learners

---

# Supported Domains

RabbitHole must not be limited to technology topics.

Examples:

Technology

* Machine Learning
* Operating Systems
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
* World War II
* Roman Empire

Finance

* Stock Market
* Investing
* Economics

General Knowledge

* Philosophy
* Psychology
* Literature

The system should be domain-agnostic.

---

# User Journey

## Step 1

User enters a topic.

Example:

Transformers

## Step 2

RabbitHole generates a topic overview.

Example:

Topic: Transformers

Domain:
Artificial Intelligence

Difficulty:
Advanced

Estimated Learning Time:
3-6 Months

Popularity:
Very High

Applications:

* ChatGPT
* Claude
* Gemini
* GitHub Copilot

## Step 3

RabbitHole generates a visual knowledge graph.

Example:

Python
↓
Linear Algebra
↓
Neural Networks
↓
Attention
↓
Transformers

## Step 4

User clicks a node.

Example:

Attention

## Step 5

RabbitHole displays detailed concept information.

## Step 6

User expands the node.

The graph grows dynamically.

## Step 7

User continues exploration.

This creates the Rabbit Hole effect.

---

# Topic Overview Requirements

Every generated topic must include:

* Topic Name
* Domain
* Difficulty
* Estimated Learning Time
* Popularity
* Applications
* Summary
* Importance Level

Example:

{
"topic": "",
"domain": "",
"difficulty": "",
"estimated_learning_time": "",
"popularity": "",
"applications": [],
"summary": "",
 "importance_level": ""
}

---

# Knowledge Graph Requirements

The graph represents relationships between concepts.

The graph is not a roadmap.

The graph is a knowledge universe.

Each graph contains:

* Nodes
* Edges
* Dependencies
* Relationships

Supported relationship types:

* prerequisite
* core_concept
* advanced_concept
* application
* related_concept
* mathematical_foundation
* tool
* framework

---

# Node Requirements

Every node must contain rich metadata.

Required fields:

* id
* name
* type
* description
* difficulty
* importance_score
* estimated_learning_time
* prerequisites
* unlocks
* applications
* why_it_matters
* resources
* depth
Example:

{
"id": "",
"depth": 0,
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
"resources": {}
}

---

# Node Details Panel

When a user clicks a node, a side panel must open.

The panel must display:

* Concept Name
* Description
* Difficulty
* Importance Score
* Estimated Learning Time
* Prerequisites
* Unlocks
* Applications
* Why It Matters
* Learning Resources

The panel should clearly answer:

- What is this?
- Why should I learn this?
- What does this unlock?
- What must I know before learning it?

The side panel is a first-class feature.

The graph shows relationships.

The side panel explains meaning.

---

# Learning Gap Detection

Users should be able to specify known concepts.

Example:

Known:

* Python
* NumPy
* Pandas

Target:
Transformers

RabbitHole should identify:

* Known Concepts
* Missing Concepts
* Recommended Learning Path

---

# Knowledge Gap Detection

Knowledge Gap Detection is a core MVP feature.

Users may provide:

- Known Concepts
- Target Topic

RabbitHole should compare the user's knowledge against the generated knowledge graph.

The system should identify:

- Concepts already known
- Missing prerequisites
- Critical learning gaps
- Recommended learning sequence

The output should clearly distinguish:

Known:
✓ Concept

Missing:
✗ Concept

The system should generate the shortest meaningful path from the user's current knowledge state to the target topic.

Example:

Known:
Python
NumPy
Pandas

Target:
Transformers

Output:

Missing:
Linear Algebra
Probability
Neural Networks
Attention

Learning Path:
Linear Algebra → Probability → Neural Networks → Attention → Transformers

# Knowledge Expansion

Knowledge Expansion is a core MVP feature.

Users should be able to expand any node and discover deeper concepts, applications, dependencies, and related topics without regenerating the entire graph.
Users can expand any node.

Example:

GPT

Expansion may generate:

* GPT-2
* GPT-3
* GPT-4
* Agents
* RAG
* Tool Use

The graph must update dynamically.

This feature is the heart of RabbitHole.

---

# AI Responsibilities

The AI system is responsible for:

* Topic analysis
* Concept discovery
* Relationship generation
* Difficulty estimation
* Learning time estimation
* Importance scoring
* Learning path generation
* Node expansion

The AI is not responsible for graph rendering.

---

# Success Criteria

The project succeeds when users can:

* Understand a topic quickly
* Discover prerequisite concepts
* Follow curiosity naturally
* Explore knowledge visually
* Learn through relationships
* Expand concepts indefinitely

RabbitHole should make learning feel like exploring a map rather than following a checklist.

---

# MVP Scope

Version 1 includes:

- Topic Search
- Topic Overview
- Knowledge Graph
- Node Details Panel
- Dynamic Node Expansion
- Knowledge Gap Detection

The MVP should allow users to specify concepts they already know and a target topic they want to learn.

RabbitHole should analyze the generated knowledge graph and identify:

- Known Concepts
- Missing Concepts
- Critical Prerequisites
- Recommended Learning Path

Example:

Known:
- Python
- NumPy
- Pandas

Goal:
Transformers

Output:

Known:
✓ Python

Missing:
✗ Linear Algebra
✗ Probability
✗ Neural Networks
✗ Attention

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

This feature transforms RabbitHole from a graph visualization tool into a personalized learning navigator.

---



# Future Vision

Future versions may include:

* Personalized Learning Paths
* Resource Recommendations
* Progress Tracking
* Saved Graphs
* User Profiles
* Graph Export
* Community Knowledge Maps

These features are not required for MVP.
