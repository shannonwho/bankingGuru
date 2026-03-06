"""
Logging and Datadog setup.

Configures structured JSON logging and optionally enables ddtrace APM.
Set DD_AGENT_HOST and DD_API_KEY env vars to enable Datadog forwarding.
"""

import json
import logging
import os
import sys


class JSONFormatter(logging.Formatter):
    """Emit logs as single-line JSON for Datadog log ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "fintechco-api",
        }

        # Merge extra fields from structured logging calls
        for key in ["trace_id", "method", "path", "status", "duration_ms",
                     "client_ip", "error", "fault", "delay_ms", "transaction_id",
                     "dd.trace_id", "dd.span_id"]:
            val = getattr(record, key, None)
            if val is not None:
                log_entry[key] = val

        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging():
    """Configure root logger with JSON output."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Clear any existing handlers
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root.addHandler(handler)

    # Quiet down noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def setup_datadog():
    """
    Initialize ddtrace if DD_AGENT_HOST is set.
    This patches FastAPI, SQLAlchemy, and requests for automatic tracing.
    """
    dd_host = os.environ.get("DD_AGENT_HOST")
    if not dd_host:
        logging.getLogger("fintechco.observability").info(
            "DD_AGENT_HOST not set — Datadog tracing disabled. "
            "Set DD_AGENT_HOST=localhost to enable."
        )
        return

    try:
        from ddtrace import config, tracer, patch_all

        config.service = "fintechco-api"
        config.env = os.environ.get("DD_ENV", "dev")
        config.version = "0.1.0"

        # Auto-patch supported libraries
        patch_all(
            fastapi=True,
            sqlalchemy=True,
            requests=True,
            logging=True,  # Injects dd.trace_id/dd.span_id into log records
        )

        tracer.configure(
            hostname=dd_host,
            port=int(os.environ.get("DD_TRACE_AGENT_PORT", 8126)),
        )

        logging.getLogger("fintechco.observability").info(
            "Datadog APM enabled — traces going to %s", dd_host
        )
    except ImportError:
        logging.getLogger("fintechco.observability").warning(
            "ddtrace not installed — run: pip install ddtrace"
        )
