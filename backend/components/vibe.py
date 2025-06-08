import requests
import ast
import os
from utils.logger import get_logger

logger = get_logger(__name__)

def groq_llm_vibes(texts, groq_api_key, vibes_list):

    vibes_desc = [
        ("Coquette", "Feminine, flirty, often featuring bows, lace, soft makeup, and romantic details."),
        ("Clean Girl", "Minimalist and polished look with slicked-back hair, gold jewelry, and natural makeup."),
        ("Cottagecore", "Pastoral, vintage-inspired, with florals, prairie dresses, and an earthy aesthetic."),
        ("Streetcore", "Urban and edgy, with oversized fits, sneakers, graphic tees, and streetwear brands."),
        ("Y2K", "Early 2000s fashion with shiny fabrics, low-rise jeans, baby tees, and retro tech accessories."),
        ("Boho", "Bohemian and free-spirited with layered textures, fringe, earthy tones, and eclectic prints."),
        ("Party Glam", "Bold, sparkly, nightlife-ready fashion with statement pieces, heels, and dramatic makeup."),
    ]
    vibe_names = [name for name, desc in vibes_desc]
    vibe_descriptions = "\n".join([f"- **{name}**: {desc}" for name, desc in vibes_desc])

    # Load prompt template from file
    prompt_path = os.path.join(os.path.dirname(__file__), "vibe_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(
        vibe_names=", ".join(vibe_names),
        vibe_descriptions=vibe_descriptions,
        texts="\n".join(texts)
    )
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",  # or another Groq-supported model
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50,
        "temperature": 0.2,
    }
    response = requests.post(url, headers=headers, json=data)
    llm_vibes = []
    if response.ok:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        logger.info(f"Groq LLM response: {content}")
        try:
            llm_vibes = ast.literal_eval(content)
            if not isinstance(llm_vibes, list):
                llm_vibes = []
        except Exception as e:
            logger.error(f"Failed to parse LLM vibes: {e}")
            llm_vibes = []
        logger.info(f"LLM vibes extracted: {llm_vibes}")
    return [v.lower() for v in llm_vibes if v in vibes_list]

def vibe_classification(hashtags, caption, audio_transcript, vibes_list, groq_api_key=None, detections=None):
    """
    Classifies vibes for a video using Groq LLM-based approaches.
    If no objects are detected (detections is an empty list), returns an empty list.

    Args:
        hashtags (list[str] or str): List of hashtags or a single hashtag string.
        caption (str): Caption text for the video.
        audio_transcript (list[str] or str): Transcript of the video's audio, as a list of lines or a single string.
        vibes_list (list[str]): List of valid vibe names to match against.
        groq_api_key (str, optional): API key for Groq LLM. If not provided, LLM-based classification is skipped.
        detections (list, optional): List of detected objects for the video. If provided and empty, vibes will be empty.

    Returns:
        list[str]: List of classified vibes (strings). Returns an empty list if no objects are detected or if classification fails.

    Logs classification progress and errors. Returns an empty list if classification fails or no objects are detected.
    """

    logger.info("Starting vibe classification...")
    # If detections is provided and empty, return empty list
    if detections is not None and len(detections) == 0:
        logger.info("No objects detected for this video. Returning empty vibes list.")
        return []

    texts = []
    try:
        if hashtags:
            if isinstance(hashtags, list):
                texts.extend(hashtags)
            else:
                texts.append(hashtags)
        if caption:
            texts.append(caption)
        if audio_transcript:
            if isinstance(audio_transcript, list):
                texts.extend(audio_transcript)
            else:
                texts.append(audio_transcript)
    except Exception as e:
        logger.error(f"Error preparing input texts for vibe classification: {e}", exc_info=True)
        return []

    llm_vibes_list = []
    if groq_api_key:
        try:
            llm_vibes_list = groq_llm_vibes(texts, groq_api_key, vibes_list)
        except Exception as e:
            logger.error(f"Groq LLM vibe classification failed: {e}", exc_info=True)
            return []

    logger.info(f"Vibes classified: {llm_vibes_list}")
    return list(llm_vibes_list)