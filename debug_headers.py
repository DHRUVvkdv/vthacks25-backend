#!/usr/bin/env python3
"""
Debug script to test what headers are being sent.
"""

import requests

def test_headers():
    """Test what headers are actually being sent."""
    
    print("🔍 Debug: Testing Header Formats")
    print("=" * 40)
    
    # Test 1: Exactly as Maya is sending
    print("1. Testing Maya's exact request...")
    
    headers = {
        "X-API-Key": "vth_hackathon_2025_secret_key",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiM2YxMWE1ODMtNGI1OS00YjFlLWI1MmUtMjlmMDIwNjhmYmQzIiwidXNlcm5hbWUiOiJtYXlhQDEyIiwiZXhwIjoxNzU5MDkxMDMzfQ.18AgdSelc7sYiRk-yIuq-RwtxS-GiWezJEtd_zkcJK8",
        "Content-Type": "application/json"
    }
    
    print(f"Headers being sent:")
    for key, value in headers.items():
        if key == "Authorization":
            print(f"  {key}: {value[:50]}...")
        else:
            print(f"  {key}: {value}")
    
    # Test the protected endpoint that we know works
    print("\n2. Testing /api/user/profile endpoint...")
    try:
        response = requests.get(
            "http://localhost:8000/api/user/profile",
            headers=headers,
            timeout=10
        )
        print(f"Profile endpoint status: {response.status_code}")
        if response.status_code != 200:
            print(f"Profile response: {response.text}")
        else:
            result = response.json()
            print(f"Profile success: {result['name']} (ID: {result['id']})")
    except Exception as e:
        print(f"Profile request failed: {e}")
    
    # Test the update endpoint
    print("\n3. Testing /api/user/preferences endpoint...")
    update_data = {"age": 25}
    
    try:
        response = requests.put(
            "http://localhost:8000/api/user/preferences",
            headers=headers,
            json=update_data,
            timeout=10
        )
        print(f"Update endpoint status: {response.status_code}")
        print(f"Update response: {response.text}")
    except Exception as e:
        print(f"Update request failed: {e}")
    
    # Test 4: Try different header case
    print("\n4. Testing different header cases...")
    alt_headers = {
        "x-api-key": "vth_hackathon_2025_secret_key",  # lowercase
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiM2YxMWE1ODMtNGI1OS00YjFlLWI1MmUtMjlmMDIwNjhmYmQzIiwidXNlcm5hbWUiOiJtYXlhQDEyIiwiZXhwIjoxNzU5MDkxMDMzfQ.18AgdSelc7sYiRk-yIuq-RwtxS-GiWezJEtd_zkcJK8",
        "content-type": "application/json"
    }
    
    try:
        response = requests.put(
            "http://localhost:8000/api/user/preferences",
            headers=alt_headers,
            json=update_data,
            timeout=10
        )
        print(f"Lowercase headers status: {response.status_code}")
        print(f"Lowercase headers response: {response.text}")
    except Exception as e:
        print(f"Lowercase headers request failed: {e}")

if __name__ == "__main__":
    test_headers()
