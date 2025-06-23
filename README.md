![image](https://github.com/user-attachments/assets/2d9dd34e-eeb2-45e2-a395-5a81d1b46f6f)
![image](https://github.com/user-attachments/assets/925a936d-8f2e-49c1-895c-39a9c585323c)
![image](https://github.com/user-attachments/assets/d96de54b-ce63-4f37-800d-d8da97e4f7cd)


# Audio Processor - Phase 1

This directory contains the Python-based audio processing component for the YouTube to Guitar Tablature project.

## Phase 1: Audio Extraction & Basic Pitch Detection

### Overview

Phase 1 focuses on the core functionality of extracting audio from YouTube videos and performing basic pitch analysis. This serves as the foundation for the more advanced transcription features in later phases.

### Features

- **YouTube Audio Extraction**: Download and extract audio from YouTube URLs using `yt-dlp`
- **Basic Audio Analysis**: Analyze audio properties (duration, sample rate, amplitude)
- **Simple Pitch Estimation**: Basic frequency domain analysis for pitch detection
- **REST API Service**: Flask-based web service for integration with Java backend

### Prerequisites

#### System Requirements

- Python 3.8+ (Python 3.11 recommended for full functionality)
- FFmpeg (required by yt-dlp for audio extraction)
- Windows Long Path Support (for TensorFlow installation in later phases)

#### Python Version Compatibility

**Important**: There are compatibility issues with Python 3.13 and the `pydub` library. We provide two versions:

1. **Full Version** (`audio_extractor.py`): Requires Python 3.11 with full audio analysis capabilities
2. **Simplified Version** (`audio_extractor_simple.py`): Works with Python 3.13 but provides simulated pitch data

#### Python Dependencies

**For Python 3.11 (Full Version):**

```bash
pip install yt-dlp pydub Flask numpy
```

**For Python 3.13 (Simplified Version):**

```bash
pip install yt-dlp Flask numpy
```

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### Installation

1. **Clone or navigate to this directory**
2. **Choose your Python version**:
   - **Python 3.11**: Use full version with complete audio analysis
   - **Python 3.13**: Use simplified version with simulated data
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Install FFmpeg** (if not already installed):
   - Windows: Download from https://ffmpeg.org/download.html
   - Or use package managers like Chocolatey: `choco install ffmpeg`

### Usage

#### Command Line Interface

**Full Version (Python 3.11):**

```bash
python audio_extractor.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1"
```

**Simplified Version (Python 3.13):**

```bash
python audio_extractor_simple.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1"
```

This will:

1. Extract audio from the YouTube video
2. Perform basic audio analysis
3. Generate pitch estimates (real or simulated)
4. Save results to `temp_audio/analysis_results.json`

#### Web Service

Start the Flask web service:

```bash
python app.py
```

The service will be available at `http://localhost:5000`

**Available Endpoints:**

- `GET /health` - Health check
- `POST /extract-audio` - Extract and analyze audio from YouTube
- `POST /analyze-audio` - Analyze existing audio file
- `POST /cleanup` - Clean up temporary files

**Example API Usage:**

```bash
# Extract audio from YouTube
curl -X POST http://localhost:5000/extract-audio \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

# Analyze existing audio file
curl -X POST http://localhost:5000/analyze-audio \
  -H "Content-Type: application/json" \
  -d '{"audio_file_path": "/path/to/audio.wav"}'
```

### Output Format

The analysis produces JSON output with the following structure:

```json
{
  "success": true,
  "audio_file": "/path/to/extracted/audio.wav",
  "analysis": {
    "file_path": "/path/to/audio.wav",
    "duration_seconds": 180.5,
    "sample_rate": 44100,
    "channels": 2,
    "max_amplitude": 32767,
    "rms_amplitude": 2048.5,
    "total_samples": 7960050
  },
  "pitch_estimates": [
    {
      "start_time": 0.0,
      "end_time": 1.0,
      "estimated_frequency": 440.0,
      "confidence": 0.85,
      "note": "A4"
    }
  ],
  "timestamp": "2024-01-01T12:00:00"
}
```

### Version Differences

| Feature         | Full Version (Python 3.11)        | Simplified Version (Python 3.13)  |
| --------------- | --------------------------------- | --------------------------------- |
| Audio Analysis  | Real audio processing with pydub  | File size and duration estimation |
| Pitch Detection | FFT-based frequency analysis      | Simulated guitar frequencies      |
| Note Mapping    | Real frequency-to-note conversion | Basic note name generation        |
| Dependencies    | yt-dlp, pydub, Flask, numpy       | yt-dlp, Flask, numpy              |
| Accuracy        | High (real analysis)              | Low (simulated data)              |

### Limitations (Phase 1)

This phase implements a simplified approach with the following limitations:

1. **Basic Pitch Detection**: Uses simple FFT-based frequency analysis (or simulation)
2. **Limited Note Mapping**: Basic frequency-to-note conversion
3. **No Polyphony Support**: Only detects the strongest frequency per segment
4. **No Guitar-Specific Logic**: Generic audio analysis, not guitar-focused
5. **No Tablature Generation**: Only provides raw frequency data

### Next Steps (Phase 2)

Phase 2 will focus on:

- **Single-Note Tablature**: Map frequencies to guitar notes
- **Improved Pitch Detection**: More sophisticated algorithms
- **Note Duration Detection**: Better onset and offset detection
- **Basic Tablature Format**: Generate simple guitar tab strings


#### Debug Mode

Run the Flask app in debug mode for detailed error messages:

```bash
python app.py
```

### File Structure

```
python-audio-processor/
├── audio_extractor.py         # Full version (Python 3.11)
├── audio_extractor_simple.py  # Simplified version (Python 3.13)
├── app.py                     # Flask web service
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── temp_audio/                # Temporary audio files (created at runtime)
```

### Integration with Java Backend

The Flask service is designed to be called by the Java Spring Boot backend. The Java application should:

1. Make HTTP requests to the Flask endpoints
2. Handle JSON responses
3. Process the pitch estimates for tablature generation
4. Manage the audio processing workflow

Example Java integration will be provided in the main project documentation.

### Testing

Test the installation:

```bash
# Test core dependencies
python -c "import yt_dlp, numpy; print('Core dependencies working!')"

# Test full version (Python 3.11 only)
python -c "import yt_dlp, pydub, numpy; print('Full version ready!')"

# Test simplified version (Python 3.13 compatible)
python -c "import yt_dlp, numpy; print('Simplified version ready!')"
```
