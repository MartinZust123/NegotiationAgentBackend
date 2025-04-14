# Negotiation Agent Backend

A Flask-based backend system for analyzing negotiation conversations and providing strategic advice to improve negotiation outcomes.

## Features

- Upload and process video/audio recordings of negotiations
- Transcribe speech to text using OpenAI's Whisper API
- Analyze conversations to build psychological profiles of participants
- Generate concise, actionable negotiation advice powered by GPT-4o
- Extract personality traits, goals, beliefs, and emotional states

## Requirements

- Python 3.8+
- FFmpeg (for audio/video processing)
- OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd NegotiationAgentBackend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file and add your OpenAI API key.

4. Make sure FFmpeg is installed on your system:
   - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - On Mac: `brew install ffmpeg`
   - On Linux: `sudo apt install ffmpeg`

5. Create required directories (these will be created automatically if they don't exist):
   ```
   mkdir -p uploads videos audios
   ```

## Usage

1. Start the server:
   ```
   python app.py
   ```
   The server will run on http://localhost:5000 by default.

## API Endpoints

### Upload Video
- **URL**: `/saveVideo`
- **Method**: `POST`
- **Data**: Form data with a `video` field containing the video file
- **Response**: JSON with a success message or error
- **Description**: Uploads a negotiation video and extracts its audio

### Transcribe Audio
- **URL**: `/transcribe`
- **Method**: `POST`
- **Data**: Form data with an `audio` field containing the audio file
- **Response**: JSON with transcribed text or error
- **Description**: Transcribes an entire audio file

### Transcribe Segment
- **URL**: `/transcribeSegment`
- **Method**: `POST`
- **Data**: JSON with `start` and `end` time in seconds
- **Response**: JSON with transcribed text for the segment or error
- **Description**: Transcribes a specific segment of the audio file

### Generate World Model
- **URL**: `/generateWorldModel`
- **Method**: `POST`
- **Data**:
  ```json
  {
    "speaker": "Speaker name",
    "segments": ["segment1", "segment2", ...]
  }
  ```
- **Response**: JSON world model with character traits, goals, etc.
- **Description**: Generates a psychological profile of the specified speaker

### Get Negotiation Advice
- **URL**: `/give-advice`
- **Method**: `POST`
- **Data**:
  ```json
  {
    "speaker": "Speaker name",
    "goals": ["goal1", "goal2", ...],
    "world_model": {/*world model JSON*/},
    "segments": ["segment1", "segment2", ...]
  }
  ```
- **Response**: JSON with concise negotiation advice
- **Description**: Provides actionable advice to help achieve negotiation goals

## Project Structure

- `app.py`: Main Flask application with API endpoints
- `worldModel.py`: Functions for generating psychological profiles and advice
- `audioTranscription.py`: Audio transcription using OpenAI's Whisper API
- `videoEditing.py`: Audio extraction from video recordings

## License

[Add license information here]

## Contributing

[Add contribution guidelines here] 