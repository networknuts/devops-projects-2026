# AI Question Answering Web Application

This package contains a minimal production-style implementation for the architecture documents.

## Structure

- `backend/` - FastAPI application that calls OpenAI and stores chats in PostgreSQL
- `frontend/` - Node.js frontend server serving a simple chat UI

## Backend run steps

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Frontend run steps

```bash
cd frontend
npm install
API_BASE_URL=http://proxy-01/api npm start
```

## Key API endpoints

- `GET /health`
- `POST /chat`
- `GET /conversations/{conversation_id}`
