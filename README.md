# Flickd AI: Fashion Video Product & Vibe Recommendation Platform

## Overview
Flickd AI is a modular, production-ready platform for analyzing short-form fashion videos. It detects products using YOLOv8, matches them to a product catalog using CLIP+FAISS, and classifies video "vibes" using LLM (Groq AI) approaches. The backend is built with FastAPI and serves results to a modern Next.js frontend.

## Features
- **Video Frame Extraction**: Extracts frames from uploaded or linked videos.
- **Object Detection**: Uses YOLOv8 to detect fashion items in video frames.
- **Product Matching**: Matches detected items to a product catalog using CLIP embeddings and FAISS similarity search.
- **Vibe Classification**: Classifies the "vibe" of a video using LLM (Groq AI) for nuanced understanding.
- **FastAPI Backend**: Serves precomputed recommendations and product metadata, with robust logging and error handling.
- **Next.js Frontend**: Dynamic video feed, product recommendations, and responsive UI.
- **Docker-ready & Cloud Deployable**: Easily containerized and deployable to platforms like Google Cloud Run.

## Project Structure
```
backend/
  api/            # FastAPI server and endpoints
  components/     # Modular pipeline components (detect, match, vibe, etc.)
  data/           # Videos, catalog, vibes list, transcripts, frames
  models/         # Model weights and catalog embeddings
  outputs/        # Precomputed pipeline results (JSON)
  runs/           # Detected fashion items from video frames
  utils/          # Utility scripts (logger, download, etc.)
  main_pipeline.py
  config.py
frontend/
  app/            # Next.js app and API proxy
  components/     # React UI components
  lib/            # TypeScript types and utilities
  public/         # Static assets
```

## How It Works
1. **Upload or select a video** via the frontend.
2. **Backend pipeline** extracts frames, detects products, matches to catalog, and classifies vibes.
3. **Results** (products, vibes) are saved as JSON and served via API.
4. **Frontend** fetches and displays recommendations and product images dynamically.

## API Example
- **POST `/api/recommendations`**
  ```json
  {
    "videoUrl": "http://localhost:8000/videos/reel_003.mp4",
    "caption": "A fun night out with a glam look!",
    "hashtags": ["#Y2K", "#partyglam"]
  }
  ```
  **Response:**
  ```json
  {
    "video_id": "reel_003",
    "vibes": ["Coquette", "Party Glam"],
    "products": [
      {
        "type": "dress",
        "color": "black",
        "match_type": "similar",
        "matched_product_id": "prod_456",
        "confidence": 0.84,
        "image_url": "https://cdn_shopify.com/s/files/1/1234/5678/products/dress_black.jpg?v=1234567890",
      }
    ]
  }
  ```

## Setup & Run
### Backend
1. `cd backend`
2. `pip install -r ../requirements.txt`
3. `uvicorn api.server:app`

### Frontend
1. `cd frontend`
2. `pnpm install` (or `npm install`)
3. `pnpm dev` (or `npm run dev`)

### Docker (recommended for local/prototyping)
- See `Dockerfile` and use Docker Compose for local development or prototyping.

## Docker & Local Development

### Local Development with Docker Compose
1. Create `.env` files in root folder as needed.
2. From the project root, run:
   ```bash
   docker-compose up --build
   ```
3. Access the backend at [http://localhost:8080](http://localhost:8080) and the frontend at [http://localhost:3000](http://localhost:3000).

### Google Cloud Run Deployment (optional)
- Build and push Docker images for backend and frontend to Google Artifact Registry.
- Deploy each image to Cloud Run as a separate service.
- Set environment variables in the Cloud Run dashboard.
- For persistent storage, use Google Cloud Storage (GCS) buckets if needed.

## HuggingFace Model Caching for Fast Docker Startup
To avoid repeated downloads and speed up container startup, pre-download required HuggingFace models and copy them into the Docker build context:

1. **Pre-download models locally:**
   ```bash
   # For vibe classification (facebook/bart-large-mnli)
   python -c "from transformers import pipeline; pipeline('zero-shot-classification', model='facebook/bart-large-mnli')"

   # For product matching (openai/clip-vit-large-patch14)
   python -c "from transformers import CLIPProcessor, CLIPModel; CLIPModel.from_pretrained('openai/clip-vit-large-patch14'); CLIPProcessor.from_pretrained('openai/clip-vit-large-patch14')"
   ```
   This will cache models in `~/.cache/huggingface/hub` by default.

2. **Copy cached models into your project:**
   ```bash
   mkdir -p backend/models/hf_cache
   cp -r ~/.cache/huggingface/hub/models--facebook--bart-large-mnli backend/models/hf_cache/
   cp -r ~/.cache/huggingface/hub/models--openai--clip-vit-large-patch14 backend/models/hf_cache/
   ```

3. **Dockerfile setup:**
   The backend Dockerfile copies `backend/models/hf_cache` to `/root/.cache/huggingface/hub` and sets the `TRANSFORMERS_CACHE` environment variable. No code changes are needed.

4. **Result:**
   On container startup, the backend will use the cached models and will not re-download them, ensuring fast and reliable startup for both local and cloud deployments.

## Environment Variables
- `GROQ_API_KEY`: Your Groq LLM API key (backend)
- `NEXT_PUBLIC_API_URL`: The backend API URL (frontend)

## Notes
- For production, restrict CORS origins in the backend to your deployed frontend URL.
- For persistent data on cloud platforms, use cloud storage (e.g., GCS, AWS S3) instead of local disk.
- For local development, all data is stored in the backend/data, backend/outputs, and backend/models folders.
- **Planned:** Deployment will be on Google Cloud Run, with Google Cloud Storage (GCS) buckets used for persistent storage.
- **Planned:** The codebase will be updated to support GPU-based inference for improved performance on supported cloud infrastructure.

---

**Flickd AI** is a hackathon project and a foundation for scalable, production-grade video recommendation systems in fashion and beyond.
