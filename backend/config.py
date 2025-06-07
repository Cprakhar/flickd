# Centralized configuration for directory and file paths
import os

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