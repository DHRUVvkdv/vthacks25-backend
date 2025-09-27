#!/usr/bin/env python3
"""
Test script for video upload and processing API.
Usage: python test_video_upload.py <video_file_path>
"""

import requests
import sys
import os

def test_video_upload(video_path: str, base_url: str = "http://localhost:8000"):
    """Test the video upload endpoint."""
    
    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} not found")
        return False
    
    # API endpoint and headers
    url = f"{base_url}/api/upload-video"
    headers = {
        "X-API-Key": "vth_hackathon_2025_secret_key"
    }
    
    # Prepare files and form data
    files = {
        "video": open(video_path, "rb")
    }
    
    data = {
        "user_background": "CS_student",
        "subject_preference": "physics"
    }
    
    try:
        print(f"Uploading video: {video_path}")
        print("Processing... (this may take a few minutes)")
        
        response = requests.post(url, headers=headers, files=files, data=data, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Video processing successful!")
            print(f"Status: {result['status']}")
            print(f"Transcript length: {len(result['transcript']['text'])} characters")
            print(f"Estimated duration: {result['concepts']['estimated_duration']} minutes")
            print(f"User context: {result['user_context']}")
            print(f"\nFirst 200 chars of transcript: {result['transcript']['text'][:200]}...")
            print(f"\nConcept analysis preview: {result['concepts']['analysis'][:300]}...")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - video processing took too long")
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
        print("Usage: python test_video_upload.py <video_file_path>")
        print("Example: python test_video_upload.py sample_video.mp4")
        sys.exit(1)
    
    video_file = sys.argv[1]
    
    # First check if server is running
    if not test_health_check():
        print("\nMake sure the server is running with: uvicorn main:app --reload")
        sys.exit(1)
    
    # Test video upload
    success = test_video_upload(video_file)
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
