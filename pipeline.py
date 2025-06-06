import os
import json
from utils.logger import get_logger
from src.extract_frames import extract_frames
from src.transcribe import transcribe_audio
from src.detect import detect_fashion_items


class FlickdPipeline:
    def __init__(self, videos_dir, frames_dir, transcripts_dir, detections_dir, yolo_model_path="models/yolov8n-best.pt"):
        self.videos_dir = videos_dir
        self.frames_dir = frames_dir
        self.transcripts_dir = transcripts_dir
        self.detections_dir = detections_dir
        self.yolo_model_path = yolo_model_path
        self.logger = get_logger(os.path.basename(__file__))

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


    def run(self):
        self.logger.info("Flickd pipeline started.")
        try:
            # self.extract_all_frames(frame_rate=1)
            # self.logger.info("Frame extraction completed successfully.")
            # self.generate_all_transcripts(model_size='small')
            # self.logger.info("Transcript generation completed successfully.")
            self.detect_all_fashion_items(conf=0.3)
            self.logger.info("Fashion items detection completed successfully.")
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
        
        self.logger.info("Flickd pipeline finished.")

if __name__ == "__main__":

    pipeline = FlickdPipeline(
        videos_dir='data/videos',
        frames_dir='data/frames',
        transcripts_dir='data/transcripts',
        detections_dir='data/detections', 
        yolo_model_path="models/yolov8n-best.pt"
        )
    pipeline.run()