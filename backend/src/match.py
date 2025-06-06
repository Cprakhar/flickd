import os
import numpy as np
import pandas as pd
import json
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
import faiss
from src.config import CATALOG_EMBEDDINGS_PATH, CATALOG_PRODUCT_IDS_PATH, CATALOG_CSV_PATH, CLIP_MODEL_NAME
from utils.download import download_image_to_pil
from utils.extract_catalog_embeddings import get_clip_embedding, extract_and_save_catalog_embeddings
from utils.logger import get_logger

logger = get_logger(__name__)

def match_products(crop, top_k=1, is_url=False):
    """
    Matches a cropped image (PIL.Image or path/URL) to the catalog using CLIP+FAISS.
    Args:
        crop (PIL.Image or str): Cropped image as PIL.Image or path/URL.
        top_k (int): Number of top matches to return.
        is_url (bool): If True, treat crop as a URL and download in-memory.
    Returns:
        List of match dicts.
    """

    # Load CLIP model and processor
    tokenizer = CLIPTokenizer.from_pretrained(CLIP_MODEL_NAME, use_fast=True)
    clip_model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)
    clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME, tokenizer=tokenizer)

    # Check for catalog embeddings and product IDs, generate if missing
    if not (os.path.exists(CATALOG_EMBEDDINGS_PATH) and os.path.exists(CATALOG_PRODUCT_IDS_PATH)):
        logger.warning("Catalog embeddings or product IDs not found. Generating them now...")
        extract_and_save_catalog_embeddings()
        logger.info("Catalog embeddings and product IDs generated.")

    # Load catalog embeddings and product IDs
    catalog_embeddings = np.load(CATALOG_EMBEDDINGS_PATH)
    with open(CATALOG_PRODUCT_IDS_PATH, "r") as f:
        catalog_product_ids = json.load(f)

    # Build FAISS index
    faiss_index = faiss.IndexFlatIP(catalog_embeddings.shape[1])
    faiss_index.add(catalog_embeddings)

    # Map product_id to catalog row (for metadata)
    def load_catalog_metadata():
        df = pd.read_csv(CATALOG_CSV_PATH)
        meta = {}
        for _, row in df.iterrows():
            meta[str(row['id'])] = {
                'title': row['title'],
                'category': row['category'],
                'color': row['color']
            }
        return meta

    catalog_meta = load_catalog_metadata()

    # Accept PIL.Image directly, or path/URL as before
    if isinstance(crop, Image.Image):
        image = crop
    elif is_url:
        image = download_image_to_pil(crop)
    else:
        image = Image.open(crop).convert("RGB")
    emb = get_clip_embedding(image, clip_model, clip_processor)
    emb = emb.reshape(1, -1)
    D, I = faiss_index.search(emb, top_k)
    matches = []
    for score, idx in zip(D[0], I[0]):
        product_id = catalog_product_ids[idx]
        meta = catalog_meta.get(str(product_id), {})
        if score < 0.75:
            continue
        match_type = (
            "exact" if score > 0.9 else
            "similar"
        )
        matches.append({
            "matched_product_id": product_id,
            "match_type": match_type,
            "confidence": float(score),
            "type": meta.get("category", None),
            "color": meta.get("color", None),
            "title": meta.get("title", None)
        })
    return matches