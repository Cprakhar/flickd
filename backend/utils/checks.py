import os

def file_exists(file_path: str) -> bool:
    """
    Check if a directory exists and is a directory.
    Args:
        directory (str): The path to the directory to check.
    Returns:
        bool: True if the directory exists and is a directory, False otherwise.
    """
    return os.path.exists(file_path)

def directory_exists(directory: str) -> bool:
    """
    Check if a directory exists and is a directory.
    Args:
        directory (str): The path to the directory to check.
    Returns:
        bool: True if the directory exists and is a directory, False otherwise.
    """
    return os.path.isdir(directory)
