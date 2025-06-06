import os
import json
from utils.logger import get_logger
from src.extract_frames import extract_frames
from src.transcribe import transcribe_audio
from src.detect import detect_fashion_items
from src.match import match_products
from utils.crop import crop_to_pil
from backend.config import VIDEOS_DIR, TRANSCRIPTS_DIR, DETECTIONS_DIR, YOLO_MODEL_PATH, FRAMES_DIR, OUTPUTS_DIR, CROPS_DIR


logger = get_logger(__name__)

class FlickdPipeline:
    def __init__(self, videos_dir, frames_dir, transcripts_dir, detections_dir, crops_dir, outputs_dir, yolo_model_path="yolov8n.pt"):
        self.videos_dir = videos_dir
        self.frames_dir = frames_dir
        self.transcripts_dir = transcripts_dir
        self.detections_dir = detections_dir
        self.yolo_model_path = yolo_model_path
        self.crops_dir = crops_dir
        self.outputs_dir = outputs_dir
        self.logger = logger

    def extract_all_frames(self, frame_rate=1):
        os.makedirs(self.frames_dir, exist_ok=True)
        for video_file in os.listdir(self.videos_dir):
            if video_file.endswith(('.mp4', '.avi', '.mov')):
                video_path = os.path.join(self.videos_dir, video_file)
                self.logger.info(f"Processing video: {video_path}...")
                extract_frames(video_path, self.frames_dir, frame_rate=frame_rate)
                self.logger.info(f"Extracted frames from {video_path} to {self.frames_dir}.")

    def generate_all_transcripts(self, model_size):
        os.makedirs(self.transcripts_dir, exist_ok=True)
        for video_file in os.listdir(self.videos_dir):
            if video_file.endswith(('.mp4', '.avi', '.mov')):
                video_path = os.path.join(self.videos_dir, video_file)
                self.logger.info(f"Transcribing video: {video_path}...")
                transcribe_audio(video_path, self.transcripts_dir, model_size=model_size)

    def detect_all_fashion_items(self, conf=0.3):
        os.makedirs(self.detections_dir, exist_ok=True)
        for root, _, files in os.walk(self.frames_dir):
            for file in files:
                if file.endswith('.jpg'):
                    frame_path = os.path.join(root, file)
                    detections = detect_fashion_items(frame_path, yolo_model_path=self.yolo_model_path, conf=conf)
                    frame_name = os.path.splitext(file)[0]
                    video_name = os.path.basename(root)
                    save_dir = os.path.join(self.detections_dir, video_name)
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = os.path.join(save_dir, f"{frame_name}_detections.json")
                    with open(save_path, "w") as f:
                        json.dump(detections, f, indent=2)
                    self.logger.info(f"Saved detections for {frame_path} to {save_path}")

    def match_all_products(self, top_k=1):
        os.makedirs(self.crops_dir, exist_ok=True)
        os.makedirs(self.outputs_dir, exist_ok=True)
        match_product = match_products
        # Group matches by video_name (reel)
        reel_matches = {}
        for root, _, files in os.walk(self.detections_dir):
            for file in files:
                if file.endswith("_detections.json"):
                    detection_path = os.path.join(root, file)
                    with open(detection_path, "r") as f:
                        detections = json.load(f)
                    frame_name = file.replace("_detections.json", ".jpg")
                    video_name = os.path.basename(root)
                    frame_path = os.path.join(self.frames_dir, video_name, frame_name)
                    if not os.path.exists(frame_path):
                        self.logger.warning(f"Frame image not found: {frame_path}")
                        continue
                    for idx, det in enumerate(detections):
                        bbox = det["bbox"]
                        # In-memory crop
                        crop = crop_to_pil(frame_path, bbox)
                        matches = match_product(crop, top_k=top_k, is_url=False)
                        # Add to reel_matches
                        if video_name not in reel_matches:
                            reel_matches[video_name] = []
                        reel_matches[video_name].append({
                            "frame": frame_name,
                            "detection_idx": idx,
                            "bbox": bbox,
                            "matches": matches
                        })
        # Save one .json per reel, only unique product matches (by matched_product_id), keep max confidence
        for video_name, matches_list in reel_matches.items():
            unique_products = {}
            for det in matches_list:
                for match in det["matches"]:
                    pid = match["matched_product_id"]
                    conf = match["confidence"]
                    if pid not in unique_products or conf > unique_products[pid]["confidence"]:
                        # Attach detection/frame info to the highest confidence occurrence
                        unique_products[pid] = {
                            "frame": det["frame"],
                            **match
                        }
            # Save only unique product matches for this reel (max confidence)
            match_save_path = os.path.join(self.outputs_dir, f"{video_name}.json")
            if unique_products:
                with open(match_save_path, "w") as mf:
                    json.dump(list(unique_products.values()), mf, indent=2)
            else:
                with open(match_save_path, "w") as mf:
                    json.dump([], mf)
            self.logger.info(f"Saved all unique (max confidence) matches for reel {video_name} to {match_save_path}")

    def run(self):
        self.logger.info("Flickd pipeline started.")
        try:
            # self.extract_all_frames(frame_rate=1)
            # self.logger.info("Frame extraction completed successfully.")
            # self.generate_all_transcripts(model_size='small')
            # self.logger.info("Transcript generation completed successfully.")
            # self.detect_all_fashion_items(conf=0.3)
            # self.logger.info("Fashion items detection completed successfully.")
            self.match_all_products(top_k=1)
            self.logger.info("Product matching completed successfully.")
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise
        self.logger.info("Flickd pipeline finished.")

if __name__ == "__main__":

    pipeline = FlickdPipeline(
        videos_dir=VIDEOS_DIR,
        frames_dir=FRAMES_DIR,
        transcripts_dir=TRANSCRIPTS_DIR,
        detections_dir=DETECTIONS_DIR, 
        yolo_model_path=YOLO_MODEL_PATH,
        crops_dir=CROPS_DIR,
        outputs_dir=OUTPUTS_DIR
        )
    pipeline.run()