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
from config import FRAMES_DIR, YOLO_MODEL_PATH, TRANSCRIPTS_DIR, CLIP_MODEL_NAME, CATALOG_EMBEDDINGS_PATH, CATALOG_PRODUCT_IDS_PATH, CATALOG_CSV_PATH, MODELS_DIR, OUTPUTS_DIR, VIBES_LIST_PATH, GROQ_API_KEY
from utils.checks import file_exists, directory_exists
from dataclasses import dataclass

logger = get_logger(__name__)

@dataclass
class PipelineConfig:
    frame_rate: int = 1
    conf: float = 0.3
    model_size: str = "small"
    yolo_model: str = YOLO_MODEL_PATH
    clip_model: str = CLIP_MODEL_NAME
    catalog_embeddings_file: str = CATALOG_EMBEDDINGS_PATH
    catalog_product_ids_file: str = CATALOG_PRODUCT_IDS_PATH
    catalog_csv_file: str = CATALOG_CSV_PATH
    models_dir: str = MODELS_DIR
    outputs_dir: str = OUTPUTS_DIR
    frames_dir: str = FRAMES_DIR
    transcripts_dir: str = TRANSCRIPTS_DIR
    vibes_list_file: str = VIBES_LIST_PATH

class FlickdPipeline:
    def __init__(self, video_item, config: PipelineConfig):
        self.video_item = video_item
        self.frame_rate = config.frame_rate
        self.conf = config.conf
        self.model_size = config.model_size
        self.yolo_model = config.yolo_model
        self.clip_model = config.clip_model
        self.catalog_embeddings_file = config.catalog_embeddings_file
        self.catalog_product_ids_file = config.catalog_product_ids_file
        self.catalog_csv_file = config.catalog_csv_file
        self.models_dir = config.models_dir
        self.outputs_dir = config.outputs_dir
        self.transcripts_dir = config.transcripts_dir
        self.frames_dir = config.frames_dir
        self.vibes_list_file = config.vibes_list_file
        self.logger = logger
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        """
        Ensures that all necessary directories for the pipeline exist.
        """
        for d in [self.outputs_dir, self.frames_dir, self.transcripts_dir, self.models_dir]:
            if not directory_exists(d):
                os.makedirs(d, exist_ok=True)
                self.logger.info(f"Created directory: {d}")

    def download_video_and_get_id(self, video_url):
        """
        Downloads the video and returns (video_id, video_capture, tmp_video_file).
        Raises an exception if download or opening fails.
        """
        video_id = os.path.splitext(os.path.basename(video_url))[0]
        video_capture, tmp_video_file = download_video(video_url)
        if not video_capture or not video_capture.isOpened():
            raise Exception("Failed to open video capture from downloaded bytes.")
        return video_id, video_capture, tmp_video_file

    def transcribe_audio(self, tmp_video_file, video_id):
        """
        Transcribes audio from the video file and returns the transcript path.
        Raises an exception if transcription fails.
        """
        return transcribe_audio(tmp_video_file, video_id, self.transcripts_dir, self.model_size)

    def extract_frames(self, video_id, video_capture):
        """
        Extracts frames from the video and saves them to the frames directory.
        Raises an exception if extraction fails.
        """
        return extract_frames(video_id, video_capture, self.frames_dir, self.frame_rate)

    def prepare_catalog_embeddings(self):
        """
        Loads or generates catalog embeddings and product IDs as needed.
        Returns (catalog_embeddings, catalog_product_ids, catalog_csv).
        Raises an exception if loading or generation fails.
        """
        catalog_csv = pd.read_csv(self.catalog_csv_file)
        if not (file_exists(self.catalog_embeddings_file) and file_exists(self.catalog_product_ids_file)):
            self.logger.warning("Required catalog files not found. Generating catalog embeddings...")
            extract_and_save_catalog_embeddings(catalog_csv, self.models_dir, self.clip_model)
        catalog_embeddings = np.load(self.catalog_embeddings_file)
        with open(self.catalog_product_ids_file, "r") as f:
            catalog_product_ids = json.load(f)
        return catalog_embeddings, catalog_product_ids, catalog_csv

    def classify_vibes(self, hashtags, caption, transcript_file, vibes_list, detections=None):
        """
        Classifies vibes using the vibe_classification function, passing detections for empty-check logic.
        Returns a list of vibes.
        """
        return vibe_classification(
            hashtags,
            caption,
            transcript_file,
            vibes_list=vibes_list,
            groq_api_key=GROQ_API_KEY,
            detections=detections
        )

    def detect_and_match_products(self, frames_path, catalog_embeddings, catalog_product_ids, catalog_csv):
        """
        Detects fashion items in all frames and matches them to catalog products.
        Returns (unique_matches, all_detections).
        """
        unique_matches = {}
        all_detections = []
        for frame_file in os.listdir(frames_path):
            if frame_file.endswith('.jpg'):
                frame_filepath = os.path.join(frames_path, frame_file)
                detections = detect_fashion_items(
                    frame_filepath,
                    self.yolo_model,
                    self.conf
                )
                all_detections.extend(detections)
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
        return unique_matches, all_detections

    def save_output(self, video_id, vibes, unique_matches):
        """
        Saves the output dictionary as a JSON file in the outputs directory.
        Logs the save location.
        """
        output_dict = {
            "video_id": video_id,
            "vibes": vibes,
            "products": list(unique_matches.values())
        }
        output_path = os.path.join(self.outputs_dir, f"{video_id}.json")
        with open(output_path, "w") as f:
            json.dump(output_dict, f, indent=2)
        self.logger.info(f"Saved unique matched products to {output_path}")
        return output_path

    def run(self):

        video_dict = self.video_item.dict() if hasattr(self.video_item, "dict") else self.video_item
        video_url = video_dict.get("videoUrl")
        hashtags = video_dict.get("hashtags")
        caption = video_dict.get("caption")
        self.logger.info(f"Starting pipeline for video: {video_url}")
        try:
            # Download video (modularized)
            video_id, video_capture, tmp_video_file = self.download_video_and_get_id(video_url)
            # Transcribe audio (modularized)
            transcript_path = self.transcribe_audio(tmp_video_file, video_id)
            # Extract frames (modularized)
            self.extract_frames(video_id, video_capture)
            # Prepare catalog embeddings (modularized)
            catalog_embeddings, catalog_product_ids, catalog_csv = self.prepare_catalog_embeddings()

            # Vibe classification (modularized)
            with open(self.vibes_list_file, 'r') as f:
                vibes_list = json.load(f)
            with open(transcript_path, 'r') as f:
                transcript_file = f.readlines()

            # Detect fashion items and match products
            frames_path = os.path.join(self.frames_dir, video_id)
            unique_matches, all_detections = self.detect_and_match_products(
                frames_path, catalog_embeddings, catalog_product_ids, catalog_csv
            )
            vibes = self.classify_vibes(hashtags, caption, transcript_file, vibes_list, detections=all_detections)
            self.save_output(video_id, vibes, unique_matches)

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
    config = PipelineConfig()
    pipeline = FlickdPipeline(video_item, config)
    pipeline.run()