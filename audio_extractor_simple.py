#!/usr/bin/env python3
import os
import sys
import tempfile
import json
from typing import Dict, List, Optional, Tuple
import yt_dlp
import numpy as np

class SimpleAudioExtractor:
    """Handles YouTube audio extraction and basic pitch analysis."""
    
    def __init__(self, output_dir: str = "temp_audio"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def extract_audio_from_youtube(self, youtube_url: str) -> Optional[str]:
        try:
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extractaudio': False,
                'postprocessors': [], 
                'socket_timeout': 30,
                'retries': 3,
                'fragment_retries': 3,
                'max_sleep_interval': 5,
                'max_filesize': 100 * 1024 * 1024,
                'max_duration': 600,
            }
            
            print(f"Extracting audio from: {youtube_url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("Getting video info...")
                info = ydl.extract_info(youtube_url, download=False)
                
                duration = info.get('duration', 0)
                if duration > 600:
                    print(f"Video too long ({duration}s), skipping...")
                    return None
                
                video_title = info.get('title', 'unknown')
                print(f"Video title: {video_title}")
                print(f"Duration: {duration}s")
                
                print("Downloading audio...")
                ydl.download([youtube_url])
                
                possible_extensions = ['m4a', 'webm', 'mp3', 'wav', 'ogg']
                file_path = None
                
                for ext in possible_extensions:
                    expected_filename = f"{video_title}.{ext}"
                    test_path = os.path.join(self.output_dir, expected_filename)
                    if os.path.exists(test_path):
                        file_path = test_path
                        break
                
                if file_path:
                    print(f"Audio extracted successfully: {file_path}")
                    return file_path
                else:
                    print("Audio file not found after extraction")
                    print("Files in output directory:")
                    for file in os.listdir(self.output_dir):
                        print(f"  - {file}")
                    return None
                    
        except Exception as e:
            print(f"Error extracting audio: {str(e)}")
            if "Video unavailable" in str(e):
                print("This video is not available for download")
            elif "Private video" in str(e):
                print("This is a private video")
            elif "Age-restricted" in str(e):
                print("This video is age-restricted")
            elif "timeout" in str(e).lower():
                print("Download timed out - try a shorter video")
            return None
    
    def get_audio_info(self, audio_file_path: str) -> Dict:
        """
        Get basic information about an audio file using file size and duration estimation.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dictionary containing basic audio information
        """
        try:
            file_size = os.path.getsize(audio_file_path)
            
            file_ext = os.path.splitext(audio_file_path)[1].lower()
            
            if file_ext in ['.wav']:
                estimated_duration = file_size / (44100 * 2 * 2)
                estimated_sample_rate = 44100
                estimated_channels = 2
            elif file_ext in ['.m4a', '.mp4']:
                estimated_duration = file_size / (128 * 1024 / 8)  # 128 kbps
                estimated_sample_rate = 44100
                estimated_channels = 2
            elif file_ext in ['.mp3']:
                estimated_duration = file_size / (128 * 1024 / 8)  # 128 kbps
                estimated_sample_rate = 44100
                estimated_channels = 2
            elif file_ext in ['.webm']:
                estimated_duration = file_size / (128 * 1024 / 8)  # 128 kbps
                estimated_sample_rate = 44100
                estimated_channels = 2
            else:
                estimated_duration = file_size / (44100 * 2 * 2)
                estimated_sample_rate = 44100
                estimated_channels = 2
            
            analysis = {
                'file_path': audio_file_path,
                'file_size_bytes': file_size,
                'estimated_duration_seconds': estimated_duration,
                'estimated_sample_rate': estimated_sample_rate,
                'estimated_channels': estimated_channels,
                'format': file_ext[1:].upper() if file_ext else 'UNKNOWN'
            }
            
            print(f"Audio file analysis completed:")
            print(f"  File size: {file_size:,} bytes")
            print(f"  Estimated duration: {estimated_duration:.2f} seconds")
            print(f"  Format: {analysis['format']}")
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing audio file: {str(e)}")
            return {}
    
    def simulate_pitch_estimation(self, audio_file_path: str, segment_duration: float = 5.0) -> List[Dict]:
        """
        Simulate pitch estimation for demonstration purposes.
        In a real implementation, this would use proper audio analysis libraries.
        
        Args:
            audio_file_path: Path to the audio file
            segment_duration: Duration of each analysis segment in seconds (default: 5.0 for faster processing)
            
        Returns:
            List of simulated pitch estimates for each segment
        """
        try:
            file_info = self.get_audio_info(audio_file_path)
            total_duration = file_info.get('estimated_duration_seconds', 60.0)
            
            num_segments = min(int(total_duration / segment_duration), 50)
            pitch_estimates = []
            
            guitar_frequencies = [82.41, 110.00, 146.83, 196.00, 246.94, 329.63, 440.00, 659.25]
            
            for i in range(num_segments):
                start_time = i * segment_duration
                end_time = (i + 1) * segment_duration
                
                freq_idx = i % len(guitar_frequencies)
                frequency = guitar_frequencies[freq_idx]
                
                frequency += np.random.normal(0, 5)
                frequency = max(80, min(800, frequency))
                
                confidence = 0.7 + np.random.normal(0, 0.1)
                confidence = max(0.1, min(1.0, confidence))
                
                pitch_estimates.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'estimated_frequency': frequency,
                    'confidence': confidence,
                    'note': self.frequency_to_note(frequency)
                })
            
            print(f"Simulated pitch estimation completed: {len(pitch_estimates)} segments")
            return pitch_estimates
            
        except Exception as e:
            print(f"Error in pitch estimation: {str(e)}")
            return []
    
    def frequency_to_note(self, frequency: float) -> str:
        """
        Convert frequency to approximate note name.
        This is a simplified implementation.
        """
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        if frequency < 80:
            return "Unknown"
        
        # A4 = 440 Hz
        a4_freq = 440.0
        a4_midi = 69
        
        midi_note = 12 * np.log2(frequency / a4_freq) + a4_midi
        note_number = int(round(midi_note)) % 12
        octave = int(midi_note) // 12 - 1
        
        return f"{note_names[note_number]}{octave}"
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            for file in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print("Temporary files cleaned up")
        except Exception as e:
            print(f"Error cleaning up: {str(e)}")

def main():
    """Main function to demonstrate Phase 1 functionality."""
    if len(sys.argv) != 2:
        print("Usage: python audio_extractor_simple.py <youtube_url>")
        print("\nNote: This is a simplified version for Python 3.13 compatibility.")
        print("For full audio analysis, use Python 3.11 with pydub support.")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    extractor = SimpleAudioExtractor()
    
    try:
        audio_file = extractor.extract_audio_from_youtube(youtube_url)
        if not audio_file:
            print("Failed to extract audio")
            return
        
        analysis = extractor.get_audio_info(audio_file)
        if not analysis:
            print("Failed to analyze audio")
            return
        
        pitch_estimates = extractor.simulate_pitch_estimation(audio_file)
        
        results = {
            'audio_analysis': analysis,
            'pitch_estimates': pitch_estimates,
            'note': 'This is simulated data for demonstration purposes'
        }
        
        output_file = os.path.join(extractor.output_dir, 'analysis_results.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        print(f"Generated {len(pitch_estimates)} simulated pitch estimates")
        
        if pitch_estimates:
            print("\nFirst 5 simulated pitch estimates:")
            for i, estimate in enumerate(pitch_estimates[:5]):
                print(f"  {i+1}. {estimate['start_time']:.1f}s - {estimate['end_time']:.1f}s: "
                      f"{estimate['estimated_frequency']:.1f} Hz ({estimate['note']}) "
                      f"(confidence: {estimate['confidence']:.3f})")
    
    finally:
        extractor.cleanup()

if __name__ == "__main__":
    main() 