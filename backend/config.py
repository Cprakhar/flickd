# Centralized configuration for directory and file paths
import os
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    # Base directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

    # Data files
    CATALOG_CSV_PATH = os.path.join(DATA_DIR, "catalog.csv")
    VIBES_LIST_PATH = os.path.join(DATA_DIR, "vibeslist.json")
    VIDEOS_DIR = os.path.join(DATA_DIR, "videos")
    TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "transcripts")
    DETECTIONS_DIR = os.path.join(DATA_DIR, "detections")
    FRAMES_DIR = os.path.join(DATA_DIR, "frames")
    CROPS_DIR = os.path.join(DATA_DIR, "crops")

    # Model files
    YOLO_MODEL_PATH = os.path.join(MODELS_DIR, "yolov8n-best.pt")
    CATALOG_EMBEDDINGS_PATH = os.path.join(MODELS_DIR, "catalog_clip_embeddings.npy")
    CATALOG_PRODUCT_IDS_PATH = os.path.join(MODELS_DIR, "catalog_product_ids.json")

    # Other config values can be added here as needed
    CLIP_MODEL_NAME = "openai/clip-vit-large-patch14"

    # Add this to make GROQ_API_KEY available in your backend
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

    logger.info("Configuration paths set up successfully.")
except Exception as e:
    logger.error(f"Failed to set up configuration paths: {e}", exc_info=True)

"""
Centralized configuration for directory and file paths used throughout the backend.

Attributes:
    BASE_DIR (str): Absolute path to the backend directory.
    DATA_DIR (str): Path to the data directory.
    MODELS_DIR (str): Path to the models directory.
    LOGS_DIR (str): Path to the logs directory.
    OUTPUTS_DIR (str): Path to the outputs directory.
    CATALOG_CSV_PATH (str): Path to the product catalog CSV file.
    VIBES_LIST_PATH (str): Path to the vibes list JSON file.
    VIDEOS_DIR (str): Path to the videos directory.
    TRANSCRIPTS_DIR (str): Path to the transcripts directory.
    DETECTIONS_DIR (str): Path to the detections directory.
    FRAMES_DIR (str): Path to the frames directory.
    CROPS_DIR (str): Path to the crops directory.
    YOLO_MODEL_PATH (str): Path to the YOLO model weights file.
    CATALOG_EMBEDDINGS_PATH (str): Path to the catalog CLIP embeddings file.
    CATALOG_PRODUCT_IDS_PATH (str): Path to the catalog product IDs file.
    CLIP_MODEL_NAME (str): Name of the CLIP model to use.
    GROQ_API_KEY (str): GROQ API key for backend access.

Logs configuration setup and errors. Raises no exceptions on import; logs errors instead.
"""