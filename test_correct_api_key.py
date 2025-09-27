#!/usr/bin/env python3
"""
Test with the correct API key from .env file.
"""

import requests

def test_with_correct_api_key():
    """Test with the actual API key from .env file."""
    
    print("🔧 Testing with Correct API Key: 'dv'")
    print("=" * 40)
    
    # Test 1: Sign in with correct API key
    print("1. Testing signin with correct API key...")
    signin_data = {
        "username": "maya@12",
        "password": "Dhruv@12"
    }
    
    try:
        signin_response = requests.post(
            "http://localhost:8000/api/auth/signin",
            headers={
                "X-API-Key": "dv",  # Correct API key from .env
                "Content-Type": "application/json"
            },
            json=signin_data,
            timeout=10
        )
        
        print(f"Signin status: {signin_response.status_code}")
        
        if signin_response.status_code == 200:
            result = signin_response.json()
            access_token = result["access_token"]
            print("✅ Signin successful with correct API key!")
            print(f"   User: {result['user']['name']}")
            print(f"   Token: {access_token[:50]}...")
            
            # Test 2: Update preferences with correct API key
            print("\n2. Testing update with correct API key...")
            update_data = {
                "age": 25,
                "major": "Data Science",
                "dyslexiaSupport": True,
                "languagePreference": "Spanish"
            }
            
            update_response = requests.put(
                "http://localhost:8000/api/user/preferences",
                headers={
                    "X-API-Key": "dv",  # Correct API key
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=update_data,
                timeout=10
            )
            
            print(f"Update status: {update_response.status_code}")
            
            if update_response.status_code == 200:
                update_result = update_response.json()
                print("✅ Update successful!")
                print(f"   New age: {update_result['age']}")
                print(f"   New major: {update_result['major']}")
                print(f"   New language: {update_result['languagePreference']}")
                print(f"   Dyslexia support: {update_result['dyslexiaSupport']}")
            else:
                print(f"❌ Update failed: {update_response.text}")
                
        else:
            print(f"❌ Signin failed: {signin_response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print(f"\n💡 Summary:")
    print(f"   Correct API Key: 'dv' (from your .env file)")
    print(f"   Wrong API Key: 'vth_hackathon_2025_secret_key' (from tests)")

if __name__ == "__main__":
    test_with_correct_api_key()
