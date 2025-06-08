import os
import logging


def get_logger(name=__name__):
    """
    Returns a logger instance with both console and file handlers.
    Logs are written to 'logs/flickd.log' and streamed to the console.
    Ensures handlers are not duplicated for the same logger.

    Args:
        name (str, optional): Logger name. Defaults to __name__.

    Returns:
        logging.Logger: Configured logger instance.

    Handles errors in logger setup and logs them to the console.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    try:
        os.makedirs('logs', exist_ok=True)
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler('logs/flickd.log')
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        if not logger.handlers:
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
        logger.propagate = False
    except Exception as e:
        # Fallback: log to console if file handler setup fails
        fallback_handler = logging.StreamHandler()
        fallback_formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
        fallback_handler.setFormatter(fallback_formatter)
        if not logger.handlers:
            logger.addHandler(fallback_handler)
        logger.error(f"Logger setup failed: {e}", exc_info=True)
    return logger