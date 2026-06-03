# RabbitHole - UI Specification

## UI Philosophy

RabbitHole is not a chatbot.

RabbitHole is not a dashboard.

RabbitHole is not a documentation website.

RabbitHole should feel like:

* A knowledge explorer
* A learning map
* A discovery engine
* An interactive knowledge universe

The user should feel like they are navigating a map of ideas.

The graph is the primary visual element.

---

# Design Principles

## Simplicity

The interface should remain clean.

Avoid unnecessary controls.

Avoid clutter.

Focus attention on:

* Search
* Graph
* Exploration

---

## Exploration First

Every design decision should encourage discovery.

The user should always have:

* Something to click
* Something to expand
* Something to learn

---

## Information Hierarchy

Priority order:

1. Knowledge Graph
2. Node Information
3. Topic Overview
4. Knowledge Gap Analysis

The graph should always dominate the screen.

---

# Theme

## Style

Modern SaaS

Dark Mode First

Minimalist

Professional

Educational

---

## Color Palette

Background:

```text
#0F172A
```

Primary Accent:

```text
#3B82F6
```

Secondary Accent:

```text
#8B5CF6
```

Success:

```text
#10B981
```

Warning:

```text
#F59E0B
```

Error:

```text
#EF4444
```

Text:

```text
#F8FAFC
```

Muted Text:

```text
#94A3B8
```

---

# Application Layout

```text
┌───────────────────────────────────────────┐
│                 Navbar                    │
├───────────────────────────────────────────┤
│                                           │
│             Topic Overview                │
│                                           │
├───────────────────────────────────────────┤
│                                           │
│                                           │
│                                           │
│             Knowledge Graph               │
│                                           │
│                                           │
│                                           │
├───────────────────────────────────────────┤
│          Knowledge Gap Panel              │
└───────────────────────────────────────────┘
```

---

# Pages

## Home Page

Purpose:

Topic input.

User enters:

```text
Transformers
```

Button:

```text
Generate Map
```

---

## Explorer Page

Main application page.

Contains:

* Topic Overview
* Graph
* Node Details Panel
* Knowledge Gap Panel

This is the primary user experience.

---

# Components

## Navbar

Displays:

* RabbitHole Logo
* Project Name

MVP does not require:

* Login
* Profile
* Settings

---

## Search Bar

Purpose:

Accept topic input.

Example:

```text
Transformers
```

Button:

```text
Generate Map
```

---

## Topic Overview Card

Displays:

* Topic
* Domain
* Difficulty
* Popularity
* Estimated Learning Time
* Applications
* Summary

Example:

```text
Topic:
Transformers

Difficulty:
Advanced

Estimated Time:
3-6 Months

Applications:
ChatGPT
Claude
Gemini
```

---

## Graph View

Technology:

React Flow

Purpose:

Visualize the knowledge universe.

Features:

* Zoom
* Pan
* Drag Nodes
* Click Nodes
* Expand Nodes

The graph should occupy most of the screen.

---

# Node Design

Every node should visually indicate:

* Concept Type
* Importance
* Difficulty

Example Types:

Prerequisite

Core Concept

Advanced Concept

Application

Framework

Tool

Each type should have a distinct visual style.

---

# Node Interaction

Single Click:

Open node details panel.

Double Click:

Expand node.

Alternative:

Expand button inside side panel.

---

# Node Details Panel

Position:

Right Side

Layout:

```text
----------------------------------

Attention

----------------------------------

What Is It?

A mechanism allowing a model
to focus on important parts
of input.

----------------------------------

Difficulty

Intermediate

----------------------------------

Importance

9/10

----------------------------------

Estimated Learning Time

2-4 Days

----------------------------------

Prerequisites

• Neural Networks

----------------------------------

Unlocks

• Self Attention
• Transformers

----------------------------------

Applications

• LLMs
• Machine Translation

----------------------------------

Why It Matters

Understanding Attention is
required for understanding
modern Transformer models.

----------------------------------

Resources

▶ YouTube

📄 Articles

📚 Documentation

----------------------------------
```

This panel is a first-class feature.

The graph shows relationships.

The panel explains meaning.

---

# Knowledge Gap Panel

Purpose:

Show users what they are missing.

Example:

```text
Goal:
Transformers

Known:

✓ Python

✓ NumPy

✓ Pandas

Missing:

✗ Linear Algebra

✗ Probability

✗ Neural Networks

✗ Attention
```

---

## Recommended Path

Display:

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

The path should be visually distinct.

---

# Loading States

During graph generation:

Display:

```text
Generating Knowledge Universe...
```

During expansion:

```text
Expanding Concept...
```

The user should always understand what is happening.

---

# Error States

Examples:

Invalid Topic

```text
Unable to generate knowledge graph.
Please try another topic.
```

API Failure

```text
Service temporarily unavailable.
Please try again.
```

---

# Empty State

Before search:

```text
Explore Any Topic

Enter a topic and generate an interactive knowledge universe.
```

---

# Responsive Design

Desktop:

Primary target.

Tablet:

Supported.

Mobile:

Basic support only.

Graph exploration is optimized for larger screens.

---

# Accessibility

The interface should support:

* Keyboard navigation
* High contrast readability
* Clear typography
* Consistent spacing

---

# Future UI Features

Not part of MVP:

* Saved Graphs
* User Profiles
* Themes
* Graph Export
* Collaborative Exploration
* Community Maps

These features should not be implemented during MVP.

---

# UI Success Criteria

The UI succeeds when:

1. Users immediately understand how to start.
2. The graph feels interactive.
3. Concept exploration feels natural.
4. The side panel provides meaningful context.
5. Knowledge gaps are clearly visible.
6. The interface encourages curiosity and exploration.

The UI should make users feel like they are navigating a universe of knowledge rather than reading a static roadmap.
