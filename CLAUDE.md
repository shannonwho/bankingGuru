# bankingGuru — Project Intelligence

## Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, SQLite (dev) / PostgreSQL (prod)
- **Frontend**: React 19, TypeScript 5, Vite, Tailwind CSS v4, shadcn/ui (Radix primitives), React Router v7, Recharts
- **Tests**: pytest + FastAPI TestClient (backend); TypeScript `tsc --noEmit` + Vite build (frontend)
- **CI**: GitHub Actions (`.github/workflows/ci.yml`)

## Project structure
```
backend/
  app/
    main.py          # FastAPI app, dashboard + seed endpoints
    models.py        # SQLAlchemy ORM models: Account, Transaction, Dispute
    schemas.py       # Pydantic request/response schemas + validators
    database.py      # DB engine, session, Base
    seed.py          # Demo data seeder
    routers/
      accounts.py
      transactions.py
      disputes.py    # DIS-10: dispute submission flow
      fraud.py       # Fraud scoring router (wires fraud_model.py)
    fraud_model.py   # Fraud scoring model (DS team, not yet wired)
  tests/
    conftest.py      # pytest fixtures: in-memory SQLite, TestClient
    test_api.py      # General API integration tests
    test_disputes.py # Focused dispute flow tests (DIS-10)

frontend/
  src/
    pages/           # Route-level components
    components/
      ui/            # shadcn primitives (do not modify)
      layout/        # Shell, Sidebar
      accounts/      # AccountCard, AccountList
      transactions/  # TransactionTable, TransactionFilters
      disputes/      # DisputeForm, DisputeList, DisputeDetail
    lib/
      api.ts         # All fetch calls — single source of truth
      utils.ts       # formatCurrency, formatDate, formatDateTime, cn
    types/index.ts   # Shared TypeScript interfaces
    contexts/
      AuthContext.tsx # Customer login context

.github/
  workflows/
    ci.yml           # lint → typecheck → test → build on push/PR
```

## Key conventions

### Backend
- All routes live under `/api/v1/` prefix
- Routers return Pydantic `Out` schemas — never raw ORM objects
- Validation happens in Pydantic schemas via `@field_validator`, not in route handlers
- Business rule constants (e.g. `DISPUTE_WINDOW_DAYS`) defined in `schemas.py` and imported where needed
- HTTP status codes: 201 for creates, 404 for not found, 409 for conflicts, 422 for business rule violations
- DB sessions injected via `Depends(get_db)` — never create sessions manually in routes

### Frontend
- All API calls go through `src/lib/api.ts` — never use `fetch` directly in components
- Shared types live in `src/types/index.ts` — keep in sync with backend schemas
- UI primitives from `src/components/ui/` — never modify these directly
- Format all currency with `formatCurrency()`, all dates with `formatDate()` / `formatDateTime()`
- Error state pattern: `const [error, setError] = useState("")` → render as `<p className="text-destructive">`
- Loading state pattern: `const [saving, setSaving] = useState(false)` on async actions

### Testing
- Backend tests use an in-memory SQLite DB via `conftest.py` fixtures — no real DB needed
- Every new API endpoint needs at minimum: happy path, 404/422, conflict/duplicate
- State machines need: every valid transition + every invalid transition + terminal state block
- Time-based logic needs: boundary tests at N-1, N, N+1 days
- Test names are sentences: `test_dispute_window_expired_rejected`, not `test_window`

### Git
- Feature branches: `feature/<linear-id>-<short-description>` (e.g. `feature/dis-10-dispute-submission-flow`)
- Main branch is always demo-ready — never push broken code to main
- One logical change per commit; message in imperative mood

## Linear teams
- **SWEs** (key: DIS): digital payments, mobile, banking infrastructure
- **DataScientiest** (key: DAT): fraud detection, credit scoring, customer behavior

## Demo personas (seed data)
- Marcus Chen — 3 accounts (checking, savings, credit card)
- Aisha Patel — 2 accounts (checking, savings)
- Sofia Rodriguez — disputes owner in seed data
- Yuki Tanaka — 1 account
- James Okafor — 1 account
