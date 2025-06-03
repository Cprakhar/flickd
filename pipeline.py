import os
from utils.logger import get_logger
from src.extract_frames import extract_frames

class FlickdPipeline:
    def __init__(self, videos_dir, frames_dir):
        self.videos_dir = videos_dir
        self.frames_dir = frames_dir
        self.logger = get_logger(os.path.basename(__file__))

    def extract_all_frames(self, frame_rate=1):
        os.makedirs(self.frames_dir, exist_ok=True)
        for video_file in os.listdir(self.videos_dir):
            if video_file.endswith(('.mp4', '.avi', '.mov')):
                video_path = os.path.join(self.videos_dir, video_file)
                self.logger.info(f"Processing video: {video_path}...")
                extract_frames(video_path, self.frames_dir, frame_rate=frame_rate)
                self.logger.info(f"Extracted frames from {video_path} to {self.frames_dir}.")

    def run(self):
        self.logger.info("Flickd pipeline started.")
        try:
            self.extract_all_frames(frame_rate=1)
            self.logger.info("Frame extraction completed successfully.")

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
        
        self.logger.info("Flickd pipeline finished.")

if __name__ == "__main__":
    pipeline = FlickdPipeline(videos_dir='data/videos', frames_dir='data/frames')
    pipeline.run()