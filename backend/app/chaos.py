"""
Fault injection engine for SRE demo scenarios.

Toggle faults at runtime via /api/v1/chaos endpoints.
Each fault simulates a real production failure mode.
"""

import random
import time
import logging
from dataclasses import dataclass, field

logger = logging.getLogger("fintechco.chaos")


@dataclass
class FaultConfig:
    enabled: bool = False
    failure_rate: float = 1.0  # 0.0–1.0, percentage of requests affected
    latency_ms: int = 0        # extra latency to inject


@dataclass
class ChaosState:
    """Global mutable state for all fault injection toggles."""

    # Scenario 1: DB queries take too long (simulates slow queries / lock contention)
    db_slow_queries: FaultConfig = field(default_factory=lambda: FaultConfig(latency_ms=5000))

    # Scenario 2: DB connection fails entirely (simulates pool exhaustion / DB down)
    db_connection_failure: FaultConfig = field(default_factory=FaultConfig)

    # Scenario 3: Third-party payment processor is down
    payment_api_down: FaultConfig = field(default_factory=FaultConfig)

    # Scenario 4: Third-party payment processor is slow
    payment_api_slow: FaultConfig = field(default_factory=lambda: FaultConfig(latency_ms=8000))

    # Scenario 5: Intermittent 500s (simulates memory pressure / OOM kills)
    random_500s: FaultConfig = field(default_factory=lambda: FaultConfig(failure_rate=0.3))

    def reset_all(self):
        for attr in ["db_slow_queries", "db_connection_failure", "payment_api_down",
                      "payment_api_slow", "random_500s"]:
            getattr(self, attr).enabled = False

    def active_faults(self) -> list[str]:
        return [
            name for name in ["db_slow_queries", "db_connection_failure", "payment_api_down",
                               "payment_api_slow", "random_500s"]
            if getattr(self, name).enabled
        ]


# Singleton — shared across the app
chaos = ChaosState()


def should_fire(config: FaultConfig) -> bool:
    """Decide whether a fault should fire on this request."""
    if not config.enabled:
        return False
    return random.random() < config.failure_rate


def inject_db_latency():
    """Call before DB operations to simulate slow queries."""
    if should_fire(chaos.db_slow_queries):
        delay = chaos.db_slow_queries.latency_ms / 1000
        logger.warning("chaos.db_slow_queries: injecting %.1fs delay", delay,
                       extra={"fault": "db_slow_queries", "delay_ms": chaos.db_slow_queries.latency_ms})
        time.sleep(delay)


def check_db_connection():
    """Call before DB operations to simulate connection failures."""
    if should_fire(chaos.db_connection_failure):
        logger.error("chaos.db_connection_failure: rejecting DB connection",
                     extra={"fault": "db_connection_failure"})
        raise ConnectionError(
            "psycopg2.OperationalError: could not connect to server: Connection refused\n"
            "  Is the server running on host \"db.internal\" (10.0.3.42) and accepting\n"
            "  TCP/IP connections on port 5432?"
        )


def simulate_payment_api_call(transaction_id: str, amount: float) -> dict:
    """
    Simulates calling an external payment processor API.
    Used to demo third-party dependency failures.
    """
    # Slow payment API
    if should_fire(chaos.payment_api_slow):
        delay = chaos.payment_api_slow.latency_ms / 1000
        logger.warning("chaos.payment_api_slow: injecting %.1fs delay on payment call",
                       delay, extra={"fault": "payment_api_slow", "delay_ms": chaos.payment_api_slow.latency_ms})
        time.sleep(delay)

    # Payment API down
    if should_fire(chaos.payment_api_down):
        logger.error("chaos.payment_api_down: payment processor unreachable",
                     extra={"fault": "payment_api_down", "transaction_id": transaction_id})
        raise ConnectionError(
            "requests.exceptions.ConnectionError: HTTPSConnectionPool("
            "host='api.paymentprocessor.io', port=443): "
            "Max retries exceeded with url: /v2/charge "
            "(Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object>: "
            "Failed to establish a new connection: [Errno 110] Connection timed out'))"
        )

    return {"status": "approved", "processor_ref": f"PP-{transaction_id[:8]}"}


def check_random_500():
    """Randomly fail requests to simulate instability."""
    if should_fire(chaos.random_500s):
        logger.error("chaos.random_500s: injecting random server error",
                     extra={"fault": "random_500s"})
        raise RuntimeError("Internal server error: worker process out of memory")
