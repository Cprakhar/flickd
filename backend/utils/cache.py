import os
import time

CACHE_EXPIRY_SECONDS = 30 * 60  # 30 minutes

def is_expired(path, expiry_seconds=CACHE_EXPIRY_SECONDS):
    """
    Returns True if the file or directory at `path` is older than `expiry_seconds`.
    Returns False if the path does not exist.
    """
    if not os.path.exists(path):
        return False
    return (time.time() - os.path.getmtime(path)) > expiry_seconds

def delete_path(path):
    """
    Recursively deletes a file or directory at `path`.
    """
    if os.path.isdir(path):
        for fname in os.listdir(path):
            fpath = os.path.join(path, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)
            elif os.path.isdir(fpath):
                delete_path(fpath)
        os.rmdir(path)
    elif os.path.isfile(path):
        os.remove(path)
