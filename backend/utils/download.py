import requests
from io import BytesIO
from PIL import Image
from utils.logger import get_logger

logger = get_logger(__name__)

def download_image_to_pil(url):
    """
    Downloads an image from a URL and returns a PIL Image object (in-memory).
    Args:
        url (str): The image URL.
    Returns:
        PIL.Image.Image: The image as a PIL object.
    Raises:
        Exception: If the image cannot be downloaded or opened.
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
