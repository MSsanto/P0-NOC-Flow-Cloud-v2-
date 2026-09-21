import json
import logging
from datetime import UTC, datetime


def configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(message)s")


def log_http_request(
    *,
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
) -> None:
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "level": "INFO" if status_code < 500 else "ERROR",
        "event": "http_request",
        "request_id": request_id,
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    logging.getLogger("nocflow.http").log(
        logging.INFO if status_code < 500 else logging.ERROR,
        json.dumps(payload, separators=(",", ":"), sort_keys=True),
    )
