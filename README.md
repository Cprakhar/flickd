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
- **Docker-ready & Cloud Deployable**: Easily containerized and deployable to platforms like Render.com.

## Project Structure
```
backend/
  api/            # FastAPI server and endpoints
  components/     # Modular pipeline components (detect, match, vibe, etc.)
  data/           # Videos, catalog, vibes list, transcripts, frames
  models/         # Model weights and catalog embeddings
  outputs/        # Precomputed pipeline results (JSON)
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
        "confidence": 0.84
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

### Docker (optional)
- See `Dockerfile` and deployment instructions for Render.com or your preferred platform.

## Technologies Used
- Python, FastAPI, YOLOv8, CLIP, FAISS, MoviePy, Groq AI (LLM), Next.js, React, Tailwind CSS, Docker
