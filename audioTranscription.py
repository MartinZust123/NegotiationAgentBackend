from openai import OpenAI
from typing import Dict, Union
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def transcribeAudio(audio_path: str) -> Union[Dict, str]:
    """
    Transcribes audio using OpenAI's Whisper API.
    
    Args:
        audio_path (str): Path to the audio file to transcribe
        
    Returns:
        Union[Dict, str]: Dictionary containing transcription results or error message string
        The dictionary contains:
        - text: Complete transcription
        - segments: List of dictionaries with segment-level info (timestamps, text)
    """
    try:
        # Initialize OpenAI client with API key from environment
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Open audio file
        with open(audio_path, "rb") as audio_file:
            # Transcribe using Whisper API
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",  # Get detailed response with timestamps
                timestamp_granularities=["segment"]
            )
        
        # Process the response
        return {
            "text": response.text,
            "segments": [
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                }
                for segment in response.segments
            ]
        }
        
    except Exception as e:
        return f"Error during transcription: {str(e)}"

if __name__ == "__main__":
    # Example usage
    audio_file = "sample.mp3"
    result = transcribeAudio(audio_file)
    if isinstance(result, dict):
        print("Full transcription:", result["text"])
        print("\nSegments:")
        for segment in result["segments"]:
            print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s]: {segment['text']}")
    else:
        print(result)
