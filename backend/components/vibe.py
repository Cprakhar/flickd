import requests
import ast
from utils.logger import get_logger

logger = get_logger(__name__)

def groq_llm_vibes(texts, groq_api_key, vibes_list):
    """
    Uses Groq AI API to classify vibes.
    """

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


    prompt = (
        "You are an AI that returns only a Python list.\n\n"
        "Given the following list of fashion vibes and their descriptions:\n"
        f"{', '.join(vibe_names)}\n\n"
        "And the following content (hashtags, captions, transcript):\n"
        f"{vibe_descriptions}\n\n"
        "-----\n"
        + "\n".join(texts) +
        "\n-----\n\n"
        "Identify and return the most relevant vibes from the list above. "
        "Return your response as a valid Python list of strings (max length == 3), containing only the matching vibes.\n\n"
        "Example output format:\n['Vibe2', 'Vibe2', 'Vibe3']"
        "Don't include any other text or explanations, just the list of vibes.\n\n"
        "Wrong output example:\n"
        """['Based on the content', "I would identify the most relevant vibes as:\n\n['Coquette'", "'Cottagecore'", "'Boho'", "'Party Glam']\n\nThese vibes match the language and aesthetic described in the content", 'which includes references to golden hour']\n"""
        "Explanation: This output is incorrect because it includes additional text and explanations, which are not allowed. The correct output should only be a list of vibes without any extra commentary.\n\n"
        "Correct output example:\n"
        "['Vibe2', 'Vibe2', 'Vibe3']\n"
        "This output is correct because it only contains the list of vibes without any additional text or explanations."
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

def vibe_classification(hashtags, caption, audio_transcript, vibes_list, groq_api_key=None):
    """
    Classifies vibes using Groq LLM-based approaches.
    Returns a unique list of vibes.
    """

    logger.info("Starting vibe classification...")
    texts = []
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

    # Groq LLM-based
    llm_vibes_list = []
    if groq_api_key:
        try:
            llm_vibes_list = groq_llm_vibes(texts, groq_api_key, vibes_list)
        except Exception as e:
            logger.error(f"Groq LLM vibe classification failed: {e}")

    logger.info(f"Vibes classified: {llm_vibes_list}")
    return list(llm_vibes_list)