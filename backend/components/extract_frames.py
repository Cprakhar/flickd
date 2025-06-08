import os
import cv2
from utils.logger import get_logger

logger = get_logger(__name__)

def extract_frames(video_id, video_capture, output_dir, frame_rate=1):
    """
    Extracts frames from a video at the specified frame rate (frames per second).
    Saves frames as JPEGs in output_dir/<video_id>/.

    Args:
        video_id (str): Unique identifier for the video (used as output folder name).
        video_capture (cv2.VideoCapture): OpenCV VideoCapture object for the video.
        output_dir (str): Directory where extracted frames will be saved.
        frame_rate (int, optional): Number of frames to extract per second. Defaults to 1.

    Returns:
        list[str]: List of file paths to the extracted frame images.

    Logs extraction progress and errors. Returns an empty list if extraction fails.
    """
    try:
        logger.info(f"Extracting frames from {video_id} at {frame_rate} fps...")

        save_dir = os.path.join(output_dir, video_id)
        os.makedirs(save_dir, exist_ok=True)

        cap = video_capture
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps / frame_rate) if fps > 0 else 1

        frame_paths = []
        frame_idx = 0
        saved_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                frame_file = os.path.join(save_dir, f"frame_{saved_idx:04d}.jpg")
                cv2.imwrite(frame_file, frame)
                frame_paths.append(frame_file)
                saved_idx += 1
            frame_idx += 1

        cap.release()
        logger.info(f"Extracted {len(frame_paths)} frames from {video_id} to {save_dir}.")
        return frame_paths
    except Exception as e:
        logger.error(f"Frame extraction failed for video {video_id}: {e}", exc_info=True)
        return []

