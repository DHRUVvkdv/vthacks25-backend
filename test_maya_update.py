#!/usr/bin/env python3
"""
Test script to verify Maya's update flow works correctly.
"""

import requests
import json

def test_maya_flow():
    """Test the complete flow for Maya's account."""
    
    print("🧪 Testing Maya's Update Flow")
    print("=" * 40)
    
    # Step 1: Sign in as Maya
    print("1. Signing in as Maya...")
    signin_data = {
        "username": "maya@12",
        "password": "Dhruv@12"
    }
    
    try:
        signin_response = requests.post(
            "http://localhost:8000/api/auth/signin",
            headers={
                "X-API-Key": "vth_hackathon_2025_secret_key",
                "Content-Type": "application/json"
            },
            json=signin_data,
            timeout=10
        )
        
        if signin_response.status_code != 200:
            print(f"❌ Signin failed: {signin_response.status_code}")
            print(f"Response: {signin_response.text}")
            return
        
        signin_result = signin_response.json()
        access_token = signin_result["access_token"]
        user = signin_result["user"]
        
        print("✅ Signin successful!")
        print(f"   User: {user['name']} ({user['username']})")
        print(f"   Current age: {user['age']}")
        print(f"   Current major: {user['major']}")
        print(f"   Token: {access_token[:50]}...")
        
    except Exception as e:
        print(f"❌ Signin request failed: {e}")
        return
    
    # Step 2: Update preferences with CORRECT Authorization header
    print("\n2. Updating preferences with correct 'Bearer ' prefix...")
    
    update_data = {
        "name": "Maya",
        "age": 23,
        "academicLevel": "College",
        "major": "Computer Science",
        "dyslexiaSupport": True,
        "languagePreference": "Spanish",
        "learningStyles": ["visual", "auditory"],
        "metadata": ["updated_via_api"]
    }
    
    try:
        update_response = requests.put(
            "http://localhost:8000/api/user/preferences",
            headers={
                "X-API-Key": "vth_hackathon_2025_secret_key",
                "Authorization": f"Bearer {access_token}",  # Correct format!
                "Content-Type": "application/json"
            },
            json=update_data,
            timeout=10
        )
        
        print(f"Update response status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            update_result = update_response.json()
            print("✅ Update successful!")
            print(f"   New age: {update_result['age']}")
            print(f"   New major: {update_result['major']}")
            print(f"   New language: {update_result['languagePreference']}")
            print(f"   New learning styles: {update_result['learningStyles']}")
            print(f"   Dyslexia support: {update_result['dyslexiaSupport']}")
            
        else:
            print(f"❌ Update failed: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            
            # Debug: Test what happens without Bearer prefix
            print("\n🔍 Debug: Testing without 'Bearer ' prefix...")
            debug_response = requests.put(
                "http://localhost:8000/api/user/preferences",
                headers={
                    "X-API-Key": "vth_hackathon_2025_secret_key",
                    "Authorization": access_token,  # Missing "Bearer "
                    "Content-Type": "application/json"
                },
                json=update_data,
                timeout=10
            )
            print(f"Without 'Bearer ': {debug_response.status_code} - {debug_response.text}")
            
    except Exception as e:
        print(f"❌ Update request failed: {e}")

if __name__ == "__main__":
    test_maya_flow()
