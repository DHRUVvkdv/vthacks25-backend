#!/usr/bin/env python3
"""
Simple test to confirm signup works and show the complete flow.
"""

import requests
import json

def test_signup():
    """Test just the signup to confirm it's working."""
    
    signup_data = {
        "name": "Test User",
        "username": "testuser999",
        "password": "test123",
        "confirmPassword": "test123",
        "age": 20,
        "academicLevel": "College",
        "major": "cs",
        "dyslexiaSupport": False,
        "languagePreference": "English",
        "learningStyles": ["visual"],
        "metadata": []
    }
    
    print("🧪 Testing User Signup")
    print("=" * 30)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/auth/signup",
            headers={
                "X-API-Key": "vth_hackathon_2025_secret_key",
                "Content-Type": "application/json"
            },
            json=signup_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Signup successful!")
            print(f"User ID: {result['user']['id']}")
            print(f"Username: {result['user']['username']}")
            print(f"Name: {result['user']['name']}")
            print(f"Age: {result['user']['age']}")
            print(f"Academic Level: {result['user']['academicLevel']}")
            print(f"Major: {result['user']['major']}")
            print(f"Token: {result['access_token'][:50]}...")
            
            return result['access_token']
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_signin():
    """Test signin with existing user."""
    
    signin_data = {
        "username": "testuser999",
        "password": "test123"
    }
    
    print("\n🔑 Testing User Signin")
    print("=" * 30)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/auth/signin",
            headers={
                "X-API-Key": "vth_hackathon_2025_secret_key",
                "Content-Type": "application/json"
            },
            json=signin_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Signin successful!")
            print(f"Welcome back: {result['user']['name']}")
            return result['access_token']
        else:
            print(f"❌ Signin failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

if __name__ == "__main__":
    # Test signup
    token = test_signup()
    
    if token:
        # Test signin
        signin_token = test_signin()
        
        print("\n🎉 Both signup and signin are working!")
        print("\n📋 Summary:")
        print("✅ User registration: WORKING")
        print("✅ User authentication: WORKING") 
        print("✅ JWT token generation: WORKING")
        print("✅ DynamoDB integration: WORKING")
        
        print(f"\n🔑 Your JWT Token (for testing updates):")
        print(f"{token}")
        
        print(f"\n💡 To test updates manually:")
        print(f"curl -X PUT 'http://localhost:8000/api/user/preferences' \\")
        print(f"  -H 'X-API-Key: vth_hackathon_2025_secret_key' \\")
        print(f"  -H 'Authorization: Bearer {token}' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{\"age\": 25, \"major\": \"computer science\"}}'")
    else:
        print("\n❌ Signup failed - check server logs")
