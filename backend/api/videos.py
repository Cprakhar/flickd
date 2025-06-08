from fastapi import APIRouter
from config import VIDEOS_DIR
import os

router = APIRouter()

@router.get("/api/videos")
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
