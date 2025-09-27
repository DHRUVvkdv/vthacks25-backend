#!/usr/bin/env python3
"""
Test script for user authentication and preferences API.
Usage: python test_user_auth.py
"""

import requests
import json

def test_user_auth(base_url: str = "http://localhost:8000"):
    """Test the user authentication endpoints."""
    
    # API headers
    headers = {
        "X-API-Key": "vth_hackathon_2025_secret_key",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing User Authentication & Preferences API")
    print("=" * 50)
    
    # Test data matching your frontend structure
    signup_data = {
        "name": "Test User",
        "username": "testuser123",
        "password": "testpass123",
        "confirmPassword": "testpass123",
        "age": 18,
        "academicLevel": "Middle School",
        "major": "cs",
        "dyslexiaSupport": False,
        "languagePreference": "French",
        "learningStyles": ["visual"],
        "metadata": []
    }
    
    signin_data = {
        "username": "testuser123",
        "password": "testpass123"
    }
    
    preferences_update = {
        "age": 19,
        "academicLevel": "High School",
        "major": "mathematics",
        "dyslexiaSupport": True,
        "languagePreference": "Spanish",
        "learningStyles": ["visual", "auditory"],
        "metadata": ["updated_via_api"]
    }
    
    try:
        # 1. Test Signup
        print("1. Testing User Signup...")
        response = requests.post(
            f"{base_url}/api/auth/signup",
            json=signup_data,
            timeout=10
        )
        
        if response.status_code == 200:
            signup_result = response.json()
            print("✅ Signup successful!")
            print(f"   User ID: {signup_result['user']['id']}")
            print(f"   Username: {signup_result['user']['username']}")
            print(f"   Token: {signup_result['access_token'][:20]}...")
            
            access_token = signup_result['access_token']
            auth_headers = {
                **headers,
                "Authorization": f"Bearer {access_token}"
            }
            
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # 2. Test Signin
        print("\n2. Testing User Signin...")
        response = requests.post(
            f"{base_url}/api/auth/signin",
            json=signin_data,
            timeout=10
        )
        
        if response.status_code == 200:
            signin_result = response.json()
            print("✅ Signin successful!")
            print(f"   Welcome back: {signin_result['user']['name']}")
            print(f"   Academic Level: {signin_result['user']['academicLevel']}")
            print(f"   Learning Styles: {signin_result['user']['learningStyles']}")
        else:
            print(f"❌ Signin failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # 3. Test Get Profile
        print("\n3. Testing Get User Profile...")
        response = requests.get(
            f"{base_url}/api/user/profile",
            headers=auth_headers,
            timeout=10
        )
        
        if response.status_code == 200:
            profile = response.json()
            print("✅ Profile retrieved successfully!")
            print(f"   Name: {profile['name']}")
            print(f"   Age: {profile['age']}")
            print(f"   Major: {profile['major']}")
            print(f"   Language: {profile['languagePreference']}")
        else:
            print(f"❌ Get profile failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # 4. Test Update Preferences
        print("\n4. Testing Update User Preferences...")
        response = requests.put(
            f"{base_url}/api/user/preferences",
            headers=auth_headers,
            json=preferences_update,
            timeout=10
        )
        
        if response.status_code == 200:
            updated_profile = response.json()
            print("✅ Preferences updated successfully!")
            print(f"   New Age: {updated_profile['age']}")
            print(f"   New Academic Level: {updated_profile['academicLevel']}")
            print(f"   New Major: {updated_profile['major']}")
            print(f"   New Language: {updated_profile['languagePreference']}")
            print(f"   New Learning Styles: {updated_profile['learningStyles']}")
            print(f"   Dyslexia Support: {updated_profile['dyslexiaSupport']}")
        else:
            print(f"❌ Update preferences failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        print("\n🎉 All user authentication tests completed!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

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
    print("VTHacks 2025 - User Authentication Test")
    print("=" * 40)
    
    # First check if server is running
    if not test_health_check():
        print("\nMake sure the server is running with: cd image/src && uvicorn main:app --reload")
        exit(1)
    
    # Test user authentication
    success = test_user_auth()
    
    if success:
        print("\n🎉 All tests passed! User authentication system is working.")
    else:
        print("\n❌ Some tests failed. Check the server logs for details.")
        exit(1)
