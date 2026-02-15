import logging
import sys
from app.core.config import settings


def setup_logging():
    """Configure application logging with file and console handlers"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    detailed_formatter = logging.Formatter(
        "%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter("%(levelname)-8s | %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter if settings.DEBUG else detailed_formatter)

    handlers = [console_handler]
    if not settings.DEBUG and settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        handlers.append(file_handler)

    logging.basicConfig(level=log_level, handlers=handlers)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Logging configured - Level: %s", settings.LOG_LEVEL)
    logger.info("Debug mode: %s", settings.DEBUG)

    return logger
