import os
import re
from ultralytics import YOLO
from utils.logger import get_logger

logger = get_logger(__name__)

def detect_fashion_items(frame_path, yolo_model_path="yolov8n.pt", conf=0.3):
    """
    Detects fashion items in a single video frame using a YOLOv8 model.

    Args:
        frame_path (str): Path to the video frame image (JPEG/PNG).
        yolo_model_path (str, optional): Path to the YOLOv8 model weights file. Defaults to "yolov8n.pt".
        conf (float, optional): Confidence threshold for detections. Defaults to 0.3.

    Returns:
        list[dict]: List of detections, each as a dict with keys:
            - class_name (str): Name of the detected class.
            - bbox (list[int]): Bounding box as [x, y, w, h].
            - confidence (float): Detection confidence score.
            - frame_number (int): Frame number parsed from filename, or -1 if not found.

    Logs detection progress and errors. Returns an empty list if detection fails.
    """

    logger.info(f"Detecting fashion items in frame: {frame_path} with model: {yolo_model_path}...")

    match = re.search(r'frame_(\d+)', os.path.basename(frame_path))
    frame_number = int(match.group(1)) if match else -1
    
    try:
        model = YOLO(yolo_model_path)
        results = model.predict(frame_path, save=True, conf=conf)
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                w, h = x2 - x1, y2 - y1
                conf_score = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = model.names[class_id] if hasattr(model, "names") else str(class_id)
                detections.append({
                    "class_name": class_name,
                    "bbox": [x1, y1, w, h],
                    "confidence": conf_score,
                    "frame_number": frame_number
                })
        logger.info(f"Detected {len(boxes)} items in frame {frame_number}.")
        return detections
    except Exception as e:
        logger.error(f"Detection failed for frame {frame_path}: {e}", exc_info=True)
        return []