"""
Request lifecycle middleware — structured logging, correlation IDs, error handling.
"""

import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.chaos import check_random_500

logger = logging.getLogger("fintechco.http")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
        request.state.trace_id = trace_id

        start = time.perf_counter()
        status_code = 500
        error_detail = None

        try:
            # Random 500 fault injection (before any route logic)
            check_random_500()

            response: Response = await call_next(request)
            status_code = response.status_code
            response.headers["x-trace-id"] = trace_id
            return response

        except RuntimeError as e:
            # From chaos random_500s
            status_code = 500
            error_detail = str(e)
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"detail": str(e), "trace_id": trace_id},
                headers={"x-trace-id": trace_id},
            )

        except Exception as e:
            status_code = 500
            error_detail = str(e)
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "trace_id": trace_id},
                headers={"x-trace-id": trace_id},
            )

        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            log_data = {
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "status": status_code,
                "duration_ms": round(duration_ms, 1),
                "client_ip": request.client.host if request.client else None,
            }
            if error_detail:
                log_data["error"] = error_detail

            level = logging.WARNING if status_code >= 400 else logging.INFO
            if status_code >= 500:
                level = logging.ERROR

            logger.log(level, "%s %s → %d (%.1fms)",
                       request.method, request.url.path, status_code, duration_ms,
                       extra=log_data)
