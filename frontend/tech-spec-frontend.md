# Flickd AI Hackathon - Frontend Tech Spec

## Overview
Flickd is reimagining how Gen Z shops - through scroll-native, video-first, vibe-led
discovery. Our shopping journey doesn’t start at a search bar - it starts with a Reel. We
want to automate the tagging of products and the classification of fashion "vibes" from these
short videos. This hackathon invites AI/ML engineers to build the backbone of this intelligent
system.

## Objective
Build a fully working MVP (Minimum Viable Product) of Flickd’s "Smart Tagging & Vibe
Classification Engine." The engine should:
1. Extract frames from videos
2. Use a pretrained object detection model (YOLOv8) to identify fashion items
3. Match detected items to a small catalog of products using image embeddings (CLIP)
4. Analyze captions or transcripts to classify the video’s vibe using NLP
5. Output structured data via API or JSON


### What You’ll Build
1. Frontend UI to interact with the backend ML logic
2. Scrollable video feed to display videos
3. Recommendation button to trigger the ML engine
4. Display results in a sidebar which can be toggled on/off.
5. No sidebar before the recommendation button is clicked
6. Autoplay videos when they come into view
7. Infinite scroll to load more videos

### Tech Stack
1. Next.js for the frontend framework
2. Tailwind CSS for styling
3. IntersectionObserver to track video visibility
4. Axios for API requests
5. Client side video caching using DOM video element


## API Endpoints
1. `POST /api/recommendations`
   - **Description**: Trigger the ML engine to process a video and return recommendations.
   - **Request Body**:
     ```json
     {
       "videoUrl": "https://example.com/video.mp4",
       "caption": "Summer vibes with this outfit!", // optional
       "hashtags": ["#summer", "#fashion"] // optional
     }
     ```
   - **Response**:
     ```json
     {
       "status": "success",
       "data": {
            "video_id": "reel_001",
            "vibes": ["Coquette", "Brunchcore"],
            "products": [
                {
                    "type": "top",
                    "color": "white",
                    "matched_product_id": "prod_002",
                    "match_type": "exact",
                    "confidence": 0.93
                },
                ...
                ]
            }
     }
     ```

2. `GET /api/videos`
   - **Description**: Fetch a list of videos to display in the feed.
   - **Response**:
     ```json
     {
       "status": "success",
       "data": [
         {
           "video_id": "reel_001",
           "video_url": "https://example.com/reel_001.mp4",
           "thumbnail_url": "https://example.com/reel_001_thumbnail.jpg"
         },
         ...
       ]
     }
     ```