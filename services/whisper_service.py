import whisper
import os
import tempfile
import subprocess

# Load the Whisper model once globally
model = whisper.load_model("base")  # You can change to "small", "medium", or "large"

def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe an audio file using Whisper.

    Args:
        audio_path (str): Path to a .wav or .mp3 file

    Returns:
        dict: Whisper's transcription result
    """
    try:
        result = model.transcribe(audio_path, word_timestamps=False, verbose=False)
        return result
    except Exception as e:
        print(f"[Whisper] Transcription failed: {e}")
        raise

def transcribe_video(video_path: str) -> dict:
    """
    Extracts audio from a video and transcribes it using Whisper.

    Args:
        video_path (str): Path to the .mp4 or .mkv video file

    Returns:
        dict: Whisper's transcription result
    """
    try:
        # Create a temporary .wav file to extract audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            audio_path = temp_audio.name

        # Use ffmpeg to extract mono 16kHz audio (preferred for Whisper)
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-ac", "1", "-ar", "16000",
            "-f", "wav", audio_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        result = transcribe_audio(audio_path)

        # Clean up
        os.remove(audio_path)
        return result

    except Exception as e:
        print(f"[Whisper] Failed to transcribe video: {e}")
        raise
