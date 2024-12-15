from pythonjsonlogger import jsonlogger

from src.conf.settings import Env
from src.conf.settings import settings


class BaseJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(BaseJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name


log_level = settings.LOG_LEVEL.value

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": BaseJsonFormatter,
        },
        "uvicorn_json": {
            "()": BaseJsonFormatter,
        },
        "local": {
            "()": "logging.Formatter",
        },
    },
    "handlers": {
        "default": {
            "formatter": "local" if settings.ENV == Env.LOCAL else "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "gunicorn_uvicorn": {
            "formatter": "local" if settings.ENV == Env.LOCAL else "uvicorn_json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": [], "level": log_level},
        "gunicorn": {"handlers": ["gunicorn_uvicorn"], "level": log_level},
        "gunicorn.access": {"handlers": ["gunicorn_uvicorn"], "level": log_level},
        "gunicorn.error": {"handlers": ["gunicorn_uvicorn"], "level": log_level},
    },
    "root": {"handlers": ["default"], "level": log_level},
}
