import os
import whisper
from utils.logger import get_logger

logger = get_logger(__name__)

def transcribe_audio(video_path, output_dir, model_size="base"):
    """
    Extracts audio from video and generates transcript using Whisper.
    Saves transcript as a .txt file in output_dir/transcript_basename.txt

    Args:
        video_path (str): Path to the input video file.
        output_dir (str): Directory where transcript will be saved.
        model_size (str): Size of the Whisper model to use (e.g., "tiny", "base", "small", "medium", "large-v3").
    """

    model = whisper.load_model(model_size)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    os.makedirs(output_dir, exist_ok=True)
    transcript_path = os.path.join(output_dir, f"{video_name}_transcript.txt")

    try:
        logger.info(f"Transcribing audio from {video_path}...")
        result = model.transcribe(video_path, language="en", verbose=True)
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        logger.info(f"Transcript saved to {transcript_path}.")

        return transcript_path
    except Exception as e:
        logger.error(f"Failed to transcribe {video_path}: {e}", exc_info=True)
        return None
