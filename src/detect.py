import os
import re
from ultralytics import YOLO
from utils.logger import get_logger

logger = get_logger(os.path.basename(__file__))

def detect_fashion_items(frame_path, yolo_model_path="models/yolov8n-best.pt", conf=0.3):
    """
    Detect fashion items in a given frame using a YOLOv11 model.
    Returns a list of detections: [{class_name, bbox (x, y, w, h), confidence, frame_number}]

    Args:
        frame_path (str): Path to the video frame image.
        model_path (str): Path to the YOLOv11 model weights.
        conf (float): Confidence threshold for detections.
    """

    match = re.search(r'frame_(\d+)', os.path.basename(frame_path))
    frame_number = int(match.group(1)) if match else -1
    
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