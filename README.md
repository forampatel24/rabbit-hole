# RabbitHole (MVP)

This repo contains the RabbitHole MVP: an AI-powered knowledge exploration platform.

Backend:
- FastAPI app in backend/app
- Run: python -m uvicorn backend.app.main:app --reload --port 8000

Frontend:
- Vite + React in frontend/
- Run: npm install && npm run dev (default port 5173)

Env:
- Backend: copy backend/.env.example to backend/.env and set GROQ_API_KEY if available. If not set, mock mode is used.

Notes:
- The Groq integration is mocked by default for local development.
- The frontend expects API at http://localhost:8000/api/v1
