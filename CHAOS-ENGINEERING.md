# Chaos Engineering + Observability System

## Architecture

### New files
- `app/chaos.py` — Fault injection engine with 5 failure modes
- `app/routers/chaos.py` — Admin API to toggle faults
- `app/middleware.py` — Request tracing with correlation IDs, structured error responses
- `app/observability.py` — JSON logging + Datadog APM setup

### Modified files
- `app/main.py` — Wired observability, chaos router, enhanced health check
- `app/database.py` — Chaos hooks in `get_db()` dependency
- `app/routers/transactions.py` — Added `/verify` endpoint for payment API demo
- `pyproject.toml` — Added `ddtrace` dependency

## Fault Scenarios

| Endpoint | What it simulates |
|----------|-------------------|
| `POST /api/v1/chaos/scenarios/db-outage` | 100% DB connection failures |
| `POST /api/v1/chaos/scenarios/db-degraded` | 60% slow queries (5s) + 10% connection failures |
| `POST /api/v1/chaos/scenarios/payment-outage` | Payment processor completely down |
| `POST /api/v1/chaos/scenarios/cascading-failure` | Slow DB + slow payments + random 500s |
| `POST /api/v1/chaos/reset` | Kill switch — disable all faults |
| `POST /api/v1/chaos/faults/{name}` | Toggle individual faults with custom rates |

### Individual Fault Names

- `db_slow_queries` — Injects latency before DB operations
- `db_connection_failure` — Simulates DB pool exhaustion / DB down
- `payment_api_down` — Third-party payment processor unreachable
- `payment_api_slow` — Third-party payment processor slow responses
- `random_500s` — Intermittent server errors (memory pressure / OOM)

### Custom Fault Toggle Example

```bash
# Enable DB slow queries on 50% of requests with 3s latency
curl -X POST http://localhost:8000/api/v1/chaos/faults/db_slow_queries \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "failure_rate": 0.5, "latency_ms": 3000}'
```

## Datadog Integration

Set env vars before starting the server:

```bash
DD_AGENT_HOST=localhost DD_ENV=dev uvicorn app.main:app --port 8000
```

This auto-instruments:
- **FastAPI routes** — request traces with status codes and durations
- **SQLAlchemy queries** — DB query spans with timing
- **Logs** — `dd.trace_id` and `dd.span_id` injected into all JSON log lines

All logs are structured JSON, ready for Datadog log pipelines with no additional parsing needed.

### Required: Datadog Agent

Make sure the Datadog Agent is running locally (or wherever `DD_AGENT_HOST` points):

```bash
# macOS
brew install datadog-agent
# Or Docker
docker run -d --name dd-agent \
  -e DD_API_KEY=<your-api-key> \
  -e DD_SITE="datadoghq.com" \
  -p 8126:8126 \
  datadog/agent:latest
```

## Health Check

`GET /api/v1/health` bypasses chaos injection and reports real status:

```json
// Healthy
{"status": "ok", "checks": {"api": "ok", "database": "ok"}}

// During chaos
{"status": "degraded", "checks": {"api": "ok", "database": "ok", "chaos_active": ["db_connection_failure"]}}
```

## Demo Flow

### 1. Start the app

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 2. Verify everything is healthy

```bash
curl http://localhost:8000/api/v1/health
```

### 3. Trigger a scenario

```bash
# DB outage
curl -X POST http://localhost:8000/api/v1/chaos/scenarios/db-outage

# Or cascading failure
curl -X POST http://localhost:8000/api/v1/chaos/scenarios/cascading-failure
```

### 4. Observe failures

```bash
# API calls now fail or are slow
curl http://localhost:8000/api/v1/accounts
curl http://localhost:8000/api/v1/health

# Payment verification fails
curl -X POST http://localhost:8000/api/v1/transactions/<id>/verify
```

### 5. Ask Claude to diagnose

Point Claude at the health endpoint, logs, or Datadog traces and ask it to identify the issue and suggest remediation.

### 6. Reset and verify recovery

```bash
curl -X POST http://localhost:8000/api/v1/chaos/reset
curl http://localhost:8000/api/v1/health
```
