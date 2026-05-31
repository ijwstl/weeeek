# Weeeek

Daily/weekly reporting platform for engineering teams.

## Stack

Backend:

- Python
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Redis
- Celery

Frontend:

- Vue 3
- TypeScript
- Vite
- Pinia
- Vue Query
- Naive UI

## Local Development

Start infrastructure:

```bash
docker compose up -d postgres redis
```

Run backend:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

- Backend health: `http://localhost:8000/api/v1/health`
- Frontend: `http://localhost:5173`

## Documents

- [Requirements](./REQUIREMENTS.md)
- [Development Plan](./DEVELOPMENT_PLAN.md)

