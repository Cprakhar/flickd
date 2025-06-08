from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import main_pipeline
import os
import json
import time
from config import OUTPUTS_DIR, VIDEOS_DIR
from utils.cache import is_expired, delete_path, CACHE_EXPIRY_SECONDS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# --- Models for request/response ---
class RecommendationRequest(BaseModel):
    videoUrl: str
    caption: str = None
    hashtags: list[str] = None

@app.post("/api/recommendations")
def recommend(req: RecommendationRequest, background_tasks: BackgroundTasks):
    # Extract video_id from videoUrl (assuming it's like .../reel_001.mp4)
    video_id = os.path.splitext(os.path.basename(req.videoUrl))[0]
    # Use backend/outputs as the outputs directory
    output_path = os.path.join(OUTPUTS_DIR, f"{video_id}.json")
    status_path = os.path.join(OUTPUTS_DIR, f"{video_id}.status")
    frames_path = os.path.join("../data/frames", video_id)
    transcript_path = os.path.join("../data/transcripts", f"{video_id}_transcript.txt")

    # Check and expire cache if needed
    expired = False
    for path in [output_path, frames_path, transcript_path]:
        if is_expired(path):
            delete_path(path)
            expired = True
    # Also delete status file if output is expired
    if expired and os.path.exists(status_path):
        os.remove(status_path)

    def run_and_track():
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

@app.get("/api/recommendations/status/{video_id}")
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

@app.get("/api/videos")
def get_videos():
    videos_dir = VIDEOS_DIR
    if not os.path.exists(videos_dir):
        return {"status": "success", "data": []}
    videos = []
    for fname in os.listdir(videos_dir):
        if fname.endswith(".mp4"):
            video_id = os.path.splitext(fname)[0]
            videos.append({
                "video_id": video_id,
                "video_url": f"/videos/{fname}"
            })
    return {"status": "success", "data": videos}

# Optionally, serve static files (videos, thumbnails) if needed
from fastapi.staticfiles import StaticFiles
app.mount("/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")
