#!/usr/bin/env python3
"""
Flask web service for audio processing.
This provides REST API endpoints for the Java backend to call.
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from audio_extractor_simple import SimpleAudioExtractor
import os
import tempfile
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from tab_generator import generate_tab
import signal
import threading
from functools import wraps

app = Flask(__name__)

# Global extractor instance
extractor = SimpleAudioExtractor()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'temp_audio')
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'webm', 'ogg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')  # Use env var if available

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'audio-processor',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/extract-audio', methods=['POST'])
def extract_audio():
    """
    Extract audio from YouTube URL.
    
    Expected JSON payload:
    {
        "youtube_url": "https://www.youtube.com/watch?v=..."
    }
    """
    try:
        data = request.get_json()
        if not data or 'youtube_url' not in data:
            return jsonify({
                'error': 'Missing youtube_url in request body'
            }), 400
        
        youtube_url = data['youtube_url']
        
        # Extract audio
        audio_file = extractor.extract_audio_from_youtube(youtube_url)
        if not audio_file:
            return jsonify({
                'error': 'Failed to extract audio from YouTube URL'
            }), 500
        
        # Basic analysis
        analysis = extractor.get_audio_info(audio_file)
        if not analysis:
            return jsonify({
                'error': 'Failed to analyze audio'
            }), 500
        
        # Simple pitch estimation
        pitch_estimates = extractor.simulate_pitch_estimation(audio_file)
        
        # Prepare response
        response = {
            'success': True,
            'audio_file': audio_file,
            'analysis': analysis,
            'pitch_estimates': pitch_estimates,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/analyze-audio', methods=['POST'])
def analyze_audio():
    """
    Analyze an existing audio file.
    
    Expected JSON payload:
    {
        "audio_file_path": "/path/to/audio/file.wav"
    }
    """
    try:
        data = request.get_json()
        if not data or 'audio_file_path' not in data:
            return jsonify({
                'error': 'Missing audio_file_path in request body'
            }), 400
        
        audio_file_path = data['audio_file_path']
        
        if not os.path.exists(audio_file_path):
            return jsonify({
                'error': f'Audio file not found: {audio_file_path}'
            }), 404
        
        # Basic analysis
        analysis = extractor.get_audio_info(audio_file_path)
        if not analysis:
            return jsonify({
                'error': 'Failed to analyze audio'
            }), 500
        
        # Simple pitch estimation
        pitch_estimates = extractor.simulate_pitch_estimation(audio_file_path)
        
        # Prepare response
        response = {
            'success': True,
            'analysis': analysis,
            'pitch_estimates': pitch_estimates,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up temporary files."""
    try:
        extractor.cleanup()
        return jsonify({
            'success': True,
            'message': 'Temporary files cleaned up',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': f'Cleanup failed: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error'
    }), 500

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def target():
                return func(*args, **kwargs)
            
            result = [None]
            exception = [None]
            
            def worker():
                try:
                    result[0] = target()
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"Operation timed out after {seconds} seconds")
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
        return wrapper
    return decorator

@app.route('/extract', methods=['POST'])
def web_extract_audio():
    youtube_url = request.form.get('youtube_url')
    if not youtube_url:
        flash('Please provide a YouTube URL.', 'error')
        return redirect(url_for('index'))
    
    print(f"Processing YouTube URL: {youtube_url}")
    try:
        audio_file = extractor.extract_audio_from_youtube(youtube_url)
        if not audio_file:
            raise Exception('Failed to extract audio from YouTube URL')
        print("Analyzing audio...")
        analysis = extractor.get_audio_info(audio_file)
        print("Generating pitch estimates...")
        pitch_estimates = extractor.simulate_pitch_estimation(audio_file)
        print("Generating full sheet tab...")
        # Generate full sheet tab with measures and line breaks
        tab = generate_tab(pitch_estimates, notes_per_measure=8, measures_per_line=4)
        print("Processing complete!")
        return render_template('results.html', audio_file=audio_file, analysis=analysis, pitch_estimates=pitch_estimates, tab=tab)
    except Exception as e:
        flash(f'Error processing YouTube video: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/analyze', methods=['POST'])
def web_analyze_audio():
    if 'audio_file' not in request.files:
        flash('No file part.', 'error')
        return redirect(url_for('index'))
    file = request.files['audio_file']
    if file.filename == '':
        flash('No selected file.', 'error')
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        print(f"Analyzing uploaded file: {filename}")
        analysis = extractor.get_audio_info(file_path)
        print("Generating pitch estimates...")
        pitch_estimates = extractor.simulate_pitch_estimation(file_path)
        print("Generating full sheet tab...")
        # Generate full sheet tab with measures and line breaks
        tab = generate_tab(pitch_estimates, notes_per_measure=8, measures_per_line=4)
        print("Processing complete!")
        
        return render_template('results.html', audio_file=file_path, analysis=analysis, pitch_estimates=pitch_estimates, tab=tab)
    else:
        flash('Invalid file type.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Run the Flask app
    print("Starting Audio Processor Service...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /extract-audio - Extract and analyze audio from YouTube")
    print("  POST /analyze-audio - Analyze existing audio file")
    print("  POST /cleanup - Clean up temporary files")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 