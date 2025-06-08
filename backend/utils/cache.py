import os
import time
from utils.logger import get_logger

logger = get_logger(__name__)

CACHE_EXPIRY_SECONDS = 30 * 60  # 30 minutes

def is_expired(path, expiry_seconds=CACHE_EXPIRY_SECONDS):
    """
    Checks if the file or directory at `path` is older than `expiry_seconds`.

    Args:
        path (str): Path to the file or directory to check.
        expiry_seconds (int, optional): Expiry time in seconds. Defaults to CACHE_EXPIRY_SECONDS.

    Returns:
        bool: True if the path exists and is older than expiry_seconds, False otherwise.

    Logs the check for expiry.
    """
    if not os.path.exists(path):
        logger.info(f"Checked expiry for non-existent path: {path}")
        return False
    expired = (time.time() - os.path.getmtime(path)) > expiry_seconds
    logger.info(f"Checked expiry for {path}: {'expired' if expired else 'not expired'}.")
    return expired

def delete_path(path):
    """
    Recursively deletes a file or directory at `path`.

    Args:
        path (str): Path to the file or directory to delete.

    Returns:
        bool: True if deletion was successful, False otherwise.

    Logs all deletion actions and errors.
    """
    try:
        if os.path.isdir(path):
            for fname in os.listdir(path):
                fpath = os.path.join(path, fname)
                if os.path.isfile(fpath):
                    try:
                        os.remove(fpath)
                        logger.info(f"Deleted file: {fpath}")
                    except Exception as e:
                        logger.error(f"Failed to delete file {fpath}: {e}", exc_info=True)
                elif os.path.isdir(fpath):
                    delete_path(fpath)
            os.rmdir(path)
            logger.info(f"Deleted directory: {path}")
        elif os.path.isfile(path):
            os.remove(path)
            logger.info(f"Deleted file: {path}")
        else:
            logger.warning(f"Path does not exist or is not a file/directory: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete path {path}: {e}", exc_info=True)
        return False
