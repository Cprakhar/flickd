import os
import numpy as np
import pandas as pd
import torch
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from utils.logger import get_logger
from utils.download import download_image_to_pil
import json

logger = get_logger(__name__)

def get_clip_embedding(image, clip_model, clip_processor) -> np.ndarray | None:
    """
    Extracts CLIP embedding for a given PIL image.
    Args:
        image (PIL.Image): The input image.
        clip_model (CLIPModel): Pretrained CLIP model.
        clip_processor (CLIPProcessor): Processor for CLIP model.
    Returns:
        np.ndarray: Normalized CLIP embedding vector.
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
        raise

def extract_and_save_catalog_embeddings(df, models_dir, clip_model="openai/clip-vit-large-patch14"):
    logger.info("Loading CLIP model and processor...")
    model, clip_processor = get_clip_processor_and_model(clip_model)

    logger.info(f"Reading catalog from catalog.csv")
    image_paths = df['image_url'].tolist()
    product_ids = df['id'].tolist()

    embeddings = []
    filtered_product_ids = []
    for url, pid in zip(image_paths, product_ids):
        try:
            image = download_image_to_pil(url)
            emb = get_clip_embedding(image, model, clip_processor)
            embeddings.append(emb)
            filtered_product_ids.append(pid)
        except Exception:
            logger.warning(f"Skipping embedding for product_id {pid} due to image/embedding failure.")
            continue

    embeddings = np.stack(embeddings)
    os.makedirs(models_dir, exist_ok=True)
    emb_path = os.path.join(models_dir, "catalog_clip_embeddings.npy")
    ids_path = os.path.join(models_dir, "catalog_product_ids.json")
    np.save(emb_path, embeddings)

    with open(ids_path, "w") as f:
        json.dump(filtered_product_ids, f)
    logger.info(f"Saved {len(embeddings)} embeddings to {emb_path} and product IDs to {ids_path}.")


def get_clip_processor_and_model(clip_model='openai/clip-vit-large-patch14'):
    model = CLIPModel.from_pretrained(clip_model)
    clip_processor = CLIPProcessor.from_pretrained(clip_model)
    return model, clip_processor