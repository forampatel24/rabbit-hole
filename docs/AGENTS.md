# RabbitHole - Agent Instructions

## Purpose

You are building RabbitHole.

RabbitHole is an AI-powered knowledge exploration platform.

RabbitHole is NOT:

* A chatbot
* A roadmap generator
* A mind map tool
* A graph visualization demo
* A note-taking application

RabbitHole IS:

* A knowledge exploration system
* A learning navigator
* A knowledge dependency mapper
* An AI-powered concept discovery platform

The primary goal is to help users understand how concepts connect, what prerequisites are required, what concepts are unlocked, and how knowledge expands through exploration.

Every architectural and UI decision should prioritize exploration, discoverability, and learning.

---

# Project Vision

Users should be able to:

* Enter any topic
* Instantly understand the topic
* Explore concept relationships visually
* Discover prerequisite concepts
* Understand why concepts matter
* Identify learning gaps
* Expand concepts indefinitely
* Follow curiosity naturally

The graph is not the product.

The exploration experience is the product.

---

# Technology Stack

Frontend:

* React
* TailwindCSS
* React Flow
* Axios

Backend:

* FastAPI
* Pydantic
* Uvicorn

AI:

* Groq API

Data Format:

* JSON

Version Control:

* Git
* GitHub

Visualization:

* React Flow

Do not introduce alternative frameworks unless explicitly requested.

---

# AI Provider Configuration

Primary Provider:

* Groq

Default Model:

* llama-3.3-70b-versatile

Fallback Model:

* deepseek-r1-distill-llama-70b

Environment Variable:

* GROQ_API_KEY

Requirements:

* All AI communication must be encapsulated inside `groq_service.py`
* The frontend must never communicate directly with Groq
* API keys must only be loaded from environment variables
* No hardcoded API keys
* All model responses must be validated using Pydantic schemas before reaching the frontend
* The system should be designed so that models can be swapped later without changing frontend code

---

# Architecture Rules

Frontend and backend must remain completely separated.

Frontend responsibilities:

* Search
* Graph visualization
* Node interaction
* Side panel rendering
* User input

Backend responsibilities:

* Prompt construction
* LLM communication
* JSON validation
* Graph generation
* Learning path generation

AI responsibilities:

* Topic analysis
* Knowledge extraction
* Relationship discovery
* Difficulty estimation
* Learning path generation
* Node expansion

AI must never be responsible for UI rendering.

---

# Development Philosophy

Build vertically.

Finish one complete feature before starting another.

Avoid placeholder implementations that do not contribute to the MVP.

Prioritize functionality over optimization.

Prioritize clarity over cleverness.

Avoid unnecessary abstractions.

Prefer maintainable code.

---

# MVP Features

The MVP consists of only the following features:

## 1. Topic Search

User enters a topic.

Example:

Transformers

RabbitHole generates a knowledge universe.

---

## 2. Topic Overview

Every topic must generate:

* Topic Name
* Domain
* Difficulty
* Estimated Learning Time
* Popularity
* Applications
* Summary
* Importance Level

---

## 3. Knowledge Graph

Generate:

* Nodes
* Edges
* Dependencies
* Relationships

Visualize using React Flow.

The graph represents knowledge relationships.

The graph is not a roadmap.

---

## 4. Node Details Panel

Clicking a node opens a side panel.

The side panel must include:

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

The panel must answer:

* What is this?
* Why should I learn this?
* What does this unlock?
* What must I know first?

The side panel is a first-class feature.

The graph shows relationships.

The side panel explains meaning.

---

## 5. Dynamic Node Expansion

Users can expand any node.

Example:

GPT

Expansion may generate:

* GPT-2
* GPT-3
* GPT-4
* Agents
* Tool Use
* RAG

Graph updates dynamically.

Do not regenerate the entire graph when expanding a node.

Only append newly discovered concepts.

---

## 6. Knowledge Gap Detection

Users can specify:

Known Concepts

Example:

* Python
* NumPy
* Pandas

Target Topic

Example:

Transformers

RabbitHole must identify:

* Known Concepts
* Missing Concepts
* Critical Prerequisites
* Recommended Learning Path

Example Output:

Known:

✓ Python

Missing:

✗ Linear Algebra

✗ Probability

✗ Neural Networks

✗ Attention

Learning Path:

Linear Algebra
→ Probability
→ Neural Networks
→ Attention
→ Transformers

This feature is a core MVP requirement.

---

# Graph Design Rules

Nodes must contain metadata.

A node is not merely a label.

Every node must be uniquely identifiable.

Node IDs should remain stable across graph expansions whenever possible.

Every node must include:

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

Nodes should support future expansion.

---

# Node Types

Supported node types:

* prerequisite
* core_concept
* advanced_concept
* application
* framework
* tool
* mathematical_foundation
* related_concept

Additional types may be added later.

---

# AI Response Rules

Never trust raw LLM responses.

All AI output must pass through validation.

Use Pydantic models.

Reject malformed responses.

Reject incomplete responses.

Never send raw AI output directly to the frontend.

AI-generated knowledge should be deterministic in structure even if content varies.

The schema is more important than the wording.
---

# JSON Rules

AI prompts must request:

Valid JSON only.

No markdown.

No explanations.

No surrounding text.

Every response must be schema validated.

---

# Prompt Engineering Rules

Prompts should:

* Request structured output
* Specify required fields
* Specify node relationships
* Specify dependency direction

Prompts should never request prose-heavy output.

Prompts should prioritize structured knowledge.

---

# UI Principles

The UI should feel like:

* A knowledge explorer
* A map
* A discovery tool

The UI should not feel like:

* A chatbot
* A dashboard full of forms
* A documentation website

Keep the interface minimal.

The graph should be the central visual element.

---

# Performance Rules

Do not optimize prematurely.

Prioritize correctness first.

After MVP completion:

* Optimize prompts
* Reduce token usage
* Cache AI responses
* Improve graph rendering

Optimization is not part of initial development.

---

# Things To Avoid

Do not add:

* Authentication
* User accounts
* Payments
* Social features
* Community feeds
* Chat functionality
* Notifications
* Gamification

These are outside MVP scope.

---

# Success Criteria

The project succeeds when a user can:

1. Enter any topic.
2. Understand the topic quickly.
3. Explore concept relationships visually.
4. Discover missing knowledge.
5. Follow a personalized learning path.
6. Expand concepts indefinitely.

The project fails if it becomes a generic chatbot, roadmap generator, or graph visualization demo.

Always prioritize exploration, learning, and curiosity-driven discovery.
