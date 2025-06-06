import os
import cv2
from utils.logger import get_logger

logger = get_logger(__name__)

def extract_frames(video_path, output_dir, frame_rate=1):
    """
    Extracts frames from a video at the specified frame rate (frames per second).
    Saves frames as JPEGs in output_dir/video_basename/.

    Args:
        video_path (str): Path to the input video file.
        output_dir (str): Directory where frames will be saved.
        frame_rate (int): Number of frames to extract per second.
    """
    

    logger.info(f"Extracting frames from {video_path} at {frame_rate} fps...")

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    save_dir = os.path.join(output_dir, video_name)
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Failed to open video file: {video_path}")
        return []
    
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

    logger.info(f"Extracted {len(frame_paths)} frames from {video_path} to {save_dir}.")
    return frame_paths

