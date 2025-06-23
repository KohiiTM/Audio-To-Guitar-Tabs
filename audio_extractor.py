import os
import sys
import tempfile
import json
from typing import Dict, List, Optional, Tuple
import yt_dlp
from pydub import AudioSegment
import numpy as np

class AudioExtractor:
    def __init__(self, output_dir: str = "temp_audio"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def extract_audio_from_youtube(self, youtube_url: str) -> Optional[str]:
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True
            }
            
            print(f"Extracting audio from: {youtube_url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                video_title = info.get('title', 'unknown')
                print(f"Video title: {video_title}")
                
                ydl.download([youtube_url])
                
                expected_filename = f"{video_title}.wav"
                file_path = os.path.join(self.output_dir, expected_filename)
                
                if os.path.exists(file_path):
                    print(f"Audio extracted successfully: {file_path}")
                    return file_path
                else:
                    print("Audio file not found after extraction")
                    return None
                    
        except Exception as e:
            print(f"Error extracting audio: {str(e)}")
            return None
    
    def analyze_audio_basic(self, audio_file_path: str) -> Dict:
        try:
            audio = AudioSegment.from_wav(audio_file_path)
            
            duration_seconds = len(audio) / 1000.0
            sample_rate = audio.frame_rate
            channels = audio.channels
            
            samples = np.array(audio.get_array_of_samples())
            
            max_amplitude = np.max(np.abs(samples))
            rms_amplitude = np.sqrt(np.mean(samples**2))
            
            analysis = {
                'file_path': audio_file_path,
                'duration_seconds': duration_seconds,
                'sample_rate': sample_rate,
                'channels': channels,
                'max_amplitude': max_amplitude,
                'rms_amplitude': rms_amplitude,
                'total_samples': len(samples)
            }
            
            print(f"Audio analysis completed:")
            print(f"  Duration: {duration_seconds:.2f} seconds")
            print(f"  Sample rate: {sample_rate} Hz")
            print(f"  Channels: {channels}")
            print(f"  Max amplitude: {max_amplitude}")
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing audio: {str(e)}")
            return {}
    
    def simple_pitch_estimation(self, audio_file_path: str, segment_duration: float = 1.0) -> List[Dict]:
        try:
            audio = AudioSegment.from_wav(audio_file_path)
            sample_rate = audio.frame_rate
            samples = np.array(audio.get_array_of_samples())
            
            if audio.channels == 2:
                samples = samples.reshape(-1, 2).mean(axis=1)
            
            segment_length = int(segment_duration * sample_rate)
            pitch_estimates = []
            
            for i in range(0, len(samples), segment_length):
                segment = samples[i:i + segment_length]
                if len(segment) < segment_length:
                    break
                
                fft = np.fft.fft(segment)
                freqs = np.fft.fftfreq(len(segment), 1/sample_rate)
                
                magnitude_spectrum = np.abs(fft)
                peak_idx = np.argmax(magnitude_spectrum[1:len(magnitude_spectrum)//2]) + 1
                peak_frequency = abs(freqs[peak_idx])
                
                if peak_frequency > 80:  # Hz
                    pitch_estimates.append({
                        'start_time': i / sample_rate,
                        'end_time': (i + segment_length) / sample_rate,
                        'estimated_frequency': peak_frequency,
                        'confidence': magnitude_spectrum[peak_idx] / np.max(magnitude_spectrum)
                    })
            
            print(f"Pitch estimation completed: {len(pitch_estimates)} segments analyzed")
            return pitch_estimates
            
        except Exception as e:
            print(f"Error in pitch estimation: {str(e)}")
            return []
    
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
        print("Usage: python audio_extractor.py <youtube_url>")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    extractor = AudioExtractor()
    
    try:
        audio_file = extractor.extract_audio_from_youtube(youtube_url)
        if not audio_file:
            print("Failed to extract audio")
            return
        
        analysis = extractor.analyze_audio_basic(audio_file)
        if not analysis:
            print("Failed to analyze audio")
            return
        
        pitch_estimates = extractor.simple_pitch_estimation(audio_file)
        
        results = {
            'audio_analysis': analysis,
            'pitch_estimates': pitch_estimates
        }
        
        output_file = os.path.join(extractor.output_dir, 'analysis_results.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        print(f"Found {len(pitch_estimates)} pitch estimates")
        
        if pitch_estimates:
            print("\nFirst 5 pitch estimates:")
            for i, estimate in enumerate(pitch_estimates[:5]):
                print(f"  {i+1}. {estimate['start_time']:.1f}s - {estimate['end_time']:.1f}s: "
                      f"{estimate['estimated_frequency']:.1f} Hz "
                      f"(confidence: {estimate['confidence']:.3f})")
    
    finally:
        extractor.cleanup()

if __name__ == "__main__":
    main() 