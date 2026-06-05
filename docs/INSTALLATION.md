# RabbitHole - Installation Guide

## Prerequisites

Before installing RabbitHole, ensure the following are installed:

### Node.js

Recommended:

```text
Node.js 20+
```

Verify installation:

```bash
node -v
npm -v
```

---

### Python

Recommended:

```text
Python 3.12+
```

Verify installation:

```bash
python --version
```

---

### Git

Verify installation:

```bash
git --version
```

---

# Clone Repository

```bash
git clone https://github.com/<your-username>/rabbit-hole.git

cd rabbit-hole
```

---

# Frontend Setup

Navigate to frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Install required packages:

```bash
npm install reactflow
npm install axios
npm install react-icons
npm install tailwindcss @tailwindcss/vite
```

Start development server:

```bash
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

# Backend Setup

Navigate to backend:

```bash
cd backend
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment.

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install fastapi
pip install uvicorn
pip install groq
pip install python-dotenv
pip install pydantic
```

Or:

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create:

```text
backend/.env
```

Add:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

# Groq API Setup

Create an account:

Groq Console

Generate an API key.

Copy the key into:

```text
backend/.env
```

Never commit API keys to GitHub.

---

# Run Backend

Navigate to backend:

```bash
cd backend
```

Start server:

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

---

# Verify Installation

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8000
```

Health Check:

```text
http://localhost:8000/api/v1/health
```

Expected Response:

```json
{
  "status": "healthy",
  "service": "rabbit-hole-api"
}
```

---

# Project Structure

```text
rabbit-hole/

├── frontend/
├── backend/
├── docs/

├── README.md
├── LICENSE
└── .gitignore
```

---

# Troubleshooting

## Port Already In Use

Frontend:

```bash
npm run dev -- --host
```

Backend:

```bash
uvicorn app.main:app --reload --port 8001
```

---

## Missing Dependencies

Update packages:

```bash
npm install

pip install -r requirements.txt
```

---

## Invalid Groq Key

Verify:

```env
GROQ_API_KEY=your_key
```

and restart backend.

---

# Installation Complete

RabbitHole is now ready for local development.
