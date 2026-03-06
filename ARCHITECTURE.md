# FinTechCo Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Frontend                         │
│              React 19 + TypeScript + Vite                │
│                  localhost:5173                          │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ LoginPage│  │DashboardPage │  │TransactionsPage   │  │
│  └──────────┘  └──────────────┘  └───────────────────┘  │
│        │              │                   │              │
│        └──────────────┼───────────────────┘              │
│                       ▼                                  │
│               lib/api.ts (all fetch calls)               │
└───────────────────────┬─────────────────────────────────┘
                        │  HTTP (JSON)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                      │
│                   localhost:8000                          │
│                                                          │
│  ┌────────────────── /api/v1/ ────────────────────────┐  │
│  │                                                    │  │
│  │  /accounts    /transactions    /disputes           │  │
│  │  (routers/)   (routers/)       (routers/)          │  │
│  │                                                    │  │
│  └────────────────────┬───────────────────────────────┘  │
│                       │                                  │
│            schemas.py (Pydantic validation)               │
│                       │                                  │
│             models.py (SQLAlchemy ORM)                    │
│                       │                                  │
│              database.py (engine + sessions)              │
└───────────────────────┬─────────────────────────────────┘
                        │  SQLAlchemy
                        ▼
              ┌───────────────────┐
              │   SQLite (dev)    │
              │  PostgreSQL (prod)│
              └───────────────────┘
```

## Data Flow

User action → React component → `api.ts` → FastAPI router → Pydantic schema validation → SQLAlchemy query → DB → Pydantic `Out` schema → JSON response → React renders.

## Key Design Decisions

- **Single API client** (`lib/api.ts`) — all fetch calls in one place, never in components
- **Pydantic as the boundary** — validation happens in schemas, not route handlers
- **SQLite for dev, PostgreSQL for prod** — same ORM, zero code changes
- **shadcn/ui primitives** — consistent UI components, never modified directly
- **Stateless backend** — no server-side sessions, customer context passed per request
