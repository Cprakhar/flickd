import requests
from io import BytesIO
from PIL import Image
import tempfile
from utils.logger import get_logger
import cv2

logger = get_logger(__name__)

def download_image_to_pil(url):
    """
    Downloads an image from a URL and returns a PIL Image object (in-memory).

    Args:
        url (str): The image URL.

    Returns:
        PIL.Image.Image or None: The image as a PIL object if successful, None otherwise.

    Logs download progress and errors. Returns None if download or conversion fails.
    """
    try:
        logger.info(f"Downloading image from {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        logger.info(f"Successfully downloaded image from {url}")
        return img
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {e}", exc_info=True)
        return None


def download_video(video_url):
    """
    Downloads a video from a URL and returns a cv2.VideoCapture object and the temp file object.

    Args:
        video_url (str): The video URL.

    Returns:
        tuple: (cv2.VideoCapture, tempfile._TemporaryFileWrapper) if successful, (None, None) otherwise.

    Logs download progress and errors. Returns (None, None) if download or opening fails.
    """
    try:
        logger.info(f"Downloading video from {video_url}...")
        response = requests.get(video_url, timeout=10)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video_file:
            temp_video_file.write(response.content)
            temp_video_file.flush()
            video_capture = cv2.VideoCapture(temp_video_file.name)
            logger.info(f"Successfully downloaded and opened video from {video_url}")
            return (video_capture, temp_video_file)
    except Exception as e:
        logger.error(f"Failed to download video from {video_url}: {e}", exc_info=True)
        return (None, None)