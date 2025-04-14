import ffmpeg
import os
from typing import Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def createAudio(video_path: str = None, audio_path: str = None) -> Union[bool, str]:
    """
    Extracts audio from video file and saves it as MP3.
    
    Args:
        video_path (str): Path to the input video file
        audio_path (str): Path to save the output audio file
        
    Returns:
        Union[bool, str]: True if successful, error message string if failed
    """
    try:
        # Use environment variables if paths are not provided
        if video_path is None:
            video_folder = os.getenv('VIDEO_FOLDER', 'videos')
            video_path = os.path.join(video_folder, 'negotiation.mp4')
            
        if audio_path is None:
            audio_folder = os.getenv('AUDIO_FOLDER', 'audios')
            audio_path = os.path.join(audio_folder, 'negotiation.mp3')
        
        # Create audios directory if it doesn't exist
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        # Extract audio using ffmpeg
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(stream, audio_path, acodec='libmp3lame', ac=2, ar='44100')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return True
        
    except Exception as e:
        return f"Error extracting audio: {str(e)}"

