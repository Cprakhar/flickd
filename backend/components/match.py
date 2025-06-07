import pandas as pd
import faiss
from utils.crop import crop_to_pil
from utils.extract_catalog_embeddings import get_clip_embedding, get_clip_processor_and_model
from utils.logger import get_logger

logger = get_logger(__name__)

def load_meta(catalog_csv: pd.DataFrame):
    meta = {}
    for _, row in catalog_csv.iterrows():
        pid = str(row['id'])
        # Only keep the first occurrence (first shot angle) for each product_id
        if pid not in meta:
            meta[pid] = {
                'title': row['title'],
                'category': row['category'],
                'color': row['color'],
                'image_url': row['image_url']
            }
    return meta


def match_product(detection, frame_file, catalog_embeddings, catalog_products_id, catalog_csv, clip_model, top_k=1):
    """
    Match a detected fashion item with the catalog embeddings.
    Args:
        detection (dict): A single detection containing class_name, bbox, confidence, and frame_number.
        frame_file (str): Path to the frame image.
        catalog_embeddings (numpy): Catalog embeddings loaded from a file.
        catalog_products_id (list): List of product IDs corresponding to the catalog embeddings.
        catalog_csv (pd.DataFrame): Catalog dataframe
        top_k (int): Number of top matches to return.
    Returns:
        list: Top K matched products with their IDs and similarity scores.
    """
    
    # Crop image, get its embeddings and load the CLIP processor and model

    logger.info(f"Matching products from catalog with detections items from {frame_file}...")
    cropped_image = crop_to_pil(frame_file, detection["bbox"])
    model, clip_processor = get_clip_processor_and_model(clip_model)
    cropped_image_embeddings = get_clip_embedding(cropped_image, model, clip_processor)
    cropped_image_embeddings = cropped_image_embeddings.reshape(1, -1)

    # Build FAISS index
    faiss_index = faiss.IndexFlatIP(catalog_embeddings.shape[1])
    faiss_index.add(catalog_embeddings)

    catalog_meta = load_meta(catalog_csv)

    D, I = faiss_index.search(cropped_image_embeddings, top_k)
    matches = []
    for score, idx in zip(D[0], I[0]):
        product_id = catalog_products_id[idx]
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
            "confidence": round(float(score), 3),
            "type": meta.get("category", None),
            "color": meta.get("color", None),
            "title": meta.get("title", None),
            "image_url": meta.get("image_url", None)
        })
    logger.info(f"{len(matches)} items got matched with the {frame_file}")
    return matches