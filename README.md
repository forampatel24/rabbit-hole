<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/🐰_RabbitHole-Explore_Knowledge._Discover_Dependencies._Follow_Curiosity.-8B5CF6?style=for-the-badge&labelColor=0F172A">
    <img alt="RabbitHole" src="https://img.shields.io/badge/🐰_RabbitHole-Explore_Knowledge._Discover_Dependencies._Follow_Curiosity.-8B5CF6?style=for-the-badge&labelColor=0F172A">
  </picture>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white" alt="TailwindCSS">
  <img src="https://img.shields.io/badge/React_Flow-FF0072?style=flat&logo=react&logoColor=white" alt="React Flow">
  <img src="https://img.shields.io/badge/Groq-FF6F00?style=flat&logo=groq&logoColor=white" alt="Groq">
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=flat&logo=pydantic&logoColor=white" alt="Pydantic">
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
</p>

<p align="center">
  <b>AI-powered knowledge exploration platform</b> — <br>
  Transform any topic into an interactive, expandable knowledge universe.
</p>

<p align="center">
  <i>Instead of asking "What should I learn next?" — see where you are, what you're missing, and what lies beyond.</i>
</p>

---

## ✨ Features

### 🧠 Multi-Mode Knowledge Generation

Generate knowledge universes in **5 modes** — each with specialized AI prompts and node types:

| Mode | Purpose | Node Types |
|------|---------|------------|
| **Learn** | Deep topic exploration | Prerequisites, core concepts, advanced topics |
| **Interview** | Technical interview prep | Must-know, frequently asked, coding patterns |
| **Project** | Build planning | Goals, phases, steps, deliverables |
| **Research** | Academic literature | Foundations, seminal papers, SOTA, open problems |
| **Quick** | Fast overview (10–15 nodes) | Essential concepts only |

### 🕸️ Interactive Knowledge Graph

- Built with **React Flow** — zoom, pan, drag, click
- **Dagre** hierarchical layout with animated edges
- **50+ node types** with unique icons and color coding
- Difficulty badges, completion checkmarks, selection glow
- Minimap, controls, grid background

### 📋 Rich Node Details Panel

Every node includes:

| Field | Description |
|-------|-------------|
| Name | Concept title |
| Description | What it is |
| Difficulty | Beginner / Intermediate / Advanced |
| Importance Score | 1–10 rating |
| Estimated Learning Time | Per-concept duration |
| Prerequisites | What you need first |
| Unlocks | What becomes accessible |
| Applications | Real-world uses |
| Why It Matters | Motivation & context |
| Resources | YouTube, courses, papers, GitHub repos |

Modes add specialized fields (Interview Questions, Technology Alternatives, Execution Guides, etc.)

### 🔍 Knowledge Gap Detection

Input your known concepts + a target topic — RabbitHole identifies:

- ✅ **Known** concepts you already have
- ❌ **Missing** prerequisites
- 📍 **Personalized learning path** from where you are to your goal

### 🌱 Dynamic Node Expansion

Click "Expand" on any node to discover deeper concepts, subtopics, and related ideas — the graph grows without regenerating.

```
GPT
├── GPT-2
├── GPT-3
├── GPT-4
├── Agents
├── Tool Use
└── RAG
```

### 👤 User Accounts & Persistence

- **JWT authentication** — sign up, log in, manage profile
- **Save & load graphs** — persist your knowledge universes
- **Collections** — organize saved graphs into named folders
- **Move / Copy / Remove** graphs between collections
- **Search** your saved graphs by topic

### ✅ Progress Tracking

- Mark nodes as **completed**
- **Progress bar** per graph
- **Node checklist** — see all concepts and your status at a glance

### 📝 Per-Graph Notes

- Built-in **notes editor** with auto-save (debounced)
- Notes persist with your saved graph

### 📚 Learning Resources

Integrated resource fetching via external APIs:

| Source | API | Content |
|--------|-----|---------|
| YouTube | Data API v3 | Videos, thumbnails, duration |
| Courses | SerpAPI | Coursera, Udemy listings |
| Papers | OpenAlex | Citations, authors, DOI |
| GitHub | GitHub API | Repos, stars, language |

Results are **cached** (24-hour TTL) for performance.

### 🎨 Design

- **Dark mode first** — glass morphism UI
- Animated loading states with rotating status messages
- Custom React Flow node rendering
- Responsive (desktop primary, tablet supported)
- Keyboard navigation ready

---

## 🧱 Tech Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| **React 19** | UI framework |
| **TailwindCSS v4** | Styling |
| **React Flow** | Graph visualization |
| **React Router v7** | Routing |
| **React Icons** | Node type icons (Feather) |
| **Axios** | HTTP client |
| **Dagre** | Graph layout algorithm |
| **Vite** | Build tool |

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **Pydantic** | Request/response validation |
| **SQLAlchemy** | ORM + database abstraction |
| **Alembic** | Database migrations |
| **Uvicorn** | ASGI server |
| **python-jose** | JWT token handling |
| **passlib** | Password hashing |
| **httpx** | Async HTTP client |

### AI Layer

| Technology | Purpose |
|------------|---------|
| **Groq API** | LLM inference |
| **Llama 3.3 70B** | Default model |
| **DeepSeek R1 70B** | Fallback model |

### Data & Storage

| Technology | Purpose |
|------------|---------|
| **SQLite** | Default database |
| **PostgreSQL** | Production-ready alternative |
| **JSON** | Graph data format |
| **Resource Cache** | 24-hour API result caching |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User (Browser)                    │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│                  React Frontend                      │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ SearchBar │  │ GraphView │  │ NodePanel         │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Overview  │  │ GapPanel  │  │ Notes + Checklist │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │  HTTP / JSON
                  ▼
┌─────────────────────────────────────────────────────┐
│                  FastAPI Backend                      │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Routes    │  │ Services  │  │ Models (Pydantic)  │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Auth      │  │ Database   │  │ Prompts           │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┼──────────┐
        ▼                    ▼
┌──────────────┐   ┌──────────────────┐
│   Groq API   │   │ External APIs    │
│  (LLM)       │   │ YouTube │ Serp   │
└──────────────┘   │ OpenAlex│ GitHub │
                   └──────────────────┘
```

**Key rule:** The frontend **never** communicates directly with Groq. All AI calls pass through FastAPI for validation, security, and consistent schemas.

---

## 🗂️ Project Structure

```
rabbit-hole/
├── frontend/                # React SPA
│   └── src/
│       ├── components/      # UI components
│       ├── context/         # State management (AuthContext, GraphContext)
│       ├── pages/           # Route pages (Home, Login, SignUp, Profile)
│       └── services/        # API client
│
├── backend/                 # FastAPI server
│   └── app/
│       ├── routes/          # HTTP endpoints
│       │   ├── graph.py            # Graph generation
│       │   ├── expansion.py        # Node expansion
│       │   ├── knowledge_gap.py    # Gap analysis
│       │   ├── auth.py             # Authentication
│       │   ├── graph_storage.py    # CRUD for saved graphs
│       │   ├── resources.py        # External resource fetching
│       │   ├── collections.py      # Collection management
│       │   └── health.py           # Health check
│       ├── services/         # Business logic
│       │   ├── groq_service.py       # AI communication
│       │   ├── graph_service.py      # Graph construction
│       │   ├── expansion_service.py  # Node expansion logic
│       │   ├── knowledge_gap_service.py
│       │   └── resource_service.py   # External API integration
│       ├── models/           # Pydantic schemas + SQLAlchemy models
│       └── prompts/          # AI prompt templates (per mode)
│
├── docs/                    # Documentation
│   ├── INSTALLATION.md
│   ├── USAGE.md
│   ├── ARCHITECTURE.md
│   ├── API_SPEC.md
│   ├── UI_SPEC.md
│   ├── FEATURES.md
│   ├── ROADMAP.md
│   └── PROJECT_SPEC.md
│
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js 20+**
- **Python 3.12+**
- **Groq API key** (free at [console.groq.com](https://console.groq.com))

### 1. Clone & Install

```bash
git clone https://github.com/<your-username>/rabbit-hole.git
cd rabbit-hole
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev          # → http://localhost:5173
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
RABBITHOLE_MOCK=true   # Enable for development without API calls
```

### 3. Run

```bash
cd backend
uvicorn app.main:app --reload     # → http://localhost:8000
```

### 4. Verify

```bash
curl http://localhost:8000/api/v1/health
# → {"status": "healthy", "service": "rabbit-hole-api"}
```

---

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [Installation](docs/INSTALLATION.md) | Full setup with troubleshooting |
| [Usage](docs/USAGE.md) | How to explore knowledge graphs |
| [Architecture](docs/ARCHITECTURE.md) | System design and data flow |
| [API Reference](docs/API_SPEC.md) | All endpoints and schemas |
| [UI Spec](docs/UI_SPEC.md) | Design system and component spec |
| [Features](docs/FEATURES.md) | Complete feature breakdown |
| [Roadmap](docs/ROADMAP.md) | Current and planned development |
| [Project Spec](docs/PROJECT_SPEC.md) | Full project specification |

---

## 🧪 Development

### Mock Mode

Set `RABBITHOLE_MOCK=true` in your `.env` to use hardcoded knowledge graphs — no Groq API key needed.

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Testing

```bash
cd backend
python test_api.py     # Integration tests
python test_groq.py    # Groq connectivity test
```

---

## 🛤️ Roadmap

| Version | Focus |
|---------|-------|
| **v1.0** | ✅ Multi-mode graph generation, node expansion, gap analysis |
| **v1.1** | 🔄 Resource recommendations, improved learning time estimation |
| **v1.5** | 📋 Progress tracking, journey history |
| **v2.0** | 💾 Graph persistence, export (PNG/PDF/JSON) |
| **v2.5** | 👤 Personalization, smart topic discovery |
| **v3.0** | 🌍 Community maps, collaborative exploration |

See [ROADMAP.md](docs/ROADMAP.md) for full details.

---

## 🤝 Contributing

Contributions, ideas, and improvements are welcome.

1. Review the [Agent Instructions](docs/AGENTS.md) for development philosophy and rules
2. Check the [Roadmap](docs/ROADMAP.md) for planned features
3. Build **vertically** — finish one feature before starting another
4. Prioritize **functionality over optimization**, **clarity over cleverness**

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with curiosity, graphs, and AI. 🐰</sub>
</p>

<p align="center">
  <sub>RabbitHole transforms learning from a linear checklist into an explorable universe of ideas.</sub>
</p>
