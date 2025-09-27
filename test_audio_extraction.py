#!/usr/bin/env python3
"""
Test script for audio extraction from video files.
Usage: python test_audio_extraction.py <video_file_path>
"""

import requests
import sys
import os

def test_audio_extraction(video_path: str, base_url: str = "http://localhost:8000"):
    """Test the audio extraction endpoint."""
    
    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} not found")
        return False
    
    # API endpoint and headers
    url = f"{base_url}/api/extract-audio"
    headers = {
        "X-API-Key": "dv"  # Using the correct API key from .env
    }
    
    # Prepare files
    files = {
        "video": open(video_path, "rb")
    }
    
    try:
        print(f"🎥 Extracting audio from: {video_path}")
        print("Processing... (this should be quick)")
        
        response = requests.post(url, headers=headers, files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Audio extraction successful!")
            
            # Display video information
            video_info = result['video_info']
            print(f"\n📹 Video Information:")
            print(f"   Duration: {video_info['duration']:.2f} seconds ({video_info['duration']/60:.1f} minutes)")
            print(f"   Size: {result['upload_info']['size_mb']:.2f} MB")
            print(f"   Format: {video_info['format']}")
            print(f"   Streams: {video_info['streams']}")
            
            # Display audio information
            audio_info = result['audio_info']
            print(f"\n🎵 Extracted Audio:")
            print(f"   Size: {audio_info['size_mb']:.2f} MB")
            print(f"   Sample Rate: {audio_info['sample_rate']} Hz")
            print(f"   Channels: {audio_info['channels']} (mono)")
            print(f"   Format: {audio_info['format']}")
            print(f"   File: {audio_info['path']}")
            
            # Calculate compression ratio
            compression_ratio = result['upload_info']['size_mb'] / audio_info['size_mb']
            print(f"\n📊 Compression Stats:")
            print(f"   Original video: {result['upload_info']['size_mb']:.2f} MB")
            print(f"   Extracted audio: {audio_info['size_mb']:.2f} MB")
            print(f"   Compression ratio: {compression_ratio:.1f}x smaller")
            
            print(f"\n✅ Audio extraction completed successfully!")
            print(f"   Status: {result['extraction_status']}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - audio extraction took too long")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    finally:
        files["video"].close()

def test_health_check(base_url: str = "http://localhost:8000"):
    """Test the health endpoint."""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_audio_extraction.py <video_file_path>")
        print("Example: python test_audio_extraction.py sample_video.mp4")
        print("\nThis tests ONLY the audio extraction step (no transcription)")
        sys.exit(1)
    
    video_file = sys.argv[1]
    
    print("🎬 VTHacks 2025 - Audio Extraction Test")
    print("=" * 45)
    
    # First check if server is running
    if not test_health_check():
        print("\nMake sure the server is running with:")
        print("cd image/src && uvicorn main:app --reload")
        sys.exit(1)
    
    # Test audio extraction
    success = test_audio_extraction(video_file)
    
    if success:
        print("\n🎉 Audio extraction test completed successfully!")
        print("\nNext steps:")
        print("1. ✅ Audio extraction working")
        print("2. 🔄 Next: Implement speech-to-text with Google Gemini")
        print("3. 🔄 Then: Content analysis and concept extraction")
    else:
        print("\n❌ Audio extraction test failed!")
        sys.exit(1)
