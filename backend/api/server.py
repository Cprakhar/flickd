from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import main_pipeline
import os
import json
from config import OUTPUTS_DIR, VIDEOS_DIR

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
def recommend(req: RecommendationRequest):
    # Extract video_id from videoUrl (assuming it's like .../reel_001.mp4)
    video_id = os.path.splitext(os.path.basename(req.videoUrl))[0]
    # Use backend/outputs as the outputs directory
    output_path = os.path.join(OUTPUTS_DIR, f"{video_id}.json")
    if not os.path.exists(output_path):
        main_pipeline.run_pipeline(req)
    with open(output_path) as f:
        data = json.load(f)
    return {"status": "success", "data": data}

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
