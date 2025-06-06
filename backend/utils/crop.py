import os
from PIL import Image
from utils.logger import get_logger

logger = get_logger(__name__)

def crop_and_save(image_path, bbox, save_dir, crop_name=None):
    """
    Crops the region defined by bbox from image_path and saves it to save_dir.
    Args:
        image_path (str): Path to the source image.
        bbox (list): [x, y, w, h] bounding box.
        save_dir (str): Directory to save the cropped image.
        crop_name (str): Optional filename for the crop. If None, uses original name + bbox.
    Returns:
        crop_path (str): Path to the saved cropped image.
    """
    try:
        os.makedirs(save_dir, exist_ok=True)
        image = Image.open(image_path).convert("RGB")
        x, y, w, h = bbox
        crop = image.crop((x, y, x + w, y + h))
        if crop_name is None:
            base = os.path.splitext(os.path.basename(image_path))[0]
            crop_name = f"{base}_crop_{x}_{y}_{w}_{h}.jpg"
        crop_path = os.path.join(save_dir, crop_name)
        crop.save(crop_path)
        logger.info(f"Cropped and saved image to {crop_path}")
        return crop_path
    except Exception as e:
        logger.error(f"Failed to crop and save image {image_path}: {e}", exc_info=True)
        raise

def crop_to_pil(image_path, bbox):
    """
    Crops the region defined by bbox from image_path and returns a PIL Image (in-memory).
    Args:
        image_path (str): Path to the source image.
        bbox (list): [x, y, w, h] bounding box.
    Returns:
        crop (PIL.Image): Cropped image in memory.
    """
    image = Image.open(image_path).convert("RGB")
    x, y, w, h = bbox
    crop = image.crop((x, y, x + w, y + h))
    logger.info(f"Cropped image from {image_path} with bbox {bbox}")
    return crop