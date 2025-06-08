import os
import numpy as np
import pandas as pd
import torch
from transformers import CLIPProcessor, CLIPModel
from utils.logger import get_logger
from utils.download import download_image_to_pil
import json

logger = get_logger(__name__)

def get_clip_embedding(image, clip_model, clip_processor) -> np.ndarray | None:
    """
    Extracts CLIP embedding for a given PIL image.

    Args:
        image (PIL.Image.Image): The input image.
        clip_model (CLIPModel): Pretrained CLIP model.
        clip_processor (CLIPProcessor): Processor for CLIP model.

    Returns:
        np.ndarray or None: Normalized CLIP embedding vector if successful, None otherwise.

    Logs embedding extraction progress and errors. Returns None if extraction fails.
    """
    try:
        inputs = clip_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            embedding = clip_model.get_image_features(**inputs)
            embedding = embedding / embedding.norm(p=2, dim=-1, keepdim=True)
        logger.info(f"Extracted embedding for image object")
        return embedding.squeeze().cpu().numpy()
    except Exception as e:
        logger.error(f"Failed to extract embedding: {e}", exc_info=True)
        return None


def extract_and_save_catalog_embeddings(df, models_dir, clip_model="openai/clip-vit-large-patch14"):
    """
    Extracts CLIP embeddings for all images in the catalog DataFrame and saves them to disk.

    Args:
        df (pd.DataFrame): DataFrame containing 'image_url' and 'id' columns.
        models_dir (str): Directory to save the embeddings and product IDs.
        clip_model (str, optional): Name or path of the CLIP model to use. Defaults to "openai/clip-vit-large-patch14".

    Returns:
        tuple: (str, str) Paths to the saved embeddings (.npy) and product IDs (.json) files.

    Logs progress and errors for each image. Skips images that fail to download or embed.
    """
    logger.info("Loading CLIP model and processor...")
    model, clip_processor = get_clip_processor_and_model(clip_model)

    logger.info(f"Reading catalog from DataFrame")
    image_paths = df['image_url'].tolist()
    product_ids = df['id'].tolist()

    embeddings = []
    filtered_product_ids = []
    for url, pid in zip(image_paths, product_ids):
        try:
            image = download_image_to_pil(url)
            if image is None:
                raise ValueError("Image download failed.")
            emb = get_clip_embedding(image, model, clip_processor)
            if emb is None:
                raise ValueError("Embedding extraction failed.")
            embeddings.append(emb)
            filtered_product_ids.append(pid)
        except Exception as e:
            logger.warning(f"Skipping embedding for product_id {pid} due to image/embedding failure: {e}")
            continue

    if not embeddings:
        logger.error("No embeddings were extracted. Nothing will be saved.")
        return None, None

    embeddings = np.stack(embeddings)
    os.makedirs(models_dir, exist_ok=True)
    emb_path = os.path.join(models_dir, "catalog_clip_embeddings.npy")
    ids_path = os.path.join(models_dir, "catalog_product_ids.json")
    try:
        np.save(emb_path, embeddings)
        with open(ids_path, "w") as f:
            json.dump(filtered_product_ids, f)
        logger.info(f"Saved {len(embeddings)} embeddings to {emb_path} and product IDs to {ids_path}.")
        return emb_path, ids_path
    except Exception as e:
        logger.error(f"Failed to save embeddings or product IDs: {e}", exc_info=True)
        return None, None


def get_clip_processor_and_model(clip_model='openai/clip-vit-large-patch14'):
    """
    Loads the CLIP model and processor from HuggingFace.

    Args:
        clip_model (str): Name or path of the CLIP model to load.

    Returns:
        tuple: (CLIPModel, CLIPProcessor)

    Logs model loading progress and errors. Raises exception if loading fails.
    """
    try:
        logger.info(f"Loading CLIP model and processor: {clip_model}")
        model = CLIPModel.from_pretrained(clip_model)
        clip_processor = CLIPProcessor.from_pretrained(clip_model)
        logger.info(f"Successfully loaded CLIP model and processor: {clip_model}")
        return model, clip_processor
    except Exception as e:
        logger.error(f"Failed to load CLIP model or processor: {e}", exc_info=True)
        raise