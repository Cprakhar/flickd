from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import os
import json
import main_pipeline
from config import OUTPUTS_DIR
from utils.cache import is_expired, delete_path

router = APIRouter()

class RecommendationRequest(BaseModel):
    videoUrl: str
    caption: str = None
    hashtags: list[str] = None

@router.post("/api/recommendations")
def recommend(req: RecommendationRequest, background_tasks: BackgroundTasks):
    video_id = os.path.splitext(os.path.basename(req.videoUrl))[0]
    output_path = os.path.join(OUTPUTS_DIR, f"{video_id}.json")
    status_path = os.path.join(OUTPUTS_DIR, f"{video_id}.status")
    frames_path = os.path.join("../data/frames", video_id)
    transcript_path = os.path.join("../data/transcripts", f"{video_id}_transcript.txt")

    expired = False
    for path in [output_path, frames_path, transcript_path]:
        if is_expired(path):
            delete_path(path)
            expired = True
    if expired and os.path.exists(status_path):
        os.remove(status_path)

    def run_and_track():
        os.makedirs(OUTPUTS_DIR, exist_ok=True)  # Ensure output dir exists
        with open(status_path, "w") as f:
            f.write("running")
        try:
            main_pipeline.run_pipeline(req)
            with open(status_path, "w") as f:
                f.write("done")
        except Exception as e:
            with open(status_path, "w") as f:
                f.write(f"error: {str(e)}")

    if not os.path.exists(output_path):
        background_tasks.add_task(run_and_track)
        return {"status": "pending", "video_id": video_id}
    else:
        with open(output_path) as f:
            data = json.load(f)
        return {"status": "success", "data": data}

@router.get("/api/recommendations/status/{video_id}")
def get_recommendation_status(video_id: str):
    output_path = os.path.join(OUTPUTS_DIR, f"{video_id}.json")
    status_path = os.path.join(OUTPUTS_DIR, f"{video_id}.status")
    if os.path.exists(output_path):
        with open(output_path) as f:
            data = json.load(f)
        return {"status": "success", "data": data}
    elif os.path.exists(status_path):
        with open(status_path) as f:
            status = f.read()
        if status == "running":
            return {"status": "running"}
        elif status.startswith("error"):
            return {"status": "error", "message": status}
        else:
            return {"status": status}
    else:
        return {"status": "not_found"}
