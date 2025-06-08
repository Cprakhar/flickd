import os
import whisper
from utils.logger import get_logger
from moviepy import VideoFileClip
import tempfile

logger = get_logger(__name__)

def transcribe_audio(video_file: tempfile._TemporaryFileWrapper, video_id, output_dir, model_size="base") -> str:
    """
    Extracts audio from a video file and generates a transcript using Whisper.
    Saves transcript as a .txt file in output_dir/<video_id>_transcript.txt.

    Args:
        video_file (tempfile._TemporaryFileWrapper): Temporary file object for the input video.
        video_id (str): Unique identifier for the video (used for output filename).
        output_dir (str): Directory where the transcript will be saved.
        model_size (str, optional): Size of the Whisper model to use (e.g., "tiny", "base", "small", "medium", "large-v3"). Defaults to "base".

    Returns:
        str or None: Path to the transcript file if successful, None if transcription fails.

    Logs transcription progress and errors. Returns None if transcription fails.
    """
    try:
        model = whisper.load_model(model_size)
        os.makedirs(output_dir, exist_ok=True)
        transcript_path = os.path.join(output_dir, f"{video_id}_transcript.txt")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            logger.info(f"Transcribing audio from {video_id}...")
            clip = VideoFileClip(video_file.name)
            clip.audio.write_audiofile(temp_audio_file.name)
            temp_audio_file.flush()
            result = model.transcribe(temp_audio_file.name, language="en", verbose=False)
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            logger.info(f"Transcript saved to {transcript_path}.")
        os.remove(temp_audio_file.name)
        video_file.close()
        os.remove(video_file.name)
        return transcript_path
    except Exception as e:
        logger.error(f"Failed to transcribe {video_id}: {e}", exc_info=True)
        return None
