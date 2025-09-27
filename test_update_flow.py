#!/usr/bin/env python3
"""
Simple test to demonstrate the user update flow step by step.
This shows exactly what headers you need for each request.
"""

import requests
import json

def test_update_flow():
    base_url = "http://localhost:8000"
    
    print("🔐 User Update Flow Demonstration")
    print("=" * 50)
    
    # Test data
    signup_data = {
        "name": "Demo User",
        "username": f"demouser{hash('test') % 1000}",  # Unique username
        "password": "demo123",
        "confirmPassword": "demo123",
        "age": 19,
        "academicLevel": "High School",
        "major": "cs",
        "dyslexiaSupport": False,
        "languagePreference": "English",
        "learningStyles": ["visual"],
        "metadata": []
    }
    
    print("📋 Step 1: User Signup (to get JWT token)")
    print("Headers needed:")
    print("  ✅ X-API-Key: vth_hackathon_2025_secret_key")
    print("  ❌ Authorization: (not needed for signup)")
    print()
    
    # Step 1: Signup
    try:
        response = requests.post(
            f"{base_url}/api/auth/signup",
            headers={
                "X-API-Key": "vth_hackathon_2025_secret_key",
                "Content-Type": "application/json"
            },
            json=signup_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            access_token = result["access_token"]
            user = result["user"]
            
            print("✅ Signup successful!")
            print(f"   User ID: {user['id']}")
            print(f"   JWT Token: {access_token[:30]}...")
            print(f"   Current age: {user['age']}")
            print(f"   Current academic level: {user['academicLevel']}")
            print()
            
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(f"   Error: {response.text}")
            print("\n💡 This might be a DynamoDB connection issue.")
            print("   The update flow still works the same way!")
            return demonstrate_headers_only()
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return demonstrate_headers_only()
    
    print("📋 Step 2: Update User Preferences")
    print("Headers needed:")
    print("  ✅ X-API-Key: vth_hackathon_2025_secret_key")
    print("  ✅ Authorization: Bearer <jwt_token_from_step_1>")
    print()
    
    # Step 2: Update preferences
    update_data = {
        "age": 21,
        "academicLevel": "College",
        "major": "computer science",
        "dyslexiaSupport": True,
        "languagePreference": "Spanish",
        "learningStyles": ["visual", "auditory", "kinesthetic"]
    }
    
    try:
        response = requests.put(
            f"{base_url}/api/user/preferences",
            headers={
                "X-API-Key": "vth_hackathon_2025_secret_key",
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=update_data,
            timeout=10
        )
        
        if response.status_code == 200:
            updated_user = response.json()
            print("✅ Update successful!")
            print(f"   New age: {updated_user['age']}")
            print(f"   New academic level: {updated_user['academicLevel']}")
            print(f"   New major: {updated_user['major']}")
            print(f"   New language: {updated_user['languagePreference']}")
            print(f"   New learning styles: {updated_user['learningStyles']}")
            print(f"   Dyslexia support: {updated_user['dyslexiaSupport']}")
            print()
            
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Update request failed: {e}")
    
    print("🎯 Summary: Headers Required for Updates")
    print("=" * 50)
    print("PUT /api/user/preferences")
    print("Headers:")
    print("  X-API-Key: vth_hackathon_2025_secret_key")
    print("  Authorization: Bearer <your_jwt_token>")
    print("  Content-Type: application/json")
    print()
    print("Body: JSON with any fields you want to update")

def demonstrate_headers_only():
    """Show the header requirements even if DynamoDB isn't working."""
    print("\n🎯 Header Requirements for User Updates")
    print("=" * 50)
    
    print("\n1. 📝 SIGNUP (to get JWT token):")
    print("   POST /api/auth/signup")
    print("   Headers:")
    print("     ✅ X-API-Key: vth_hackathon_2025_secret_key")
    print("     ❌ Authorization: (not needed)")
    
    print("\n2. 🔄 UPDATE PREFERENCES:")
    print("   PUT /api/user/preferences") 
    print("   Headers:")
    print("     ✅ X-API-Key: vth_hackathon_2025_secret_key")
    print("     ✅ Authorization: Bearer <jwt_token_from_signup>")
    
    print("\n3. 👤 GET PROFILE:")
    print("   GET /api/user/profile")
    print("   Headers:")
    print("     ✅ X-API-Key: vth_hackathon_2025_secret_key")
    print("     ✅ Authorization: Bearer <jwt_token_from_signup>")
    
    print("\n💡 Key Points:")
    print("   • All endpoints need the API key")
    print("   • User-specific endpoints need BOTH API key AND JWT token")
    print("   • JWT token comes from signup/signin response")
    print("   • Updates are partial - only send fields you want to change")

if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not running. Start with: cd image/src && uvicorn main:app --reload")
            exit(1)
    except:
        print("❌ Cannot connect to server. Start with: cd image/src && uvicorn main:app --reload")
        exit(1)
    
    test_update_flow()
