"""
Admin endpoints to toggle fault injection scenarios.
In production these would be behind auth — here they're open for demo purposes.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.chaos import chaos

router = APIRouter(prefix="/chaos", tags=["chaos-engineering"])


class FaultToggle(BaseModel):
    enabled: bool
    failure_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    latency_ms: int = Field(default=0, ge=0, le=30000)


class ChaosStatus(BaseModel):
    db_slow_queries: dict
    db_connection_failure: dict
    payment_api_down: dict
    payment_api_slow: dict
    random_500s: dict
    active_faults: list[str]


def _fault_to_dict(f):
    return {"enabled": f.enabled, "failure_rate": f.failure_rate, "latency_ms": f.latency_ms}


@router.get("", response_model=ChaosStatus)
def get_chaos_status():
    """Show current state of all fault injection toggles."""
    return ChaosStatus(
        db_slow_queries=_fault_to_dict(chaos.db_slow_queries),
        db_connection_failure=_fault_to_dict(chaos.db_connection_failure),
        payment_api_down=_fault_to_dict(chaos.payment_api_down),
        payment_api_slow=_fault_to_dict(chaos.payment_api_slow),
        random_500s=_fault_to_dict(chaos.random_500s),
        active_faults=chaos.active_faults(),
    )


# ---- Kill switch (must be before /{fault_name} to avoid route conflict) ----

@router.post("/reset")
def reset_all_faults():
    """Kill switch — disable all faults immediately."""
    chaos.reset_all()
    return {"message": "All faults disabled", "active_faults": []}


# ---- Pre-built SRE scenarios ----

@router.post("/scenarios/db-outage")
def scenario_db_outage():
    """Simulate a full database outage — connection failures on 100% of requests."""
    chaos.reset_all()
    chaos.db_connection_failure.enabled = True
    chaos.db_connection_failure.failure_rate = 1.0
    return {"scenario": "db-outage", "description": "All DB connections are failing"}


@router.post("/scenarios/db-degraded")
def scenario_db_degraded():
    """Simulate degraded DB — slow queries on 60% of requests + 10% connection failures."""
    chaos.reset_all()
    chaos.db_slow_queries.enabled = True
    chaos.db_slow_queries.failure_rate = 0.6
    chaos.db_slow_queries.latency_ms = 5000
    chaos.db_connection_failure.enabled = True
    chaos.db_connection_failure.failure_rate = 0.1
    return {"scenario": "db-degraded", "description": "60% of queries are slow (5s), 10% fail entirely"}


@router.post("/scenarios/payment-outage")
def scenario_payment_outage():
    """Simulate payment processor down — all payment API calls fail."""
    chaos.reset_all()
    chaos.payment_api_down.enabled = True
    chaos.payment_api_down.failure_rate = 1.0
    return {"scenario": "payment-outage", "description": "Payment processor is unreachable"}


@router.post("/scenarios/cascading-failure")
def scenario_cascading_failure():
    """Simulate cascading failure — slow DB + slow payments + random 500s."""
    chaos.reset_all()
    chaos.db_slow_queries.enabled = True
    chaos.db_slow_queries.failure_rate = 0.4
    chaos.db_slow_queries.latency_ms = 3000
    chaos.payment_api_slow.enabled = True
    chaos.payment_api_slow.failure_rate = 0.5
    chaos.payment_api_slow.latency_ms = 8000
    chaos.random_500s.enabled = True
    chaos.random_500s.failure_rate = 0.2
    return {
        "scenario": "cascading-failure",
        "description": "40% slow DB (3s) + 50% slow payments (8s) + 20% random 500s",
    }


# ---- Individual fault toggle (path param — must be last) ----

@router.post("/faults/{fault_name}")
def toggle_fault(fault_name: str, body: FaultToggle):
    """Enable or disable a specific fault. Valid names: db_slow_queries, db_connection_failure, payment_api_down, payment_api_slow, random_500s."""
    config = getattr(chaos, fault_name, None)
    if config is None:
        return {"error": f"Unknown fault: {fault_name}", "valid": [
            "db_slow_queries", "db_connection_failure", "payment_api_down",
            "payment_api_slow", "random_500s",
        ]}
    config.enabled = body.enabled
    config.failure_rate = body.failure_rate
    if body.latency_ms:
        config.latency_ms = body.latency_ms
    action = "ENABLED" if body.enabled else "DISABLED"
    return {"fault": fault_name, "action": action, **_fault_to_dict(config)}
