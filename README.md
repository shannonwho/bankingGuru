# FinTechCo

A production-credible Digital Banking Dashboard demo featuring account management, transaction tracking, and a complete dispute workflow.

**Stack**: FastAPI + SQLAlchemy + PostgreSQL | React 19 + TypeScript + Vite + Tailwind + shadcn/ui

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000. OpenAPI docs at http://localhost:8000/docs.

### 3. Seed Data

```bash
curl -X POST http://localhost:8000/api/v1/seed
```

This creates 8 accounts, ~400 transactions, and 5-8 disputes with synthetic data.

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The UI runs at http://localhost:5173.

### 5. Run Tests

```bash
cd backend
pytest
```

## Project Structure

```
FinTechCo/
├── docker-compose.yml          # PostgreSQL 16
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/                # Database migrations
│   └── app/
│       ├── main.py             # FastAPI app + CORS + dashboard endpoint
│       ├── config.py           # Settings via env vars
│       ├── database.py         # SQLAlchemy engine + session
│       ├── models.py           # Account, Transaction, Dispute ORM models
│       ├── schemas.py          # Pydantic request/response models
│       ├── seed.py             # Synthetic data generator
│       └── routers/            # API route handlers
└── frontend/
    └── src/
        ├── App.tsx             # Router setup
        ├── lib/api.ts          # API client
        ├── types/index.ts      # TypeScript interfaces
        ├── components/         # UI components (shadcn + feature)
        └── pages/              # Dashboard, Transactions, Disputes
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/accounts` | List all accounts |
| GET | `/api/v1/accounts/{id}` | Account detail with stats |
| GET | `/api/v1/transactions` | Paginated + filterable transactions |
| GET | `/api/v1/transactions/{id}` | Single transaction |
| GET | `/api/v1/disputes` | List disputes (filterable) |
| GET | `/api/v1/disputes/{id}` | Single dispute |
| POST | `/api/v1/disputes` | File a new dispute |
| PATCH | `/api/v1/disputes/{id}` | Update dispute status |
| GET | `/api/v1/dashboard/summary` | Aggregate dashboard stats |
| POST | `/api/v1/seed` | Regenerate synthetic data |
| GET | `/api/v1/health` | Health check |

## Dispute Workflow

Disputes follow a strict state machine:
- **open** → investigating, denied
- **investigating** → resolved, denied
- **resolved**, **denied** → terminal (no further transitions)
