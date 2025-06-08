import os
from utils.logger import get_logger

logger = get_logger(__name__)

def file_exists(file_path: str) -> bool:
    """
    Check if a file exists at the given path.

    Args:
        file_path (str): The path to the file to check.

    Returns:
        bool: True if the file exists, False otherwise.

    Logs the result of the existence check.
    """
    try:
        exists = os.path.isfile(file_path)
        logger.info(f"Checked file existence: {file_path} - {'exists' if exists else 'does not exist'}.")
        return exists
    except Exception as e:
        logger.error(f"Error checking file existence for {file_path}: {e}", exc_info=True)
        return False

def directory_exists(directory: str) -> bool:
    """
    Check if a directory exists at the given path.

    Args:
        directory (str): The path to the directory to check.

    Returns:
        bool: True if the directory exists and is a directory, False otherwise.

    Logs the result of the existence check.
    """
    try:
        exists = os.path.isdir(directory)
        logger.info(f"Checked directory existence: {directory} - {'exists' if exists else 'does not exist'}.")
        return exists
    except Exception as e:
        logger.error(f"Error checking directory existence for {directory}: {e}", exc_info=True)
        return False
