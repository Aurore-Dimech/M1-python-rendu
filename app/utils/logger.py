import logging
import os
import sys


def setup_logging() -> None:
    type_env = os.getenv("ENV", "development")

    if type_env == "development":
        level = logging.DEBUG
    else:
        level = logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if type_env == "development":
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    else:
        # Production : format plus simple
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configuré - Environnement: {type_env}")


def get_logger(name: str) -> logging.Logger:
    """
    Get the logger for logs

    Args:
        name (str): Name of the file (by default __name__ of the module)

    Returns:
        logging.Logger: Logger for module
    """
    return logging.getLogger(name)
