#!/usr/bin/env python3
"""
Debug script to test YouTube audio extraction.
"""

import os
import sys
from audio_extractor_simple import SimpleAudioExtractor

def test_extraction():
    """Test audio extraction directly."""
    print("Testing YouTube audio extraction...")
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    extractor = SimpleAudioExtractor()
    
    try:
        print(f"Extracting from: {test_url}")
        audio_file = extractor.extract_audio_from_youtube(test_url)
        
        if audio_file:
            print(f"Success! Audio file: {audio_file}")
            
            analysis = extractor.get_audio_info(audio_file)
            print(f"Analysis: {analysis}")
            
            pitch_estimates = extractor.simulate_pitch_estimation(audio_file)
            print(f"Pitch estimates: {len(pitch_estimates)} segments")
            
            return True
        else:
            print("Extraction failed")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_extraction()
    sys.exit(0 if success else 1) 