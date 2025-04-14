from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from worldModel import generate_world_model
import os
import json
from werkzeug.utils import secure_filename
from audioTranscription import transcribeAudio
from pathlib import Path
from videoEditing import createAudio
import ffmpeg
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {  # Apply CORS to all endpoints
        "origins": "*",
        "methods": ["POST", "GET"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})

# Configure folders from environment variables
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

VIDEO_FOLDER = os.getenv('VIDEO_FOLDER', 'videos')
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)
app.config['VIDEO_FOLDER'] = VIDEO_FOLDER

AUDIO_FOLDER = os.getenv('AUDIO_FOLDER', 'audios')
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        # Check if audio file is in request
        if 'audio' not in request.files:
            return jsonify({'error': 'Missing audio file'}), 400
        
        audio_file = request.files['audio']
        
        # Save audio file temporarily
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(audio_file.filename))
        audio_file.save(audio_path)
        
        # Transcribe audio
        result = transcribeAudio(audio_path)
        
        # Clean up the temporary file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        # Check if transcription was successful
        if isinstance(result, dict):
            return jsonify({'text': result['text']})
        else:
            return jsonify({'error': result}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add new endpoint
@app.route('/saveVideo', methods=['POST'])
def save_video():
    try:
        # Check if video file is in request
        if 'video' not in request.files:
            return jsonify({'error': 'Missing video file'}), 400
        
        video_file = request.files['video']
        
        # Check if the file is actually a video file
        if not video_file.content_type.startswith('video/'):
            return jsonify({'error': 'File must be a video file'}), 400
        
        # Save video file
        video_path = os.path.join(app.config['VIDEO_FOLDER'], 'negotiation.mp4')
        video_file.save(video_path)
        
        # Extract audio from the video
        audio_result = createAudio()
        if audio_result is not True:
            return jsonify({'error': f'Video saved but audio extraction failed: {audio_result}'}), 500
        
        return jsonify({'message': 'Video saved and audio extracted successfully'}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcribeSegment', methods=['POST'])
def transcribe_segment():
    try:
        # Validate input JSON
        data = request.get_json()
        if not data or 'start' not in data or 'end' not in data:
            return jsonify({'error': 'Missing start or end time'}), 400
        
        start_time = float(data['start'])
        end_time = float(data['end'])
        
        if start_time >= end_time:
            return jsonify({'error': 'Start time must be less than end time'}), 400
        
        # Create temporary file for the segment
        temp_segment = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_segment_{int(time.time())}.mp3')
        
        try:
            # Extract segment using ffmpeg
            audio_path = os.path.join(app.config['AUDIO_FOLDER'], 'negotiation.mp3')
            stream = ffmpeg.input(audio_path, ss=start_time, t=end_time-start_time)
            stream = ffmpeg.output(stream, temp_segment, acodec='copy')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # Transcribe the segment
            result = transcribeAudio(temp_segment)
            
            # Clean up temporary file
            if os.path.exists(temp_segment):
                os.remove(temp_segment)
            
            # Return transcription result
            if isinstance(result, dict):
                return jsonify({'text': result['text']})
            else:
                return jsonify({'error': result}), 500
                
        finally:
            # Ensure temporary file is cleaned up even if an error occurs
            if os.path.exists(temp_segment):
                os.remove(temp_segment)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def generateDialogue(list_of_segments):
    dialogue = ""
    for i in range(len(list_of_segments)):
        if (i % 2 == 1):
            dialogue += ("Speaker 1: \n" + list_of_segments[i] + "\n \n")
        else:
            dialogue += ("Speaker 2: \n" + list_of_segments[i] + "\n \n")
    return dialogue

@app.route('/generateWorldModel', methods=['POST'])
def generateWorldModel():
    try: 
        data = request.get_json()
        speaker = data["speaker"]
        conversation = generateDialogue(data["segments"])
        world_model = generate_world_model(speaker, conversation)
        return world_model
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/give-advice', methods=['POST'])
def give_advice():
    try: 
        print("=== GIVE ADVICE ENDPOINT CALLED ===")
        data = request.get_json()
        print(f"Received data: {json.dumps(data, indent=2)}")
        
        print("Generating dialogue from segments...")
        conversation = generateDialogue(data["segments"])
        print(f"Generated conversation: {conversation[:100]}...")  # Print first 100 chars
        
        print("Extracting goals...")
        goals = data["goals"]
        print(f"Goals: {goals}")
        
        print("Extracting world model...")
        # This is a world model of the other person that we are negotiating with
        world_model = data["world_model"]
        print(f"World model: {json.dumps(world_model, indent=2)}")
        
        print("Extracting speaker...")
        speaker = data["speaker"]
        print(f"Speaker: {speaker}")
        
        print("Calling give_advice function from worldModel.py...")
        # This is the advice that we are giving to this person
        from worldModel import give_advice as get_advice_func
        advice = get_advice_func(world_model, goals, conversation, speaker)
        print(f"Generated advice: {advice[:100]}...")  # Print first 100 chars
        
        print("=== GIVE ADVICE ENDPOINT COMPLETED SUCCESSFULLY ===")
        return jsonify({"advice": advice})
    except Exception as e:
        print(f"=== ERROR IN GIVE ADVICE ENDPOINT: {str(e)} ===")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=debug_mode, port=port) 