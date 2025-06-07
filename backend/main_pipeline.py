import os
import json
import numpy as np
import pandas as pd
from components.extract_frames import extract_frames
from components.detect import detect_fashion_items
from components.transcribe import transcribe_audio
from components.match import match_product
from utils.logger import get_logger
from utils.download import download_video
from components.vibe import vibe_classification
from utils.extract_catalog_embeddings import extract_and_save_catalog_embeddings
from config import FRAMES_DIR, YOLO_MODEL_PATH, TRANSCRIPTS_DIR, CLIP_MODEL_NAME, CATALOG_EMBEDDINGS_PATH, CATALOG_PRODUCT_IDS_PATH, CATALOG_CSV_PATH, MODELS_DIR, OUTPUTS_DIR, VIBES_LIST_PATH
from utils.checks import file_exists, directory_exists

logger = get_logger(__name__)


class FlickdPipeline:
    def __init__(self, 
                video_item,
                frame_rate=1, 
                conf=0.3, 
                model_size="small", 
                yolo_model='yolov8n.pt',
                clip_model='openai/clip-vit-large-patch14',
                catalog_embeddings_file=None,
                catalog_product_ids_file=None,
                catalog_csv_file=None,
                models_dir = 'models',
                outputs_dir = 'outputs',
                transcripts_dir = 'transcripts',
                frames_dir = 'frames',
                vibes_list_file = None
                ):
        self.video_item = video_item
        self.frame_rate = frame_rate
        self.conf = conf
        self.model_size = model_size
        self.yolo_model = yolo_model
        self.clip_model = clip_model
        self.catalog_embeddings_file = catalog_embeddings_file
        self.catalog_product_ids_file = catalog_product_ids_file  # Placeholder for catalog embeddings
        self.catalog_csv_file = catalog_csv_file
        self.models_dir = models_dir
        self.outputs_dir = outputs_dir
        self.transcripts_dir = transcripts_dir
        self.frames_dir = frames_dir
        self.vibes_list_file = vibes_list_file
        self.logger = logger

    def run(self):

        video_dict = self.video_item.dict() if hasattr(self.video_item, "dict") else self.video_item
        video_url = video_dict.get("videoUrl")
        hashtags = video_dict.get("hashtags")
        caption = video_dict.get("caption")
        self.logger.info(f"Starting pipeline for video: {video_url}")
        try:
            # Download video
            video_id = os.path.splitext(os.path.basename(video_url))[0]
            video_capture, tmp_video_file = download_video(video_url)
            
            if not video_capture.isOpened():
                raise Exception("Failed to open video capture from downloaded bytes.")

            # Transcribe audio
            transcript_path = transcribe_audio(tmp_video_file, video_id, self.transcripts_dir, self.model_size)
            
            # Extract frames
            extract_frames(video_id, video_capture, self.frames_dir, self.frame_rate)

            # Generate catalog embeddings
            catalog_csv = pd.read_csv(self.catalog_csv_file)
            if not (file_exists(self.catalog_embeddings_file) and file_exists(self.catalog_product_ids_file)):
                self.logger.warning("Required catalog files not found. Generating catalog embeddings...")
                extract_and_save_catalog_embeddings(catalog_csv, self.models_dir, self.clip_model)

            catalog_embeddings = np.load(self.catalog_embeddings_file)
            with open(self.catalog_product_ids_file, "r") as f:
                catalog_product_ids = json.load(f)
            
            # Vibe classification
            with open(self.vibes_list_file, 'r') as f:
                vibes_list = json.load(f)
            with open(transcript_path, 'r') as f:
                transcript_file = f.readlines()

            vibes = vibe_classification(hashtags, caption, transcript_file, groq_api_key='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', vibes_list=vibes_list)

            # Detect fashion items and match products
            frames_path = os.path.join(self.frames_dir, video_id)
            unique_matches = {}
            for frame_file in os.listdir(frames_path):
                if frame_file.endswith('.jpg'):
                    frame_filepath = os.path.join(frames_path, frame_file)
                    detections = detect_fashion_items(
                        frame_filepath,
                        self.yolo_model,
                        self.conf
                    )
                    for detection in detections:
                        matches = match_product(
                            detection,
                            frame_filepath,
                            catalog_embeddings,
                            catalog_product_ids,
                            catalog_csv,
                            self.clip_model,
                            top_k=1
                        )
                        for match in matches:
                            pid = match["matched_product_id"]
                            # Keep only the highest confidence match for each product
                            if (pid not in unique_matches) or (match["confidence"] > unique_matches[pid]["confidence"]):
                                unique_matches[pid] = match

            output_dict = {
                "video_id": video_id,
                "vibes": vibes,
                "products": list(unique_matches.values())
            }
            # Save unique matches as a list
            output_path = os.path.join(self.outputs_dir, f"{video_id}.json")
            with open(output_path, "w") as f:
                json.dump(output_dict, f, indent=2)
            self.logger.info(f"Saved unique matched products to {output_path}")

        except Exception as e:
            self.logger.error(f'Pipeline failed with an error: {e}', exc_info=True)
            raise
        self.logger.info("Pipeline completed successfully.")
        

def run_pipeline(video_item):
    """
    Run the Flickd pipeline for a given video item.
    Args:
        video_item (request.body): The video with videoUrl, hashtags, captions from the frontend.
    """

    if not directory_exists(OUTPUTS_DIR):
        os.makedirs(OUTPUTS_DIR)
    if not directory_exists(FRAMES_DIR):
        os.makedirs(FRAMES_DIR)
    if not directory_exists(TRANSCRIPTS_DIR):
        os.makedirs(TRANSCRIPTS_DIR)
    if not directory_exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    pipeline = FlickdPipeline(
        video_item,
        frame_rate=1,
        conf=0.3,
        model_size="small",
        yolo_model=YOLO_MODEL_PATH,
        clip_model=CLIP_MODEL_NAME,
        catalog_embeddings_file=CATALOG_EMBEDDINGS_PATH,
        catalog_product_ids_file=CATALOG_PRODUCT_IDS_PATH,
        catalog_csv_file=CATALOG_CSV_PATH,
        models_dir = MODELS_DIR,
        outputs_dir = OUTPUTS_DIR,
        frames_dir=FRAMES_DIR,
        transcripts_dir=TRANSCRIPTS_DIR,
        vibes_list_file = VIBES_LIST_PATH
        )
    
    pipeline.run()