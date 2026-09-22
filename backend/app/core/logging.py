import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.core.config import Settings, get_settings

_LOGGER_NAME = "nocflow"
_RESERVED_FIELDS = {
    "request_id",
    "trace_id",
    "route",
    "method",
    "status_code",
    "duration_ms",
    "actor_id",
    "tenant_id",
    "error_code",
}


class JsonFormatter(logging.Formatter):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": self.settings.app_name,
            "environment": self.settings.environment,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in _RESERVED_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception_type"] = record.exc_info[0].__name__
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    logger = logging.getLogger(_LOGGER_NAME)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(settings))
    logger.addHandler(handler)
    logger.setLevel(settings.log_level.upper())
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{_LOGGER_NAME}.{name}")
