import os
import whisper

# ====== SET YOUR FFMPEG BIN FOLDER PATH HERE ======
# Replace the path below with your actual extracted ffmpeg bin path
FFMPEG_BIN = r"C:\Users\AKANKSHA SINGH\Downloads\ffmpeg-8.1-essentials_build\ffmpeg-8.1-essentials_build\bin"

# Add ffmpeg bin to PATH for this Python process only (NO system PATH change)
os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ["PATH"]

# Load Whisper model once
model = whisper.load_model("base")

def transcribe_audio(audio_path):
    """
    Transcribe audio file using OpenAI Whisper
    """
    try:
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")