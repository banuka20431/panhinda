import logging.config
import os

LOG_DIR = os.environ.get("LOG_DIR", "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, "app.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "panhinda_logger": {  # Base logger for your app
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {  # Catch-all for 3rd party libraries (like Flask/SQLAlchemy)
        "level": "WARNING",
        "handlers": ["console"],
    }
}

def init_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
